# HƯỚNG DẪN SỬ DỤNG: XỬ LÝ ĐỀ TOÁN SKYLINE TRÊN VERCEL

Tài liệu này hướng dẫn chi tiết quy trình triển khai và sử dụng hệ thống Trích xuất Toán Học chuẩn LaTeX (JSON) ra ngoài mạng Internet thông qua nền tảng Vercel Serverless.

> [!WARNING]
> Theo lựa chọn Kiến trúc Vercel (FastAPI + Frontend Tĩnh), Ứng dụng gốc Streamlit rườm rà đã bị huỷ bỏ, đổi lấy tốc độ và chuẩn API hiện đại. 

---

## 1. Yêu cầu Hệ thống (Prerequisites)

Nếu thầy muốn chạy Web App này trực tiếp ở Máy tính cá nhân (Local) để thử nghiệm trước khi đẩy lên Vercel, hãy mở Terminal:
```bash
pip install -r requirements.txt
```

API Key bắt buộc: Truy cập [Google AI Studio](https://aistudio.google.com/app/apikey) để lấy `GEMINI_API_KEY`. (Khi chạy Web chỉ cần copy-paste lên khung giao diện).

---

## 2. Triển khai (Deploy) lên VERCEL

Dự án này đã được cấu hình chặt chẽ theo đặc thù Serverless Python (thông qua `vercel.json` và thư mục lõi `/api`). Thầy có 2 cách để đưa dự án này lên Live Production.

### CÁCH 1: Kéo thả qua Github (Khuyên dùng)
1. Thầy đẩy toàn bộ source code này (`api`, `public`, `vercel.json`, `requirements.txt`) lên 1 kho chứa GitHub.
2. Đăng nhập [Vercel Dashboard](https://vercel.com).
3. Bấm **Add New Project** -> Chọn kho GitHub vừa nãy.
4. Giao diện Framework Preset: ĐỂ TRỐNG (Vercel tự hiểu Python nhờ file json).
5. Bấm Deploy. Nhận Link xịn xò chưa đầy 3 phút.

### CÁCH 2: Deploy bằng Vercel CLI ở Terminal
1. Bật Terminal CMD, gõ: `npm i -g vercel` (Cài công cụ Vercel).
2. Gõ lệnh: `vercel login` (Xác thực đăng nhập tài khoản).
3. Đứng tại thư mục dự án Toán Skyline, gõ: `vercel`
4. Ấn liên tục 5 phím `Enter` để chấp nhận setup mặc định. Link URL hoàn chỉnh sẽ hiện ra.

---

## 3. Cách Dùng Giao Diện Hệ Thống (Frontend HTML)

Sau khi Vercel nhả ra một đường link (Ví dụ: `https://toan-skyline-ocr.vercel.app`), quá trình sử dụng cho toàn bộ Giáo viên cực dễ:
1. Mở trang Web `Vercel` của thầy.
2. Dán mã `GEMINI API KEY` vào bảng Sidebar.
3. Kéo-Thả file PDF vào. **(Chú ý: Vercel Free Plan cắt mạng sau 10s, do đó file PDF phải siêu cắt ngắn - khuyến khích 1 đến tối đa 2 trang mỗi lần up).**
4. Bấm *Bắt đầu nhận diện*. Chờ AI lấy ảnh, bóc tách LaTeX và sắp xếp các câu Trắc nghiệm.
5. Hiện nút ✅ Tải File JSON Câu Hỏi Trắc Nghiệm.

---

## 4. Chạy trực tiếp qua Code Terminal (Xử lý hàng loạt)
Nếu thầy không muốn up Web và sợ giới hạn Vercel 10 giây? Hãy chạy kịch bản Terminal siêu bền bỉ mà em đã tạo sẵn trước đó:
1. Bỏ toàn bộ PDF vào `docs/`
2. Chạy: `python extract_math_gemini.py` (Lấy Markdown chuẩn hình thức Công Thức).
3. Chạy: `python format_mcq_processor.py` (Cắt ghép ra JSON tự động).

Hy vọng dự án mang lại giải thưởng Sáng kiến lớn cho Trường học.
