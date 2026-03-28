import streamlit as st
import pickle
import jieba
import opencc
from KeyMojiAPI import KeyMoji

@st.cache_resource
def load_model():
    with open('fraud_model.pkl', 'rb') as f:
        model = pickle.load(f)
    with open('vectorizer.pkl', 'rb') as f:
        vectorizer = pickle.load(f)
    return model, vectorizer

@st.cache_resource
def load_keymoji():
    return KeyMoji()

model, vectorizer = load_model()
km = load_keymoji()
s2tw = opencc.OpenCC('s2tw')

st.set_page_config(page_title="防詐守護", layout="centered")

st.markdown("""
    <style>
    html, body, [class*="css"] { font-size: 20px; }
    .title { font-size: 36px; font-weight: bold; text-align: center; color: #1a1a1a; margin-bottom: 4px; }
    .subtitle { font-size: 18px; text-align: center; color: #888; margin-bottom: 20px; }
    .status-on { font-size: 18px; color: #2ecc71; text-align: center; font-weight: bold; }
    .status-off { font-size: 18px; color: #aaa; text-align: center; font-weight: bold; }
    .stButton > button { font-size: 20px; padding: 14px; border-radius: 12px; width: 100%; background-color: #1a1a2e; color: white; border: none; margin-top: 8px; }
    .alert-box { background-color: #fff0f0; border-left: 6px solid #e74c3c; padding: 16px 20px; border-radius: 8px; font-size: 22px; font-weight: bold; color: #c0392b; text-align: center; margin: 12px 0; }
    .safe-box { background-color: #f0fff4; border-left: 6px solid #2ecc71; padding: 16px 20px; border-radius: 8px; font-size: 22px; font-weight: bold; color: #27ae60; text-align: center; margin: 12px 0; }
    .warn-box { background-color: #fffbf0; border-left: 6px solid #f39c12; padding: 16px 20px; border-radius: 8px; font-size: 22px; font-weight: bold; color: #d68910; text-align: center; margin: 12px 0; }
    </style>
""", unsafe_allow_html=True)

def predict_xgb(text):
    text_tw = s2tw.convert(text)
    tokens = ' '.join(jieba.cut(text_tw))
    X = vectorizer.transform([tokens])
    prob = model.predict_proba(X)[0][1]
    return float(prob)

def get_keyword_density(text):
    keywords = [
        "ATM", "解除", "匯款", "轉帳", "帳戶異常", "點數", "獲利", "投資",
        "擔保金", "凍結", "金管會", "線上授權", "分期付款", "操作錯誤",
        "核實", "專員", "主任", "啟動資金", "入金", "第三方", "工程師",
        "保證獲利", "主力", "飆股", "加LINE"
    ]
    hit = [kw for kw in keywords if kw in text]
    density = min(len(hit) / 5, 1.0)
    return float(density), hit

def get_emotion_score(text):
    try:
        result = km.sense8(text)
        if result['status'] and result['results']:
            scores = result['results'][0]
            fear = scores.get('Fear', 0)
            anger = scores.get('Anger', 0)
            disgust = scores.get('Disgust', 0)
            emotion_score = min((fear + anger + disgust) / 15, 1.0)
            return float(emotion_score), scores
    except:
        pass
    return 0.0, {}

def calculate_risk(text):
    xgb_prob = predict_xgb(text)
    keyword_density, hit_keywords = get_keyword_density(text)
    emotion_score, emotion_detail = get_emotion_score(text)
    risk_score = 0.5 * xgb_prob + 0.3 * keyword_density + 0.2 * emotion_score
    return {
        'risk_score': float(risk_score),
        'xgb_prob': xgb_prob,
        'keyword_density': keyword_density,
        'emotion_score': emotion_score,
        'hit_keywords': hit_keywords,
        'emotion_detail': emotion_detail
    }

def show_result(text):
    r = calculate_risk(text)
    score = r['risk_score']
    risk_pct = int(score * 100)

    if score >= 0.7:
        st.markdown('<div class="alert-box">高風險　請立即停止操作</div>', unsafe_allow_html=True)
        level = "高風險"
    elif score >= 0.4:
        st.markdown('<div class="warn-box">中風險　請謹慎確認</div>', unsafe_allow_html=True)
        level = "中風險"
    else:
        st.markdown('<div class="safe-box">低風險　未偵測到明顯詐騙</div>', unsafe_allow_html=True)
        level = "低風險"

    st.progress(score)
    st.markdown(f"**綜合風險分數：{risk_pct}%（{level}）**")

    with st.expander("查看詳細分析"):
        st.markdown(f"- 文字模型（XGBoost）：{int(r['xgb_prob']*100)}%")
        st.markdown(f"- 關鍵字密度：{int(r['keyword_density']*100)}%")
        if r['hit_keywords']:
            st.markdown(f"- 偵測到關鍵字：{', '.join(r['hit_keywords'])}")
        st.markdown(f"- 情緒風險分數：{int(r['emotion_score']*100)}%")

    if score >= 0.4:
        st.error("建議：請勿匯款或轉帳，立即撥打 165 反詐騙專線，通知家人確認")

st.markdown('<div class="title">防詐守護</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">守護您的財產安全</div>', unsafe_allow_html=True)
st.markdown("---")

detect_on = st.toggle("開啟防詐偵測")
if detect_on:
    st.markdown('<div class="status-on">偵測中</div>', unsafe_allow_html=True)
else:
    st.markdown('<div class="status-off">偵測已關閉</div>', unsafe_allow_html=True)

st.markdown("---")

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
    user_input = st.text_area("請貼上收到的訊息：", height=180,
        placeholder="例如：您的帳戶異常，請立即操作ATM解除...")
    if st.button("立即分析"):
        if not detect_on:
            st.warning("請先開啟偵測功能")
        elif user_input.strip() == "":
            st.warning("請輸入訊息內容")
        else:
            show_result(user_input)

elif page == "通話偵測":
    st.markdown("### 輸入通話內容")
    call_input = st.text_area("請輸入通話中對方說的話：", height=180,
        placeholder="例如：您好，我是金管會人員，您的帳戶涉嫌洗錢...")
    if st.button("立即分析"):
        if not detect_on:
            st.warning("請先開啟偵測功能")
        elif call_input.strip() == "":
            st.warning("請輸入通話內容")
        else:
            show_result(call_input)

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
opencc-python-reimplemented
