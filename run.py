#!/usr/bin/env python3
"""CLI chinh cua Jarvis MVP.

  python3 run.py fetch              # keo RSS, luu data/articles.json
  python3 run.py briefing           # tao data/briefing-YYYY-MM-DD.md
  python3 run.py briefing --days 7  # doi cua so ngay
  python3 run.py ask "MoS2"        # tim trong bai da luu, tra top 5
  python3 run.py top                # in 10 bai diem cao nhat
"""
import argparse
import sys

sys.path.insert(0, ".")

from jarvis.briefing import save_briefing
from jarvis.fetch_feeds import fetch_all
from jarvis.memory import load_articles, load_profile, rank_articles


def cmd_fetch(_args):
    result = fetch_all()
    print(f"Tong so bai da luu: {result['total_stored']} (moi trong lan nay: {result['new_this_run']})")
    for name, status in result["report"].items():
        print(f"  - {name}: {status}")


def cmd_briefing(args):
    out, text = save_briefing(days=args.days, top_n=args.top)
    print(f"Da tao: {out}")
    print(text[:3000])


def cmd_top(args):
    profile = load_profile()
    ranked = rank_articles(load_articles(), profile)[: args.top]
    if not ranked:
        print("Chua co du lieu. Chay: python3 run.py fetch")
        return
    for i, a in enumerate(ranked, 1):
        print(f"{i}. [{a['score']}] {a['title']} ({a['source']})")
        print(f"   {a['link']}")


def cmd_ask(args):
    q = args.query.lower()
    profile = load_profile()
    hits = [a for a in load_articles()
            if q in a["title"].lower() or q in a.get("summary", "").lower()]
    if not hits:
        print(f"Khong thay bai nao chua '{args.query}' trong du lieu da keo. Thu chay fetch truoc, hoac doi tu khoa rong hon.")
        return
    for a in rank_articles(hits, profile)[:5]:
        print(f"- [{a['score']}] {a['title']} ({a['source']})")
        print(f"  {a['link']}")
        print(f"  {a.get('summary','')[:300]}")
        print()


def main():
    p = argparse.ArgumentParser(description="Jarvis MVP")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("fetch")
    b = sub.add_parser("briefing")
    b.add_argument("--days", type=int, default=3)
    b.add_argument("--top", type=int, default=12)
    t = sub.add_parser("top")
    t.add_argument("--top", type=int, default=10)
    a = sub.add_parser("ask")
    a.add_argument("query")
    args = p.parse_args()
    {"fetch": cmd_fetch, "briefing": cmd_briefing, "top": cmd_top, "ask": cmd_ask}[args.cmd](args)


if __name__ == "__main__":
    main()
