
import os
from dotenv import load_dotenv
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, MailSettings, SandBoxMode

from app import APP_ENV

load_dotenv()

SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
SENDER_ADDRESS = os.getenv("SENDER_ADDRESS")


def send_email(sender_address=SENDER_ADDRESS, recipient_addresses=SENDER_ADDRESS, subject="[Tweet Collection 2022] Email Service", html="<p>Hello World</p>", cc_addresses=None):
    """
    Params:

        recipient_addresses (str or list) : an email address or list of addresses

        cc_addresses (str or list) : an email address or list of addresses

    """
    client = SendGridAPIClient(SENDGRID_API_KEY) #> <class 'sendgrid.sendgrid.SendGridAPIClient>
    print("CLIENT:", type(client))
    print("SUBJECT:", subject)
    #print("HTML:", html)
    message = Mail(from_email=sender_address, to_emails=recipient_addresses, subject=subject, html_content=html)
    if cc_addresses:
        for cc_address in cc_addresses:
            message.add_cc(cc_address)

    if APP_ENV == "test":
        # SEND MAIL IN "SANDBOX MODE" IN TEST ENVIRONMENT!!!
        # see: https://docs.sendgrid.com/for-developers/sending-email/sandbox-mode
        mail_settings = MailSettings()
        mail_settings.sandbox_mode = SandBoxMode(True)
        message.mail_settings = mail_settings

    try:
        response = client.send(message)
        print("RESPONSE:", type(response)) #> <class 'python_http_client.client.Response'>
        print(response.status_code) #> 202 indicates SUCCESS
        return response
    except Exception as e:
        print("ERROR SENDING EMAIL:", e)
        return None


if __name__ == "__main__":


    example_html = """
    <h3>Email Service</h3>

    <p>Lorum ipsum...</p>
    """

    send_email(html=example_html)
