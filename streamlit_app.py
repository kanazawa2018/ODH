import streamlit as st
import pandas as pd
import random
import os
import math

# --- 定数定義 ---
USER_DATA_FILE = 'tmp/users.csv'
CHAR_INFO_FILE = 'tmp/キャラ情報.csv'
ROUTE_DATA_FILE = 'tmp/周遊ルート.csv'
CHAR_IMAGE_DIR = 'tmp/キャラ画像'

# --- 初期設定: 必要なファイルやディレクトリが存在しない場合に作成 ---
def setup_files():
    """
    アプリ実行に必要なユーザーデータファイルやディレクトリを初期作成する。
    """
    # ユーザー情報CSV
    if not os.path.exists(USER_DATA_FILE):
        df_users = pd.DataFrame(columns=[
            'name', 'gender', 'age_group', 'hobbies',
            'pref_age_group', 'pref_hobbies', 'animal', 'group_id', 'route_no'
        ])
        df_users.to_csv(USER_DATA_FILE, index=False)

    # ../input ディレクトリがなければ作成
    input_dir = os.path.dirname(CHAR_INFO_FILE)
    if not os.path.exists(input_dir):
        os.makedirs(input_dir)

    # キャラ画像ディレクトリがなければ作成
    if not os.path.exists(CHAR_IMAGE_DIR):
        os.makedirs(CHAR_IMAGE_DIR)

# --- Step.1 の関数 ---
def assign_animal(char_df):
    """
    キャラ情報.csvに存在する動物の中からランダムに1つを割り当てる。
    """
    available_animals = char_df['動物'].tolist()
    if available_animals:
        return random.choice(available_animals)
    else:
        # CSVが空か、カラムが存在しない場合のフォールバック
        return '不明'

# --- Step.2 の関数 ---
def assign_groups_and_routes(users_df, routes_df):
    """
    ユーザーをグループ分けし、各グループに周遊ルートを割り当てる。
    """
    group_size = 4
    all_users_shuffled = users_df.sample(frac=1).reset_index(drop=True)
    num_groups = math.ceil(len(users_df) / group_size)

    for i, row in all_users_shuffled.iterrows():
        original_index = users_df[users_df['name'] == row['name']].index[0]
        users_df.loc[original_index, 'group_id'] = (i % num_groups) + 1

    unique_routes = routes_df['周遊ルートNo.'].unique().tolist()
    random.shuffle(unique_routes)

    if not unique_routes:
        st.error("周遊ルートが見つかりません。")
        return users_df

    for group_id in range(1, num_groups + 1):
        assigned_route_no = unique_routes[(group_id - 1) % len(unique_routes)]
        users_df.loc[users_df['group_id'] == group_id, 'route_no'] = assigned_route_no

    return users_df.sort_values(by=['group_id', 'name']).reset_index(drop=True)

# --- Step.3 の関数 ---
def get_assistant_response(user_input):
    responses = {
        "緊張": "深呼吸してみましょう！まずは笑顔で挨拶から始めると、自然と会話が弾みますよ。",
        "話": "相手のプロフィールを見て、共通の趣味について質問するのがおすすめです。「休日は何をされているんですか？」なども良いですね。",
        "沈黙": "沈黙が気まずい時は、周りの景色やお店の雰囲気について話してみるのはどうでしょう？「このお店、おしゃれですね」みたいに話しかけましょう。",
        "ありがとう": "どういたしまして！何か困ったことがあれば、いつでも話しかけてくださいね。",
    }
    for keyword, response in responses.items():
        if keyword in user_input:
            return response
    default_responses = [
        "なるほど、そうなんですね！", "面白いですね！もう少し詳しく教えてください。",
        "応援しています！楽しんでくださいね！", "何かお手伝いできることはありますか？"
    ]
    return random.choice(default_responses)

# --- Streamlit アプリ本体 ---
setup_files()

# ページ設定とカスタムCSS
st.set_page_config(
    page_title="アニマル縁結び - 多摩地域の魅力を楽しむ街コンアプリ", 
    page_icon="💕",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# モダンなカスタムCSS
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@300;400;500;700&display=swap');

/* 全体のフォント設定 */
html, body, [class*="css"] {
    font-family: 'Noto Sans JP', sans-serif;
}

/* メインコンテナ */
.main {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    min-height: 100vh;
}

/* ヘッダースタイル */
.header-container {
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(10px);
    border-radius: 20px;
    padding: 2rem;
    margin: 1rem 0 2rem 0;
    box-shadow: 0 8px 32px rgba(31, 38, 135, 0.37);
    border: 1px solid rgba(255, 255, 255, 0.18);
    text-align: center;
}

.app-title {
    font-size: 3rem;
    font-weight: 700;
    background: linear-gradient(45deg, #667eea, #764ba2);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 0.5rem;
    letter-spacing: 2px;
}

.app-subtitle {
    font-size: 1.2rem;
    color: #666;
    font-weight: 300;
    margin-bottom: 1rem;
}

.tama-badge {
    display: inline-block;
    background: linear-gradient(45deg, #FF6B6B, #4ECDC4);
    color: white;
    padding: 0.5rem 1.5rem;
    border-radius: 25px;
    font-weight: 500;
    font-size: 0.9rem;
    letter-spacing: 1px;
}

/* タブスタイル */
.stTabs [data-baseweb="tab-list"] {
    gap: 1rem;
    background: rgba(255, 255, 255, 0.1);
    padding: 0.5rem;
    border-radius: 15px;
    backdrop-filter: blur(10px);
}

.stTabs [data-baseweb="tab"] {
    height: 60px;
    background: rgba(255, 255, 255, 0.9);
    border-radius: 12px;
    border: none;
    color: #333;
    font-weight: 500;
    padding: 0 2rem;
    transition: all 0.3s ease;
}

.stTabs [aria-selected="true"] {
    background: linear-gradient(45deg, #667eea, #764ba2) !important;
    color: white !important;
    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
}

/* カードスタイル */
.card {
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(15px);
    border-radius: 20px;
    padding: 2rem;
    margin: 1rem 0;
    box-shadow: 0 8px 32px rgba(31, 38, 135, 0.37);
    border: 1px solid rgba(255, 255, 255, 0.18);
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.card:hover {
    transform: translateY(-5px);
    box-shadow: 0 15px 35px rgba(31, 38, 135, 0.5);
}

/* フォームスタイル */
.stSelectbox > div > div {
    background: rgba(255, 255, 255, 0.9);
    border-radius: 12px;
    border: 2px solid rgba(102, 126, 234, 0.2);
}

.stTextInput > div > div > input {
    background: rgba(255, 255, 255, 0.9);
    border-radius: 12px;
    border: 2px solid rgba(102, 126, 234, 0.2);
    font-weight: 500;
}

.stMultiSelect > div > div {
    background: rgba(255, 255, 255, 0.9);
    border-radius: 12px;
    border: 2px solid rgba(102, 126, 234, 0.2);
}

/* ボタンスタイル */
.stButton > button {
    background: linear-gradient(45deg, #667eea, #764ba2);
    color: white;
    border: none;
    border-radius: 25px;
    padding: 0.75rem 2rem;
    font-weight: 600;
    font-size: 1rem;
    letter-spacing: 1px;
    transition: all 0.3s ease;
    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
}

.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(102, 126, 234, 0.6);
}

/* エクスパンダースタイル */
.streamlit-expanderHeader {
    background: linear-gradient(45deg, #667eea, #764ba2);
    color: white;
    border-radius: 12px;
    font-weight: 600;
    padding: 1rem;
}

.streamlit-expanderContent {
    background: rgba(255, 255, 255, 0.95);
    border-radius: 0 0 12px 12px;
    padding: 1.5rem;
}

/* メトリクススタイル */
.metric-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 1.5rem;
    border-radius: 15px;
    text-align: center;
    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
}

/* チャットスタイル */
.chat-container {
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(15px);
    border-radius: 20px;
    padding: 2rem;
    margin: 1rem 0;
    box-shadow: 0 8px 32px rgba(31, 38, 135, 0.37);
}

.chat-row {
    display: flex;
    align-items: flex-start;
    margin-bottom: 2rem;
    animation: fadeInUp 0.5s ease;
}

.avatar-container {
    width: 80px;
    flex-shrink: 0;
    text-align: center;
    margin-right: 1rem;
}

.avatar-container img {
    width: 80px;
    height: 80px;
    border-radius: 50%;
    object-fit: cover;
    border: 3px solid #667eea;
    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
}

.avatar-container .char-name {
    font-weight: 600;
    margin-top: 0.5rem;
    font-size: 0.8rem;
    color: #667eea;
}

.message-bubble {
    background: linear-gradient(135deg, #f8f9ff 0%, #e8efff 100%);
    padding: 1.5rem;
    border-radius: 20px;
    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.1);
    border: 1px solid rgba(102, 126, 234, 0.1);
    font-size: 1rem;
    line-height: 1.6;
    max-width: 70%;
}

.user-message {
    justify-content: flex-end;
}

.user-message .message-bubble {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    margin-right: 1rem;
}

.user-message .avatar-container {
    margin-left: 1rem;
    margin-right: 0;
}

/* アニメーション */
@keyframes fadeInUp {
    from {
        opacity: 0;
        transform: translateY(30px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.fade-in {
    animation: fadeInUp 0.6s ease;
}

/* 成功・エラーメッセージのカスタマイズ */
.stSuccess {
    background: linear-gradient(45deg, #4ECDC4, #44A08D);
    color: white;
    border-radius: 12px;
    border: none;
    font-weight: 500;
}

.stError {
    background: linear-gradient(45deg, #FF6B6B, #FF8E8E);
    color: white;
    border-radius: 12px;
    border: none;
    font-weight: 500;
}

.stInfo {
    background: linear-gradient(45deg, #667eea, #764ba2);
    color: white;
    border-radius: 12px;
    border: none;
    font-weight: 500;
}

.stWarning {
    background: linear-gradient(45deg, #FFA726, #FFB74D);
    color: white;
    border-radius: 12px;
    border: none;
    font-weight: 500;
}

/* データフレームスタイル */
.dataframe {
    background: rgba(255, 255, 255, 0.95);
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.1);
}

/* アイコンスタイル */
.icon-large {
    font-size: 4rem;
    text-align: center;
    padding: 1rem;
    border-radius: 50%;
    background: linear-gradient(45deg, #667eea, #764ba2);
    color: white;
    width: 80px;
    height: 80px;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
}
</style>
""", unsafe_allow_html=True)

# ヘッダー
st.markdown("""
<div class="header-container fade-in">
    <div class="app-title">アニマル縁結び</div>
    <div class="app-subtitle">多摩地域で素敵な出会いを見つけよう</div>
    <div class="tama-badge">🌸 TOKYO TAMA AREA 🌸</div>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs([
    "🌟 事前登録",
    "👥 グループ編成・ルート確認", 
    "💬 当日用チャット"
])

# --- Tab1: 事前登録 ---
with tab1:
    st.markdown('<div class="card fade-in">', unsafe_allow_html=True)
    st.markdown("## 🌟 ユーザー情報登録")
    st.markdown("**多摩地域での素敵な街コンに参加しませんか？あなたの情報を教えてください！**")
    
    gender_options = ['男性', '女性']
    age_options = ['20代前半', '20代後半', '30代前半', '30代後半', '40代', '50代']
    hobby_options = [
        'アウトドア', 'スポーツ', '旅行', 'キャンプ', '読書', '映画鑑賞', 'ゲーム',
        '料理', '美術館巡り', '音楽鑑賞', 'カメラ', '歴史探訪'
    ]
    
    with st.form("registration_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🎯 あなたの情報")
            name = st.text_input("ニックネーム", placeholder="例：タロウ")
            gender = st.selectbox("性別", gender_options)
            age_group = st.selectbox("年代", age_options)
            hobbies = st.multiselect("趣味（複数選択可）", hobby_options)
        
        with col2:
            st.markdown("### 💕 お相手への希望")
            pref_age_group = st.multiselect("希望する年代", age_options)
            pref_hobbies = st.multiselect("希望する趣味", hobby_options)
            st.markdown("**※空欄でもOKです**")
        
        st.markdown("<br>", unsafe_allow_html=True)
        submitted = st.form_submit_button("✨ 登録して動物キャラを決める！", use_container_width=True)

    if submitted:
        if not name: 
            st.error("ニックネームを入力してください。")
        elif not hobbies: 
            st.error("趣味を1つ以上選択してください。")
        else:
            try:
                char_df = pd.read_csv(CHAR_INFO_FILE)
                if '動物' not in char_df.columns or char_df.empty:
                    st.error(f"'{CHAR_INFO_FILE}' が正しくないか、空です。")
                    st.stop()
            except FileNotFoundError:
                st.error(f"'{CHAR_INFO_FILE}' が見つかりません。アプリを続行できません。")
                st.stop()

            # 修正点: 趣味(hobbies)を渡さず、ランダムに動物を割り当てる
            animal = assign_animal(char_df)
            new_user = pd.DataFrame([{
                'name': name, 
                'gender': gender, 
                'age_group': age_group, 
                'hobbies': ", ".join(hobbies), 
                'pref_age_group': ", ".join(pref_age_group), 
                'pref_hobbies': ", ".join(pref_hobbies), 
                'animal': animal, 
                'group_id': 0, 
                'route_no': 0
            }])
            
            users_df = pd.read_csv(USER_DATA_FILE)
            if name in users_df['name'].values: 
                st.error("そのニックネームは既に使用されています。")
            else:
                updated_users_df = pd.concat([users_df, new_user], ignore_index=True)
                updated_users_df.to_csv(USER_DATA_FILE, index=False)
                
                st.success(f"🎉 {name}さん、登録が完了しました！")
                st.info(f"✨ あなたの動物キャラクターは「**{animal}**」です！")
                st.balloons()
    
    st.markdown('</div>', unsafe_allow_html=True)

# --- Tab2: グループ編成・ルート確認 ---
with tab2:
    st.markdown('<div class="card fade-in">', unsafe_allow_html=True)
    st.markdown("## 👥 グループと周遊ルートの確認")
    st.info("🌟 参加者全員が登録を終えたら、代表者が一度だけこのボタンを押してください。")
    
    if st.button("🚀 最新の参加者でグループとルートを編成する", use_container_width=True):
        users_df = pd.read_csv(USER_DATA_FILE)

        try:
            routes_df = pd.read_csv(ROUTE_DATA_FILE)
            required_cols = ['周遊ルートNo.', 'コース名', '所要時間', '参加費', '時間', '行程・内容', '交通・費用', '交流ポイント']
            if not all(col in routes_df.columns for col in required_cols):
                st.error(f"エラー: '{ROUTE_DATA_FILE}' に必要なカラムが不足しています。")
                st.stop()
        except FileNotFoundError:
            st.error(f"エラー: 周遊ルートファイル '{ROUTE_DATA_FILE}' が見つかりません。")
            st.stop()

        if len(users_df) > 0:
            users_with_groups_df = assign_groups_and_routes(users_df, routes_df)
            users_with_groups_df.to_csv(USER_DATA_FILE, index=False)

            st.success("🎉 グループ編成と周遊ルートの作成が完了しました！")
            st.balloons()

            num_groups = int(users_with_groups_df['group_id'].max())
            
            for group_id in range(1, num_groups + 1):
                with st.expander(f"🌟 **グループ {group_id}**", expanded=True):
                    col1, col2 = st.columns([1, 2])
                    
                    with col1:
                        st.markdown("#### 👫 メンバー")
                        group_members = users_with_groups_df[users_with_groups_df['group_id'] == group_id]
                        for _, row in group_members.iterrows():
                            st.markdown(f"**{row['name']}** ({row['gender']}, {row['age_group']}) - 🐾 **{row['animal']}**")

                    with col2:
                        st.markdown("#### 🗺️ 周遊プラン")
                        assigned_route_no = group_members['route_no'].iloc[0]
                        route_info = routes_df[routes_df['周遊ルートNo.'] == assigned_route_no]

                        if not route_info.empty:
                            header_info = route_info.iloc[0]
                            st.markdown(f"**ルートNo:** {int(header_info['周遊ルートNo.'])}　**コース名:** {header_info['コース名']}")
                            
                            metric_col1, metric_col2 = st.columns(2)
                            with metric_col1:
                                st.markdown(f'<div class="metric-card">⏰ 所要時間<br><strong>{header_info["所要時間"]}</strong></div>', unsafe_allow_html=True)
                            with metric_col2:
                                st.markdown(f'<div class="metric-card">💰 参加費目安<br><strong>{header_info["参加費"]}</strong></div>', unsafe_allow_html=True)

                            st.markdown("#### 📅 詳細スケジュール")
                            display_cols = ['時間', '行程・内容', '交通・費用', '交流ポイント']
                            st.dataframe(route_info[display_cols], hide_index=True, use_container_width=True)
                        else:
                            st.warning(f"ルートNo.{int(assigned_route_no)} の詳細が見つかりません。")
        else:
            st.warning("まだ参加者が登録されていません。")
    
    st.markdown('</div>', unsafe_allow_html=True)

# --- Tab3: 当日用チャット ---
with tab3:
    st.markdown('<div class="chat-container fade-in">', unsafe_allow_html=True)
    st.markdown("## 💬 アシスタントチャット")
    st.info("🤖 街コンでの振る舞いや会話に困ったら、多摩地域のことを知り尽くしたアシスタントに相談してみましょう！")

    users_df = pd.read_csv(USER_DATA_FILE)

    try:
        char_df = pd.read_csv(CHAR_INFO_FILE)
        if not all(col in char_df.columns for col in ['動物', 'キャラクター名']):
            st.warning(f"'{CHAR_INFO_FILE}' に必要なカラム（動物, キャラクター名）がありません。")
            char_df = None
    except FileNotFoundError:
        st.warning(f"キャラクター情報ファイル '{CHAR_INFO_FILE}' が見つかりません。")
        char_df = None

    if len(users_df) > 0:
        user_name = st.selectbox("🎭 あなたのニックネームを選択してください", options=users_df['name'].unique())

        if user_name:
            user_info = users_df[users_df['name'] == user_name].iloc[0]
            user_animal = user_info['animal']

            assistant_avatar_path = None
            assistant_char_name = user_animal
            if char_df is not None:
                char_info_row = char_df[char_df['動物'] == user_animal]
                if not char_info_row.empty:
                    assistant_char_name = char_info_row['キャラクター名'].iloc[0]
                    image_path = os.path.join(CHAR_IMAGE_DIR, f"{assistant_char_name}.jpg")
                    if os.path.exists(image_path):
                        assistant_avatar_path = image_path
                    else:
                        st.warning(f"アシスタント用アイコン画像が見つかりません: {image_path}")

            st.markdown(f"🌟 こんにちは、**{user_name}**さん！ あなたは **{user_animal}** タイプです。")

            if "messages" not in st.session_state:
                st.session_state.messages = []

            # チャット履歴の表示 (カスタムレイアウト)
            for msg in st.session_state.messages:
                if msg["role"] == "assistant":
                    st.markdown('<div class="chat-row">', unsafe_allow_html=True)
                    col1, col2 = st.columns([1, 5])
                    with col1:
                        if msg.get("avatar_path"):
                            st.image(msg["avatar_path"])
                        else:
                            st.markdown('<div class="icon-large">🤖</div>', unsafe_allow_html=True)
                        st.markdown(f"<p class='char-name'>{msg['char_name']}</p>", unsafe_allow_html=True)
                    with col2:
                        st.markdown(f'<div class="message-bubble">{msg["content"]}</div>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                else: # user
                    st.markdown('<div class="chat-row user-message">', unsafe_allow_html=True)
                    col1, col2 = st.columns([5, 1])
                    with col1:
                        st.markdown(f'<div class="message-bubble">{msg["content"]}</div>', unsafe_allow_html=True)
                    with col2:
                        st.markdown('<div class="icon-large">👤</div>', unsafe_allow_html=True)
                        st.markdown("<p class='char-name'>あなた</p>", unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)

            if prompt := st.chat_input("💬 アシスタントにメッセージを送る"):
                st.session_state.messages.append({"role": "user", "content": prompt})

                response = get_assistant_response(prompt)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response,
                    "avatar_path": assistant_avatar_path,
                    "char_name": assistant_char_name
                })
                st.rerun()
    else:
        st.warning("利用するには、まず「事前登録」タブでユーザーを登録してください。")
    
    st.markdown('</div>', unsafe_allow_html=True)
