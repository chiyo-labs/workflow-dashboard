# 📋 案件見える化ダッシュボード

## 🧭 概要
案件の進捗・期限・売上を一元管理できるダッシュボードツールです。  
未対応や期限切れを可視化し、対応漏れを防ぐことを目的としています。

---

## 🌐 デモURL
https://workflow-dashboard-xtnygqratjpfyhtv6nrzu8.streamlit.app/

---

## 🚀 使い方

### ① データ準備
data.example.csv をコピーして data.csv を作成してください。

#### Windows
```bash
copy data.example.csv data.csv
Mac / Linux
cp data.example.csv data.csv
② ライブラリインストール
pip install -r requirements.txt
③ アプリ起動
streamlit run app.py

ブラウザで以下を開きます。
http://localhost:8501

💡 主な機能
案件の登録・編集・削除
状態管理（未対応・対応中・完了）
期限アラート（期限切れ・直近）
売上の自動計算
フィルター・一覧表示
🎯 工夫したポイント
期限切れ・直近の案件を自動で検知しアラート表示
状態ごとに色分けして視覚的に分かりやすく設計
編集・削除機能を実装し、実務で使える構成にした
初心者でも扱いやすいシンプルなUI
⚠️ 注意事項
data.csv はローカルデータとして管理されます（Gitには含まれません）
個人情報・機密情報は自己責任で管理してください
🔧 使用技術
Python
Streamlit
pandas
👤 Author

chiyo-labs