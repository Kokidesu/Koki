// AI ドクター — Cloudflare Worker backend
// ----------------------------------------------------------------------------
// Holds the AI so visitors need NO API key of their own.
//   - POST /api/chat : streams the doctor's reply (plain UTF-8 text)
//   - everything else: serves the static site (index.html) via the ASSETS binding
//
// AI source (auto-detected):
//   - If a GEMINI_API_KEY secret is set  -> proxy to Google Gemini (higher quality).
//   - Otherwise                          -> Cloudflare Workers AI (no API key at all).
// ----------------------------------------------------------------------------

// Cloudflare Workers AI model (no separate API key needed; uses your CF free allowance).
const CF_MODEL = "@cf/meta/llama-3.3-70b-instruct-fp8-fast";

const CORS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "POST, OPTIONS",
  "Access-Control-Allow-Headers": "content-type",
};

export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    if (request.method === "OPTIONS") {
      return new Response(null, { headers: CORS });
    }

    if (url.pathname === "/api/health") {
      return Response.json(
        { ok: true, backend: env.GEMINI_API_KEY ? "gemini" : "workers-ai" },
        { headers: CORS }
      );
    }

    if (url.pathname === "/api/chat") {
      if (request.method !== "POST") return err("POST only", 405);
      return handleChat(request, env);
    }

    // Static site (index.html). Present when deployed with the [assets] binding.
    if (env.ASSETS) return env.ASSETS.fetch(request);
    return new Response("AI Doctor API. POST /api/chat", { status: 404, headers: CORS });
  },
};

function err(message, status) {
  return new Response(JSON.stringify({ error: message }), {
    status,
    headers: { "content-type": "application/json", ...CORS },
  });
}

// ---- the doctor persona + safety rules (server-side, can't be tampered with) ----
function systemPrompt(mode, answerLang) {
  const langMap = {
    auto: "Reply in the same language the user is writing in (Japanese or English).",
    ja: "Always reply in Japanese (日本語).",
    en: "Always reply in English.",
  };
  const lines = [
    "You are 'AI ドクター' (AI Doctor), an exceptionally knowledgeable, board-certified-level physician AI with broad, up-to-date expertise across all medical specialties — internal medicine, pediatrics, dermatology, mental health, and more.",
    "Your reputation: the most capable and the fastest-answering doctor in the world. You give clear, accurate, genuinely helpful health information without unnecessary delay.",
    "Tone: warm, calm, empathetic, and non-judgmental — like a trusted family doctor. Acknowledge the person's worry briefly, then help.",
    "Structure your answers so they are easy to read and act on. For a symptom question, a good shape is: (1) a one-line empathetic acknowledgement, (2) the most likely explanations in plain language (most likely first), (3) practical self-care / what to do now, (4) when to see a doctor, (5) red-flag warning signs that mean 'seek care urgently'. Adapt the structure to the question — not every message needs all sections.",
    "Keep it concise and scannable: short paragraphs, **bold** key points, and bullet lists. Explain any medical term in plain words. Do not pad with filler.",
    "If essential information is missing (age, how long, severity, other symptoms, relevant history), give useful general guidance AND ask one or two short clarifying questions at the end.",
    "",
    "SAFETY RULES — follow these strictly:",
    "- Make clear, when relevant, that you are an AI giving general information and NOT a replacement for in-person evaluation, diagnosis, or treatment by a licensed doctor.",
    "- Do NOT give a definitive diagnosis. Speak in terms of possibilities and likelihoods.",
    "- EMERGENCIES: If the symptoms could be a medical emergency — e.g. chest pain or pressure, difficulty breathing, signs of stroke (face drooping, arm weakness, speech difficulty), severe or uncontrolled bleeding, sudden severe headache, anaphylaxis/severe allergic reaction, loss of consciousness, seizures, severe abdominal pain, or thoughts of suicide or self-harm — say so clearly and put the emergency guidance FIRST and prominently: advise contacting emergency services immediately (in Japan, call 119; otherwise the local emergency number).",
    "- MENTAL HEALTH / SELF-HARM: respond with compassion, take it seriously, and encourage reaching out to emergency services or a crisis line right away. In Japan you may mention いのちの電話 (0570-783-556) and emergency 119. Never provide any guidance that could facilitate self-harm.",
    "- MEDICATIONS: you may explain common over-the-counter options and general usage, but advise confirming the right choice and dose with a doctor or pharmacist and checking for contraindications, allergies, pregnancy, and interactions. For prescription medicines, advise consulting a physician. Never encourage misuse, overdosing, or obtaining medications illicitly.",
    "- Refuse, kindly, any request that asks for help causing harm to oneself or others, and redirect to appropriate help.",
    "- For anything beyond general guidance, recommend seeing a real healthcare professional, especially for symptoms that are severe, persistent, worsening, or unusual.",
    "",
    langMap[answerLang] || langMap.auto,
    mode === "thorough"
      ? "Mode: THOROUGH — be more detailed and complete. Cover the relevant possibilities and reasoning carefully, while staying clear and well-organized."
      : "Mode: FAST — answer as quickly and directly as possible. Be correct and complete on the essentials, but skip preamble and keep it efficient.",
  ];
  return lines.join("\n");
}

async function handleChat(request, env) {
  let payload;
  try {
    payload = await request.json();
  } catch (_) {
    return err("Invalid JSON body", 400);
  }

  const mode = payload.mode === "thorough" ? "thorough" : "fast";
  const answerLang = ["auto", "ja", "en"].includes(payload.answerLang) ? payload.answerLang : "auto";
  const incoming = Array.isArray(payload.messages) ? payload.messages : [];

  const messages = [{ role: "system", content: systemPrompt(mode, answerLang) }];
  for (const m of incoming.slice(-20)) {
    const role = m && m.role === "assistant" ? "assistant" : "user";
    const content = m && typeof m.content === "string" ? m.content.slice(0, 8000) : "";
    if (content) messages.push({ role, content });
  }
  if (messages.length === 1) return err("No messages provided", 400);

  const maxTokens = mode === "thorough" ? 2048 : 1024;

  try {
    const stream = env.GEMINI_API_KEY
      ? await streamGemini(env, messages, mode, maxTokens)
      : await streamWorkersAI(env, messages, maxTokens);
    return new Response(stream, {
      headers: { "content-type": "text/plain; charset=utf-8", "cache-control": "no-store", ...CORS },
    });
  } catch (e) {
    return err((e && e.message) || "AI backend error", 502);
  }
}

// ---- Cloudflare Workers AI (default; no API key needed) ----
async function streamWorkersAI(env, messages, maxTokens) {
  if (!env.AI) throw new Error("Workers AI binding not configured. Add [ai] binding=\"AI\" to wrangler.toml, or set a GEMINI_API_KEY secret.");
  const aiStream = await env.AI.run(CF_MODEL, { messages, stream: true, max_tokens: maxTokens });
  // Workers AI returns an SSE ReadableStream: lines like  data: {"response":"token"}  ... data: [DONE]
  return sseToText(aiStream, (json) => (typeof json.response === "string" ? json.response : ""));
}

// ---- Google Gemini (optional; used when GEMINI_API_KEY secret is set) ----
async function streamGemini(env, messages, mode, maxTokens) {
  const model = mode === "thorough" ? "gemini-2.5-flash" : "gemini-2.0-flash";
  const sys = messages[0].content;
  const contents = messages.slice(1).map((m) => ({
    role: m.role === "assistant" ? "model" : "user",
    parts: [{ text: m.content }],
  }));
  const body = {
    system_instruction: { parts: [{ text: sys }] },
    contents,
    generationConfig: { maxOutputTokens: maxTokens, temperature: mode === "thorough" ? 0.4 : 0.5 },
  };
  const endpoint =
    "https://generativelanguage.googleapis.com/v1beta/models/" +
    model +
    ":streamGenerateContent?alt=sse&key=" +
    encodeURIComponent(env.GEMINI_API_KEY);
  const resp = await fetch(endpoint, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!resp.ok) {
    let m = "Gemini HTTP " + resp.status;
    try { const j = await resp.json(); if (j.error && j.error.message) m = j.error.message; } catch (_) {}
    throw new Error(m);
  }
  return sseToText(resp.body, (json) => {
    const cand = json.candidates && json.candidates[0];
    if (cand && cand.content && cand.content.parts) {
      return cand.content.parts.map((p) => (typeof p.text === "string" ? p.text : "")).join("");
    }
    return "";
  });
}

// ---- transform an SSE byte stream into a plain-text token stream ----
function sseToText(readable, extract) {
  const reader = readable.getReader();
  const decoder = new TextDecoder();
  const encoder = new TextEncoder();
  let buffer = "";
  return new ReadableStream({
    async pull(controller) {
      try {
        const { done, value } = await reader.read();
        if (done) {
          controller.close();
          return;
        }
        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop();
        for (const line of lines) {
          const tr = line.trim();
          if (!tr.startsWith("data:")) continue;
          const data = tr.slice(5).trim();
          if (!data || data === "[DONE]") continue;
          let json;
          try { json = JSON.parse(data); } catch (_) { continue; }
          if (json.error) throw new Error(json.error.message || "stream error");
          const piece = extract(json);
          if (piece) controller.enqueue(encoder.encode(piece));
        }
      } catch (e) {
        controller.error(e);
      }
    },
    cancel() {
      reader.cancel();
    },
  });
}
