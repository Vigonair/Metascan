import os
import uuid

PDF_DIR = os.path.join("uploads", "pdfs")

def save_pdf_permanently(uploaded_file) -> str:
    """
    Saves uploaded PDF to uploads/pdfs/{uuid}.pdf
    Returns the stored file path.
    """
    os.makedirs(PDF_DIR, exist_ok=True)

    unique_name = f"{uuid.uuid4().hex}.pdf"
    final_path = os.path.join(PDF_DIR, unique_name)

    with open(final_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    return final_path
