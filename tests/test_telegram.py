import logging
import os

import pytest

from messengers_loggers.telegram.handlers import TelegramHandler
from dotenv import load_dotenv

load_dotenv()


@pytest.fixture
def telegram_handler_fixture():
    return TelegramHandler(
        token=os.getenv("TELEGRAM_LOGGER_TOKEN"), chat_id=os.getenv("TELEGRAM_LOGGER_CHAT_ID"), service="logs"
    )


@pytest.fixture
def telegram_formatter_fixture():
    pass


def test_handler_get_chat_id(monkeypatch, telegram_handler_fixture: TelegramHandler):
    chat_id = telegram_handler_fixture.get_chat_id()

    assert chat_id, "Undefined chat_id"
    assert str(chat_id) == os.getenv("TELEGRAM_LOGGER_CHAT_ID"), "Invalid get_chat_id function"


def test_logging_handler_send_message(monkeypatch, telegram_handler_fixture: TelegramHandler):
    test_logger = logging.getLogger(__name__)
    test_logger.setLevel(logging.INFO)
    test_logger.addHandler(telegram_handler_fixture)
    test_logger.propagate = False

    test_logger.info(
        {
            "test": "test"
        }
    )


def test_formatter():
    pass
