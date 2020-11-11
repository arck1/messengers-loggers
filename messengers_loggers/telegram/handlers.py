import logging
from io import BytesIO
from typing import Dict, Optional, Union

import requests

from messengers_loggers.telegram.formatters import HtmlFormatter, TelegramFormatter

logger = logging.getLogger(__name__)
logger.setLevel(logging.NOTSET)
logger.propagate = False

__all__ = ["TelegramHandler", "TelegramDjangoHandler"]

MAX_MESSAGE_LEN = 4096


class TelegramHandler(logging.Handler):
    API_ENDPOINT = "https://api.telegram.org"

    def __init__(
        self,
        token: str,
        chat_id: str,
        *,
        is_enabled: bool = False,
        service: str = None,
        level=logging.NOTSET,
        timeout: int = 2,
        disable_notification: bool = False,
        disable_web_page_preview: bool = False,
        proxies=None,
        formatter: TelegramFormatter = None,
    ):
        self.token = token
        self.chat_id = chat_id

        self.disable_web_page_preview = disable_web_page_preview
        self.disable_notification = disable_notification
        self.timeout = timeout
        self.proxies = proxies

        self.is_enabled = is_enabled

        if not self.chat_id:
            level = logging.NOTSET
            logger.error("Did not get chat id. Setting handler logging level to NOTSET.")
        logger.info("TelegramHandler: Chat id: %s", self.chat_id)

        super(TelegramHandler, self).__init__(level=level)

        self._defaultFormatter = formatter or HtmlFormatter(use_emoji=True, service=service)

    @classmethod
    def format_url(cls, token, method):
        return "%s/bot%s/%s" % (cls.API_ENDPOINT, token, method)

    def _find_chat_id(self, key: Union[str, int], data: Dict) -> Optional[Dict]:
        if key in data:
            return data[key]
        for k, value in data.items():
            if isinstance(value, dict):
                item = self._find_chat_id(key, value)
                if item is not None:
                    return item

    def get_chat_id(self) -> Optional[str]:
        response = self.request("getUpdates")
        if not response or not response.get("ok", False):
            logger.error("Telegram response is not ok: %s", str(response))
            return
        try:
            return self._find_chat_id("chat", response["result"][-1]).get("id")
        except Exception as e:
            logger.exception("Error on getting chat id from last response")
            logger.debug(response)

    def request(self, method: str, **kwargs) -> Optional[Dict]:
        url = self.format_url(self.token, method)

        kwargs.setdefault("timeout", self.timeout)
        kwargs.setdefault("proxies", self.proxies)
        response = None
        try:
            response = requests.post(url, **kwargs)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.exception("Error while making POST to %s", url)
            logger.debug(str(kwargs))
            if response is not None:
                logger.debug(response.content)

        return response

    def send_message(self, text: str, **kwargs) -> Optional[Dict]:
        data = {
            "text": text,
            **kwargs,
        }
        return self.request("sendMessage", json=data)

    def send_document(self, text: str, document, **kwargs) -> Optional[Dict]:
        data = {
            "caption": text,
            **kwargs,
        }
        return self.request("sendDocument", data=data, files={"document": ("traceback.txt", document, "text/plain")})

    def format(self, record):
        if self.formatter:
            fmt = self.formatter
        else:
            fmt = self._defaultFormatter
        return fmt.format(record)

    def emit(self, record: logging.LogRecord):
        text = self.format(record)

        if not self.is_enabled:
            logger.info("TelegramHandler disabled:\n{}".format(text))
            return

        if not self.chat_id:
            logger.warning("TelegramHandler without chat_id:\n{}".format(text))
            return

        data = {
            "chat_id": self.chat_id,
            "no_webpage": self.disable_web_page_preview,
            "silent": self.disable_notification,
        }

        if getattr(self.formatter, "parse_mode", None):
            data["parse_mode"] = self.formatter.parse_mode

        if len(text) < MAX_MESSAGE_LEN:
            response = self.send_message(text, **data)
        else:
            response = self.send_document(text[:1000], document=BytesIO(text.encode()), **data)

        if response and not response.get("ok", False):
            logger.warning("Telegram responded with ok=false status! {}".format(response))


class TelegramDjangoHandler(TelegramHandler):
    def __init__(self, token: str = None, chat_id: str = None, is_enabled: bool = False, *args, **kwargs):
        from django.conf import settings

        token = token or getattr(settings, "TELEGRAM_LOGGER_TOKEN", None)
        chat_id = chat_id or getattr(settings, "TELEGRAM_LOGGER_CHAT_ID", None)
        is_enabled = is_enabled or getattr(settings, "MESSENGERS_LOGGER_ENABLE", False)
        config: Dict = getattr(settings, "MESSENGERS_LOGGER_CONFIG", {})

        kwargs.update(config)

        super().__init__(token, chat_id, is_enabled=is_enabled, *args, **kwargs)
