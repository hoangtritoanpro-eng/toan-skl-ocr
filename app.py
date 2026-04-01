import streamlit as st
import os
import io
import json
import fitz  # PyMuPDF
from PIL import Image

try:
    from google import genai
    from google.genai import types
except ImportError:
    st.error("Thiết lập hệ thống thiếu thư viện. Hãy chạy: pip install google-genai PyMuPDF Pillow")
    st.stop()

# --- CONFIGURATION ---
st.set_page_config(
    page_title="Hệ thống OCR Toán SKYLINE",
    page_icon="📐",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for modern look
st.markdown("""
<style>
    .reportview-container {
        background: #fafafa;
    }
    .main-title {
        color: #1E3A8A;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        font-weight: 800;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stDownloadButton > button {
        background-color: #2563eb !important;
        color: white !important;
        border-radius: 8px !important;
        height: 3rem !important;
        font-weight: 600 !important;
    }
    .stDownloadButton > button:hover {
        background-color: #1d4ed8 !important;
    }
    div[data-testid="stSidebar"] {
        background-color: #f1f5f9;
        border-right: 1px solid #e2e8f0;
    }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3048/3048122.png", width=60)
    st.title("⚙️ Cấu Hình Hệ Thống")
    st.markdown("---")
    
    # API Key Input
    api_key_env = os.environ.get("GEMINI_API_KEY", "")
    api_key_input = st.text_input(
        "🔑 Nhập Google Gemini API Key:", 
        value=api_key_env, 
        type="password",
        help="Lấy khóa API miễn phí tại Google AI Studio"
    )
    
    st.markdown("---")
    st.markdown("""
    **Hướng dẫn sử dụng:**
    1. Nhập API Key hợp lệ.
    2. Kéo thả file PDF Đề thi Toán.
    3. Bấm **Bắt đầu Nhận diện & Xử lý**.
    4. Xem trước (Preview) đoạn lệnh LaTeX.
    5. Tải về file Trắc nghiệm JSON.
    """)
    st.caption("v1.0.0 - Developed for Sáng kiến kinh nghiệm.")

# --- MAIN CONTENT ---
st.markdown("<h1 class='main-title'>📐 HỆ THỐNG OCR TOÁN SKYLINE BẰNG AI</h1>", unsafe_allow_html=True)
st.write("Giải pháp Số hoá **Đề thi Toán học** chuẩn dạng LaTeX và bóc tách cấu trúc Trắc nghiệm tự động (A B C D).")

# Prompts
PROMPT_OCR = """
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

SCHEMA_MCQ = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "question_number": {"type": "integer", "description": "Số thứ tự câu hỏi"},
            "question_content": {"type": "string", "description": "Nội dung câu hỏi (chứa LaTeX)"},
            "options": {
                "type": "object",
                "properties": {
                    "A": {"type": "string"},
                    "B": {"type": "string"},
                    "C": {"type": "string"},
                    "D": {"type": "string"}
                },
                "required": ["A", "B", "C", "D"]
            },
            "correct_answer": {"type": "string"},
            "explanation": {"type": "string"}
        },
        "required": ["question_number", "question_content", "options"]
    }
}

PROMPT_JSON = """
You are a master at parsing educational data.
Read the following markdown text containing math multiple-choice questions (extracted via OCR).
Extract all questions into a clean JSON array structure.
Ensure all LaTeX formatting ($...$ and $$...$$) is preserved perfectly.
Ignore irrelevant headers, page numbers, or noise. Only extract the MCQs.
"""

uploaded_file = st.file_uploader("📂 Tải lên File PDF Đề thi Toán", type=['pdf'])

if uploaded_file is not None:
    if not api_key_input:
        st.warning("⚠️ Vui lòng nhập GEMINI API KEY ở Menu bên trái để tiếp tục!")
        st.stop()
        
    client = genai.Client(api_key=api_key_input)
    
    if st.button("🚀 Bắt đầu Nhận diện & Xử lý", use_container_width=True):
        
        # 1. OCR PDF -> MARKSOWN
        st.subheader("Trích xuất OCR (Giai đoạn 1/2)")
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        pdf_bytes = uploaded_file.read()
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        
        extracted_md_lines = [f"# {uploaded_file.name}\n"]
        total_pages = len(doc)
        
        for i in range(total_pages):
            status_text.text(f"Đang scan ảnh Toán học trang {i+1}/{total_pages}...")
            page = doc[i]
            pix = page.get_pixmap(dpi=300)
            img_bytes = pix.tobytes("png")
            img = Image.open(io.BytesIO(img_bytes))
            
            try:
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=[PROMPT_OCR, img],
                )
                if response.text:
                    extracted_md_lines.append(f"## Trang {i+1}\n")
                    extracted_md_lines.append(response.text.strip() + "\n---\n")
            except Exception as e:
                st.error(f"Lỗi đọc trang {i+1}: {e}")
                
            progress_bar.progress(int(((i+1)/total_pages)*50)) # up to 50%
            
        full_markdown = "\n".join(extracted_md_lines)
        st.success("✅ Đã trích xuất xong nội dung Đề thi thuần (Markdown).")
        
        with st.expander("👁️ Xem trước nội dung Đề (LaTeX)"):
            st.markdown(full_markdown)

        # 2. MARKSOWN -> JSON
        st.subheader("Cấu trúc hoá Dữ liệu (Giai đoạn 2/2)")
        status_text.text("Đang nhờ AI phân tích Câu hỏi và Phương án A B C D...")
        
        try:
            json_response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=[PROMPT_JSON, full_markdown],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=SCHEMA_MCQ,
                    temperature=0.1,
                ),
            )
            
            parsed_data = json.loads(json_response.text)
            st.success(f"✅ Đã cấu trúc xong {len(parsed_data)} Câu hỏi Trắc nghiệm.")
            progress_bar.progress(100)
            
            # Show JSON and Download Button
            col1, col2 = st.columns([1, 1])
            with col1:
                st.write("**Bản đồ Dữ liệu (JSON):**")
                st.json(parsed_data)
            
            with col2:
                st.write("**Chuyển tiếp (Download):**")
                json_string = json.dumps(parsed_data, ensure_ascii=False, indent=2)
                file_name = uploaded_file.name.replace(".pdf", "_TrắcNghiệm.json")
                
                st.download_button(
                    label=f"💾 Tải về File {file_name}",
                    data=json_string,
                    file_name=file_name,
                    mime="application/json",
                )
                st.info("💡 Lưu ý: File JSON này đã hoàn thiện cấu trúc, thầy có thể tự động nạp thẳng vào hệ thống Quản lý Thư viện Câu hỏi (hoặc OMRChecker).")
                
        except Exception as e:
            st.error(f"❌ Xảy ra lỗi khi cấu trúc hoá Trắc nghiệm: {e}")
            progress_bar.empty()
