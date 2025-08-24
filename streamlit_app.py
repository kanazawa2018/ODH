import streamlit as st
import pandas as pd
import random
import os
import math
import json
import datetime
from typing import Dict, List, Tuple

# --- 定数定義 (File paths for the demo) ---
# For the demo, ensure your CSV files are placed in these locations.
USER_DATA_FILE = '/tmp/users.csv'
CHAR_INFO_FILE = '/tmp/キャラ情報.csv'
ROUTE_DATA_FILE = '/tmp/input/周遊ルート.csv'
CHAR_IMAGE_DIR = '/tmp/input/キャラ画像'
EVENT_DATA_FILE = '/tmp/tama_events.json'  # 多摩地域イベント情報

# --- カラーパレット（東京都×若者向けデザイン） ---
COLORS = {
    'primary': '#1E88E5',      # 東京ブルー
    'secondary': '#FF6B6B',    # アクセントレッド
    'success': '#4ECDC4',      # ミントグリーン
    'warning': '#FFD93D',      # イエロー
    'dark': '#2C3E50',         # ダークグレー
    'light': '#F8F9FA',        # ライトグレー
    'gradient_start': '#667eea',
    'gradient_end': '#764ba2'
}

# --- デモ用サンプルデータ (Used only if the CSV files are not found) ---
SAMPLE_USERS_DATA = """name,gender,age_group,hobbies,pref_age_group,pref_hobbies,animal,group_id,route_no
えりか,女性,30代前半,"美術館巡り, 映画鑑賞","30代後半, 20代後半","映画鑑賞, 旅行",チーター,1,4
まこと,男性,20代後半,"読書, 歴史探訪","20代前半, 20代後半","読書, 映画鑑賞, 美術館巡り, 歴史探訪",チーター,1,4
みほ,女性,40代,"読書, 美術館巡り","30代前半, 30代後半","音楽鑑賞, 美術館巡り",アカカンガルー,1,4
りな,女性,30代前半,"アウトドア, カメラ","20代後半, 30代前半","アウトドア, カメラ",タスマニアデビル,1,4
さくら,男性,20代前半,"読書, 料理","20代前半, 20代後半","読書, 旅行",コアラ,2,5
しょうた,男性,30代前半,"ゲーム, カメラ","30代前半, 30代後半","映画鑑賞, 旅行",インドサイ,2,5
たくや,男性,20代前半,"アウトドア, 旅行","20代前半, 20代後半","スポーツ, キャンプ",インドサイ,2,5
まい,女性,20代後半,"音楽鑑賞, スポーツ","30代前半, 30代後半, 40代","スポーツ, 映画鑑賞",アカカンガルー,2,5
あやか,女性,40代,"料理, 美術館巡り","40代, 50代","旅行, 美術館巡り",コアラ,3,2
けんた,男性,30代前半,"スポーツ, 映画鑑賞, ゲーム",20代後半,スポーツ,オラウータン,3,2
だいき,男性,50代,"スポーツ, ゲーム","50代, 40代","料理, 美術館巡り",ライオン,3,2
なおみ,女性,30代後半,"スポーツ, アウトドア","30代前半, 30代後半","旅行, キャンプ",インドサイ,3,2
こうすけ,男性,30代後半,"旅行, アウトドア","20代後半, 20代前半","アウトドア, キャンプ",ライオン,4,1
みゆき,女性,20代後半,"料理, 旅行","20代前半, 20代後半, 30代前半","旅行, カメラ",オラウータン,4,1
ゆうた,男性,20代後半,"旅行, 音楽鑑賞","20代後半, 20代前半",音楽鑑賞,タイリクオオカミ,4,1
かな,女性,20代後半,"音楽鑑賞, 映画鑑賞","30代前半, 30代後半","映画鑑賞, 美術館巡り",コツメカワウソ,5,3
ひろき,男性,30代後半,"アウトドア, カメラ","30代前半, 20代後半","カメラ, 旅行",タスマニアデビル,5,3
ゆかり,女性,30代後半,"旅行, カメラ","30代前半, 30代後半, 40代","旅行, アウトドア",アカカンガルー,5,3
けんじ,男性,40代,"読書, 音楽鑑賞","30代前半, 30代後半","料理, 美術館巡り",ライオン,6,4
しんじ,男性,20代前半,"スポーツ, 音楽鑑賞",20代前半,"旅行, スポーツ",ワライカワセミ,6,4
りょう,男性,40代,"料理, カメラ","30代前半, 20代後半","旅行, 料理, 美術館巡り",コツメカワウソ,6,4"""

SAMPLE_CHAR_DATA = """動物,キャラクター名
コアラ,きんとき
インドサイ,デコポン
ライオン,ナナ
チーター,カロリーナ
オラウータン,キーボー
カピバラ,なえ
タイリクオオカミ,カヨラン
コツメカワウソ,ごんた
モウコノウマ,メロス
ワライカワセミ,キイロ
タスマニアデビル,パピティ
アカカンガルー,マルオ"""

SAMPLE_ROUTE_DATA = """周遊ルートNo.,コース名,時間,行程・内容,交通・費用,交流ポイント,所要時間,参加費
1,"Safari ✕ 花畑ピクニック",12:00,"多摩動物公園正門前→園内ラリー→モノレール→昭和記念公園ピクニック","入園600円+モノレール310円+公園450円","写真を見せ合いながらトーク・４人１組ゲーム",4時間15分,3000円
2,"レトロ建築スタンプラリー",9:30,"江戸東京たてもの園でスタンプラリー→昭和の居間体験→伝統玩具ワークショップ","モノレール・JR・バス片道750円+入園400円","20分毎にチーム替え・作品交換タイム",5時間20分,3500円
3,"深大寺そば打ち Love クッキング",11:00,"深大寺おみくじ→そば打ち体験→神代植物公園バラ園ツアー","京王線・バス片道490円+体験2000円+入園500円","共同作業で距離縮まる・花言葉トーク",5時間,4500円
4,"府中 歴史＆ホースバックヤードツアー",10:00,"府中市郷土の森→謎解き脱出ゲーム→東京競馬場バックヤード見学","交通費740円+入園300円+見学200円","５人１組で協力・競走馬の名前ビンゴ",5時間10分,4000円
5,"高尾山 サンセット・ケーブル Love Walk",13:00,"ケーブルカーで中腹→ペアトレッキング→山頂カフェ→駅前足湯","京王線300円+ケーブル960円+足湯500円","山恋フォトミッション・目隠し足湯Q&A",4時間,4000円"""

# --- 初期設定: 必要なファイルやディレクトリが存在しない場合にサンプルを作成 ---
def setup_files():
    """
    For demo purposes, this function checks for necessary files.
    If a file doesn't exist, it creates it using the sample data.
    If you provide your own CSV files, they will be used instead.
    """
    # Create directories if they don't exist
    os.makedirs(os.path.dirname(USER_DATA_FILE), exist_ok=True)
    os.makedirs(os.path.dirname(CHAR_INFO_FILE), exist_ok=True)
    os.makedirs(os.path.dirname(ROUTE_DATA_FILE), exist_ok=True)
    os.makedirs(CHAR_IMAGE_DIR, exist_ok=True)
    
    # User Info CSV - Create from sample if it doesn't exist
    if not os.path.exists(USER_DATA_FILE):
        try:
            with open(USER_DATA_FILE, 'w', encoding='utf-8') as f:
                f.write(SAMPLE_USERS_DATA)
        except Exception as e:
            st.error(f"Failed to create sample user data file: {e}")
    
    # Character Info CSV - Create from sample if it doesn't exist
    if not os.path.exists(CHAR_INFO_FILE):
        try:
            with open(CHAR_INFO_FILE, 'w', encoding='utf-8') as f:
                f.write(SAMPLE_CHAR_DATA)
        except Exception as e:
            st.error(f"Failed to create sample character info file: {e}")
    
    # Route CSV - Create from sample if it doesn't exist
    if not os.path.exists(ROUTE_DATA_FILE):
        try:
            with open(ROUTE_DATA_FILE, 'w', encoding='utf-8') as f:
                f.write(SAMPLE_ROUTE_DATA)
        except Exception as e:
            st.error(f"Failed to create sample route file: {e}")
    
    # Tama Events JSON - Create if it doesn't exist
    if not os.path.exists(EVENT_DATA_FILE):
        try:
            sample_events = {
                "seasonal_events": [
                    {"month": 1, "event": "🎍 多摩センター新春イルミネーション", "crowd_level": 3, "description": "100万球のLEDが織りなす幻想的な光の世界。カップルに大人気！"},
                    {"month": 4, "event": "🌺 昭和記念公園チューリップフェスティバル", "crowd_level": 4, "description": "20万球のチューリップが咲く、関東最大級の花畑"},
                    {"month": 8, "event": "🎆 立川まつり国営昭和記念公園花火大会", "crowd_level": 5, "description": "約5000発の花火が夜空を彩る！多摩地域最大級の花火大会"},
                    {"month": 11, "event": "🍁 高尾山もみじまつり", "crowd_level": 5, "description": "紅葉の絶景スポット！ケーブルカーから見る紅葉は格別"},
                ],
                "popular_spots": [
                    {
                        "name": "🏔️ 高尾山", "category": "自然・絶景", "avg_crowd": 3.5,
                        "highlight": "ミシュラン三ツ星の山！都心から1時間で本格登山",
                        "instagram_spots": ["山頂からの富士山", "もみじ台", "薬王院"],
                        "date_point": "ケーブルカーでの会話、達成感の共有", "best_time": "平日午前"
                    },
                    {
                        "name": "🎀 サンリオピューロランド", "category": "テーマパーク", "avg_crowd": 4.0,
                        "highlight": "全天候型屋内テーマパーク！キャラクターグリーティングが充実",
                        "instagram_spots": ["レディキティハウス", "ミラクルギフトパレード", "キキララ撮影スポット"],
                        "date_point": "童心に返って楽しめる、写真撮影で盛り上がる", "best_time": "平日"
                    },
                    {
                        "name": "🦁 多摩動物公園", "category": "動物園", "avg_crowd": 3.0,
                        "highlight": "300種を超える動物！アジア園のオランウータンスカイウォークは必見",
                        "instagram_spots": ["ライオンバス", "コアラ館", "チーターの丘"],
                        "date_point": "動物の話題で自然に会話が弾む", "best_time": "開園直後"
                    }
                ],
                 "hidden_gems": [
                    {
                        "name": "🎨 府中市美術館",
                        "description": "「生活と美術」をテーマにした展示。公園内にありピクニックも楽しめる",
                        "access": "京王線「東府中」駅からバス"
                    }
                ],
                "gourmet_spots": [
                    {
                        "name": "🍜 八王子ラーメン",
                        "description": "刻み玉ねぎが特徴の醤油ラーメン。市内に50店舗以上！",
                        "recommended": "みんみんラーメン、吾衛門"
                    }
                ]
            }
            with open(EVENT_DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump(sample_events, f, ensure_ascii=False, indent=2)
        except Exception as e:
            pass # Non-critical error, app can continue

# --- モダンなスタイル定義 ---
def apply_modern_style():
    st.markdown(f"""
    <style>
        .stApp {{
            background: linear-gradient(135deg, {COLORS['light']} 0%, #E3F2FD 100%);
        }}
        .main-header {{
            background: linear-gradient(90deg, {COLORS['primary']} 0%, {COLORS['gradient_start']} 100%);
            color: white; padding: 2rem; border-radius: 20px; margin-bottom: 2rem;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1); text-align: center;
        }}
        .main-header h1 {{
            font-size: 2.5rem; font-weight: 800; margin: 0;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }}
        .info-card {{
            background: white; border-radius: 16px; padding: 1.5rem; margin: 1rem 0;
            box-shadow: 0 4px 20px rgba(0,0,0,0.08);
            border-left: 4px solid {COLORS['primary']};
            transition: all 0.3s ease;
        }}
        .info-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 30px rgba(0,0,0,0.12);
        }}
        .animal-card {{
            background: linear-gradient(135deg, #fff 0%, #f8f9fa 100%);
            border: 2px solid {COLORS['primary']}; border-radius: 20px;
            padding: 1.5rem; text-align: center;
            box-shadow: 0 8px 25px rgba(0,0,0,0.1);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }}
        .animal-card:hover {{
            transform: scale(1.02) translateY(-3px);
            border-color: {COLORS['secondary']};
        }}
        .animal-name {{
            font-size: 1.8rem; font-weight: 700; color: {COLORS['primary']}; margin: 1rem 0;
        }}
        .member-card {{
            background: white; border-radius: 12px; padding: 1rem; margin: 0.5rem 0;
            display: flex; align-items: center; box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        }}
        .member-animal {{ font-size: 2rem; margin-right: 1rem; }}
        .route-card {{
            background: linear-gradient(135deg, #ffffff 0%, #f0f7ff 100%);
            border-radius: 16px; padding: 1.5rem; margin: 1rem 0;
            border: 1px solid #e0e0e0; box-shadow: 0 4px 15px rgba(0,0,0,0.06);
        }}
        .route-header {{
            display: flex; align-items: center; justify-content: space-between;
            margin-bottom: 1rem; padding-bottom: 0.5rem; border-bottom: 2px solid {COLORS['primary']};
        }}
        .route-title {{ font-size: 1.3rem; font-weight: 700; color: {COLORS['dark']}; }}
        .stButton > button {{
            background: linear-gradient(90deg, {COLORS['primary']} 0%, {COLORS['gradient_start']} 100%);
            color: white; border: none; border-radius: 30px; padding: 0.75rem 2rem;
            font-weight: 600; font-size: 1rem; transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(30, 136, 229, 0.3);
        }}
        .stButton > button:hover {{
            transform: translateY(-2px); box-shadow: 0 6px 20px rgba(30, 136, 229, 0.4);
        }}
        .stTabs [data-baseweb="tab"] {{ border-radius: 10px; padding: 0.75rem 1.5rem; font-weight: 600; }}
        .stTabs [aria-selected="true"] {{ background: {COLORS['primary']}; color: white; }}
        .success-message {{
            background: linear-gradient(90deg, {COLORS['success']} 0%, #26C6DA 100%);
            color: white; padding: 1rem 1.5rem; border-radius: 12px; margin: 1rem 0;
        }}
        .spot-card {{
            background: white; border-radius: 16px; padding: 1.2rem; margin: 0.5rem 0;
            box-shadow: 0 4px 15px rgba(0,0,0,0.08); transition: all 0.3s ease;
            border: 2px solid transparent;
        }}
        .spot-card:hover {{
            transform: translateY(-3px); border-color: {COLORS['primary']};
        }}
        .spot-title {{
            font-size: 1.2rem; font-weight: 700; color: {COLORS['dark']}; margin-bottom: 0.5rem;
        }}
        .crowd-indicator {{ display: inline-block; padding: 0.25rem 0.75rem; border-radius: 20px; font-weight: 600; }}
        .crowd-low {{ background: #C8E6C9; color: #2E7D32; }}
        .crowd-medium {{ background: #FFF9C4; color: #F57C00; }}
        .crowd-high {{ background: #FFCDD2; color: #C62828; }}
    </style>
    """, unsafe_allow_html=True)

# --- 多摩地域情報表示関数 ---
def show_tama_info():
    try:
        if not os.path.exists(EVENT_DATA_FILE):
            setup_files()
        
        with open(EVENT_DATA_FILE, 'r', encoding='utf-8') as f:
            event_data = json.load(f)
    except Exception:
        event_data = {} # Default to empty if any error
        st.warning("Could not load Tama area information.")

    current_month = datetime.datetime.now().month
    
    info_tab1, info_tab2 = st.tabs(["📅 季節のイベント", "📍 人気スポット"])
    
    with info_tab1:
        monthly_events = [e for e in event_data.get('seasonal_events', []) if e.get('month') == current_month]
        if monthly_events:
            st.markdown("### 🎊 今月のおすすめイベント")
            for event in monthly_events:
                crowd_level = event.get('crowd_level', 3)
                crowd_text = ['空いている', '普通', 'やや混雑', '混雑', '非常に混雑'][min(crowd_level - 1, 4)]
                st.info(f"**{event.get('event', 'イベント')}**\n\n{event.get('description', '')}\n\n混雑予想: {crowd_text}")
    
    with info_tab2:
        st.markdown("### 🌟 多摩地域の人気デートスポット")
        for spot in event_data.get('popular_spots', []):
            crowd_level = spot.get('avg_crowd', 3.0)
            crowd_class = 'low' if crowd_level < 2.5 else 'medium' if crowd_level < 3.5 else 'high'
            st.markdown(f"""
            <div class="spot-card">
                <div class="spot-title">{spot.get('name', 'N/A')}</div>
                <p><strong>✨ ここがすごい！</strong><br>{spot.get('highlight', 'N/A')}</p>
                <p><strong>💕 デートポイント:</strong><br>{spot.get('date_point', 'N/A')}</p>
                <p>
                    <strong>混雑度:</strong> 
                    <span class="crowd-indicator crowd-{crowd_class}">
                        {'★' * int(crowd_level)}{'☆' * (5 - int(crowd_level))}
                    </span>
                    <small>| 💡 おすすめ時間: {spot.get('best_time', 'N/A')}</small>
                </p>
            </div>
            """, unsafe_allow_html=True)

# --- 動物の絵文字マッピング ---
ANIMAL_EMOJI_MAP = {
    'コアラ': '🐨', 'インドサイ': '🦏', 'ライオン': '🦁', 'チーター': '🐆',
    'オラウータン': '🦧', 'カピバラ': '🦦', 'タイリクオオカミ': '🐺', 'コツメカワウソ': '🦦',
    'モウコノウマ': '🐴', 'ワライカワセミ': '🦜', 'タスマニアデビル': '😈', 'アカカンガルー': '🦘'
}
def get_animal_emoji(animal_name):
    return ANIMAL_EMOJI_MAP.get(animal_name, '🦊')

# --- Step.1 の関数 ---
def assign_animal(char_df):
    available_animals = char_df['動物'].tolist()
    return random.choice(available_animals) if available_animals else 'コアラ'

# --- Step.2 の関数 ---
def assign_groups_and_routes(users_df, routes_df):
    group_size = 4
    all_users_shuffled = users_df.sample(frac=1).reset_index(drop=True)
    num_groups = math.ceil(len(users_df) / group_size)
    
    for i, row in all_users_shuffled.iterrows():
        original_index = users_df[users_df['name'] == row['name']].index[0]
        users_df.loc[original_index, 'group_id'] = (i % num_groups) + 1
    
    try:
        routes_df['周遊ルートNo.'] = pd.to_numeric(routes_df['周遊ルートNo.'], errors='coerce')
        unique_routes = routes_df['周遊ルートNo.'].dropna().unique().tolist()
    except:
        unique_routes = [1, 2, 3, 4, 5]
    
    if not unique_routes:
        st.error("周遊ルートが見つかりません。")
        return users_df
    
    random.shuffle(unique_routes)
    
    for group_id in range(1, num_groups + 1):
        assigned_route_no = unique_routes[(group_id - 1) % len(unique_routes)]
        users_df.loc[users_df['group_id'] == group_id, 'route_no'] = assigned_route_no
    
    return users_df.sort_values(by=['group_id', 'name']).reset_index(drop=True)

# --- Step.3 の関数 ---
def get_assistant_response(user_input):
    responses = {
        "緊張": "深呼吸してリラックス！😊 まずは相手の動物キャラクターについて聞いてみるのはどうでしょう？「○○さんは何の動物になったんですか？」から始めると自然ですよ。",
        "話": "プロフィールカードを見て共通点を探してみましょう！多摩地域のおすすめスポットについて話すのも盛り上がりますよ。「高尾山行ったことありますか？」とか！",
        "沈黙": "周りの景色について話してみましょう！「この辺は初めて来ました」「いいお店ありそうですね」など、場所の話題は続きやすいです。",
        "ありがとう": "どういたしまして！楽しい街コンになりますように！何か困ったらいつでも聞いてくださいね😊",
        "おすすめ": "多摩地域なら、高尾山でハイキングデート、サンリオピューロランドで童心に返る、深大寺でのんびり散歩がおすすめです！",
    }
    for keyword, response in responses.items():
        if keyword in user_input:
            return response
    return random.choice([
        "いいですね！その調子で楽しんでください😊",
        "素敵な出会いになるといいですね！応援してます✨"
    ])

# --- ユーザー統計情報 ---
def show_user_stats():
    try:
        # Use the python engine and handle bad lines for more robust parsing
        users_df = pd.read_csv(USER_DATA_FILE, engine='python', on_bad_lines='warn')
        if not users_df.empty:
            col1, col2, col3, col4 = st.columns(4)
            male_count = len(users_df[users_df['gender'] == '男性'])
            female_count = len(users_df[users_df['gender'] == '女性'])
            col1.metric("👥 登録者数", f"{len(users_df)}名")
            col2.metric("⚖️ 男女比", f"{male_count}:{female_count}")
            col3.metric("👫 グループ数", f"{users_df['group_id'].nunique()}組")
            if 'animal' in users_df.columns and not users_df['animal'].empty:
                popular_animal = users_df['animal'].mode().iloc[0] if not users_df['animal'].mode().empty else "未定"
                col4.metric("🏆 人気キャラ", popular_animal)
    except (FileNotFoundError, pd.errors.EmptyDataError):
        pass # Don't show stats if file is missing or empty

# --- Streamlit アプリ本体 ---
def main():
    st.set_page_config(page_title="アニマル縁結び🦊", page_icon="🦊", layout="wide")
    
    setup_files()
    apply_modern_style()
    
    st.markdown("""
    <div class="main-header">
        <h1>🦊 アニマル縁結び 🦊</h1>
        <p>多摩地域で素敵な出会いを ～ 東京都オープンデータ活用街コンアプリ ～</p>
    </div>
    """, unsafe_allow_html=True)
    
    show_user_stats()
    
    tab1, tab2, tab3, tab4 = st.tabs([
        "📝 Step.1: 事前登録", "👥 Step.2: グループ編成・ルート確認",
        "💬 Step.3: 当日用チャット", "📍 多摩地域情報"
    ])
    
    # --- Tab1: 事前登録 ---
    with tab1:
        st.markdown("## 🎯 ユーザー情報登録")
        st.markdown("あなたの情報を登録して、運命の動物キャラクターを見つけよう！")
        
        with st.form("registration_form", clear_on_submit=True):
            name = st.text_input("ニックネーム *", placeholder="例: たまちゃん")
            gender = st.selectbox("性別 *", ['男性', '女性'])
            age_group = st.selectbox("年代 *", ['20代前半', '20代後半', '30代前半', '30代後半', '40代', '50代'])
            hobbies = st.multiselect("趣味（複数選択可） *", ['アウトドア', 'スポーツ', '旅行', '読書', '映画鑑賞', 'ゲーム', '料理', '美術館巡り'])
            submitted = st.form_submit_button("🎊 登録してキャラクターを受け取る", use_container_width=True)

        if submitted:
            if not name or not hobbies:
                st.error("⚠️ ニックネームと趣味は必須です。")
            else:
                try:
                    # Use the python engine and handle bad lines for more robust parsing
                    char_df = pd.read_csv(CHAR_INFO_FILE, engine='python', on_bad_lines='warn')
                    animal = assign_animal(char_df)
                    
                    new_user = pd.DataFrame([{'name': name, 'gender': gender, 'age_group': age_group, 'hobbies': ", ".join(hobbies), 'pref_age_group': '', 'pref_hobbies': '', 'animal': animal, 'group_id': 0, 'route_no': 0}])
                    
                    try:
                        # Use the python engine and handle bad lines for more robust parsing
                        users_df = pd.read_csv(USER_DATA_FILE, engine='python', on_bad_lines='warn')
                    except (FileNotFoundError, pd.errors.EmptyDataError):
                        users_df = pd.DataFrame()

                    if not users_df.empty and name in users_df['name'].values:
                        st.error("⚠️ そのニックネームは既に使用されています。")
                    else:
                        updated_users_df = pd.concat([users_df, new_user], ignore_index=True)
                        updated_users_df.to_csv(USER_DATA_FILE, index=False)
                        st.balloons()
                        st.markdown(f'<div class="success-message">✨ {name}さん、登録が完了しました！</div>', unsafe_allow_html=True)
                        st.markdown(f'<div class="animal-card"><div style="font-size: 5rem;">{get_animal_emoji(animal)}</div><div class="animal-name">あなたは「{animal}」タイプです！</div></div>', unsafe_allow_html=True)
                
                except Exception as e:
                    st.error(f"エラーが発生しました: {str(e)}")

    # --- Tab2: グループ編成・ルート確認 ---
    with tab2:
        st.markdown("## 👥 グループと周遊ルートの確認")
        st.info("💡 参加者全員が登録を終えたら、代表者が一度だけグループ編成ボタンを押してください。")
        
        if st.button("🎲 最新の参加者でグループとルートを編成する", use_container_width=True):
            try:
                # Use the python engine and handle bad lines for more robust parsing
                users_df = pd.read_csv(USER_DATA_FILE, engine='python', on_bad_lines='warn')
                routes_df = pd.read_csv(ROUTE_DATA_FILE, engine='python', on_bad_lines='warn')
                if not users_df.empty:
                    users_with_groups_df = assign_groups_and_routes(users_df, routes_df)
                    users_with_groups_df.to_csv(USER_DATA_FILE, index=False)
                    st.success("✅ グループ編成と周遊ルートの作成が完了しました！")
                    st.rerun() # Rerun to display the new groups immediately
                else:
                    st.warning("⚠️ まだ参加者が登録されていません。")
            except Exception as e:
                st.error(f"⚠️ エラーが発生しました: {e}")
        
        try:
            # Use the python engine and handle bad lines for more robust parsing
            users_df = pd.read_csv(USER_DATA_FILE, engine='python', on_bad_lines='warn')
            routes_df = pd.read_csv(ROUTE_DATA_FILE, engine='python', on_bad_lines='warn')
            
            if not users_df.empty and 'group_id' in users_df.columns and users_df['group_id'].max() > 0:
                st.markdown("--- \n### 📋 現在のグループ編成")
                num_groups = int(users_df['group_id'].max())
                
                for group_id in range(1, num_groups + 1):
                    group_members = users_df[users_df['group_id'] == group_id]
                    if not group_members.empty:
                        route_no = group_members['route_no'].iloc[0]
                        route_info = routes_df[routes_df['周遊ルートNo.'] == route_no]
                        route_name = route_info['コース名'].iloc[0] if not route_info.empty else "ルート未定"
                        
                        with st.expander(f"**📍 グループ {group_id}** - {len(group_members)}名 - {route_name}", expanded=True):
                            st.markdown("### 👥 メンバー")
                            for _, member in group_members.iterrows():
                                st.markdown(f'<div class="member-card"><span class="member-animal">{get_animal_emoji(member["animal"])}</span><div><strong>{member["name"]}</strong> ({member["gender"]}, {member["age_group"]})<br><small>趣味: {member["hobbies"]}</small></div></div>', unsafe_allow_html=True)
                            
                            st.markdown("### 🗺️ 周遊プラン")
                            if not route_info.empty:
                                details = route_info.iloc[0]
                                st.markdown(f"""
                                <div class="route-card">
                                    <div class="route-header"><span class="route-title">{details.get('コース名', 'N/A')}</span></div>
                                    <p><strong>📍 行程:</strong> {details.get('行程・内容', 'N/A')}</p>
                                    <p><strong>💕 交流ポイント:</strong> {details.get('交流ポイント', 'N/A')}</p>
                                </div>
                                """, unsafe_allow_html=True)
                            else:
                                st.warning(f"ルートNo.{int(route_no)} の詳細が見つかりません。")
            else:
                st.info("📝 まだグループが編成されていません。")
        except (FileNotFoundError, pd.errors.EmptyDataError):
            st.warning("⚠️ データファイルが見つかりません。「事前登録」タブから始めてください。")

    # --- Tab3: 当日用チャット ---
    with tab3:
        st.markdown("## 💬 AIアシスタントチャット")
        st.info("街コンでの会話に困ったら、アシスタントに相談してみましょう！")
        
        try:
            # Use the python engine and handle bad lines for more robust parsing
            users_df = pd.read_csv(USER_DATA_FILE, engine='python', on_bad_lines='warn')
            if not users_df.empty:
                user_name = st.selectbox("あなたのニックネームを選択してください", options=[''] + users_df['name'].unique().tolist())
                if user_name:
                    if "messages" not in st.session_state or st.session_state.get("current_user") != user_name:
                        st.session_state.messages = [{"role": "assistant", "content": f"こんにちは、{user_name}さん！🎉 何でも気軽に相談してくださいね！"}]
                        st.session_state.current_user = user_name

                    for message in st.session_state.messages:
                        with st.chat_message(message["role"]):
                            st.write(message["content"])

                    if prompt := st.chat_input("メッセージを入力..."):
                        st.session_state.messages.append({"role": "user", "content": prompt})
                        with st.chat_message("user"):
                            st.write(prompt)
                        
                        response = get_assistant_response(prompt)
                        st.session_state.messages.append({"role": "assistant", "content": response})
                        with st.chat_message("assistant"):
                            st.write(response)
        except (FileNotFoundError, pd.errors.EmptyDataError):
            st.warning("⚠️ 利用するには、まず「事前登録」タブでユーザーを登録してください。")

    # --- Tab4: 多摩地域情報 ---
    with tab4:
        st.markdown("## 📍 多摩地域観光情報")
        st.markdown("東京都オープンデータを活用した、リアルタイム観光情報をお届けします。")
        show_tama_info()

if __name__ == "__main__":
    main()
