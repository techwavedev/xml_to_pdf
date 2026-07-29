# XML to PDF CV Builder

Un motor genérico em Python para conversão de currículos **JSON → DOCX (Design Nativo) → PDF (Com Metadados HR-XML ATS)**.

---

## 🎯 Principais Recursos

1. **Design 100% Nativo a partir de Modelos DOCX**:
   - Preserva layout, colunas, tabelas de 2 colunas, bordas, marcas d'água e molduras de avatar de qualquer arquivo `.docx` em `samples/`.
2. **Conteúdo 100% Oriundo do JSON**:
   - Povoa nome, contatos, resumo, experiências, habilidades, educação, certificações e idiomas exclusivamente a partir de `sample_cv.json`.
3. **Purga Total de Dados Não Relacionados**:
   - Remove automaticamente empregos antigos, habilidades não mapeadas (ex: `NSX`), localizações e idiomas que não pertençam ao JSON do candidato.
4. **Geração PDF-First (Headless via LibreOffice)**:
   - Converte diretamente para PDF em ~0.5s sem abrir interface gráfica do Word (`soffice --headless`).
   - Apaga arquivos `.docx` temporários por padrão (a menos que a flag `--out-docx` seja fornecida).
5. **Conformidade HR-XML v3.0 ATS**:
   - Incorpora `resume.xml` com metadados estruturados para robôs de recrutamento (ATS).

---

## 🚀 Como Usar

### Geração Padrão (Saída Exclusiva em PDF):
```bash
python3 cv_builder.py --json sample_cv.json --docx expert
```

### Mantendo também o arquivo DOCX populado:
```bash
python3 cv_builder.py --json sample_cv.json --docx expert --out-docx
```

### Lista de Modelos Disponíveis:
```bash
python3 cv_builder.py --list-samples
```

---

## 🧪 Suíte de Testes Unificada E2E

Para executar a validação completa de geração de PDFs, expurgo de dados antigos e conformidade OpenXML:

```bash
python3 tests/test_e2e_pipeline.py
```
