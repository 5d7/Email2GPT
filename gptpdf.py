import os  # Module to interact with the operating system
import smtplib  # Module to send emails using the Simple Mail Transfer Protocol (SMTP)
import ssl  # Module to handle secure connections (SSL/TLS)
import time  # Module to handle time-related tasks
import imaplib  # Module to interact with mail servers using IMAP
import email  # Module to manage email messages
import openai  # Module to interact with OpenAI's API
import logging  # Module for logging messages
from email.mime.multipart import MIMEMultipart  # Class for creating a multipart email
from email.mime.text import MIMEText  # Class for creating plain text email
from email.mime.base import MIMEBase  # Base class for creating attachments
from email import encoders  # Module to encode attachments
from fpdf import FPDF  # Module to generate PDF files
from dotenv import load_dotenv  # Module to load environment variables from a .env file

# Load environment variables from a .env file to keep sensitive data like API keys and passwords secure
load_dotenv()

# Configure logging to display info-level messages
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MailBot:
    def __init__(self, api_key, api_role, sender, mail_host, password, sender_email, sent_folder, inbox_folder, IMAP_SSL, SMTP_SSL):
        # Initialize the MailBot object with the necessary parameters
        self.api_key = api_key  # API key for OpenAI
        self.api_role = api_role  # Role configuration for OpenAI
        self.sender = sender  # Sender's name
        self.mail_host = mail_host  # Mail server host (e.g., smtp.gmail.com)
        self.password = password  # Password for the email account
        self.sender_email = sender_email  # Sender's email address
        self.sent_folder = sent_folder  # Folder to store sent emails
        self.inbox_folder = inbox_folder  # Folder to read incoming emails
        self.IMAP_SSL = IMAP_SSL  # Port for IMAP SSL connection
        self.SMTP_SSL = SMTP_SSL  # Port for SMTP SSL connection
    
    def reply_to_emails(self, unread_messages: bool):
        # Method to reply to emails, specifically unread ones if unread_messages is True
        try:
            # Connect to the IMAP server using SSL
            mail = imaplib.IMAP4_SSL(self.mail_host)
            mail.login(self.sender_email, self.password)
            mail.select(self.inbox_folder)  # Select the inbox folder

            # Search for emails, either unread or all, based on the parameter
            status, messages = mail.search(None, 'UNSEEN' if unread_messages else 'ALL')
            message_ids = messages[0].split()  # Get the list of email IDs

            for msg_id in message_ids:
                # Fetch the full email message using its ID
                status, data = mail.fetch(msg_id, '(RFC822)')
                raw_email = data[0][1]
                email_message = email.message_from_bytes(raw_email)

                # Extract sender's email and the subject of the message
                sender = email_message['From']
                subject = email_message['Subject']

                # Get the body of the email
                body = self.get_email_body(email_message)

                # Generate a response using OpenAI
                new_body = self.ai_responder(body)

                # Create a PDF from the generated response
                pdf_filename = self.create_pdf(new_body)

                # Send an email back to the sender with the PDF attached
                self.send_email(subject=subject, body=new_body, receiver_email=sender, pdf_filename=pdf_filename)

            # Logout from the IMAP server
            mail.logout()
        except Exception as e:
            # Log any errors that occur
            logger.error(f"Failed to process emails: {e}")
        return []

    def get_email_body(self, email_message):
        # Method to extract the body of an email message
        body = ""

        if email_message.is_multipart():
            # If the email has multiple parts (e.g., text and attachments)
            for part in email_message.walk():
                content = part.get_content_type()
                disposition = str(part.get('Content-Disposition'))
                # Extract the plain text part of the email that is not an attachment
                if content == 'text/plain' and 'attachment' not in disposition:
                    body = part.get_payload(decode=True) 
                    break
        else:
            # If the email is not multipart, just get the payload
            body = email_message.get_payload(decode=True)

        return body.decode('utf-8')  # Decode the body into a UTF-8 string

    def create_pdf(self, text, filename="response.pdf"):
        # Method to create a PDF file from the provided text
        pdf = FPDF()
        pdf.add_page()  # Add a new page to the PDF
        pdf.set_font("Arial", size=12)  # Set the font and size
        pdf.multi_cell(0, 10, text)  # Write the text in the PDF
        pdf.output(filename)  # Output the PDF to a file
        return filename  # Return the filename of the generated PDF

    def send_email(self, subject, body, receiver_email, pdf_filename):
        # Method to send an email with a PDF attachment
        try:
            # Create a multipart email message
            message = MIMEMultipart()
            message["From"] = self.sender_email
            message["To"] = receiver_email
            message["Subject"] = subject

            # Attach the body of the email
            message.attach(MIMEText("Please find the attached response PDF.", "plain"))

            # Open the PDF file in binary mode
            with open(pdf_filename, "rb") as attachment:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(attachment.read())

            # Encode the PDF file to base64 so it can be attached to the email
            encoders.encode_base64(part)

            # Add necessary headers to the attachment
            part.add_header(
                "Content-Disposition",
                f"attachment; filename= {pdf_filename}",
            )

            # Attach the PDF file to the email
            message.attach(part)
            text = message.as_string()  # Convert the message to a string

            # Send the email securely using SMTP_SSL
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(self.mail_host, self.SMTP_SSL, context=context) as server:
                server.login(self.sender_email, self.password)
                server.sendmail(self.sender_email, receiver_email, text)

            # Optionally add the email to the sent folder and mark it as seen
            imap = imaplib.IMAP4_SSL(self.mail_host, self.IMAP_SSL)
            imap.login(self.sender_email, self.password)
            imap.append(self.sent_folder, '\\Seen', imaplib.Time2Internaldate(time.time()), text.encode('utf8'))
            imap.logout()
        except Exception as e:
            # Log any errors that occur
            logger.error(f"Failed to send email: {e}")

    def ai_responder(self, message):
        # Method to generate a response using OpenAI's API
        try:
            openai.api_key = self.api_key  # Set the OpenAI API key
            response = openai.ChatCompletion.create(
                model="gpt-4o-mini",  # Model to use
                messages=[
                    {
                        "role": "system",
                        "content": self.api_role  # Define the role or behavior of the AI
                    },
                    {
                        "role": "user",
                        "content": str(message)  # Pass the user's message to the AI
                    }
                ],
                temperature=0.8,  # Control the creativity of the response
                max_tokens=256  # Limit the response length
            )

            # Extract the generated message from the response
            my_openai_obj = list(response.choices)[0]
            return (my_openai_obj.to_dict()['message']['content'])
        except Exception as e:
            # Log any errors and return a default message if OpenAI fails
            logger.error(f"Failed to get response from OpenAI: {e}")
            return "Sorry, I could not generate a response at this time."

if __name__ == "__main__":
    # Load environment variables for API keys and email configuration
    new_api_key = os.getenv("OPENAI_API_KEY")
    new_mail_host = os.getenv("MAIL_HOST")
    new_password = os.getenv("MAIL_PASSWORD")
    new_your_email = os.getenv("YOUR_EMAIL")

    # Configuration for OpenAI GPT model's behavior
    new_api_role = "You are a service assistant. You try to solve problems."

    # Email related configurations
    new_subject = "generated answer with GPT BOT"
    new_sender = "GPT BOT"    
    new_sent_folder = 'SENT'
    new_inbox_folder = 'INBOX'
    new_SMTP_SSL = 465  # SSL port for SMTP
    new_IMAP_SSL = 993  # SSL port for IMAP

    # Create an instance of the MailBot class with the loaded configurations
    mail_operator = MailBot(
        new_api_key, 
        new_api_role, 
        new_sender, 
        new_mail_host, 
        new_password, 
        new_your_email, 
        new_sent_folder, 
        new_inbox_folder, 
        new_IMAP_SSL, 
        new_SMTP_SSL 
    )

    # Trigger the email processing, focusing on unread emails
    unread_messages = mail_operator.reply_to_emails(unread_messages=True)
        
    logger.info("done")  # Log that the process is complete

