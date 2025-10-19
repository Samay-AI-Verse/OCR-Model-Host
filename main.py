from fastapi import FastAPI, File, UploadFile
import pytesseract
from pdf2image import convert_from_path
import fitz  # PyMuPDF
from docx import Document
import pandas as pd
from PIL import Image
import os

app = FastAPI(title="OCR Extractor API", description="Extract text from PDF, DOCX, Images, and Excel files")

# Tesseract path inside Docker (Linux)
pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"

OCR_LANGS = "eng+hin+mar"  # Remove 'ml' for EasyOCR support

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


def extract_text_from_pdf(pdf_path):
    text = ""
    images = convert_from_path(pdf_path)
    for img in images:
        ocr_text = pytesseract.image_to_string(img, lang=OCR_LANGS)
        text += ocr_text + "\n"
    return text


def extract_text_from_image(image_path):
    img = Image.open(image_path)
    text = pytesseract.image_to_string(img, lang=OCR_LANGS)
    return text


def extract_text_from_docx(docx_path):
    doc = Document(docx_path)
    return "\n".join([para.text for para in doc.paragraphs])


def extract_text_from_excel(excel_path):
    df = pd.read_excel(excel_path, sheet_name=None)
    text = ""
    for sheet_name, sheet_df in df.items():
        text += f"\n--- Sheet: {sheet_name} ---\n"
        text += sheet_df.to_string(index=False)
    return text


@app.post("/extract-text")
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
        return {"error": "Unsupported file type"}

    return {"filename": file.filename, "extracted_text": text[:3000]}  # limit response
