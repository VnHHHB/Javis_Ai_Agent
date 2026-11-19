"""Tom tat trich xuat (extractive) - chay offline, khong can API key.

Chon toi da 3 cau chua nhieu keyword cua profile nhat. Khi co API key,
ham summarize_with_llm() la cho de cam LLM vao (xem KE_HOACH.md buoc 2),
nhung MVP mac dinh KHONG goi API de khong ton tien / khong loi khi chua co key.
"""
import re

SENT_RE = re.compile(r"(?<=[.!?])\s+")


def extractive_summary(text, keywords, max_sentences=3, max_chars=600):
    if not text:
        return ""
    sentences = [s.strip() for s in SENT_RE.split(text) if len(s.strip()) > 30]
    if not sentences:
        return text[:max_chars]
    kws = [k.lower() for k in keywords]
    def sent_score(s):
        low = s.lower()
        return sum(1 for k in kws if k in low)
    ranked = sorted(sentences, key=sent_score, reverse=True)
    picked = [s for s in ranked[:max_sentences] if sent_score(s) > 0] or sentences[:1]
    out = " ".join(picked)
    return out[:max_chars] + ("..." if len(out) > max_chars else "")


def all_keywords(profile):
    kws = []
    for t in profile.get("topics", []):
        kws.extend(t["keywords"])
    return kws


def summarize_with_llm(text, api_key=None):
    """Cho san de nang cap. Tra ve None neu chua co key -> caller dung ban trich xuat."""
    if not api_key:
        return None
    # TODO buoc 2: goi OpenAI/Gemini o day, chi khi user da set key trong .env
    # Khong goi that o MVP de tranh goi API ngoai y muon.
    return None
