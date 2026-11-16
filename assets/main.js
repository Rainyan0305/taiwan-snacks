// 台灣小吃圖鑑 — 首頁腳本
// 讀取 data/snacks.json，產生圖鑑卡片，並提供搜尋與分類篩選。
// 新增分類時：在 CATEGORY_LABELS 加一筆（見 CLAUDE.md 第 4 節）。

const CATEGORY_LABELS = {
  rice: "飯食",
  noodle: "麵食",
  fried: "煎炸",
  soup: "湯品",
  sweet: "甜點",
  drink: "飲品",
};

const state = { snacks: [], category: "all", query: "" };

const grid = document.getElementById("grid");
const chips = document.getElementById("chips");
const search = document.getElementById("search");
const count = document.getElementById("count");

function el(tag, attrs = {}, children = []) {
  const node = document.createElement(tag);
  for (const [key, value] of Object.entries(attrs)) {
    if (key === "text") node.textContent = value;
    else node.setAttribute(key, value);
  }
  for (const child of children) node.append(child);
  return node;
}

function renderChips() {
  const used = new Set(state.snacks.map((s) => s.category));
  const options = [["all", "全部"], ...Object.entries(CATEGORY_LABELS).filter(([k]) => used.has(k))];
  chips.replaceChildren(
    ...options.map(([key, label]) => {
      const btn = el("button", {
        class: "chip",
        type: "button",
        "aria-pressed": String(state.category === key),
        text: label,
      });
      btn.addEventListener("click", () => {
        state.category = key;
        renderChips();
        renderGrid();
      });
      return btn;
    })
  );
}

function matches(snack) {
  if (state.category !== "all" && snack.category !== state.category) return false;
  if (!state.query) return true;
  const haystack = [snack.name, snack.nameEn, snack.summary, snack.region, ...snack.tags]
    .join(" ")
    .toLowerCase();
  return haystack.includes(state.query);
}

function card(snack, index) {
  const no = "No." + String(index + 1).padStart(3, "0");
  return el("a", { class: "card", href: `snacks/${snack.slug}.html`, "data-category": snack.category }, [
    el("div", { class: "card-top" }, [
      el("span", { class: "card-no", text: no }),
      el("span", { class: "card-emoji", "aria-hidden": "true", text: snack.emoji }),
    ]),
    el("div", { class: "card-body" }, [
      el("h2", { text: snack.name }),
      el("p", { class: "card-en", text: snack.nameEn }),
      el("p", { class: "card-summary", text: snack.summary }),
      el("div", { class: "card-tags" }, [
        el("span", { class: "tag tag-cat", text: CATEGORY_LABELS[snack.category] || snack.category }),
        ...snack.tags.map((t) => el("span", { class: "tag", text: "#" + t })),
      ]),
    ]),
  ]);
}

function renderGrid() {
  const shown = state.snacks.map((s, i) => [s, i]).filter(([s]) => matches(s));
  count.textContent = `共 ${shown.length} 道小吃`;
  if (shown.length === 0) {
    grid.replaceChildren(el("p", { class: "empty", text: "找不到符合的小吃，換個關鍵字試試？" }));
    return;
  }
  grid.replaceChildren(...shown.map(([s, i]) => card(s, i)));
}

search.addEventListener("input", (e) => {
  state.query = e.target.value.trim().toLowerCase();
  renderGrid();
});

fetch("data/snacks.json")
  .then((res) => res.json())
  .then((data) => {
    state.snacks = data;
    renderChips();
    renderGrid();
  })
  .catch(() => {
    grid.replaceChildren(
      el("p", {
        class: "empty",
        text: "資料載入失敗。若是直接開啟檔案，請改用 python3 -m http.server 預覽。",
      })
    );
  });
