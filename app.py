import streamlit as st

st.set_page_config(
    page_title="诡秘晚上一起打三角洲",
    layout="centered",
    page_icon="🌙"
)

# Custom CSS for styling
st.markdown("""
    <style>
    body {
        background-color: #0d0d0d;
        color: #f2f2f2;
        font-family: "Noto Sans SC", "Microsoft YaHei", sans-serif;
        text-align: center;
    }
    .main-title {
        font-size: 64px;
        font-weight: 700;
        letter-spacing: 6px;
        color: #e3e3e3;
        text-shadow: 0 0 20px #9f00ff, 0 0 40px #3300ff;
        margin-top: 25vh;
    }
    .subtitle {
        font-size: 18px;
        color: #999;
        margin-top: 30px;
        font-style: italic;
    }
    </style>
""", unsafe_allow_html=True)

# Center content
st.markdown('<div class="main-title">诡秘晚上一起打三角洲</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">A quiet, mysterious night begins...</div>', unsafe_allow_html=True)
