import logging, io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from PIL import Image

logger = logging.getLogger(__name__)

class PDFGenerator:
    @staticmethod
    def generate(images_list: list[bytes], output_path: str) -> bool:
        if not images_list: return False
        try:
            c = canvas.Canvas(output_path, pagesize=letter)
            pw, ph = letter
            for img_bytes in images_list:
                stream = io.BytesIO(img_bytes)
                iw, ih = Image.open(stream).size
                scale = min(pw / iw, ph / ih, 1.0)
                sw, sh = iw * scale, ih * scale
                c.drawImage(ImageReader(stream), (pw - sw)/2, (ph - sh)/2, width=sw, height=sh, mask='auto')
                c.showPage()
            c.save()
            return True
        except Exception as e:
            logger.error(f"PDF Error: {e}")
            return False