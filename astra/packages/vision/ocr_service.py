from typing import Any, List, Dict

class OCRService:
    """
    Wraps an OCR engine (e.g. easyocr or pytesseract) for reading text from frames/screenshots.
    """
    def __init__(self, use_gpu: bool = False):
        self.is_loaded = True
        # self.reader = easyocr.Reader(['en'], gpu=use_gpu)

    def extract_text(self, image: Any) -> str:
        """
        Extracts text from an image/frame.
        """
        if image is None:
            return ""
            
        # result = self.reader.readtext(image, detail=0)
        # return " ".join(result)
        return "mocked OCR text from image"
