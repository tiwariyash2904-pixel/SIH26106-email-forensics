def calculate_auth_risk(authentication: dict) -> int:
    risk = 0

    spf = authentication.get("spf", "none")
    dkim = authentication.get("dkim", "none")
    dmarc = authentication.get("dmarc", "none")

    if spf == "fail":
        risk += 30
    elif spf == "softfail":
        risk += 20
    elif spf == "none":
        risk += 10

    if dkim == "fail":
        risk += 30
    elif dkim == "none":
        risk += 10

    if dmarc == "fail":
        risk += 40
    elif dmarc == "none":
        risk += 20

    return min(risk, 100)
