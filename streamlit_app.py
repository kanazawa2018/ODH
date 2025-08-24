import streamlit as st
import pandas as pd
import random
import os
import math
import json
import datetime
from typing import Dict, List, Tuple

# --- 定数定義 ---
USER_DATA_FILE = 'tmp/users.csv'
CHAR_INFO_FILE = 'tmp/キャラ情報.csv'
ROUTE_DATA_FILE = 'tmp/周遊ルート.csv'
CHAR_IMAGE_DIR = 'tmp/キャラ画像'
EVENT_DATA_FILE = 'tmp/tama_events.json'  # 多摩地域イベント情報

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

# --- デモ用サンプルデータ（既存データがない場合のフォールバック） ---
SAMPLE_USERS_DATA = """name,gender,age_group,hobbies,pref_age_group,pref_hobbies,animal,group_id,route_no
えりか,女性,30代前半,"美術館巡り, 映画鑑賞","30代後半, 20代後半","映画鑑賞, 旅行",チーター,1,4
まこと,男性,20代後半,"読書, 歴史探訪","20代前半, 20代後半","読書, 映画鑑賞, 美術館巡り, 歴史探訪",チーター,1,4
みほ,女性,40代,"読書, 美術館巡り","30代前半, 30代後半","音楽鑑賞, 美術館巡り",アカカンガルー,1,4
りな,女性,30代前半,"アウトドア, カメラ","20代後半, 30代前半","アウトドア, カメラ",タスマニアデビル,1,4
さくら,男性,20代前半,"読書, 料理","20代前半, 20代後半","読書, 旅行",コアラ,2,5
しょうた,男性,30代前半,"ゲーム, カメラ","30代前半, 30代後半","映画鑑賞, 旅行",インドサイ,2,5
たくや,男性,20代前半,"アウトドア, 旅行","20代前半, 20代後半","スポーツ, キャンプ",インドサイ,2,5
まい,女性,20代後半,"音楽鑑賞, スポーツ","30代前半, 30代後半, 40代","スポーツ, 映画鑑賞",アカカンガルー,2,5"""

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
1,Safari ✕ 花畑ピクニック,12:00,多摩動物公園正門前→園内ラリー→モノレール→昭和記念公園ピクニック,入園600円+モノレール310円+公園450円,写真を見せ合いながらトーク・４人１組ゲーム,4時間15分,3000円
2,レトロ建築スタンプラリー,9:30,江戸東京たてもの園でスタンプラリー→昭和の居間体験→伝統玩具ワークショップ,モノレール・JR・バス片道750円+入園400円,20分毎にチーム替え・作品交換タイム,5時間20分,3500円
3,深大寺そば打ち Love クッキング,11:00,深大寺おみくじ→そば打ち体験→神代植物公園バラ園ツアー,京王線・バス片道490円+体験2000円+入園500円,共同作業で距離縮まる・花言葉トーク,5時間,4500円
4,府中 歴史＆ホースバックヤードツアー,10:00,府中市郷土の森→謎解き脱出ゲーム→東京競馬場バックヤード見学,交通費740円+入園300円+見学200円,５人１組で協力・競走馬の名前ビンゴ,5時間10分,4000円
5,高尾山 サンセット・ケーブル Love Walk,13:00,ケーブルカーで中腹→ペアトレッキング→山頂カフェ→駅前足湯,京王線300円+ケーブル960円+足湯500円,山恋フォトミッション・目隠し足湯Q&A,4時間,4000円"""

# --- 初期設定: 必要なファイルやディレクトリが存在しない場合に作成 ---
def setup_files():
    """
    アプリ実行に必要なユーザーデータファイルやディレクトリを初期作成する。
    デモ用のため、サンプルデータを使用してファイルが作成されるよう修正。
    """
    # ディレクトリ作成
    os.makedirs(os.path.dirname(USER_DATA_FILE), exist_ok=True)
    os.makedirs(os.path.dirname(CHAR_INFO_FILE), exist_ok=True)
    os.makedirs(os.path.dirname(ROUTE_DATA_FILE), exist_ok=True)
    os.makedirs(CHAR_IMAGE_DIR, exist_ok=True)
    
    # ユーザー情報CSV - デモ用にサンプルデータを作成
    if not os.path.exists(USER_DATA_FILE):
        try:
            with open(USER_DATA_FILE, 'w', encoding='utf-8') as f:
                f.write(SAMPLE_USERS_DATA)
        except Exception as e:
            st.error(f"ユーザーデータファイルの作成に失敗しました: {e}")
    
    # キャラ情報CSV - デモ用にサンプルデータを作成
    if not os.path.exists(CHAR_INFO_FILE):
        try:
            with open(CHAR_INFO_FILE, 'w', encoding='utf-8') as f:
                f.write(SAMPLE_CHAR_DATA)
        except Exception as e:
            st.error(f"キャラ情報ファイルの作成に失敗しました: {e}")
    
    # 周遊ルートCSV - デモ用にサンプルデータを作成
    if not os.path.exists(ROUTE_DATA_FILE):
        try:
            with open(ROUTE_DATA_FILE, 'w', encoding='utf-8') as f:
                f.write(SAMPLE_ROUTE_DATA)
        except Exception as e:
            st.error(f"周遊ルートファイルの作成に失敗しました: {e}")
    
    # 多摩地域イベント情報の作成
    if not os.path.exists(EVENT_DATA_FILE):
        try:
            sample_events = {
                "seasonal_events": [
                    {"month": 1, "event": "🎍 多摩センター新春イルミネーション", "crowd_level": 3, 
                     "description": "100万球のLEDが織りなす幻想的な光の世界。カップルに大人気！"},
                    {"month": 2, "event": "🌸 高尾山梅まつり", "crowd_level": 2,
                     "description": "約1000本の紅白の梅が咲き誇る。甘酒の振る舞いもあり♪"},
                    {"month": 3, "event": "🌸 小金井公園桜まつり", "crowd_level": 5,
                     "description": "都内屈指の桜の名所！50種1700本の桜が見事です"},
                ]
            }
            with open(EVENT_DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump(sample_events, f, ensure_ascii=False, indent=2)
        except Exception as e:
            pass

# --- 動物の絵文字マッピング ---
ANIMAL_EMOJI_MAP = {
    'コアラ': '🐨',
    'インドサイ': '🦏',
    'ライオン': '🦁',
    'チーター': '🐆',
    'オラウータン': '🦧',
    'カピバラ': '🦫',
    'タイリクオオカミ': '🐺',
    'コツメカワウソ': '🦦',
    'モウコノウマ': '🐴',
    'ワライカワセミ': '🦜',
    'タスマニアデビル': '😈',
    'アカカンガルー': '🦘'
}

def get_animal_emoji(animal_name):
    """動物名から絵文字を取得"""
    return ANIMAL_EMOJI_MAP.get(animal_name, '🦊')

# --- モダンなスタイル定義 ---
def apply_modern_style():
    """
    東京都らしい信頼感と若者向けのモダンさを両立させたデザインを適用
    """
    st.markdown(f"""
    <style>
        /* メインアプリケーションの背景 */
        .stApp {{
            background: linear-gradient(135deg, {COLORS['light']} 0%, #E3F2FD 100%);
        }}
        
        /* ヘッダースタイル */
        .main-header {{
            background: linear-gradient(90deg, {COLORS['primary']} 0%, {COLORS['gradient_start']} 100%);
            color: white;
            padding: 2rem;
            border-radius: 20px;
            margin-bottom: 2rem;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            text-align: center;
        }}
        
        .main-header h1 {{
            font-size: 2.5rem;
            font-weight: 800;
            margin: 0;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }}
        
        /* アニマルカード */
        .animal-card {{
            background: linear-gradient(135deg, #fff 0%, #f8f9fa 100%);
            border: 2px solid {COLORS['primary']};
            border-radius: 20px;
            padding: 1.5rem;
            text-align: center;
            box-shadow: 0 8px 25px rgba(0,0,0,0.1);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }}
        
        .animal-name {{
            font-size: 1.8rem;
            font-weight: 700;
            color: {COLORS['primary']};
            margin: 1rem 0;
        }}
        
        /* グループメンバーカード */
        .member-card {{
            background: white;
            border-radius: 12px;
            padding: 1rem;
            margin: 0.5rem 0;
            display: flex;
            align-items: center;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            transition: all 0.2s ease;
        }}
        
        .member-animal {{
            font-size: 2rem;
            margin-right: 1rem;
        }}
        
        /* チャット用CSS */
        .chat-row {{
            display: flex;
            align-items: flex-start;
            margin-bottom: 1.5rem;
        }}
        
        .avatar-container {{
            width: 8rem;
            flex-shrink: 0;
            text-align: center;
            margin-right: 1rem;
        }}
        
        .avatar-container img {{
            width: 8rem;
            height: 8rem;
            border-radius: 10px;
        }}
        
        .avatar-container .char-name {{
            font-weight: bold;
            margin-top: 0.5rem;
            font-size: 0.9rem;
        }}
        
        .message-bubble {{
            padding: 1rem;
            border-radius: 10px;
            background-color: #f0f2f6;
            word-wrap: break-word;
            width: 100%;
        }}
        
        .user-message .message-bubble {{
            background-color: #dcf8c6;
        }}
        
        .user-message .avatar-container {{
            margin-left: 1rem;
            margin-right: 0;
        }}
        
        .user-message {{
            justify-content: flex-end;
        }}
    </style>
    """, unsafe_allow_html=True)

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
        return 'コアラ'

# --- Step.2 の関数 ---
def assign_groups_and_routes(users_df, routes_df):
    """
    ユーザーをグループ分けし、各グループに周遊ルートを割り当てる。
    """
    group_size = 4
    all_users_shuffled = users_df.sample(frac=1).reset_index(drop=True)
    num_groups = math.ceil(len(users_df) / group_size)
    
    # グループ割り当て
    for i, row in all_users_shuffled.iterrows():
        original_index = users_df[users_df['name'] == row['name']].index[0]
        users_df.loc[original_index, 'group_id'] = (i % num_groups) + 1
    
    # ルート割り当て - 周遊ルートNo.の型を統一
    try:
        # 周遊ルートNo.を数値型に変換
        routes_df['周遊ルートNo.'] = pd.to_numeric(routes_df['周遊ルートNo.'], errors='coerce')
        unique_routes = routes_df['周遊ルートNo.'].dropna().unique().tolist()
    except:
        unique_routes = [1, 2, 3, 4, 5]  # フォールバック
    
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
    """
    AIアシスタント機能：街コンでの会話をサポート
    """
    responses = {
        "緊張": "深呼吸してリラックス！😊 まずは相手の動物キャラクターについて聞いてみるのはどうでしょう？「○○さんは何の動物になったんですか？」から始めると自然ですよ。",
        "話": "プロフィールカードを見て共通点を探してみましょう！多摩地域のおすすめスポットについて話すのも盛り上がりますよ。「高尾山行ったことありますか？」とか！",
        "沈黙": "周りの景色について話してみましょう！「この辺は初めて来ました」「いいお店ありそうですね」など、場所の話題は続きやすいです。",
        "ありがとう": "どういたしまして！楽しい街コンになりますように！何か困ったらいつでも聞いてくださいね😊",
    }
    
    # キーワードマッチング
    for keyword, response in responses.items():
        if keyword in user_input:
            return response
    
    # デフォルトレスポンス
    default_responses = [
        "いいですね！その調子で楽しんでください😊",
        "素敵な出会いになるといいですね！応援してます✨",
        "リラックスして自然体でいきましょう！きっと上手くいきますよ。",
        "何かお手伝いできることがあれば言ってくださいね！"
    ]
    return random.choice(default_responses)

# --- ユーザー統計情報 ---
def show_user_stats():
    """
    登録ユーザーの統計情報を表示（ダッシュボード機能）
    """
    try:
        users_df = pd.read_csv(USER_DATA_FILE)
        if len(users_df) > 0:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("👥 登録者数", f"{len(users_df)}名")
            
            with col2:
                male_count = len(users_df[users_df['gender'] == '男性'])
                female_count = len(users_df[users_df['gender'] == '女性'])
                st.metric("⚖️ 男女比", f"{male_count}:{female_count}")
            
            with col3:
                avg_groups = users_df['group_id'].nunique()
                st.metric("👫 グループ数", f"{avg_groups}組")
            
            with col4:
                # 人気の動物キャラクター
                if 'animal' in users_df.columns and not users_df['animal'].empty:
                    popular_animal = users_df['animal'].mode().iloc[0] if len(users_df['animal'].mode()) > 0 else "未定"
                    st.metric("🏆 人気キャラ", popular_animal)
                else:
                    st.metric("🏆 人気キャラ", "未定")
    except (FileNotFoundError, pd.errors.EmptyDataError):
        # ファイルが存在しない場合は初期値を表示
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("👥 登録者数", "0名")
        with col2:
            st.metric("⚖️ 男女比", "0:0")
        with col3:
            st.metric("👫 グループ数", "0組")
        with col4:
            st.metric("🏆 人気キャラ", "未定")

# --- Streamlit アプリ本体 ---
def main():
    """
    メインアプリケーション
    """
    # ページ設定
    st.set_page_config(
        page_title="アニマル縁結び🦊 - 多摩地域街コンアプリ",
        page_icon="🦊",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    # 初期設定（デモ用データを含む）
    setup_files()
    
    # スタイル適用
    apply_modern_style()
    
    # ヘッダー
    st.markdown("""
    <div class="main-header">
        <h1>🦊 アニマル縁結び 🦊</h1>
        <p>多摩地域で素敵な出会いを ～ 東京都オープンデータ活用街コンアプリ ～</p>
    </div>
    """, unsafe_allow_html=True)
    
    # デモ用の注意書き
    st.info("🎬 **デモモード**: このアプリではサンプルデータを使用しています。実際のデータファイル（users.csv, キャラ情報.csv, 周遊ルート.csv）がtmpフォルダに存在する場合は、そちらのデータを優先して表示します。")
    
    # ユーザー統計を表示
    show_user_stats()
    
    # タブ設定
    tab1, tab2, tab3 = st.tabs([
        "📝 Step.1: 事前登録",
        "👥 Step.2: グループ編成・ルート確認",
        "💬 Step.3: 当日用チャット"
    ])
    
    # --- Tab1: 事前登録 ---
    with tab1:
        st.header("ユーザー情報登録")
        st.info("💡 デモモードでは既にユーザーが登録されています。新規ユーザーを追加することも可能です。")
        
        # 既存のユーザー一覧を表示
        try:
            existing_users_df = pd.read_csv(USER_DATA_FILE)
            if len(existing_users_df) > 0:
                st.subheader("📋 現在の登録ユーザー")
                display_df = existing_users_df[['name', 'gender', 'age_group', 'animal']].copy()
                display_df.columns = ['ニックネーム', '性別', '年代', '動物キャラクター']
                st.dataframe(display_df, use_container_width=True)
                st.write(f"合計 {len(existing_users_df)} 名が登録済み")
        except:
            st.warning("⚠️ ユーザーデータの読み込みに失敗しました。")
        
        gender_options = ['男性', '女性']
        age_options = ['20代前半', '20代後半', '30代前半', '30代後半', '40代', '50代']
        hobby_options = [
            'アウトドア', 'スポーツ', '旅行', 'キャンプ', '読書', '映画鑑賞', 'ゲーム',
            '料理', '美術館巡り', '音楽鑑賞', 'カメラ', '歴史探訪'
        ]
        
        with st.form("registration_form"):
            st.subheader("🆕 新規ユーザー登録")
            name = st.text_input("ニックネーム", placeholder="例: たまちゃん")
            gender = st.selectbox("性別", gender_options)
            age_group = st.selectbox("年代", age_options)
            hobbies = st.multiselect("趣味（複数選択可）", hobby_options)
            
            st.subheader("💝 お相手に求める条件")
            pref_age_group = st.multiselect("希望する年代", age_options)
            pref_hobbies = st.multiselect("希望する趣味", hobby_options)
            
            submitted = st.form_submit_button("🎊 登録してキャラクターを受け取る")
        
        if submitted:
            if not name:
                st.error("⚠️ ニックネームを入力してください。")
            elif not hobbies:
                st.error("⚠️ 趣味を1つ以上選択してください。")
            else:
                try:
                    # キャラクター情報読み込み
                    char_df = pd.read_csv(CHAR_INFO_FILE)
                    if '動物' not in char_df.columns or char_df.empty:
                        st.error(f"'{CHAR_INFO_FILE}' が正しくないか、空です。")
                        st.stop()
                    
                    # 動物キャラクター割り当て
                    animal = assign_animal(char_df)
                    
                    # 新規ユーザー作成
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
                    
                    # 既存データと結合
                    users_df = pd.read_csv(USER_DATA_FILE)
                    if name in users_df['name'].values:
                        st.error("⚠️ そのニックネームは既に使用されています。")
                    else:
                        updated_users_df = pd.concat([users_df, new_user], ignore_index=True)
                        updated_users_df.to_csv(USER_DATA_FILE, index=False)
                        
                        st.success(f"✨ {name}さん、登録が完了しました！")
                        
                        # 動物キャラクター表示
                        animal_emoji = get_animal_emoji(animal)
                        st.markdown(f"""
                        <div class="animal-card">
                            <div style="font-size: 5rem;">{animal_emoji}</div>
                            <div class="animal-name">あなたは「{animal}」タイプです！</div>
                            <p>このキャラクターが街コンでのあなたの相棒になります。</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # ページリロード
                        st.rerun()
                        
                except FileNotFoundError:
                    st.error(f"⚠️ '{CHAR_INFO_FILE}' が見つかりません。")
                except Exception as e:
                    st.error(f"⚠️ エラーが発生しました: {str(e)}")
    
    # --- Tab2: グループ編成・ルート確認 ---
    with tab2:
        st.header("グループと周遊ルートの確認")
        
        # 既存データの確認表示
        try:
            users_df = pd.read_csv(USER_DATA_FILE)
            routes_df = pd.read_csv(ROUTE_DATA_FILE)
            char_df = pd.read_csv(CHAR_INFO_FILE)
            
            st.info(f"現在の登録者数: {len(users_df)}名")
            
            # デモ用の説明
            st.success("📋 デモ用データが読み込まれています。既にグループ分けとルート割り当てが完了済みです。")
            
            # グループ編成ボタン（デモ用に再編成可能にする）
            if st.button("🔄 グループを再編成する（デモ用）"):
                users_with_groups_df = assign_groups_and_routes(users_df, routes_df)
                users_with_groups_df.to_csv(USER_DATA_FILE, index=False)
                st.success("✅ グループが再編成されました！")
                st.rerun()
            
            # 既存のグループ情報を表示
            if 'group_id' in users_df.columns and users_df['group_id'].max() > 0:
                num_groups = int(users_df['group_id'].max())
                
                st.markdown("---")
                st.subheader(f"📋 現在のグループ編成（{num_groups}グループ）")
                
                for group_id in range(1, num_groups + 1):
                    group_members = users_df[users_df['group_id'] == group_id]
                    
                    if len(group_members) > 0:
                        # ルート情報を先に取得
                        assigned_route_no = group_members['route_no'].iloc[0]
                        route_info = routes_df[routes_df['周遊ルートNo.'] == assigned_route_no]
                        route_name = route_info['コース名'].iloc[0] if not route_info.empty else "未定"
                        
                        with st.expander(f"👥 グループ {group_id} - {len(group_members)}名 - {route_name}", expanded=True):
                            
                            # メンバー情報を画像付きで表示
                            st.markdown("### 👥 グループメンバー")
                            
                            cols = st.columns(len(group_members))
                            for idx, (_, member) in enumerate(group_members.iterrows()):
                                with cols[idx]:
                                    # キャラクター画像を表示
                                    char_info = char_df[char_df['動物'] == member['animal']]
                                    if not char_info.empty:
                                        char_name = char_info['キャラクター名'].iloc[0]
                                        image_path = os.path.join(CHAR_IMAGE_DIR, f"{char_name}.jpg")
                                        
                                        # 画像が存在する場合は表示
                                        if os.path.exists(image_path):
                                            st.image(image_path, width=100)
                                        else:
                                            st.markdown(f"<div style='font-size: 4rem; text-align: center;'>🎭</div>", unsafe_allow_html=True)
                                        
                                        st.markdown(f"""
                                        **{member['name']}**  
                                        {member['gender']} / {member['age_group']}  
                                        🎭 {member['animal']} ({char_name})  
                                        🎯 {member['hobbies'][:20]}...
                                        """)
                                    else:
                                        st.markdown(f"""
                                        **{member['name']}**  
                                        {member['gender']} / {member['age_group']}  
                                        🎭 {member['animal']}  
                                        🎯 {member['hobbies'][:20]}...
                                        """)
                            
                            # 相性分析（簡易版）
                            st.markdown("### 💕 グループ相性分析")
                            hobbies_list = []
                            for _, member in group_members.iterrows():
                                member_hobbies = [h.strip() for h in member['hobbies'].split(',')]
                                hobbies_list.extend(member_hobbies)
                            
                            # 共通趣味をカウント
                            from collections import Counter
                            hobby_counts = Counter(hobbies_list)
                            common_hobbies = [hobby for hobby, count in hobby_counts.items() if count > 1]
                            
                            if common_hobbies:
                                st.success(f"🎉 共通の趣味: {', '.join(common_hobbies)}")
                            else:
                                st.info("🌟 多様な趣味で新しい発見がありそうです！")
                            
                            # 年代バランス
                            ages = group_members['age_group'].unique()
                            st.info(f"📊 年代構成: {', '.join(ages)}")
                            
                            # 周遊プラン詳細表示
                            st.markdown("### 🗺️ 周遊プラン詳細")
                            
                            if not route_info.empty:
                                route_details = route_info.iloc[0]
                                
                                # ルートのヘッダー情報
                                col1, col2, col3 = st.columns(3)
                                with col1:
                                    st.metric("⏰ 所要時間", route_details['所要時間'])
                                with col2:
                                    st.metric("💰 参加費", route_details['参加費'])
                                with col3:
                                    st.metric("🕐 開始時間", route_details['時間'])
                                
                                # 詳細情報をタブで整理
                                tab_schedule, tab_transport, tab_interaction = st.tabs(["📍 行程", "🚃 交通", "💬 交流"])
                                
                                with tab_schedule:
                                    st.markdown("**📍 行程・内容:**")
                                    st.write(route_details['行程・内容'])
                                
                                with tab_transport:
                                    st.markdown("**🚃 交通・費用:**")
                                    st.write(route_details['交通・費用'])
                                
                                with tab_interaction:
                                    st.markdown("**💬 交流ポイント:**")
                                    st.write(route_details['交流ポイント'])
                                    
                                    # おすすめ会話トピック（自動生成）
                                    st.markdown("**💡 おすすめ会話トピック:**")
                                    topics = [
                                        "今日のルートで一番楽しみにしている場所",
                                        "普段の休日の過ごし方",
                                        "多摩地域のお気に入りスポット",
                                        f"「{route_details['コース名']}」の感想"
                                    ]
                                    for topic in topics:
                                        st.write(f"• {topic}")
                            else:
                                st.warning(f"⚠️ ルートNo.{int(assigned_route_no)} の詳細情報が見つかりません。")
            else:
                st.warning("⚠️ グループ分けがまだ行われていません。")
                
        except FileNotFoundError as e:
            st.error(f"⚠️ 必要なファイルが見つかりません: {e}")
            st.info("CSVファイルが正しく配置されているか確認してください。")
        except Exception as e:
            st.error(f"⚠️ データの読み込みエラー: {e}")
    
    # --- Tab3: 当日用チャット ---
    with tab3:
        st.header("🤖 AIアシスタントチャット")
        st.info("街コンでの振る舞いや会話に困ったら、アシスタントに相談してみましょう！")
        
        try:
            users_df = pd.read_csv(USER_DATA_FILE)
            char_df = pd.read_csv(CHAR_INFO_FILE)
            
            if len(users_df) > 0:
                # ユーザー選択
                user_name = st.selectbox(
                    "あなたのニックネームを選択してください", 
                    options=['選択してください...'] + list(users_df['name'].unique()),
                    index=0
                )
                
                if user_name != '選択してください...':
                    user_info = users_df[users_df['name'] == user_name].iloc[0]
                    user_animal = user_info['animal']
                    
                    # アシスタントキャラクター情報を取得
                    assistant_avatar_path = None
                    assistant_char_name = user_animal
                    
                    char_info_row = char_df[char_df['動物'] == user_animal]
                    if not char_info_row.empty:
                        assistant_char_name = char_info_row['キャラクター名'].iloc[0]
                        # 複数の画像形式に対応
                        for ext in ['jpg', 'jpeg', 'png', 'gif']:
                            image_path = os.path.join(CHAR_IMAGE_DIR, f"{assistant_char_name}.{ext}")
                            if os.path.exists(image_path):
                                assistant_avatar_path = image_path
                                break
                    
                    # ユーザー情報表示
                    col1, col2 = st.columns([1, 3])
                    with col1:
                        if assistant_avatar_path:
                            st.image(assistant_avatar_path, width=120)
                        else:
                            st.markdown("<div style='font-size: 6rem; text-align: center;'>🎭</div>", unsafe_allow_html=True)
                        st.markdown(f"**{user_name}**")
                        st.markdown(f"🎭 {user_animal}")
                        st.markdown(f"✨ {assistant_char_name}")
                    
                    with col2:
                        st.markdown(f"### こんにちは、{user_name}さん！")
                        st.markdown(f"あなたのパートナー「**{assistant_char_name}**」がサポートします 🎉")
                        
                        # グループ情報も表示
                        if 'group_id' in user_info and user_info['group_id'] > 0:
                            st.info(f"👥 あなたはグループ {int(user_info['group_id'])} のメンバーです")
                    
                    # チャット履歴の初期化
                    if "messages" not in st.session_state:
                        st.session_state.messages = []
                        # ウェルカムメッセージ
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": f"こんにちは、{user_name}さん！🎉\n私は{assistant_char_name}です。街コンでの会話や行動について、何でも気軽に相談してくださいね！",
                            "avatar_path": assistant_avatar_path,
                            "char_name": assistant_char_name
                        })
                    
                    # チャット履歴の表示
                    for msg in st.session_state.messages:
                        if msg["role"] == "assistant":
                            # アシスタントメッセージ
                            st.markdown('<div class="chat-row">', unsafe_allow_html=True)
                            col1, col2 = st.columns([1, 4])
                            with col1:
                                st.markdown('<div class="avatar-container">', unsafe_allow_html=True)
                                if msg.get("avatar_path") and os.path.exists(msg.get("avatar_path")):
                                    st.image(msg["avatar_path"], width=80)
                                else:
                                    st.markdown("<div style='font-size: 4rem; text-align: center;'>🤖</div>", unsafe_allow_html=True)
                                st.markdown(f'<div class="char-name">{msg["char_name"]}</div>', unsafe_allow_html=True)
                                st.markdown('</div>', unsafe_allow_html=True)
                            with col2:
                                st.markdown(f'<div class="message-bubble">{msg["content"]}</div>', unsafe_allow_html=True)
                            st.markdown('</div>', unsafe_allow_html=True)
                        else:
                            # ユーザーメッセージ
                            st.markdown('<div class="chat-row user-message">', unsafe_allow_html=True)
                            col1, col2 = st.columns([4, 1])
                            with col1:
                                st.markdown(f'<div class="message-bubble">{msg["content"]}</div>', unsafe_allow_html=True)
                            with col2:
                                st.markdown('<div class="avatar-container">', unsafe_allow_html=True)
                                st.markdown("<div style='font-size: 4rem; text-align: center;'>👤</div>", unsafe_allow_html=True)
                                st.markdown(f'<div class="char-name">{user_name}</div>', unsafe_allow_html=True)
                                st.markdown('</div>', unsafe_allow_html=True)
                            st.markdown('</div>', unsafe_allow_html=True)
                    
                    # クイックアクションボタン
                    st.markdown("### 💡 クイックヘルプ")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        if st.button("😰 緊張しています"):
                            quick_response = get_assistant_response("緊張")
                            st.session_state.messages.append({
                                "role": "assistant",
                                "content": quick_response,
                                "avatar_path": assistant_avatar_path,
                                "char_name": assistant_char_name
                            })
                            st.rerun()
                    
                    with col2:
                        if st.button("🗣️ 話題に困った"):
                            quick_response = get_assistant_response("話")
                            st.session_state.messages.append({
                                "role": "assistant",
                                "content": quick_response,
                                "avatar_path": assistant_avatar_path,
                                "char_name": assistant_char_name
                            })
                            st.rerun()
                    
                    with col3:
                        if st.button("🤐 沈黙が気まずい"):
                            quick_response = get_assistant_response("沈黙")
                            st.session_state.messages.append({
                                "role": "assistant",
                                "content": quick_response,
                                "avatar_path": assistant_avatar_path,
                                "char_name": assistant_char_name
                            })
                            st.rerun()
                    
                    # チャット入力
                    if prompt := st.chat_input("アシスタントにメッセージを送る"):
                        # ユーザーメッセージを追加
                        st.session_state.messages.append({
                            "role": "user", 
                            "content": prompt
                        })
                        
                        # アシスタントの応答を生成
                        response = get_assistant_response(prompt)
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": response,
                            "avatar_path": assistant_avatar_path,
                            "char_name": assistant_char_name
                        })
                        st.rerun()
                else:
                    st.info("👆 上のセレクトボックスからあなたのニックネームを選択してください。")
            else:
                st.warning("⚠️ 利用するには、まず「事前登録」タブでユーザーを登録してください。")
                
        except FileNotFoundError as e:
            st.error(f"⚠️ 必要なファイルが見つかりません: {e}")
        except Exception as e:
            st.error(f"⚠️ エラーが発生しました: {e}")
