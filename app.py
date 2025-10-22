# app.py
import streamlit as st
from RAG import load_dataset, build_index, get_fix
# ── Page ────────────────────────────────────────────────────────────────────
st.set_page_config(page_title="ITSM Assistant", page_icon="🛠️", layout="wide")

# ── Global styles: White & Blue only (fixed input parity + chat bar) ───────
st.markdown("""
<style>
:root{
  --blue-950:#082865;
  --blue-900:#0A3D91;
  --blue-800:#1549B3;
  --blue-700:#1D59CC;
  --blue-600:#2768E3;
  --blue-300:#9FC0FF;
  --blue-150:#DDEAFF;
  --blue-100:#EAF2FF;
  --blue-075:#F2F7FF;
  --white:#FFFFFF;

  /* unified input tokens */
  --inp-bg: var(--white);
  --inp-fg: var(--blue-800);
  --inp-br: 16px;
  --inp-bd: 1px solid var(--blue-150);
  --inp-shadow: 0 1px 6px rgba(8,40,101,.04);
  --inp-height: 64px;
}

/* Force light look everywhere (even if system is dark) */
html, body, [data-testid="stAppViewContainer"], .stApp {
  background: var(--white) !important;
  color: var(--blue-800) !important;
  font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, "Helvetica Neue", Arial, "Noto Sans", "Liberation Sans", sans-serif;
  color-scheme: light;
}

/* Clean header */
header[data-testid="stHeader"]{
  background: var(--white) !important;
  border-bottom: 1px solid var(--blue-150) !important;
  color: var(--blue-800) !important;
}

.block-container{ padding-top:.75rem; padding-bottom:1.5rem; }

/* ── Sidebar ─────────────────────────────────────────────────────────────── */
section[data-testid="stSidebar"]{
  background: var(--blue-075) !important;
  border-right: 2px solid var(--blue-150) !important;
  box-shadow: none !important;
}
.sidebar-section{ padding:.5rem .6rem 1rem .6rem; }
.sidebar-title{
  font-weight:800; margin:.25rem 0 .5rem 0; color: var(--blue-900);
}

/* ── SIDEBAR INPUT: single, perfectly fitted blue border ──────────────────── */
section[data-testid="stSidebar"] .stTextInput > div > div{
  background: var(--white) !important;
  border: 1px solid var(--blue-150) !important;   /* only border we keep */
  border-radius: 16px !important;                 /* same radius everywhere */
  box-shadow: 0 1px 6px rgba(8,40,101,.04) !important;
  box-sizing: border-box !important;
  overflow: hidden !important;                    /* clip inner focus rings */
  padding: 0 !important;                          /* no extra inset padding */
  margin-top: -4px !important;
}

/* kill borders/shadows on BaseWeb wrappers so they don't add a second outline */
section[data-testid="stSidebar"] [data-baseweb="input"],
section[data-testid="stSidebar"] [data-baseweb="input"] > div{
  border: none !important;
  box-shadow: none !important;
  background: transparent !important;
  border-radius: 16px !important;                 /* match radius exactly */
  box-sizing: border-box !important;
}

/* actual input field */
section[data-testid="stSidebar"] .stTextInput input{
  background: transparent !important;
  color: var(--inp-fg) !important;
  border: none !important;
  outline: none !important;
  height: 56px !important;                        /* unified height */
  line-height: 56px !important;                   /* vertically center text */
  padding: 0 14px !important;                     /* horizontal padding only */
  border-radius: 16px !important;
  box-shadow: none !important;
  box-sizing: border-box !important;
}

/* placeholder */
section[data-testid="stSidebar"] .stTextInput input::placeholder{
  color: rgba(21,73,179,.50) !important;
  font-style: italic !important;
}

/* focus state: no extra outline that would misalign the border */
section[data-testid="stSidebar"] .stTextInput input:focus{
  box-shadow: none !important;   /* no inner glow */
  outline: none !important;
}

/* Buttons */
button[kind="primary"]{
  background: var(--blue-600) !important; color: var(--white) !important;
  border: 1px solid var(--blue-700) !important; border-radius: 12px !important;
}
button[kind="secondary"]{
  background: var(--white) !important; color: var(--blue-800) !important;
  border: 1px solid var(--blue-600) !important; border-radius: 12px !important;
}

hr{ border-color: var(--blue-150) !important; }

/* ── Title row ───────────────────────────────────────────────────────────── */
.header{
  max-width: 980px; margin: 0 auto 8px auto;
  display:flex; align-items:center; gap:.6rem;
  padding:.6rem .25rem .9rem .25rem;
}
.header .title{ font-size:1.15rem; font-weight:800; letter-spacing:.2px; color:var(--blue-950); }
.badge{
  display:inline-flex; align-items:center; justify-content:center;
  min-width:28px; height:28px; border-radius:999px;
  background: var(--blue-600); color: var(--white); font-size:.9rem; font-weight:700;
}

/* ── Chat area ───────────────────────────────────────────────────────────── */
.chat-wrap{ max-width: 920px; margin: 0 auto; padding: .25rem 0 6rem 0; }
.chat-row{ display:flex; margin: .8rem 0 1.2rem 0; }
.chat-row.assistant{ justify-content:flex-start; }
.chat-row.user{ justify-content:flex-end; }

/* Bubbles */
.bubble{
  border-radius: 18px; padding: 1.05rem 1.2rem; line-height: 1.58;
  max-width: 760px;
  border: 1px solid var(--blue-150);
  box-shadow: 0 2px 8px rgba(8,40,101,0.06);
}
.bubble.assistant{ background: var(--blue-100); color: var(--blue-950); }
.bubble.user{ background: var(--blue-600); border-color: var(--blue-700); color: var(--white); }
.bubble a{ color: var(--blue-600); text-decoration:none; }
.bubble a:hover{ text-decoration:underline; }
.bubble strong{ color: var(--blue-900); }

/* ── CHAT BAR & its parents: clean white + divider line ───────────────────── */
div[data-testid="stChatInput"],
div[data-testid="stChatInput"] *{
  background: transparent !important;
  box-shadow: none !important;
}

/* outer container: add top divider line */
div[data-testid="stBottomBlockContainer"],
div[data-testid="stChatInput"]{
  background: var(--white) !important;
  border-top: 1px solid var(--blue-150) !important;  /* <── divider line */
  padding-top: .6rem !important;
}

/* center the chat bar */
div[data-testid="stChatInput"] > div{
  max-width: 920px;
  margin: 0 auto;
  padding: .4rem 0 1rem 0;
}

/* remove BaseWeb underline */
[data-testid="stChatInput"] [data-baseweb="textarea"],
[data-testid="stChatInput"] [data-baseweb="textarea"] > div {
  border: none !important;
  box-shadow: none !important;
}

/* main chat textarea */
[data-testid="stChatInput"] textarea{
  background: var(--inp-bg) !important;
  color: var(--inp-fg) !important;
  border-radius: var(--inp-br) !important;
  border: 1px solid var(--blue-150) !important;
  box-shadow: var(--inp-shadow) !important;
  height: 70px !important;
  padding: 1rem 1.1rem !important;
  margin-top: 0 !important;
  line-height: 1.6rem !important;
  resize: none !important;
}

/* focus state — remove the glow completely */
[data-testid="stChatInput"] textarea:focus{
  border: 1px solid var(--blue-150) !important;
  box-shadow: none !important;  /* <── no glow */
  outline: none !important;
}

/* placeholder style */
[data-testid="stChatInput"] textarea::placeholder {
  color: rgba(21,73,179,.45) !important;
  font-style: italic !important;
  font-size: 1.05rem !important;
}

/* ── SEND / SUBMIT BUTTON STYLE ─────────────────────────────── */
[data-testid="stChatInput"] button{
  background: var(--blue-600) !important;       /* solid blue background */
  color: var(--white) !important;               /* white arrow */
  border: 1px solid var(--blue-700) !important; /* subtle border */
  border-radius: 16px !important;               /* rounded to match input box */
  width: 48px !important;                       /* consistent button size */
  height: 48px !important;
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  margin-left: 6px !important;                  /* small gap from textarea */
  margin-top: -6px !important;                  /* lift button upward */
  position: relative !important;
  top: -2px !important;                         /* fine-tune vertical centering */
  box-shadow: 0 2px 6px rgba(8,40,101,0.08) !important;
  transition: all 0.15s ease-in-out !important;
  cursor: pointer !important;
}

/* Hover + active states for better feedback */
[data-testid="stChatInput"] button:hover{
  background: var(--blue-700) !important;
  box-shadow: 0 3px 8px rgba(8,40,101,0.12) !important;
}

[data-testid="stChatInput"] button:active{
  background: var(--blue-800) !important;
  transform: scale(0.97) !important;
}



/* kill green/colored alert backgrounds */
div[role="alert"]{
  background: #eaf3ff !important;
  border: 1px solid var(--blue-150) !important;
  color: var(--blue-900) !important;
}

/* remove stray dark footers/toolbars */
footer, .stFooter,
[data-testid="stStatusWidget"],
[data-testid="stToolbar"],
[data-testid="stDecoration"]{
  background: var(--white) !important; box-shadow: none !important;
}

/* keep main area white next to sidebar */
main[role="main"]{ background: var(--white) !important; }
</style>
""", unsafe_allow_html=True)

# ── Load dataset + FAISS index (cached) ─────────────────────────────────────
if "df" not in st.session_state or "index" not in st.session_state:
    with st.spinner("Loading knowledge base…"):
        df = load_dataset()
        index, dim = build_index(df)
        st.session_state.df = df
        st.session_state.index = index
        st.session_state.dim = dim
    # ⛔️ replace st.success (green) with a blue status banner
    st.markdown(
        '<div role="alert" style="margin:8px 0;padding:10px 12px;border-radius:12px">'
        '✅ <strong>Ready!</strong>'
        '</div>',
        unsafe_allow_html=True
    )
else:
    df = st.session_state.df
    index = st.session_state.index
    dim = st.session_state.dim

# ── Chat state ───────────────────────────────────────────────────────────────
if "chats" not in st.session_state:
    st.session_state.chats = {"Chat 1": []}
if "active" not in st.session_state:
    st.session_state.active = "Chat 1"

# ── Sidebar (no rename feature) ─────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-title">💬 Chats</div>', unsafe_allow_html=True)
    new_name = st.text_input("➕ New chat name", placeholder="e.g., VPN issue")
    if st.button("Add Chat", use_container_width=True):
        if new_name and new_name not in st.session_state.chats:
            st.session_state.chats[new_name] = []
            st.session_state.active = new_name

    st.divider()

    for name in list(st.session_state.chats.keys()):
        if st.button(name, key=f"sel_{name}", use_container_width=True,
                     type=("primary" if name == st.session_state.active else "secondary")):
            st.session_state.active = name

    st.markdown("---")
    st.caption(f"Index dimension: {st.session_state.dim}")
    st.markdown('</div>', unsafe_allow_html=True)

# ── Chat area ────────────────────────────────────────────────────────────────
st.markdown('<div class="chat-wrap">', unsafe_allow_html=True)
messages = st.session_state.chats[st.session_state.active]

# Render history
for m in messages:
    if m["role"] == "user":
        st.markdown(
            f"<div class='chat-row user'><div class='bubble user'>🧑‍💻 {m['content']}</div></div>",
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f"<div class='chat-row assistant'><div class='bubble assistant'>{m['fix']}</div></div>",
            unsafe_allow_html=True
        )

# Chat input
text = st.chat_input("Write your issue here")
# On submit
if text:
    messages.append({"role": "user", "content": text})
    st.markdown(
        f"<div class='chat-row user'><div class='bubble user'>🧑‍💻 {text}</div></div>",
        unsafe_allow_html=True
    )

    with st.spinner("Wait for me to answer…"):
        result = get_fix(text, df, index)

    if result["matched"]:
        combined_md = (
            f"💡 <strong>Summary:</strong> {result['matched']}<br><br>"
            f"🛠️ <strong>How to Fix:</strong><br>{result['fix']}"
        )
        st.markdown(
            f"<div class='chat-row assistant'><div class='bubble assistant'>{combined_md}</div></div>",
            unsafe_allow_html=True
        )
        messages.append({
            "role": "assistant",
            "title": result["title"],
            "fix": combined_md
        })
    else:
        no_match_md = f"{result['fix']}"
        st.markdown(
            f"<div class='chat-row assistant'><div class='bubble assistant'>{no_match_md}</div></div>",
            unsafe_allow_html=True
        )
        messages.append({"role": "assistant", "title": "No match", "fix": no_match_md})

    st.session_state.chats[st.session_state.active] = messages
