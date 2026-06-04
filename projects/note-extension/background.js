// background.js — note 自動投稿ボット（MV3 サービスワーカー）
// あなたのChromeの中で動き、Geminiで記事生成 → note に自動投稿します。

const DEFAULTS = {
  urlname: "light_roses761",   // 投稿先アカウント（https://note.com/＜ここ＞）
  theme: "auto",               // "auto"=アカウントから自動推定 / 文字列で固定
  apiKey: "",                  // Gemini APIキー（ポップアップで設定）
  model: "gemini-2.5-pro",
  targetChars: 20000,
  publish: false,              // false=下書き / true=公開（まずfalse推奨）
  tags: ["毎日note"],
  intervalMinutes: 180,
  maxPerDay: 3,                // 1日の投稿上限（凍結対策。必ず付ける）
  running: false
};

async function getSettings() {
  const s = await chrome.storage.local.get("settings");
  return { ...DEFAULTS, ...(s.settings || {}) };
}
async function setSettings(patch) {
  const next = { ...(await getSettings()), ...patch };
  await chrome.storage.local.set({ settings: next });
  return next;
}
async function log(msg) {
  const t = new Date().toLocaleString("ja-JP");
  const { logs = [] } = await chrome.storage.local.get("logs");
  logs.unshift(`[${t}] ${msg}`);
  await chrome.storage.local.set({ logs: logs.slice(0, 60) });
  console.log("[note-bot]", msg);
}

// ---------- 1日の上限 ----------
const today = () => new Date().toISOString().slice(0, 10);
async function getCount() {
  const { count } = await chrome.storage.local.get("count");
  return (count && count.date === today()) ? count.n : 0;
}
async function bump() {
  await chrome.storage.local.set({ count: { date: today(), n: (await getCount()) + 1 } });
}

// ---------- Gemini ----------
async function gem(apiKey, model, prompt) {
  const url = `https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent?key=${apiKey}`;
  const res = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ contents: [{ parts: [{ text: prompt }] }] })
  });
  if (!res.ok) throw new Error("Gemini API " + res.status + " " + (await res.text()).slice(0, 200));
  const j = await res.json();
  return (j.candidates?.[0]?.content?.parts?.[0]?.text || "").trim();
}

async function genArticle(s, theme) {
  const outline = await gem(s.apiKey, s.model,
    `テーマ「${theme}」で長文note記事の構成をJSONのみで返す（説明やコードフェンス不要）:\n` +
    `{"title":"30字前後の魅力的なタイトル","sections":["見出し1","見出し2", ... 8〜10個]}\n` +
    `本文合計 約${s.targetChars}字を想定。`);
  let title = theme, sections = [];
  try {
    const o = JSON.parse(outline.replace(/^```[a-zA-Z]*|```$/g, "").trim());
    title = o.title; sections = o.sections;
  } catch (e) { sections = [1,2,3,4,5,6,7,8].map(i => `${theme}のポイント${i}`); }

  const per = Math.max(800, Math.floor(s.targetChars / Math.max(1, sections.length)));
  const parts = [];
  let total = 0;
  for (const h of sections) {
    const p = await gem(s.apiKey, s.model,
      `記事「${title}」（テーマ:${theme}）の節「${h}」を約${per}字で執筆。` +
      `見出しは「## ${h}」で開始。具体例・体験談を入れて読み応えを出す。前置き禁止・本文のみ。`);
    parts.push(p.startsWith("#") ? p : `## ${h}\n\n${p}`);
    total += p.length;
    if (total >= s.targetChars) break;
  }
  const body = parts.join("\n\n");
  await log(`生成: ${title}（約${body.length}字）`);
  return { title, body };
}

// ---------- note: テーマ自動取得 ----------
async function detectTheme(urlname) {
  const tab = await chrome.tabs.create({ url: `https://note.com/${urlname}`, active: false });
  await waitComplete(tab.id);
  await sleep(2000);
  const [{ result }] = await chrome.scripting.executeScript({
    target: { tabId: tab.id },
    args: [urlname],
    func: async (u) => {
      const out = { titles: [], bio: "" };
      try { const r = await fetch(`/api/v2/creators/${u}`); if (r.ok) { const d = (await r.json()).data || {}; out.bio = [d.nickname, d.profile, d.description].filter(Boolean).join("\n"); } } catch (e) {}
      try { const r = await fetch(`/api/v2/creators/${u}/contents?kind=note&page=1`); if (r.ok) { const d = (await r.json()).data || {}; out.titles = (d.contents || []).map(c => c.name).filter(Boolean); } } catch (e) {}
      return out;
    }
  });
  await chrome.tabs.remove(tab.id).catch(() => {});
  return result;
}

// ---------- note: 投稿 ----------
async function postToNote(s, article) {
  const tab = await chrome.tabs.create({ url: "https://note.com/notes/new", active: true });
  await waitComplete(tab.id);
  await sleep(3500);
  const [{ result }] = await chrome.scripting.executeScript({
    target: { tabId: tab.id },
    args: [article.title, article.body, s.publish, s.tags],
    func: postInPage
  });
  return result;
}

// ↓ note の編集画面で実行されるDOM操作（UI変更でズレたらここを調整）
// 失敗時は画面の状態(候補要素・ボタン名)を文字列で返すので、それを見てセレクタを直せる。
function postInPage(title, bodyText, publish, tags) {
  return (async () => {
    const sleep = (ms) => new Promise(r => setTimeout(r, ms));
    const pick = (sels) => { for (const s of sels) { const el = document.querySelector(s); if (el) return el; } return null; };
    // 画面診断：今あるボタン名・編集系要素を一覧化（失敗時に返して原因特定に使う）
    const diag = () => {
      const btns = [...document.querySelectorAll("button")]
        .map(b => (b.innerText || b.getAttribute("aria-label") || "").trim())
        .filter(Boolean).slice(0, 25);
      const edits = [...document.querySelectorAll('textarea,input,[contenteditable="true"]')]
        .map(e => `${e.tagName.toLowerCase()}[ph=${e.getAttribute("placeholder") || e.getAttribute("aria-label") || e.getAttribute("data-placeholder") || ""}]`)
        .slice(0, 15);
      return ` | URL:${location.pathname} | 編集欄:${JSON.stringify(edits)} | ボタン:${JSON.stringify(btns)}`;
    };
    const clickByText = (texts) => {
      for (const b of document.querySelectorAll('button,[role="button"],a')) {
        const t = (b.innerText || b.getAttribute("aria-label") || "").trim();
        if (texts.some(x => t.includes(x))) { b.click(); return true; }
      }
      return false;
    };

    if (location.pathname.includes("/login")) return "NG: ログイン画面です（noteにログインしてから実行してください）" + diag();

    // --- タイトル ---
    const tb = pick([
      'textarea[placeholder="記事タイトル"]',
      'textarea[placeholder*="タイトル"]',
      'input[placeholder*="タイトル"]',
      '[contenteditable="true"][data-placeholder*="タイトル"]',
      'textarea',
    ]);
    if (!tb) return "NG: タイトル欄が見つからない（ログイン切れ/UI変更の可能性）" + diag();
    tb.focus();
    if (tb.isContentEditable) { document.execCommand("insertText", false, title); }
    else if (!document.execCommand("insertText", false, title)) {
      tb.value = title; tb.dispatchEvent(new Event("input", { bubbles: true }));
    }
    await sleep(800);

    // --- 本文 ---
    const bb = pick(['div.ProseMirror[contenteditable="true"]', 'div[contenteditable="true"][role="textbox"]', '[contenteditable="true"]']);
    if (!bb) return "NG: 本文欄が見つからない" + diag();
    bb.focus();
    for (const para of bodyText.split("\n").filter(x => x.trim())) {
      // 「## 見出し」は note のマークダウン変換を狙って "## " を先に確定入力する
      const m = para.match(/^(#{1,3})\s+(.*)$/);
      if (m) {
        document.execCommand("insertText", false, m[1] + " ");
        document.execCommand("insertText", false, m[2]);
      } else {
        document.execCommand("insertText", false, para);
      }
      document.execCommand("insertParagraph");
    }
    await sleep(1500);

    if (!publish) return "OK: 本文まで入力（下書きはnoteが自動保存）" + diag();

    if (!clickByText(["公開に進む", "公開設定", "公開"])) return "OK(本文まで): 「公開に進む」ボタンが見つからず停止" + diag();
    await sleep(2000);
    const done = clickByText(["投稿する", "公開する"]);
    await sleep(3000);
    return (done ? "OK: 公開まで実行" : "OK(公開画面まで): 最終ボタンが見つからず停止") + diag();
  })();
}

// ---------- helpers ----------
const sleep = (ms) => new Promise(r => setTimeout(r, ms));
function waitComplete(tabId) {
  return new Promise((resolve) => {
    const fn = (id, info) => { if (id === tabId && info.status === "complete") { chrome.tabs.onUpdated.removeListener(fn); resolve(); } };
    chrome.tabs.onUpdated.addListener(fn);
    setTimeout(() => { chrome.tabs.onUpdated.removeListener(fn); resolve(); }, 20000);
  });
}

// ---------- 本体ジョブ ----------
async function runJob() {
  try {
    const s = await getSettings();
    if (!s.apiKey) { await log("Geminiキー未設定。ポップアップで設定してください。"); return; }
    if (await getCount() >= s.maxPerDay) { await log(`本日の上限 ${s.maxPerDay} 件に到達。`); return; }

    let theme = (s.theme || "").trim();
    if (!theme || theme.toLowerCase() === "auto") {
      const info = await detectTheme(s.urlname);
      if (!info || (!info.titles?.length && !info.bio)) { await log("テーマ自動取得に失敗（noteログイン確認 or theme手動指定を）"); return; }
      theme = (await gem(s.apiKey, s.model,
        `次のnoteのプロフィールと記事タイトルから、今後書くべき記事のテーマを日本語1文で。前置き不要、テーマだけ。\n` +
        `プロフ:${info.bio}\nタイトル:\n- ${(info.titles || []).join("\n- ")}`)).trim().replace(/^[「"']|[」"']$/g, "");
      await log("テーマ自動判定: " + theme);
    }

    const article = await genArticle(s, theme);
    const res = await postToNote(s, article);
    await log("投稿結果: " + res);
    if (res.startsWith("OK")) await bump();
  } catch (e) {
    await log("エラー: " + (e?.message || e));
  }
}

// ---------- アラーム & ポップアップ連携 ----------
chrome.alarms.onAlarm.addListener((a) => { if (a.name === "tick") runJob(); });

chrome.runtime.onMessage.addListener((msg, _sender, sendResponse) => {
  (async () => {
    if (msg.type === "save") {
      sendResponse({ ok: true, settings: await setSettings(msg.settings) });
    } else if (msg.type === "start") {
      const s = await getSettings();
      await chrome.alarms.create("tick", { periodInMinutes: Math.max(5, s.intervalMinutes) });
      await setSettings({ running: true });
      await log(`開始：${s.intervalMinutes}分ごと / 1日最大 ${s.maxPerDay} 件`);
      runJob();
      sendResponse({ ok: true });
    } else if (msg.type === "stop") {
      await chrome.alarms.clear("tick");
      await setSettings({ running: false });
      await log("停止しました。");
      sendResponse({ ok: true });
    } else if (msg.type === "runNow") {
      await log("手動で1回実行します…");
      runJob();
      sendResponse({ ok: true });
    } else if (msg.type === "status") {
      const { logs = [] } = await chrome.storage.local.get("logs");
      sendResponse({ settings: await getSettings(), count: await getCount(), logs });
    }
  })();
  return true; // 非同期レスポンス
});
