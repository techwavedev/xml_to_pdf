#!/usr/bin/env python3
"""
generate_sample_pdf.py
Script auxiliar simples para gerar um arquivo PDF básico para testar o embed_xml_cv.py.
"""

def create_simple_pdf(filename: str = "sample_cv.pdf"):
    pdf_content = (
        b"%PDF-1.4\n"
        b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n"
        b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n"
        b"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>\nendobj\n"
        b"4 0 obj\n<< /Length 175 >>\nstream\n"
        b"BT\n"
        b"/F1 24 Tf\n"
        b"50 720 Td\n"
        b"(John Doe - Senior Software Engineer) Tj\n"
        b"0 -36 Td\n"
        b"/F1 12 Tf\n"
        b"(Email: john.doe@example.com | Phone: +1-555-0199) Tj\n"
        b"0 -24 Td\n"
        b"(Skills: Python, Go, Docker, Kubernetes, AWS, PostgreSQL) Tj\n"
        b"0 -24 Td\n"
        b"(Experience: Staff Engineer at Tech Solutions Inc.) Tj\n"
        b"ET\n"
        b"endstream\nendobj\n"
        b"5 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n"
        b"xref\n"
        b"0 6\n"
        b"0000000000 65535 f \n"
        b"0000000009 00000 n \n"
        b"0000000058 00000 n \n"
        b"0000000115 00000 n \n"
        b"0000000246 00000 n \n"
        b"0000000472 00000 n \n"
        b"trailer\n<< /Size 6 /Root 1 0 R >>\n"
        b"startxref\n543\n"
        b"%%EOF\n"
    )
    with open(filename, "wb") as f:
        f.write(pdf_content)
    print(f"[✓] Currículo PDF de teste criado com sucesso: '{filename}'")

if __name__ == "__main__":
    create_simple_pdf()
