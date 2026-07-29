# Workspace Rules: xml_to_pdf

## DOCX-to-PDF Template Engine Standards

When building or modifying generic DOCX-to-PDF population engines:

1. **Autonomous Agent Testing & Self-Verification Loop**:
   - The AI assistant **MUST ALWAYS** run all build, conversion, and verification commands autonomously in an internal test loop.
   - **NEVER** ask or rely on the user to run test commands in their terminal.
   - Automatically verify outputs (PDF text extraction, XML schema validation, image rendering) and iterate until 100% of tests pass cleanly.

2. **PDF-First Default Output**:
   - The primary and default deliverable is the **PDF file** (`output/<template>_<candidate>_ats.pdf`) with embedded HR-XML v3.0 ATS metadata (`resume.xml`).
   - Temporary intermediate `.docx` files generated during conversion **MUST NOT** be kept in `output/` unless the user explicitly passes the `--out-docx` flag.

3. **Headless Execution**:
   - Convert populated DOCX files directly to PDF using LibreOffice CLI (`soffice --headless`).
   - Never call desktop GUI apps via AppleScript (`osascript`) or `win32com`.

4. **Visual Design vs. Text Content Isolation**:
   - Retain 100% of the visual layout (colors, fonts, borders, background watermarks, header photo frames, 2-column table grids) from the sample `.docx` template.
   - Replace 100% of writing content exclusively with data from the candidate JSON feed.

5. **Strict Content Purge**:
   - Remove all old sample data, job histories, unmapped skills, old locations, old certifications, and old language entries not present in the input JSON.

6. **Zero Hardcoding**:
   - Use generic XML container targeting and dynamic RegEx engines—never hardcode specific company names, candidate names, or universities in Python code.

7. **Native Style Preservation**:
   - Do not inject custom font colors (e.g. `<w:color>`); allow paragraphs to inherit native heading styles (`<w:pStyle w:val="Heading1"/>`) directly from `word/styles.xml`.

8. **ECMA-376 OpenXML Compliance**:
   - Preserve `<w:tcPr>` element properties when updating table cells to maintain column widths, borders, and cell padding.
   - Ensure `<w:sectPr>` (Section Properties) remains the absolute final child element of `<body>` to prevent Microsoft Word "unreadable content" recovery dialogs.
