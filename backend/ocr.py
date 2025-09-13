import pytesseract
from pdf2image import convert_from_path
from PIL import Image
import cv2
import numpy as np
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TESSERACT_PATH = os.environ.get("TESSERACT_PATH", "tesseract")
try:
    # Test if tesseract command works
    import subprocess
    subprocess.run([TESSERACT_PATH, "--version"], check=True, capture_output=True)
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH
    logger.info(f"Tesseract configured successfully: {TESSERACT_PATH}")
except Exception as e:
    logger.warning(f"Tesseract configuration failed: {e}. OCR may not work properly.")

def preprocess_image(image):
    """
    Preprocess image for OCR, handling various image modes.
    """
    try:
        # Convert image to RGB if needed
        if image.mode in ("RGBA", "LA"):
            # Convert with alpha channel handling
            background = Image.new("RGB", image.size, (255, 255, 255))
            if image.mode == "RGBA":
                background.paste(image, mask=image.split()[-1])  # alpha channel
            else:
                background.paste(image)
            image = background
        elif image.mode not in ("RGB", "L"):
            image = image.convert("RGB")
        
        # Convert to grayscale for OpenCV processing
        if image.mode == "RGB":
            gray = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)
        else:  # mode == "L" (grayscale)
            gray = np.array(image)
        
        # Apply denoising and thresholding
        denoised = cv2.fastNlMeansDenoising(gray, h=10)
        _, thresh = cv2.threshold(denoised, 150, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        return Image.fromarray(thresh)
    except Exception as e:
        logger.warning(f"Image preprocessing failed: {e}. Using original image.")
        return image

def extract_text_from_image(image_path):
    """
    Extract text from a single image file using OCR.
    """
    try:
        # Open image directly
        image = Image.open(image_path)
        processed = preprocess_image(image)
        text = pytesseract.image_to_string(processed, lang="eng")
        ocr_data = pytesseract.image_to_data(processed, lang="eng", output_type=pytesseract.Output.DICT)
        return True, text, [(image, ocr_data)]
    except Exception as e:
        logger.warning(f"Image OCR with preprocessing failed: {e}. Trying with original image.")
        try:
            # Fallback: Try OCR with original image
            image = Image.open(image_path)
            # Convert to RGB if not already for basic compatibility
            if image.mode != "RGB":
                image = image.convert("RGB")
            text = pytesseract.image_to_string(image, lang="eng")
            ocr_data = pytesseract.image_to_data(image, lang="eng", output_type=pytesseract.Output.DICT)
            return True, text, [(image, ocr_data)]
        except Exception as e2:
            logger.error(f"Image OCR extraction completely failed: {e2}")
            return False, "", []

def extract_text_from_scanned_pdf(pdf_path, dpi=300):
    """
    Extract text from a scanned PDF using OCR.
    """
    try:
        images = convert_from_path(pdf_path, dpi=dpi)
        ocr_text = ""
        ocr_data_pages = []
        for img in images:
            processed = preprocess_image(img)
            text = pytesseract.image_to_string(processed, lang="eng")
            ocr_data = pytesseract.image_to_data(processed, lang="eng", output_type=pytesseract.Output.DICT)
            ocr_text += text + "\n"
            ocr_data_pages.append((img, ocr_data))
        return True, ocr_text, ocr_data_pages
    except Exception as e:
        logger.error(f"PDF OCR extraction failed: {e}")
        return False, "", []



