import streamlit as st
import pickle
import jieba

@st.cache_resource
def load_model():
    with open('fraud_model.pkl', 'rb') as f:
        model = pickle.load(f)
    with open('vectorizer.pkl', 'rb') as f:
        vectorizer = pickle.load(f)
    return model, vectorizer

model, vectorizer = load_model()

st.set_page_config(page_title="防詐守護", page_icon="🛡️", layout="centered")

st.markdown("""
    <style>
    html, body, [class*="css"] { font-size: 20px; }

    .title {
        font-size: 36px;
        font-weight: bold;
        text-align: center;
        color: #1a1a1a;
        margin-bottom: 4px;
    }
    .subtitle {
        font-size: 18px;
        text-align: center;
        color: #888;
        margin-bottom: 20px;
    }
    .toggle-container {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 16px;
        margin: 20px 0;
    }
    .toggle-label {
        font-size: 20px;
        font-weight: bold;
        color: #333;
    }
    .toggle-switch {
        position: relative;
        width: 64px;
        height: 34px;
    }
    .toggle-switch input { opacity: 0; width: 0; height: 0; }
    .slider {
        position: absolute;
        cursor: pointer;
        top: 0; left: 0; right: 0; bottom: 0;
        background-color: #ccc;
        transition: .4s;
        border-radius: 34px;
    }
    .slider:before {
        position: absolute;
        content: "";
        height: 26px;
        width: 26px;
        left: 4px;
        bottom: 4px;
        background-color: white;
        transition: .4s;
        border-radius: 50%;
    }
    input:checked + .slider { background-color: #2ecc71; }
    input:checked + .slider:before { transform: translateX(30px); }

    .status-on {
        font-size: 18px;
        color: #2ecc71;
        text-align: center;
        font-weight: bold;
    }
    .status-off {
        font-size: 18px;
        color: #aaa;
        text-align: center;
        font-weight: bold;
    }
    .stButton > button {
        font-size: 20px;
        padding: 14px;
        border-radius: 12px;
        width: 100%;
        background-color: #1a1a2e;
        color: white;
        border: none;
        margin-top: 8px;
    }
    .stButton > button:hover {
        background-color: #16213e;
    }
    .alert-box {
        background-color: #fff0f0;
        border-left: 6px solid #e74c3c;
        padding: 16px 20px;
        border-radius: 8px;
        font-size: 22px;
        font-weight: bold;
        color: #c0392b;
        text-align: center;
        margin: 12px 0;
    }
    .safe-box {
        background-color: #f0fff4;
        border-left: 6px solid #2ecc71;
        padding: 16px 20px;
        border-radius: 8px;
        font-size: 22px;
        font-weight: bold;
        color: #27ae60;
        text-align: center;
        margin: 12px 0;
    }
    .nav-btn {
        display: block;
        width: 100%;
        padding: 18px;
        margin: 10px 0;
        font-size: 20px;
        font-weight: bold;
        background-color: #f5f5f5;
        border: 1px solid #ddd;
        border-radius: 12px;
        text-align: left;
        cursor: pointer;
        color: #1a1a1a;
    }
    </style>
""", unsafe_allow_html=True)

def predict(text):
    tokens = ' '.join(jieba.cut(text))
    X = vectorizer.transform([tokens])
    prob = model.predict_proba(X)[0][1]
    return float(prob)

def analyze(text):
    prob = predict(text)
    risk = int(prob * 100)
    if prob >= 0.5:
        st.markdown(f'<div class="alert-box">警告　偵測到詐騙風險</div>', unsafe_allow_html=True)
        st.progress(prob)
        st.markdown(f"**詐騙機率：{risk}%**")
        st.error("請勿匯款或轉帳，立即撥打 165 反詐騙專線，通知家人確認")
    else:
        st.markdown(f'<div class="safe-box">未偵測到明顯詐騙風險</div>', unsafe_allow_html=True)
        st.progress(prob)
        st.markdown(f"**詐騙機率：{risk}%**")
        st.info("仍請保持警覺，如有疑慮請撥打 165")

# 標題
st.markdown('<div class="title">防詐守護</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">守護您的財產安全</div>', unsafe_allow_html=True)
st.markdown("---")

# 切換開關
detect_on = st.toggle("開啟防詐偵測")

if detect_on:
    st.markdown('<div class="status-on">偵測中</div>', unsafe_allow_html=True)
else:
    st.markdown('<div class="status-off">偵測已關閉</div>', unsafe_allow_html=True)

st.markdown("---")

# 頁面切換
if 'page' not in st.session_state:
    st.session_state.page = "訊息偵測"

col1, col2, col3 = st.columns(3)
with col1:
    if st.button("訊息偵測"):
        st.session_state.page = "訊息偵測"
with col2:
    if st.button("通話偵測"):
        st.session_state.page = "通話偵測"
with col3:
    if st.button("緊急聯絡人"):
        st.session_state.page = "緊急聯絡人"

st.markdown("---")

page = st.session_state.page

if page == "訊息偵測":
    st.markdown("### 輸入可疑訊息")
    user_input = st.text_area(
        "請貼上收到的訊息：",
        height=180,
        placeholder="例如：您的帳戶異常，請立即操作ATM解除..."
    )
    if st.button("立即分析"):
        if not detect_on:
            st.warning("請先開啟偵測功能")
        elif user_input.strip() == "":
            st.warning("請輸入訊息內容")
        else:
            analyze(user_input)

elif page == "通話偵測":
    st.markdown("### 輸入通話內容")
    call_input = st.text_area(
        "請輸入通話中對方說的話：",
        height=180,
        placeholder="例如：您好，我是金管會人員，您的帳戶涉嫌洗錢..."
    )
    if st.button("立即分析"):
        if not detect_on:
            st.warning("請先開啟偵測功能")
        elif call_input.strip() == "":
            st.warning("請輸入通話內容")
        else:
            analyze(call_input)

elif page == "緊急聯絡人":
    st.markdown("### 緊急聯絡人")
    st.markdown("當偵測到高風險訊息時，將自動通知以下聯絡人")
    st.markdown("---")
    with st.form("contact_form"):
        name = st.text_input("聯絡人姓名", placeholder="例如：王小明")
        phone = st.text_input("聯絡人電話", placeholder="例如：0912345678")
        relation = st.selectbox("關係", ["子女", "配偶", "兄弟姐妹", "其他"])
        submitted = st.form_submit_button("儲存聯絡人")
        if submitted:
            if name and phone:
                st.success(f"已儲存聯絡人：{name}（{relation}）{phone}")
            else:
                st.warning("請填寫完整資料")

st.markdown("---")
st.markdown(
    "<div style='text-align:center; color:gray; font-size:14px;'>如有緊急狀況請撥打 165 反詐騙專線</div>",
    unsafe_allow_html=True
)
