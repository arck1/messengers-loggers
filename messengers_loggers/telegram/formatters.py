import json
import logging

__all__ = ["TelegramFormatter", "MarkdownFormatter", "HtmlFormatter"]

import pprint

from messengers_loggers.utils.html import escape_html


class TelegramFormatter(logging.Formatter):
    """Base formatter class suitable for use with `TelegramHandler`"""

    fmt = "%(levelname)s\n[%(name)s:%(funcName)s]\n%(message)s"
    parse_mode = None

    def __init__(self, fmt=None, *args, **kwargs):
        fmt = kwargs.get("format")

        super(TelegramFormatter, self).__init__(fmt or self.fmt, *args, **kwargs)


class MarkdownFormatter(TelegramFormatter):
    """Markdown formatter for telegram."""

    fmt = "*%(levelname)s*\n[%(name)s:%(funcName)s]\n%(message)s"
    parse_mode = "Markdown"

    def formatException(self, *args, **kwargs):
        string = super(MarkdownFormatter, self).formatException(*args, **kwargs)
        return "```\n%s\n```" % string


class EMOJI:
    WHITE_CIRCLE = "⚪"
    BLUE_CIRCLE = "🔵"
    RED_CIRCLE = "🔴"
    ORANGE_CIRCLE = "🟠"
    BLACK_CIRCLE = "⚫"


LOG_LEVEL_EMOJI = {
    logging.DEBUG: EMOJI.WHITE_CIRCLE,
    logging.INFO: EMOJI.BLUE_CIRCLE,
    logging.ERROR: EMOJI.RED_CIRCLE,
    logging.WARNING: EMOJI.ORANGE_CIRCLE,
    logging.FATAL: EMOJI.BLACK_CIRCLE,
}
DEFAULT_LOG_LEVEL_EMOJI = EMOJI.RED_CIRCLE

HTML_PRE_TAG = "<pre>%s</pre>"


class HtmlFormatter(TelegramFormatter):
    """HTML formatter for telegram."""

    fmt = "<b>%(levelname)s</b>\nFrom [%(module)s:%(funcName)s]\n%(message)s"
    fmt_service = "<b>%(levelname)s</b>\nFrom %(service)\n[%(module)s:%(funcName)s]\n%(message)s"
    parse_mode = "HTML"

    def __init__(self, *args, **kwargs):
        self.use_emoji = kwargs.pop("use_emoji", False)
        self.service = kwargs.pop("service", None)

        super(HtmlFormatter, self).__init__(*args, **kwargs)

    def format(self, record):
        """
        :param logging.LogRecord record:
        """

        record.service = self.service or "logs"

        if record.module:
            record.module = escape_html(str(record.module))
        if record.funcName:
            record.funcName = escape_html(str(record.funcName))
        if record.name:
            record.name = escape_html(str(record.name))
        if record.msg:
            if isinstance(record.msg, (dict, list, tuple)):
                """
                try beautifully format message
                """
                try:
                    msg_str = json.dumps(record.msg, indent=4, ensure_ascii=False)
                except Exception as e:
                    msg_str = pprint.pformat(record.msg, indent=4)
            else:
                msg_str = str(record.msg)
            if record.args:
                msg_str = msg_str % record.args
            record.message = escape_html(msg_str)
        if self.use_emoji:
            record.levelname = "{emoji} {loglevel}".format(
                emoji=LOG_LEVEL_EMOJI.get(record.levelno, DEFAULT_LOG_LEVEL_EMOJI),
                loglevel=escape_html(str(record.levelname)),
            )
        return super(HtmlFormatter, self).format(record)

    def formatException(self, *args, **kwargs) -> str:
        string: str = super(HtmlFormatter, self).formatException(*args, **kwargs)
        return HTML_PRE_TAG % escape_html(string)

    def formatStack(self, *args, **kwargs) -> str:
        string: str = super(HtmlFormatter, self).formatStack(*args, **kwargs)
        return HTML_PRE_TAG % escape_html(string)
