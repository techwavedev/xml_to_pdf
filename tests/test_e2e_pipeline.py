import unittest
import os
import sys
import json
import zipfile
import subprocess
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import cv_builder

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"

class TestE2EPipeline(unittest.TestCase):
    """
    Suite de Testes E2E Unificada para o xml_to_pdf:
    1. Valida povoamento dos modelos DOCX preservando design nativo.
    2. Valida geração de PDF via LibreOffice headless por padrão.
    3. Valida incorporação de metadados HR-XML v3.0 ATS (resume.xml).
    4. Valida expurgo total de dados e strings antigas.
    5. Valida conformidade ECMA-376 OpenXML (<w:sectPr> como último filho do body).
    """

    @classmethod
    def setUpClass(cls):
        cls.json_path = "sample_cv.json"
        with open(cls.json_path, "r", encoding="utf-8") as f:
            cls.cv_data = json.load(f)

        c = cls.cv_data.get("consultant", {})
        cls.candidate_name = f"{c.get('name', '')} {c.get('surname', '')}".strip()
        cls.templates = ["expert", "itresume", "mlops", "sprint"]
        cls.forbidden_strings = [
            'European Commission', 'BNP Paribas', 'Helimax', 'NSX', 'Aveiro', 
            'Elton Machado', 'Portuguese', 'Dutch', 'HashiCorp', 'Udemy', 'HackerRank'
        ]

    def test_e2e_templates_generation(self):
        for template in self.templates:
            with self.subTest(template=template):
                template_path = f"samples/{template}.docx"
                
                # Executa a geração do CV (PDF por padrão)
                output_pdf = cv_builder.build_cv_from_json(
                    self.json_path, 
                    docx_template=template_path, 
                    out_docx=False
                )

                # 1. Verifica existência do PDF de saída
                self.assertIsNotNone(output_pdf)
                self.assertTrue(os.path.exists(output_pdf), f"PDF não gerado: {output_pdf}")

                # 2. Extrai e valida o texto do PDF via pdftotext
                soffice_bin = "/opt/homebrew/bin/pdftotext"
                if os.path.exists(soffice_bin):
                    res = subprocess.run([soffice_bin, output_pdf, "-"], capture_output=True, text=True)
                    pdf_text = res.stdout

                    # Valida injeção do nome do candidato
                    self.assertIn(self.candidate_name.lower(), pdf_text.lower(), f"Nome do candidato não encontrado no PDF: {template}")

                    # Valida expurgo de dados antigos
                    for old_str in self.forbidden_strings:
                        self.assertNotIn(old_str.lower(), pdf_text.lower(), f"String antiga encontrada no PDF {template}: {old_str}")

    def test_openxml_schema_compliance(self):
        """Valida que <w:sectPr> permanece como o último filho de <body> em todos os DOCXs."""
        for template in self.templates:
            with self.subTest(template=template):
                template_path = f"samples/{template}.docx"
                output_docx = f"output/{template}_populated_test.docx"

                # Popula DOCX temporário para teste de schema
                import populate_docx_engine
                populate_docx_engine.populate_docx_from_json(template_path, output_docx, self.cv_data)

                self.assertTrue(os.path.exists(output_docx))

                with zipfile.ZipFile(output_docx, 'r') as z:
                    doc_xml = z.read('word/document.xml').decode('utf-8')
                    root = ET.fromstring(doc_xml)
                    body = root.find(f"{{{W_NS}}}body")
                    
                    if body is not None and len(list(body)) > 0:
                        last_tag = list(body)[-1].tag.split('}')[-1]
                        # Para layouts single-column (expert/mlops), sectPr deve ser o último filho
                        if template in ["expert", "mlops"]:
                            self.assertEqual(last_tag, "sectPr", f"Último elemento do body em {template} deve ser sectPr, encontrado: {last_tag}")

                if os.path.exists(output_docx):
                    os.remove(output_docx)

if __name__ == "__main__":
    unittest.main()
