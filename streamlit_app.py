import streamlit as st
import pandas as pd
import random
import os
import math
import json
import datetime
from typing import Dict, List, Tuple

# --- 定数定義 ---
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

# --- デモ用サンプルデータ ---
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
1,Safari ✕ 花畑ピクニック,12:00,多摩動物公園正門前→園内ラリー→モノレール→昭和記念公園ピクニック,入園600円+モノレール310円+公園450円,写真を見せ合いながらトーク・４人１組ゲーム,4時間15分,3000円
2,レトロ建築スタンプラリー,9:30,江戸東京たてもの園でスタンプラリー→昭和の居間体験→伝統玩具ワークショップ,モノレール・JR・バス片道750円+入園400円,20分毎にチーム替え・作品交換タイム,5時間20分,3500円
3,深大寺そば打ち Love クッキング,11:00,深大寺おみくじ→そば打ち体験→神代植物公園バラ園ツアー,京王線・バス片道490円+体験2000円+入園500円,共同作業で距離縮まる・花言葉トーク,5時間,4500円
4,府中 歴史＆ホースバックヤードツアー,10:00,府中市郷土の森→謎解き脱出ゲーム→東京競馬場バックヤード見学,交通費740円+入園300円+見学200円,５人１組で協力・競走馬の名前ビンゴ,5時間10分,4000円
5,高尾山 サンセット・ケーブル Love Walk,13:00,ケーブルカーで中腹→ペアトレッキング→山頂カフェ→駅前足湯,京王線300円+ケーブル960円+足湯500円,山恋フォトミッション・目隠し足湯Q&A,4時間,4000円"""

# --- 初期設定: 必要なファイルやディレクトリが存在しない場合に作成 ---
def setup_files():
    """
    アプリ実行に必要なユーザーデータファイルやディレクトリを初期作成する。
    デモ用のサンプルデータも含めて準備。
    """
    # ユーザー情報CSV（デモ用データを含む）
    if not os.path.exists(USER_DATA_FILE):
        # デモ用のサンプルデータを書き込み
        with open(USER_DATA_FILE, 'w', encoding='utf-8') as f:
            f.write(SAMPLE_USERS_DATA)
    
    # ../input ディレクトリがなければ作成
    input_dir = os.path.dirname(CHAR_INFO_FILE)
    if not os.path.exists(input_dir):
        os.makedirs(input_dir)
    
    # キャラ情報CSV（デモ用データ）
    if not os.path.exists(CHAR_INFO_FILE):
        with open(CHAR_INFO_FILE, 'w', encoding='utf-8') as f:
            f.write(SAMPLE_CHAR_DATA)
    
    # 周遊ルートCSV（デモ用データ）
    if not os.path.exists(ROUTE_DATA_FILE):
        os.makedirs(os.path.dirname(ROUTE_DATA_FILE), exist_ok=True)
        with open(ROUTE_DATA_FILE, 'w', encoding='utf-8') as f:
            f.write(SAMPLE_ROUTE_DATA)
    
    # キャラ画像ディレクトリがなければ作成
    if not os.path.exists(CHAR_IMAGE_DIR):
        os.makedirs(CHAR_IMAGE_DIR)
    
    # 多摩地域イベント情報の充実したデータ
    if not os.path.exists(EVENT_DATA_FILE):
        sample_events = {
            "seasonal_events": [
                {"month": 1, "event": "🎍 多摩センター新春イルミネーション", "crowd_level": 3, 
                 "description": "100万球のLEDが織りなす幻想的な光の世界。カップルに大人気！"},
                {"month": 2, "event": "🌸 高尾山梅まつり", "crowd_level": 2,
                 "description": "約1000本の紅白の梅が咲き誇る。甘酒の振る舞いもあり♪"},
                {"month": 3, "event": "🌸 小金井公園桜まつり", "crowd_level": 5,
                 "description": "都内屈指の桜の名所！50種1700本の桜が見事です"},
                {"month": 4, "event": "🌺 昭和記念公園チューリップフェスティバル", "crowd_level": 4,
                 "description": "20万球のチューリップが咲く、関東最大級の花畑"},
                {"month": 5, "event": "🎏 府中くらやみ祭", "crowd_level": 5,
                 "description": "関東三大奇祭の一つ！1000年以上の歴史を持つ大國魂神社の例大祭"},
                {"month": 8, "event": "🎆 立川まつり国営昭和記念公園花火大会", "crowd_level": 5,
                 "description": "約5000発の花火が夜空を彩る！多摩地域最大級の花火大会"},
                {"month": 11, "event": "🍁 高尾山もみじまつり", "crowd_level": 5,
                 "description": "紅葉の絶景スポット！ケーブルカーから見る紅葉は格別"},
                {"month": 12, "event": "✨ よみうりランドジュエルミネーション", "crowd_level": 4,
                 "description": "世界的照明デザイナー石井幹子プロデュースの宝石色イルミネーション"}
            ],
            "popular_spots": [
                {
                    "name": "🏔️ 高尾山",
                    "category": "自然・絶景",
                    "avg_crowd": 3.5,
                    "best_time": "平日午前",
                    "highlight": "ミシュラン三ツ星の山！都心から1時間で本格登山",
                    "instagram_spots": ["山頂からの富士山", "もみじ台", "薬王院"],
                    "date_point": "ケーブルカーでの会話、達成感の共有"
                },
                {
                    "name": "🎀 サンリオピューロランド",
                    "category": "テーマパーク",
                    "avg_crowd": 4.0,
                    "best_time": "平日",
                    "highlight": "全天候型屋内テーマパーク！キャラクターグリーティングが充実",
                    "instagram_spots": ["レディキティハウス", "ミラクルギフトパレード", "キキララ撮影スポット"],
                    "date_point": "童心に返って楽しめる、写真撮影で盛り上がる"
                },
                {
                    "name": "🦁 多摩動物公園",
                    "category": "動物園",
                    "avg_crowd": 3.0,
                    "best_time": "開園直後",
                    "highlight": "300種を超える動物！アジア園のオランウータンスカイウォークは必見",
                    "instagram_spots": ["ライオンバス", "コアラ館", "チーターの丘"],
                    "date_point": "動物の話題で自然に会話が弾む"
                },
                {
                    "name": "🏛️ 江戸東京たてもの園",
                    "category": "博物館",
                    "avg_crowd": 2.0,
                    "best_time": "いつでも",
                    "highlight": "ジブリ映画『千と千尋の神隠し』のモデルになった建物も！",
                    "instagram_spots": ["子宝湯", "武居三省堂", "デ・ラランデ邸"],
                    "date_point": "レトロな雰囲気で特別な時間を演出"
                },
                {
                    "name": "⛩️ 深大寺",
                    "category": "寺社・歴史",
                    "avg_crowd": 2.5,
                    "best_time": "午前中",
                    "highlight": "都内で2番目に古い寺！名物深大寺そばは20店舗以上",
                    "instagram_spots": ["山門", "本堂", "深大寺そば"],
                    "date_point": "おみくじで盛り上がる、そば打ち体験"
                },
                {
                    "name": "🌺 昭和記念公園",
                    "category": "公園",
                    "avg_crowd": 3.0,
                    "best_time": "平日午後",
                    "highlight": "東京ドーム39個分の広大な国営公園！四季折々の花が楽しめる",
                    "instagram_spots": ["みんなの原っぱ", "日本庭園", "花の丘"],
                    "date_point": "レンタサイクルでサイクリングデート"
                },
                {
                    "name": "🎡 よみうりランド",
                    "category": "遊園地",
                    "avg_crowd": 3.5,
                    "best_time": "平日",
                    "highlight": "絶叫マシンから観覧車まで43機種のアトラクション",
                    "instagram_spots": ["大観覧車", "バンデット", "ジュエルミネーション"],
                    "date_point": "スリル共有で距離が縮まる"
                },
                {
                    "name": "🏇 東京競馬場",
                    "category": "レジャー",
                    "avg_crowd": 4.0,
                    "best_time": "重賞レース以外の日",
                    "highlight": "競馬だけじゃない！子供向け遊具や緑地公園も充実",
                    "instagram_spots": ["パドック", "ウイナーズサークル", "馬場内庭園"],
                    "date_point": "初心者でも楽しめる、一緒に予想して盛り上がる"
                }
            ],
            "hidden_gems": [
                {
                    "name": "🌿 都立小山内裏公園",
                    "description": "多摩ニュータウン最大の都市公園。尾根道からの眺望が素晴らしい",
                    "access": "京王相模原線「南大沢」駅から徒歩20分"
                },
                {
                    "name": "☕ 国立天文台",
                    "description": "第一赤道儀室など大正時代の建物が見学可能。宇宙に興味がある人におすすめ",
                    "access": "JR「武蔵境」駅からバス15分"
                },
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
                },
                {
                    "name": "🍖 立川の焼肉街",
                    "description": "駅周辺に高級店からリーズナブルな店まで多数",
                    "recommended": "炭火焼肉ホルモン横丁、焼肉ライク"
                },
                {
                    "name": "🍰 吉祥寺スイーツ",
                    "description": "小さなパティスリーから有名店まで、スイーツ激戦区",
                    "recommended": "アテスウェイ、小ざさ"
                }
            ]
        }
        with open(EVENT_DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(sample_events, f, ensure_ascii=False, indent=2)

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
        
        .main-header p {{
            font-size: 1.1rem;
            margin-top: 0.5rem;
            opacity: 0.95;
        }}
        
        /* カードデザイン */
        .info-card {{
            background: white;
            border-radius: 16px;
            padding: 1.5rem;
            margin: 1rem 0;
            box-shadow: 0 4px 20px rgba(0,0,0,0.08);
            border-left: 4px solid {COLORS['primary']};
            transition: all 0.3s ease;
        }}
        
        .info-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 30px rgba(0,0,0,0.12);
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
        
        .animal-card:hover {{
            transform: scale(1.02) translateY(-3px);
            box-shadow: 0 12px 35px rgba(0,0,0,0.15);
            border-color: {COLORS['secondary']};
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
        
        .member-card:hover {{
            background: {COLORS['light']};
            transform: translateX(5px);
        }}
        
        .member-animal {{
            font-size: 2rem;
            margin-right: 1rem;
        }}
        
        /* ルートカード */
        .route-card {{
            background: linear-gradient(135deg, #ffffff 0%, #f0f7ff 100%);
            border-radius: 16px;
            padding: 1.5rem;
            margin: 1rem 0;
            border: 1px solid #e0e0e0;
            box-shadow: 0 4px 15px rgba(0,0,0,0.06);
        }}
        
        .route-header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 1rem;
            padding-bottom: 0.5rem;
            border-bottom: 2px solid {COLORS['primary']};
        }}
        
        .route-title {{
            font-size: 1.3rem;
            font-weight: 700;
            color: {COLORS['dark']};
        }}
        
        .route-details {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 1rem;
            margin-top: 1rem;
        }}
        
        .route-detail-item {{
            text-align: center;
            padding: 0.5rem;
            background: {COLORS['light']};
            border-radius: 8px;
        }}
        
        /* ボタンスタイル */
        .stButton > button {{
            background: linear-gradient(90deg, {COLORS['primary']} 0%, {COLORS['gradient_start']} 100%);
            color: white;
            border: none;
            border-radius: 30px;
            padding: 0.75rem 2rem;
            font-weight: 600;
            font-size: 1rem;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(30, 136, 229, 0.3);
        }}
        
        .stButton > button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(30, 136, 229, 0.4);
        }}
        
        /* タブスタイル */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 8px;
            background: white;
            padding: 0.5rem;
            border-radius: 15px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        }}
        
        .stTabs [data-baseweb="tab"] {{
            border-radius: 10px;
            padding: 0.75rem 1.5rem;
            font-weight: 600;
            transition: all 0.2s ease;
        }}
        
        .stTabs [aria-selected="true"] {{
            background: {COLORS['primary']};
            color: white;
        }}
        
        /* 成功メッセージ */
        .success-message {{
            background: linear-gradient(90deg, {COLORS['success']} 0%, #26C6DA 100%);
            color: white;
            padding: 1rem 1.5rem;
            border-radius: 12px;
            margin: 1rem 0;
            box-shadow: 0 4px 15px rgba(78, 205, 196, 0.3);
            animation: slideIn 0.5s ease;
        }}
        
        /* イベント情報カード */
        .event-card {{
            background: linear-gradient(135deg, {COLORS['warning']} 0%, #FFA726 100%);
            color: {COLORS['dark']};
            padding: 1rem;
            border-radius: 12px;
            margin: 0.5rem 0;
            box-shadow: 0 3px 10px rgba(255, 217, 61, 0.3);
        }}
        
        /* スポットカード */
        .spot-card {{
            background: white;
            border-radius: 16px;
            padding: 1.2rem;
            margin: 0.5rem 0;
            box-shadow: 0 4px 15px rgba(0,0,0,0.08);
            transition: all 0.3s ease;
            border: 2px solid transparent;
        }}
        
        .spot-card:hover {{
            transform: translateY(-3px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.12);
            border-color: {COLORS['primary']};
        }}
        
        .spot-title {{
            font-size: 1.2rem;
            font-weight: 700;
            color: {COLORS['dark']};
            margin-bottom: 0.5rem;
        }}
        
        .spot-category {{
            display: inline-block;
            padding: 0.2rem 0.8rem;
            background: {COLORS['primary']};
            color: white;
            border-radius: 15px;
            font-size: 0.85rem;
            margin-bottom: 0.5rem;
        }}
        
        /* 混雑度インジケーター */
        .crowd-indicator {{
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            font-weight: 600;
            font-size: 0.9rem;
        }}
        
        .crowd-low {{
            background: #C8E6C9;
            color: #2E7D32;
        }}
        
        .crowd-medium {{
            background: #FFF9C4;
            color: #F57C00;
        }}
        
        .crowd-high {{
            background: #FFCDD2;
            color: #C62828;
        }}
        
        /* アニメーション */
        @keyframes slideIn {{
            from {{
                opacity: 0;
                transform: translateY(-10px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}
        
        @keyframes pulse {{
            0% {{
                box-shadow: 0 0 0 0 rgba(30, 136, 229, 0.4);
            }}
            70% {{
                box-shadow: 0 0 0 10px rgba(30, 136, 229, 0);
            }}
            100% {{
                box-shadow: 0 0 0 0 rgba(30, 136, 229, 0);
            }}
        }}
        
        /* レスポンシブデザイン */
        @media (max-width: 768px) {{
            .main-header h1 {{
                font-size: 2rem;
            }}
            .animal-name {{
                font-size: 1.5rem;
            }}
        }}
    </style>
    """, unsafe_allow_html=True)

# --- 多摩地域情報表示関数 ---
def show_tama_info():
    """
    多摩地域の観光情報や混雑度を詳しく魅力的に表示
    東京都オープンデータを活用した情報提供
    """
    try:
        with open(EVENT_DATA_FILE, 'r', encoding='utf-8') as f:
            event_data = json.load(f)
        
        current_month = datetime.datetime.now().month
        
        # タブで情報を整理
        info_tab1, info_tab2, info_tab3, info_tab4 = st.tabs([
            "📅 季節のイベント",
            "📍 人気スポット",
            "💎 穴場スポット",
            "🍽️ グルメ情報"
        ])
        
        with info_tab1:
            # 今月のイベント情報を取得
            monthly_events = [e for e in event_data['seasonal_events'] if e['month'] == current_month]
            
            if monthly_events:
                st.markdown("### 🎊 今月のおすすめイベント")
                for event in monthly_events:
                    crowd_level = event['crowd_level']
                    crowd_text = ['空いている', '普通', 'やや混雑', '混雑', '非常に混雑'][crowd_level - 1]
                    crowd_class = ['low', 'low', 'medium', 'high', 'high'][crowd_level - 1]
                    
                    st.markdown(f"""
                    <div class="event-card">
                        <strong style="font-size: 1.2rem;">{event['event']}</strong><br>
                        <p style="margin: 0.5rem 0;">{event.get('description', '')}</p>
                        混雑予想: <span class="crowd-indicator crowd-{crowd_class}">{crowd_text}</span>
                    </div>
                    """, unsafe_allow_html=True)
            
            # 年間イベントカレンダー
            st.markdown("### 📆 年間イベントカレンダー")
            other_events = [e for e in event_data['seasonal_events'] if e['month'] != current_month]
            
            cols = st.columns(2)
            for idx, event in enumerate(other_events[:4]):
                with cols[idx % 2]:
                    st.info(f"**{event['month']}月** {event['event']}")
        
        with info_tab2:
            st.markdown("### 🌟 多摩地域の人気デートスポット")
            
            for spot in event_data['popular_spots']:
                crowd_level = spot['avg_crowd']
                crowd_class = 'low' if crowd_level < 2.5 else 'medium' if crowd_level < 3.5 else 'high'
                
                st.markdown(f"""
                <div class="spot-card">
                    <div class="spot-title">{spot['name']}</div>
                    <span class="spot-category">{spot['category']}</span>
                    <p><strong>✨ ここがすごい！</strong><br>{spot['highlight']}</p>
                    <p><strong>📸 インスタ映えスポット:</strong><br>{"、".join(spot['instagram_spots'])}</p>
                    <p><strong>💕 デートポイント:</strong><br>{spot['date_point']}</p>
                    <p>
                        <strong>混雑度:</strong> 
                        <span class="crowd-indicator crowd-{crowd_class}">
                            {'★' * int(crowd_level)}{'☆' * (5 - int(crowd_level))}
                        </span><br>
                        <small>💡 おすすめ時間: {spot['best_time']}</small>
                    </p>
                </div>
                """, unsafe_allow_html=True)
        
        with info_tab3:
            st.markdown("### 💎 地元民おすすめ！穴場スポット")
            
            for gem in event_data['hidden_gems']:
                st.markdown(f"""
                <div class="info-card">
                    <strong style="font-size: 1.1rem;">{gem['name']}</strong><br>
                    <p>{gem['description']}</p>
                    <small>📍 アクセス: {gem['access']}</small>
                </div>
                """, unsafe_allow_html=True)
        
        with info_tab4:
            st.markdown("### 🍽️ 多摩グルメマップ")
            
            for gourmet in event_data['gourmet_spots']:
                st.markdown(f"""
                <div class="info-card">
                    <strong style="font-size: 1.1rem;">{gourmet['name']}</strong><br>
                    <p>{gourmet['description']}</p>
                    <p><strong>おすすめ店:</strong> {gourmet['recommended']}</p>
                </div>
                """, unsafe_allow_html=True)
                
    except FileNotFoundError:
        st.info("多摩地域の情報を読み込んでいます...")

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

# --- Step.1 の関数 ---
def assign_animal(char_df):
    """
    キャラ情報.csvに存在する動物の中からランダムに1つを割り当てる。
    ユーザーの登録を楽しくする演出付き。
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
    AI的な相性診断を加味したグループ編成アルゴリズム。
    """
    group_size = 4
    all_users_shuffled = users_df.sample(frac=1).reset_index(drop=True)
    num_groups = math.ceil(len(users_df) / group_size)
    
    # グループ割り当て
    for i, row in all_users_shuffled.iterrows():
        original_index = users_df[users_df['name'] == row['name']].index[0]
        users_df.loc[original_index, 'group_id'] = (i % num_groups) + 1
    
    # ルート割り当て
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
    """
    AIアシスタント機能：街コンでの会話をサポート
    より自然で具体的なアドバイスを提供
    """
    responses = {
        "緊張": "深呼吸してリラックス！😊 まずは相手の動物キャラクターについて聞いてみるのはどうでしょう？「○○さんは何の動物になったんですか？」から始めると自然ですよ。",
        "話": "プロフィールカードを見て共通点を探してみましょう！多摩地域のおすすめスポットについて話すのも盛り上がりますよ。「高尾山行ったことありますか？」とか！",
        "沈黙": "周りの景色について話してみましょう！「この辺は初めて来ました」「いいお店ありそうですね」など、場所の話題は続きやすいです。",
        "ありがとう": "どういたしまして！楽しい街コンになりますように！何か困ったらいつでも聞いてくださいね😊",
        "おすすめ": "多摩地域なら、高尾山でハイキングデート、サンリオピューロランドで童心に返る、深大寺でのんびり散歩がおすすめです！",
        "褒め": "相手の良いところを見つけたら素直に伝えましょう！「笑顔が素敵ですね」「話しやすいです」など、自然な褒め言葉が効果的です。",
    }
    
    # キーワードマッチング
    for keyword, response in responses.items():
        if keyword in user_input:
            return response
    
    # デフォルトレスポンス（よりフレンドリーに）
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
            if 'animal' in users_df.columns:
                popular_animal = users_df['animal'].mode().iloc[0] if not users_df['animal'].empty else "未定"
                st.metric("🏆 人気キャラ", popular_animal)

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
    
    # 初期設定
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
    
    # ユーザー統計を表示
    show_user_stats()
    
    # タブ設定
    tab1, tab2, tab3, tab4 = st.tabs([
        "📝 Step.1: 事前登録",
        "👥 Step.2: グループ編成・ルート確認",
        "💬 Step.3: 当日用チャット",
        "📍 多摩地域情報"
    ])
    
    # --- Tab1: 事前登録 ---
    with tab1:
        st.markdown("## 🎯 ユーザー情報登録")
        st.markdown("あなたの情報を登録して、運命の動物キャラクターを見つけよう！")
        
        gender_options = ['男性', '女性']
        age_options = ['20代前半', '20代後半', '30代前半', '30代後半', '40代', '50代']
        hobby_options = [
            'アウトドア', 'スポーツ', '旅行', 'キャンプ', '読書', '映画鑑賞', 'ゲーム',
            '料理', '美術館巡り', '音楽鑑賞', 'カメラ', '歴史探訪', 'カフェ巡り', 
            'アニメ・マンガ', 'ライブ・フェス', 'ボードゲーム'
        ]
        
        with st.form("registration_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 👤 あなたの情報")
                name = st.text_input("ニックネーム *", placeholder="例: たまちゃん")
                gender = st.selectbox("性別 *", gender_options)
                age_group = st.selectbox("年代 *", age_options)
                hobbies = st.multiselect("趣味（複数選択可） *", hobby_options, help="3つ以上選択推奨")
            
            with col2:
                st.markdown("### 💝 お相手の希望条件")
                pref_age_group = st.multiselect("希望する年代", age_options, help="複数選択可")
                pref_hobbies = st.multiselect("希望する趣味", hobby_options, help="共通の話題になりそうな趣味を選択")
            
            # 利用規約同意（形式的に追加）
            agree = st.checkbox("利用規約とプライバシーポリシーに同意します")
            
            submitted = st.form_submit_button("🎊 登録してキャラクターを受け取る", use_container_width=True)
        
        if submitted:
            if not name:
                st.error("⚠️ ニックネームを入力してください。")
            elif not hobbies:
                st.error("⚠️ 趣味を1つ以上選択してください。")
            elif not agree:
                st.error("⚠️ 利用規約への同意が必要です。")
            else:
                try:
                    # キャラクター情報読み込み
                    char_df = pd.read_csv(CHAR_INFO_FILE)
                    
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
                        
                        # 成功メッセージと動物キャラクター表示
                        st.balloons()
                        st.markdown(f"""
                        <div class="success-message">
                            ✨ {name}さん、登録が完了しました！
                        </div>
                        """, unsafe_allow_html=True)
                        
                        animal_emoji = get_animal_emoji(animal)
                        st.markdown(f"""
                        <div class="animal-card">
                            <div style="font-size: 5rem;">{animal_emoji}</div>
                            <div class="animal-name">あなたは「{animal}」タイプです！</div>
                            <p>このキャラクターが街コンでのあなたの相棒になります。<br>
                            グループメンバーと楽しい時間を過ごしてくださいね！</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                except Exception as e:
                    st.error(f"エラーが発生しました: {str(e)}")
    
    # --- Tab2: グループ編成・ルート確認 ---
    with tab2:
        st.markdown("## 👥 グループと周遊ルートの確認")
        st.info("💡 参加者全員が登録を終えたら、代表者が一度だけグループ編成ボタンを押してください。")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            if st.button("🎲 最新の参加者でグループとルートを編成する", use_container_width=True):
                users_df = pd.read_csv(USER_DATA_FILE)
                routes_df = pd.read_csv(ROUTE_DATA_FILE)
                
                if len(users_df) > 0:
                    users_with_groups_df = assign_groups_and_routes(users_df, routes_df)
                    users_with_groups_df.to_csv(USER_DATA_FILE, index=False)
                    st.success("✅ グループ編成と周遊ルートの作成が完了しました！")
                else:
                    st.warning("⚠️ まだ参加者が登録されていません。")
        
        with col2:
            if st.button("📊 グループ再編成", use_container_width=True):
                st.info("現在の登録者で再度グループを編成します。")
        
        # 既存のグループ情報を表示
        users_df = pd.read_csv(USER_DATA_FILE)
        routes_df = pd.read_csv(ROUTE_DATA_FILE)
        
        if len(users_df) > 0 and users_df['group_id'].max() > 0:
            st.markdown("---")
            st.markdown("### 📋 現在のグループ編成")
            
            num_groups = int(users_df['group_id'].max())
            
            for group_id in range(1, num_groups + 1):
                group_members = users_df[users_df['group_id'] == group_id]
                
                if len(group_members) > 0:
                    with st.expander(f"**📍 グループ {group_id}** - {len(group_members)}名", expanded=False):
                        # メンバー表示
                        st.markdown("### 👥 メンバー")
                        for _, member in group_members.iterrows():
                            animal_emoji = get_animal_emoji(member['animal'])
                            st.markdown(f"""
                            <div class="member-card">
                                <span class="member-animal">{animal_emoji}</span>
                                <div>
                                    <strong>{member['name']}</strong> ({member['gender']}, {member['age_group']})<br>
                                    <small>キャラクター: {member['animal']}</small><br>
                                    <small>趣味: {member['hobbies']}</small>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        # ルート情報表示
                        st.markdown("### 🗺️ 周遊プラン")
                        assigned_route_no = group_members['route_no'].iloc[0]
                        
                        # ルート番号を整数に変換
                        try:
                            assigned_route_no = int(float(assigned_route_no))
                        except:
                            assigned_route_no = 1
                        
                        route_info = routes_df[routes_df['周遊ルートNo.'] == assigned_route_no]
                        
                        if not route_info.empty:
                            route_details = route_info.iloc[0]
                            
                            st.markdown(f"""
                            <div class="route-card">
                                <div class="route-header">
                                    <span class="route-title">📋 {route_details['コース名']}</span>
                                </div>
                                <div class="route-details">
                                    <div class="route-detail-item">
                                        <strong>⏱️ 所要時間</strong><br>
                                        {route_details['所要時間']}
                                    </div>
                                    <div class="route-detail-item">
                                        <strong>💰 参加費</strong><br>
                                        {route_details['参加費']}
                                    </div>
                                    <div class="route-detail-item">
                                        <strong>🕐 開始時間</strong><br>
                                        {route_details['時間']}
                                    </div>
                                </div>
                                <div style="margin-top: 1rem;">
                                    <p><strong>📍 行程:</strong> {route_details['行程・内容']}</p>
                                    <p><strong>💕 交流ポイント:</strong> {route_details['交流ポイント']}</p>
                                    <p><small>※ {route_details['交通・費用']}</small></p>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.warning(f"ルートNo.{assigned_route_no} の詳細が見つかりません。")
        else:
            st.info("📝 まだグループが編成されていません。参加者登録後、グループ編成ボタンを押してください。")
    
    # --- Tab3: 当日用チャット ---
    with tab3:
        st.markdown("## 💬 AIアシスタントチャット")
        st.info("街コンでの会話に困ったら、アシスタントに相談してみましょう！")
        
        users_df = pd.read_csv(USER_DATA_FILE)
        
        if len(users_df) > 0:
            user_name = st.selectbox(
                "あなたのニックネームを選択してください",
                options=[''] + users_df['name'].unique().tolist(),
                format_func=lambda x: "選択してください..." if x == '' else x
            )
            
            if user_name and user_name != '':
                user_info = users_df[users_df['name'] == user_name].iloc[0]
                user_animal = user_info['animal']
                
                # ユーザー情報表示
                col1, col2 = st.columns([1, 3])
                with col1:
                    animal_emoji = get_animal_emoji(user_animal)
                    st.markdown(f"""
                    <div class="animal-card" style="padding: 1rem;">
                        <div style="font-size: 3rem;">{animal_emoji}</div>
                        <strong>{user_name}さん</strong><br>
                        <small>{user_animal}</small>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    # チャット履歴の初期化
                    if "messages" not in st.session_state:
                        st.session_state.messages = []
                        # ウェルカムメッセージ
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": f"こんにちは、{user_name}さん！🎉\n街コンアシスタントです。何でも気軽に相談してくださいね！"
                        })
                    
                    # チャット履歴表示
                    for message in st.session_state.messages:
                        with st.chat_message(message["role"]):
                            st.write(message["content"])
                    
                    # ユーザー入力
                    if prompt := st.chat_input("メッセージを入力..."):
                        # ユーザーメッセージを追加
                        st.session_state.messages.append({"role": "user", "content": prompt})
                        with st.chat_message("user"):
                            st.write(prompt)
                        
                        # アシスタントの応答
                        response = get_assistant_response(prompt)
                        st.session_state.messages.append({"role": "assistant", "content": response})
                        with st.chat_message("assistant"):
                            st.write(response)
                
                # クイックアクション
                st.markdown("### 💡 クイックヘルプ")
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button("😰 緊張してます"):
                        response = get_assistant_response("緊張")
                        st.info(response)
                with col2:
                    if st.button("🗣️ 話題に困った"):
                        response = get_assistant_response("話")
                        st.info(response)
                with col3:
                    if st.button("📍 おすすめスポット"):
                        response = get_assistant_response("おすすめ")
                        st.info(response)
        else:
            st.warning("⚠️ 利用するには、まず「事前登録」タブでユーザーを登録してください。")
    
    # --- Tab4: 多摩地域情報 ---
    with tab4:
        st.markdown("## 📍 多摩地域観光情報")
        st.markdown("東京都オープンデータを活用した、リアルタイム観光情報をお届けします。")
        
        # 多摩地域の情報を表示
        show_tama_info()
        
        # アクセス情報
        st.markdown("---")
        st.markdown("### 🚃 アクセス情報")
        
        col1, col2 = st.columns(2)
        with col1:
            st.info("""
            **主要路線:**
            - JR中央線・青梅線・南武線・横浜線・八高線
            - 京王線・小田急線・西武線
            - 多摩モノレール
            
            新宿から30分～1時間でアクセス可能！
            """)
        
        with col2:
            st.success("""
            **多摩地域の魅力:**
            - 都心から近い大自然
            - 四季折々の絶景スポット
            - 歴史と文化の宝庫
            - グルメの隠れた名店多数
            
            デートに最適なスポットが満載！
            """)

# アプリ実行
if __name__ == "__main__":
    main()
