🧾 Workflow Dashboard（案件管理ツール）
■ Overview

案件の登録・管理・売上確認ができるWebアプリです。
Supabaseを利用した認証機能とデータベース連携により、ユーザーごとのデータ管理を実現しています。

■ Demo

👉 https://workflow-dashboard-xtnygqratjpfyhtv6nrzu8.streamlit.app/

※ログイン機能を使用するため、初回はユーザー登録が必要です

■ Features
🔐 ユーザー認証（Supabase Auth）
📋 案件の登録 / 編集 / 削除
📊 案件一覧表示
💰 売上の自動計算
👤 ユーザーごとのデータ分離
■ Tech Stack
Python（Streamlit）
Supabase（Auth / Database）
Pandas
■ Architecture
フロント：Streamlit
認証：Supabase Auth
DB：Supabase（PostgreSQL）
ユーザー識別：auth.uid() による分離
■ Database Schema

Table: cases

user_id
case_id
order_date
due_date
customer_name
case_name
count
unit_price
revenue
status
memo
■ Setup
1. Clone
git clone （URL）
cd workflow-dashboard
2. Install
pip install -r requirements.txt
3. Secrets設定

.streamlit/secrets.toml

SUPABASE_URL = "https://xxxx.supabase.co"
SUPABASE_KEY = "your-anon-key"
4. Run
streamlit run app.py
■ Deployment（重要）

Streamlit Cloudで動かす場合は
Settings → Secrets に以下を設定

SUPABASE_URL
SUPABASE_KEY
■ Improvements
UI/UX改善
スマホ対応
LINE通知機能
カレンダー連携
■ Why I built this

案件管理をシンプルに行えるツールを作りたいと考え、開発しました。
また、自分用だけでなく「他の人にも使えるツール」を意識して設計しています。