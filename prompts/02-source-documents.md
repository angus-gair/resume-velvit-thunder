You are tasked with creating a backend script that supports a frontend UI for document analysis. This script will focus on collecting and loading documents in preparation for analysis. Follow these instructions carefully:

1. Document Types and File Formats:
The script should handle the following document types and file formats:
<document_types>
PDF, Word Document, Text File, JSON File
</document_types>

<file_formats>
.pdf, .doc, .docx, .txt, .json
</file_formats>

2. Document Collection:
- Implement a function to collect documents from a specified directory or upload location.
- Ensure that only the file formats listed above are accepted.
- Validate that each file is not empty and is readable.

3. Document Loading:
- Create a function to load the contents of each collected document.
- Use appropriate libraries or methods to read each file format (e.g., 'docx' for Word documents, 'PyPDF2' for PDFs, etc.).
- For Markdown files, preserve the original formatting.

4. Preparation for Analysis:
- Store the loaded documents in a suitable data structure (e.g., a list of dictionaries) where each entry contains:
  a. The document's filename
  b. The document's content
  c. The document's type/format
- Implement basic error handling to manage issues like unreadable files or unsupported formats.

5. Output:
The script should output a JSON object with the following structure:
<output_format>
{
  "status": "success" or "error",
  "message": "Description of the result or error",
  "documents": [
    {
      "filename": "name of the file",
      "content": "text content of the document",
      "type": "file format/type"
    },
    ...
  ]
}
</output_format>

Your final output should be the Python script that implements these functionalities. Include comments to explain key parts of the code. Do not include any functionality beyond what is specified here. The script should focus solely on collecting and loading documents for future analysis.