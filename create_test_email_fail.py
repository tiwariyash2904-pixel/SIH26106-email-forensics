from email.message import EmailMessage

msg = EmailMessage()

msg["From"] = "support@paypa1-security.com"
msg["To"] = "investigator@example.com"
msg["Subject"] = "URGENT: Verify your account"
msg["User-Agent"] = "Mozilla Thunderbird 115.0"
msg["Authentication-Results"] = (
    "mx.example.com; "
    "spf=fail smtp.mailfrom=paypa1-security.com; "
    "dkim=fail header.i=@paypa1-security.com; "
    "dmarc=fail (p=REJECT) header.from=paypa1-security.com"
)

msg.set_content(
    """URGENT!

Your account has been suspended.
Click here immediately: http://paypa1-security.com/login
"""
)

with open("test_with_fail.eml", "wb") as f:
    f.write(bytes(msg))

print("Failing test email created successfully!")