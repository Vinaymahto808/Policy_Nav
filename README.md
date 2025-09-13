# PDF/Image Text Extraction App

A powerful Streamlit-based web application for extracting text from PDF documents and images using Optical Character Recognition (OCR). Supports both digital PDFs and scanned documents with robust image processing capabilities.

## 🚀 Features

- **PDF Text Extraction**: Extract text from both digital and scanned PDF documents
- **Image OCR**: Extract text from PNG, JPG, and JPEG image files
- **Smart Detection**: Automatically detects if a PDF is scanned or digital
- **Download Options**: Download extracted text as plain text (.txt) or structured XML
- **Visual Interface**: Clean, intuitive web interface with file upload center
- **Chat Interface**: Interactive chat section for document discussion
- **Multiple Formats**: Support for various image modes (RGB, RGBA, Grayscale)

## 🛠️ Libraries and Tools

### Core Framework
- **[Streamlit](https://streamlit.io/)** - Web application framework for creating the user interface
  - Provides file upload, text display, download buttons, and chat interface
  - Handles page configuration and layout management

### PDF Processing
- **[PyMuPDF (fitz)](https://pymupdf.readthedocs.io/)** - PDF document processing
  - Extracts text from digital PDFs
  - Retrieves PDF metadata (author, title, page count, dates)
  - Determines if a PDF is scanned or contains extractable text

### OCR (Optical Character Recognition)
- **[Tesseract](https://github.com/tesseract-ocr/tesseract)** - OCR engine (system dependency)
  - Industry-standard open-source OCR engine
  - Recognizes text in multiple languages
- **[pytesseract](https://pypi.org/project/pytesseract/)** - Python wrapper for Tesseract
  - Provides Python interface to Tesseract OCR engine
  - Handles text extraction and detailed OCR data output

### Image Processing
- **[OpenCV (cv2)](https://opencv.org/)** - Computer vision and image processing
  - Image preprocessing: grayscale conversion, denoising, thresholding
  - Enhances image quality for better OCR accuracy
  - Used in headless mode (`opencv-python-headless`) for server environments
- **[Pillow (PIL)](https://python-pillow.org/)** - Python Imaging Library
  - Image file handling and format conversion
  - Supports various image modes (RGB, RGBA, Grayscale, CMYK)
  - Handles alpha channel processing for transparent images
- **[NumPy](https://numpy.org/)** - Numerical computing library
  - Array operations for image data manipulation
  - Used by OpenCV for image processing operations

### PDF to Image Conversion
- **[pdf2image](https://pypi.org/project/pdf2image/)** - Convert PDF pages to images
  - Converts scanned PDF pages to images for OCR processing
  - Requires Poppler utilities as system dependency
- **[Poppler](https://poppler.freedesktop.org/)** - PDF rendering library (system dependency)
  - Backend for pdf2image conversion
  - Provides `pdftoppm` utility for PDF to image conversion

### Development and Utilities
- **[python-dotenv](https://pypi.org/project/python-dotenv/)** - Environment variable management
  - Loads configuration from `.env` files
  - Manages environment-specific settings
- **[watchdog](https://pypi.org/project/watchdog/)** - File system monitoring
  - Development utility for file change detection
- **[FastAPI](https://fastapi.tiangolo.com/)** & **[Uvicorn](https://www.uvicorn.org/)** - Web framework and ASGI server
  - Included for potential API extensions (currently unused)

### Optional/Extended Libraries
- **[spaCy](https://spacy.io/)** - Natural language processing
  - Advanced text processing capabilities (currently unused)
  - Can be used for text analysis and entity extraction

## 🔧 System Dependencies

### Required System Packages
- **Tesseract OCR** - OCR engine binary
- **Poppler Utils** - PDF processing utilities
- **ImageMagick** - Image manipulation toolkit

### Installation (Replit Environment)
These are automatically installed via the package manager:
```bash
# System dependencies are managed automatically
# Python dependencies are installed from requirements.txt
```

## 📁 Project Structure

```
├── app.py                 # Main Streamlit application
├── backend/               # Backend modules
│   ├── ocr.py            # OCR functionality and image processing
│   ├── pdf_loader.py     # PDF text extraction and metadata
│   ├── pdf_writer.py     # PDF writing utilities (unused)
│   ├── pii_detector.py   # PII detection (unused)
│   └── datasets/         # Sample data files
├── temp_files/           # Temporary uploaded files
├── requirements.txt      # Python dependencies
├── replit.md            # Project documentation and preferences
└── README.md            # This file
```

## 🏗️ Architecture

### Text Extraction Flow
1. **File Upload**: User uploads PDF or image file
2. **File Type Detection**: System determines file type and processing method
3. **Processing Path Selection**:
   - **Digital PDF**: Direct text extraction using PyMuPDF
   - **Scanned PDF**: Convert to images → OCR processing
   - **Image Files**: Direct OCR processing
4. **Image Preprocessing**: Enhance image quality for better OCR
   - Format normalization (handle RGBA, grayscale, etc.)
   - Noise reduction using OpenCV
   - Threshold adjustment for text clarity
5. **Text Extraction**: Extract text using Tesseract OCR
6. **Output Generation**: 
   - Display text in interface
   - Generate XML structured output
   - Provide download options

### Error Handling and Fallbacks
- **Robust Image Processing**: Handles various image formats and modes
- **OCR Fallback**: If preprocessing fails, attempts OCR on original image
- **Graceful Degradation**: Continues operation even if some features fail

## 🚀 Getting Started

### Running the Application
The application runs on Streamlit with the following configuration:
- **Host**: 0.0.0.0 (accessible from any interface)
- **Port**: 5000
- **Mode**: Headless (no browser auto-open)

### Usage Instructions
1. **Upload File**: Click "Choose a file to upload" and select a PDF or image
2. **View Results**: Extracted text appears in the text area
3. **Download**: Use download buttons for text (.txt) or XML format
4. **Chat**: Interact with the extracted content (placeholder functionality)

## 🔒 Security Considerations

- File uploads are stored in temporary directory
- No persistent storage of user data
- OCR processing is performed locally
- XML output is properly formatted and escaped

## 🎯 Performance Optimizations

- **Headless OpenCV**: Reduced memory footprint for server deployment
- **Image Preprocessing**: Optimized for OCR accuracy
- **Error Recovery**: Multiple fallback strategies for robust operation
- **Efficient File Handling**: Temporary storage with automatic cleanup

## 📈 Future Enhancements

- Integration with Large Language Models for intelligent document analysis
- Batch processing for multiple files
- Advanced text analysis and entity extraction using spaCy
- API endpoints using FastAPI for programmatic access
- Enhanced security with filename sanitization
- Progress indicators for long-running OCR operations

## 🤝 Contributing

This project uses a modular architecture making it easy to extend:
- Add new file format support in `backend/` modules
- Enhance OCR accuracy with additional preprocessing
- Integrate new text analysis capabilities
- Improve user interface with additional Streamlit components

## 📄 License

This project uses open-source libraries and tools. Please refer to individual library licenses for specific terms.