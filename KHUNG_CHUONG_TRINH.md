# Khung chương trình Jarvis MVP — từ tổng quan đến chi tiết

Đọc tài liệu này theo kiểu zoom: mức 0 cho biết chương trình là gì trong
1 câu, mức 1 cho thấy toàn cảnh, mức 2 cho thấy luồng dữ liệu, mức 3 mới
đi vào từng module, mức 4 là schema và hàm cụ thể. Đừng đọc từ dưới lên.

---

## Mức 0 — Định nghĩa trong 1 câu

Jarvis MVP là một **chương trình đọc tin hộ bạn, chấm điểm theo sở thích
của bạn, rồi tóm tắt thành bản tin sáng** — không phải một mô hình AI
được train từ đầu.

Cái làm nó “giống Jarvis” không nằm ở mô hình, mà nằm ở 3 thứ:
sở thích của bạn được lưu thành dữ liệu, chương trình tự chạy theo lịch,
và mọi câu trả lời đều dẫn về bài gốc có link.

## Mức 1 — Tổng quan: 6 tầng

```
Người dùng (bạn)
      ▲  ▼
[6] Giao diện: CLI run.py, dashboard app.py (Streamlit, tùy chọn)
      ▲  ▼
[5] Trí tuệ: tóm tắt + trả lời (MVP: trích câu gốc; nâng cấp: LLM/RAG)
      ▲  ▼
[4] Trí nhớ & chấm điểm: profile.json + hàm score/rank trong memory.py
      ▲  ▼
[3] Kho dữ liệu: data/articles.json (bài đã kéo), data/briefing-*.md
      ▲  ▼
[2] Thu thập: fetch_feeds.py — RSS/Atom + arXiv API
      ▲  ▼
[1] Nguồn bên ngoài: arXiv, MIT Tech Review, IEEE Spectrum,
    Nature Energy, PV Magazine, TechCrunch, Hacker News
      ─────────────────────────────────────────────
      Chạy ngang qua mọi tầng: cấu hình (profile.json, sources.json),
      lịch chạy (cron 7h30), log lỗi từng nguồn, quy tắc an toàn
      (không cho LLM chạy lệnh shell tùy ý, không ghi đè file gốc).
```

Giải thích nhanh từng tầng, từ dưới lên:

1. **Nguồn bên ngoài:** nơi tin sinh ra. Bạn không sở hữu chúng, chỉ đọc
   qua RSS/Atom/API công khai. Nguồn nào chết thì chương trình vẫn chạy
   với các nguồn còn lại.
2. **Thu thập:** đi lấy tin, làm sạch, chống trùng. Đây là tầng “tai/mắt”.
3. **Kho dữ liệu:** nơi tin đã lấy được lưu lại để các tầng trên dùng lại
   nhiều lần mà không phải kéo lại.
4. **Trí nhớ & chấm điểm:** nơi “sở thích của bạn” sống. Không có tầng này
   thì chương trình chỉ là một RSS reader bình thường.
5. **Trí tuệ:** biến bài thô thành thứ đọc được: tóm tắt, trả lời câu hỏi.
   MVP cố tình làm tầng này đơn giản nhất để không phụ thuộc API key.
6. **Giao diện:** nơi bạn chạm vào chương trình: gõ lệnh, xem dashboard,
   sau này là Telegram và giọng nói.

Quy tắc quan trọng: **tầng trên chỉ được gọi tầng dưới qua hàm đã định
sẵn, không được tự đi kéo nguồn hay tự ghi file lung tung.** Ví dụ:
`briefing.py` không tự gọi mạng, nó chỉ đọc bài từ kho rồi gọi
`memory.py` để chấm điểm và `summarize.py` để tóm tắt.

## Mức 2 — Luồng dữ liệu: 3 việc chính chương trình làm

### Luồng A: Kéo tin (fetch)

```
sources.json
    → fetch_feeds.fetch_all()
        → requests.get từng URL (timeout 20s, lỗi 1 nguồn không dừng cả lượt)
        → parse_feed(): RSS <item> hoặc Atom <entry>
            → clean(): bỏ thẻ HTML, gom khoảng trắng
        → dedupe theo link
    → gộp với bài cũ trong data/articles.json, sắp theo ngày mới nhất
    → in báo cáo từng nguồn: OK / LỖI
```

Lưu ý đã kiểm chứng: arXiv RSS thường rỗng vào cuối tuần (do skipDays),
nên MVP dùng arXiv API thay cho RSS của arXiv:
`export.arxiv.org/api/query?search_query=...&sortBy=submittedDate`.
Các nguồn còn lại vẫn dùng RSS.

### Luồng B: Tạo bản tin sáng (briefing)

```
data/articles.json
    → memory.rank_articles(): chấm điểm mọi bài theo profile.json
    → lọc bài trong N ngày gần nhất (mặc định 3, briefing mẫu dùng 7)
    → lấy top N bài có điểm > 0 (mặc định 12)
    → summarize.extractive_summary(): chọn tối đa 3 câu chứa nhiều keyword nhất
    → briefing.make_briefing() / save_briefing()
    → data/briefing-YYYY-MM-DD.md
```

### Luồng C: Hỏi đáp trên tin đã đọc (ask)

```
Câu hỏi của bạn
    → tìm bài chứa đúng từ khóa trong tiêu đề hoặc tóm tắt
    → rank_articles() để xếp lại theo profile
    → in top 5 kèm link và đoạn tóm tắt
```

Phiên bản nâng cấp của luồng C (xem KE_HOACH.md bước 2) đổi bước tìm
thành tìm theo ngữ nghĩa (embedding + ChromaDB) rồi đưa 5 bài đó cho LLM
trả lời — khung không đổi, chỉ thay “cách tìm” bên trong.

## Mức 3 — Chi tiết từng module (file nào làm việc gì)

### 3.1. `jarvis/fetch_feeds.py` — Thu thập

| Vai trò | Chi tiết |
|---|---|
| Vào | `sources.json`: danh sách `{name, url, kind}` |
| Ra | `data/articles.json`: danh sách bài đã dedupe |
| Hàm chính | `fetch_all()`, `parse_feed()`, `clean()`, `_text()`, `_link()`, `_date()` |
| Xử lý lỗi | Mỗi nguồn try/except riêng; nguồn lỗi chỉ ghi vào báo cáo |
| Giới hạn | arXiv API mỗi nguồn 20 bài; RSS các nguồn khác lấy theo feed của họ |

Bài viết (Article) là đơn vị nhỏ nhất chảy qua toàn bộ chương trình.
Mọi tầng sau đều làm việc trên Article, không làm việc trực tiếp với XML.

### 3.2. `jarvis/memory.py` — Trí nhớ & chấm điểm

| Vai trò | Chi tiết |
|---|---|
| Vào | `profile.json` + danh sách Article |
| Ra | Article kèm `score` và `topics` |
| Hàm chính | `load_profile()`, `load_articles()`, `score_article()`, `rank_articles()`, `like()` |
| Công thức MVP | Tiêu đề trúng keyword = 2 điểm, nội dung trúng = 1 điểm, nhân với `weight` của topic; trúng `blocked_keywords` thì điểm = 0 |
| Học từ bạn | `like(link)` tăng weight của topic của bài đó thêm 0.2, tối đa 5.0. Đây là học đơn giản, chưa phải ML thật |

Đây là module bạn sẽ sửa nhiều nhất khi tùy chỉnh. Muốn Jarvis hiểu bạn
hơn thì sửa `profile.json` (keyword, weight, blocked), không cần sửa code.

### 3.3. `jarvis/summarize.py` — Tóm tắt

| Vai trò | Chi tiết |
|---|---|
| Vào | Tóm tắt gốc (abstract/mô tả) + danh sách keyword của profile |
| Ra | Tối đa 3 câu, tối đa 600 ký tự |
| Hàm chính | `extractive_summary()`, `all_keywords()`, `summarize_with_llm()` (chỗ cắm LLM, MVP trả về None) |
| Vì sao chưa dùng LLM | Để MVP chạy được ngay, 0 đồng, không cần key. Khi có key, chỉ cần cài đặt `summarize_with_llm()` mà không phải sửa luồng briefing |

### 3.4. `jarvis/briefing.py` — Tạo bản tin

| Vai trò | Chi tiết |
|---|---|
| Vào | Bài đã chấm điểm, tham số `days`, `top_n` |
| Ra | Chuỗi Markdown + file `data/briefing-YYYY-MM-DD.md` |
| Hàm chính | `make_briefing()`, `save_briefing()` |
| Quy tắc | Không tự kéo mạng, không tự chấm điểm lại theo cách khác — chỉ dùng kết quả của `memory.py` và `summarize.py` |

### 3.5. `run.py` và `app.py` — Giao diện

| File | Vai trò |
|---|---|
| `run.py` | CLI duy nhất: `fetch`, `top`, `ask "<từ khóa>"`, `briefing [--days N] [--top N]`. Đây là “bảng điều khiển” để kiểm chứng mọi tầng |
| `app.py` | Dashboard Streamlit tùy chọn: chọn topic để lọc, xem 30 bài đầu, bấm nút tạo briefing. Cần `pip install streamlit`; không có nó thì CLI vẫn đủ |

### 3.6. Cấu hình — 2 file JSON quyết định hành vi

- `profile.json`: bạn là ai, thích gì. Gồm `topics` (mỗi topic có `name`,
  `keywords`, `weight`), `blocked_keywords`, `briefing` (`days`, `top_n`,
  giờ chạy), `language`.
- `sources.json`: đọc ở đâu. Gồm `sources` (mỗi nguồn có `name`, `url`,
  `kind`: paper/news/project).

Muốn đổi hành vi của Jarvis thì đổi 2 file này trước, đổi code sau.

## Mức 4 — Schema dữ liệu (hình dạng thật của dữ liệu)

### Article (1 bài trong `data/articles.json`)

```json
{
  "title": "Benchmark for Structured Retrieval-Augmented Generation in Perovskite Photovoltaics",
  "link": "https://arxiv.org/abs/2610.25575v1",
  "summary": "While retrieval-augmented language models increasingly serve as...",
  "source": "arXiv ML materials",
  "kind": "paper",
  "published": "2026-10-18T00:00:00+00:00"
}
```

Sau khi chấm điểm, thêm 2 trường: `"score": 12.0`, `"topics": ["Pin mặt trời tandem / perovskite"]`.

### Topic (1 chủ đề trong `profile.json`)

```json
{
  "name": "MoS2",
  "keywords": ["mos2", "molybdenum disulfide", "2d material"],
  "weight": 3
}
```

### Briefing (1 file `data/briefing-YYYY-MM-DD.md`)

Mỗi bài là 1 mục: tiêu đề, dòng nguồn/điểm/chủ đề/ngày, 1 đoạn tóm tắt,
1 link gốc, và dòng ghi chú cuối file nói rõ tóm tắt là trích xuất,
chưa phải LLM viết lại.

## Mức 5 — Thứ tự xây dựng (đọc khung xong thì làm theo thứ tự này)

1. **Khóa nguồn + schema trước:** chốt `sources.json` và hình dạng Article.
   Nếu schema đổi giữa chừng, mọi module phải sửa theo.
2. **Làm fetch chạy được trước:** 1 nguồn OK là đủ để đi tiếp, đừng đợi
   đủ 8 nguồn mới test.
3. **Làm score chạy được trước:** keyword đơn giản trước, ngữ nghĩa sau.
   Score sai thì briefing sai, dù tóm tắt có hay đến đâu.
4. **Làm briefing chạy được trước:** file Markdown trước, Telegram sau,
   giọng nói sau cùng.
5. **Mới thêm LLM/RAG:** khi briefing bằng trích xuất đã có 70% bài đáng
   đọc, lúc đó LLM chỉ làm cho bản tin hay hơn, không phải gánh cả hệ thống.
6. **Mới thêm “tay làm việc” (SCAPS):** chỉ cho chạy script đã duyệt sẵn,
   tham số trong whitelist, log mọi lệnh. Xem KE_HOACH.md bước 5.

## Sơ đồ đọc code (bắt đầu từ đâu)

```
Muốn hiểu toàn cảnh  → đọc file này (KHUNG_CHUONG_TRINH.md)
Muốn chạy thử ngay   → đọc README.md, gõ: python3 run.py fetch
Muốn hiểu 1 luồng    → đọc run.py trước, rồi theo hàm nó gọi
Muốn tùy chỉnh       → sửa profile.json / sources.json, không sửa code
Muốn nâng cấp        → đọc KE_HOACH.md, làm theo đúng thứ tự bước 1 → 5
```

## Những gì khung này cố tình CHƯA có

- Chưa có database thật (SQLite/ChromaDB) — MVP dùng JSON cho dễ nhìn,
  dễ sửa tay. Đổi sang database ở bước 1–2 của kế hoạch.
- Chưa có xác thực, phân quyền, multi-user — đây là công cụ cá nhân
  chạy trên máy bạn, không phải web app cho nhiều người.
- Chưa có voice và hand tracking — đó là project Iron Man spatial riêng
  ở `workspace/ironman-spatial/`, không gộp vào Jarvis briefing này.
