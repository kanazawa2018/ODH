import streamlit as st
import pandas as pd
import random
import os
import math
import json
import datetime
from typing import Dict, List, Tuple

# ==============================
# デモ設定
# ==============================
DEMO_MODE = True  # デモ用に既存CSVを毎回上書きロード

# --- 定数定義 ---
USER_DATA_FILE = '/tmp/users.csv'
CHAR_INFO_FILE = '/tmp/キャラ情報.csv'
ROUTE_DATA_FILE = '/tmp/input/周遊ルート.csv'
CHAR_IMAGE_DIR = '/tmp/input/キャラ画像'
EVENT_DATA_FILE = '/tmp/tama_events.json'  # 多摩地域イベント情報

# ==============================
# ご提示のCSVデータ（そのまま上書き保存）
# ==============================
DEMO_USERS_CSV = """name,gender,age_group,hobbies,pref_age_group,pref_hobbies,animal,group_id,route_no
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
りょう,男性,40代,"料理, カメラ","30代前半, 20代後半","旅行, 料理, 美術館巡り",コツメカワウソ,6,4
"""

DEMO_CHAR_CSV = """動物,キャラクター名
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
アカカンガルー,マルオ
"""

# 周遊ルート：1コース=複数行（概要1行 + 詳細n行）
DEMO_ROUTES_CSV = """周遊ルートNo.,コース名,時間,行程・内容,交通・費用,交流ポイント,所要時間,参加費
1,Safari ✕ 花畑ピクニック,12:00,多摩動物公園 正門前で受付・チーム分け—ネームカードに「好きな動物」を記入する,,自己紹介,4時間15分,3,000円
1,Safari ✕ 花畑ピクニック,12:05‑13:35,園内ラリー「推しアニマル撮れ高対決」〈ペアを15分ごとにシャッフル〉,入園600円,写真を見せ合いながらトーク,,
1,Safari ✕ 花畑ピクニック,13:35,モノレール乗車 多摩動物公園 → 立川北（25分）,310円,車内で“共通点ビンゴ”,,
1,Safari ✕ 花畑ピクニック,14:05‑16:00,国営昭和記念公園 ・桜の園でレジャーシートピクニック（お花畑シーズンはポピー/コスモスエリア）・巨大フリスビー・ペアボート（1艇30分）,入園450円 + ボート300円 + お弁当1,000円,４人１組でゲーム→勝利チームには公園オリジナルグッズ,,
1,Safari ✕ 花畑ピクニック,16:00‑16:15,立川駅前で解散（希望者は二次会へ）,徒歩10分,LINE交換タイム,,
2,レトロ建築スタンプラリー,9:30,多摩動物公園駅前集合—オープニングアイスブレイク,,オープニングアイスブレイク,5時間20分,3,500円
2,レトロ建築スタンプラリー,09:40‑10:25,モノレール→JR中央線→バスで小金井公園西口へ,310+220+220円,車内で“過去に住んだ街クイズ”,,
2,レトロ建築スタンプラリー,10:40‑12:30,江戸東京たてもの園 ・チーム対抗スタンプラリー（15軒制覇で景品）・旧自証院霊屋前でグループ写真,入園400円,20分毎にチーム替え,,
2,レトロ建築スタンプラリー,12:30‑13:30,「昭和の居間」体験室で伝統玩具ワークショップ（万華鏡づくり 500円）＋軽食,万華鏡500円 + 軽食1,000円,作品交換タイム,,
2,レトロ建築スタンプラリー,13:30‑14:50,逆経路で多摩動物公園へ戻り解散,310+220+220円,帰路は自由席で気になる人と並び席,,
3,深大寺そば打ち Love クッキング,11:00,多摩動物公園駅集合 → 京王線で調布,片道270円,座席シャッフル自己紹介,5時間,4,500円
3,深大寺そば打ち Love クッキング,11:35‑11:55,バスで深大寺,220円,２列シートで質問カードトーク,,
3,深大寺そば打ち Love クッキング,11:55‑12:25,深大寺 おみくじ & ペア開運散策（御朱印100円）,100円,結果報告で盛り上がる,,
3,深大寺そば打ち Love クッキング,12:30‑14:00,そば打ち道場（市営施設）２人１組でそば打ち→そのまま昼食,体験2,000円,共同作業で距離縮まる,,
3,深大寺そば打ち Love クッキング,14:05‑15:15,都立神代植物公園 バラ園ガイドツアー,入園500円,花言葉トーク,,
3,深大寺そば打ち Love クッキング,15:15‑16:00,バス→京王線で多摩動物公園へ戻り、駅前カフェでフリータイム,220+270円 + カフェ500円,最後のマッチングカード提出,,
4,府中 歴史＆ホースバックヤードツアー,10:00,多摩動物公園集合 → モノレール・JR・バスで 府中市郷土の森博物館,310+220+210円,道中「東京あるある」カード,5時間10分,4,000円
4,府中 歴史＆ホースバックヤードツアー,10:50‑12:10,野外建築エリアで 謎解き脱出ゲーム（オリジナル台本提供）,入園300円,５人１組で協力,,
4,府中 歴史＆ホースバックヤードツアー,12:10‑12:50,勾玉づくりワークショップ（500円）& 芝生ランチ（お弁当1,000円）,1,500円,作品交換,,
4,府中 歴史＆ホースバックヤードツアー,12:55‑13:15,バスで府中競馬正門前,210円,,,
4,府中 歴史＆ホースバックヤードツアー,13:15‑14:45,東京競馬場 バックヤード見学（国際厩舎・調教コース）,見学200円,競走馬の名前ビンゴ,,
4,府中 歴史＆ホースバックヤードツアー,14:45‑15:10,京王線で多摩動物公園へ戻り解散,260円,帰路でカップリング結果発表,,
5,高尾山 サンセット・ケーブル Love Walk,13:00,多摩動物公園駅集合 → 京王線で高尾山口,片道300円,“理想の休日”トークカード,4時間,4,000円
5,高尾山 サンセット・ケーブル Love Walk,13:45,ケーブルカーで中腹へ,往復960円,隣席ペアトーク,,
5,高尾山 サンセット・ケーブル Love Walk,14:00‑15:45,高尾山 ペアトレッキング & 山頂カフェタイム（ソフトドリンク700円）・途中で「山恋フォトミッション」,700円,写真共有で盛り上がる,,
5,高尾山 サンセット・ケーブル Love Walk,15:45‑16:15,ケーブル下山→駅前足湯（15分 500円）,500円,目隠し足湯 Q&A,,
5,高尾山 サンセット・ケーブル Love Walk,16:15‑16:45,京王線で多摩動物公園へ戻り解散,,,,
"""

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

# --- 初期設定: 必要なファイルやディレクトリが存在しない場合に作成 or デモで上書き ---
def setup_files():
    """
    デモ: ご提示のCSVを必ず書き込み（上書き）
    """
    os.makedirs(os.path.dirname(USER_DATA_FILE), exist_ok=True)
    os.makedirs(os.path.dirname(CHAR_INFO_FILE), exist_ok=True)
    os.makedirs(os.path.dirname(ROUTE_DATA_FILE), exist_ok=True)
    os.makedirs(CHAR_IMAGE_DIR, exist_ok=True)

    # デモモードでは必ず上書き
    if DEMO_MODE:
        with open(USER_DATA_FILE, 'w', encoding='utf-8') as f:
            f.write(DEMO_USERS_CSV)
        with open(CHAR_INFO_FILE, 'w', encoding='utf-8') as f:
            f.write(DEMO_CHAR_CSV)
        with open(ROUTE_DATA_FILE, 'w', encoding='utf-8') as f:
            f.write(DEMO_ROUTES_CSV)
    else:
        # 通常動作（必要時のみ作成）※未使用だが保守のため残置
        if not os.path.exists(USER_DATA_FILE):
            with open(USER_DATA_FILE, 'w', encoding='utf-8') as f:
                f.write(DEMO_USERS_CSV)
        if not os.path.exists(CHAR_INFO_FILE):
            with open(CHAR_INFO_FILE, 'w', encoding='utf-8') as f:
                f.write(DEMO_CHAR_CSV)
        if not os.path.exists(ROUTE_DATA_FILE):
            with open(ROUTE_DATA_FILE, 'w', encoding='utf-8') as f:
                f.write(DEMO_ROUTES_CSV)

    # 多摩地域イベント情報（既存なければ生成）
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
                    {"name":"🌿 都立小山内裏公園","description":"多摩ニュータウン最大の都市公園。尾根道からの眺望が素晴らしい","access":"京王相模原線「南大沢」駅から徒歩20分"},
                    {"name":"☕ 国立天文台","description":"第一赤道儀室など大正時代の建物が見学可能。宇宙に興味がある人におすすめ","access":"JR「武蔵境」駅からバス15分"},
                    {"name":"🎨 府中市美術館","description":"「生活と美術」をテーマにした展示。公園内にありピクニックも楽しめる","access":"京王線「東府中」駅からバス"}
                ],
                "gourmet_spots": [
                    {"name":"🍜 八王子ラーメン","description":"刻み玉ねぎが特徴の醤油ラーメン。市内に50店舗以上！","recommended":"みんみんラーメン、吾衛門"},
                    {"name":"🍖 立川の焼肉街","description":"駅周辺に高級店からリーズナブルな店まで多数","recommended":"炭火焼肉ホルモン横丁、焼肉ライク"},
                    {"name":"🍰 吉祥寺スイーツ","description":"小さなパティスリーから有名店まで、スイーツ激戦区","recommended":"アテスウェイ、小ざさ"}
                ]
            }
            with open(EVENT_DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump(sample_events, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

# --- モダンなスタイル定義 ---
def apply_modern_style():
    st.markdown(f"""
    <style>
        .stApp {{ background: linear-gradient(135deg, {COLORS['light']} 0%, #E3F2FD 100%); }}
        .main-header {{
            background: linear-gradient(90deg, {COLORS['primary']} 0%, {COLORS['gradient_start']} 100%);
            color: white; padding: 2rem; border-radius: 20px; margin-bottom: 2rem;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1); text-align: center;
        }}
        .main-header h1 {{ font-size: 2.5rem; font-weight: 800; margin: 0; text-shadow: 2px 2px 4px rgba(0,0,0,0.2); }}
        .main-header p {{ font-size: 1.1rem; margin-top: 0.5rem; opacity: 0.95; }}
        .info-card {{
            background: white; border-radius: 16px; padding: 1.5rem; margin: 1rem 0;
            box-shadow: 0 4px 20px rgba(0,0,0,0.08); border-left: 4px solid {COLORS['primary']};
            transition: all 0.3s ease;
        }}
        .info-card:hover {{ transform: translateY(-2px); box-shadow: 0 6px 30px rgba(0,0,0,0.12); }}
        .animal-card {{
            background: linear-gradient(135deg, #fff 0%, #f8f9fa 100%); border: 2px solid {COLORS['primary']};
            border-radius: 20px; padding: 1.5rem; text-align: center;
            box-shadow: 0 8px 25px rgba(0,0,0,0.1); transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }}
        .animal-card:hover {{ transform: scale(1.02) translateY(-3px); box-shadow: 0 12px 35px rgba(0,0,0,0.15); border-color: {COLORS['secondary']}; }}
        .animal-name {{ font-size: 1.8rem; font-weight: 700; color: {COLORS['primary']}; margin: 1rem 0; }}
        .member-card {{
            background: white; border-radius: 12px; padding: 1rem; margin: 0.5rem 0; display: flex; align-items: center;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05); transition: all 0.2s ease;
        }}
        .member-card:hover {{ background: {COLORS['light']}; transform: translateX(5px); }}
        .member-animal {{ font-size: 2rem; margin-right: 1rem; }}
        .route-card {{
            background: linear-gradient(135deg, #ffffff 0%, #f0f7ff 100%);
            border-radius: 16px; padding: 1.5rem; margin: 1rem 0; border: 1px solid #e0e0e0;
            box-shadow: 0 4px 15px rgba(0,0,0,0.06);
        }}
        .route-header {{ display:flex; align-items:center; justify-content:space-between; margin-bottom:1rem; padding-bottom:0.5rem; border-bottom:2px solid {COLORS['primary']}; }}
        .route-title {{ font-size:1.3rem; font-weight:700; color:{COLORS['dark']}; }}
        .route-details {{ display:grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap:1rem; margin-top:1rem; }}
        .route-detail-item {{ text-align:center; padding:0.5rem; background:{COLORS['light']}; border-radius:8px; }}
        .timeline-item {{ border-left: 3px solid {COLORS['primary']}; padding-left: 0.75rem; margin: 0.5rem 0; }}
        .event-card {{
            background: linear-gradient(135deg, {COLORS['warning']} 0%, #FFA726 100%);
            color: {COLORS['dark']}; padding: 1rem; border-radius: 12px; margin: 0.5rem 0; box-shadow: 0 3px 10px rgba(255, 217, 61, 0.3);
        }}
        .spot-card {{
            background: white; border-radius: 16px; padding: 1.2rem; margin: 0.5rem 0; box-shadow: 0 4px 15px rgba(0,0,0,0.08);
            transition: all 0.3s ease; border: 2px solid transparent;
        }}
        .spot-card:hover {{ transform: translateY(-3px); box-shadow: 0 8px 25px rgba(0,0,0,0.12); border-color: {COLORS['primary']}; }}
        .spot-title {{ font-size:1.2rem; font-weight:700; color:{COLORS['dark']}; margin-bottom:0.5rem; }}
        .spot-category {{ display:inline-block; padding:0.2rem 0.8rem; background:{COLORS['primary']}; color:white; border-radius:15px; font-size:0.85rem; margin-bottom:0.5rem; }}
        .crowd-indicator {{ display:inline-block; padding:0.25rem 0.75rem; border-radius:20px; font-weight:600; font-size:0.9rem; }}
        .crowd-low {{ background:#C8E6C9; color:#2E7D32; }}
        .crowd-medium {{ background:#FFF9C4; color:#F57C00; }}
        .crowd-high {{ background:#FFCDD2; color:#C62828; }}
    </style>
    """, unsafe_allow_html=True)

# --- 多摩地域情報表示関数 ---
def show_tama_info():
    default_event_data = {
        "seasonal_events": [
            {"month": datetime.datetime.now().month, "event": "🌸 多摩地域の季節イベント", "crowd_level": 3, 
             "description": "四季折々の素敵なイベントが開催されています"}
        ],
        "popular_spots": [
            {"name": "🏔️ 高尾山", "category": "自然・絶景", "avg_crowd": 3.5, "best_time": "平日午前"},
            {"name": "🎀 サンリオピューロランド", "category": "テーマパーク", "avg_crowd": 4.0, "best_time": "平日"}
        ],
        "hidden_gems": [],
        "gourmet_spots": []
    }
    try:
        if not os.path.exists(EVENT_DATA_FILE):
            setup_files()
        with open(EVENT_DATA_FILE, 'r', encoding='utf-8') as f:
            event_data = json.load(f)
    except Exception:
        event_data = default_event_data
        st.warning("観光情報の読み込みに失敗しました。デフォルト情報を表示しています。")

    current_month = datetime.datetime.now().month

    info_tab1, info_tab2, info_tab3, info_tab4 = st.tabs(["📅 季節のイベント","📍 人気スポット","💎 穴場スポット","🍽️ グルメ情報"])
    with info_tab1:
        monthly_events = [e for e in event_data.get('seasonal_events', []) if e.get('month') == current_month]
        if monthly_events:
            st.markdown("### 🎊 今月のおすすめイベント")
            for event in monthly_events:
                crowd_level = event.get('crowd_level', 3)
                crowd_text = ['空いている', '空いている', '普通', 'やや混雑', '混雑'][min(crowd_level, 4)]
                crowd_class = ['low', 'low', 'medium', 'high', 'high'][min(crowd_level, 4)]
                st.markdown(f"""
                <div class="event-card">
                    <strong style="font-size: 1.2rem;">{event.get('event','イベント')}</strong><br>
                    <p style="margin: 0.5rem 0;">{event.get('description','')}</p>
                    混雑予想: <span class="crowd-indicator crowd-{crowd_class}">{crowd_text}</span>
                </div>
                """, unsafe_allow_html=True)
        st.markdown("### 📆 年間イベントカレンダー")
        other_events = [e for e in event_data.get('seasonal_events', []) if e.get('month') != current_month]
        if other_events:
            cols = st.columns(2)
            for idx, event in enumerate(other_events[:8]):
                with cols[idx % 2]:
                    st.info(f"**{event.get('month','?')}月** {event.get('event','イベント')}")

    with info_tab2:
        st.markdown("### 🌟 多摩地域の人気デートスポット")
        for spot in event_data.get('popular_spots', []):
            crowd_level = spot.get('avg_crowd', 3.0)
            crowd_class = 'low' if crowd_level < 2.5 else 'medium' if crowd_level < 3.5 else 'high'
            name = spot.get('name','名称不明')
            category = spot.get('category','その他')
            highlight = spot.get('highlight','素敵なスポットです')
            instagram_spots = spot.get('instagram_spots',['フォトスポット多数'])
            date_point = spot.get('date_point','二人で楽しめます')
            best_time = spot.get('best_time','終日')
            st.markdown(f"""
            <div class="spot-card">
                <div class="spot-title">{name}</div>
                <span class="spot-category">{category}</span>
                <p><strong>✨ ここがすごい！</strong><br>{highlight}</p>
                <p><strong>📸 インスタ映えスポット:</strong><br>{"、".join(instagram_spots)}</p>
                <p><strong>💕 デートポイント:</strong><br>{date_point}</p>
                <p>
                    <strong>混雑度:</strong>
                    <span class="crowd-indicator crowd-{crowd_class}">
                        {'★' * int(crowd_level)}{'☆' * (5 - int(crowd_level))}
                    </span><br>
                    <small>💡 おすすめ時間: {best_time}</small>
                </p>
            </div>
            """, unsafe_allow_html=True)

    with info_tab3:
        st.markdown("### 💎 地元民おすすめ！穴場スポット")
        for gem in event_data.get('hidden_gems', []):
            st.markdown(f"""
            <div class="info-card">
                <strong style="font-size: 1.1rem;">{gem.get('name','名称不明')}</strong><br>
                <p>{gem.get('description','詳細情報なし')}</p>
                <small>📍 アクセス: {gem.get('access','アクセス情報なし')}</small>
            </div>
            """, unsafe_allow_html=True)

    with info_tab4:
        st.markdown("### 🍽️ 多摩グルメマップ")
        for gourmet in event_data.get('gourmet_spots', []):
            st.markdown(f"""
            <div class="info-card">
                <strong style="font-size: 1.1rem;">{gourmet.get('name','名称不明')}</strong><br>
                <p>{gourmet.get('description','詳細情報なし')}</p>
                <p><strong>おすすめ店:</strong> {gourmet.get('recommended','おすすめ店舗情報なし')}</p>
            </div>
            """, unsafe_allow_html=True)

# --- 動物の絵文字マッピング ---
ANIMAL_EMOJI_MAP = {
    'コアラ': '🐨','インドサイ': '🦏','ライオン': '🦁','チーター': '🐆','オラウータン': '🦧','カピバラ': '🦫',
    'タイリクオオカミ': '🐺','コツメカワウソ': '🦦','モウコノウマ': '🐴','ワライカワセミ': '🦜','タスマニアデビル': '😈','アカカンガルー': '🦘'
}
def get_animal_emoji(animal_name): return ANIMAL_EMOJI_MAP.get(animal_name, '🦊')

# --- AIアシスタント応答 ---
def get_assistant_response(user_input):
    responses = {
        "緊張": "深呼吸してリラックス！😊 まずは相手の動物キャラクターについて聞いてみましょう。「○○さんは何の動物になったんですか？」から始めると自然ですよ。",
        "話": "プロフィールの共通点や多摩のおすすめスポットの話題が盛り上がります。「高尾山行ったことありますか？」など！",
        "沈黙": "周りの景色や場所の話題に切り替えてみましょう。「この辺は初めて」「良さそうなお店ありますね」など。",
        "ありがとう": "どういたしまして！楽しい街コンになりますように😊",
        "おすすめ": "多摩なら高尾山ハイキング、サンリオピューロランド、深大寺散策が鉄板です！",
        "褒め": "自然体の褒め言葉が◎「笑顔が素敵ですね」「話しやすいです」など。"
    }
    for k, v in responses.items():
        if k in user_input:
            return v
    return "いいですね！その調子で楽しんでください😊"

# --- ユーザー統計 ---
def show_user_stats():
    try:
        users_df = pd.read_csv(USER_DATA_FILE)
        if len(users_df) > 0:
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("👥 登録者数", f"{len(users_df)}名")
            with col2:
                male_count = (users_df['gender'] == '男性').sum()
                female_count = (users_df['gender'] == '女性').sum()
                st.metric("⚖️ 男女比", f"{male_count}:{female_count}")
            with col3:
                st.metric("👫 グループ数", f"{users_df['group_id'].nunique()}組")
            with col4:
                popular_animal = users_df['animal'].mode().iloc[0] if 'animal' in users_df.columns and not users_df['animal'].empty else "未定"
                st.metric("🏆 人気キャラ", popular_animal)
    except Exception:
        col1, col2, col3, col4 = st.columns(4)
        with col1: st.metric("👥 登録者数", "0名")
        with col2: st.metric("⚖️ 男女比", "0:0")
        with col3: st.metric("👫 グループ数", "0組")
        with col4: st.metric("🏆 人気キャラ", "未定")

# --- Streamlit アプリ本体 ---
def main():
    st.set_page_config(page_title="アニマル縁結び🦊 - 多摩地域街コンアプリ（デモ）", page_icon="🦊", layout="wide", initial_sidebar_state="collapsed")
    setup_files()               # ★ デモCSVを上書き
    apply_modern_style()

    st.markdown("""
    <div class="main-header">
        <h1>🦊 アニマル縁結び（デモ版） 🦊</h1>
        <p>既存データを読み込み、街コン当日の進行イメージを体験できます（登録・再編成はロック）。</p>
    </div>
    """, unsafe_allow_html=True)

    show_user_stats()

    tab1, tab2, tab3, tab4 = st.tabs(["📝 Step.1: 事前登録（デモ表示）","👥 Step.2: グループ・ルート","💬 Step.3: 当日用チャット","📍 多摩地域情報"])

    # --- Tab1: 事前登録（読み取り専用） ---
    with tab1:
        st.markdown("### 📄 既存登録データ（読み取り専用）")
        st.info("デモでは新規登録はできません。下表は事前に登録済みのユーザー一覧です。")
        try:
            users_df = pd.read_csv(USER_DATA_FILE)
            st.dataframe(users_df, use_container_width=True)
        except Exception as e:
            st.error(f"ユーザーデータの読み込みに失敗しました: {e}")

        st.markdown("#### 🧩 キャラクター対応表")
        try:
            char_df = pd.read_csv(CHAR_INFO_FILE)
            st.dataframe(char_df, use_container_width=True)
        except Exception as e:
            st.error(f"キャラ情報の読み込みに失敗しました: {e}")

    # --- Tab2: グループ・ルート（既存割当を表示） ---
    with tab2:
        st.markdown("## 👥 現在のグループ編成 & 周遊ルート")
        st.info("デモのため、グループ再編成ボタンは非表示です。既存の割り当てをそのまま表示します。")
        try:
            users_df = pd.read_csv(USER_DATA_FILE)
            routes_df = pd.read_csv(ROUTE_DATA_FILE)

            if len(users_df) > 0 and users_df['group_id'].max() > 0:
                st.markdown("---")
                st.markdown("### 📋 グループ一覧")

                num_groups = int(users_df['group_id'].max())
                # ルートNo.の型を揃える
                routes_df['周遊ルートNo.'] = pd.to_numeric(routes_df['周遊ルートNo.'], errors='coerce')

                for group_id in range(1, num_groups + 1):
                    group_members = users_df[users_df['group_id'] == group_id]
                    if len(group_members) == 0:
                        continue

                    route_no = group_members['route_no'].iloc[0]
                    try:
                        route_no_int = int(float(route_no)) if not pd.isna(route_no) else 1
                    except Exception:
                        route_no_int = 1

                    route_info = routes_df[routes_df['周遊ルートNo.'] == route_no_int]
                    route_name = route_info['コース名'].iloc[0] if not route_info.empty else "ルート未定"

                    with st.expander(f"**📍 グループ {group_id}** - {len(group_members)}名 - {route_name}", expanded=False):
                        # メンバー
                        st.markdown("#### 👥 メンバー")
                        for _, member in group_members.iterrows():
                            animal_emoji = get_animal_emoji(member['animal'])
                            st.markdown(f"""
                            <div class="member-card">
                                <span class="member-animal">{animal_emoji}</span>
                                <div>
                                    <strong>{member['name']}</strong> ({member['gender']}, {member['age_group']})<br>
                                    <small>キャラ: {member['animal']}</small><br>
                                    <small>趣味: {member['hobbies']}</small>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)

                        # ルート概要 + タイムライン
                        if not route_info.empty:
                            # 概要行= 所要時間 or 参加費 が入っている最初の行（なければ最初行）
                            summary_candidates = route_info.dropna(subset=['所要時間','参加費'], how='all')
                            if not summary_candidates.empty:
                                summary_row = summary_candidates.iloc[0]
                            else:
                                summary_row = route_info.iloc[0]

                            # 表示用
                            course_name = summary_row.get('コース名','名称不明')
                            duration = summary_row.get('所要時間','未定')
                            price = summary_row.get('参加費','未定')
                            start_time = summary_row.get('時間','未定')
                            schedule = summary_row.get('行程・内容','詳細未定')
                            point = summary_row.get('交流ポイント','楽しく交流しましょう')
                            transport = summary_row.get('交通・費用','')

                            st.markdown("#### 🗺️ 周遊プラン（概要）")
                            st.markdown(f"""
                            <div class="route-card">
                                <div class="route-header">
                                    <span class="route-title">📋 {course_name}</span>
                                </div>
                                <div class="route-details">
                                    <div class="route-detail-item"><strong>⏱️ 所要時間</strong><br>{duration}</div>
                                    <div class="route-detail-item"><strong>💰 参加費</strong><br>{price}</div>
                                    <div class="route-detail-item"><strong>🕐 開始時間</strong><br>{start_time}</div>
                                </div>
                                <div style="margin-top: 1rem;">
                                    <p><strong>📍 行程（概要）:</strong> {schedule}</p>
                                    <p><strong>💕 交流ポイント:</strong> {point}</p>
                                    {f"<p><small>※ {transport}</small></p>" if isinstance(transport, str) and transport.strip() else ""}
                                </div>
                            </div>
                            """, unsafe_allow_html=True)

                            # 詳細タイムライン（概要行以外）
                            timeline_df = route_info.copy()
                            timeline_df = timeline_df.drop(index=summary_candidates.head(1).index if not summary_candidates.empty else [])
                            if len(timeline_df) > 0:
                                st.markdown("#### 🧭 詳細タイムライン")
                                for _, r in timeline_df.iterrows():
                                    tm = r.get('時間','')
                                    itn = r.get('行程・内容','')
                                    fee = r.get('交通・費用','')
                                    pt = r.get('交流ポイント','')
                                    st.markdown(f"""
                                    <div class="timeline-item">
                                        <strong>🕒 {tm}</strong><br>
                                        <span>{itn}</span><br>
                                        {f"<small>🚃 交通・費用: {fee}</small><br>" if isinstance(fee, str) and fee.strip() else ""}
                                        {f"<small>🤝 交流ポイント: {pt}</small>" if isinstance(pt, str) and pt.strip() else ""}
                                    </div>
                                    """, unsafe_allow_html=True)
                        else:
                            st.warning(f"ルートNo.{route_no_int} の詳細が見つかりません。")
            else:
                st.info("📝 グループ情報が未設定です。")
        except Exception as e:
            st.error(f"データの読み込みエラー: {e}")

    # --- Tab3: 当日チャット ---
    with tab3:
        st.markdown("## 💬 AIアシスタントチャット")
        st.info("街コンでの会話に困ったらアシスタントへ。")
        try:
            users_df = pd.read_csv(USER_DATA_FILE)
            if len(users_df) > 0:
                user_name = st.selectbox("あなたのニックネームを選択", options=[''] + users_df['name'].unique().tolist(), format_func=lambda x: "選択してください..." if x=='' else x)
                if user_name and user_name != '':
                    user_info = users_df[users_df['name'] == user_name].iloc[0]
                    user_animal = user_info['animal']
                    col1, col2 = st.columns([1,3])
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
                        if "messages" not in st.session_state:
                            st.session_state.messages = [{"role":"assistant","content":f"こんにちは、{user_name}さん！🎉 街コンアシスタントです。何でも気軽にどうぞ！"}]
                        for message in st.session_state.messages:
                            with st.chat_message(message["role"]):
                                st.write(message["content"])
                        if prompt := st.chat_input("メッセージを入力..."):
                            st.session_state.messages.append({"role":"user","content":prompt})
                            with st.chat_message("user"):
                                st.write(prompt)
                            response = get_assistant_response(prompt)
                            st.session_state.messages.append({"role":"assistant","content":response})
                            with st.chat_message("assistant"):
                                st.write(response)
                    st.markdown("### 💡 クイックヘルプ")
                    c1, c2, c3 = st.columns(3)
                    with c1:
                        if st.button("😰 緊張してます"):
                            st.info(get_assistant_response("緊張"))
                    with c2:
                        if st.button("🗣️ 話題に困った"):
                            st.info(get_assistant_response("話"))
                    with c3:
                        if st.button("📍 おすすめスポット"):
                            st.info(get_assistant_response("おすすめ"))
            else:
                st.warning("⚠️ ユーザーがいません。")
        except Exception as e:
            st.warning(f"⚠️ データ読み込みエラー: {e}")

    # --- Tab4: 多摩地域情報 ---
    with tab4:
        st.markdown("## 📍 多摩地域観光情報")
        st.markdown("東京都オープンデータを活用した観光ヒントを表示します。")
        show_tama_info()
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
            - 四季折々の絶景
            - 歴史と文化
            - 隠れた名店グルメ

            デートに最適なスポットが満載！
            """)

if __name__ == "__main__":
    main()
