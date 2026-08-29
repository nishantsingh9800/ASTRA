from typing import Any, Dict
from packages.vision.ocr_service import OCRService

class ScreenPerception:
    """
    Combines screenshots and OCR to provide visual screen context when UI Automation is insufficient.
    """
    def __init__(self, ocr_service: OCRService):
        self.ocr_service = ocr_service

    def capture_screen(self) -> Any:
        """Captures the current screen (e.g. using mss or PIL.ImageGrab)."""
        try:
            import mss
            from PIL import Image
            with mss.mss() as sct:
                monitor = sct.monitors[1]
                sct_img = sct.grab(monitor)
                return Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
        except ImportError:
            return b"mock_screenshot_data"

    def analyze_screen(self) -> Dict[str, Any]:
        """
        Takes a screenshot and runs OCR on it.
        """
        import time
        img = self.capture_screen()
        text = self.ocr_service.extract_text(img)
        
        return {
            "screenshot": img,
            "visibleText": text,
            "ocrResults": text.split() if isinstance(text, str) else [],
            "timestamp": time.time()
        }
