# Main script to send an email using the SMTP server and the S/MIME protocol
import os

from omegaconf import OmegaConf

from config import LocalhostScenario, Scenario
from smime.smime_message import create_smime
from smtp import create_temp_mailbox, list_email, send_email

# Get config
conf: Scenario = OmegaConf.structured(LocalhostScenario)
SMTP_USER = os.environ.get("SMTP_USER")
SMTP_PASS = os.environ.get("SMTP_PASS")

USE_SMIME = True
DEBUG = True

# Email details
SENDER_EMAIL = "remy.tang@telecom-paris.fr"
RECEIVER_EMAIL = "remy.tang31@gmail.com"
SUBJECT = "IBE Test Email"
BODY = "This is a test email for the IBE project."

if __name__ == "__main__":

    # Create the server with a temporary mailbox
    controller, resources, maildir_path = create_temp_mailbox(
        conf.smtp_server.hostname, conf.smtp_server.port, DEBUG
    )

    try:

        if USE_SMIME:
            # Create an S/MIME message
            out = create_smime(
                from_addr=conf.sender.address,
                to_addrs=conf.recipient.address,
                subject="test",
                msg=b"test",
                from_key=conf.sender.sk,
                from_cert=conf.sender.cert,
                to_certs=[conf.recipient.cert],
            )

        # Send the email
        send_email(
            from_addr=conf.sender.address,
            to_addrs=conf.recipient.address,
            smtpd=conf.smtp_server.hostname,
            smtp_port=conf.smtp_server.port,
            out=out,
        )

        # List the messages in the mailbox
        list_email(maildir_path)

    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Cleanup mails when finished
        resources.close()
