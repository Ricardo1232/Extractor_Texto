# Text Extraction Tool

A powerful Python-based tool for extracting text from PDF documents with advanced preprocessing and OCR capabilities.

## Features

- Multi-engine text extraction (Tesseract OCR and EasyOCR)
- Advanced image preprocessing for improved accuracy
- Support for multiple languages
- Automatic error handling and logging
- Progress tracking with status bar
- Grammar and spelling correction

## Prerequisites

- Python 3.x
- Tesseract OCR installed on your system
- Required Python packages (listed in requirements below)

## Installation

1. Clone this repository:
   ```bash
   git clone [your-repository-url]
   cd ext_text
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv myenv
   myenv\Scripts\activate  # On Windows
   source myenv/bin/activate  # On Unix/MacOS
   ```

3. Install required packages:
   ```bash
   pip install opencv-python pytesseract PyMuPDF numpy tqdm easyocr language-tool-python spacy
   ```

4. Download the English language model for spaCy:
   ```bash
   python -m spacy download en_core_web_sm
   ```

## Usage

```python
from src.file_text_extractor import extract_text_from_pdf

# Extract text from a PDF file
pdf_path = 'path/to/your/document.pdf'
output_txt_path = 'output.txt'

extract_text_from_pdf(pdf_path, output_txt_path)
```

## How It Works

The tool employs a sophisticated text extraction pipeline:

1. **PDF Processing**: Converts PDF pages to images
2. **Image Preprocessing**:
   - Resolution enhancement
   - Grayscale conversion
   - Illumination normalization
   - Noise reduction
   - Adaptive thresholding
3. **Text Extraction**:
   - Dual OCR engine processing (Tesseract and EasyOCR)
   - Text combination using voting algorithm
4. **Post-processing**:
   - Grammar and spelling correction
   - Text cleanup and formatting

## Configuration

You can customize the Tesseract path in `file_text_extractor.py`:

```python
pytesseract.tesseract_cmd = r"C:/Program Files/Tesseract-OCR/tesseract.exe"
```

## Output

The extracted text is saved to the specified output file with:
- Preserved text structure
- Corrected grammar and spelling
- Clean formatting

## Error Handling

The tool includes comprehensive error handling with:
- Detailed logging
- Progress tracking
- Audible notifications for process completion or errors

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.