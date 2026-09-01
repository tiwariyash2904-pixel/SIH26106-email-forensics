from email.message import EmailMessage

msg = EmailMessage()

msg["From"] = "test@example.com"
msg["To"] = "investigator@example.com"
msg["Subject"] = "SIH26106 Auth Header Test"
msg["User-Agent"] = "Mozilla Thunderbird 115.0"
msg["Authentication-Results"] = (
    "mx.example.com; "
    "spf=pass smtp.mailfrom=test@example.com; "
    "dkim=pass header.i=@example.com; "
    "dmarc=pass (p=REJECT) header.from=example.com"
)

msg.set_content(
    """This is a harmless plain-text test email.

Please visit:
https://example.com/login
"""
)

msg.add_alternative(
    """
    <html>
      <body>
        <p>This is a harmless HTML test email.</p>
        <p>Please visit: <a href="https://example.com/login-html">this link</a></p>
      </body>
    </html>
    """,
    subtype="html"
)

with open("test_attachment.txt", "rb") as f:
    attachment_data = f.read()

msg.add_attachment(
    attachment_data,
    maintype="text",
    subtype="plain",
    filename="test_attachment.txt"
)

with open("test_with_auth.eml", "wb") as f:
    f.write(bytes(msg))

print("Test email with auth headers created successfully!")