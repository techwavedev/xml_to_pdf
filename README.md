# Gerador de CVs PDF com Suporte a Templates DOCX & Otimização ATS HR-XML 🚀

Sistema completo em Python para gerar Currículos/CVs em PDF estilizados a partir de uma base única de dados em JSON, suportando **templates nativos do Word (.docx)**, **templates gráficos em HTML/CSS** e **incorporação automática de metadados ATS XML**.

---

## 💡 Como Funciona?

1. **Base Única em JSON (`.json`)**: Todos os dados do candidato (dados pessoais, contatos, resumo, conquistas, experiências de trabalho, habilidades, idiomas, formação e certificações) ficam armazenados em um único arquivo JSON.
2. **Templates em Word Nativos (`.docx`)**: Você pode passar diretamente o seu modelo `.docx` original (da pasta `Samples/`) com a flag `--docx`. O sistema converte o arquivo via Microsoft Word do macOS com **100% de fidelidade visual** e **remove automaticamente qualquer imagem/logo de rodapé do SprintCV**.
3. **Templates Gráficos HTML/CSS (`templates/`)**: O mesmo arquivo JSON pode ser renderizado em múltiplos layouts gráficos HTML (`sprintcv_docx`, `sprintcv`, `modern`, `classic`, `tech_dark`).
4. **Conversão Automática para HR-XML**: O sistema converte o JSON automaticamente para o padrão internacional HR-XML 3.0.
5. **Otimização para ATS (Applicant Tracking Systems)**: O XML e os metadados XMP/Info são injetados diretamente dentro do PDF gerado (de forma limpa e invisível para o leitor humano).
6. **Saída Segura (`output/`)**: Todos os arquivos gerados vão por padrão para a pasta `output/` (ignorada no Git para proteger seus dados pessoais).

---

## 🚀 Guia de Uso Rápido

### 1. Gerar PDF a partir de um Modelo NATIVO em Word (`.docx`)

Para utilizar o seu arquivo `.docx` original (na pasta `Samples/`) como modelo exato de design:

```bash
python3 cv_builder.py --json sample_cv.json --docx "Samples/Sprint CV Elton Machado 20260729 085709.docx"
```

> **Nota**: O sistema limpa automaticamente qualquer imagem/logo de rodapé do `.docx` antes de gerar o PDF final!

---

### 2. Gerar PDF com Templates Gráficos HTML

Escolha um dos templates disponíveis na pasta [templates/](file:///Users/elton/Library/CloudStorage/SynologyDrive-m1/code/xml_to_pdf/templates):

```bash
# Template SprintCV HTML (Design baseado no SprintCV)
python3 cv_builder.py --json sample_cv.json --template sprintcv_docx

# Template Modern (2 Colunas com barra lateral escura)
python3 cv_builder.py --json sample_cv.json --template modern

# Template Classic (Estilo Executivo)
python3 cv_builder.py --json sample_cv.json --template classic

# Template Tech Dark (Tema escuro para DevOps & TI)
python3 cv_builder.py --json sample_cv.json --template tech_dark
```

---

## 🛠️ Opções do Comando `cv_builder.py`

| Parâmetro | Descrição | Exemplo |
| :--- | :--- | :--- |
| `--json` | Arquivo JSON com a base de dados do CV | `--json sample_cv.json` |
| `--docx` | Arquivo template nativo em Word (`.docx`) | `--docx "Samples/meu_modelo.docx"` |
| `--template` | Nome do template HTML na pasta `templates/` | `--template sprintcv_docx` |
| `--out` | Caminho personalizado para salvar o PDF de saída | `--out output/meu_cv_final.pdf` |
| `--list-templates` | Lista todos os templates HTML disponíveis | `--list-templates` |

---

## 📁 Estrutura do Projeto

- **[cv_builder.py](file:///Users/elton/Library/CloudStorage/SynologyDrive-m1/code/xml_to_pdf/cv_builder.py)**: Script mestre de orquestração do pipeline.
- **[clean_docx_completely.py](file:///Users/elton/Library/CloudStorage/SynologyDrive-m1/code/xml_to_pdf/clean_docx_completely.py)**: Utilitário que limpa rodapés e logos de arquivos `.docx`.
- **[json_to_xml.py](file:///Users/elton/Library/CloudStorage/SynologyDrive-m1/code/xml_to_pdf/json_to_xml.py)**: Converte dados JSON em arquivo HR-XML 3.0.
- **[embed_xml_cv.py](file:///Users/elton/Library/CloudStorage/SynologyDrive-m1/code/xml_to_pdf/embed_xml_cv.py)**: Injeta o XML e metadados ATS em qualquer PDF.
- **[CV_WRITING_TIPS.md](file:///Users/elton/Library/CloudStorage/SynologyDrive-m1/code/xml_to_pdf/CV_WRITING_TIPS.md)**: Guia de boas práticas de escrita de currículo.
- **[templates/](file:///Users/elton/Library/CloudStorage/SynologyDrive-m1/code/xml_to_pdf/templates)**: Pasta de templates HTML/CSS (`sprintcv_docx.html`, `sprintcv.html`, `modern.html`, `classic.html`, `tech_dark.html`).
- **[Samples/](file:///Users/elton/Library/CloudStorage/SynologyDrive-m1/code/xml_to_pdf/Samples)**: Pasta privada contendo seu arquivo `.docx` original (ignorada pelo Git).
- **[output/](file:///Users/elton/Library/CloudStorage/SynologyDrive-m1/code/xml_to_pdf/output)**: Pasta de destino dos PDFs e XMLs gerados (ignorada pelo Git).
