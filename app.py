"""Dashboard Streamlit (tuy chon). Chay: streamlit run app.py

Neu chua cai streamlit thi dung CLI run.py thay the - chuc nang giong nhau.
"""
try:
    import streamlit as st
except ImportError:
    raise SystemExit("Chua cai streamlit. Chay: pip install streamlit  (hoac dung: python3 run.py briefing)")

from jarvis.briefing import make_briefing
from jarvis.memory import load_articles, load_profile, rank_articles

st.set_page_config(page_title="Jarvis MVP", layout="wide")
st.title("Jarvis MVP - Feed cua PHAM")
profile = load_profile()
ranked = rank_articles(load_articles(), profile)
topic = st.selectbox("Loc theo chu de", ["Tat ca"] + [t["name"] for t in profile["topics"]])
shown = ranked if topic == "Tat ca" else [a for a in ranked if topic in a["topics"]]
for a in shown[:30]:
    st.markdown(f"### [{a['title']}]({a['link']})")
    st.caption(f"{a['source']} | Diem {a['score']} | {', '.join(a['topics']) or 'Chung'} | {a.get('published','')[:10]}")
    st.write(a.get("summary", "")[:500])
st.divider()
if st.button("Tao briefing hom nay"):
    st.markdown(make_briefing())
