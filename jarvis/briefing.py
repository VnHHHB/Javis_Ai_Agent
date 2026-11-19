"""Tao ban tin sang dang Markdown tu bai da cham diem."""
from datetime import datetime, timedelta, timezone
from pathlib import Path

from .memory import load_articles, load_profile, rank_articles
from .summarize import all_keywords, extractive_summary

BASE = Path(__file__).resolve().parent.parent


def make_briefing(days=3, top_n=12):
    profile = load_profile()
    articles = load_articles()
    if not articles:
        return "# Briefing Jarvis MVP\n\nChua co du lieu. Chay `python3 run.py fetch` truoc.\n"
    cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
    recent = [a for a in articles if a.get("published", "") >= cutoff] or articles
    ranked = [a for a in rank_articles(recent, profile) if a["score"] > 0][:top_n]
    if not ranked:
        ranked = rank_articles(recent, profile)[:top_n]
    kws = all_keywords(profile)
    lines = [
        f"# Briefing - {datetime.now().strftime('%d/%m/%Y %H:%M')}",
        "",
        f"Tu {len(recent)} bai trong {days} ngay qua, chon {len(ranked)} bai lien quan nhat theo profile cua ban.",
        "",
    ]
    for i, a in enumerate(ranked, 1):
        summary = extractive_summary(a.get("summary", ""), kws) or a.get("summary", "")[:300]
        topics = ", ".join(a["topics"]) if a["topics"] else "Chung"
        lines += [
            f"## {i}. {a['title']}",
            f"- Nguon: {a['source']} | Diem: {a['score']} | Chu de: {topics} | {a.get('published','')[:10]}",
            f"- Tom tat: {summary}",
            f"- Link: {a['link']}",
            "",
        ]
    lines.append("_Ghi chu: tom tat MVP la trich xuat cau goc, chua phai LLM viet lai. Xem KE_HOACH.md de nang cap._")
    return "\n".join(lines)


def save_briefing(days=3, top_n=12):
    text = make_briefing(days, top_n)
    out = BASE / "data" / f"briefing-{datetime.now().strftime('%Y-%m-%d')}.md"
    out.write_text(text, encoding="utf-8")
    return out, text
