import streamlit as st
import pickle
import jieba

# 載入模型
@st.cache_resource
def load_model():
    with open('fraud_model.pkl', 'rb') as f:
        model = pickle.load(f)
    with open('vectorizer.pkl', 'rb') as f:
        vectorizer = pickle.load(f)
    return model, vectorizer

model, vectorizer = load_model()

# 頁面設定
st.set_page_config(page_title="防詐守護", page_icon="🛡️", layout="centered")

# 大字體 CSS
st.markdown("""
    <style>
    html, body, [class*="css"] { font-size: 22px; }
    .title { font-size: 48px; font-weight: bold; text-align: center; }
    .subtitle { font-size: 24px; text-align: center; color: #555; }
    .status-on { font-size: 28px; color: green; text-align: center; font-weight: bold; padding: 10px; }
    .status-off { font-size: 28px; color: gray; text-align: center; font-weight: bold; padding: 10px; }
    .stButton > button { font-size: 24px; padding: 16px 40px; border-radius: 12px; width: 100%; }
    .alert { font-size: 26px; color: red; font-weight: bold; text-align: center; padding: 20px; }
    .safe { font-size: 26px; color: green; font-weight: bold; text-align: center; padding: 20px; }
    </style>
""", unsafe_allow_html=True)

# 預測函數
def predict(text):
    tokens = ' '.join(jieba.cut(text))
    X = vectorizer.transform([tokens])
    prob = model.predict_proba(X)[0][1]
    return prob

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

def analyze(text):
    prob = predict(text)
    risk = int(prob * 100)

    if prob >= 0.5:
        st.markdown('<div class="alert">🚨 警告！偵測到詐騙風險！</div>', unsafe_allow_html=True)
        st.progress(prob)
        st.markdown(f"**詐騙機率：{risk}%**")
        st.error("建議：請勿匯款或轉帳，立即撥打 **165** 反詐騙專線，通知家人確認")
    else:
        st.markdown('<div class="safe">✅ 未偵測到明顯詐騙風險</div>', unsafe_allow_html=True)
        st.progress(prob)
        st.markdown(f"**詐騙機率：{risk}%**")
        st.info("仍請保持警覺，如有疑慮請撥打 165")

if page == "📩 訊息偵測":
    st.markdown("### 📩 輸入可疑訊息")
    user_input = st.text_area("請貼上收到的訊息：", height=180,
        placeholder="例如：您的帳戶異常，請立即操作ATM解除...")
    if st.button("🔍 立即分析"):
        if not st.session_state.detect_on:
            st.warning("⚠️ 請先開啟偵測功能")
        elif user_input.strip() == "":
            st.warning("⚠️ 請輸入訊息內容")
        else:
            analyze(user_input)

elif page == "📞 通話內容偵測":
    st.markdown("### 📞 輸入通話內容")
    call_input = st.text_area("請輸入通話中對方說的話：", height=180,
        placeholder="例如：您好，我是金管會人員，您的帳戶涉嫌洗錢...")
    if st.button("🔍 立即分析"):
        if not st.session_state.detect_on:
            st.warning("⚠️ 請先開啟偵測功能")
        elif call_input.strip() == "":
            st.warning("⚠️ 請輸入通話內容")
        else:
            analyze(call_input)

elif page == "👨‍👩‍👧 緊急聯絡人":
    st.markdown("### 👨‍👩‍👧 緊急聯絡人")
    st.markdown("當偵測到高風險訊息時，將自動通知以下聯絡人")
    st.markdown("---")
    with st.form("contact_form"):
        name = st.text_input("聯絡人姓名", placeholder="例如：王小明")
        phone = st.text_input("聯絡人電話", placeholder="例如：0912345678")
        relation = st.selectbox("關係", ["子女", "配偶", "兄弟姐妹", "其他"])
        submitted = st.form_submit_button("💾 儲存聯絡人")
        if submitted:
            if name and phone:
                st.success(f"✅ 已儲存聯絡人：{name}（{relation}）{phone}")
            else:
                st.warning("請填寫完整資料")

st.markdown("---")
st.markdown("<div style='text-align:center; color:gray; font-size:16px;'>如有緊急狀況請撥打 165 反詐騙專線</div>",
    unsafe_allow_html=True)
