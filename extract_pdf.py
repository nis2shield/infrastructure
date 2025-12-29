from pypdf import PdfReader
import sys

try:
    reader = PdfReader("/Users/dipriamo.fabrizio/Desktop/nis2_infrastructure/Nis2Shield - Investment Memo .pdf")
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    print(text)
except Exception as e:
    print(f"Error reading PDF: {e}")
