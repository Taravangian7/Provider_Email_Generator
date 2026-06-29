import smtplib
import os
from dotenv import load_dotenv
load_dotenv(override=True)
user=os.getenv("OUTLOOK_EMAIL")
contra=os.getenv("OUTLOOK_PASSWORD")
server = smtplib.SMTP("smtp.gmail.com", 587)
server.starttls()
server.login(user, contra)
print("OK")
server.quit()