# Sơ đồ cây: Các công việc cần tìm hiểu và build — Jarvis HUD + Voice trên LOQ

Phạm vi: Jarvis briefing (HUD + voice + LLM local + dữ liệu) trên laptop
Lenovo LOQ 2024, i5 dòng 12, RTX 3050 6GB, 16GB RAM.
Không gộp project hand tracking Iron Man spatial — đó là cây riêng.

Cách đọc: đi từ trái sang phải, từ trên xuống dưới.
Nhánh TÌM HIỂU cho biết cần học cái gì trước khi code nhánh đó.
Nhánh BUILD làm theo thứ tự Giai đoạn 0 → 6, đừng nhảy giai đoạn.
Mỗi lá có [ ] để bạn tick khi xong.

```
JARVIS TRÊN LOQ (HUD + Voice, local-first, RTX 3050 6GB)
│
├── A. TÌM HIỂU (học trước, mỗi mục ~30–90 phút, học đủ dùng rồi code)
│   ├── A1. Giao diện kiểu phim
│   │   ├── [ ] Ngôn ngữ HUD: vòng đồng tâm, panel 2 bên, chữ cyan/nền tối
│   │   ├── [ ] Figma Community: tìm JARVIS HUD, Sci-fi HUD, Futuristic dashboard
│   │   ├── [ ] Font + màu: Orbitron / Rajdhani / Share Tech Mono, #050A12 / #00E5FF
│   │   └── [ ] Vì sao không dùng Streamlit cho HUD này (khó làm vòng xoay, sóng âm)
│   ├── A2. Giọng nói
│   │   ├── [ ] VAD là gì, vì sao phải lọc khoảng lặng trước khi phiên âm
│   │   ├── [ ] faster-whisper: small vs base vs large-v3-turbo trên tiếng Việt
│   │   ├── [ ] Wake word: openWakeWord (local) vs Porcupine, vì sao làm sau
│   │   └── [ ] TTS tiếng Việt: Piper vi-VN (offline) vs Edge-TTS vi-VN (gửi text lên cloud)
│   ├── A3. Não LLM local + RAG
│   │   ├── [ ] LLM lượng tử hóa Q4 là gì, vì sao 3–4B vừa VRAM 6GB
│   │   ├── [ ] Ollama vs llama.cpp: chọn 1, chạy thử Qwen3 4B / Llama 3.2 3B
│   │   ├── [ ] Embedding + ChromaDB: chỉ embedding tiêu đề + tóm tắt, top-k = 5
│   │   └── [ ] Prompt RAG: trả lời dựa trên bài đã kéo, kèm link, không bịa số liệu
│   ├── A4. Dữ liệu đi về đâu + an toàn
│   │   ├── [ ] Vẽ lại luồng dữ liệu hiện tại: RSS → máy bạn → articles.json (không rời máy)
│   │   ├── [ ] Bảng đi-đâu: LLM cloud, Telegram, Edge-TTS gửi gì, đi đâu
│   │   ├── [ ] Công tắc local-only + log: ngày giờ, gửi gì, đi đâu
│   │   └── [ ] Cổng an toàn cho tool: LLM chỉ gợi ý, code mới được quyết định chạy
│   └── A5. Hiệu năng trên LOQ
│       ├── [ ] Đọc VRAM/RAM/CPU bằng Task Manager + nvidia-smi khi chạy model
│       ├── [ ] Nút thắt thường gặp: load lại model, STT+LLM song song, JSON quá lớn
│       └── [ ] Khi nào mới cần nâng RAM 32GB dual-channel (chỉ sau khi đo)
│
├── B. BUILD (làm theo thứ tự, mỗi giai đoạn xong là dùng được)
│   ├── Giai đoạn 0. Củng cố MVP (đã có, chỉ kiểm chứng lại)
│   │   ├── [ ] Chạy lại: fetch → top → ask → briefing, briefing đọc được thật
│   │   └── [ ] Chốt profile.json: topic, weight, blocked_keywords sau 1 tuần đọc
│   ├── Giai đoạn 1. Nền tảng FastAPI + dữ liệu (nền cho mọi thứ sau)
│   │   ├── [ ] Bọc code MVP thành API: GET /api/briefing, GET /api/top, GET /api/ask?q=
│   │   ├── [ ] Chuyển articles.json → SQLite khi bài vượt vài nghìn, thêm index
│   │   ├── [ ] Log thời gian từng bước: fetch / score / STT / LLM / TTS
│   │   └── [ ] Chế độ local-only mặc định + file cấu hình công tắc cloud
│   ├── Giai đoạn 2. HUD giống phim (web, không phải Streamlit)
│   │   ├── [ ] Vẽ 1 màn Figma 1920×1080: giữa vòng, trái briefing, phải hệ thống, dưới ô lệnh
│   │   ├── [ ] Code HUD HTML/CSS/JS: vòng xoay, trạng thái, panel briefing thật từ API
│   │   ├── [ ] Hiệu ứng theo trạng thái: chờ / nghe / nghĩ / nói (không chạy animation vô tội vạ)
│   │   └── [ ] Nút nhanh: Briefing / Tin MoS2 / Tin perovskite + ô gõ lệnh
│   ├── Giai đoạn 3. Voice nấc 1 — bấm để nói
│   │   ├── [ ] Mic → VAD → faster-whisper small (GPU) → text hiển thị lên HUD
│   │   ├── [ ] Lệnh cố định bằng rule trước: briefing, tin MoS2/perovskite, tóm tắt bài đầu
│   │   ├── [ ] Lệnh bắt buộc: “dừng lại” ngắt TTS ngay lập tức
│   │   └── [ ] TTS đọc briefing: thử Piper vi-VN trước, fallback Edge-TTS có công tắc
│   ├── Giai đoạn 4. Não LLM local + RAG (hỏi tự do)
│   │   ├── [ ] Chạy Ollama/llama.cpp, model 3–4B Q4, load 1 lần, giữ ấm
│   │   ├── [ ] Embedding tiêu đề + tóm tắt → ChromaDB, tìm top-5 rồi mới đưa cho LLM
│   │   ├── [ ] Trả lời kèm link gốc, câu nào không có trong bài thì nói “không có trong dữ liệu”
│   │   └── [ ] STT và LLM chạy NỐI TIẾP, không song song trên VRAM
│   ├── Giai đoạn 5. Voice nấc 2 + chủ động
│   │   ├── [ ] Wake word “Jarvis” bằng openWakeWord, chỉ bật khi nấc 1 đã ổn
│   │   ├── [ ] Lịch chạy: fetch + briefing 7h30, cảnh báo khi có bài điểm ≥ 10
│   │   └── [ ] (Tùy chọn) Telegram bot: /briefing, /top, /ask — tắt mặc định
│   ├── Giai đoạn 6. Tay làm việc — nối SCAPS (làm cuối cùng)
│   │   ├── [ ] Chỉ chạy script SCAPS đã duyệt sẵn, tham số trong whitelist
│   │   ├── [ ] Log mọi lệnh, không cho LLM chạy shell tùy ý, không ghi đè file gốc
│   │   └── [ ] Lệnh mẫu: “chạy pilot 20 run rồi báo PCE cao nhất” + log kiểm chứng lại
│   └── Giai đoạn 7. Đo, tối ưu, hoàn thiện
│       ├── [ ] Đo: lệnh cố định < ~3s, RAG ngắn < ~6s, VRAM không tràn, HUD mượt
│       ├── [ ] Tối ưu theo log: fetch song song 4–6 nguồn, cache 6–12h, giảm animation khi chạy model
│       └── [ ] Dọn: README cập nhật, xóa code thử nghiệm, backup profile.json + sources.json
│
├── C. KIỂM CHỨNG (mỗi giai đoạn phải qua mới sang giai đoạn sau)
│   ├── [ ] Giai đoạn 1 qua khi: API trả briefing thật, ngắt mạng vẫn xem được bài cũ
│   ├── [ ] Giai đoạn 2 qua khi: đọc được tiêu đề từ 1m, bấm được bằng chuột
│   ├── [ ] Giai đoạn 3 qua khi: bấm mic → nói → text đúng → TTS đọc được, “dừng lại” có tác dụng
│   ├── [ ] Giai đoạn 4 qua khi: hỏi “MoS2 làm HTL có gì mới?” trả lời bằng bài thật + link
│   ├── [ ] Giai đoạn 5 qua khi: sáng 7h30 có briefing mà không cần mở máy tính (nếu bật)
│   └── [ ] Giai đoạn 6 qua khi: chạy SCAPS pilot xong, log khớp với kết quả CSV
│
└── D. VIỆC CHỈ BẠN LÀM ĐƯỢC (không giao cho code tự quyết)
    ├── [ ] Chốt weight topic + nguồn tin sau 1 tuần đọc thật
    ├── [ ] Cấp API key / token Telegram qua Secure Vault, không gửi key trong chat
    ├── [ ] Quyết định: có cho Jarvis chạm vào thư mục SCAPS không, chạm tới đâu
    ├── [ ] Quyết định: bật hay tắt từng công tắc gửi cloud (LLM cloud, Edge-TTS, Telegram)
    └── [ ] Kiểm chứng số liệu trong briefing trước khi trích vào bài báo
```

## Phụ thuộc giữa các nhánh (đừng làm ngược)

- Giai đoạn 2 (HUD) cần Giai đoạn 1 (API) — HUD không tự kéo RSS.
- Giai đoạn 3 (Voice nấc 1) cần Giai đoạn 1 + 2 — voice cần HUD hiển thị text.
- Giai đoạn 4 (RAG) cần Giai đoạn 1 — RAG cần kho bài + embedding.
- Giai đoạn 5 (Wake word + lịch) cần Giai đoạn 3 + 4 đã ổn.
- Giai đoạn 6 (SCAPS) cần tất cả các giai đoạn trước đã ổn + cổng an toàn.
- Nhánh A không cần học hết mới code: học A1 rồi làm Giai đoạn 2,
  học A2 rồi làm Giai đoạn 3, cứ thế cuốn chiếu.
