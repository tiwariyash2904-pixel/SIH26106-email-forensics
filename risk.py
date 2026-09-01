from email import policy
from email.parser import BytesParser
import re
import hashlib


IP_PATTERN = r"\b(?:\d{1,3}\.){3}\d{1,3}\b"
URL_PATTERN = r"https?://[^\s<>\"']+"

SPF_PATTERN = r"spf=(\w+)"
DKIM_PATTERN = r"dkim=(\w+)"
DMARC_PATTERN = r"dmarc=(\w+)"


def get_mime_structure(part, depth=0):
    """
    Recursively walk the MIME tree and describe each part:
    content-type, charset, encoding, filename (if any), and children.
    """
    node = {
        "content_type": part.get_content_type(),
        "charset": part.get_content_charset(),
        "content_transfer_encoding": part.get("Content-Transfer-Encoding"),
        "is_attachment": part.get_filename() is not None,
        "filename": part.get_filename(),
        "depth": depth,
        "children": []
    }

    if part.is_multipart():
        for subpart in part.iter_parts():
            node["children"].append(
                get_mime_structure(subpart, depth + 1)
            )

    return node


def parse_email(file_path):

    with open(file_path, "rb") as f:
        message = BytesParser(
            policy=policy.default
        ).parse(f)

    # -------------------------
    # HEADER INFORMATION
    # -------------------------

    received_headers = message.get_all("Received", [])
    received_text = "\n".join(received_headers)

    received_ips = re.findall(
        IP_PATTERN,
        received_text
    )

    # -------------------------
    # USER-AGENT / X-MAILER
    # -------------------------

    # Different clients use different headers for this.
    # We check the common ones and return whichever is present.
    user_agent = (
        message.get("User-Agent")
        or message.get("X-Mailer")
        or message.get("X-MimeOLE")
        or None
    )

    # -------------------------
    # AUTHENTICATION RESULTS (SPF/DKIM/DMARC)
    # -------------------------

    auth_headers = message.get_all("Authentication-Results", [])
    auth_text = "\n".join(auth_headers)

    spf_match = re.search(SPF_PATTERN, auth_text, re.IGNORECASE)
    dkim_match = re.search(DKIM_PATTERN, auth_text, re.IGNORECASE)
    dmarc_match = re.search(DMARC_PATTERN, auth_text, re.IGNORECASE)

    authentication = {
        "spf": spf_match.group(1).lower() if spf_match else "none",
        "dkim": dkim_match.group(1).lower() if dkim_match else "none",
        "dmarc": dmarc_match.group(1).lower() if dmarc_match else "none",
        "raw": auth_headers
    }

    # -------------------------
    # EMAIL BODY (plain + html)
    # -------------------------

    body_plain = ""
    body_html = ""

    if message.is_multipart():

        for part in message.walk():

            content_type = part.get_content_type()

            if content_type == "text/plain" and not part.get_filename():
                try:
                    body_plain += part.get_content()
                except Exception:
                    pass

            elif content_type == "text/html" and not part.get_filename():
                try:
                    body_html += part.get_content()
                except Exception:
                    pass

    else:
        try:
            if message.get_content_type() == "text/html":
                body_html = message.get_content()
            else:
                body_plain = message.get_content()
        except Exception:
            pass

    # -------------------------
    # URL EXTRACTION (plain + html)
    # -------------------------

    urls = re.findall(URL_PATTERN, body_plain)
    urls += re.findall(URL_PATTERN, body_html)
    urls = list(dict.fromkeys(urls))  # de-duplicate, keep order

    # -------------------------
    # ATTACHMENT EXTRACTION
    # -------------------------

    attachments = []

    for part in message.walk():

        filename = part.get_filename()

        if filename:

            payload = part.get_payload(decode=True)

            if payload is None:
                payload = b""

            file_hash = hashlib.sha256(payload).hexdigest()

            attachments.append({
                "filename": filename,
                "content_type": part.get_content_type(),
                "size": len(payload),
                "sha256": file_hash
            })

    # -------------------------
    # MIME STRUCTURE TREE
    # -------------------------

    mime_structure = get_mime_structure(message)

    # -------------------------
    # FINAL RESULT
    # -------------------------

    return {
        "from": message.get("From"),
        "to": message.get("To"),
        "subject": message.get("Subject"),
        "date": message.get("Date"),
        "reply_to": message.get("Reply-To"),
        "return_path": message.get("Return-Path"),
        "message_id": message.get("Message-ID"),
        "user_agent": user_agent,

        "received_headers": received_headers,
        "received_ips": received_ips,

        "authentication": authentication,

        "body_plain": body_plain,
        "body_html": body_html,

        "urls": urls,
        "attachments": attachments,

        "mime_structure": mime_structure
    }