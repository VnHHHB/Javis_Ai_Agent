# Nâng cấp Jarvis: HUD kiểu phim + Voice + Chạy mượt trên LOQ 2024

Máy đích: Lenovo LOQ 2024, Core i5-12450HX (hoặc 13450HX cùng dòng),
RTX 3050 6GB GDDR6, 16GB DDR5, SSD NVMe, màn 15.6" FHD 144Hz.
Nguyên tắc: **không quá đơn giản, nhưng không vượt quá 6GB VRAM.**
Mọi thứ nặng đều phải có bản nhẹ để fallback.

## 1. Giao diện giống phim nhất có thể

### 1.1. Tham khảo ở đâu (miễn phí, không cần mua asset Marvel)

- **Phim để “lấy mắt”:** Iron Man 1–2 và Avengers — cảnh Tony làm việc
  trong lab, không phải cảnh đánh nhau. Chú ý 3 thứ: vòng tròn đồng tâm
  ở giữa, panel thông tin 2 bên, chữ nhỏ màu cyan trên nền tối.
  Đây là tham khảo phong cách, không copy logo/asset có bản quyền Marvel.
- **Figma Community (free):** tìm đúng từ khóa `JARVIS HUD`, `Sci-fi HUD`,
  `Futuristic dashboard`, `Cyberpunk UI`. Tải file về, tách lấy: vòng tròn,
  thanh trạng thái, panel, bảng màu — rồi vẽ lại theo dữ liệu của bạn.
- **Dribbble / Behance / Pinterest:** tìm `HUD interface`, `AI assistant HUD`.
  Dùng để chốt bố cục, không dùng để lấy code.
- **GitHub / CodePen:** tìm `jarvis hud html css`, `iron man hud`.
  Nhiều demo chỉ là vòng tròn xoay bằng CSS/SVG — học kỹ thuật vẽ,
  đừng bê nguyên code không hiểu.
- **Công cụ thiết kế free:** Figma (bản free đủ dùng), Penpot (mã nguồn mở,
  chạy trên trình duyệt, không cần cài). Font free trên Google Fonts:
  `Orbitron` cho tiêu đề, `Rajdhani` cho nội dung, `Share Tech Mono`
  cho số liệu. Màu gợi ý: nền `#050A12`, cyan `#00E5FF`, xanh phụ
  `#00FFC8`, cảnh báo `#FFB300`, lỗi `#FF4D5E`.

### 1.2. Thiết kế bắt đầu thế nào (làm theo đúng thứ tự này)

1. **Phác bố cục 1 trang, không vẽ chi tiết vội:**
   - Giữa: vòng arc-reactor + sóng giọng nói + trạng thái
     (Đang nghe / Đang nghĩ / Đang nói).
   - Trái: briefing hôm nay, 5–12 bài, mỗi bài 1 dòng tiêu đề + điểm.
   - Phải: hệ thống — GPU/VRAM/RAM, số bài đã kéo, nguồn OK/lỗi,
     lịch chạy tiếp theo.
   - Dưới: ô lệnh (gõ hoặc bấm mic) + 3 nút nhanh: Briefing / Tin MoS2 /
     Tin perovskite.
2. **Vẽ 1 màn hình duy nhất trong Figma/Penpot trước**, đúng 1920×1080
   cho màn LOQ. Chốt màu, font, độ dày vòng tròn, khoảng cách panel.
   Chưa hài lòng ở Figma thì đừng vội code — sửa ở Figma rẻ hơn sửa code.
3. **Chuyển sang code web, không dùng Streamlit cho HUD này:**
   Streamlit tiện nhưng khó làm vòng xoay, sóng âm, hiệu ứng giống phim.
   Dùng HTML + CSS + JavaScript thuần, hoặc React + Tailwind nếu bạn
   đã quen. Backend vẫn là FastAPI (xem mục 4), frontend chỉ gọi API.
4. **Hiệu ứng theo trạng thái, không chạy animation vô tội vạ:**
   vòng xoay chậm khi chờ, nhanh + sáng khi đang nghe, sóng âm nhảy
   theo biên độ mic, chữ chạy từng ký tự khi Jarvis trả lời.
   Animation nặng, chạy 60fps liên tục, chính là một nguồn gây lag —
   tắt bớt khi máy đang chạy model (xem mục 3.3).
5. **Tiêu chí “giống phim mà vẫn dùng được”:** đọc được tiêu đề bài báo
   từ khoảng cách 1m, bấm được bằng chuột, không cần nhớ lệnh.
   HUD trong phim đẹp vì nó là phim — HUD thật phải đọc được trước đã.

## 2. Điều khiển và giao tiếp bằng giọng nói — làm được, theo 2 nấc

### 2.1. Luồng voice đầy đủ

```
Mic → VAD (chỉ ghi khi có tiếng nói) → STT → Hiểu lệnh → Làm việc → TTS → Loa
         faster-whisper (local)          rule + LLM nhỏ       Piper / Edge-TTS
```

- **Nấc 1 — bấm để nói (làm trước, chắc chắn chạy):** bấm nút mic hoặc
  giữ phím, nói xong nhả ra. Không cần wake word, không sợ máy tự kích
  hoạt khi xem video. Đây là nấc nên làm đầu tiên.
- **Nấc 2 — gọi “Jarvis” để đánh thức (làm sau):** dùng openWakeWord
  (mã nguồn mở, chạy local) hoặc Porcupine (bản cá nhân miễn phí).
  Chỉ bật khi nấc 1 đã ổn, vì wake word chạy nền liên tục sẽ tốn CPU
  và dễ nhận nhầm.

### 2.2. Lệnh mẫu (tiếng Việt, ưu tiên lệnh cố định trước khi dùng LLM tự do)

- “Briefing sáng nay” → đọc 5 bài điểm cao nhất.
- “Tin mới về MoS2” / “Tin mới về perovskite” → lọc theo topic.
- “Tóm tắt bài đầu tiên” → đọc tóm tắt bài đang hiển thị.
- “Dừng lại” / “Im lặng” → dừng TTS ngay lập tức (bắt buộc phải có).
- Câu hỏi tự do (“MoS2 làm HTL có gì mới?”) → đi qua RAG trên bài đã kéo,
  trả lời kèm link, không bịa số liệu.

Lệnh cố định nên nhận bằng rule (so khớp từ khóa) trước, LLM chỉ xử lý
phần còn lại. Như vậy vừa nhanh, vừa ít tốn GPU, vừa ít trả lời sai.

### 2.3. Chọn model voice cho RTX 3050 6GB

- **STT:** `faster-whisper`, model `small` chạy GPU, int8/float16.
  Trên RTX 3050, một câu nói thường phiên âm xong trong khoảng dưới
  2 giây theo các bản build thực tế dùng faster-whisper + RTX 3050.
  Model `large-v3-turbo` chính xác hơn nhưng nặng hơn — chỉ thử khi
  `small` nghe sai tiếng Việt nhiều.
- **TTS tiếng Việt là điểm yếu nhất, nói thẳng:** giọng tiếng Anh
  offline (Piper) khá tốt, giọng tiếng Việt offline chưa mượt bằng.
  Phương án thực tế: thử Piper voice vi-VN trước; nếu nghe robot quá
  thì dùng Edge-TTS giọng vi-VN (miễn phí, nhưng text sẽ gửi lên
  Microsoft — xem mục 3.2). Đừng hứa giọng Jarvis tiếng Việt như phim
  ngay từ đầu.
- **Không chạy STT + LLM + TTS cùng lúc trên VRAM:** xếp hàng —
  STT xong thì nhả VRAM (hoặc giữ model nhỏ), rồi mới chạy LLM.
  Chạy song song là cách nhanh nhất làm máy lag và tràn VRAM.

## 3. Thông tin bạn đọc đi về đâu — và làm sao giảm lag

### 3.1. Hiện tại (MVP bạn đang có): không có gì rời khỏi máy

```
RSS / arXiv API  →  máy bạn  →  data/articles.json, data/briefing-*.md
profile.json (sở thích) cũng chỉ nằm trên máy bạn.
```

MVP hiện tại không dùng API LLM, không có Telegram, không có tài khoản
đám mây — nên tiêu đề/tóm tắt bài báo và profile của bạn **không được
gửi cho bên thứ ba nào**. Muốn kiểm chứng: ngắt mạng sau khi fetch xong,
lệnh `top`, `ask`, `briefing` vẫn chạy.

### 3.2. Khi nâng cấp, mỗi thứ mới thêm sẽ gửi đi đâu

| Thêm cái gì | Dữ liệu đi đâu | Cách giữ riêng tư |
|---|---|---|
| LLM cloud (Gemini/OpenAI) | Tiêu đề + tóm tắt bài bạn hỏi gửi lên nhà cung cấp đó | Chỉ gửi khi bạn bật; mặc định dùng LLM local, hoặc chỉ gửi bài đã công khai (paper/tin), không gửi file SCAPS riêng |
| LLM local (Ollama/llama.cpp) | Ở yên trên máy bạn | Ưu tiên cho câu hỏi liên quan dữ liệu riêng |
| Telegram bot | Briefing đi qua máy chủ Telegram | Chỉ bật khi bạn cần nhận tin trên điện thoại; không bật mặc định |
| Edge-TTS | Câu trả lời (text) gửi lên Microsoft để tạo giọng | Dùng Piper local nếu muốn 100% offline |
| Wake word local | Âm thanh xử lý trên máy, không gửi lên cloud | Không dùng wake word cloud |

Quy tắc đặt ra cho bản nâng cấp: **mặc định local-only.** Mọi thứ gửi
ra ngoài phải có công tắc riêng trong file cấu hình, và log lại:
ngày giờ nào, gửi cái gì, đi đâu. File SCAPS/dữ liệu riêng của bạn
không bao giờ được đưa vào prompt gửi cloud nếu chưa được bạn duyệt.

### 3.3. Giảm lag trên LOQ — 10 việc, làm theo thứ tự hiệu quả

1. **Chọn model đúng cỡ VRAM (quan trọng nhất):** LLM local ưu tiên
   3–4B dạng lượng tử hóa Q4 (ví dụ Qwen3 4B, Llama 3.2 3B qua Ollama).
   Các bản test cộng đồng trên RTX 3050 8GB cũng chỉ khuyến nghị tối đa
   khoảng 4B cho mượt; bản 6GB của bạn còn chật hơn, nên đừng cố chạy
   7–8B full-precision rồi than lag. Model 8B Q4 chỉ thử khi đã đo VRAM
   còn trống và chấp nhận chậm hơn.
2. **Load model một lần, giữ ấm:** backend FastAPI load LLM/Whisper lúc
   khởi động, các request sau dùng lại. Load lại model mỗi câu hỏi là
   lỗi gây lag phổ biến nhất.
3. **Tách tiến trình:** 1 tiến trình fetch/briefing chạy nền theo lịch,
   1 tiến trình UI + voice chạy trước mặt. Fetch đừng chạy cùng lúc
   với lúc bạn đang nói chuyện với Jarvis.
4. **Fetch thông minh:** kéo song song có giới hạn (4–6 nguồn cùng lúc),
   cache 6–12 giờ, chỉ kéo lại nguồn lỗi, giới hạn 20 bài/nguồn như MVP
   đang làm. Đừng kéo toàn bộ lịch sử mỗi lần.
5. **Bỏ JSON khi dữ liệu lớn:** chuyển `articles.json` sang SQLite khi
   vượt vài nghìn bài; truy vấn có index nhanh hơn đọc cả file mỗi lần.
6. **UI nhẹ:** HUD web thuần + CSS animation có giới hạn; tắt hiệu ứng
   nền, giảm vòng xoay khi đang chạy model. Đừng dùng Electron nặng
   nếu chỉ cần 1 trang HUD.
7. **Whisper tiết kiệm:** dùng VAD để không phiên âm khoảng lặng, dùng
   model `small` thay vì `large`, chunk audio ngắn (câu nói, không phải
   đoạn dài 5 phút).
8. **RAG tiết kiệm:** embedding chỉ cho tiêu đề + tóm tắt, không
   embedding toàn văn paper; top-k = 5, không lấy 20 bài rồi nhét hết
   vào prompt.
9. **Hệ thống LOQ:** cắm sạc, để chế độ Performance trong Lenovo Vantage,
   cập nhật driver NVIDIA, đóng bớt tab Chrome khi chạy Jarvis, để
   model trên SSD NVMe (không để trên ổ HDD ngoài nếu có).
10. **Đo trước khi tối ưu:** bật log thời gian từng bước
    (fetch / score / STT / LLM / TTS). Lag ở bước nào thì sửa bước đó —
    đừng đoán rồi nâng cấp RAM vội. Nếu RAM của bạn là 16GB đơn kênh,
    nâng lên 32GB dual-channel là nâng cấp phần cứng đáng tiền nhất
    cho cả LLM local lẫn đa nhiệm, nhưng chỉ làm sau khi đã đo và thấy
    RAM là nút thắt.

## 4. Khung chương trình nâng cấp — “không quá đơn giản”, vừa máy LOQ

```
HUD web (HTML/CSS/JS, vòng + sóng + panel)
        ↕ WebSocket / REST
FastAPI backend (1 tiến trình, load model 1 lần)
   ├── Voice: VAD → faster-whisper → rule/LLM → Piper/Edge-TTS
   ├── Brain: Ollama/llama.cpp, model 3–4B Q4 (fallback: LLM cloud, có công tắc)
   ├── Memory: SQLite (bài + lịch sử) + ChromaDB (embedding tiêu đề/tóm tắt)
   ├── Feed: fetch song song, cache, briefing theo lịch (giữ code MVP, bọc thêm API)
   └── Tools (có cổng an toàn): chỉ chạy script SCAPS đã duyệt, log mọi lệnh
Scheduler: cron / APScheduler — fetch + briefing 7h30, cảnh báo bài điểm ≥ 10
```

Thứ tự làm khuyên dùng (mỗi bước xong là dùng được, đừng làm cùng lúc):

1. **HUD tĩnh + FastAPI:** HUD hiển thị được briefing thật từ MVP.
2. **Voice nấc 1:** bấm để nói, 4 lệnh cố định, TTS đọc briefing.
3. **LLM local 3–4B + RAG:** hỏi tự do trên bài đã kéo, trả lời kèm link.
4. **Voice nấc 2 + scheduler:** wake word, briefing tự động, cảnh báo.
5. **Tools SCAPS:** chỉ sau khi 4 bước trên ổn định.

Tiêu chí “đạt” trên LOQ: từ lúc nói xong đến lúc Jarvis bắt đầu trả lời
dưới ~3 giây cho lệnh cố định, dưới ~6 giây cho câu hỏi RAG ngắn;
VRAM không tràn khi STT + LLM chạy nối tiếp; HUD vẫn mượt 60fps khi
không chạy model.
