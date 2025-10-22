# app.py
import streamlit as st
from RAG import load_dataset, build_index, get_fix

# ── Page + styles ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="ITSM Assistant", page_icon="🛠️", layout="wide")

st.markdown("""
<style>
/* Layout */
.block-container {padding-top: .5rem;}
.chat-wrap {max-width: 1000px; margin: 0 auto; padding-top: .5rem;}
/* Hide Streamlit dev toolbar */
[data-testid="stToolbar"] { display:none !important; }

/* Bubbles */
.user-bubble {
  background:#e74c3c; color:#fff; padding:.75rem 1rem; border-radius:12px;
  display:inline-block; margin:.25rem 0 .75rem 0;
}
.assistant-bubble {
  background:#f5c542; color:#111; padding:.9rem 1rem; border-radius:12px;
  display:block; margin:.25rem 0 1rem 0;
}

/* Sidebar buttons + inputs */
.sidebar-btn {border-radius:8px;}
.sidebar-rename {width:100%;}
</style>
""", unsafe_allow_html=True)

# ── Load dataset + FAISS index once (then cache in session) ─────────────────────
if "df" not in st.session_state or "index" not in st.session_state:
    st.write("🔄 Loading knowledge base…")
    df = load_dataset()
    index, dim = build_index(df)
    st.session_state.df = df
    st.session_state.index = index
    st.session_state.dim = dim
    st.success("✅ Ready!")
else:
    df = st.session_state.df
    index = st.session_state.index
    dim = st.session_state.dim

# ── Chat state ───────────────────────────────────────────────────────────────────
if "chats" not in st.session_state:
    st.session_state.chats = {"Chat 1": []}   # {chat_name: [ {role, content} / {role, title, fix} ]}
if "active" not in st.session_state:
    st.session_state.active = "Chat 1"
if "rename_name" not in st.session_state:
    st.session_state.rename_name = ""

# ── Sidebar (ChatGPT-like, with naming/renaming) ────────────────────────────────
with st.sidebar:
    st.markdown("### 💬 Chats")

    new_name = st.text_input("➕ New chat name", placeholder="e.g., Incident issue")
    if st.button("Add Chat", use_container_width=True):
        if new_name and new_name not in st.session_state.chats:
            st.session_state.chats[new_name] = []
            st.session_state.active = new_name
            st.session_state.rename_name = ""

    st.divider()

    for name in list(st.session_state.chats.keys()):
        cols = st.columns([0.62, 0.19, 0.19])
        with cols[0]:
            if st.button(name, key=f"sel_{name}", use_container_width=True,
                         type=("primary" if name == st.session_state.active else "secondary")):
                st.session_state.active = name
        with cols[1]:
            if st.button("✏️", key=f"edit_{name}", use_container_width=True):
                st.session_state.rename_target = name
                st.session_state.rename_name = name
        with cols[2]:
            if st.button("🗑️", key=f"del_{name}", use_container_width=True):
                if len(st.session_state.chats) > 1:
                    del st.session_state.chats[name]
                    st.session_state.active = list(st.session_state.chats.keys())[0]

    if "rename_target" in st.session_state:
        st.text_input("Rename chat", key="rename_name")
        rc1, rc2 = st.columns(2)
        with rc1:
            if st.button("Save", use_container_width=True):
                old = st.session_state.rename_target
                new = st.session_state.rename_name.strip()
                if new and new not in st.session_state.chats:
                    st.session_state.chats[new] = st.session_state.chats.pop(old)
                    st.session_state.active = new
                del st.session_state.rename_target
        with rc2:
            if st.button("Cancel", use_container_width=True):
                del st.session_state.rename_target
                st.session_state.rename_name = ""

    st.markdown("---")
    st.caption(f"Index dimension: {st.session_state.dim}")

# ── Chat area ───────────────────────────────────────────────────────────────────
st.markdown('<div class="chat-wrap">', unsafe_allow_html=True)
st.title("IT Incident Assistant")

messages = st.session_state.chats[st.session_state.active]

# Render history
for m in messages:
    if m["role"] == "user":
        st.markdown(f"<div class='user-bubble'>🧑‍💻 {m['content']}</div>", unsafe_allow_html=True)
    else:
        # m["fix"] already contains the formatted block (title/match/score/fix)
        st.markdown(f"<div class='assistant-bubble'>{m['fix']}</div>", unsafe_allow_html=True)

# Chat input
text = st.chat_input("Describe your IT incident…")

# On submit
if text:
    # show the user's question as a red bubble immediately
    messages.append({"role": "user", "content": text})
    st.markdown(f"<div class='user-bubble'>🧑‍💻 {text}</div>", unsafe_allow_html=True)

    # assistant response with spinner
    with st.chat_message("assistant"):
        with st.spinner("🔍 Finding best solution…"):
            result = get_fix(text, df, index)

        if result["matched"]:
            detailed_msg = (
                f"🧾 Generated Title: {result['title']}  \n\n"
                f"💡 Matched Short Description: {result['matched']}  \n\n"
                f"📈 Similarity Score: {result['score']:.3f}  \n\n"
                f"🛠️ How to Fix:\n{result['fix']}"
            )
            st.markdown(f"<div class='assistant-bubble'>{detailed_msg}</div>", unsafe_allow_html=True)
            messages.append({"role": "assistant", "title": result["title"], "fix": detailed_msg})
        else:
            detailed_msg = (
                f"🧾 Generated Title: {result['title']}  \n\n"
                f"📈 Similarity Score: {result['score']:.3f}  \n\n"
                f"{result['fix']}"
            )
            st.markdown(f"<div class='assistant-bubble'>{detailed_msg}</div>", unsafe_allow_html=True)
            messages.append({"role": "assistant", "title": "No match", "fix": detailed_msg})

    st.session_state.chats[st.session_state.active] = messages
