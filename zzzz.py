import streamlit as st
import fitz  # PyMuPDF
from PIL import Image
import io
import os
import email
from email import policy
from email.parser import BytesParser
import msg_parser
from weasyprint import HTML

def display_pdf(file_bytes):
    # PDF aus Bytes laden
    pdf_document = fitz.open("pdf", file_bytes)

    # Durch jede Seite im PDF iterieren
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        pix = page.get_pixmap()

        # Bild aus dem Pixmap-Objekt erstellen
        img = Image.open(io.BytesIO(pix.tobytes()))

        # Bild in Streamlit anzeigen
        st.image(img, caption=f'Seite {page_num + 1}', use_column_width=True)

def eml_to_pdf(eml_content):
    # EML-Inhalt parsen
    msg = BytesParser(policy=policy.default).parsebytes(eml_content)
    html_content = msg.get_body(preferencelist=('html')).get_content()
    
    # HTML-Inhalt in eine PDF-Datei konvertieren
    pdf_bytes = HTML(string=html_content).write_pdf()
    return pdf_bytes

def msg_to_pdf(msg_file_path):
    # MSG-Datei parsen
    msg = msg_parser.Message(msg_file_path)
    html_content = msg.body
    pdf_bytes = HTML(string=html_content).write_pdf()
    return pdf_bytes

def process_uploaded_file(uploaded_file):
    file_type = uploaded_file.name.split('.')[-1]
    if file_type == 'eml':
        pdf_bytes = eml_to_pdf(uploaded_file.getvalue())
        display_pdf(pdf_bytes)
    elif file_type == 'msg':
        # Temporäre Speicherung der MSG-Datei, da extract-msg nur Dateipfade akzeptiert
        temp_msg_path = os.path.join('Data/tmp', uploaded_file.name)
        with open(temp_msg_path, 'wb') as temp_msg_file:
            temp_msg_file.write(uploaded_file.getvalue())
        pdf_bytes = msg_to_pdf(temp_msg_path)
        display_pdf(pdf_bytes)
        os.remove(temp_msg_path)  # Temporäre Datei löschen
    else:
        st.error("Unsupported file type")

def main():
    st.title('File Viewer')

    # Datei-Upload
    uploaded_file = st.file_uploader('Laden Sie eine EML- oder MSG-Datei hoch', type=['eml', 'msg'])

    if uploaded_file is not None:
        process_uploaded_file(uploaded_file)

if __name__ == "__main__":
    main()