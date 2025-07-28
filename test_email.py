import smtplib
from email.mime.text import MIMEText

sender_email = "manojsomarowthu123@gmail.com"
app_password = "yptq ivvi ryxp jdei"  # 16-char Gmail App Password
receiver_email = "manojnaidusomarowthu@gmail.com"

subject = "Test Email from Python"
body = "This is a test email sent via Gmail SMTP."

msg = MIMEText(body, "plain")
msg["Subject"] = subject
msg["From"] = sender_email
msg["To"] = receiver_email

try:
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender_email, app_password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
    print("✅ Email sent successfully!")
except Exception as e:
    print("❌ Failed to send email:", e)
