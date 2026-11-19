# Jarvis MVP 

Bản chạy được ngay, không cần API key, không cần cài thêm gì ngoài `requests`.
Profile đã nạp sẵn chủ đề của bạn: pin tandem/perovskite, SCAPS/mô phỏng,
MoS2, ML cho vật liệu/surrogate, công nghệ chung.

## Chạy trong 2 phút

```bash
cd ~/workspace/jarvis-mvp
python3 run.py fetch          # kéo tin, lưu data/articles.json
python3 run.py top            # 10 bài điểm cao nhất
python3 run.py ask "perovskite"
python3 run.py briefing       # tạo data/briefing-YYYY-MM-DD.md
```

Dashboard đẹp hơn (tuỳ chọn):

```bash
pip install streamlit
streamlit run app.py
```

## Tuỳ chỉnh — đây là phần “Javis hiểu bạn”

- Sửa `profile.json`: thêm/bớt keyword, tăng `weight` topic nào bạn thích,
  thêm từ vào `blocked_keywords` để loại hẳn.
- Sửa `sources.json`: thêm RSS/API của tạp chí, blog, lab bạn theo dõi.
- Sau khi đọc, nếu muốn topic đó nặng hơn, gọi trong code:
  `from jarvis.memory import like; like("https://...link-bai...")`
  (MVP hiện chỉ có hàm này, chưa có nút bấm — xem kế hoạch bước 2.)

## Tự động chạy mỗi sáng (Linux/macOS)

```bash
crontab -e
# thêm dòng: chạy fetch + briefing lúc 7h30 mỗi ngày
30 7 * * * cd ~/workspace/jarvis-mvp && python3 run.py fetch && python3 run.py briefing >> data/cron.log 2>&1
```

Muốn gửi briefing qua Telegram thì làm ở bước 3 trong KE_HOACH.md.

## Cấu trúc

- `jarvis/fetch_feeds.py` — kéo RSS/Atom + arXiv API, dedupe theo link
- `jarvis/memory.py` — profile + chấm điểm (tiêu đề ×2, nội dung ×1, × weight)
- `jarvis/summarize.py` — tóm tắt trích xuất, chỗ cắm LLM để sẵn
- `jarvis/briefing.py` — tạo briefing Markdown
- `run.py` — CLI: fetch / top / ask / briefing
- `app.py` — dashboard Streamlit (tuỳ chọn)

## Tự phê bình — những gì MVP này CHƯA làm được

1. Tóm tắt là trích câu gốc tiếng Anh, chưa phải LLM viết lại tiếng Việt.
2. Chấm điểm bằng keyword, chưa hiểu ngữ nghĩa — sẽ bỏ sót bài dùng từ đồng nghĩa,
   và chấm cao cho bài chỉ nhắc keyword thoáng qua.
3. Một số bài arXiv bị mất ngày xuất bản do định dạng Atom, nên lọc “7 ngày qua”
   có thể bỏ sót vài bài. File `articles.json` vẫn giữ đủ bài.
4. arXiv API mỗi nguồn chỉ lấy 20 bài mới nhất, truy vấn còn hẹp
   (solar/perovskite/MoS2 và ML materials) — chưa bao quát hết SCAPS.
5. Chưa có voice, chưa có Telegram, chưa tự chạy — bạn phải chạy tay hoặc đặt cron.
6. Chưa có nút Thích/Không thích trên giao diện, chưa học từ phản hồi thật.

Những điểm này đều có bước sửa cụ thể trong KE_HOACH.md. Đừng coi MVP này
là Javis hoàn chỉnh — nó là khung để bạn kiểm chứng xem feed này có đáng
đọc mỗi sáng không, trước khi đầu tư thêm.
