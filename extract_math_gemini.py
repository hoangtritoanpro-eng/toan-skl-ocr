import os
import io
from pathlib import Path

# Thư viện xử lý PDF và Ảnh
import fitz  # pip install PyMuPDF
from PIL import Image

# Thư viện Google GenAI (Gemini)
try:
    from google import genai
    from google.genai import types
except ImportError:
    print("Vui lòng cài đặt thư viện: pip install google-genai PyMuPDF Pillow")
    exit(1)

# Kiểm tra API Key
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    print("LỖI: Chưa cấu hình GEMINI_API_KEY!")
    print("Vui lòng chạy lệnh: set GEMINI_API_KEY=your_api_key (Windows) hoặc export GEMINI_API_KEY=your_api_key (Mac/Linux)")
    exit(1)

client = genai.Client(api_key=api_key)

# Cấu hình đường dẫn
BASE = Path(__file__).resolve().parent
PDF_DIR = BASE / 'skl_agent_kit-main' / 'docs'
OUT_DIR = BASE / 'skl_agent_kit-main' / 'extracted_markdown_gemini'
OUT_DIR.mkdir(parents=True, exist_ok=True)

print(f"Thư mục nguồn: {PDF_DIR}")
print(f"Thư mục đích: {OUT_DIR}")

prompt = """
You are an expert OCR system for mathematics.
Extract all text and mathematical formulas from this image.
Preserve the exact layout, question numbers, and choices (A, B, C, D) if any.
CRITICAL INSTRUCTIONS:
- Use inline LaTeX `$...$` for inline math equations.
- Use block LaTeX `$$...$$` for block math equations.
- Maintain the Vietnamese language exactly as written.
- Start multiple choice options on new lines.
- Do not add any conversational text. Only output the extracted content in Markdown.
"""

def process_pdfs():
    pdfs = sorted(PDF_DIR.glob('*.pdf'))
    if not pdfs:
        print("Không tìm thấy file PDF nào trong thư mục docs/")
        return

    print(f"Tìm thấy {len(pdfs)} file PDF. Bắt đầu OCR bằng Gemini 2.5 Flash...")

    for pdf_path in pdfs:
        print(f"\n--- Đang xử lý: {pdf_path.name} ---")
        doc = fitz.open(pdf_path)
        out_path = OUT_DIR / (pdf_path.stem + '.md')
        
        # Bỏ qua nếu đã OCR rồi (tiết kiệm API)
        if out_path.exists():
            print(f"File {out_path.name} đã tồn tại. Bỏ qua.")
            continue
            
        lines = [f'# {pdf_path.name}\n']
        
        for page_num in range(len(doc)):
            print(f"  -> Đọc trang {page_num + 1}/{len(doc)}...", end="", flush=True)
            page = doc[page_num]
            
            # Xuất ảnh độ phân giải cao để model nhìn rõ công thức Toán (dpi=300)
            pix = page.get_pixmap(dpi=300)
            img_bytes = pix.tobytes("png")
            image = Image.open(io.BytesIO(img_bytes))
            
            try:
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=[prompt, image],
                )
                
                lines.append(f'## Page {page_num + 1}\n')
                if response.text:
                    lines.append(response.text.strip())
                else:
                    lines.append('*[Không nhận diện được nội dung]*')
                lines.append('\n---\n')
                print(" Hoàn tất.")
                
            except Exception as e:
                print(f" LỖI ở trang {page_num + 1}: {str(e)}")
                lines.append(f'## Page {page_num + 1}\n*[Lỗi khi gọi API: {str(e)}]*\n---\n')
        
        # Lưu kết quả
        out_path.write_text('\n'.join(lines), encoding='utf-8')
        print(f"✅ Đã lưu kết quả tại: {out_path}")

if __name__ == "__main__":
    process_pdfs()
    print("\nHoàn tất toàn bộ! Thầy có thể xem file kết quả trong folder extracted_markdown_gemini")
