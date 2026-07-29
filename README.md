# Injetor de XML e Gerador de Currículos PDF a partir de JSON 🚀

Sistema completo em Python para gerar Currículos/CVs em PDF estilizados a partir de uma base única de dados em JSON, com suporte a **múltiplos templates gráficos** e **incorporação automática de metadados ATS XML**.

---

## 💡 Como Funciona?

1. **Base Única em JSON (`.json`)**: Todos os dados do candidato (dados pessoais, contatos, resumo, conquistas, habilidades, idiomas, formação e certificações) ficam armazenados em um único arquivo JSON.
2. **Templates Gráficos Flexíveis (`templates/`)**: O mesmo arquivo JSON pode ser renderizado em diferentes layouts gráficos HTML/CSS (`modern`, `classic`, `tech_dark`).
3. **Conversão Automática para HR-XML**: O sistema converte o JSON automaticamente para o padrão internacional HR-XML 3.0.
4. **Otimização para ATS (Applicant Tracking Systems)**: O XML e metadados XMP/Info são injetados diretamente dentro do PDF gerado. O PDF mantém um visual profissional para recrutadores humanos e uma leitura 100% precisa para robôs de ATS.
5. **Saída Segura (`output/`)**: Todos os arquivos gerados vão por padrão para a pasta `output/` (ignorada no Git para proteger seus dados pessoais).

---

## 🚀 Guia de Uso Rápido

### 1. Criar ou editar seu arquivo JSON
O projeto inclui o modelo genérico [sample_cv.json](file:///Users/elton/Library/CloudStorage/SynologyDrive-m1/code/xml_to_pdf/sample_cv.json) (com dados de exemplo "John Doe"). 

Você pode criar seu próprio arquivo JSON (ex: `meu_cv.json`). Todos os arquivos `.json` pessoais são automaticamente ignorados pelo Git!

### 2. Gerar Currículo PDF com um Template Gráfico

Escolha um dos templates disponíveis na pasta [templates/](file:///Users/elton/Library/CloudStorage/SynologyDrive-m1/code/xml_to_pdf/templates):

- **Modern** (Layout moderno em 2 colunas):
  ```bash
  python3 cv_builder.py --json meu_cv.json --template modern
  ```
- **Classic** (Layout executivo clássico):
  ```bash
  python3 cv_builder.py --json meu_cv.json --template classic
  ```
- **Tech Dark** (Tema escuro para profissionais de DevOps e Tecnologia):
  ```bash
  python3 cv_builder.py --json meu_cv.json --template tech_dark
  ```

O PDF final será salvo automaticamente em `output/` (ex: `output/John_modern_ats.pdf`).

---

## 🛠️ Comandos Adicionais

### Incorporar XML diretamente em um PDF existente:
```bash
python3 embed_xml_cv.py embed --pdf meu_curriculo.pdf --xml sample_cv.xml
```

### Verificar Metadados incorporados em um PDF:
```bash
python3 embed_xml_cv.py verify --pdf output/John_modern_ats.pdf
```

### Extrair XML de um PDF:
```bash
python3 embed_xml_cv.py extract --pdf output/John_modern_ats.pdf
```

---

## 📁 Estrutura do Projeto

- **[cv_builder.py](file:///Users/elton/Library/CloudStorage/SynologyDrive-m1/code/xml_to_pdf/cv_builder.py)**: Script principal para construir PDFs a partir de JSON + Template + HR-XML.
- **[json_to_xml.py](file:///Users/elton/Library/CloudStorage/SynologyDrive-m1/code/xml_to_pdf/json_to_xml.py)**: Converte dados JSON em arquivo HR-XML 3.0.
- **[embed_xml_cv.py](file:///Users/elton/Library/CloudStorage/SynologyDrive-m1/code/xml_to_pdf/embed_xml_cv.py)**: Injeta o XML e metadados ATS em qualquer PDF.
- **[templates/](file:///Users/elton/Library/CloudStorage/SynologyDrive-m1/code/xml_to_pdf/templates)**: Pasta **única** de templates HTML/CSS (`modern.html`, `classic.html`, `tech_dark.html`).
- **[sample_cv.json](file:///Users/elton/Library/CloudStorage/SynologyDrive-m1/code/xml_to_pdf/sample_cv.json)**: Modelo genérico de dados em JSON.
- **[output/](file:///Users/elton/Library/CloudStorage/SynologyDrive-m1/code/xml_to_pdf/output)**: Pasta onde os PDFs e XMLs gerados são gravados (ignorada no Git).
