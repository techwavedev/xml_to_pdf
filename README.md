# Gerador de CVs PDF Multiplataforma (Windows, Linux, Mac) 🚀

Sistema completo em Python para gerar Currículos/CVs em PDF estilizados a partir de uma base única de dados em JSON, suportando **modelos de entrada em Word (.docx)**, **templates gráficos em HTML/CSS** e **incorporação automática de metadados ATS XML**.

> 🌐 **MULTIPLATAFORMA**: Funciona nativamente em **macOS**, **Windows** e **Linux**.
> 📌 **A SAÍDA É SEMPRE UM ARQUIVO PDF (`.pdf`)** com metadados HR-XML incorporados para robôs ATS e visual perfeito para recrutadores humanos.

---

## 💡 Como Funciona?

1. **Base Única em JSON (`.json`)**: Todos os dados do candidato (dados pessoais, contatos, resumo, conquistas, experiências de trabalho, habilidades, idiomas, formação e certificações) ficam armazenados em um único arquivo JSON.
2. **Modelo de Entrada em Word NATIVO (`--docx`)**: Você pode passar o seu arquivo `.docx` original (da pasta `Samples/`) como modelo de entrada. O sistema converte o arquivo em PDF de forma **multiplataforma** (MS Word no Windows/macOS, LibreOffice no Linux/Windows/Mac) e **remove automaticamente qualquer imagem/logo de rodapé do SprintCV**.
3. **Templates Gráficos HTML/CSS (`--template`)**: O mesmo arquivo JSON pode ser renderizado em múltiplos layouts gráficos HTML (`sprintcv_docx`, `sprintcv`, `modern`, `classic`, `tech_dark`).
4. **Conversão Automática para HR-XML**: O sistema converte o JSON automaticamente para o padrão internacional HR-XML 3.0.
5. **Otimização para ATS (Applicant Tracking Systems)**: O XML e os metadados XMP/Info são injetados diretamente dentro do PDF gerado (de forma limpa e invisível para o leitor humano).
6. **Saída em PDF (`output/`)**: Todos os arquivos gerados são salvos por padrão como `.pdf` na pasta `output/` (ignorada no Git para proteger seus dados pessoais).

---

## 🚀 Guia de Uso Rápido

### 1. Gerar PDF de Saída a partir de um Modelo `.docx` de Entrada

Para utilizar o seu arquivo `.docx` original (na pasta `Samples/`) como modelo de entrada para gerar um **PDF de saída**:

```bash
python3 cv_builder.py --json sample_cv.json --docx "Samples/modern.docx"
```

> **Resultado de Saída**: O arquivo final gerado em `output/` será um arquivo PDF (`.pdf`), limpo e com metadados ATS HR-XML incorporados!

---

### 2. Gerar PDF de Saída a partir de Templates HTML

```bash
# Template SprintCV HTML
python3 cv_builder.py --json sample_cv.json --template sprintcv_docx

# Template Modern (2 Colunas)
python3 cv_builder.py --json sample_cv.json --template modern

# Template Classic (Executivo)
python3 cv_builder.py --json sample_cv.json --template classic

# Template Tech Dark (DevOps)
python3 cv_builder.py --json sample_cv.json --template tech_dark
```

---

## 🛠️ Suporte Multiplataforma (Windows, Linux, macOS)

| Sistema Operacional | Método de Conversão DOCX -> PDF | Renderizador HTML -> PDF |
| :--- | :--- | :--- |
| **Windows** | MS Word (win32com) ou LibreOffice | Playwright (Chromium) / Chrome |
| **Linux** | LibreOffice (`soffice`) / unoconv | Playwright (Chromium) / Chrome |
| **macOS** | MS Word (`osascript`) / LibreOffice | Playwright (Chromium) / Chrome |

---

## 📁 Estrutura do Projeto

- **[cv_builder.py](file:///Users/elton/Library/CloudStorage/SynologyDrive-m1/code/xml_to_pdf/cv_builder.py)**: Script principal multiplataforma para gerar os PDFs de saída.
- **[clean_docx_completely.py](file:///Users/elton/Library/CloudStorage/SynologyDrive-m1/code/xml_to_pdf/clean_docx_completely.py)**: Utilitário que limpa rodapés e logos de arquivos `.docx`.
- **[json_to_xml.py](file:///Users/elton/Library/CloudStorage/SynologyDrive-m1/code/xml_to_pdf/json_to_xml.py)**: Converte dados JSON em arquivo HR-XML 3.0.
- **[embed_xml_cv.py](file:///Users/elton/Library/CloudStorage/SynologyDrive-m1/code/xml_to_pdf/embed_xml_cv.py)**: Injeta o XML e metadados ATS no PDF.
- **[CV_WRITING_TIPS.md](file:///Users/elton/Library/CloudStorage/SynologyDrive-m1/code/xml_to_pdf/CV_WRITING_TIPS.md)**: Guia de boas práticas de escrita de currículo.
- **[templates/](file:///Users/elton/Library/CloudStorage/SynologyDrive-m1/code/xml_to_pdf/templates)**: Pasta de templates HTML/CSS (`sprintcv_docx.html`, `sprintcv.html`, `modern.html`, `classic.html`, `tech_dark.html`).
- **[Samples/](file:///Users/elton/Library/CloudStorage/SynologyDrive-m1/code/xml_to_pdf/Samples)**: Pasta privada contendo seu arquivo `.docx` original (ignorada pelo Git).
- **[output/](file:///Users/elton/Library/CloudStorage/SynologyDrive-m1/code/xml_to_pdf/output)**: Pasta de destino dos PDFs gerados (ignorada pelo Git).
