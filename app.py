import streamlit as st

from src.orchestration.chat_service import ChatResponse, ChatService


DEFAULT_CUSTOMER_ID = "cus_001"
DEFAULT_HISTORY_TURNS = 5

AGENT_LABELS = {
    "card_services": "Card Services",
    "payments_and_disputes": "Payments & Disputes",
    "transfers_and_topups": "Transfers & Top-ups",
    "account_currency_and_access": "Accounts, Currency & Access",
    "general_agent": "General Support",
}


def initialize_session() -> None:
    if "chat_service" not in st.session_state:
        st.session_state.chat_service = ChatService(
            customer_id=DEFAULT_CUSTOMER_ID,
            max_history_turns=DEFAULT_HISTORY_TURNS,
        )
    if "history" not in st.session_state:
        st.session_state.history = []
    if "last_response" not in st.session_state:
        st.session_state.last_response = None


def clear_conversation() -> None:
    st.session_state.chat_service.clear_history()
    st.session_state.history = []
    st.session_state.last_response = None


st.set_page_config(page_title="Synthetic Bank Support", page_icon="🏦", layout="wide")
st.title("🏦 Synthetic Bank Support")
st.caption("A demonstration assistant using synthetic banking data.")

try:
    initialize_session()
except Exception as error:
    st.error(f"The support service could not start: {error}")
    st.stop()

with st.sidebar:
    st.subheader("Routing")
    last_response: ChatResponse | None = st.session_state.last_response
    if last_response is None:
        st.caption("Send a message to see routing information.")
    else:
        st.metric("Predicted route", last_response.route)
        st.metric("Model confidence", f"{last_response.confidence:.1%}")
        st.write(
            f"Handled by: **{AGENT_LABELS.get(last_response.route, last_response.route)}**"
        )

    st.divider()
    st.caption(f"Customer: `{DEFAULT_CUSTOMER_ID}`")
    st.caption(f"Memory: last {DEFAULT_HISTORY_TURNS} turns")
    if st.button("Clear conversation", use_container_width=True):
        clear_conversation()
        st.rerun()

for turn in st.session_state.history:
    with st.chat_message(turn["role"]):
        st.write(turn["content"])

if user_message := st.chat_input("How can I help?"):
    st.session_state.history.append(
        {"role": "user", "content": user_message}
    )
    with st.chat_message("user"):
        st.write(user_message)

    try:
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = st.session_state.chat_service.respond_with_metadata(
                    user_message
                )
            st.write(response.reply)
    except Exception as error:
        st.error(f"The assistant could not complete the request: {error}")
    else:
        st.session_state.history.append(
            {"role": "assistant", "content": response.reply}
        )
        st.session_state.last_response = response
        st.rerun()
