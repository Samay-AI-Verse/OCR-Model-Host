from fastapi import FastAPI, File, UploadFile
from fastapi.responses import PlainTextResponse
import pytesseract
from pdf2image import convert_from_path
from docx import Document
import pandas as pd
from PIL import Image
import os

app = FastAPI(
    title="OCR Extractor API",
    description="Extract text from PDF, DOCX, Images, and Excel files"
)

# Tesseract path inside Docker
pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"

OCR_LANGS = "eng+hin+mar"  # Only supported languages inside Docker

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# -------------------- OCR Functions --------------------

def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        images = convert_from_path(pdf_path, fmt='png', dpi=200)
        for img in images:
            ocr_text = pytesseract.image_to_string(img, lang=OCR_LANGS)
            text += ocr_text + "\n"
    except Exception as e:
        return f"PDF conversion failed: {str(e)}"
    return text

def extract_text_from_image(image_path):
    try:
        img = Image.open(image_path)
        text = pytesseract.image_to_string(img, lang=OCR_LANGS)
        return text
    except Exception as e:
        return f"Image OCR failed: {str(e)}"

def extract_text_from_docx(docx_path):
    try:
        doc = Document(docx_path)
        return "\n".join([para.text for para in doc.paragraphs])
    except Exception as e:
        return f"DOCX extraction failed: {str(e)}"

def extract_text_from_excel(excel_path):
    try:
        df = pd.read_excel(excel_path, sheet_name=None)
        text = ""
        for sheet_name, sheet_df in df.items():
            text += f"\n--- Sheet: {sheet_name} ---\n"
            text += sheet_df.to_string(index=False)
        return text
    except Exception as e:
        return f"Excel extraction failed: {str(e)}"

# -------------------- API Endpoints --------------------

@app.post("/extract-text", response_class=PlainTextResponse)
async def extract_text(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as f:
        f.write(await file.read())

    if file.filename.endswith(".pdf"):
        text = extract_text_from_pdf(file_path)
    elif file.filename.endswith((".png", ".jpg", ".jpeg")):
        text = extract_text_from_image(file_path)
    elif file.filename.endswith(".docx"):
        text = extract_text_from_docx(file_path)
    elif file.filename.endswith((".xls", ".xlsx")):
        text = extract_text_from_excel(file_path)
    else:
        return "❌ Unsupported file type"

    # Remove empty lines for cleaner output
    text = "\n".join([line for line in text.splitlines() if line.strip()])

    return text[:5000]  # Limit response size

@app.get("/health")
def health_check():
    return {"status": "ok"}
