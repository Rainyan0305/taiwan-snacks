# 🏮 台灣小吃圖鑑

用「圖鑑卡」的方式介紹台灣小吃的靜態網站。每道小吃都有固定的資料欄位與段落：基本資料、起源故事、特色與口感、推薦吃法、小知識、相關小吃。

這個專案的重點是 [`CLAUDE.md`](./CLAUDE.md)：一份給 AI 看的規則說明書。AI 讀完後，就能用同一套格式持續新增小吃，不用每次重新說明風格與結構。

## 🌐 線上瀏覽

`https://<你的 GitHub 帳號>.github.io/<repo 名稱>/`

## 📁 專案結構

| 路徑 | 說明 |
| --- | --- |
| `CLAUDE.md` / `AGENTS.md` | AI 協作規則 |
| `index.html` | 首頁：搜尋、分類篩選、圖鑑卡片 |
| `about.html` | 關於本站 |
| `data/snacks.json` | 所有小吃的索引資料 |
| `snacks/` | 每道小吃一頁 |
| `templates/snack-template.html` | 新增小吃用的模板 |
| `assets/` | 樣式與首頁腳本 |
| `scripts/check.py` | 規則檢查程式 |

## ➕ 新增小吃

對 AI 說：

> 請閱讀 CLAUDE.md，新增一道小吃「豆花」。

AI 會依照 `CLAUDE.md` 第 5 節的 6 個步驟完成，最後執行：

```bash
python3 scripts/check.py
```

## 💻 本機預覽

```bash
python3 -m http.server 8000
# 打開 http://localhost:8000
```

## 🛠 技術

純 HTML + CSS + 原生 JavaScript，沒有任何建置步驟，直接部署在 GitHub Pages。
