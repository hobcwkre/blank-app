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

st.set_page_config(page_title="守護長輩", layout="centered", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    /* 隱藏 Streamlit 預設元素 */
    #MainMenu, footer, header { visibility: hidden; }
    .stDeployButton { display: none; }
    section[data-testid="stSidebar"] { display: none; }

    html, body, [class*="css"] {
        font-size: 16px;
        background-color: #f0f2f5;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }
    .block-container {
        padding: 0 0 120px 0 !important;
        max-width: 480px !important;
        margin: auto !important;
    }

    /* 頂部列 */
    .top-bar {
        background: white;
        padding: 16px 20px 12px;
        position: sticky;
        top: 0;
        z-index: 100;
        border-bottom: 1px solid #f0f0f0;
    }
    .top-title { font-size: 20px; font-weight: 700; color: #1a1a1a; }
    .top-sub { font-size: 13px; color: #999; margin-top: 2px; }

    /* 盾牌區域 */
    .shield-wrap {
        display: flex;
        flex-direction: column;
        align-items: center;
        padding: 32px 0 20px;
        background: white;
        margin-bottom: 12px;
    }
    .shield-circle {
        width: 160px; height: 160px;
        border-radius: 50%;
        background: #e8edf5;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        margin-bottom: 16px;
        transition: all 0.3s;
    }
    .shield-circle-on {
        background: linear-gradient(135deg, #4a90e2, #2563eb);
        box-shadow: 0 8px 32px rgba(74,144,226,0.35);
    }
    .shield-svg { width: 72px; height: 72px; }
    .shield-label {
        font-size: 15px;
        font-weight: 600;
        color: #666;
        margin-top: 6px;
    }
    .shield-label-on { color: white; }
    .status-pill {
        padding: 8px 28px;
        border-radius: 24px;
        font-size: 14px;
        font-weight: 600;
    }
    .status-pill-on { background: #e8f5e9; color: #2e7d32; }
    .status-pill-off { background: #f5f5f5; color: #999; }

    /* 功能卡片區 */
    .card-section {
        padding: 16px;
        background: #f0f2f5;
    }
    .card-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 12px;
    }
    .nav-card {
        background: white;
        border-radius: 20px;
        padding: 24px 16px 20px;
        text-align: center;
        box-shadow: 0 2px 12px rgba(0,0,0,0.06);
    }
    .nav-card-icon {
        width: 52px; height: 52px;
        border-radius: 14px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto 12px;
        font-size: 26px;
    }
    .icon-blue { background: #e8f0fe; }
    .icon-orange { background: #fff3e0; }
    .icon-purple { background: #f3e5f5; }
    .icon-teal { background: #e0f7f4; }
    .nav-card-label { font-size: 16px; font-weight: 700; color: #1a1a1a; }
    .nav-card-desc { font-size: 12px; color: #999; margin-top: 4px; }

    /* 底部導覽列 */
    .bottom-nav {
        position: fixed;
        bottom: 0; left: 50%;
        transform: translateX(-50%);
        width: 100%;
        max-width: 480px;
        background: white;
        border-top: 1px solid #eee;
        display: flex;
        justify-content: space-around;
        padding: 10px 0 16px;
        z-index: 999;
        box-shadow: 0 -2px 12px rgba(0,0,0,0.06);
    }
    .bnav-item {
        display: flex;
        flex-direction: column;
        align-items: center;
        font-size: 11px;
        color: #bbb;
        min-width: 60px;
    }
    .bnav-item-active { color: #4a90e2; }
    .bnav-icon { font-size: 22px; margin-bottom: 3px; }

    /* 按鈕覆蓋 */
    .stButton > button {
        border-radius: 14px !important;
        font-size: 16px !important;
        padding: 13px !important;
        width: 100% !important;
        background-color: #4a90e2 !important;
        color: white !important;
        border: none !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 12px rgba(74,144,226,0.3) !important;
    }
    .stButton > button:hover {
        background-color: #2563eb !important;
    }

    /* 隱藏導覽按鈕文字 */
    .nav-btn-row .stButton > button {
        background: transparent !important;
        color: transparent !important;
        border: none !important;
        box-shadow: none !important;
        padding: 4px !important;
        font-size: 1px !important;
        height: 60px !important;
    }

    /* 內容區塊 */
    .content-area { padding: 16px; }
    .section-card {
        background: white;
        border-radius: 20px;
        padding: 20px;
        margin-bottom: 12px;
        box-shadow: 0 2px 12px rgba(0,0,0,0.06);
    }
    .alert-box {
        background: #fff0f0;
        border-left: 5px solid #e74c3c;
        border-radius: 12px;
        padding: 16px;
        font-size: 18px;
        font-weight: 700;
        color: #c0392b;
        text-align: center;
        margin: 12px 0;
    }
    .warn-box {
        background: #fffbf0;
        border-left: 5px solid #f39c12;
        border-radius: 12px;
        padding: 16px;
        font-size: 18px;
        font-weight: 700;
        color: #d68910;
        text-align: center;
        margin: 12px 0;
    }
    .safe-box {
        background: #f0fff4;
        border-left: 5px solid #2ecc71;
        border-radius: 12px;
        padding: 16px;
        font-size: 18px;
        font-weight: 700;
        color: #27ae60;
        text-align: center;
        margin: 12px 0;
    }
    .fraud-item {
        background: white;
        border-radius: 16px;
        padding: 16px;
        margin-bottom: 10px;
        box-shadow: 0 1px 6px rgba(0,0,0,0.06);
        display: flex;
        align-items: flex-start;
        gap: 12px;
    }
    .fraud-icon {
        width: 44px; height: 44px;
        border-radius: 12px;
        background: #fff0f0;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 22px;
        flex-shrink: 0;
    }
    .fraud-content {}
    .fraud-title { font-size: 15px; font-weight: 700; color: #1a1a1a; margin-bottom: 4px; }
    .fraud-desc { font-size: 13px; color: #666; line-height: 1.5; }
    .stTextArea textarea {
        border-radius: 12px !important;
        font-size: 15px !important;
        border: 1px solid #eee !important;
    }
    </style>
""", unsafe_allow_html=True)

# 函數定義
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

# Session state
if 'page' not in st.session_state:
    st.session_state.page = "首頁"
if 'detect_on' not in st.session_state:
    st.session_state.detect_on = False

page = st.session_state.page

# 底部導覽列 HTML
nav_pages = ["首頁", "聯絡家人", "AI客服", "詐騙百科", "個人中心"]
nav_icons = ["🏠", "📞", "🤖", "📖", "👤"]
nav_html = '<div class="bottom-nav">'
for i, (label, icon) in enumerate(zip(nav_pages, nav_icons)):
    active = "bnav-item-active" if page == label else ""
    nav_html += f'<div class="bnav-item {active}"><div class="bnav-icon">{icon}</div>{label}</div>'
nav_html += '</div>'
st.markdown(nav_html, unsafe_allow_html=True)

# 導覽按鈕（透明覆蓋）
cols = st.columns(5)
for i, (col, label) in enumerate(zip(cols, nav_pages)):
    with col:
        if st.button("　", key=f"nav_{i}"):
            st.session_state.page = label
            st.rerun()

# 首頁
if page == "首頁":
    st.markdown("""
        <div class="top-bar">
            <div class="top-title">🛡️ 守護長輩</div>
            <div class="top-sub">防詐騙守護系統</div>
        </div>
    """, unsafe_allow_html=True)

    if st.session_state.detect_on:
        st.markdown("""
            <div class="shield-wrap">
                <div class="shield-circle shield-circle-on">
                    <svg class="shield-svg" viewBox="0 0 24 24" fill="none">
                        <path d="M12 2L3 6V12C3 16.5 7 20.7 12 22C17 20.7 21 16.5 21 12V6L12 2Z"
                            fill="white" opacity="0.9"/>
                        <path d="M9 12L11 14L15 10" stroke="#4a90e2" stroke-width="2"
                            stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                    <div class="shield-label shield-label-on">守護中</div>
                </div>
                <div class="status-pill status-pill-on">🟢 偵測中，您的安全有保障</div>
            </div>
        """, unsafe_allow_html=True)
        if st.button("關閉守護"):
            st.session_state.detect_on = False
            st.rerun()
    else:
        st.markdown("""
            <div class="shield-wrap">
                <div class="shield-circle">
                    <svg class="shield-svg" viewBox="0 0 24 24" fill="none">
                        <path d="M12 2L3 6V12C3 16.5 7 20.7 12 22C17 20.7 21 16.5 21 12V6L12 2Z"
                            fill="#b0bec5"/>
                    </svg>
                    <div class="shield-label">開始守護</div>
                </div>
                <div class="status-pill status-pill-off">⚪ 請按下方按鈕開始</div>
            </div>
        """, unsafe_allow_html=True)
        if st.button("開始守護"):
            st.session_state.detect_on = True
            st.rerun()

    st.markdown("""
        <div class="card-section">
            <div class="card-grid">
                <div class="nav-card">
                    <div class="nav-card-icon icon-blue">📞</div>
                    <div class="nav-card-label">聯絡家人</div>
                    <div class="nav-card-desc">一鍵傳送紀錄</div>
                </div>
                <div class="nav-card">
                    <div class="nav-card-icon icon-orange">🤖</div>
                    <div class="nav-card-label">AI客服</div>
                    <div class="nav-card-desc">AI辨識詐騙</div>
                </div>
                <div class="nav-card">
                    <div class="nav-card-icon icon-purple">📖</div>
                    <div class="nav-card-label">詐騙百科</div>
                    <div class="nav-card-desc">認識常見詐騙</div>
                </div>
                <div class="nav-card">
                    <div class="nav-card-icon icon-teal">👤</div>
                    <div class="nav-card-label">個人中心</div>
                    <div class="nav-card-desc">帳號設定</div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

# AI客服
elif page == "AI客服":
    st.markdown("""
        <div class="top-bar">
            <div class="top-title">🤖 AI防詐幫手</div>
            <div class="top-sub">告訴我發生了什麼，我來幫您判斷</div>
        </div>
    """, unsafe_allow_html=True)
    st.markdown('<div class="content-area">', unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["📩 訊息偵測", "📞 通話偵測"])
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
    st.markdown('</div>', unsafe_allow_html=True)

# 聯絡家人
elif page == "聯絡家人":
    st.markdown("""
        <div class="top-bar">
            <div class="top-title">📞 聯絡家人</div>
            <div class="top-sub">直接打電話給家人</div>
        </div>
    """, unsafe_allow_html=True)
    st.markdown('<div class="content-area">', unsafe_allow_html=True)
    st.markdown("""
        <div class="section-card" style="text-align:center; padding: 40px 20px;">
            <div style="font-size:56px; margin-bottom:16px;">👥</div>
            <div style="font-size:18px; font-weight:700; color:#1a1a1a; margin-bottom:8px;">尚未設定緊急聯絡人</div>
            <div style="font-size:14px; color:#999;">請先到個人中心新增聯絡人</div>
        </div>
    """, unsafe_allow_html=True)
    if st.button("前往設定"):
        st.session_state.page = "個人中心"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# 詐騙百科
elif page == "詐騙百科":
    st.markdown("""
        <div class="top-bar">
            <div class="top-title">📖 詐騙百科</div>
            <div class="top-sub">認識常見詐騙，保護自己</div>
        </div>
    """, unsafe_allow_html=True)
    st.markdown('<div class="content-area">', unsafe_allow_html=True)
    frauds = [
        ("📞", "假冒銀行客服詐騙", "詐騙集團假冒銀行客服來電，聲稱帳戶異常需要操作ATM或匯款。銀行不會要求您操作ATM或提供密碼。"),
        ("🎁", "中獎通知詐騙", "透過簡訊或通訊軟體通知您中了大獎，但需先繳稅金或手續費才能領取獎金。"),
        ("👥", "假冒親友借錢", "詐騙集團假冒您的家人或朋友，用LINE或電話說急需用錢，要求匯款。"),
        ("📈", "投資詐騙", "以高獲利、保證獲利為誘餌，要求您加入投資群組或操作不明平台。"),
        ("🏛️", "假冒公務員詐騙", "假冒警察、檢察官、金管會人員來電，聲稱您涉嫌犯罪需要配合調查或轉帳。"),
    ]
    for icon, title, desc in frauds:
        st.markdown(f"""
            <div class="fraud-item">
                <div class="fraud-icon">{icon}</div>
                <div class="fraud-content">
                    <div class="fraud-title">{title}</div>
                    <div class="fraud-desc">{desc}</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# 個人中心
elif page == "個人中心":
    st.markdown("""
        <div class="top-bar">
            <div class="top-title">👤 個人中心</div>
            <div class="top-sub">帳號和聯絡人設定</div>
        </div>
    """, unsafe_allow_html=True)
    st.markdown('<div class="content-area">', unsafe_allow_html=True)
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown("**帳號類型**")
    col1, col2 = st.columns(2)
    with col1:
        st.button("👴 我是長者", key="role_elder")
    with col2:
        st.button("👨‍👩‍👧 我是家屬", key="role_family")
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
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
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
