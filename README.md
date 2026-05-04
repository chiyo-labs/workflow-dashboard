# WorkFlow Dashboard

Streamlit 製のワークフロー／案件管理ダッシュボードです。

## データファイルについて

- **`data.csv`** は実データ用です。**Git には含めません**（`.gitignore` で無視されます）。
- リポジトリを clone したあと、初回はサンプル構造の **`data.example.csv`** をコピーして `data.csv` を作成してください。

### macOS / Linux（例）

```bash
cp data.example.csv data.csv
```

### Windows（PowerShell）

```powershell
Copy-Item data.example.csv data.csv
```

### Windows（コマンドプロンプト）

```cmd
copy data.example.csv data.csv
```

その後、アプリを起動すると空のテーブルから利用を開始できます（画面上の案内に従い、必要ならサンプル投入や手入力でデータを追加してください）。

## 起動例

```bash
pip install -r requirements.txt
streamlit run app.py
```
