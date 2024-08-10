
# Python Email Automation Script

## Overview
This Python script defines a class `MailBot` that automates the process of reading unread emails, generating responses using OpenAI's GPT model, creating PDF documents of the responses, and sending them back as email attachments. The script is designed to handle secure connections to mail servers, manage email interactions, and log errors during the process.

### Features
- **Automatic Email Retrieval**: Connects to an email inbox using IMAP and retrieves unread emails.
- **AI-Powered Responses**: Uses OpenAI's GPT model to generate context-based responses to emails.
- **PDF Generation**: Converts AI-generated responses into PDF documents.
- **Automated Email Reply**: Sends the PDF documents as attachments in reply emails.
- **Logging**: Logs information and errors for monitoring the script's activity.

## Script Breakdown

### 1. **Imports and Environment Setup**
```python
import os
import smtplib
import ssl
import time
import imaplib
import email
import openai
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from fpdf import FPDF
from dotenv import load_dotenv
```
These imports bring in various modules necessary for handling email communication, interacting with OpenAI's API, managing PDFs, and handling environment variables securely.

### 2. **Load Environment Variables**
```python
load_dotenv()
```
The `load_dotenv()` function loads environment variables from a `.env` file. This is used to securely manage sensitive information like API keys and passwords.

### 3. **Logging Setup**
```python
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
```
Logging is set up to capture information and errors, helping track the script’s behavior.

### 4. **MailBot Class Initialization**
```python
class MailBot:
    def __init__(self, api_key, api_role, sender, mail_host, password, sender_email, sent_folder, inbox_folder, IMAP_SSL, SMTP_SSL):
        ...
```
The `MailBot` class is initialized with parameters required for API interaction and email communication. These include credentials, email folders, and server details.

### 5. **Replying to Emails**
```python
def reply_to_emails(self, unread_messages: bool):
    ...
```
This method retrieves unread emails, processes them, generates responses using GPT, and sends back replies with the generated PDF attached.

### 6. **Extracting Email Body**
```python
def get_email_body(self, email_message):
    ...
```
This method extracts the plain text body from an email, handling both multipart and single-part email formats.

### 7. **Generating PDFs**
```python
def create_pdf(self, text, filename="response.pdf"):
    ...
```
The `create_pdf` method generates a PDF from the provided text using the `FPDF` library. The PDF is saved with the specified filename.

### 8. **Sending Emails**
```python
def send_email(self, subject, body, receiver_email, pdf_filename):
    ...
```
This method sends an email with the generated PDF attached. It handles the email creation, attachment process, and secure sending via SMTP.

### 9. **AI Response Generation**
```python
def ai_responder(self, message):
    ...
```
This method interacts with OpenAI’s API to generate a response based on the provided email message. It uses the `ChatCompletion.create` method to get a context-based reply from GPT.

### 10. **Main Execution Block**
```python
if __name__ == "__main__":
    ...
```
The script’s main block loads environment variables and creates an instance of the `MailBot` class. It then triggers the process to reply to unread emails.

### Conclusion
This script is a robust tool for automating email replies using AI. It can be further expanded or customized based on specific requirements, such as handling different types of email content or generating responses based on other AI models.

## Potential Use Cases
- **Customer Support Automation**: Automatically generate responses to customer inquiries.
- **Ticketing Systems**: Reply to tickets with solutions or follow-ups in PDF format.
- **Personal Email Management**: Automate responses to common queries.

## Considerations
- **Security**: Ensure that environment variables (API keys, passwords) are securely managed.
- **Rate Limits**: Be mindful of API usage limits when interacting with OpenAI.
- **Error Handling**: The script includes basic error handling, but more specific cases might need attention based on the deployment environment.
