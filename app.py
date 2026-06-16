import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
import os
from datetime import datetime
import pandas as pd
import random
import plotly.express as px
import plotly.graph_objects as go

from database import create_database, save_journal, get_entries

st.set_page_config(page_title="MindCare AI", page_icon="🧠", layout="wide")
st.sidebar.image(
    "logo.png",
    use_container_width=True
)
st.markdown("""
<style>

/* Background Image */
.stApp{
background-image:url("https://images.unsplash.com/photo-1519681393784-d120267933ba");
background-size:cover;
background-position:center;
background-attachment:fixed;
}

/* Transparent Main Area */
[data-testid="stAppViewContainer"]{
background:transparent;
}

/* Glassmorphism Metric Cards */
div[data-testid="stMetric"]{
background:rgba(30,41,59,0.75);
backdrop-filter:blur(12px);
border:1px solid rgba(255,255,255,0.1);
padding:20px;
border-radius:15px;
text-align:center;
}

/* Better Tabs */
button[data-baseweb="tab"]{
font-size:18px;
border-radius:10px;
}

/* General Spacing */
.main{
padding-top:1rem;
}

</style>
""", unsafe_allow_html=True)
load_dotenv()
create_database()

genai.configure(
    api_key=os.getenv("GEMINI_API_KEY")
)

if "messages" not in st.session_state:
    st.session_state.messages = []

if "analysis" not in st.session_state:
    st.session_state.analysis = {}

quotes = [
    "Every day is a fresh start.",
    "Progress is progress, no matter how small.",
    "You are stronger than you think.",
    "Small steps lead to big changes.",
    "Your mental health matters."
]

st.sidebar.title("🧠 MindCare AI")
st.sidebar.success(random.choice(quotes))

if st.sidebar.button("🗑 Clear Chat"):
    st.session_state.messages = []
    st.session_state.analysis = {}
    st.rerun()

col1, col2 = st.columns([1,5])

with col1:
    st.image(
        "logo.png",
        width=250
    )

with col2:
    st.markdown("""
    # MindCare AI

    ### Your Personal Mental Wellness Companion

    Track emotions • Journal thoughts • Gain insights
    """)
st.markdown("""
<div style="
background:rgba(30,41,59,0.75);
padding:20px;
border-radius:15px;
margin-top:15px;
margin-bottom:15px;
">

<h3>👋 Welcome to MindCare AI</h3>

<p>
Track your emotional wellbeing, journal your thoughts,
and receive AI-powered emotional support.
</p>

<ul>
<li>💬 Chat with AI</li>
<li>📓 Daily Journaling</li>
<li>📊 Wellness Analytics</li>
<li>🧠 Emotional Insights</li>
</ul>

</div>
""", unsafe_allow_html=True)
tab1, tab2, tab3, tab4 = st.tabs(
    ["AI Chat", "Journal", "Mood Dashboard", "Admin Dashboard"]
)

with tab1:

    user_input = st.chat_input("Share what's on your mind...")

    if user_input:

        history = ""

        for msg in st.session_state.messages[-6:]:
            history += f"{msg['role']}: {msg['message']}\n"

        prompt = f"""
You are MindCare AI.

Talk like a caring, emotionally intelligent friend.
Be warm, natural and conversational.
Give at least 70 words.

Return EXACTLY:

EMOTION: <emotion>

WELLNESS_SCORE: <0-100>

REASONING:
<one short sentence>

RESPONSE:
<your response>

Conversation History:
{history}

Current User Message:
{user_input}
"""

        try:
            model = genai.GenerativeModel("gemini-2.5-flash")

            with st.spinner("Analyzing emotions and generating insights....."):
                response = model.generate_content(prompt)

            raw = response.text

            emotion = "Neutral"
            score = 70
            reasoning = ""

            for line in raw.splitlines():

                if line.startswith("EMOTION:"):
                    emotion = line.replace(
                        "EMOTION:",
                        ""
                    ).strip()

                elif line.startswith("WELLNESS_SCORE:"):
                    try:
                        score = int(
                            line.replace(
                                "WELLNESS_SCORE:",
                                ""
                            ).strip()
                        )
                    except:
                        pass

            if "REASONING:" in raw and "RESPONSE:" in raw:
                reasoning = (
                    raw.split("REASONING:", 1)[1]
                    .split("RESPONSE:", 1)[0]
                    .strip()
                )

            if "RESPONSE:" in raw:
                ai_reply = raw.split(
                    "RESPONSE:",
                    1
                )[1].strip()
            else:
                ai_reply = raw

            st.session_state.analysis = {
                "emotion": emotion,
                "score": score,
                "reasoning": reasoning
            }

            st.session_state.messages.append(
                {
                    "role": "user",
                    "message": user_input
                }
            )

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "message": ai_reply
                }
            )

        except Exception as e:
            st.error(f"Gemini Error: {e}")

    if st.session_state.analysis:

        score = st.session_state.analysis["score"]

        st.success(
            f"AI Detected Emotion: {st.session_state.analysis['emotion']}"
        )

        fig = go.Figure(
            go.Indicator(
                mode="gauge+number",
                value=score,
                title={"text": "Wellness Score ❤️"},
                gauge={
                    "axis": {
                        "range": [0, 100]
                    }
                }
            )
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        st.caption(
            f"Reasoning: {st.session_state.analysis['reasoning']}"
        )

        if score >= 80:
            st.success("🌟 Thriving")
        elif score >= 60:
            st.info("🙂 Doing Well")
        elif score >= 40:
            st.warning("💛 Facing Challenges")
        else:
            st.error("❤️‍🩹 Needs Support")

        tips = [
            "Take a short walk today.",
            "Drink some water and stretch.",
            "Talk to someone you trust.",
            "Spend 10 minutes away from screens."
        ]

        st.info(
            f"💡 Daily Tip: {random.choice(tips)}"
        )

    st.markdown("### Chat History")

    for msg in st.session_state.messages:

        avatar = (
            "🧠"
            if msg["role"] == "assistant"
            else "👤"
        )

        with st.chat_message(
            msg["role"],
            avatar=avatar
        ):
            st.write(msg["message"])
with tab2:

    mood = st.selectbox("Current Mood",
                        ["Happy","Neutral","Sad","Anxious","Excited"])

    entry = st.text_area("Write your thoughts...")

    if st.button("Save Journal Entry"):
        if entry.strip():
            save_journal(
                datetime.now().strftime("%Y-%m-%d"),
                mood,
                entry
            )
            st.success("Journal Saved Successfully!")
        else:
            st.warning("Please write something.")

with tab3:

    data = get_entries()

    if len(data) > 0:

        df = pd.DataFrame(data, columns=["ID","Date","Mood","Entry"])

        mood_scores = {
            "Happy":100,
            "Excited":90,
            "Neutral":70,
            "Anxious":40,
            "Sad":20
        }

        overall = df["Mood"].map(mood_scores).mean()

        c1,c2,c3 = st.columns(3)

        c1.metric("Overall Wellness Score ❤️", f"{overall:.0f}/100")
        c2.metric("Journal Entries 📓", len(df))
        c3.metric("Active Days 🔥", df["Date"].nunique())

        mood_count = df["Mood"].value_counts().reset_index()
        mood_count.columns = ["Mood","Count"]

        st.plotly_chart(
            px.pie(mood_count, names="Mood", values="Count",
                   title="Mood Distribution"),
            use_container_width=True
        )

        df["Wellness Score"] = df["Mood"].map(mood_scores)
        df["Entry Number"] = range(1, len(df)+1)

        trend = px.line(
            df,
            x="Entry Number",
            y="Wellness Score",
            markers=True,
            title="Mental Wellness Journey"
        )

        trend.update_layout(
            yaxis=dict(range=[0,100])
        )

        st.plotly_chart(trend, use_container_width=True)

    else:
        st.info("No journal entries yet.")

with tab4:

    import sqlite3

    data = get_entries()

    if len(data) > 0:

        df = pd.DataFrame(
            data,
            columns=["ID", "Date", "Mood", "Entry"]
        )

        a, b, c = st.columns(3)

        a.metric("Total Entries", len(df))
        b.metric("Most Common Mood", df["Mood"].mode()[0])
        c.metric(
            "Conversations",
            len(st.session_state.messages) // 2
        )

        st.markdown("### 📋 Journal Entries")

        st.dataframe(
            df,
            use_container_width=True
        )

        st.markdown("---")
        st.markdown("### ⚠️ Database Controls")

        confirm = st.checkbox(
            "I understand this will permanently delete all journal entries"
        )

        if confirm:

            if st.button("🗑 Delete All Journal Entries"):

                conn = sqlite3.connect("journal.db")
                cursor = conn.cursor()

                cursor.execute("DELETE FROM journal")

                conn.commit()
                conn.close()

                st.success(
                    "All journal entries deleted successfully!"
                )

                st.rerun()

    else:

        st.info("No journal entries found.")

        confirm = st.checkbox(
            "I understand this will permanently delete all journal entries"
        )

        if confirm:

            if st.button("🗑 Delete All Journal Entries"):

                conn = sqlite3.connect("journal.db")
                cursor = conn.cursor()

                cursor.execute("DELETE FROM journal")

                conn.commit()
                conn.close()

                st.success(
                    "Database cleared successfully!"
                )

                st.rerun()
st.markdown("""
---
<center>
MindCare AI v1.0 • Built by Sai Shishir 🚀
</center>
""", unsafe_allow_html=True)
