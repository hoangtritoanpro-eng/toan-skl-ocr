import ssl
ssl._create_default_https_context = ssl._create_unverified_context

from pathlib import Path
import fitz
import easyocr
import numpy as np
from PIL import Image

BASE = Path(__file__).resolve().parent
PDF_DIR = BASE / 'skl_agent_kit-main' / 'docs'
OUT_DIR = BASE / 'skl_agent_kit-main' / 'extracted_markdown'
OUT_DIR.mkdir(parents=True, exist_ok=True)

print('PDF_DIR=', PDF_DIR)
print('OUT_DIR=', OUT_DIR)

reader = easyocr.Reader(['vi', 'en'], gpu=False, verbose=False)
print('OCR reader ready')

pdfs = sorted(PDF_DIR.glob('*.pdf'))
print('Found', len(pdfs), 'pdf files')

for pdf_path in pdfs:
    print('Processing', pdf_path.name)
    doc = fitz.open(pdf_path)
    out_path = OUT_DIR / (pdf_path.stem + '.md')
    lines = [f'# {pdf_path.name}', '']
    for page_num in range(len(doc)):
        page = doc[page_num]
        page_text = page.get_text('text').strip()
        lines.append(f'## Page {page_num + 1}')
        if len(page_text) > 100:
            lines.append(page_text)
        else:
            pix = page.get_pixmap(dpi=150)
            mode = 'RGBA' if pix.alpha else 'RGB'
            img = Image.frombytes(mode, [pix.width, pix.height], pix.samples)
            arr = np.array(img)
            result = reader.readtext(arr, detail=0)
            if result:
                lines.extend(result)
            else:
                lines.append('*[no text detected]*')
        lines.append('')
    out_path.write_text('\n'.join(lines), encoding='utf-8')
    print('Wrote', out_path)

print('Done')
