# Injetor de XML e Gerador de Currículos PDF a partir de JSON 🚀

Sistema completo em Python para gerar Currículos/CVs em PDF estilizados a partir de uma base única de dados em JSON, com suporte a **templates nativos em Word (.docx)**, **templates gráficos HTML/CSS** e **incorporação automática de metadados ATS XML**.

---

## 💡 Como Funciona?

1. **Base Única em JSON (`.json`)**: Todos os dados do candidato (dados pessoais, contatos, resumo, conquistas, habilidades, idiomas, formação e certificações) ficam armazenados em um único arquivo JSON.
2. **Uso de Templates DOCX Nativos (`.docx`)**: Você pode passar diretamente o seu arquivo `.docx` original (da pasta `Samples/`) como modelo para gerar um PDF com **100% de fidelidade visual exata** do Word.
3. **Templates Gráficos HTML/CSS (`templates/`)**: O mesmo arquivo JSON pode ser renderizado em diferentes layouts gráficos (`sprintcv_docx`, `sprintcv`, `modern`, `classic`, `tech_dark`).
4. **Conversão Automática para HR-XML**: O sistema converte o JSON automaticamente para o padrão internacional HR-XML 3.0.
5. **Otimização para ATS (Applicant Tracking Systems)**: O XML e metadados XMP/Info são injetados diretamente dentro do PDF gerado (de forma limpa e invisível para o leitor humano).
6. **Saída Segura (`output/`)**: Todos os arquivos gerados vão por padrão para a pasta `output/` (ignorada no Git para proteger seus dados pessoais).

---

## 🚀 Guia de Uso Rápido

### 1. Gerar PDF com 100% de Fidelidade Visual a partir do seu Modelo `.docx`

Para converter e gerar o PDF exatamente idêntico ao seu arquivo `.docx` original (da pasta `Samples/`) com injeção de metadados ATS HR-XML:

```bash
python3 cv_builder.py --json sample_cv.json --docx "Samples/Sprint CV Elton Machado 20260729 085709.docx"
```

---

### 2. Gerar Currículo PDF com Templates Gráficos HTML

Escolha um dos templates disponíveis na pasta [templates/](file:///Users/elton/Library/CloudStorage/SynologyDrive-m1/code/xml_to_pdf/templates):

```bash
# Template SprintCV HTML
python3 cv_builder.py --json sample_cv.json --template sprintcv_docx

# Template Modern (2 Colunas)
python3 cv_builder.py --json sample_cv.json --template modern

# Template Executive Classic
python3 cv_builder.py --json sample_cv.json --template classic

# Template Tech Dark
python3 cv_builder.py --json sample_cv.json --template tech_dark
```

---

## 📁 Estrutura do Projeto

- **[cv_builder.py](file:///Users/elton/Library/CloudStorage/SynologyDrive-m1/code/xml_to_pdf/cv_builder.py)**: Script principal com suporte a templates `.docx` e HTML.
- **[json_to_xml.py](file:///Users/elton/Library/CloudStorage/SynologyDrive-m1/code/xml_to_pdf/json_to_xml.py)**: Converte dados JSON em arquivo HR-XML 3.0.
- **[embed_xml_cv.py](file:///Users/elton/Library/CloudStorage/SynologyDrive-m1/code/xml_to_pdf/embed_xml_cv.py)**: Injeta o XML e metadados ATS em qualquer PDF.
- **[CV_WRITING_TIPS.md](file:///Users/elton/Library/CloudStorage/SynologyDrive-m1/code/xml_to_pdf/CV_WRITING_TIPS.md)**: Guia de boas práticas de escrita de currículo.
- **[Samples/](file:///Users/elton/Library/CloudStorage/SynologyDrive-m1/code/xml_to_pdf/Samples)**: Pasta privada contendo seu arquivo `.docx` original.
- **[output/](file:///Users/elton/Library/CloudStorage/SynologyDrive-m1/code/xml_to_pdf/output)**: Pasta de destino dos PDFs gerados (ignorada no Git).
