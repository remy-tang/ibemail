# Create and run an SMTP server
import os
from contextlib import ExitStack
import smtplib
from tempfile import TemporaryDirectory
import time

from aiosmtpd.controller import Controller
from aiosmtpd.handlers import Mailbox

from mailbox import Maildir

from operator import itemgetter


class MailboxHandler(Mailbox):

    def __init__(self, maildir_path: str, debug):
        super().__init__(maildir_path)
        self.debug = debug

    async def handle_DATA(self, server, session, envelope):
        print(f"New message from {envelope.mail_from} to {envelope.rcpt_tos}")
        
        if self.debug:
            print('Message data:\n')
            for ln in envelope.content.decode('utf8', errors='replace').splitlines():
                print(f'> {ln}'.strip())
    
            print('End of message')
        print()
        return "250 Message accepted for delivery"
    


def list_email(maildir_path: str):
    """List all messages in the mailbox."""
    mailbox = Maildir(maildir_path)

    messages = sorted(mailbox, key=itemgetter("message-id"))

    for message in messages:
        print(message["Message-ID"], message["From"], message["To"])


def create_temp_mailbox(
    hostname: str | None = None, port: int = 8025, debug: bool = False
) -> tuple[Controller, ExitStack]:
    """Create a mailbox using a temporary directory called maildir.

    Don't forget to cleanup at the end by running `resources.close()`
    """
    # Clean up the temporary directory at the end
    resources = ExitStack()
    tempdir = resources.enter_context(TemporaryDirectory())
    maildir_path = os.path.join(tempdir, "maildir")

    controller = Controller(
        handler=MailboxHandler(maildir_path, debug), hostname=hostname, port=port
    )

    controller.start()

    # Arrange for the controller to be stopped at the end
    _ = resources.callback(controller.stop)

    return controller, resources, maildir_path


def send_email(from_addr: str, to_addrs: str, smtpd: str, smtp_port: int, out: str):
    """Send an email using SMTP."""
    smtp = smtplib.SMTP()
    smtp.connect(smtpd, smtp_port)
    time.sleep(1)
    smtp.sendmail(from_addr, to_addrs, out)
    smtp.quit()


def read_email(maildir_path: str):
    mailbox = Maildir(maildir_path)

    messages = sorted(mailbox, key=itemgetter("message-id"))

    for message in messages:
        print(message["Message-ID"], message["From"], message["To"])


if __name__ == "__main__":

    controller, resources, maildir_path = create_temp_mailbox("localhost")
    controller
