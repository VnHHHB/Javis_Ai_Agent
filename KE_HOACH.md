# Kế hoạch chi tiết: từ MVP lên Jarvis đầy đủ

Nguyên tắc: mỗi bước xong là dùng được ngay, không bước nào phụ thuộc
vào việc “train model từ đầu”. Thứ tự này là thứ tự khuyên làm.

## Bước 0 — Kiểm chứng MVP (hôm nay, 30 phút) — ĐÃ XONG PHẦN CODE

- [x] Chạy `fetch` → 139 bài đã lưu, 8/8 nguồn OK (sau khi sửa arXiv RSS
      cuối tuần bị rỗng bằng arXiv API).
- [ ] Bạn chạy `python3 run.py briefing` và đọc file briefing mẫu.
- [ ] Bạn sửa `profile.json` 1 lần: xoá 1 topic không thích, tăng weight
      topic thích lên, rồi chạy lại `top` để thấy thứ hạng đổi.
- Tiêu chí qua bước: bạn thấy ít nhất 3/12 bài briefing là đáng đọc thật.

## Bước 1 — Cá nhân hoá thật (cuối tuần 1, 2–3 giờ)

1. Thêm feedback vào `app.py`: nút Thích / Bỏ qua → gọi `like()` / giảm weight.
2. Thêm lưu lịch sử đã đọc vào SQLite thay vì chỉ JSON, để không gợi lại
   bài cũ.
3. Thêm lọc trùng nội dung: so sánh tiêu đề giống >80% thì giữ 1 bài.
4. Thêm dịch/tóm tắt tiếng Việt: chỉ khi có API key, trong
   `summarize_with_llm()` gọi Gemini (rẻ) hoặc OpenAI, prompt cố định:
   “Tóm tắt 3 dòng tiếng Việt, nêu rõ con số và vật liệu, không bịa thêm.”
- Tiêu chí: briefing sáng có ít nhất 70% bài bạn chưa đọc và liên quan.

## Bước 2 — Trí nhớ dài hạn + hỏi đáp RAG (tuần 2, 3–4 giờ)

1. Cài `chromadb` + `sentence-transformers` (hoặc dùng API embedding).
2. Khi fetch xong, embedding tiêu đề + tóm tắt, lưu vào ChromaDB.
3. Lệnh `ask` nâng cấp: tìm 5 bài gần nghĩa nhất (không chỉ chứa đúng từ),
   rồi đưa cho LLM trả lời dựa trên 5 bài đó, kèm link nguồn.
4. Thêm profile dài hạn: “PHAM đang làm tandem CsPb0.9Sn0.1IBr2/Cs2TiI6,
   quan tâm MoS2 nhưng chưa chọn vai trò” — để câu trả lời nhắc đúng bối cảnh.
- Tiêu chí: hỏi “MoS2 làm HTL có gì mới?” trả lời được bằng bài thật, có link.

## Bước 3 — Chủ động + chat mọi nơi (tuần 3, 2–3 giờ)

1. Telegram bot: dùng `python-telegram-bot`, 3 lệnh `/briefing`, `/top`, `/ask`.
2. Cron 7h30 gửi briefing qua Telegram thay vì chỉ lưu file.
3. Thêm cảnh báo: nếu có paper mới điểm ≥10 về perovskite/MoS2 thì gửi ngay,
   không đợi sáng hôm sau.
- Tiêu chí: bạn không cần mở máy tính vẫn nhận được briefing sáng.

## Bước 4 — Giọng nói kiểu Javis (tuần 4, tuỳ chọn, 3–5 giờ)

1. STT: Whisper local (`faster-whisper`) hoặc API.
2. TTS: Piper (offline, tiếng Anh tốt; tiếng Việt cần kiểm chứng giọng)
   hoặc API TTS.
3. Chỉ làm voice sau khi bước 1–3 đã ổn — voice mà feed còn dở thì chỉ
   thêm ồn, không thêm giá trị.
- Tiêu chí: nói “briefing sáng nay” → nghe được 5 tin chính trong 2 phút.

## Bước 5 — Tay làm việc: nối vào SCAPS/ML của bạn (khi MVP đã tin cậy)

1. Thêm tool `chay_scaps_pilot.py`: Jarvis chỉ được chạy script bạn đã duyệt,
   với tham số trong whitelist, log mọi lệnh ra file.
2. Thêm tool `tong_hop_ket_qua.py`: đọc CSV kết quả SCAPS, tóm tắt PCE/Jsc/Voc
   tốt nhất, không tự sửa file gốc.
3. Quy tắc an toàn bắt buộc: không cho LLM tự chạy lệnh shell tuỳ ý,
   không cho xoá/ghi đè file, mọi hành động ghi đều phải qua hàm bạn viết sẵn.
- Tiêu chí: bạn nói “chạy pilot 20 run rồi báo PCE cao nhất” và nó làm đúng,
  có log để kiểm tra lại.

## Chi phí ước tính

- MVP hiện tại: 0 đồng (chỉ RSS/API công khai).
- Bước 1–2 với Gemini: vài chục nghìn/tháng nếu briefing mỗi ngày + hỏi ít.
- Chạy local bằng Ollama: 0 đồng tiền API, đổi lại cần máy đủ RAM và chậm hơn.
- Đừng trả tiền train/fine-tune model riêng ở giai đoạn này — chưa cần.

## Những việc chỉ bạn làm được

- Chốt weight topic và nguồn tin sau 1 tuần đọc thật.
- Cấp API key / token Telegram (qua Secure Vault, không gửi key trong chat).
- Quyết định có cho Jarvis chạm vào thư mục SCAPS của bạn không, và chạm tới đâu.
- Kiểm chứng lại mọi con số trong briefing trước khi trích vào bài báo.
