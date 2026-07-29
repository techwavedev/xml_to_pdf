# Injetor de XML para Currículos PDF (Otimização ATS) 🚀

Script automatizado em Python para incorporar metadados XML estruturados e anexos de arquivos em Currículos/CVs no formato PDF.

---

## 💡 Por que incorporar XML no seu Currículo PDF?

Sistemas de Rastreamento de Candidatos (ATS - *Applicant Tracking Systems*), como Workday, Greenhouse, Lever, Taleo e DaXtra, analisam currículos para extrair automaticamente informações dos candidatos (Nome, Contato, Histórico Profissional, Formação Acadêmica e Habilidades).

A leitura padrão de texto em PDFs pode sofrer com quebras de linha acidentais, problemas de alinhamento em colunas e erros de codificação de fontes.

Esta ferramenta incorpora dados estruturados no padrão internacional **HR-XML** diretamente dentro do contêiner do seu PDF em **3 camadas complementares**:

1. **Anexo de Arquivo PDF (`/EmbeddedFiles`)**: Anexa o arquivo `resume.xml` diretamente dentro do PDF. Leitores modernos de PDF/A-3 e sistemas ATS extraem arquivos anexos automaticamente.
2. **Fluxo de Metadados XMP (`/Metadata`)**: Injeta um pacote XMP RDF com dados estruturados do candidato na raiz do catálogo do PDF.
3. **Informações do Documento (`/Info`)**: Atualiza os campos de metadados (`/Keywords`, `/Author`, `/Title`, `/Subject`) para garantir que extratores legados de ATS leiam as principais habilidades e informações sem erros.

Seu currículo em PDF mantém seu visual gráfico original e elegante, enquanto carrega dados XML 100% precisos e legíveis por máquina para ferramentas de automação ATS.

---

## 🛠️ Requisitos e Instalação

- **Python**: 3.8+ (Suporta execução nativa sem dependências externas!)
- **Opcional**: `pip install pypdf` (Recomendado para operações avançadas de PDF)

---

## 🚀 Guia de Uso Rápido (Saída Padrão na Pasta `output/`)

### 1. Prepare seus dados XML do Currículo
Personalize o arquivo `sample_cv.xml` ou crie seu próprio arquivo `resume.xml` com seus dados pessoais (Contato, Habilidades, Experiência, Educação).

### 2. Incorporar o XML no Currículo PDF
Por padrão, a saída será gerada **automaticamente na pasta `output/`**:

```bash
# Gera o arquivo otimizado em: output/meu_curriculo_ats.pdf
python3 embed_xml_cv.py embed --pdf meu_curriculo.pdf --xml sample_cv.xml
```

*(Opcional: Você pode especificar um nome personalizado com `--out meu_nome.pdf`, e o script salvará em `output/meu_nome.pdf`).*

### 3. Verificar os Metadados e Anexos Incorporados
Verifique o arquivo gerado na pasta `output/`:

```bash
python3 embed_xml_cv.py verify --pdf output/meu_curriculo_ats.pdf
```

### 4. Extrair o XML de um Currículo PDF
Extrai o XML de volta do PDF (salva por padrão em `output/resume_extraido.xml`):

```bash
python3 embed_xml_cv.py extract --pdf output/meu_curriculo_ats.pdf
```

---

## 🔒 Controle de Versão (Git / .gitignore)

A pasta `output/`, os arquivos de saída `.pdf`, `.xml` extraídos e templates pessoais estão ignorados no [.gitignore](file:///Users/elton/Library/CloudStorage/SynologyDrive-m1/code/xml_to_pdf/.gitignore) para garantir que seus currículos gerados não sejam sincronizados acidentalmente no repositório.

---

## 📁 Estrutura dos Arquivos

- `embed_xml_cv.py`: Ferramenta principal em linha de comando (CLI) para incorporar, verificar e extrair XML em PDFs.
- `sample_cv.xml`: Modelo padrão no formato HR-XML pronto para ser personalizado.
- `output/`: Pasta de saída padrão para onde todos os PDFs e XMLs gerados são gravados (ignorada no Git).
- `generate_sample_pdf.py`: Script auxiliar para gerar um PDF de teste.
- `requirements.txt`: Arquivo de dependências (`pypdf`).
