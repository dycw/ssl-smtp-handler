import datetime as dt
from logging import basicConfig
from logging import debug
from logging.handlers import SMTPHandler
from os import getenv
from typing import Any

from pytest import mark
from pytest import raises
from pytest import skip

from ssl_smtp_handler import SSLSMTPHandler


def test_instantiating() -> None:
    handler = SSLSMTPHandler(
        mailhost="smtp.gmail.com",
        fromaddr="from@example.com",
        toaddrs=["to@example.com"],
        subject="Example subject",
        credentials=("username", "password"),
    )
    assert isinstance(handler, SMTPHandler)


def test_credentials_mandatory() -> None:
    with raises(ValueError, match='"credentials" is mandatory'):
        SSLSMTPHandler(
            mailhost="smtp.gmail.com",
            fromaddr="from@example.com",
            toaddrs=["to@example.com"],
            subject="Example subject",
        )


@mark.parametrize("secure", [(), ("keyfile",), ("keyfile", "certfile")])
def test_secure_deprecated(secure: Any) -> None:
    with raises(ValueError, match='"secure" is deprecated on SSLSMTPHandler'):
        SSLSMTPHandler(
            mailhost="smtp.gmail.com",
            fromaddr="from@example.com",
            toaddrs=["to@example.com"],
            subject="Example subject",
            credentials=("username", "password"),
            secure=secure,
        )


def test_sending_email_to_user() -> None:
    mailhost = getenv("TEST_MAILHOST")
    fromaddr = getenv("TEST_FROMADDR")
    toaddr = getenv("TEST_TOADDR")
    username = getenv("TEST_USERNAME")
    password = getenv("TEST_PASSWORD")
    if (
        (mailhost is None)
        or (fromaddr is None)
        or (toaddr is None)
        or (username is None)
        or (password is None)
    ):
        skip(msg="No test credentials found")
        raise RuntimeError("You shouldn't hit this line")
    mailport = getenv("TEST_MAILPORT")
    handler = SSLSMTPHandler(
        mailhost=mailhost if mailport is None else (mailhost, int(mailport)),
        fromaddr=fromaddr,
        toaddrs=[toaddr],
        subject="Example subject",
        credentials=(username, password),
    )
    basicConfig(handlers=[handler], level="DEBUG", style="{")
    debug("This is an example message, sent {now}", now=dt.datetime.now())
