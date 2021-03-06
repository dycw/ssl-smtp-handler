from email.message import EmailMessage
from email.utils import localtime
from logging import LogRecord
from logging.handlers import SMTPHandler
from smtplib import SMTP_SSL
from smtplib import SMTP_SSL_PORT
from ssl import SSLContext
from typing import Optional
from typing import Union


class SSLSMTPHandler(SMTPHandler):
    def __init__(
        self,
        mailhost: Union[str, tuple[str, int]],
        fromaddr: str,
        toaddrs: list[str],
        subject: str,
        credentials: Optional[tuple[str, str]] = None,
        secure: Optional[Union[tuple[()], tuple[str], tuple[str, str]]] = None,
        timeout: float = 1.0,
        context: Optional[SSLContext] = None,
    ) -> None:
        """Initialize the SSLSMTPHandler. Arguments are the same as
        SMTPHandler except that:

        - "credentials" is mandatory; pass in a tuple of the form (username,
                        password)
        - "secure" is deprecated; use "context" instead; see
                   https://docs.python.org/3/library/smtplib.html
        """
        if credentials is None:
            raise ValueError(
                '"credentials" is mandatory; please pass in a tuple of the '
                "form (username, password)"
            )
        if secure is not None:
            raise ValueError(
                '"secure" is deprecated on SSLSMTPHandler, for since Python '
                '3.6, the "keyfield" and "certfile" fields have been '
                'in favour of "context"; '
                "see https://docs.python.org/3/library/smtplib.html. Please "
                'use the "context" argument instead.'
            )
        super().__init__(
            mailhost,
            fromaddr,
            toaddrs,
            subject,
            credentials=credentials,
            secure=secure,
            timeout=timeout,
        )
        self.mailhost: str
        if self.mailport is None:
            self.mailport = SMTP_SSL_PORT
        self.username: str
        self.password: str
        self.fromaddr: str
        self.toaddrs: list[str]
        self.timeout: float
        self.context = context

    def emit(self, record: LogRecord) -> None:
        """
        Emit a record.

        Format the record and send it to the specified addressees.
        """
        try:
            msg = EmailMessage()
            msg["From"] = self.fromaddr
            msg["To"] = ",".join(self.toaddrs)
            msg["Date"] = localtime()
            msg["Subject"] = self.getSubject(record)
            msg.set_content(self.format(record))
            smtp = SMTP_SSL(
                host=self.mailhost,
                port=self.mailport,
                timeout=self.timeout,
                context=self.context,
            )
            smtp.login(user=self.username, password=self.password)
            smtp.send_message(
                msg=msg, from_addr=self.fromaddr, to_addrs=self.toaddrs
            )
            smtp.quit()
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception:
            self.handleError(record)


__all__ = ["SSLSMTPHandler"]
