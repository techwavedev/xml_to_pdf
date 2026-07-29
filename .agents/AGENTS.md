# Workspace Rules: xml_to_pdf

## DOCX-to-PDF Template Engine Standards

When building or modifying generic DOCX-to-PDF population engines:

1. **Headless Execution**: Convert DOCX to PDF using LibreOffice CLI (`soffice --headless`). Never call desktop GUI apps via AppleScript (`osascript`) or `win32com`.
2. **Visual Design vs. Text Content**:
   - Retain 100% of the visual layout (colors, fonts, borders, background watermarks, header photo frames, 2-column table grids) from the sample `.docx` template.
   - Replace 100% of writing content exclusively with data from the candidate JSON feed.
3. **Strict Content Purge**: Remove all old sample data, job histories, unmapped skills, old locations, and old language entries not present in the input JSON.
4. **Zero Hardcoding**: Use generic XML container targeting and dynamic RegEx engines—never hardcode specific company names, candidate names, or universities in code.
5. **Native Style Preservation**: Do not inject custom font colors (e.g. `<w:color>`); allow paragraphs to inherit native heading styles (`<w:pStyle w:val="Heading1"/>`) directly from `word/styles.xml`.
6. **ECMA-376 OpenXML Compliance**: Preserve `<w:tcPr>` element properties when updating table cells to maintain column widths, borders, and cell padding.
