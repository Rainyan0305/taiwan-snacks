#!/usr/bin/env python3
"""檢查台灣小吃圖鑑是否符合 CLAUDE.md 的規則。

用法：在專案根目錄執行  python3 scripts/check.py
只使用 Python 標準函式庫，不需要安裝任何套件。
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CATEGORIES = {"rice", "noodle", "fried", "soup", "sweet", "drink"}
FIELDS = ["slug", "name", "nameEn", "emoji", "category", "region", "price", "summary", "tags"]
SECTIONS = ["hero", "info", "origin", "taste", "howto", "trivia", "related"]

errors = []


def err(where, msg):
    errors.append(f"✗ {where}: {msg}")


# ---------- data/snacks.json ----------
try:
    snacks = json.loads((ROOT / "data/snacks.json").read_text(encoding="utf-8"))
except Exception as e:  # noqa: BLE001
    print(f"✗ data/snacks.json 無法解析：{e}")
    sys.exit(1)

slugs = set()
for i, s in enumerate(snacks):
    where = f"snacks.json[{i}] {s.get('name', '?')}"
    for f in FIELDS:
        if not s.get(f):
            err(where, f"缺少欄位 {f}")
    slug = s.get("slug", "")
    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", slug):
        err(where, f"slug「{slug}」只能用小寫英文、數字與連字號")
    if slug in slugs:
        err(where, f"slug「{slug}」重複")
    slugs.add(slug)
    if s.get("category") not in CATEGORIES:
        err(where, f"分類「{s.get('category')}」不在 CLAUDE.md 的分類表中")
    if len(s.get("summary", "")) > 40:
        err(where, f"summary 超過 40 字（目前 {len(s['summary'])} 字）")
    if not 1 <= len(s.get("tags", [])) <= 3:
        err(where, "tags 需要 1～3 個")
    if not s.get("price", "").startswith("約 NT$ "):
        err(where, "price 格式需為「約 NT$ 最低–最高」")

# ---------- snacks/*.html ----------
pages = {p.stem for p in (ROOT / "snacks").glob("*.html")}
for slug in sorted(slugs - pages):
    err(f"snacks/{slug}.html", "JSON 有這筆資料，但找不到頁面")
for slug in sorted(pages - slugs):
    err(f"snacks/{slug}.html", "有頁面，但 data/snacks.json 沒有這筆資料（首頁不會顯示）")

by_slug = {s.get("slug"): s for s in snacks}
for slug in sorted(pages & slugs):
    path = f"snacks/{slug}.html"
    html = (ROOT / path).read_text(encoding="utf-8")
    s = by_slug[slug]

    if "{{" in html:
        err(path, "還有沒替換的 {{佔位符}}")
    if f"<title>{s['name']}｜台灣小吃圖鑑</title>" not in html:
        err(path, "<title> 格式需為「中文名｜台灣小吃圖鑑」")
    if f'<body data-category="{s["category"]}">' not in html:
        err(path, "<body data-category> 與 JSON 的 category 不一致")
    if re.search(r'(href|src)="/', html):
        err(path, "使用了根目錄絕對路徑，請改成相對路徑")
    if re.search(r'\sstyle="', html):
        err(path, "不可使用 inline style")

    positions = [html.find(f'id="{sid}"') for sid in SECTIONS]
    for sid, pos in zip(SECTIONS, positions):
        if pos == -1:
            err(path, f"缺少區塊 #{sid}")
    found = [p for p in positions if p != -1]
    if found != sorted(found):
        err(path, "區塊順序不對，應為 " + " → ".join(SECTIONS))

    info = re.search(r'id="info">(.*?)</section>', html, re.S)
    if info and len(re.findall(r"<dt>", info.group(1))) != 4:
        err(path, "基本資料必須剛好 4 格")

    taste = re.search(r'id="taste">(.*?)</section>', html, re.S)
    if taste and not 3 <= len(re.findall(r"<li>", taste.group(1))) <= 5:
        err(path, "特色與口感需要 3～5 條")

    howto = re.search(r'id="howto">(.*?)</section>', html, re.S)
    if howto and not 3 <= len(re.findall(r"<li>", howto.group(1))) <= 4:
        err(path, "推薦吃法需要 3～4 條")

    related = re.search(r'id="related">(.*?)</section>', html, re.S)
    if related:
        links = re.findall(r'href="([a-z0-9-]+)\.html"', related.group(1))
        if not 1 <= len(links) <= 3:
            err(path, "相關小吃需要 1～3 個連結")
        for target in links:
            if target not in pages:
                err(path, f"相關小吃連到不存在的頁面 {target}.html")
            if target == slug:
                err(path, "相關小吃不能連到自己")

# ---------- 結果 ----------
if errors:
    print("\n".join(errors))
    print(f"\n共 {len(errors)} 個問題，請依 CLAUDE.md 修正。")
    sys.exit(1)
print(f"✓ 全部通過：{len(snacks)} 道小吃，{len(pages)} 個頁面都符合 CLAUDE.md 規則。")
