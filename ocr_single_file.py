import ssl
ssl._create_default_https_context = ssl._create_unverified_context

from pathlib import Path
import fitz
import easyocr
import numpy as np
from PIL import Image

BASE = Path(__file__).resolve().parent
PDF_DIR = BASE / 'skl_agent_kit-main' / 'docs'
OUTPUT_DIR = BASE / 'skl_agent_kit-main' / 'extracted_markdown'
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

PDF_FILE = 'sach-bai-tap-toan-6-tap-1-ket-noi-tri-thuc-voi-cuoc-song.pdf'
PDF_PATH = PDF_DIR / PDF_FILE
if not PDF_PATH.exists():
    raise FileNotFoundError(PDF_PATH)

print('Processing', PDF_PATH)
reader = easyocr.Reader(['vi', 'en'], gpu=False, verbose=False)
print('OCR reader ready')

doc = fitz.open(PDF_PATH)
output_lines = [f'# {PDF_FILE}', '']
for page_num, page in enumerate(doc, start=1):
    output_lines.append(f'## Page {page_num}')
    page_text = page.get_text('text').strip()
    if len(page_text) > 120:
        output_lines.append(page_text)
    else:
        pix = page.get_pixmap(dpi=150)
        mode = 'RGBA' if pix.alpha else 'RGB'
        img = Image.frombytes(mode, [pix.width, pix.height], pix.samples)
        arr = np.array(img)
        result = reader.readtext(arr, detail=0)
        if result:
            output_lines.extend(result)
        else:
            output_lines.append('*[no text detected]*')
    output_lines.append('')

out_path = OUTPUT_DIR / (PDF_PATH.stem + '.md')
out_path.write_text('\n'.join(output_lines), encoding='utf-8')
print('Wrote', out_path)
