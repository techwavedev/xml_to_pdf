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

## 🚀 Guia de Uso Rápido

### 1. Prepare seus dados XML do Currículo
Personalize o arquivo `sample_cv.xml` ou crie seu próprio arquivo `resume.xml` com seus dados pessoais (Contato, Habilidades, Experiência, Educação).

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Resume xmlns="http://ns.hr-xml.org/2007-04-15" version="3.0">
  <StructuredXMLResume>
    <ContactInfo>
      <PersonName>
        <GivenName>João</GivenName>
        <FamilyName>Silva</FamilyName>
      </PersonName>
      <ContactMethod>
        <InternetEmailAddress>joao.silva@example.com</InternetEmailAddress>
      </ContactMethod>
    </ContactInfo>
    <CoreCompetencies>
      <Skill>Python</Skill>
      <Skill>FastAPI</Skill>
      <Skill>Docker</Skill>
    </CoreCompetencies>
  </StructuredXMLResume>
</Resume>
```

### 2. Incorporar o XML no Currículo PDF
Execute o comando `embed`:

```bash
python3 embed_xml_cv.py embed --pdf meu_curriculo.pdf --xml sample_cv.xml --out meu_curriculo_ats.pdf
```

### 3. Verificar os Metadados e Anexos Incorporados
Confirme se o fluxo XML e os anexos foram incorporados corretamente:

```bash
python3 embed_xml_cv.py verify --pdf meu_curriculo_ats.pdf
```

### 4. Extrair o XML de um Currículo PDF
Extraia o XML estruturado de volta do arquivo PDF:

```bash
python3 embed_xml_cv.py extract --pdf meu_curriculo_ats.pdf --out resume_extraido.xml
```

---

## 📁 Estrutura dos Arquivos

- `embed_xml_cv.py`: Ferramenta principal em linha de comando (CLI) para incorporar, verificar e extrair XML em PDFs.
- `sample_cv.xml`: Modelo padrão no formato HR-XML pronto para ser personalizado.
- `generate_sample_pdf.py`: Script auxiliar para gerar um PDF de teste.
- `requirements.txt`: Arquivo de dependências (`pypdf`).
