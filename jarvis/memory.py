"""Profile + cham diem lien quan. Day la 'tri nho so thich' cua Jarvis MVP.

Nguyen tac: tieu de trung keyword = 2 diem, noi dung = 1 diem, nhan voi
weight cua topic. Bai trung blocked_keyword thi loai luon.
"""
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent


def load_profile(path=None):
    path = Path(path) if path else BASE / "profile.json"
    return json.loads(path.read_text(encoding="utf-8"))


def load_articles(path=None):
    path = Path(path) if path else BASE / "data" / "articles.json"
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8"))


def score_article(article, profile):
    title = article.get("title", "").lower()
    body = article.get("summary", "").lower()
    blocked = [b.lower() for b in profile.get("blocked_keywords", [])]
    if any(b in title or b in body for b in blocked if b):
        return 0.0, []
    score, matched_topics = 0.0, []
    for topic in profile.get("topics", []):
        topic_score = 0
        for kw in topic["keywords"]:
            kw = kw.lower()
            if kw in title:
                topic_score += 2
            elif kw in body:
                topic_score += 1
        if topic_score:
            score += topic_score * topic.get("weight", 1)
            matched_topics.append(topic["name"])
    return score, matched_topics


def rank_articles(articles, profile):
    ranked = []
    for a in articles:
        score, topics = score_article(a, profile)
        ranked.append({**a, "score": score, "topics": topics})
    ranked.sort(key=lambda x: (x["score"], x.get("published", "")), reverse=True)
    return ranked


def like(article_link, profile_path=None):
    """Tang weight topic cua bai duoc 'thich'. Luu y: day la hoc don gian,
    chua phai ML that - du de MVP co cam giac ca nhan hoa."""
    profile = load_profile(profile_path)
    articles = load_articles()
    target = next((a for a in articles if a["link"] == article_link), None)
    if not target:
        return profile
    _, topics = score_article(target, profile)
    for topic in profile["topics"]:
        if topic["name"] in topics:
            topic["weight"] = round(min(topic["weight"] + 0.2, 5.0), 2)
    path = Path(profile_path) if profile_path else BASE / "profile.json"
    path.write_text(json.dumps(profile, ensure_ascii=False, indent=2), encoding="utf-8")
    return profile
