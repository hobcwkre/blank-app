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

st.set_page_config(page_title="守護長輩", layout="centered")

st.markdown("""
    <style>
    html, body, [class*="css"] {
        font-size: 18px;
        background-color: #f5f5f5;
    }
    .main { max-width: 400px; margin: auto; }
    .title {
        font-size: 28px;
        font-weight: bold;
        text-align: center;
        color: #1a1a1a;
        padding-top: 20px;
    }
    .subtitle {
        font-size: 15px;
        text-align: center;
        color: #888;
        margin-bottom: 24px;
    }
    .card {
        background: white;
        border-radius: 16px;
        padding: 20px;
        margin: 12px 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    }
    .nav-card {
        background: white;
        border-radius: 16px;
        padding: 20px 16px;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        cursor: pointer;
    }
    .nav-icon { font-size: 32px; margin-bottom: 8px; }
    .nav-label { font-size: 16px; font-weight: bold; color: #1a1a1a; }
    .nav-desc { font-size: 13px; color: #888; margin-top: 4px; }
    .shield-btn {
        width: 140px;
        height: 140px;
        border-radius: 50%;
        background: #e8edf5;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        margin: 20px auto;
        cursor: pointer;
        font-size: 48px;
    }
    .shield-on {
        background: linear-gradient(135deg, #4a90e2, #357abd);
        box-shadow: 0 4px 20px rgba(74,144,226,0.4);
    }
    .shield-label { font-size: 16px; font-weight: bold; color: #555; margin-top: 8px; }
    .status-bar {
        text-align: center;
        padding: 10px;
        border-radius: 20px;
        font-size: 15px;
        font-weight: bold;
        margin: 8px 0 20px;
    }
    .status-on-bar { background: #e8f5e9; color: #2e7d32; }
    .status-off-bar { background: #f5f5f5; color: #999; }
    .alert-box {
        background: #fff0f0;
        border-left: 5px solid #e74c3c;
        border-radius: 12px;
        padding: 16px;
        font-size: 20px;
        font-weight: bold;
        color: #c0392b;
        text-align: center;
        margin: 12px 0;
    }
    .warn-box {
        background: #fffbf0;
        border-left: 5px solid #f39c12;
        border-radius: 12px;
        padding: 16px;
        font-size: 20px;
        font-weight: bold;
        color: #d68910;
        text-align: center;
        margin: 12px 0;
    }
    .safe-box {
        background: #f0fff4;
        border-left: 5px solid #2ecc71;
        border-radius: 12px;
        padding: 16px;
        font-size: 20px;
        font-weight: bold;
        color: #27ae60;
        text-align: center;
        margin: 12px 0;
    }
    .stButton > button {
        border-radius: 12px;
        font-size: 17px;
        padding: 12px;
        width: 100%;
        background-color: #4a90e2;
        color: white;
        border: none;
        font-weight: bold;
    }
    .stTextArea textarea {
        border-radius: 12px;
        font-size: 16px;
    }
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
    density = min(len(hit) / 3, 1.0)
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
        st.markdown('<div class="alert-box">🚨 高風險　請立即停止操作</div>', unsafe_allow_html=True)
        level = "高風險"
    elif score >= 0.4:
        st.markdown('<div class="warn-box">⚠️ 中風險　請謹慎確認</div>', unsafe_allow_html=True)
        level = "中風險"
    else:
        st.markdown('<div class="safe-box">✅ 低風險　未偵測到明顯詐騙</div>', unsafe_allow_html=True)
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
        st.error("請勿匯款或轉帳，立即撥打 165 反詐騙專線，通知家人確認")

# session state
if 'page' not in st.session_state:
    st.session_state.page = "首頁"
if 'detect_on' not in st.session_state:
    st.session_state.detect_on = False

page = st.session_state.page

# 首頁
if page == "首頁":
    st.markdown('<div class="title">🛡️ 守護長輩</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">防詐騙守護系統</div>', unsafe_allow_html=True)

    if st.session_state.detect_on:
        st.markdown('<div class="shield-btn shield-on">🛡️<div style="font-size:14px;color:white;margin-top:8px;">守護中</div></div>', unsafe_allow_html=True)
        st.markdown('<div class="status-bar status-on-bar">🟢 偵測中，您的安全有保障</div>', unsafe_allow_html=True)
        if st.button("關閉守護"):
            st.session_state.detect_on = False
            st.rerun()
    else:
        st.markdown('<div class="shield-btn">🛡️<div style="font-size:14px;color:#888;margin-top:8px;">開始守護</div></div>', unsafe_allow_html=True)
        st.markdown('<div class="status-bar status-off-bar">⚪ 請按上方按鈕開始</div>', unsafe_allow_html=True)
        if st.button("開始守護"):
            st.session_state.detect_on = True
            st.rerun()

    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📞 聯絡家人"):
            st.session_state.page = "聯絡家人"
            st.rerun()
        if st.button("📖 詐騙百科"):
            st.session_state.page = "詐騙百科"
            st.rerun()
    with col2:
        if st.button("🤖 AI客服"):
            st.session_state.page = "AI客服"
            st.rerun()
        if st.button("👤 個人中心"):
            st.session_state.page = "個人中心"
            st.rerun()

# AI客服
elif page == "AI客服":
    st.markdown("### 🤖 AI防詐幫手")
    st.markdown("告訴我發生了什麼，我來幫您判斷")
    st.markdown("---")

    tab1, tab2 = st.tabs(["訊息偵測", "通話內容偵測"])

    with tab1:
        user_input = st.text_area("請貼上收到的訊息：", height=150,
            placeholder="例如：您的帳戶異常，請立即操作ATM解除...")
        if st.button("立即分析", key="msg"):
            if not st.session_state.detect_on:
                st.warning("請先回首頁開啟守護功能")
            elif user_input.strip() == "":
                st.warning("請輸入訊息內容")
            else:
                show_result(user_input)

    with tab2:
        call_input = st.text_area("請輸入通話中對方說的話：", height=150,
            placeholder="例如：我是金管會人員，您的帳戶涉嫌洗錢...")
        if st.button("立即分析", key="call"):
            if not st.session_state.detect_on:
                st.warning("請先回首頁開啟守護功能")
            elif call_input.strip() == "":
                st.warning("請輸入通話內容")
            else:
                show_result(call_input)

    if st.button("← 返回首頁"):
        st.session_state.page = "首頁"
        st.rerun()

# 聯絡家人
elif page == "聯絡家人":
    st.markdown("### 📞 聯絡家人")
    st.markdown("直接打電話給家人")
    st.markdown("---")
    st.info("尚未設定緊急聯絡人，請前往個人中心新增")
    if st.button("前往設定"):
        st.session_state.page = "個人中心"
        st.rerun()
    if st.button("← 返回首頁"):
        st.session_state.page = "首頁"
        st.rerun()

# 詐騙百科
elif page == "詐騙百科":
    st.markdown("### 📖 詐騙百科")
    st.markdown("認識常見詐騙，保護自己")
    st.markdown("---")

    frauds = [
        ("假冒銀行客服詐騙", "詐騙集團假冒銀行客服來電，聲稱帳戶異常需要操作ATM或匯款。銀行不會要求您操作ATM或提供密碼。"),
        ("中獎通知詐騙", "透過簡訊或通訊軟體通知您中了大獎，但需先繳稅金或手續費才能領取獎金。"),
        ("假冒親友借錢", "詐騙集團假冒您的家人或朋友，用LINE或電話說急需用錢，要求匯款。"),
        ("投資詐騙", "以高獲利、保證獲利為誘餌，要求您加入投資群組或操作不明平台。"),
    ]

    for title, desc in frauds:
        with st.expander(title):
            st.write(desc)

    if st.button("← 返回首頁"):
        st.session_state.page = "首頁"
        st.rerun()

# 個人中心
elif page == "個人中心":
    st.markdown("### 👤 個人中心")
    st.markdown("帳號和聯絡人設定")
    st.markdown("---")

    with st.form("contact_form"):
        st.markdown("**新增緊急聯絡人**")
        name = st.text_input("聯絡人姓名", placeholder="例如：王小明")
        phone = st.text_input("聯絡人電話", placeholder="例如：0912345678")
        relation = st.selectbox("關係", ["子女", "配偶", "兄弟姐妹", "其他"])
        submitted = st.form_submit_button("儲存聯絡人")
        if submitted:
            if name and phone:
                st.success(f"已儲存聯絡人：{name}（{relation}）{phone}")
            else:
                st.warning("請填寫完整資料")

    if st.button("← 返回首頁"):
        st.session_state.page = "首頁"
        st.rerun()

st.markdown("---")
st.markdown(
    "<div style='text-align:center; color:gray; font-size:13px;'>如有緊急狀況請撥打 165 反詐騙專線</div>",
    unsafe_allow_html=True
)
