import streamlit as st
import pandas as pd
from datetime import date
import os
import unicodedata
from typing import Optional, Tuple
try:
    from supabase import Client, create_client
except Exception:
    Client = object  # type: ignore[assignment]
    create_client = None  # type: ignore[assignment]

COLUMNS = ["ID", "受注日", "期限", "顧客名", "案件名", "件数", "単価", "売上", "状態", "メモ"]
STATUS_OPTIONS = ["未対応", "対応中", "保留", "確認待ち", "完了"]
SUPABASE_TABLE = "cases"

STATUS_BG = {
    "未対応":   "#FFE4E4",
    "対応中":   "#FFFBE0",
    "保留":     "#F0E8FF",
    "確認待ち": "#E4F0FF",
    "完了":     "#E4F5E4",
}
STATUS_FG = {
    "未対応":   "#B00020",
    "対応中":   "#7A5F00",
    "保留":     "#5E35B1",
    "確認待ち": "#1565C0",
    "完了":     "#1A6B1A",
}
STATUS_EMOJI = {
    "未対応":   "🔴",
    "対応中":   "🟡",
    "保留":     "🟣",
    "確認待ち": "🔵",
    "完了":     "🟢",
}

JP_FONT_STACK = (
    '"Noto Sans JP", Meiryo, "Yu Gothic UI", "MS PGothic", "Yu Gothic", sans-serif'
)

_JP_UI_STYLE = f"""
<style>
  @import url("https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;600;700&display=swap");

  /* ── 日本語フォント ── */
  html, body {{ font-family: {JP_FONT_STACK} !important; }}
  [data-testid="stAppViewContainer"],
  [data-testid="stAppViewContainer"] .stMarkdown,
  [data-testid="stAppViewContainer"] [data-testid="stMarkdownContainer"],
  [data-testid="stAppViewContainer"] [data-testid="stWidgetLabel"],
  [data-testid="stAppViewContainer"] [data-testid="stWidgetLabel"] p,
  [data-testid="stAppViewContainer"] [data-testid="stWidgetLabel"] span,
  [data-testid="stTextInput"] label, [data-testid="stTextInput"] input,
  [data-testid="stTextArea"] label, [data-testid="stTextArea"] textarea,
  [data-testid="stNumberInput"] label, [data-testid="stNumberInput"] input,
  [data-testid="stDateInput"] label, [data-testid="stDateInput"] input,
  [data-testid="stSelectbox"] label,
  [data-testid="stSelectbox"] [data-baseweb="select"],
  [data-testid="stMetricLabel"], [data-testid="stMetricValue"],
  [data-testid="stTabs"] [data-baseweb="tab"],
  [data-testid="stDataFrame"], [data-testid="stAlert"],
  [data-testid="stFormSubmitButton"] button,
  [data-testid="stAppViewContainer"] [data-baseweb="input"] {{
    font-family: {JP_FONT_STACK} !important;
  }}
  [data-testid="stAppViewContainer"] pre,
  [data-testid="stAppViewContainer"] code,
  [data-testid="stAppViewContainer"] .stCodeBlock {{
    font-family: ui-monospace, "Cascadia Code", Consolas, monospace !important;
  }}

  /* ── セクションヘッダー ── */
  .wf-section-header {{
    background: linear-gradient(90deg, #1a365d 0%, #2a69ac 100%);
    color: white;
    padding: 10px 18px;
    border-radius: 8px;
    margin: 2px 0 14px 0;
    font-weight: 700;
    font-size: 1.05rem;
    letter-spacing: 0.3px;
  }}

  /* ── KPI カード ── */
  .wf-kpi {{
    padding: 16px 20px;
    border-radius: 12px;
    border-left: 5px solid;
    box-shadow: 0 2px 8px rgba(0,0,0,0.07);
    margin-bottom: 2px;
    min-height: 84px;
  }}
  .wf-kpi-label {{
    font-size: 0.74rem;
    font-weight: 700;
    letter-spacing: 0.7px;
    text-transform: uppercase;
    margin-bottom: 6px;
    opacity: 0.78;
  }}
  .wf-kpi-value {{
    font-size: 1.85rem;
    font-weight: 800;
    line-height: 1;
  }}

  /* ── 登録・保存ボタン（フォーム送信）→ 緑 ── */
  [data-testid^="stFormSubmitButton"] button,
  [data-testid="stFormSubmitButton"] button {{
    background-color: #1a7f4b !important;
    border-color: #1a7f4b !important;
    color: white !important;
    font-weight: 700 !important;
    font-size: 1rem !important;
    border-radius: 8px !important;
    padding: 0.6rem 1.5rem !important;
    transition: all 0.18s ease !important;
  }}
  [data-testid^="stFormSubmitButton"] button:hover,
  [data-testid="stFormSubmitButton"] button:hover {{
    background-color: #15693e !important;
    border-color: #15693e !important;
    box-shadow: 0 4px 14px rgba(26,127,75,0.3) !important;
    transform: translateY(-1px) !important;
  }}

  /* ── 削除ボタン（primary type）→ 赤 ── */
  [data-testid="stBaseButton-primary"],
  button[kind="primary"] {{
    background-color: #dc3545 !important;
    border-color: #dc3545 !important;
    color: white !important;
    font-weight: 700 !important;
    border-radius: 8px !important;
    transition: all 0.18s ease !important;
  }}
  [data-testid="stBaseButton-primary"]:hover:not(:disabled),
  button[kind="primary"]:hover:not(:disabled) {{
    background-color: #c82333 !important;
    border-color: #bd2130 !important;
    box-shadow: 0 4px 14px rgba(220,53,69,0.3) !important;
    transform: translateY(-1px) !important;
  }}
  [data-testid="stBaseButton-primary"]:disabled,
  button[kind="primary"]:disabled {{
    background-color: #f5c6cb !important;
    border-color: #f5c6cb !important;
    color: #721c24 !important;
    opacity: 0.75 !important;
    cursor: not-allowed !important;
    transform: none !important;
    box-shadow: none !important;
  }}

  /* ── 通常ボタン（secondary）─ 角丸 + ホバー ── */
  [data-testid="stBaseButton-secondary"],
  button[kind="secondary"] {{
    border-radius: 8px !important;
    font-weight: 600 !important;
    transition: all 0.18s ease !important;
  }}
  [data-testid="stBaseButton-secondary"]:hover,
  button[kind="secondary"]:hover {{
    transform: translateY(-1px) !important;
    box-shadow: 0 3px 10px rgba(0,0,0,0.12) !important;
  }}

  /* ── CSVダウンロードボタン → ダークグレー ── */
  [data-testid="stDownloadButton"] button {{
    background-color: #2d3748 !important;
    border-color: #2d3748 !important;
    color: white !important;
    font-weight: 600 !important;
    border-radius: 8px !important;
    transition: all 0.18s ease !important;
  }}
  [data-testid="stDownloadButton"] button:hover {{
    background-color: #1a202c !important;
    border-color: #1a202c !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.2) !important;
  }}

  /* ── フォームコンテナ ── */
  [data-testid="stForm"] {{
    background-color: #f7f9fc !important;
    border-radius: 12px !important;
    border: 1px solid #e2e8f0 !important;
    padding: 4px 8px 8px !important;
  }}

  /* ── 入力フィールド ── */
  [data-testid="stTextInput"] input,
  [data-testid="stTextArea"] textarea {{
    border-radius: 7px !important;
    border: 1.5px solid #d1d9e0 !important;
    transition: border-color 0.15s, box-shadow 0.15s !important;
  }}
  [data-testid="stTextInput"] input:focus,
  [data-testid="stTextArea"] textarea:focus {{
    border-color: #3182ce !important;
    box-shadow: 0 0 0 3px rgba(49,130,206,0.12) !important;
  }}

  /* ── タブ（ピルスタイル）── */
  [data-baseweb="tab-list"] {{
    background: #f1f5f9 !important;
    border-radius: 10px !important;
    padding: 4px !important;
    gap: 2px !important;
  }}
  [data-baseweb="tab"] {{
    border-radius: 8px !important;
    font-weight: 600 !important;
    transition: all 0.15s !important;
  }}
  [data-baseweb="tab"][aria-selected="true"] {{
    background: white !important;
    box-shadow: 0 1px 6px rgba(0,0,0,0.1) !important;
  }}

  /* ── ガイド expander（ブルー情報ボックス）── */
  [data-testid="stExpander"] {{
    border: 1px solid #bee3f8 !important;
    border-radius: 10px !important;
    overflow: hidden !important;
  }}

  /* ── 区切り線 ── */
  hr {{
    border: none !important;
    height: 2px !important;
    background: linear-gradient(90deg, #e2e8f0 0%, #cbd5e0 50%, #e2e8f0 100%) !important;
    margin: 24px 0 !important;
    border-radius: 2px !important;
  }}

  /* ── アラートの角丸 ── */
  [data-testid="stAlert"] {{
    border-radius: 10px !important;
  }}
</style>
"""


def _inject_jp_font() -> None:
    st.markdown(_JP_UI_STYLE, unsafe_allow_html=True)


@st.cache_resource
def _get_supabase_client() -> Client:
    if create_client is None:
        raise RuntimeError("supabase パッケージが未インストールです。`pip install -r requirements.txt` を実行してください。")
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)


def _try_get_supabase_client() -> Tuple[Optional[Client], Optional[str]]:
    try:
        client = _get_supabase_client()
        return client, None
    except KeyError:
        return None, "Supabase 設定が未完了です。`st.secrets` に `SUPABASE_URL` / `SUPABASE_KEY` を設定してください。"
    except Exception as e:
        return None, f"Supabase への接続に失敗しました: {e}"


def _render_auth_gate() -> bool:
    """未ログイン時にログイン/新規登録画面を表示し、ログイン済みなら True を返す。"""
    if st.session_state.get("auth_user") is not None:
        return True

    client, err = _try_get_supabase_client()

    st.title("🔐 ログイン")
    st.caption("このアプリはログイン済みユーザーのみ利用できます。")
    st.info(
        "はじめての方へ\n\n"
        "このツールは、案件の進捗・期限・売上を管理するためのツールです。\n"
        "まずは新規登録またはログイン後、案件登録から入力してください。"
    )
    if err:
        st.error(err)
        return False

    left, center, right = st.columns([1, 1.6, 1])
    with center:
        tab_login, tab_signup = st.tabs(["ログイン", "新規登録"])

        with tab_login:
            with st.form("login_form"):
                email = st.text_input("メールアドレス", key="login_email")
                password = st.text_input(
                    "パスワード", type="password", key="login_password"
                )
                do_login = st.form_submit_button("ログイン", use_container_width=True)
                if do_login:
                    if not email.strip() or not password:
                        st.error("メールアドレスとパスワードを入力してください。")
                    else:
                        try:
                            res = client.auth.sign_in_with_password(
                                {"email": email.strip(), "password": password}
                            )
                            if res.user is None:
                                st.error("ログインできませんでした。メールアドレスやパスワードをもう一度ご確認ください。")
                            else:
                                st.session_state.auth_user = {
                                    "id": res.user.id,
                                    "email": res.user.email,
                                }
                                st.success("ログインしました。")
                                st.rerun()
                        except Exception as e:
                            msg = str(e).lower()
                            if "invalid login credentials" in msg:
                                st.error("ログインできませんでした。メールアドレスやパスワードをもう一度ご確認ください。")
                            elif "email not confirmed" in msg:
                                st.error("メール確認が未完了です。受信箱の確認メールから認証を完了してください。")
                            elif "network" in msg or "timeout" in msg:
                                st.error("通信エラーが発生しました。時間をおいて再度お試しください。")
                            else:
                                st.error("ログイン時にエラーが発生しました。時間をおいて再度お試しください。")

        with tab_signup:
            with st.form("signup_form"):
                new_email = st.text_input("メールアドレス", key="signup_email")
                new_password = st.text_input(
                    "パスワード（6文字以上）", type="password", key="signup_password"
                )
                do_signup = st.form_submit_button("新規登録", use_container_width=True)
                if do_signup:
                    if not new_email.strip() or not new_password:
                        st.error("メールアドレスとパスワードを入力してください。")
                    elif len(new_password) < 6:
                        st.error("パスワードは6文字以上にしてください。")
                    else:
                        try:
                            client.auth.sign_up(
                                {
                                    "email": new_email.strip(),
                                    "password": new_password,
                                }
                            )
                            st.success(
                                "新規登録を受け付けました。メール確認が必要な場合は受信箱を確認してください。"
                            )
                        except Exception as e:
                            msg = str(e).lower()
                            if "already registered" in msg or "already been registered" in msg:
                                st.error("このメールアドレスは既に登録されています。ログインをお試しください。")
                            elif "password" in msg and "6" in msg:
                                st.error("パスワードは6文字以上で設定してください。")
                            elif "network" in msg or "timeout" in msg:
                                st.error("通信エラーが発生しました。時間をおいて再度お試しください。")
                            else:
                                st.error("新規登録時にエラーが発生しました。入力内容を確認して再度お試しください。")

    return False


def _nk(name: str) -> str:
    return unicodedata.normalize("NFKC", str(name).strip())


def _current_user_id() -> Optional[str]:
    return st.session_state.get("auth_user", {}).get("id")


def _debug_log(msg: str) -> None:
    logs = st.session_state.setdefault("debug_logs", [])
    logs.append(msg)
    # 肥大化を防ぐ
    if len(logs) > 200:
        st.session_state.debug_logs = logs[-200:]


def _render_debug_logs() -> None:
    logs = st.session_state.get("debug_logs", [])
    with st.sidebar.expander("🛠 保存デバッグログ", expanded=False):
        if not logs:
            st.caption("まだログはありません。")
        else:
            st.code("\n".join(logs[-80:]))
        if st.button("ログをクリア", key="btn_clear_debug_logs", use_container_width=True):
            st.session_state.debug_logs = []
            st.rerun()


def _ui_id_to_uuid(ui_id: str) -> str:
    """画面表示用の WF-xxx から Supabase の UUID を引く。"""
    m = st.session_state.get("case_uuid_map", {}) or {}
    return str(m.get(ui_id, ui_id)).strip()


def _to_db_record(row: dict, user_id: str) -> dict:
    """画面用レコードを Supabase 保存形式へ変換する。"""
    juchuubi = pd.to_datetime(row.get("受注日"), errors="coerce")
    kigen = pd.to_datetime(row.get("期限"), errors="coerce")
    return {
        "user_id": user_id,
        "order_date": juchuubi.date().isoformat() if pd.notna(juchuubi) else None,
        "deadline": kigen.date().isoformat() if pd.notna(kigen) else None,
        "customer_name": str(row.get("顧客名", "")).strip(),
        "case_name": str(row.get("案件名", "")).strip(),
        "quantity": int(pd.to_numeric(row.get("件数"), errors="coerce") or 0),
        "unit_price": int(pd.to_numeric(row.get("単価"), errors="coerce") or 0),
        "revenue": int(pd.to_numeric(row.get("売上"), errors="coerce") or 0),
        "status": str(row.get("状態", "")).strip(),
        "memo": str(row.get("メモ", "")).strip(),
    }


def _from_db_records(records: list[dict]) -> Tuple[pd.DataFrame, dict[str, str]]:
    rows = []
    id_map: dict[str, str] = {}
    for r in records:
        supa_uuid = str(r.get("id") or "").strip()
        if not supa_uuid:
            continue
        ui_id = f"WF-{len(id_map) + 1:03d}"
        id_map[ui_id] = supa_uuid
        rows.append(
            {
                "ID": ui_id,
                "受注日": pd.to_datetime(r.get("order_date"), errors="coerce"),
                "期限": pd.to_datetime(r.get("deadline"), errors="coerce"),
                "顧客名": r.get("customer_name", ""),
                "案件名": r.get("case_name", ""),
                "件数": int(pd.to_numeric(r.get("quantity"), errors="coerce") or 0),
                "単価": int(pd.to_numeric(r.get("unit_price"), errors="coerce") or 0),
                "売上": int(pd.to_numeric(r.get("revenue"), errors="coerce") or 0),
                "状態": r.get("status", ""),
                "メモ": r.get("memo", ""),
            }
        )

    if not rows:
        return pd.DataFrame(columns=COLUMNS), {}
    df = pd.DataFrame(rows)
    for col in COLUMNS:
        if col not in df.columns:
            df[col] = None
    df["受注日"] = pd.to_datetime(df["受注日"], errors="coerce")
    df["期限"] = pd.to_datetime(df["期限"], errors="coerce")
    df["件数"] = pd.to_numeric(df["件数"], errors="coerce").fillna(0).astype(int)
    df["単価"] = pd.to_numeric(df["単価"], errors="coerce").fillna(0).astype(int)
    df["売上"] = pd.to_numeric(df["売上"], errors="coerce").fillna(0).astype(int)
    df["メモ"] = df["メモ"].fillna("").astype(str).replace("nan", "")
    return df[COLUMNS], id_map


# ── ID 管理 ────────────────────────────────────────────────────
def _next_id(df: pd.DataFrame) -> str:
    if len(df) == 0 or "ID" not in df.columns:
        return "WF-001"
    nums = (
        df["ID"]
        .dropna()
        .astype(str)
        .str.extract(r"WF-(\d+)", expand=False)
        .dropna()
        .astype(int)
    )
    return f"WF-{(nums.max() + 1 if len(nums) > 0 else 1):03d}"


# ── データ読み書き ──────────────────────────────────────────────
def load_data(user_id: str) -> pd.DataFrame:
    client, err = _try_get_supabase_client()
    if err or client is None:
        st.error(err or "Supabase クライアントの初期化に失敗しました。")
        return pd.DataFrame(columns=COLUMNS)
    try:
        res = (
            client.table(SUPABASE_TABLE)
            .select(
                "id,order_date,deadline,customer_name,case_name,quantity,unit_price,revenue,status,memo,created_at"
            )
            .eq("user_id", user_id)
            .order("created_at")
            .execute()
        )
        records = res.data if res and res.data else []
        df, id_map = _from_db_records(records)
        st.session_state.case_uuid_map = id_map
        return df
    except Exception as e:
        st.error(f"データ読み込みに失敗しました: {e}")
        return pd.DataFrame(columns=COLUMNS)


def _insert_case(row: dict, user_id: str) -> bool:
    _debug_log(f"[insert] called id={row.get('ID')!r} user_id={user_id!r}")
    client, err = _try_get_supabase_client()
    if err or client is None:
        _debug_log(f"[insert] supabase client error: {err!r}")
        st.error(err or "Supabase クライアントの初期化に失敗しました。")
        return False
    try:
        payload = _to_db_record(row, user_id)
        _debug_log(f"[insert] payload={payload!r}")
        ins_res = client.table(SUPABASE_TABLE).insert(payload).execute()
        _debug_log(
            f"[insert] success returned_rows={len(ins_res.data) if getattr(ins_res, 'data', None) else 0}"
        )
        return True
    except Exception as e:
        _debug_log(f"[insert] exception type={type(e).__name__} detail={e!r}")
        st.error(f"データ登録に失敗しました。詳細: {type(e).__name__}: {e}")
        return False


def _update_case(case_id: str, updates: dict, user_id: str) -> bool:
    _debug_log(f"[update] called uuid={case_id!r} user_id={user_id!r}")
    client, err = _try_get_supabase_client()
    if err or client is None:
        _debug_log(f"[update] supabase client error: {err!r}")
        st.error(err or "Supabase クライアントの初期化に失敗しました。")
        return False
    try:
        # 部分更新（例: 期限だけ削除）でも他フィールドを消さないよう、
        # まず既存レコードを取得してマージしてから update する。
        existing_res = (
            client.table(SUPABASE_TABLE)
            .select(
                "order_date,deadline,customer_name,case_name,quantity,unit_price,revenue,status,memo"
            )
            .eq("user_id", user_id)
            .eq("id", case_id)
            .execute()
        )
        existing = (existing_res.data or [None])[0]
        if not existing:
            raise RuntimeError("更新対象のレコードが見つかりません。")

        merged_row = {
            "受注日": existing.get("order_date"),
            "期限": existing.get("deadline"),
            "顧客名": existing.get("customer_name", ""),
            "案件名": existing.get("case_name", ""),
            "件数": existing.get("quantity", 0),
            "単価": existing.get("unit_price", 0),
            "売上": existing.get("revenue", 0),
            "状態": existing.get("status", ""),
            "メモ": existing.get("memo", ""),
        }
        # updates（例: {"期限": pd.NaT}）で上書き
        merged_row.update(updates)

        payload = _to_db_record(merged_row, user_id)
        payload.pop("user_id", None)
        _debug_log(f"[update] payload={payload!r}")
        upd_res = (
            client.table(SUPABASE_TABLE)
            .update(payload)
            .eq("user_id", user_id)
            .eq("id", case_id)
            .execute()
        )
        _debug_log(
            f"[update] success returned_rows={len(upd_res.data) if getattr(upd_res, 'data', None) else 0}"
        )
        return True
    except Exception as e:
        _debug_log(f"[update] exception type={type(e).__name__} detail={e!r}")
        st.error(f"データ更新に失敗しました。詳細: {type(e).__name__}: {e}")
        return False


def _delete_case(case_id: str, user_id: str) -> bool:
    _debug_log(f"[delete] called uuid={case_id!r} user_id={user_id!r}")
    client, err = _try_get_supabase_client()
    if err or client is None:
        _debug_log(f"[delete] supabase client error: {err!r}")
        st.error(err or "Supabase クライアントの初期化に失敗しました。")
        return False
    try:
        del_res = (
            client.table(SUPABASE_TABLE)
            .delete()
            .eq("user_id", user_id)
            .eq("id", case_id)
            .execute()
        )
        _debug_log(
            f"[delete] success returned_rows={len(del_res.data) if getattr(del_res, 'data', None) else 0}"
        )
        return True
    except Exception as e:
        _debug_log(f"[delete] exception type={type(e).__name__} detail={e!r}")
        st.error(f"データ削除に失敗しました。詳細: {type(e).__name__}: {e}")
        return False


def _add_sample_data() -> None:
    """デモ用サンプルデータを3件追加する（空の状態でのみ呼び出す想定）。"""
    today = date.today()
    rows = [
        {
            "ID":     "WF-001",
            "受注日": pd.Timestamp(today),
            "期限":   pd.Timestamp(today) + pd.Timedelta(days=7),
            "顧客名": "株式会社サンプル",
            "案件名": "Webサイト制作",
            "件数":   1,
            "単価":   500_000,
            "売上":   500_000,
            "状態":   "対応中",
            "メモ":   "デザイン確認待ち",
        },
        {
            "ID":     "WF-002",
            "受注日": pd.Timestamp(today) - pd.Timedelta(days=5),
            "期限":   pd.Timestamp(today) + pd.Timedelta(days=14),
            "顧客名": "テスト商事",
            "案件名": "システム開発",
            "件数":   3,
            "単価":   200_000,
            "売上":   600_000,
            "状態":   "未対応",
            "メモ":   "",
        },
        {
            "ID":     "WF-003",
            "受注日": pd.Timestamp(today) - pd.Timedelta(days=30),
            "期限":   pd.NaT,
            "顧客名": "デモ株式会社",
            "案件名": "月次保守契約",
            "件数":   12,
            "単価":   50_000,
            "売上":   600_000,
            "状態":   "完了",
            "メモ":   "毎月自動更新",
        },
    ]
    user_id = _current_user_id()
    if not user_id:
        return
    ok = True
    for row in rows:
        if not _insert_case(row, user_id):
            ok = False
            break
    if ok:
        st.session_state.df = load_data(user_id)


# ── ユーティリティ ─────────────────────────────────────────────
def _fmt_date(val) -> str:
    try:
        ts = pd.Timestamp(val)
        return ts.strftime("%Y-%m-%d") if pd.notna(ts) else "―"
    except Exception:
        return "―"


def _build_styled_table(data: pd.DataFrame) -> "pd.io.formats.style.Styler":
    d = data.copy()
    d["受注日"] = d["受注日"].apply(_fmt_date)
    d["期限"]   = d["期限"].apply(_fmt_date)
    d["単価"]   = d["単価"].apply(lambda x: f"{int(x):,} 円")
    d["売上"]   = d["売上"].apply(lambda x: f"{int(x):,} 円")

    def _color(val: str) -> str:
        bg = STATUS_BG.get(val, "")
        fg = STATUS_FG.get(val, "")
        return f"background-color:{bg}; color:{fg}; font-weight:700;" if bg else ""

    styler = d.style
    try:
        return styler.map(_color, subset=["状態"])
    except AttributeError:
        return styler.applymap(_color, subset=["状態"])


def _apply_sort(data: pd.DataFrame, opt: str) -> pd.DataFrame:
    if opt == "期限が近い順":
        has  = data[data["期限"].notna()].sort_values("期限")
        none = data[data["期限"].isna()]
        return pd.concat([has, none])
    if opt == "期限が遠い順":
        has  = data[data["期限"].notna()].sort_values("期限", ascending=False)
        none = data[data["期限"].isna()]
        return pd.concat([has, none])
    if opt == "受注日（新しい順）":
        return data.sort_values("受注日", ascending=False, na_position="last")
    if opt == "受注日（古い順）":
        return data.sort_values("受注日", ascending=True, na_position="last")
    try:
        return data.sort_values(
            "ID",
            key=lambda s: s.astype(str)
            .str.extract(r"(\d+)", expand=False)
            .fillna("0")
            .astype(int),
        )
    except Exception:
        return data


def _to_csv_bytes(data: pd.DataFrame) -> bytes:
    out = data.copy()
    out["受注日"] = pd.to_datetime(out["受注日"]).dt.strftime("%Y-%m-%d")
    kigen = pd.to_datetime(out["期限"])
    out["期限"] = kigen.dt.strftime("%Y-%m-%d").where(kigen.notna(), "")
    return out.to_csv(index=False).encode("utf-8-sig")


def _validate_dates(juchuubi: date, kigen) -> str | None:
    """期限が受注日より前ならエラーメッセージを返す。問題なければ None。"""
    if kigen and kigen < juchuubi:
        return "期限は受注日（{}）より後の日付を設定してください。".format(
            juchuubi.strftime("%Y-%m-%d")
        )
    return None


def _case_name_label() -> None:
    _ff = JP_FONT_STACK.replace('"', "&quot;")
    st.markdown(
        f'<p style="font-family:{_ff} !important; font-size:0.875rem;'
        f' font-weight:600; margin:0 0 0.35rem 0;">案件名</p>',
        unsafe_allow_html=True,
    )


def _status_badge(case_id: str, status: str, customer: str, case: str,
                  juchuubi, kigen) -> None:
    bg    = STATUS_BG.get(status, "#F5F5F5")
    fg    = STATUS_FG.get(status, "#333")
    emoji = STATUS_EMOJI.get(status, "")
    st.markdown(
        f'<div style="background:{bg}; border-left:4px solid {fg}; padding:10px 16px;'
        f' border-radius:6px; margin:8px 0;">'
        f'<code style="background:transparent; color:{fg}; font-weight:700;">{case_id}</code>'
        f' ｜ <span style="color:{fg}; font-weight:700;">{emoji} {status}</span>'
        f' ｜ {customer} ｜ {case}'
        f' ｜ 受注日: {_fmt_date(juchuubi)}'
        f' ｜ 期限: {_fmt_date(kigen)}'
        f'</div>',
        unsafe_allow_html=True,
    )


# ── メイン ─────────────────────────────────────────────────────
def main():
    st.set_page_config(page_title="案件管理ツール", page_icon="📋", layout="wide")
    _inject_jp_font()

    if not _render_auth_gate():
        _inject_jp_font()
        return

    user_email = st.session_state.get("auth_user", {}).get("email", "")
    st.sidebar.markdown("### アカウント")
    if user_email:
        st.sidebar.caption(f"ログイン中: {user_email}")
    _render_debug_logs()
    if st.sidebar.button("ログアウト", use_container_width=True):
        client, _ = _try_get_supabase_client()
        if client is not None:
            try:
                client.auth.sign_out()
            except Exception:
                pass
        st.session_state.auth_user = None
        st.session_state.loaded_user_id = None
        st.session_state.df = pd.DataFrame(columns=COLUMNS)
        st.session_state.debug_logs = []
        st.rerun()

    st.title("📋 案件管理ツール")
    st.caption(
        "はじめての方へ：このツールは案件の進捗・期限・売上を管理するためのツールです。"
        " まずは「1️⃣ 案件登録」から入力してください。"
    )
    user_id = _current_user_id()
    if not user_id:
        st.error("ユーザー情報を取得できません。再ログインしてください。")
        return

    if "loaded_user_id" not in st.session_state:
        st.session_state.loaded_user_id = None
    if ("df" not in st.session_state) or (st.session_state.loaded_user_id != user_id):
        st.session_state.df = load_data(user_id)
        st.session_state.loaded_user_id = user_id
    if "editing_id" not in st.session_state:
        st.session_state.editing_id = None

    df       = st.session_state.df
    today    = date.today()
    today_ts = pd.Timestamp(today)
    cnt      = (
        {s: len(df[df["状態"] == s]) for s in STATUS_OPTIONS}
        if len(df) > 0
        else {s: 0 for s in STATUS_OPTIONS}
    )

    # ── 初回ガイド ────────────────────────────────────────────
    with st.expander("📖 このツールの使い方", expanded=(len(df) == 0)):
        st.markdown("""
**案件管理ツール**は、受注した案件を一元管理するシンプルなツールです。

| ステップ | 操作 |
|---|---|
| **1️⃣ 案件登録** | 顧客名・案件名・受注日などを入力して登録します |
| **2️⃣ 案件一覧** | 登録済みの案件を検索・絞り込み・並び替えで確認できます |
| **3️⃣ 編集・削除** | IDで案件を選んで内容を修正したり、削除できます |

**状態の種類：**
🔴 未対応 ／ 🟡 対応中 ／ 🟣 保留 ／ 🔵 確認待ち ／ 🟢 完了

**その他のポイント：**
- 各案件に `WF-001` 形式の一意IDが自動で付きます
- 期限が設定された案件は、期限切れ・3日前になると画面上部にアラートが表示されます
- データは Supabase の `cases` テーブルに保存されます（ユーザーごとに分離）
        """)

    # ── アラート ──────────────────────────────────────────────
    if len(df) > 0:
        active   = df[df["状態"] != "完了"]
        overdue  = active[active["期限"].notna() & (active["期限"] < today_ts)]
        due_soon = active[
            active["期限"].notna()
            & (active["期限"] >= today_ts)
            & (active["期限"] <= today_ts + pd.Timedelta(days=3))
        ]
        if len(overdue) > 0:
            st.error(f"🚨 期限切れの案件が {len(overdue)} 件あります！早急に対応してください。")
        if len(due_soon) > 0:
            st.warning(f"⚠️ 3日以内に期限を迎える案件が {len(due_soon)} 件あります。")
        if len(overdue) == 0 and len(due_soon) == 0:
            if cnt["未対応"] > 0:
                st.warning(f"⚠️ 未対応の案件が {cnt['未対応']} 件あります。確認してください。")
            else:
                st.success("✅ 未対応・期限切れの案件はありません。")
    else:
        st.info(
            "案件データはまだ0件です。\n\n"
            "はじめて使う場合は、次のどちらかで開始できます。\n"
            "・下の「1️⃣ 案件登録」から1件登録する\n"
            "・「📥 サンプルデータを追加する（3件）」で動作を試す"
        )
        if st.button("📥 サンプルデータを追加する（3件）", key="btn_sample"):
            _add_sample_data()
            st.success("サンプルデータを3件追加しました！")
            st.rerun()

    # ── KPI ──────────────────────────────────────────────────
    kc1, kc2, kc3 = st.columns(3)
    kc1.metric("総案件数", f"{len(df)} 件")
    kc2.metric("⏳ 進行中", f"{cnt['対応中'] + cnt['保留'] + cnt['確認待ち']} 件")
    kc3.metric("💰 総売上", f"{int(df['売上'].sum()):,} 円" if len(df) else "0 円")

    sc = st.columns(5)
    for i, s in enumerate(STATUS_OPTIONS):
        sc[i].metric(f"{STATUS_EMOJI[s]} {s}", f"{cnt[s]} 件")

    st.markdown("---")

    # ═══════════════════════════════════════════════════════════
    # 1️⃣  案件登録
    # ═══════════════════════════════════════════════════════════
    st.subheader("1️⃣  案件登録")
    with st.form("registration_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            inp_juchuubi = st.date_input("受注日", value=today)
            inp_kigen    = st.date_input("期限（任意）", value=None)
            inp_customer = st.text_input("顧客名", placeholder="例：株式会社ABC")
            _case_name_label()
            inp_case = st.text_input(
                "案件名",
                placeholder="例：Webサイト制作",
                label_visibility="collapsed",
                key="reg_case_name",
            )
        with c2:
            inp_count  = st.number_input("件数", min_value=0, value=1, step=1)
            inp_price  = st.number_input("単価（円）", min_value=0, value=0, step=1000)
            inp_status = st.selectbox("状態", STATUS_OPTIONS)
            inp_memo   = st.text_area(
                "メモ", placeholder="補足情報があれば入力してください", height=120
            )

        revenue = inp_count * inp_price
        st.info(f"💴 売上（自動計算）：**{revenue:,} 円**")

        if st.form_submit_button("登録する", use_container_width=True):
            # ── バリデーション（エラー）
            errors = []
            if not inp_customer.strip():
                errors.append("顧客名を入力してください。")
            if not inp_case.strip():
                errors.append("案件名を入力してください。")
            date_err = _validate_dates(inp_juchuubi, inp_kigen)
            if date_err:
                errors.append(date_err)

            if errors:
                for e in errors:
                    st.error(e)
            else:
                # ── ソフト警告（保存は続行）
                if inp_count == 0:
                    st.toast("⚠️ 件数が0件で登録されました。後から編集できます。")
                if inp_price == 0:
                    st.toast("⚠️ 単価が0円で登録されました。売上も0円になります。")

                new_id = _next_id(st.session_state.df)
                new_row = pd.DataFrame([{
                    "ID":     new_id,
                    "受注日": pd.Timestamp(inp_juchuubi),
                    "期限":   pd.Timestamp(inp_kigen) if inp_kigen else pd.NaT,
                    "顧客名": inp_customer.strip(),
                    "案件名": inp_case.strip(),
                    "件数":   inp_count,
                    "単価":   inp_price,
                    "売上":   revenue,
                    "状態":   inp_status,
                    "メモ":   inp_memo.strip(),
                }])
                st.session_state.df = pd.concat(
                    [st.session_state.df, new_row], ignore_index=True
                )
                _debug_log(f"[register] insert start new_id={new_id} user_id={user_id!r}")
                if _insert_case(new_row.iloc[0].to_dict(), user_id):
                    st.success(f"✅ 案件を登録しました！（ID: {new_id}）")
                    st.session_state.df = load_data(user_id)
                    st.rerun()
                # DB保存失敗時はローカル差分を戻す
                st.session_state.df = st.session_state.df.iloc[:-1].reset_index(drop=True)

    st.markdown("---")
    df = st.session_state.df

    # ═══════════════════════════════════════════════════════════
    # 2️⃣  案件一覧
    # ═══════════════════════════════════════════════════════════
    st.subheader("2️⃣  案件一覧")

    if len(df) == 0:
        st.info("まだ案件が登録されていません。")
    else:
        # ── 検索・絞り込み・並び替え
        fc1, fc2, fc3 = st.columns([3, 3, 2])
        with fc1:
            search_q = st.text_input(
                "🔍 顧客名・案件名で検索",
                placeholder="キーワードを入力（部分一致）",
                key="search_q",
            )
        with fc2:
            status_filter = st.multiselect(
                "状態で絞り込み",
                STATUS_OPTIONS,
                default=STATUS_OPTIONS,
                key="status_filter",
            )
        with fc3:
            sort_opt = st.selectbox(
                "並び替え",
                ["登録順（ID順）", "期限が近い順", "期限が遠い順",
                 "受注日（新しい順）", "受注日（古い順）"],
                key="sort_opt",
            )

        # ── フィルター適用
        view_df = df.copy()
        if search_q.strip():
            q = search_q.strip()
            view_df = view_df[
                view_df["顧客名"].str.contains(q, na=False, case=False)
                | view_df["案件名"].str.contains(q, na=False, case=False)
            ]
        if status_filter:
            view_df = view_df[view_df["状態"].isin(status_filter)]
        view_df = _apply_sort(view_df, sort_opt)

        filtered = len(view_df) < len(df)
        st.caption(
            f"表示中: {len(view_df)} 件 / 全 {len(df)} 件"
            + (" （絞り込み中）" if filtered else "")
        )

        # ── 状態別タブ
        cnt_v = {s: len(view_df[view_df["状態"] == s]) for s in STATUS_OPTIONS}
        tabs = st.tabs([
            f"すべて ({len(view_df)})",
            f"🔴 未対応 ({cnt_v['未対応']})",
            f"🟡 対応中 ({cnt_v['対応中']})",
            f"🟣 保留 ({cnt_v['保留']})",
            f"🔵 確認待ち ({cnt_v['確認待ち']})",
            f"🟢 完了 ({cnt_v['完了']})",
        ])

        def render_table(data: pd.DataFrame) -> None:
            if len(data) == 0:
                st.info("該当する案件はありません。")
                return
            st.dataframe(
                _build_styled_table(data), use_container_width=True, hide_index=True
            )

        with tabs[0]:
            render_table(view_df)
        with tabs[1]:
            render_table(view_df[view_df["状態"] == "未対応"])
        with tabs[2]:
            render_table(view_df[view_df["状態"] == "対応中"])
        with tabs[3]:
            render_table(view_df[view_df["状態"] == "保留"])
        with tabs[4]:
            render_table(view_df[view_df["状態"] == "確認待ち"])
        with tabs[5]:
            render_table(view_df[view_df["状態"] == "完了"])

        # ── CSV ダウンロード
        label = "表示中のデータ" if filtered else "全データ"
        st.download_button(
            f"📥 {label}をCSVでダウンロード（{len(view_df)} 件）",
            data=_to_csv_bytes(view_df),
            file_name=f"案件一覧_{today}.csv",
            mime="text/csv",
            use_container_width=True,
        )

    st.markdown("---")

    # ═══════════════════════════════════════════════════════════
    # 3️⃣  編集・削除
    # ═══════════════════════════════════════════════════════════
    st.subheader("3️⃣  編集・削除")

    if len(df) == 0:
        st.info("操作する案件がありません。")
        _inject_jp_font()
        return

    st.caption("IDドロップダウンから操作したい案件を選択してください。")

    case_options = df.apply(
        lambda r: (
            f"{r['ID']} ｜ {r['顧客名']} ｜ {r['案件名']}"
            f" ｜ {STATUS_EMOJI.get(r['状態'], '')} {r['状態']}"
        ),
        axis=1,
    ).tolist()

    sel_opt = st.selectbox("操作する案件を選択", case_options, key="sel_case_opt")
    sel_id  = sel_opt.split(" ｜ ")[0].strip()

    sel_mask = df["ID"] == sel_id
    if not sel_mask.any():
        st.error("選択した案件が見つかりません。")
        _inject_jp_font()
        return

    sel_real_idx = df[sel_mask].index[0]
    sel_row      = df.loc[sel_real_idx]

    _status_badge(
        sel_id, sel_row["状態"], sel_row["顧客名"], sel_row["案件名"],
        sel_row["受注日"], sel_row["期限"],
    )

    col_edit_btn, col_del_area = st.columns(2)
    with col_edit_btn:
        if st.button("✏️ この案件を編集する", use_container_width=True, key="btn_edit"):
            st.session_state.editing_id = sel_id
            st.rerun()

    with col_del_area:
        confirm_del = st.checkbox("削除を確認する（元に戻せません）", key="del_confirm")
        if st.button(
            "🗑️ この案件を削除する",
            use_container_width=True,
            type="primary",
            disabled=not confirm_del,
            key="btn_delete",
        ):
            if st.session_state.editing_id == sel_id:
                st.session_state.editing_id = None
            if _delete_case(_ui_id_to_uuid(sel_id), user_id):
                st.session_state.df = df.drop(sel_real_idx).reset_index(drop=True)
                st.success(f"🗑️ {sel_id} を削除しました。")
                st.rerun()

    # ── 編集フォーム ──────────────────────────────────────────
    if st.session_state.editing_id is not None:
        edit_id   = st.session_state.editing_id
        edit_df   = st.session_state.df
        edit_mask = edit_df["ID"] == edit_id

        if not edit_mask.any():
            st.session_state.editing_id = None
            st.rerun()

        edit_real_idx = edit_df[edit_mask].index[0]
        edit_row      = edit_df.loc[edit_real_idx]

        st.markdown("---")
        st.subheader(
            f"✏️ 編集中：{edit_id} ｜ {edit_row['顧客名']} ｜ {edit_row['案件名']}"
        )

        with st.form(f"edit_form_{edit_id}"):
            ec1, ec2 = st.columns(2)
            with ec1:
                e_juchuubi = st.date_input(
                    "受注日",
                    value=edit_row["受注日"].date()
                    if pd.notna(edit_row["受注日"])
                    else today,
                )
                e_kigen = st.date_input(
                    "期限（任意）",
                    value=edit_row["期限"].date()
                    if pd.notna(edit_row["期限"])
                    else None,
                )
                e_customer = st.text_input("顧客名", value=str(edit_row["顧客名"]))
                _case_name_label()
                e_case = st.text_input(
                    "案件名",
                    value=str(edit_row["案件名"]),
                    label_visibility="collapsed",
                    key=f"edit_case_{edit_id}",
                )
            with ec2:
                e_count = st.number_input(
                    "件数", min_value=0, value=int(edit_row["件数"]), step=1
                )
                e_price = st.number_input(
                    "単価（円）", min_value=0, value=int(edit_row["単価"]), step=1000
                )
                status_i = (
                    STATUS_OPTIONS.index(edit_row["状態"])
                    if edit_row["状態"] in STATUS_OPTIONS
                    else 0
                )
                e_status = st.selectbox("状態", STATUS_OPTIONS, index=status_i)
                e_memo = st.text_area(
                    "メモ",
                    value=str(edit_row["メモ"]) if pd.notna(edit_row["メモ"]) else "",
                    height=120,
                )

            e_revenue = e_count * e_price
            st.info(f"💴 売上：{e_revenue:,} 円")

            if st.form_submit_button("💾 変更を保存", use_container_width=True):
                # ── バリデーション（エラー）
                errors = []
                if not e_customer.strip():
                    errors.append("顧客名を入力してください。")
                if not e_case.strip():
                    errors.append("案件名を入力してください。")
                date_err = _validate_dates(e_juchuubi, e_kigen)
                if date_err:
                    errors.append(date_err)

                if errors:
                    for e in errors:
                        st.error(e)
                else:
                    # ── ソフト警告（保存は続行）
                    if e_count == 0:
                        st.toast("⚠️ 件数が0件で保存されました。")
                    if e_price == 0:
                        st.toast("⚠️ 単価が0円で保存されました。売上も0円になります。")

                    updates = {
                        "受注日": pd.Timestamp(e_juchuubi),
                        "期限":   pd.Timestamp(e_kigen) if e_kigen else pd.NaT,
                        "顧客名": e_customer.strip(),
                        "案件名": e_case.strip(),
                        "件数":   int(e_count),
                        "単価":   int(e_price),
                        "売上":   int(e_revenue),
                        "状態":   e_status,
                        "メモ":   e_memo.strip(),
                    }
                    if _update_case(_ui_id_to_uuid(edit_id), updates, user_id):
                        for col, val in updates.items():
                            st.session_state.df.at[edit_real_idx, col] = val
                        st.session_state.editing_id = None
                        st.success("✅ 変更を保存しました！")
                        st.rerun()

        col_cancel, col_clear = st.columns(2)
        with col_cancel:
            if st.button("✖ キャンセル", key="btn_cancel_edit", use_container_width=True):
                st.session_state.editing_id = None
                st.rerun()
        with col_clear:
            if pd.notna(edit_row["期限"]) and st.button(
                "📅 期限を削除する", key="btn_clear_deadline", use_container_width=True
            ):
                if _update_case(_ui_id_to_uuid(edit_id), {"期限": pd.NaT}, user_id):
                    st.session_state.df.at[edit_real_idx, "期限"] = pd.NaT
                    st.success("期限を削除しました。")
                    st.rerun()

    _inject_jp_font()


if __name__ == "__main__":
    main()
