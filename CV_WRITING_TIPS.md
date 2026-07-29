# Guia de Boas Práticas para Escrita de CVs (Diretrizes SprintCV) 📄✨

Este guia integra as melhores práticas de elaboração de currículos profissionais de TI publicadas pela [SprintCV](https://www.sprintcv.com/cv-writing-tips/) com a nossa automação de geração em PDF + metadados ATS XML.

---

## 🎯 5 Princípios Fundamentais para um Currículo de TI de Alto Impacto

### 1. Conte uma História Relevante (Tell a Compelling Story)
- **Foco e Clareza**: Destaque logo no início o seu perfil executivo (`about`) e resumo profissional (`cv_summary`).
- **Resultados Quantificáveis**: Em vez de apenas listar tarefas, destaque o impacto real dos seus projetos (`relevant_accomplishments`), por exemplo: *"redução de 60% no tempo de implantação"*, *"disponibilidade de 99.99%"*.

### 2. Otimização de Palavras-Chave para ATS (Applicant Tracking Systems)
- **Nomes Exatos de Tecnologias**: Certifique-se de que linguagens, frameworks, ferramentas de nuvem (AWS, GCP, Azure), orquestradores (Kubernetes, Docker) e práticas (CI/CD, IaC, FinOps) estão explicitamente listados no campo `technical_skills`.
- **Estrutura Padronizada**: Sistemas de parsing ATS buscam seções bem definidas: *Perfil Profissional*, *Habilidades Técnicas*, *Realizações*, *Formação Acadêmica* e *Certificações*.

### 3. Formatação Gráfica Limpa e Padronizada
- **Layouts Consistentes**: Utilize templates limpos e modernos (como `sprintcv.html`, `modern.html` e `classic.html`).
- **Hierarquia Visual**: Títulos em destaque, fontes legíveis e bom espaçamento entre elementos facilitam a leitura para recrutadores humanos.

### 4. Proteção e Privacidade dos Dados (Data Protection / GDPR)
- **Informações Sensíveis**: Evite expor números de documentos pessoais (CPF, Passaporte) ou endereços residenciais completos no CV. Utilize Cidade e País.
- **GitIgnore Ativo**: Seu arquivo JSON pessoal (ex: `meu_cv.json`) fica protegido localmente na pasta ignorada pelo Git.

### 5. Dados Estruturados em JSON como Fonte da Verdade
- Manter o currículo em um único formato JSON estruturado permite gerar **múltiplos PDFs gráficos** e garantir que todas as ferramentas automáticas leiam exatamente os mesmos dados via **HR-XML incorporado**.

---

## 🚀 Como Aplicar as Diretrizes no cv_builder

Para gerar o seu currículo aplicando 100% o layout e diretrizes do SprintCV com injeção de XML para ATS, execute:

```bash
python3 cv_builder.py --json sample_cv.json --template sprintcv
```
