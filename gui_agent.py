import json
import time
from flask import Flask, request, jsonify, render_template_string
from openai import OpenAI

app = Flask(__name__)

# 🔑 OpenRouter client — replace with your actual key
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="your-api-key-here"   # ← paste your key here
)

MODEL = "meta-llama/llama-3-8b-instrusct"

SYSTEM_PROMPT = """You are an expert Islamic teacher and guide who loves teaching and explaining Islamic knowledge in depth. 
You break down complex concepts from the Quran, Sunnah, Fiqh, Aqeedah, Seerah, and Akhlaq into simple, step-by-step explanations. 
You always explain the 'why' behind rulings, beliefs, and practices, not just the 'how', connecting them to wisdom, purpose, and the bigger picture of submission to Allah. 
You use clear examples, analogies, stories from the Prophets and Companions, and real-life situations to make Islamic teachings relatable and alive. 
You adapt to the student's level — building understanding gradually from basics to advanced, while remaining true to authentic sources. 
You encourage curiosity, reflection, and critical thinking within the framework of Shariah and sound Islamic scholarship. 
When explaining Quranic verses or Hadiths, you go word by word or section by section, explaining the meaning, context, and practical application. 
You highlight common mistakes, misconceptions, and cultural confusions that people often have. 
You sometimes ask gentle questions to encourage the student to reflect and internalize the knowledge.
You only will tell Quranic verses as they are — no changes — and with references.
Your tone is supportive, patient, compassionate, and clear. You focus on deep understanding, spiritual growth, and closeness to Allah."""

# In-memory session store (keyed by session_id sent from browser)
sessions = {}


@app.route("/")
def index():
    return render_template_string(HTML_PAGE)


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_input = data.get("message", "").strip()
    session_id = data.get("session_id", "default")

    if not user_input:
        return jsonify({"error": "Empty message"}), 400

    # Build or retrieve history
    if session_id not in sessions:
        sessions[session_id] = [{"role": "system", "content": SYSTEM_PROMPT}]

    history = sessions[session_id]
    history.append({"role": "user", "content": user_input})

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=history
        )
        answer = response.choices[0].message.content
        history.append({"role": "assistant", "content": answer})
        return jsonify({"reply": answer})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/reset", methods=["POST"])
def reset():
    data = request.get_json()
    session_id = data.get("session_id", "default")
    sessions.pop(session_id, None)
    return jsonify({"status": "ok"})


# ─────────────────────────────────────────────
#  The entire frontend, embedded as a string
# ─────────────────────────────────────────────
HTML_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>Quranic Guidance AI</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Amiri:ital,wght@0,400;0,700;1,400&family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet">
<style>
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

  :root {
    --bg:        #0d1117;
    --surface:   #161b22;
    --border:    #21262d;
    --gold:      #c9a84c;
    --gold-dim:  #8a6f2e;
    --text:      #e6edf3;
    --muted:     #7d8590;
    --user-bg:   #1c2433;
    --ai-bg:     #131a20;
    --radius:    14px;
    --font-body: 'DM Sans', sans-serif;
    --font-ar:   'Amiri', serif;
  }

  body {
    font-family: var(--font-body);
    background: var(--bg);
    color: var(--text);
    height: 100dvh;
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }

  /* ── top bar ── */
  header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 14px 24px;
    border-bottom: 1px solid var(--border);
    background: var(--surface);
    flex-shrink: 0;
    gap: 12px;
  }

  .brand {
    display: flex;
    align-items: center;
    gap: 12px;
  }

  .logo-ring {
    width: 38px; height: 38px;
    border-radius: 50%;
    border: 2px solid var(--gold);
    display: grid;
    place-items: center;
    font-size: 18px;
    color: var(--gold);
    flex-shrink: 0;
  }

  .brand-text h1 {
    font-family: var(--font-ar);
    font-size: 1.15rem;
    color: var(--gold);
    line-height: 1.1;
    letter-spacing: 0.01em;
  }
  .brand-text p {
    font-size: 0.7rem;
    color: var(--muted);
    font-weight: 300;
    letter-spacing: 0.04em;
    text-transform: uppercase;
  }

  #reset-btn {
    background: none;
    border: 1px solid var(--border);
    color: var(--muted);
    border-radius: 8px;
    padding: 6px 14px;
    font-size: 0.75rem;
    cursor: pointer;
    font-family: var(--font-body);
    transition: border-color 0.2s, color 0.2s;
    white-space: nowrap;
  }
  #reset-btn:hover { border-color: var(--gold-dim); color: var(--gold); }

  /* ── messages ── */
  #chat-box {
    flex: 1;
    overflow-y: auto;
    padding: 28px 20px;
    display: flex;
    flex-direction: column;
    gap: 20px;
    scroll-behavior: smooth;
  }

  #chat-box::-webkit-scrollbar { width: 5px; }
  #chat-box::-webkit-scrollbar-track { background: transparent; }
  #chat-box::-webkit-scrollbar-thumb { background: var(--border); border-radius: 4px; }

  .msg {
    display: flex;
    gap: 12px;
    max-width: 800px;
    animation: fadeUp 0.3s ease both;
  }

  @keyframes fadeUp {
    from { opacity: 0; transform: translateY(10px); }
    to   { opacity: 1; transform: translateY(0); }
  }

  .msg.user { align-self: flex-end; flex-direction: row-reverse; }
  .msg.ai   { align-self: flex-start; }

  .avatar {
    width: 32px; height: 32px;
    border-radius: 50%;
    display: grid;
    place-items: center;
    font-size: 14px;
    flex-shrink: 0;
    margin-top: 2px;
  }
  .msg.user .avatar { background: var(--gold-dim); color: #fff; }
  .msg.ai   .avatar { background: var(--border); color: var(--gold); border: 1px solid var(--gold-dim); }

  .bubble {
    padding: 12px 16px;
    border-radius: var(--radius);
    font-size: 0.9rem;
    line-height: 1.7;
    max-width: calc(100% - 48px);
    white-space: pre-wrap;
    word-break: break-word;
  }
  .msg.user .bubble {
    background: var(--user-bg);
    border: 1px solid #2a3548;
    border-bottom-right-radius: 4px;
  }
  .msg.ai .bubble {
    background: var(--ai-bg);
    border: 1px solid var(--border);
    border-bottom-left-radius: 4px;
  }

  /* typing dots */
  .typing-dots span {
    display: inline-block;
    width: 7px; height: 7px;
    border-radius: 50%;
    background: var(--muted);
    animation: dot 1.2s infinite;
    margin: 0 2px;
  }
  .typing-dots span:nth-child(2) { animation-delay: 0.2s; }
  .typing-dots span:nth-child(3) { animation-delay: 0.4s; }
  @keyframes dot {
    0%,80%,100% { transform: scale(0.6); opacity: 0.4; }
    40%         { transform: scale(1);   opacity: 1; }
  }

  /* ── welcome ── */
  #welcome {
    margin: auto;
    text-align: center;
    max-width: 380px;
    padding: 20px;
  }
  #welcome .big-icon { font-size: 3rem; margin-bottom: 16px; }
  #welcome h2 { font-family: var(--font-ar); font-size: 1.5rem; color: var(--gold); margin-bottom: 8px; }
  #welcome p  { color: var(--muted); font-size: 0.85rem; line-height: 1.6; }

  .suggestions {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    justify-content: center;
    margin-top: 20px;
  }
  .sug-btn {
    background: var(--surface);
    border: 1px solid var(--border);
    color: var(--text);
    border-radius: 20px;
    padding: 7px 14px;
    font-size: 0.78rem;
    cursor: pointer;
    font-family: var(--font-body);
    transition: border-color 0.2s, color 0.2s;
  }
  .sug-btn:hover { border-color: var(--gold-dim); color: var(--gold); }

  /* ── input bar ── */
  footer {
    padding: 14px 20px 18px;
    border-top: 1px solid var(--border);
    background: var(--surface);
    flex-shrink: 0;
  }

  .input-row {
    display: flex;
    gap: 10px;
    align-items: flex-end;
    max-width: 800px;
    margin: 0 auto;
  }

  #user-input {
    flex: 1;
    background: var(--bg);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    color: var(--text);
    font-family: var(--font-body);
    font-size: 0.9rem;
    padding: 11px 16px;
    resize: none;
    line-height: 1.5;
    max-height: 140px;
    outline: none;
    transition: border-color 0.2s;
    overflow-y: auto;
  }
  #user-input:focus { border-color: var(--gold-dim); }
  #user-input::placeholder { color: var(--muted); }

  #send-btn {
    background: var(--gold);
    border: none;
    border-radius: 10px;
    width: 42px; height: 42px;
    display: grid;
    place-items: center;
    cursor: pointer;
    transition: background 0.2s, transform 0.1s;
    flex-shrink: 0;
    color: #0d1117;
  }
  #send-btn:hover   { background: #e0bb6a; }
  #send-btn:active  { transform: scale(0.94); }
  #send-btn:disabled { background: var(--border); color: var(--muted); cursor: not-allowed; }

  #send-btn svg { width: 18px; height: 18px; }

  .hint {
    text-align: center;
    color: var(--muted);
    font-size: 0.68rem;
    margin-top: 8px;
    letter-spacing: 0.03em;
  }
</style>
</head>
<body>

<header>
  <div class="brand">
    <div class="logo-ring">&#9789;</div>
    <div class="brand-text">
      <h1>Quranic Guidance AI</h1>
      <p>Powered by Islamic Knowledge</p>
    </div>
  </div>
  <button id="reset-btn" onclick="resetChat()">&#8634; New Chat</button>
</header>

<div id="chat-box">
  <div id="welcome">
    <div class="big-icon">&#128214;</div>
    <h2>&#1575;&#1604;&#1587;&#1604;&#1575;&#1605; &#1593;&#1604;&#1610;&#1603;&#1605;</h2>
    <p>Ask anything about the Quran, Sunnah, Fiqh, Aqeedah, Seerah, or daily Islamic guidance. I'm here to help you learn and grow.</p>
    <div class="suggestions">
      <button class="sug-btn" onclick="suggest(this)">What is Tawakkul?</button>
      <button class="sug-btn" onclick="suggest(this)">Explain Surah Al-Fatiha</button>
      <button class="sug-btn" onclick="suggest(this)">How to increase Iman?</button>
      <button class="sug-btn" onclick="suggest(this)">What are the pillars of Islam?</button>
      <button class="sug-btn" onclick="suggest(this)">Stories of the Prophets</button>
    </div>
  </div>
</div>

<footer>
  <div class="input-row">
    <textarea id="user-input" rows="1" placeholder="Ask your question..." onkeydown="handleKey(event)" oninput="autoResize(this)"></textarea>
    <button id="send-btn" onclick="sendMessage()" title="Send">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
        <line x1="22" y1="2" x2="11" y2="13"></line>
        <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
      </svg>
    </button>
  </div>
  <p class="hint">Press Enter to send &middot; Shift+Enter for new line</p>
</footer>

<script>
  const SESSION_ID = Math.random().toString(36).slice(2);
  let isLoading = false;

  function autoResize(el) {
    el.style.height = 'auto';
    el.style.height = Math.min(el.scrollHeight, 140) + 'px';
  }

  function handleKey(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  }

  function suggest(btn) {
    document.getElementById('user-input').value = btn.textContent;
    sendMessage();
  }

  function removeWelcome() {
    const w = document.getElementById('welcome');
    if (w) w.remove();
  }

  function scrollBottom() {
    const box = document.getElementById('chat-box');
    box.scrollTop = box.scrollHeight;
  }

  function addBubble(role, text) {
    const box = document.getElementById('chat-box');
    const div = document.createElement('div');
    div.className = 'msg ' + role;

    const avatar = document.createElement('div');
    avatar.className = 'avatar';
    avatar.textContent = role === 'user' ? String.fromCodePoint(0x1F464) : String.fromCodePoint(0x2619);

    const bubble = document.createElement('div');
    bubble.className = 'bubble';
    bubble.textContent = text;

    div.appendChild(avatar);
    div.appendChild(bubble);
    box.appendChild(div);
    scrollBottom();
    return bubble;
  }

  function addTyping() {
    const box = document.getElementById('chat-box');
    const div = document.createElement('div');
    div.className = 'msg ai';
    div.id = 'typing-indicator';

    const avatar = document.createElement('div');
    avatar.className = 'avatar';
    avatar.textContent = String.fromCodePoint(0x2619);

    const bubble = document.createElement('div');
    bubble.className = 'bubble typing-dots';
    bubble.innerHTML = '<span></span><span></span><span></span>';

    div.appendChild(avatar);
    div.appendChild(bubble);
    box.appendChild(div);
    scrollBottom();
  }

  function removeTyping() {
    const t = document.getElementById('typing-indicator');
    if (t) t.remove();
  }

  async function sendMessage() {
    if (isLoading) return;
    const input = document.getElementById('user-input');
    const text = input.value.trim();
    if (!text) return;

    removeWelcome();
    addBubble('user', text);
    input.value = '';
    input.style.height = 'auto';

    isLoading = true;
    document.getElementById('send-btn').disabled = true;
    addTyping();

    try {
      const res = await fetch('/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text, session_id: SESSION_ID })
      });
      const data = await res.json();
      removeTyping();

      if (data.error) {
        addBubble('ai', 'Error: ' + data.error);
      } else {
        typewriterBubble(data.reply);
      }
    } catch (err) {
      removeTyping();
      addBubble('ai', 'Could not reach the server. Is the Flask app running?');
    }

    isLoading = false;
    document.getElementById('send-btn').disabled = false;
    input.focus();
  }

  function typewriterBubble(text) {
    const box = document.getElementById('chat-box');
    const div = document.createElement('div');
    div.className = 'msg ai';

    const avatar = document.createElement('div');
    avatar.className = 'avatar';
    avatar.textContent = String.fromCodePoint(0x2619);

    const bubble = document.createElement('div');
    bubble.className = 'bubble';

    div.appendChild(avatar);
    div.appendChild(bubble);
    box.appendChild(div);

    let i = 0;
    const speed = 12;
    function type() {
      if (i < text.length) {
        bubble.textContent += text[i++];
        scrollBottom();
        setTimeout(type, speed);
      }
    }
    type();
  }

  async function resetChat() {
    await fetch('/reset', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: SESSION_ID })
    });
    const box = document.getElementById('chat-box');
    box.innerHTML = `
      <div id="welcome">
        <div class="big-icon">&#128214;</div>
        <h2 style="font-family:'Amiri',serif;font-size:1.5rem;color:#c9a84c;margin-bottom:8px;">&#1575;&#1604;&#1587;&#1604;&#1575;&#1605; &#1593;&#1604;&#1610;&#1603;&#1605;</h2>
        <p style="color:#7d8590;font-size:.85rem;line-height:1.6;">Ask anything about the Quran, Sunnah, Fiqh, Aqeedah, Seerah, or daily Islamic guidance.</p>
        <div class="suggestions" style="display:flex;flex-wrap:wrap;gap:8px;justify-content:center;margin-top:20px;">
          <button class="sug-btn" onclick="suggest(this)">What is Tawakkul?</button>
          <button class="sug-btn" onclick="suggest(this)">Explain Surah Al-Fatiha</button>
          <button class="sug-btn" onclick="suggest(this)">How to increase Iman?</button>
          <button class="sug-btn" onclick="suggest(this)">What are the pillars of Islam?</button>
          <button class="sug-btn" onclick="suggest(this)">Stories of the Prophets</button>
        </div>
      </div>`;
  }
</script>
</body>
</html>"""


if __name__ == "__main__":
    print("✦ Quranic Guidance AI — GUI mode")
    print("  Open http://127.0.0.1:5000 in your browser")
    print("  Press Ctrl+C to stop\n")
    app.run(debug=False, port=5000)