import base64
import os
import smtplib
import logging
import sys
import textwrap
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from app.config.config_loader import load_config


def resource_path(relative_path):
	try:
		# PyInstaller creates a temp folder and stores path in _MEIPASS
		base_path = sys._MEIPASS2
	except Exception:
		base_path = os.path.abspath(".")
	
	return os.path.join(base_path, relative_path)


class TestEmailSender:
	"""
	This class is used to send test emails to the email address specified in the config file.
	"""
	def __init__(self, use_mailhog=False):
		self.config = load_config()
		self.use_mailhog = use_mailhog
		self.sender_email = self.config['email']['sender_email']
		self.link_calendly = self.config['email']['link_calendly']

	
	def encode_image_to_base64(self, image_path):
		try:
			with open(image_path, "rb") as image_file:
				encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
			return encoded_string
		except FileNotFoundError:
			logging.error(f"File not found: {image_path}")
		except Exception as e:
			logging.error(f"Error encoding image to base64: {e}")
		return None
	
	def format_email_text(self, text, width=100):
		
		wrapped_text = textwrap.fill(text, width)
		
		lines = wrapped_text.split('.')
		lines = [line + '.' for line in lines if line]
		
		for i in range(2, len(lines), 3):
			if lines[i].endswith(('.', '?', '!')):
				lines[i] += '<br><br>'
		html_formatted_text = '<br>'.join(lines).rstrip('.')
		return html_formatted_text
	
	def send_test_email(self, subject, text_raw):
		self.config = load_config()

		try:
			logo_GT = resource_path("./asset/logoGT.jpg")
			
			sender_email = self.sender_email
			smtp_server = self.config['email']['smtp_server']
			smtp_port = self.config['email']['smtp_port']
			login = self.config['email']['login']
			password = self.config['email']['password']
			link_calendly = self.link_calendly

			bcc_email = "fbernard@akema.fr"
			receiver_email = self.config['email_test']['receiver_email_test']

			text = self.format_email_text(text_raw)

			msg = MIMEMultipart('related')
			msg['From'] = sender_email
			msg['To'] = receiver_email
			msg['Subject'] = subject
			msg['Bcc'] = bcc_email

			
			html_content = f"""\
                        <html>
                        <head></head>
                        <body>
                            <p style="font-family: Arial, sans-serif; font-size: 14px;">
                                Bonjour , </p><br><br>
								{text}

								<p>Pour planifier un entretien, veuillez utiliser notre <a href="{link_calendly}">lien
								Calendly</a>.</p>
                                <p>Service de recrutement <a href="mailto:{sender_email}"> <br>
                                {sender_email} </a><p>
                                <hr>
                                <img src="cid:logo_GT" alt="logo_GT" style="width:130px; height:55px;">

                            </body>
                            </html>
                            """
			msg.attach(MIMEText(html_content, 'html'))
			
			# Attach image as related content
			logo_GT_base64 = self.encode_image_to_base64(logo_GT)
			if logo_GT_base64:
				img = MIMEImage(base64.b64decode(logo_GT_base64), name=os.path.basename(logo_GT))
				img.add_header('Content-ID', '<logo_GT>')
				img.add_header('Content-Disposition', 'inline', filename=os.path.basename(logo_GT))
				msg.attach(img)
			
			if self.use_mailhog:
				# Use smtplib for testing
				with smtplib.SMTP('localhost', 1025) as server:
					server.send_message(msg)
			else:
				# Send via SMTP server
				with smtplib.SMTP(smtp_server, smtp_port) as server:
					server.starttls()
					server.login(login, password)
					server.send_message(msg)
			
			logging.info("Email TEST sent successfully")
			return True
		except Exception as e:
			logging.error(f"Error sending  Test email: {e} ")
			return False
