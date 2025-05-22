import streamlit as st
import requests
import re
from langchain_core.messages import ChatMessage

st.title("Ophthalmology Chatbot: Ophtimus")

API_URL = "https://3430-117-16-152-30.ngrok-free.app/chat"

if "Chat_History" not in st.session_state:
    st.session_state['Chat_History'] = []

for key in ["generated_answers", "selected_answer", "current_question", "show_answers", "selected_idx"]:
    if key not in st.session_state:
        st.session_state[key] = [] if "answers" in key else None

with st.sidebar:
    st.markdown("## 설정")
    clear_button = st.button("remove chat history")

    selected_task = st.selectbox("Select model", ("Ophtimus Diagnosis", "Ophtimus Q&A"))
    selected_version = st.radio("Select version", ("Basic Chat", "Dual Answer"))

    if clear_button:
        for key in st.session_state:
            st.session_state[key] = [] if isinstance(st.session_state[key], list) else None
        st.rerun()

def add_message(role, content):
    st.session_state.Chat_History.append(ChatMessage(role=role, content=content))

def print_chat_history():
    for chat in st.session_state.Chat_History:
        st.chat_message(chat.role).write(chat.content)

def clean_assistant(raw_text: str) -> str:
    pattern = re.compile(r"<\|start_header_id\|>assistant<\|end_header_id\|>\s*(.*?)\s*(?:<\|eot_id\|>|$)", re.DOTALL)
    m = pattern.search(raw_text)
    return m.group(1).strip() if m else raw_text.strip()

print_chat_history()
user_input = st.chat_input("Input your question")

if user_input:
    st.chat_message("user").write(user_input)
    st.session_state.current_question = user_input

    if selected_version == "Basic Chat":
        res = requests.post(API_URL, json={
            "instruction": user_input,
            "task": selected_task,
            "n": 1
        })
        ai_response = clean_assistant(res.json()["response"])

        with st.chat_message("assistant"):
            st.markdown(ai_response)

        add_message("user", user_input)
        add_message("assistant", ai_response)

    elif selected_version == "Dual Answer":
        with st.spinner("답변 생성 중..."):
            res = requests.post(API_URL, json={
                "instruction": user_input,
                "task": selected_task,
                "n": 2
            })
            st.session_state.generated_answers = res.json()["response"]
            st.session_state.show_answers = True

if st.session_state.show_answers and st.session_state.generated_answers:
    col1, col2 = st.columns(2)
    for idx, col in enumerate((col1, col2)):
        with col:
            st.subheader(f"답변 {idx + 1}")
            st.markdown(st.session_state.generated_answers[idx])

    selected_idx = st.radio(
        "더 도움이 된 답변을 선택해주세요:",
        options=[0, 1],
        format_func=lambda i: f"답변 {i + 1}",
        horizontal=True,
        key="answer_selection",
    )
    st.session_state.selected_idx = selected_idx

    if st.button("이 답변 선택", key="select_answer"):
        chosen = st.session_state.generated_answers[selected_idx]
        st.session_state.selected_answer = chosen
        add_message("user", st.session_state.current_question)
        add_message("assistant", f"**선택된 답변**\n\n{chosen}")
        st.session_state.show_answers = False
        st.session_state.generated_answers = []
        st.session_state.selected_idx = None
        st.success("선택이 저장되었습니다!")
        st.rerun()
