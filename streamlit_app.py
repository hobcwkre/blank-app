import streamlit as st

# 頁面設定
st.set_page_config(page_title="防詐守護", page_icon="🛡️", layout="centered")

# 大字體 CSS
st.markdown("""
    <style>
    html, body, [class*="css"] {
        font-size: 22px;
    }
    .title {
        font-size: 48px;
        font-weight: bold;
        text-align: center;
        color: #1a1a1a;
    }
    .subtitle {
        font-size: 24px;
        text-align: center;
        color: #555;
    }
    .status-on {
        font-size: 28px;
        color: green;
        text-align: center;
        font-weight: bold;
        padding: 10px;
    }
    .status-off {
        font-size: 28px;
        color: gray;
        text-align: center;
        font-weight: bold;
        padding: 10px;
    }
    .stButton > button {
        font-size: 24px;
        padding: 16px 40px;
        border-radius: 12px;
        width: 100%;
    }
    .alert {
        font-size: 26px;
        color: red;
        font-weight: bold;
        text-align: center;
        padding: 20px;
    }
    .safe {
        font-size: 26px;
        color: green;
        font-weight: bold;
        text-align: center;
        padding: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# 詐騙關鍵字（從卡方結果取出）
FRAUD_KEYWORDS = [
    "ATM", "解除", "匯款", "轉帳", "帳戶異常", "點數", "獲利", "投資",
    "擔保金", "凍結", "金管會", "線上授權", "分期付款", "操作錯誤",
    "核實", "專員", "主任", "啟動資金", "高階專案", "入金", "提領",
    "第三方", "工程師", "財力證明", "獎金", "兌換", "升級會員",
    "保證獲利", "主力", "飆股", "黑馬股", "加LINE", "私加"
]

# 標題
st.markdown('<div class="title">🛡️ 防詐守護</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">守護您的財產安全</div>', unsafe_allow_html=True)
st.markdown("---")

# 偵測開關
if 'detect_on' not in st.session_state:
    st.session_state.detect_on = False

col1, col2 = st.columns(2)
with col1:
    if st.button("✅ 開啟偵測"):
        st.session_state.detect_on = True
with col2:
    if st.button("❌ 關閉偵測"):
        st.session_state.detect_on = False

if st.session_state.detect_on:
    st.markdown('<div class="status-on">🟢 偵測中...</div>', unsafe_allow_html=True)
else:
    st.markdown('<div class="status-off">⚪ 偵測已關閉</div>', unsafe_allow_html=True)

st.markdown("---")

# 頁面切換
page = st.radio("選擇功能", ["📩 訊息偵測", "📞 通話內容偵測", "👨‍👩‍👧 緊急聯絡人"], horizontal=True)

st.markdown("---")

if page == "📩 訊息偵測":
    st.markdown("### 📩 輸入可疑訊息")
    user_input = st.text_area(
        "請貼上收到的訊息：",
        height=180,
        placeholder="例如：您的帳戶異常，請立即操作ATM解除..."
    )

    if st.button("🔍 立即分析"):
        if not st.session_state.detect_on:
            st.warning("⚠️ 請先開啟偵測功能")
        elif user_input.strip() == "":
            st.warning("⚠️ 請輸入訊息內容")
        else:
            hit = [kw for kw in FRAUD_KEYWORDS if kw in user_input]
            risk_score = min(len(hit) / 3, 1.0)

            if hit:
                st.markdown('<div class="alert">🚨 警告！偵測到詐騙風險！</div>', unsafe_allow_html=True)
                st.error(f"偵測到關鍵字：{', '.join(hit)}")
                st.progress(risk_score)
                st.markdown(f"**風險程度：{int(risk_score*100)}%**")
                st.markdown("---")
                st.markdown("**建議：**")
                st.markdown("- 請勿匯款或轉帳")
                st.markdown("- 立即撥打 **165** 反詐騙專線")
                st.ma
