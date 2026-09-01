from fastapi import FastAPI, UploadFile, File
from email_parser import parse_email
import tempfile
import os

app = FastAPI(
    title="SIH26106 Email Forensics API",
    description="AI-Powered Email Threat Detection & Forensic Intelligence Platform",
    version="1.0.0"
)


@app.get("/")
def home():
    return {
        "message": "SIH26106 Email Forensics API is running!"
    }


@app.post("/analyze-email")
async def analyze_email(file: UploadFile = File(...)):

    # Create temporary file
    with tempfile.NamedTemporaryFile(delete=False) as temp:
        contents = await file.read()
        temp.write(contents)
        temp_path = temp.name

    try:
        # Parse email
        result = parse_email(temp_path)

        return {
            "filename": file.filename,
            "analysis": result
        }

    finally:
        # Delete temporary file
        os.remove(temp_path)