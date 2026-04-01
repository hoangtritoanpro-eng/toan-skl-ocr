import ssl
ssl._create_default_https_context = ssl._create_unverified_context
import easyocr
import fitz
import numpy as np
from PIL import Image
from pathlib import Path
root = Path('docs')
reader = easyocr.Reader(['vi','en'], gpu=False, verbose=False)
output = []
for path in sorted(root.glob('*.pdf')):
    doc = fitz.open(path)
    page = doc[0]
    pix = page.get_pixmap(dpi=200)
    img = Image.frombytes('RGB', [pix.width, pix.height], pix.samples)
    res = reader.readtext(np.array(img))
    text = ' '.join([t for _, t, _ in res])
    output.append(f'FILE: {path.name}\npages: {len(doc)}\n{text[:5000]}\n---\n')
Path('ocr_results_all.txt').write_text('\n'.join(output), encoding='utf-8')
print('done')
