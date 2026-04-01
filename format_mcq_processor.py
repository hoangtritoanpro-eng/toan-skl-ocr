import os
import json
from pathlib import Path

try:
    from google import genai
    from google.genai import types
except ImportError:
    print("Vui lòng cài đặt: pip install google-genai")
    exit(1)

# Kiểm tra API Key
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    print("LỖI: Chưa cấu hình GEMINI_API_KEY!")
    exit(1)

client = genai.Client(api_key=api_key)

# Cấu hình đường dẫn
BASE = Path(__file__).resolve().parent
IN_DIR = BASE / 'skl_agent_kit-main' / 'extracted_markdown_gemini'
OUT_DIR = BASE / 'skl_agent_kit-main' / 'output_mcq'

OUT_DIR.mkdir(parents=True, exist_ok=True)

schema = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "question_number": {"type": "integer", "description": "Số thứ tự câu hỏi (ví dụ: 1, 2, 3)"},
            "question_content": {"type": "string", "description": "Nội dung câu hỏi (chứa LaTeX nếu có)"},
            "options": {
                "type": "object",
                "properties": {
                    "A": {"type": "string"},
                    "B": {"type": "string"},
                    "C": {"type": "string"},
                    "D": {"type": "string"}
                },
                "required": ["A", "B", "C", "D"],
                "description": "Các phương án lựa chọn ABCD"
            },
            "correct_answer": {"type": "string", "description": "Đáp án đúng (A, B, C, hoặc D) nếu có trong đề, để trống nếu không có"},
            "explanation": {"type": "string", "description": "Lời giải chi tiết nếu có"}
        },
        "required": ["question_number", "question_content", "options"]
    }
}

prompt = """
You are a master at parsing educational data.
Read the following markdown text containing math multiple-choice questions (extracted via OCR).
Extract all questions into a clean JSON array structure.
Ensure all LaTeX formatting ($...$ and $$...$$) is preserved perfectly.
Ignore irrelevant headers, page numbers, or noise. Only extract the MCQs.
"""

def extract_mcq(file_path):
    print(f"Bắt đầu xử lý: {file_path.name}")
    content = file_path.read_text(encoding='utf-8')
    
    if len(content.strip()) < 50:
        print("  -> File quá ngắn, bỏ qua.")
        return None
        
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[prompt, content],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=schema,
            ),
        )
        
        # Lưu ra JSON
        out_name = file_path.stem + '.json'
        out_path = OUT_DIR / out_name
        
        parsed_data = json.loads(response.text)
        
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(parsed_data, f, ensure_ascii=False, indent=2)
            
        print(f"✅ Đã parse thành công {len(parsed_data)} câu hỏi -> {out_path.name}")
        return parsed_data
        
    except Exception as e:
        print(f"❌ Lỗi khi xử lý file {file_path.name}: {e}")
        return None

def main():
    if not IN_DIR.exists():
        print(f"Không tìm thấy thư mục: {IN_DIR}")
        print("Vui lòng chạy extract_math_gemini.py trước.")
        return
        
    md_files = sorted(IN_DIR.glob('*.md'))
    if not md_files:
        print("Chưa có file .md nào trong thư mục in.")
        return
        
    print(f"Bắt đầu phân tích {len(md_files)} file Markdown thành JSON...")
    
    for md_file in md_files:
        extract_mcq(md_file)
        
    print("\nHoàn tất! Các file JSON câu hỏi trắc nghiệm đã được lưu trong:", OUT_DIR)

if __name__ == "__main__":
    main()
