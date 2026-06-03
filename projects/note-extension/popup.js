// popup.js — 設定UIとボタン操作

const $ = (id) => document.getElementById(id);
const FIELDS = ["apiKey", "urlname", "theme", "model", "targetChars", "maxPerDay", "intervalMinutes"];

function send(type, extra = {}) {
  return chrome.runtime.sendMessage({ type, ...extra });
}

async function refresh() {
  const r = await send("status");
  if (!r) return;
  const s = r.settings;
  for (const f of FIELDS) if ($(f)) $(f).value = s[f] ?? "";
  $("publish").value = String(!!s.publish);
  $("status").textContent =
    `状態: ${s.running ? "▶ 稼働中" : "停止中"} ／ 本日の投稿: ${r.count} / ${s.maxPerDay}`;
  $("logs").textContent = (r.logs || []).join("\n");
}

function collect() {
  return {
    apiKey: $("apiKey").value.trim(),
    urlname: $("urlname").value.trim() || "light_roses761",
    theme: $("theme").value.trim() || "auto",
    model: $("model").value.trim() || "gemini-2.5-flash",
    targetChars: parseInt($("targetChars").value) || 20000,
    maxPerDay: parseInt($("maxPerDay").value) || 3,
    intervalMinutes: parseInt($("intervalMinutes").value) || 180,
    publish: $("publish").value === "true"
  };
}

$("save").onclick = async () => { await send("save", { settings: collect() }); await refresh(); };
$("run").onclick = async () => { await send("save", { settings: collect() }); await send("runNow"); setTimeout(refresh, 800); };
$("start").onclick = async () => { await send("save", { settings: collect() }); await send("start"); setTimeout(refresh, 800); };
$("stop").onclick = async () => { await send("stop"); setTimeout(refresh, 300); };

document.addEventListener("DOMContentLoaded", refresh);
setInterval(refresh, 3000);
