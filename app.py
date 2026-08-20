import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, date, timedelta
import os
import json
import glob
import psycopg2

# ─── PAGE CONFIG ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="FunzAI — Channel Dashboard",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── PASSWORD GATE ────────────────────────────────────────────────────────────
def _check_password():
    if st.session_state.get("authenticated"):
        return True
    col_l, col_c, col_r = st.columns([1, 2, 1])
    with col_c:
        logo = os.path.join(os.path.dirname(__file__), "..", "logos", "funza_logo_transparent.png")
        if os.path.exists(logo):
            st.image(logo, use_container_width=True)
        st.markdown(
            "<h1 style='text-align:center; color:#de0f3f; letter-spacing:0.04em;'>FunzAI</h1>"
            "<p style='text-align:center; color:#888; margin-top:-0.6rem; margin-bottom:1.5rem;'>Channel Dashboard</p>",
            unsafe_allow_html=True,
        )
        pw = st.text_input("Password", type="password", placeholder="Enter password to continue")
        if pw:
            if pw == st.secrets["app"]["password"]:
                st.session_state["authenticated"] = True
                st.rerun()
            else:
                st.error("Incorrect password.")
    st.stop()

_check_password()

# ─── CSS ──────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main-header { color: #de0f3f; font-size: 1.7rem; font-weight: 700; margin-bottom: 0.1rem; }
    .sub-header  { color: #888; font-size: 0.82rem; margin-bottom: 1.5rem; }
    .section-head {
        color: #de0f3f; font-size: 0.95rem; font-weight: 700; letter-spacing: 0.08em;
        border-bottom: 1px solid #de0f3f; padding-bottom: 4px; margin: 1.4rem 0 0.8rem 0;
    }
    .sb-card {
        background: #1e1e2e; border-radius: 8px;
        padding: 0.75rem 1rem; margin: 0.4rem 0 0.8rem 0;
        color: #f0f0f0 !important;
    }
    .sb-label {
        font-size: 0.65rem; color: #aaa !important; letter-spacing: 0.1em;
        text-transform: uppercase; margin-bottom: 0.5rem;
    }
    .sb-row {
        font-size: 0.85rem; line-height: 2.0; color: #f0f0f0 !important;
    }
    .sb-row strong { color: #ffffff !important; font-weight: 700; }
    .sb-protected {
        background: #de0f3f; color: #fff !important; font-weight: 700; font-size: 0.82rem;
        border-radius: 4px; padding: 4px 10px; display: inline-block; margin-top: 8px;
        letter-spacing: 0.04em;
    }
    .north-star {
        background: linear-gradient(135deg, #1e1e2e 0%, #2a1520 100%);
        border: 2px solid #de0f3f; border-radius: 12px;
        padding: 1.5rem 2rem; margin-bottom: 1.5rem; text-align: center;
    }
    .north-star .ns-label { font-size: 0.75rem; color: #aaa; letter-spacing: 0.12em; text-transform: uppercase; }
    .north-star .ns-value { font-size: 2.8rem; font-weight: 800; color: #de0f3f; line-height: 1.1; }
    .north-star .ns-sub   { font-size: 1.0rem; color: #ccc; margin-top: 0.3rem; }
    .rev-card {
        background: #1e1e2e; border-radius: 10px;
        padding: 1.2rem 1.4rem; margin-bottom: 1rem;
        border-left: 4px solid #de0f3f;
    }
    .rev-card.cat2 { border-left-color: #00b894; }
    .rev-card h4 { color: #fff; margin: 0 0 0.6rem 0; font-size: 1.0rem; }
    .rev-card ul { color: #ccc; font-size: 0.85rem; margin: 0; padding-left: 1.2rem; line-height: 2.0; }
    .milestone-row {
        display: flex; align-items: flex-start; gap: 1rem;
        padding: 0.75rem 0; border-bottom: 1px solid #2a2a3e;
    }
    .milestone-dot {
        width: 12px; height: 12px; border-radius: 50%;
        background: #de0f3f; margin-top: 5px; flex-shrink: 0;
    }
    .milestone-dot.done  { background: #00b894; }
    .milestone-dot.ahead { background: #aaa; }
    .threshold-note { font-size: 0.72rem; color: #888; margin-top: -0.4rem; margin-bottom: 0.6rem; }
    .threshold-red  { font-size: 0.72rem; color: #ff6b6b; margin-top: -0.4rem; margin-bottom: 0.6rem; }
    .bench-table { width: 100%; border-collapse: collapse; font-size: 0.85rem; }
    .bench-table th { background: #1e1e2e; color: #de0f3f; padding: 8px 12px; text-align: left; font-weight: 600; }
    .bench-table td { padding: 7px 12px; border-bottom: 1px solid #2a2a3e; color: #e0e0e0; background: #12121e; }
    .bench-table tr:last-child td { border-bottom: none; }
    .bench-table td:first-child { color: #ffffff; font-weight: 600; }
    .bench-table td:nth-child(2) { color: #f5a623; font-weight: 700; }
    .bench-table td:nth-child(3) { color: #b8e0b8; font-weight: 500; }
    .rev-table { width: 100%; border-collapse: collapse; font-size: 0.84rem; margin-bottom: 1.5rem; }
    .rev-table th { background: #1e1e2e; color: #de0f3f; padding: 9px 12px; text-align: left; font-weight: 600; letter-spacing: 0.04em; }
    .rev-table td { padding: 9px 12px; border-bottom: 1px solid #2a2a3e; vertical-align: top; color: #e0e0e0; line-height: 1.5; background: #12121e; }
    .rev-table tr:last-child td { border-bottom: none; }
    .rev-table td:first-child { color: #ffffff; font-weight: 700; white-space: nowrap; width: 16%; }
    .rev-table td:nth-child(2) { color: #ccc; width: 34%; }
    .rev-table td:nth-child(3) { color: #b8e0b8; width: 50%; }
    .rev-table tr:hover td { background: #1a1a2e; }
    .name-hi   { color: #f5a623; font-weight: 700; }
    .okr-obj   { font-size: 0.85rem; color: #aaa; font-style: italic; margin-bottom: 0.8rem; }
    .kr-label  { font-size: 0.88rem; color: #e0e0e0; margin-bottom: 0.3rem; font-weight: 600; }
    .kr-status { font-size: 0.76rem; color: #aaa; margin-top: 0.15rem; }

    /* ── Intelligence tab ─────────────────────────────────────────── */
    .perf-card {
        background: #1a1a2e; border-radius: 10px;
        padding: 1rem 1.2rem; margin-bottom: 0.75rem;
        border-left: 4px solid #00b894;
    }
    .perf-card.bottom { border-left-color: #ff6b6b; }
    .perf-rank  { font-size: 0.7rem; color: #aaa; letter-spacing: 0.08em; text-transform: uppercase; margin-bottom: 0.25rem; }
    .perf-title { font-size: 0.92rem; font-weight: 700; color: #fff; line-height: 1.35; margin-bottom: 0.6rem; }
    .perf-cat   {
        font-size: 0.65rem; font-weight: 700; letter-spacing: 0.06em;
        background: #de0f3f; color: #fff; border-radius: 3px;
        padding: 2px 7px; display: inline-block; margin-bottom: 0.55rem;
    }
    .perf-metrics { display: flex; gap: 1.2rem; flex-wrap: wrap; margin-top: 0.4rem; }
    .perf-metric .pm-val { font-size: 1.0rem; font-weight: 700; color: #fff; display: block; }
    .perf-metric .pm-lbl { font-size: 0.62rem; color: #888; text-transform: uppercase; letter-spacing: 0.07em; display: block; }
    .perf-score { font-size: 0.7rem; color: #555; margin-top: 0.55rem; }

    .outlier-card {
        background: #1a1a2e; border-radius: 8px;
        padding: 0.85rem 1rem; margin-bottom: 0.6rem;
        border-left: 3px solid #f5a623;
    }
    .outlier-card.warn { border-left-color: #ff6b6b; }
    .outlier-label { font-size: 0.65rem; color: #aaa; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 0.2rem; }
    .outlier-value { font-size: 1.3rem; font-weight: 800; color: #f5a623; line-height: 1.1; }
    .outlier-card.warn .outlier-value { color: #ff6b6b; }
    .outlier-title { font-size: 0.8rem; color: #ccc; margin-top: 0.3rem; line-height: 1.3; }
    .outlier-note  { font-size: 0.72rem; color: #777; margin-top: 0.25rem; line-height: 1.4; }

    .pattern-item {
        background: #1a1a2e; border-radius: 7px;
        padding: 0.65rem 0.9rem; margin-bottom: 0.45rem;
        font-size: 0.83rem; color: #ccc; line-height: 1.45;
        border-left: 3px solid #4e8cff;
    }
    .rec-item {
        background: #1a2e1a; border-radius: 7px;
        padding: 0.65rem 0.9rem; margin-bottom: 0.45rem;
        font-size: 0.83rem; color: #ccc; line-height: 1.45;
        border-left: 3px solid #00b894;
    }
    .rec-num { font-size: 0.65rem; font-weight: 700; color: #00b894; text-transform: uppercase; letter-spacing: 0.08em; display: block; margin-bottom: 0.2rem; }
</style>
""", unsafe_allow_html=True)

# ─── PATHS ────────────────────────────────────────────────────────────────────
BASE_DIR     = os.path.dirname(__file__)
LOGO_PATH    = os.path.join(BASE_DIR, "funza_logo_transparent.png")
INSIGHTS_DIR = os.path.join(BASE_DIR, "weekly_insights")
LONGS_DIR    = os.path.join(BASE_DIR, "..", "YouTubeAnalytics", "Longs")

# ─── CONSTANTS ────────────────────────────────────────────────────────────────

BASELINE = {
    "shorts_completion_rate": 48.81,
    "shorts_engaged_views":   331.0,
    "shorts_ctr":             1.49,
    "longs_ctr":              1.81,
    "longs_pct_viewed":       19.75,
    "longs_avg_views":        116.0,
    "net_new_subs_week":      5,
    "cumulative_new_ai_subs": 85,
    "shorts_this_week":       0,
    "longs_this_week":        0,
}

OKR = {
    "shorts_completion_rate": {"target": 62.0, "unit": "%",   "label": "Shorts stayed to watch"},
    "shorts_avg_pct_viewed":  {"target": 68.0, "unit": "%",   "label": "Shorts avg % viewed"},
    "shorts_engaged_views":   {"target": 600,  "unit": "",    "label": "Shorts avg engaged views"},
    "shorts_ctr":             {"target": 4.0,  "unit": "%",   "label": "Shorts avg CTR (non-feed)"},
    "longs_ctr":              {"target": 4.0,  "unit": "%",   "label": "Longs avg CTR"},
    "longs_pct_viewed":       {"target": 35.0, "unit": "%",   "label": "Longs avg % viewed"},
    "longs_avg_views":        {"target": 400,  "unit": "",    "label": "Longs avg views"},
    "net_new_subs_week":      {"target": 22,   "unit": "/wk", "label": "Net new subs per week"},
    "cumulative_new_ai_subs": {"target": 400,  "unit": "",    "label": "Cumulative new AI subs (since May 2026)"},
    "shorts_per_week":        {"target": 3,    "unit": "/wk", "label": "Shorts per week"},
    "longs_per_week":         {"target": 2,    "unit": "/wk", "label": "Longs per week"},
}

THRESHOLDS = {
    "longs_ctr":              {"green": 4.0,  "amber": 2.0,  "unit": "%"},
    "longs_pct_viewed":       {"green": 40.0, "amber": 30.0, "unit": "%"},
    "shorts_completion_rate": {"green": 58.0, "amber": 45.0, "unit": "%"},
    "shorts_avg_pct_viewed":  {"green": 62.0, "amber": 50.0, "unit": "%"},
    "shorts_ctr":             {"green": 4.0,  "amber": 2.0,  "unit": "%"},
    "net_new_subs_week":      {"green": 10,   "amber": 0,    "unit": ""},
}

OKR_END_DATE     = date(2026, 12, 31)
REVENUE_END_DATE = date(2027, 12, 31)
N_RECENT_SHORTS  = 12
N_RECENT_LONGS   = 10

# Composite score weights — single source of truth for Intelligence tab ranking.
# Maps JSON video field → (weight, OKR key). Targets come from OKR dict above.
SCORE_WEIGHTS = {
    "stayed_to_watch": (0.40, "shorts_completion_rate"),
    "avg_pct_viewed":  (0.25, "shorts_avg_pct_viewed"),
    "engaged_views":   (0.25, "shorts_engaged_views"),
    "ctr":             (0.10, "shorts_ctr"),
}

def compute_composite(row: dict) -> float:
    """Recompute composite score from current OKR targets — never trust the pre-computed JSON value."""
    total = 0.0
    for field, (weight, okr_key) in SCORE_WEIGHTS.items():
        val    = float(row.get(field) or 0)
        target = OKR[okr_key]["target"]
        ratio  = min(val / target, 1.5) if target else 0.0
        total += weight * ratio
    return round(total, 3)

# ─── DATE HELPERS ─────────────────────────────────────────────────────────────

def weeks_left(target=None):
    target = target or OKR_END_DATE
    return max(0, (target - date.today()).days // 7)

def current_week_monday():
    today = date.today()
    return today - timedelta(days=today.weekday())

def current_week_label():
    mon = current_week_monday()
    sun = mon + timedelta(days=6)
    return f"Mon {mon.strftime('%d %b')} – Sun {sun.strftime('%d %b %Y')}"

# ─── DATA HELPERS ─────────────────────────────────────────────────────────────

def parse_publish_date(val):
    if pd.isna(val):
        return None
    for fmt in ("%b %d, %Y", "%B %d, %Y"):
        try:
            return datetime.strptime(str(val).strip(), fmt).date()
        except ValueError:
            continue
    return None

def light(value, key):
    if key not in THRESHOLDS:
        return "⚪"
    t = THRESHOLDS[key]
    if value >= t["green"]:
        return "🟢"
    if value >= t["amber"]:
        return "🟡"
    return "🔴"

def threshold_note(value, key):
    if key not in THRESHOLDS:
        return ""
    t = THRESHOLDS[key]
    unit = t["unit"]
    if value < t["amber"]:
        return f'<div class="threshold-red">🔴 Red threshold: below {t["amber"]}{unit}. Act before next video.</div>'
    if value < t["green"]:
        return f'<div class="threshold-note">🟡 Amber: {t["amber"]}{unit}–{t["green"]}{unit}. Monitor.</div>'
    return f'<div class="threshold-note">🟢 Green: above {t["green"]}{unit}. Replicate.</div>'

def pct_of_target(current, target):
    return min(1.0, current / target) if target else 0.0

def metric_card(col, label, primary, alltime, target, unit, threshold_key, description="", n_label=""):
    thres   = THRESHOLDS.get(threshold_key, {})
    green_t = thres.get("green")
    amber_t = thres.get("amber")
    t_unit  = thres.get("unit", unit)
    traffic = light(primary, threshold_key)
    delta   = primary - alltime
    fmt     = ".2f" if unit == "%" and abs(primary) < 10 else (".1f" if unit == "%" else ".0f")

    if green_t is not None:
        thresh_str = f"🟢 &gt;{green_t}{t_unit} &nbsp; 🟡 &gt;{amber_t}{t_unit}"
    else:
        thresh_str = "—"

    with col:
        st.metric(
            f"{traffic} {label}",
            f"{primary:{fmt}}{unit}",
            f"{delta:+{fmt}}{unit} vs all-time ({alltime:{fmt}}{unit})",
        )
        st.progress(pct_of_target(primary, target))
        st.markdown(f"""
<div style="font-size:0.78rem; line-height:2.1; margin-top:0.2rem; padding:0.5rem 0.6rem;
     background:#1e1e2e; border-radius:6px; border-left:3px solid #de0f3f;">
  <span style="color:#aaa;">🎯 Target</span>&nbsp;
  <strong style="color:#fff;">{target}{unit}</strong>
  &nbsp;&nbsp;&nbsp;
  <span style="color:#aaa;">🚦 Threshold</span>&nbsp;
  <strong style="color:#fff;">{thresh_str}</strong>
  <br>
  <span style="color:#aaa;">📊 Primary (last {n_label})</span>&nbsp;
  <strong style="color:#fff;">{primary:{fmt}}{unit}</strong>
  &nbsp;&nbsp;&nbsp;
  <span style="color:#aaa;">📈 All-time avg</span>&nbsp;
  <strong style="color:#fff;">{alltime:{fmt}}{unit}</strong>
</div>
        """, unsafe_allow_html=True)
        if description:
            st.caption(description)

def process_excel(uploaded_file, content_type):
    REQUIRED_COLS = {
        "shorts": "Stayed to watch (%)",
        "longs":  "Average percentage viewed (%)",
    }
    try:
        df = pd.read_excel(uploaded_file, sheet_name="Table data", engine="openpyxl")
        df = df[df["Content"] != "Total"].copy()

        if REQUIRED_COLS[content_type] not in df.columns:
            st.error(
                f"❌ Unrecognised file format for **{content_type.title()}**. "
                f"Expected column '{REQUIRED_COLS[content_type]}' not found. "
                f"Export from YouTube Studio → Analytics → Content → {content_type.title()}."
            )
            return None, None

        df["publish_date"] = df["Video publish time"].apply(parse_publish_date)
        df = df.dropna(subset=["publish_date"])
        df = df.sort_values("publish_date", ascending=False).reset_index(drop=True)

        n_recent = N_RECENT_SHORTS if content_type == "shorts" else N_RECENT_LONGS
        recent   = df.head(n_recent)

        mon = current_week_monday()
        sun = mon + timedelta(days=6)
        this_week = df[(df["publish_date"] >= mon) & (df["publish_date"] <= sun)]

        recent_range = ""
        if len(recent) > 0:
            oldest = recent["publish_date"].min().strftime("%d %b")
            newest = recent["publish_date"].max().strftime("%d %b %Y")
            recent_range = f"{oldest} – {newest}"

        net_subs         = int(df["Subscribers gained"].sum() - df["Subscribers lost"].sum())
        first_date       = df["publish_date"].min()
        weeks_since_launch = max(1.0, (date.today() - first_date).days / 7.0)
        avg_subs_per_week  = round(net_subs / weeks_since_launch, 1)

        m = {
            "count_this_week":    len(this_week),
            "total_videos":       len(df),
            "recent_count":       len(recent),
            "recent_range":       recent_range,
            "total_subs_gained":  int(df["Subscribers gained"].sum()),
            "total_subs_lost":    int(df["Subscribers lost"].sum()),
            "net_subs":           net_subs,
            "first_video_date":   first_date.strftime("%d %b %Y"),
            "weeks_since_launch": round(weeks_since_launch, 1),
            "avg_subs_per_week":  avg_subs_per_week,
        }

        if content_type == "shorts":
            m["avg_completion_rate"]     = round(recent["Stayed to watch (%)"].mean(), 2)                   if len(recent) else 0.0
            m["avg_pct_viewed"]          = round(recent["Average percentage viewed (%)"].mean(), 2)          if len(recent) else 0.0
            m["avg_ctr"]                 = round(recent["Impressions click-through rate (%)"].mean(), 2)     if len(recent) else 0.0
            m["avg_engaged_views"]       = round(recent["Engaged views"].mean(), 1)                          if len(recent) else 0.0
            m["alltime_completion_rate"] = round(df["Stayed to watch (%)"].mean(), 2)                        if len(df)     else 0.0
            m["alltime_avg_pct_viewed"]  = round(df["Average percentage viewed (%)"].mean(), 2)              if len(df)     else 0.0
            m["alltime_ctr"]             = round(df["Impressions click-through rate (%)"].mean(), 2)         if len(df)     else 0.0
            m["alltime_engaged_views"]   = round(df["Engaged views"].mean(), 1)                              if len(df)     else 0.0
        else:
            m["avg_ctr"]           = round(recent["Impressions click-through rate (%)"].mean(), 2) if len(recent) else 0.0
            m["avg_pct_viewed"]    = round(recent["Average percentage viewed (%)"].mean(), 2)      if len(recent) else 0.0
            m["avg_views"]         = round(recent["Views"].mean(), 1)                              if len(recent) else 0.0
            m["alltime_ctr"]       = round(df["Impressions click-through rate (%)"].mean(), 2)    if len(df)     else 0.0
            m["alltime_pct_viewed"]= round(df["Average percentage viewed (%)"].mean(), 2)         if len(df)     else 0.0
            m["alltime_avg_views"] = round(df["Views"].mean(), 1)                                 if len(df)     else 0.0

        st.session_state[f"{content_type}_metrics"] = m

        if "upload_log" not in st.session_state:
            st.session_state["upload_log"] = []
        log_entry = {
            "File":           getattr(uploaded_file, "name", "unknown"),
            "Type":           content_type.title(),
            "Uploaded":       datetime.now().strftime("%d %b %Y %H:%M"),
            "Videos in file": m["total_videos"],
            "Status":         "✅ Processed",
        }
        st.session_state["upload_log"] = [
            e for e in st.session_state["upload_log"] if e["Type"] != content_type.title()
        ] + [log_entry]

        return m, df
    except Exception as e:
        st.error(f"Could not process file: {e}")
        return None, None

# ─── DATABASE CONNECTION ──────────────────────────────────────────────────────

@st.cache_resource
def _get_conn():
    return psycopg2.connect(st.secrets["database"]["url"])

def _conn():
    """Return the cached connection, reconnecting automatically if stale."""
    conn = _get_conn()
    try:
        conn.cursor().execute("SELECT 1")
    except Exception:
        st.cache_resource.clear()
        conn = _get_conn()
    return conn

def _fetchdf(cur) -> pd.DataFrame:
    rows = cur.fetchall()
    cols = [desc[0] for desc in cur.description]
    return pd.DataFrame(rows, columns=cols)

# ─── METRICS PERSISTENCE ──────────────────────────────────────────────────────

def load_history():
    try:
        con = _conn()
        cur = con.cursor()
        cur.execute("SELECT * FROM weekly_metrics ORDER BY week")
        df = _fetchdf(cur)
        return df
    except Exception:
        return pd.DataFrame()

def save_week(row: dict):
    try:
        con  = _conn()
        cur  = con.cursor()
        cols = list(row.keys())
        col_names    = ", ".join(cols)
        placeholders = ", ".join(["%s"] * len(cols))
        updates      = ", ".join([f"{c} = EXCLUDED.{c}" for c in cols if c != "week"])
        values       = [row[k] for k in cols]
        cur.execute(
            f"INSERT INTO weekly_metrics ({col_names}) VALUES ({placeholders}) "
            f"ON CONFLICT (week) DO UPDATE SET {updates}",
            values,
        )
        con.commit()
        return True
    except Exception as e:
        st.error(f"Database error: {e}")
        return False

# ─── LONGS ANALYTICS PERSISTENCE ─────────────────────────────────────────────

def load_longs_analytics() -> pd.DataFrame:
    try:
        con = _conn()
        try:
            con.rollback()  # clear any aborted-transaction state before reading
        except Exception:
            pass
        cur = con.cursor()
        cur.execute(
            "SELECT content_id, video_title, publish_time, views, ctr_pct, avg_pct_viewed, "
            "subscribers_gained, uploaded_at FROM longs_analytics ORDER BY publish_time DESC"
        )
        return _fetchdf(cur)
    except Exception as e:
        st.warning(f"Could not load longs data from database: {e}")
        return pd.DataFrame()


def save_longs_analytics(df: pd.DataFrame):
    con = _conn()
    cur = con.cursor()
    for _, row in df.iterrows():
        cur.execute(
            """
            INSERT INTO longs_analytics
                (content_id, video_title, publish_time, views, ctr_pct, avg_pct_viewed,
                 subscribers_gained, uploaded_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
            ON CONFLICT (content_id) DO UPDATE SET
                video_title        = EXCLUDED.video_title,
                publish_time       = EXCLUDED.publish_time,
                views              = EXCLUDED.views,
                ctr_pct            = EXCLUDED.ctr_pct,
                avg_pct_viewed     = EXCLUDED.avg_pct_viewed,
                subscribers_gained = EXCLUDED.subscribers_gained,
                uploaded_at        = NOW()
            """,
            (
                str(row.get("Content", "")),
                str(row.get("Video title", "")),
                str(row.get("Video publish time", "")),
                int(row.get("Views", 0) or 0),
                float(row.get("Impressions click-through rate (%)", 0) or 0),
                float(row.get("Average percentage viewed (%)", 0) or 0),
                int(row.get("Subscribers gained", 0) or 0),
            ),
        )
    con.commit()

# ─── KR PROGRESS HELPERS ─────────────────────────────────────────────────────

def load_kr_progress() -> dict:
    try:
        con = _conn()
        cur = con.cursor()
        cur.execute("SELECT kr_id, value FROM kr_progress")
        rows = cur.fetchall()
        return {r[0]: r[1] for r in rows}
    except Exception:
        return {}

def save_kr(kr_id: str, value: float) -> bool:
    try:
        con = _conn()
        cur = con.cursor()
        cur.execute(
            "INSERT INTO kr_progress (kr_id, value, updated_at) VALUES (%s, %s, NOW()) "
            "ON CONFLICT (kr_id) DO UPDATE SET value = EXCLUDED.value, updated_at = NOW()",
            (kr_id, value),
        )
        con.commit()
        return True
    except Exception as e:
        st.error(f"Database error: {e}")
        return False

def load_okr_comments(okr_key: str) -> pd.DataFrame:
    try:
        con = _conn()
        cur = con.cursor()
        cur.execute(
            "SELECT id, date, person, status, title, comment FROM okr_comments "
            "WHERE okr_key = %s ORDER BY date DESC, id DESC",
            (okr_key,),
        )
        df = _fetchdf(cur)
        return df
    except Exception:
        return pd.DataFrame(columns=["id", "date", "person", "status", "title", "comment"])

def save_okr_comment(okr_key: str, date_str: str, person: str, title: str, comment: str, status: str) -> bool:
    try:
        con = _conn()
        cur = con.cursor()
        cur.execute(
            "INSERT INTO okr_comments (okr_key, date, person, title, comment, status) "
            "VALUES (%s, %s, %s, %s, %s, %s)",
            (okr_key, date_str, person, title, comment, status),
        )
        con.commit()
        return True
    except Exception as e:
        st.error(f"Database error: {e}")
        return False

def delete_okr_comment(comment_id: int) -> bool:
    try:
        con = _conn()
        cur = con.cursor()
        cur.execute("DELETE FROM okr_comments WHERE id = %s", (comment_id,))
        con.commit()
        return True
    except Exception as e:
        st.error(f"Database error: {e}")
        return False

def update_okr_comment(comment_id: int, new_title: str, new_text: str) -> bool:
    try:
        con = _conn()
        cur = con.cursor()
        cur.execute(
            "UPDATE okr_comments SET title = %s, comment = %s, updated_at = NOW() WHERE id = %s",
            (new_title, new_text, comment_id),
        )
        con.commit()
        return True
    except Exception as e:
        st.error(f"Database error: {e}")
        return False

def load_long_video_status(content_id: str) -> bool:
    try:
        con = _conn()
        cur = con.cursor()
        cur.execute("SELECT actioned FROM long_video_status WHERE content_id = %s", (content_id,))
        row = cur.fetchone()
        return bool(row[0]) if row else False
    except Exception:
        return False

def save_long_video_status(content_id: str, actioned: bool) -> None:
    try:
        con = _conn()
        cur = con.cursor()
        cur.execute(
            "INSERT INTO long_video_status (content_id, actioned, updated_at) VALUES (%s, %s, NOW()) "
            "ON CONFLICT (content_id) DO UPDATE SET actioned = EXCLUDED.actioned, updated_at = NOW()",
            (content_id, actioned),
        )
        con.commit()
    except Exception as e:
        st.error(f"Database error: {e}")


def hi(text: str) -> str:
    text = text.replace("Sanjay",  '<span class="name-hi">Sanjay</span>')
    text = text.replace("Shailee", '<span class="name-hi">Shailee</span>')
    return text


# ─── NON-YOUTUBE OKR DEFINITIONS ────────────────────────────────────────────

NON_YT_OKRS = [
    {
        "key": "public_speaking",
        "title": "🎤 Public Speaking & Keynotes",
        "objective": "Establish a public speaking presence at organisations and institutions by December 31, 2026.",
        "description": (
            "Public speaking is the channel's entry point into credibility-building outside YouTube — and the most direct way "
            "to demonstrate expertise in front of professional audiences before asking to be paid. In 2026 the goal is track "
            "record, not fee: sessions are free or nominally paid, and the venues are intentionally broad — corporates, schools, "
            "community institutions, monasteries and religious organisations, professional networks, and industry events. "
            "Sanjay and Shailee will each pursue invitations independently. Topics span AI, technology, education, professional development, "
            "AI productivity for individuals and teams, and AI governance. Sessions are typically 30–90 minutes — a keynote "
            "talk, panel appearance, lunch-and-learn, or interactive workshop. The speaking record built in 2026 directly "
            "feeds paid keynotes in 2027 (€2K–5K per event) and opens the door to consulting engagements where credibility "
            "is the primary prerequisite."
        ),
        "krs": [
            {"id": "ps_sanjay_sessions",  "label": "Sessions delivered — Sanjay",        "type": "counter", "target": 3},
            {"id": "ps_shailee_sessions", "label": "Sessions delivered — Shailee",       "type": "counter", "target": 1},
            {"id": "ps_linkedin_posts",   "label": "LinkedIn posts about sessions",       "type": "counter", "target": 4},
            {"id": "ps_references",       "label": "References / testimonials obtained", "type": "counter", "target": 3},
        ],
    },
    {
        "key": "sponsorships",
        "title": "🤝 Sponsorships",
        "objective": "Secure first sponsorship deal (paid or contra) and publish first sponsored content by December 31, 2026.",
        "description": (
            "A sponsorship means a company pays to be featured inside FunzAI content. Two models are in play: "
            "(1) Integrated segment — 60–90 seconds inside a video FunzAI was already making, where the sponsor is relevant "
            "to the topic. (2) Dedicated video — an entire video on a topic the company wants covered, with FunzAI controlling "
            "the script and angle. In both cases FunzAI owns the content and it stays on the channel; the company receives "
            "a licence to share it on their own platforms. Before a cash deal is viable, contra deals are a legitimate "
            "bridge: the company provides expert access, audience promotion, tool access, event invitations, or co-marketing "
            "in exchange for a feature — no money changes hands, but real value is exchanged. FunzAI's pitch angle is always "
            "audience quality — professional, non-technical AI decision-makers are commercially rare and valuable — not raw "
            "subscriber numbers. Full disclosure to viewers is mandatory on every deal regardless of model."
        ),
        "krs": [
            {"id": "sp_pitch_deck",        "label": "Pitch deck ready",                       "type": "binary",  "target": 1},
            {"id": "sp_companies_pitched", "label": "Companies pitched",                      "type": "counter", "target": 8},
            {"id": "sp_first_deal",        "label": "First deal secured (paid or contra)",    "type": "binary",  "target": 1},
            {"id": "sp_first_content",     "label": "First sponsored content published",      "type": "binary",  "target": 1},
        ],
    },
    {
        "key": "freelance_training",
        "title": "🏫 Freelance Training",
        "objective": "Secure and deliver paid corporate AI literacy training engagements by December 31, 2026.",
        "description": (
            "Freelance training means Sanjay or Shailee is hired by a client to deliver an AI literacy training session "
            "on the client's brief and for the client's audience. The client defines the topic, audience size, format, and "
            "duration — FunzAI is the trainer-for-hire. Format is intentionally open: half-day workshop, lunch-and-learn, "
            "full-day session, or a live online cohort. This is distinct from Courses (own brand), where FunzAI controls "
            "the curriculum — here the client brings the brief. Both Sanjay and Shailee have prior training experience "
            "and can deliver independently. Revenue is immediate — there is no subscriber threshold or channel performance "
            "requirement. Outreach begins with warm networks and LinkedIn before expanding to cold outreach. A post-session "
            "testimonial from the first client is a strategic asset: it becomes the first proof point for the outreach pitch "
            "to subsequent clients."
        ),
        "krs": [
            {"id": "ft_offering_defined",  "label": "Training offering defined (topic, format, rate)", "type": "binary",  "target": 1},
            {"id": "ft_outreach_list",     "label": "Outreach list of target companies built",          "type": "counter", "target": 10},
            {"id": "ft_sanjay_sessions",   "label": "Sessions delivered — Sanjay",                     "type": "counter", "target": 2},
            {"id": "ft_shailee_sessions",  "label": "Sessions delivered — Shailee",                    "type": "counter", "target": 1},
            {"id": "ft_testimonial",       "label": "Post-session testimonial obtained",               "type": "counter", "target": 1},
        ],
    },
    {
        "key": "consulting_advisory",
        "title": "💼 Consulting & Advisory",
        "objective": "Secure and deliver first paid consulting & advisory engagements by December 31, 2026.",
        "description": (
            "Consulting and advisory is the highest-value Category II stream — and the one the channel's credibility most "
            "directly unlocks. A company or organisation hires Sanjay or Shailee for ongoing strategic advice: how to adopt "
            "AI responsibly, how to govern it, how to manage an AI-using team without being technical. Sanjay's focus areas "
            "are AI governance (including EU AI Act implications) and AI adoption strategy. Shailee's focus is AI literacy "
            "strategy — helping organisations understand where their people are and building a structured path forward. "
            "The engagement model is open: retainer, project-based, or a fixed multi-session advisory package. Unlike "
            "freelance training (where the client hands you a curriculum), consulting means Sanjay or Shailee shapes the "
            "direction. The channel is the portfolio — every published long-form video on governance or strategy is a proof "
            "point. Inbound inquiries should be accepted immediately without waiting for a target number of videos; "
            "outbound pitching follows once sufficient long-form depth is published. Engagements typically run €5K–15K."
        ),
        "krs": [
            {"id": "ca_offering_defined",   "label": "Consulting offering defined (scope, areas, rate)", "type": "binary",  "target": 1},
            {"id": "ca_outreach_list",      "label": "Outreach list of target organisations built",      "type": "counter", "target": 10},
            {"id": "ca_sanjay_engagement",  "label": "Engagement delivered — Sanjay",                   "type": "counter", "target": 1},
            {"id": "ca_shailee_engagement", "label": "Engagement delivered — Shailee",                  "type": "counter", "target": 1},
            {"id": "ca_testimonial",        "label": "Client reference / testimonial obtained",          "type": "counter", "target": 1},
        ],
    },
    {
        "key": "courses_training",
        "title": "🎓 Courses & Training (Own Brand)",
        "objective": "Have the FunzAI course curriculum designed and its video content produced by December 31, 2026.",
        "description": (
            "Courses and training (own brand) is FunzAI's scalable education product — a curriculum FunzAI designs, "
            "owns, and can deliver in multiple formats: live in-person, live online (cohort-based), or self-paced video. "
            "The Marisa Map (V8) provides the skeleton, built on four lanes — Learn, Use, Lead, Guard — with Lead and Guard "
            "forming the core of the course, Use providing practical tool content, and Learn videos feeding in as foundation. "
            "The key structural decision made is that long-form YouTube videos serve double duty: they are free public content "
            "on the channel and simultaneously the building blocks of the paid course. Build once on YouTube, package and "
            "sell as a course — no separate production required. The 2026 goal is to complete the curriculum outline and "
            "produce the associated videos through the regular long-form publishing schedule. First commercial delivery "
            "(live cohort or first online enrolment) is a 2027 goal. This stream eventually supports corporate training "
            "contracts, an online course product, and provides the methodology framework for consulting engagements."
        ),
        "krs": [
            {"id": "ct_curriculum_defined", "label": "Curriculum outline complete (modules, objectives, video-to-module map)", "type": "binary", "target": 1},
            {"id": "ct_videos_pct",         "label": "Course videos produced (% of curriculum modules covered)",              "type": "pct",    "target": 100},
        ],
    },
]


# ─── PIPELINE CONSTANTS ──────────────────────────────────────────────────────

PIPELINE_STATUSES = ["Idea", "Published"]
STATUS_EMOJI = {"Idea": "💡", "Published": "✅"}
SHORT_CATS = {
    "A1": "A1 · Governance & Safety",
    "A2": "A2 · Jobs & Economy",
    "A3": "A3 · Indirect Trend",
    "B1": "B1 · Meeting Terms",
    "B2": "B2 · Manager Decision Terms",
    "B3": "B3 · Tool Explainers",
    "C1": "C1 · Peer Stories",
    "C2": "C2 · Resources",
}
LONG_CATS = {
    "Framework": "Framework — Marisa Map branch",
    "Harvest":   "Harvest — Short → Long",
}
PERSONA_OPTS = {"Marisa": "Marisa (M)", "Sevrien": "Sevrien (S)", "Both": "Both (M+S)"}

# ─── PIPELINE HELPERS ─────────────────────────────────────────────────────────

def week_key_to_label(week_key: str) -> str:
    try:
        year, w = week_key.split("-W")
        monday = date.fromisocalendar(int(year), int(w), 1)
        sunday = monday + timedelta(days=6)
        if monday.month == sunday.month:
            span = f"{monday.strftime('%b')} {monday.day}–{sunday.day}"
        else:
            span = f"{monday.strftime('%b')} {monday.day}–{sunday.strftime('%b')} {sunday.day}"
        return f"Week {int(w)} · {span}"
    except Exception:
        return week_key

def get_week_options() -> list:
    today = date.today()
    opts = []
    for delta in range(3):
        d = today + timedelta(weeks=delta)
        iso = d.isocalendar()
        wk = f"{iso[0]}-W{iso[1]:02d}"
        opts.append((wk, week_key_to_label(wk)))
    return opts

def get_next_video_id(video_type: str) -> str:
    prefix = "S" if video_type == "Short" else "V"
    fallback = {"Short": 78, "Long": 9}
    try:
        con = _conn()
        cur = con.cursor()
        cur.execute("SELECT video_id FROM video_pipeline WHERE video_type = %s", (video_type,))
        rows = cur.fetchall()
        nums = [int(''.join(filter(str.isdigit, r[0]))) for r in rows if any(c.isdigit() for c in r[0])]
        return f"{prefix}{max(nums) + 1}" if nums else f"{prefix}{fallback[video_type] + 1}"
    except Exception:
        return f"{prefix}{fallback[video_type] + 1}"

def load_okr_periods() -> pd.DataFrame:
    try:
        con = _conn()
        cur = con.cursor()
        cur.execute("SELECT id, name, label FROM okr_periods ORDER BY from_date")
        df = _fetchdf(cur)
        return df
    except Exception:
        return pd.DataFrame(columns=["id", "name", "label"])

def load_pipeline(week_key: str | None = None) -> pd.DataFrame:
    try:
        con = _conn()
        cur = con.cursor()
        q = ("SELECT vp.id, vp.video_id, vp.week_key, vp.video_type, vp.category, "
             "vp.source, vp.demand_checked, vp.suitable_for, vp.title, vp.details, "
             "op.label AS okr_period, vp.status, vp.recommended_by, vp.video_approved "
             "FROM video_pipeline vp "
             "LEFT JOIN okr_periods op ON vp.okr_period_id = op.id ")
        if week_key:
            cur.execute(q + "WHERE vp.week_key = %s ORDER BY vp.video_type DESC, vp.id", (week_key,))
        else:
            cur.execute(q + "ORDER BY vp.week_key, vp.video_type DESC, vp.id")
        df = _fetchdf(cur)
        return df
    except Exception:
        return pd.DataFrame()

def save_pipeline_entry(video_id, week_key, video_type, category, source,
                         demand_checked, suitable_for, title, details,
                         okr_period_id, recommended_by, video_approved) -> bool:
    try:
        con = _conn()
        cur = con.cursor()
        cur.execute(
            """INSERT INTO video_pipeline
               (video_id, week_key, video_type, category, source, demand_checked,
                suitable_for, title, details, okr_period_id, status, recommended_by, video_approved)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'Idea', %s, %s)""",
            (video_id, week_key, video_type, category, source or None,
             demand_checked, suitable_for, title, details or None,
             okr_period_id, recommended_by, video_approved),
        )
        con.commit()
        return True
    except Exception as e:
        st.error(f"Database error: {e}")
        return False

def update_pipeline_entry(entry_id: int, title: str, status: str,
                           details: str, video_approved: bool,
                           demand_checked: bool = False,
                           week_key: str | None = None) -> bool:
    try:
        con = _conn()
        cur = con.cursor()
        if week_key:
            cur.execute(
                """UPDATE video_pipeline
                   SET title=%s, status=%s, details=%s, video_approved=%s, demand_checked=%s,
                       week_key=%s, updated_at=NOW()
                   WHERE id=%s""",
                (title, status, details or None, video_approved, demand_checked, week_key, entry_id),
            )
        else:
            cur.execute(
                """UPDATE video_pipeline
                   SET title=%s, status=%s, details=%s, video_approved=%s, demand_checked=%s, updated_at=NOW()
                   WHERE id=%s""",
                (title, status, details or None, video_approved, demand_checked, entry_id),
            )
        con.commit()
        return True
    except Exception as e:
        st.error(f"Database error: {e}")
        return False

def delete_pipeline_entry(entry_id: int) -> bool:
    try:
        con = _conn()
        cur = con.cursor()
        cur.execute("DELETE FROM video_pipeline WHERE id = %s", (entry_id,))
        con.commit()
        return True
    except Exception as e:
        st.error(f"Database error: {e}")
        return False

# ─── ISSUES HELPERS ───────────────────────────────────────────────────────────

def load_issues() -> pd.DataFrame:
    try:
        con = _conn()
        cur = con.cursor()
        cur.execute(
            "SELECT id, title, description, raised_by, priority, status, created_at "
            "FROM dashboard_issues ORDER BY "
            "CASE priority WHEN 'High' THEN 1 WHEN 'Medium' THEN 2 ELSE 3 END, created_at DESC"
        )
        df = _fetchdf(cur)
        return df
    except Exception:
        return pd.DataFrame(columns=["id","title","description","raised_by","priority","status","created_at"])

def save_issue(title: str, description: str, raised_by: str, priority: str) -> bool:
    try:
        con = _conn()
        cur = con.cursor()
        cur.execute(
            "INSERT INTO dashboard_issues (title, description, raised_by, priority) VALUES (%s, %s, %s, %s)",
            (title, description or None, raised_by, priority),
        )
        con.commit()
        return True
    except Exception as e:
        st.error(f"Database error: {e}")
        return False

def resolve_issue(issue_id: int) -> bool:
    try:
        con = _conn()
        cur = con.cursor()
        cur.execute(
            "UPDATE dashboard_issues SET status='Resolved', resolved_at=NOW() WHERE id=%s",
            (issue_id,),
        )
        con.commit()
        return True
    except Exception as e:
        st.error(f"Database error: {e}")
        return False

def delete_issue(issue_id: int) -> bool:
    try:
        con = _conn()
        cur = con.cursor()
        cur.execute("DELETE FROM dashboard_issues WHERE id = %s", (issue_id,))
        con.commit()
        return True
    except Exception as e:
        st.error(f"Database error: {e}")
        return False


def _comments_section(section_key: str, snapshot_title: str = "", status_options: list | None = None) -> None:
    """Reusable comments log with title, per-row edit and delete. Works for any OKR key."""
    st.markdown("**📝 Comments & Updates**")
    comments_df = load_okr_comments(section_key)

    if not comments_df.empty:
        for _, row in comments_df.iterrows():
            comment_id = int(row["id"])
            is_editing = st.session_state.get(f"editing_{section_key}") == comment_id
            title_text = str(row.get("title", "")).strip()
            body_text  = str(row.get("comment", "")).strip()

            col_text, col_edit, col_del = st.columns([9, 1, 1])
            with col_text:
                header = (
                    f"**{title_text}**  \n" if title_text else ""
                )
                meta = (
                    f"<span style='font-size:0.78rem;color:#aaa'>"
                    f"{row['date']} &nbsp;·&nbsp; {row['person']} &nbsp;·&nbsp; {row['status']}"
                    f"</span>"
                )
                body = f"  \n{body_text}" if body_text else ""
                st.markdown(f"{header}{meta}{body}", unsafe_allow_html=True)
            with col_edit:
                if st.button("✏️", key=f"eb_{section_key}_{comment_id}", help="Edit"):
                    st.session_state[f"editing_{section_key}"] = comment_id
                    st.rerun()
            with col_del:
                if st.button("🗑️", key=f"db_{section_key}_{comment_id}", help="Delete"):
                    delete_okr_comment(comment_id)
                    if st.session_state.get(f"editing_{section_key}") == comment_id:
                        st.session_state.pop(f"editing_{section_key}", None)
                    st.rerun()

            if is_editing:
                edit_title = st.text_input(
                    "Title", value=title_text, max_chars=140,
                    key=f"et_{section_key}_{comment_id}",
                )
                edit_body = st.text_area(
                    "Description (optional)", value=body_text,
                    key=f"ea_{section_key}_{comment_id}",
                )
                save_col, cancel_col = st.columns(2)
                with save_col:
                    if st.button("💾 Save edit", key=f"se_{section_key}_{comment_id}", type="primary"):
                        if edit_title.strip():
                            update_okr_comment(comment_id, edit_title.strip(), edit_body.strip())
                            st.session_state.pop(f"editing_{section_key}", None)
                            st.rerun()
                        else:
                            st.warning("Title is required.")
                with cancel_col:
                    if st.button("Cancel", key=f"ce_{section_key}_{comment_id}"):
                        st.session_state.pop(f"editing_{section_key}", None)
                        st.rerun()

            st.divider()
    else:
        st.caption("No comments yet — add the first one below.")

    with st.form(key=f"cf_{section_key}", clear_on_submit=True):
        new_title = st.text_input(
            "Title ✱  (what is this about? — 140 chars)",
            max_chars=140,
            value=snapshot_title,
            placeholder="e.g. V16 hook quality, Outreach email to Accenture, Stat needs verification…",
        )
        c1, c2, c3 = st.columns([2, 2, 2])
        with c1:
            comment_date = st.date_input("Date", value=date.today())
        with c2:
            comment_person = st.selectbox("Person", ["Sanjay", "Shailee"])
        with c3:
            _status_opts = status_options or ["📝 Note", "✅ Action taken", "🔴 Blocker", "🏆 Win"]
            comment_status = st.selectbox("Status" if status_options else "Type", _status_opts)
        comment_text = st.text_area(
            "Description (optional)",
            placeholder="Additional detail, context, or next steps…",
        )
        submitted = st.form_submit_button("➕ Add comment")

    if submitted:
        if new_title.strip():
            save_okr_comment(
                section_key, str(comment_date),
                comment_person, new_title.strip(), comment_text.strip(), comment_status,
            )
            st.rerun()
        else:
            st.warning("Title is required — describe what this comment is about.")


def _okr_progress_section(okr: dict, progress_data: dict) -> None:
    krs      = okr["krs"]
    card_key = okr["key"]

    scores = []
    for kr in krs:
        current = float(progress_data.get(kr["id"], 0))
        if kr["type"] == "binary":
            scores.append(1.0 if current > 0 else 0.0)
        elif kr["type"] == "pct":
            scores.append(min(1.0, current / 100))
        else:
            scores.append(min(1.0, current / kr["target"]) if kr["target"] > 0 else 0.0)
    overall = sum(scores) / len(scores) if scores else 0.0

    with st.expander(f"{okr['title']}  —  {int(overall * 100)}% complete", expanded=False):
        st.caption(f"Objective: {okr['objective']}")
        if okr.get("description"):
            st.markdown(okr["description"])
        st.progress(overall)
        st.divider()

        new_vals = {}
        for kr in krs:
            current = float(progress_data.get(kr["id"], 0))
            col_input, col_status = st.columns([3, 1])
            with col_input:
                if kr["type"] == "binary":
                    checked = st.checkbox(kr["label"], value=current > 0,
                                          key=f"ck_{card_key}_{kr['id']}")
                    new_vals[kr["id"]] = 1.0 if checked else 0.0
                elif kr["type"] == "pct":
                    new_vals[kr["id"]] = float(
                        st.slider(kr["label"], 0, 100, int(current), step=5,
                                  key=f"sl_{card_key}_{kr['id']}")
                    )
                else:
                    new_vals[kr["id"]] = float(
                        st.number_input(kr["label"], min_value=0,
                                        max_value=int(kr["target"] * 3) + 1,
                                        value=int(current), step=1,
                                        key=f"ni_{card_key}_{kr['id']}")
                    )
            with col_status:
                if kr["type"] == "binary":
                    st.markdown("✅ Done" if current > 0 else "⬜ Pending")
                elif kr["type"] == "pct":
                    st.metric("", f"{int(current)}%", f"target 100%")
                    st.progress(min(1.0, current / 100))
                else:
                    pct = min(1.0, current / kr["target"]) if kr["target"] > 0 else 0.0
                    st.metric("", f"{int(current)} / {int(kr['target'])}")
                    st.progress(pct)

        st.divider()
        if st.button("💾 Save progress", key=f"save_btn_{card_key}", type="primary"):
            for kr_id, val in new_vals.items():
                save_kr(kr_id, val)
            st.success("✅ Saved.")
            st.rerun()

        # ── Comments log ──────────────────────────────────────────────────
        st.divider()
        _comments_section(card_key)


# ─── SIDEBAR ─────────────────────────────────────────────────────────────────

def sidebar():
    with st.sidebar:
        if os.path.exists(LOGO_PATH):
            st.image(LOGO_PATH, use_container_width=True)
        else:
            st.markdown("## FunzAI")

        today    = date.today()
        week_num = today.isocalendar()[1]
        wl_okr   = weeks_left(OKR_END_DATE)
        wl_rev   = weeks_left(REVENUE_END_DATE)

        st.markdown(f"""
        <div class="sb-card" style="padding:1.1rem 1.2rem;">
            <div class="sb-label" style="font-size:0.75rem;margin-bottom:0.7rem;">STATUS</div>
            <div style="font-size:1rem;line-height:2.1;color:#f0f0f0;">
                <strong>Today</strong> &nbsp; {today.strftime('%d %b %Y')}<br>
                <strong>Week</strong> &nbsp; Week {week_num} of 2026<br>
                <strong>OKR deadline</strong> &nbsp; Dec 31, 2026 &nbsp;
                    <span style="color:#de0f3f;font-size:1.15rem;font-weight:700;">{wl_okr} wks</span><br>
                <strong>Revenue target</strong> &nbsp; Dec 31, 2027 &nbsp;
                    <span style="color:#de0f3f;font-size:1.15rem;font-weight:700;">{wl_rev} wks</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(
            'For <span class="name-hi">Sanjay</span> and <span class="name-hi">Shailee</span> only.',
            unsafe_allow_html=True,
        )

        st.markdown("---")
        if st.button("🔓 Log out", use_container_width=True):
            st.session_state["authenticated"] = False
            st.rerun()


# ─── TAB 1 — MISSION ─────────────────────────────────────────────────────────

def tab_mission():
    st.markdown('<div class="main-header">🎯 Mission — Where We Want to Be</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">The north star, the revenue model, and the milestones that connect today\'s work to the goal.</div>', unsafe_allow_html=True)

    # ── North Star ────────────────────────────────────────────────────────────
    st.markdown("""
    <div class="north-star">
        <div class="ns-label">North Star — Channel Revenue Target</div>
        <div class="ns-value">€4,500 / month</div>
        <div class="ns-sub">by December 31, 2027 &nbsp;·&nbsp; Category I + Category II combined</div>
    </div>
    """, unsafe_allow_html=True)

    # ── Revenue Categories ────────────────────────────────────────────────────
    st.markdown('<div class="section-head">REVENUE MODEL</div>', unsafe_allow_html=True)
    st.caption("Two categories. Different drivers. Both required to reach the north star. Column 3 tells you when to activate each stream — and informs which OKRs to prioritise.")

    st.markdown("#### 📺 Category I — Channel Revenue")
    st.caption("Scales with reach and subscriber quality. Rewards consistent publishing, strong CTR and retention, and an engaged professional audience.")
    st.markdown("""
<table class="rev-table">
  <tr>
    <th>Sub-category</th>
    <th>Description</th>
    <th>When to pursue</th>
  </tr>
  <tr>
    <td>AdSense</td>
    <td>Passive income from YouTube ads on all content. Requires joining the <strong>YouTube Partner Program (YPP)</strong> — YouTube's monetisation scheme that grants access to AdSense ad revenue, channel memberships, and Super Thanks.</td>
    <td>YPP Standard (AdSense) requires: <strong>(1) 1,000+ subscribers</strong> AND <strong>(2) 4,000 watch hours in the last 12 months</strong> OR <strong>10M Shorts views in the last 90 days</strong>. Meaningful revenue only when weekly views across all content exceed ~50K. Do not pursue this directly — it follows naturally from CTR and retention improvements. Focus on content quality; AdSense follows.</td>
  </tr>
  <tr>
    <td>Sponsorships</td>
    <td>A company pays to be featured inside FunzAI's content. Two models: (1) <strong>Integrated segment</strong> — 60–90 seconds inside a video FunzAI was making anyway. (2) <strong>Dedicated video</strong> — entire video on a topic the company wants covered; FunzAI controls the script and angle. In both cases <strong>FunzAI owns the content</strong> and it stays on the channel. Company gets a licence to share it on their platforms. Disclosure required. No view guarantees — pricing is based on average historical reach and audience quality. Contra deals (value-in-kind: expert access, audience promotion, tool access) are a valid middle ground before cash deals.</td>
    <td>Pitch proactively now. Lead with <strong>audience quality</strong> (professional non-technical AI decision-makers — rare and valuable), not raw subscriber numbers. First deal: paid or contra. <em>Q4 2026 OKR: first deal secured.</em></td>
  </tr>
  <tr>
    <td>Affiliate marketing</td>
    <td>Commission from recommending courses and tools (Andrew Ng, Google, Coursera, etc.).</td>
    <td>Later stage. C2 shorts are building the organic track record now. Once that track record is established, register for programs, disclose, and begin earning. Do not pursue this before the track record exists.</td>
  </tr>
  <tr>
    <td>Memberships</td>
    <td>YouTube channel memberships from loyal core viewers.</td>
    <td>Pursue when cumulative AI subs &gt; 1,000 and a clear membership perk is defined. <em>Earliest: Q2 2027.</em></td>
  </tr>
  <tr>
    <td>Agency work</td>
    <td>A company briefs FunzAI to produce content to their specification. <strong>Key difference from sponsorships:</strong> the company controls the topic and creative direction; the output can live anywhere (their site, their channels, internal use). FunzAI is the production studio. <strong>FunzAI still owns the content</strong> — the company receives a licence, not ownership. Think of it as FunzAI producing an AI literacy video series for a corporate client's internal training programme.</td>
    <td>Only viable once the channel is the portfolio — OKR targets consistently green (Dec 2026 checkpoint) + 15+ long-form videos published. The channel analytics report and video library become the pitch document. <em>Earliest: Q1 2027.</em></td>
  </tr>
  <tr>
    <td>Podcasts</td>
    <td>Audio spinoff with sponsorship and ad revenue.</td>
    <td>Only after main channel OKRs are consistently green and Category II is generating income. Requires separate production capacity. <em>July–December 2027 at earliest.</em></td>
  </tr>
</table>
    """, unsafe_allow_html=True)

    st.markdown("#### 💼 Category II — Individual Revenue *(the bigger prize)*")
    st.caption("A single consulting contract can exceed months of AdSense. The channel is a credibility portfolio — not a views machine. The right 30,000 subscribers matter more than 300,000 wrong ones.")
    st.markdown("""
<table class="rev-table">
  <tr>
    <th>Sub-category</th>
    <th>Description</th>
    <th>When to pursue</th>
  </tr>
  <tr>
    <td>Public speaking &amp; keynotes</td>
    <td>Presentations at conferences, corporate events, and panels across AI, technology, education, and professional development. €2K–5K per event.</td>
    <td>Pitch for free/low-paid events <strong>now</strong> — the channel is already the portfolio. Paid keynotes realistic once 5+ governance/strategy longs are published and LinkedIn signals availability. <em>Q1 2027 for first paid event.</em></td>
  </tr>
  <tr>
    <td>Consulting &amp; advisory</td>
    <td>AI strategy, adoption, and governance advisory for organisations. Includes project-based engagements that come through channel credibility. €5K–15K per engagement.</td>
    <td>Credibility-based, not reach-based. Signal availability on LinkedIn <strong>now</strong>. Actively pitch when 5+ long-form videos demonstrate strategic depth. Accept opportunistic inbound immediately. <em>Q4 2026 OKR: first paid engagement.</em></td>
  </tr>
  <tr>
    <td>Freelance trainer</td>
    <td>Teaching other organisations' AI courses — in-person or online. Already active (e.g. CivAI). Revenue is immediate; no channel threshold required.</td>
    <td>Already underway. <em>Q4 2026 OKR: 2+ paid sessions per month tracked.</em></td>
  </tr>
  <tr>
    <td>Courses &amp; training (own brand)</td>
    <td>FunzAI develops its own curriculum and delivers it — live in-person, live online, or self-paced. One course, flexible delivery. The Marisa Map is the skeleton. Teaching others' courses (e.g. Amsterdam Data Academy) is viable in the interim while building toward this.</td>
    <td>Build curriculum once, deliver in any format. <em>Q4 2026 OKR: course outline complete + first session delivered (live or online). Full self-paced launch Q2 2027.</em></td>
  </tr>
</table>
    """, unsafe_allow_html=True)

    # ── Stream Distinctions ───────────────────────────────────────────────────
    st.markdown('<div class="section-head">STREAM DISTINCTIONS — What Each Revenue Stream Actually Is</div>', unsafe_allow_html=True)
    st.caption("Four Category II streams can sound similar. This table shows exactly how they differ.")
    st.markdown("""
<table class="rev-table">
  <tr>
    <th>Stream</th>
    <th>What it is</th>
    <th>How it differs from the others</th>
  </tr>
  <tr>
    <td>Public speaking</td>
    <td>An invited talk at a company, institution, or conference. Typically 30–90 minutes. Free or low fee in 2026 — the goal is to build the speaking track record.</td>
    <td>One-off. You are a guest — they set the event context. No ongoing relationship implied. The door-opener for consulting.</td>
  </tr>
  <tr>
    <td>Freelance training</td>
    <td>Hired by a client to deliver AI training on their brief. Session-based. The client defines the topic, audience, and format — you are the trainer-for-hire.</td>
    <td>Client controls the brief. You deliver. Longer and more structured than speaking. Different from consulting (they hand you the curriculum, not an open-ended problem).</td>
  </tr>
  <tr>
    <td>Consulting &amp; advisory</td>
    <td>Strategic, ongoing AI advice to an organisation — adoption strategy, governance, literacy planning. You are the expert advisor shaping their direction.</td>
    <td>You set the direction. Longer engagement. Higher value per hour. Different from training (no curriculum delivery) and speaking (ongoing, not a one-time visit).</td>
  </tr>
  <tr>
    <td>Courses (own brand)</td>
    <td>FunzAI's own curriculum — built once, delivered live in-person, live online, or self-paced. One course, multiple delivery formats, sold to many clients.</td>
    <td>FunzAI owns the content. Scalable. Different from freelance training (your curriculum, not the client's) and consulting (a structured learning path, not ad-hoc advice).</td>
  </tr>
</table>
    """, unsafe_allow_html=True)

    # ── Milestones ────────────────────────────────────────────────────────────
    st.markdown('<div class="section-head">MILESTONE TIMELINE</div>', unsafe_allow_html=True)

    today = date.today()

    milestones = [
        {
            "date": date(2026, 5, 1),
            "label": "May 2026 — AI Relaunch",
            "detail": "Channel relaunched as AI literacy for non-technical professionals. Content DNA established.",
            "done": True,
        },
        {
            "date": date(2026, 8, 2),
            "label": "Aug 2, 2026 — OKR Baseline Set",
            "detail": "85 net new AI subs. Shorts avg stayed 48.8%, CTR 1.49%. Longs CTR 1.81%. Performance tracking begins.",
            "done": True,
        },
        {
            "date": date(2026, 12, 31),
            "label": "Dec 31, 2026 — OKR Checkpoint",
            "detail": "Target: 500 cumulative AI subs · 22/wk · Shorts stayed ≥70% · Longs CTR ≥4%. Foundation for monetisation.",
            "done": today > date(2026, 12, 31),
        },
        {
            "date": date(2027, 3, 31),
            "label": "Q1 2027 — First Monetisation Signals",
            "detail": "Category I: first affiliate income and/or sponsorship approach. Category II: first speaking inquiry or consulting engagement.",
            "done": today > date(2027, 3, 31),
        },
        {
            "date": date(2027, 7, 1),
            "label": "Mid-2027 — Paid Course Launch",
            "detail": "Marisa Map framework → first paid cohort course. Category II revenue begins compounding.",
            "done": today > date(2027, 7, 1),
        },
        {
            "date": date(2027, 12, 31),
            "label": "Dec 31, 2027 — North Star",
            "detail": "€4,500/month combined. Category I: €1,000–1,500 (AdSense + one sponsorship). Category II: €3,000–3,500 (consulting + training).",
            "done": False,
        },
    ]

    for m in milestones:
        is_current = m["date"] >= today and (
            milestones.index(m) == 0 or milestones[milestones.index(m) - 1]["date"] < today
        )
        dot_class  = "done" if m["done"] else ("milestone-dot" if is_current else "ahead")
        dot_colour = "#00b894" if m["done"] else ("#de0f3f" if is_current else "#555")
        label_col  = "#fff" if is_current else ("#00b894" if m["done"] else "#888")
        st.markdown(f"""
        <div class="milestone-row">
            <div style="width:12px;height:12px;border-radius:50%;background:{dot_colour};margin-top:5px;flex-shrink:0;"></div>
            <div>
                <strong style="color:{label_col};">{m['label']}</strong><br>
                <span style="color:#aaa;font-size:0.85rem;">{m['detail']}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── Channel Promise ───────────────────────────────────────────────────────
    st.markdown('<div class="section-head">CHANNEL PROMISE</div>', unsafe_allow_html=True)
    st.markdown("""
    > *This channel helps non-technical professionals understand what AI actually is, what it means
    > for their jobs and their families, and how to use it responsibly — so they can lead with
    > confidence instead of following with fear.*

    **Primary audience:** Working professionals in non-technical roles — HR, marketing, legal, finance,
    operations, teaching, consulting. People who use AI daily but did not build it.

    **The channel is a portfolio, not a views machine.** A video that earns one consulting contract
    is worth more than ten videos that each get 10,000 views. Never sacrifice credibility for reach.
    """)


# ─── TAB 2 — PERFORMANCE ─────────────────────────────────────────────────────

def tab_performance(history_df, kr_data):
    st.markdown('<div class="main-header">📊 OKR Tracker — How We Get There</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="sub-header">Upload both Analytics files to refresh all metrics. '
        f'This week: {current_week_label()}</div>',
        unsafe_allow_html=True,
    )

    # ── FILE UPLOAD — must run first so session_state is populated ────────────
    st.markdown('<div class="section-head">DATA UPLOAD</div>', unsafe_allow_html=True)
    st.caption("Export both files from YouTube Studio → Analytics → Content. Always use **All time** export.")

    if "shorts_key" not in st.session_state:
        st.session_state["shorts_key"] = 0
    if "longs_key" not in st.session_state:
        st.session_state["longs_key"] = 0

    def clear_file(content_type):
        st.session_state[f"{content_type}_key"] += 1
        st.session_state.pop(f"{content_type}_metrics", None)
        st.session_state["upload_log"] = [
            e for e in st.session_state.get("upload_log", [])
            if e["Type"] != content_type.title()
        ]

    def loaded_label(content_type):
        log   = st.session_state.get("upload_log", [])
        entry = next((e for e in log if e["Type"] == content_type.title()), None)
        if entry:
            return f"Loaded: **{entry['File']}** (uploaded {entry['Uploaded']}, {entry['Videos in file']} videos)"
        return "Data loaded."

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Shorts Analytics Excel**")
        sf = st.file_uploader(
            "Upload Shorts file", type=["xlsx"],
            key=f"shorts_up_{st.session_state['shorts_key']}",
        )
        if sf:
            process_excel(sf, "shorts")
        if st.session_state.get("shorts_metrics"):
            st.caption(loaded_label("shorts"))
            if st.button("🗑️ Clear Shorts data", key="clear_shorts",
                         help="Removes from session only. Re-upload to refresh."):
                clear_file("shorts"); st.rerun()

    with c2:
        st.markdown("**Longs Analytics Excel**")
        lf = st.file_uploader(
            "Upload Longs file", type=["xlsx"],
            key=f"longs_up_{st.session_state['longs_key']}",
        )
        if lf:
            process_excel(lf, "longs")
        if st.session_state.get("longs_metrics"):
            st.caption(loaded_label("longs"))
            if st.button("🗑️ Clear Longs data", key="clear_longs",
                         help="Removes from session only. Re-upload to refresh."):
                clear_file("longs"); st.rerun()

    upload_log = st.session_state.get("upload_log", [])
    if upload_log:
        log_df = pd.DataFrame(upload_log)[["File", "Type", "Uploaded", "Videos in file", "Status"]]
        st.dataframe(log_df, use_container_width=True, hide_index=True)

    # ── OKR DASHBOARD ────────────────────────────────────────────────────────
    live_s = st.session_state.get("shorts_metrics", {})
    live_l = st.session_state.get("longs_metrics",  {})

    # If no Excel uploaded this session, fall back to last saved SQLite row
    if not live_s and not history_df.empty:
        last = history_df.iloc[-1]
        weeks_ai = max(1.0, (date.today() - date(2026, 5, 1)).days / 7.0)
        live_s = {
            "avg_completion_rate":     float(last.get("shorts_completion_rate", 0) or 0),
            "avg_pct_viewed":          float(last.get("shorts_avg_pct_viewed",  0) or 0),
            "avg_engaged_views":       float(last.get("shorts_engaged_views",   0) or 0),
            "avg_ctr":                 float(last.get("shorts_ctr",             0) or 0),
            "alltime_completion_rate": BASELINE["shorts_completion_rate"],
            "alltime_avg_pct_viewed":  BASELINE.get("shorts_avg_pct_viewed", 0),
            "alltime_engaged_views":   BASELINE["shorts_engaged_views"],
            "alltime_ctr":             BASELINE["shorts_ctr"],
            "recent_count":            N_RECENT_SHORTS,
            "net_subs":               int(last.get("cumulative_new_ai_subs", 0) or 0),
            "weeks_since_launch":     weeks_ai,
            "count_this_week":        int(last.get("shorts_this_week", 0) or 0),
            "_from_db": True, "_saved_week": str(last.get("week", "")),
        }
    if not live_l and not history_df.empty:
        last = history_df.iloc[-1]
        live_l = {
            "avg_pct_viewed":     float(last.get("longs_pct_viewed", 0) or 0),
            "avg_views":          float(last.get("longs_avg_views",  0) or 0),
            "avg_ctr":            float(last.get("longs_ctr",        0) or 0),
            "alltime_pct_viewed": BASELINE["longs_pct_viewed"],
            "alltime_avg_views":  BASELINE["longs_avg_views"],
            "alltime_ctr":        BASELINE["longs_ctr"],
            "recent_count":       N_RECENT_LONGS,
            "net_subs":          0,
            "weeks_since_launch": 0,
            "count_this_week":   int(last.get("longs_this_week", 0) or 0),
            "_from_db": True, "_saved_week": str(last.get("week", "")),
        }

    _from_db = live_s.get("_from_db") or live_l.get("_from_db")
    if _from_db:
        saved_wk = live_s.get("_saved_week") or live_l.get("_saved_week", "")
        st.info(f"📂 Showing last saved data (week of {saved_wk}). Upload new Excel files above to refresh with current data.")

    st.markdown('<div class="section-head">SHORTS OKRs</div>', unsafe_allow_html=True)

    if live_s:
        c1, c2 = st.columns(2)
        metric_card(c1, "Stayed to Watch",
            primary=float(live_s["avg_completion_rate"]),
            alltime=float(live_s["alltime_completion_rate"]),
            target=OKR["shorts_completion_rate"]["target"], unit="%",
            threshold_key="shorts_completion_rate",
            description="People signal — did the hook stop the scroll in 1–3 seconds? ≥65% = good, ≥75% = viral territory.",
            n_label=str(live_s.get("recent_count", N_RECENT_SHORTS)),
        )
        metric_card(c2, "Avg % Viewed",
            primary=float(live_s["avg_pct_viewed"]),
            alltime=float(live_s["alltime_avg_pct_viewed"]),
            target=OKR["shorts_avg_pct_viewed"]["target"], unit="%",
            threshold_key="shorts_avg_pct_viewed",
            description="Video signal — hook + micro-story + payoff + exit. If this lags behind Stayed to Watch, the middle is losing people. ≥62% = good, ≥75% = excellent (30–60s Shorts).",
            n_label=str(live_s.get("recent_count", N_RECENT_SHORTS)),
        )
        c3, c4 = st.columns(2)
        metric_card(c3, "Avg Engaged Views",
            primary=float(live_s["avg_engaged_views"]),
            alltime=float(live_s["alltime_engaged_views"]),
            target=OKR["shorts_engaged_views"]["target"], unit="",
            threshold_key="shorts_engaged_views",
            description="≥600: engaged views drive subscriber conversion — this is the growth signal, not raw views.",
            n_label=str(live_s.get("recent_count", N_RECENT_SHORTS)),
        )
        metric_card(c4, "Avg CTR (non-feed)",
            primary=float(live_s["avg_ctr"]),
            alltime=float(live_s["alltime_ctr"]),
            target=OKR["shorts_ctr"]["target"], unit="%",
            threshold_key="shorts_ctr",
            description="≥4%: YouTube's signal that packaging is working → unlocks wider impression testing. Non-feed only (excludes Shorts swipe feed).",
            n_label=str(live_s.get("recent_count", N_RECENT_SHORTS)),
        )
    else:
        st.info("Upload the **Shorts Excel** above to see Shorts OKRs.")

    st.markdown('<div class="section-head">LONGS OKRs</div>', unsafe_allow_html=True)

    if live_l:
        c1, c2, c3 = st.columns(3)
        metric_card(c1, "Avg % Viewed",
            primary=float(live_l["avg_pct_viewed"]),
            alltime=float(live_l["alltime_pct_viewed"]),
            target=OKR["longs_pct_viewed"]["target"], unit="%",
            threshold_key="longs_pct_viewed",
            description="≥35%: signals content holds past the hook — YouTube's key retention checkpoint before it broadens distribution.",
            n_label=str(live_l.get("recent_count", N_RECENT_LONGS)),
        )
        metric_card(c2, "Avg Views",
            primary=float(live_l["avg_views"]),
            alltime=float(live_l["alltime_avg_views"]),
            target=OKR["longs_avg_views"]["target"], unit="",
            threshold_key="longs_avg_views",
            description="≥400: enough signal for YouTube to push the video beyond your existing audience to cold viewers.",
            n_label=str(live_l.get("recent_count", N_RECENT_LONGS)),
        )
        metric_card(c3, "Avg CTR",
            primary=float(live_l["avg_ctr"]),
            alltime=float(live_l["alltime_ctr"]),
            target=OKR["longs_ctr"]["target"], unit="%",
            threshold_key="longs_ctr",
            description="≥4%: packaging signal — if CTR is low, title or thumbnail is failing regardless of content quality.",
            n_label=str(live_l.get("recent_count", N_RECENT_LONGS)),
        )
    else:
        st.info("Upload the **Longs Excel** above to see Longs OKRs.")

    st.markdown('<div class="section-head">SUBSCRIBER OKRs</div>', unsafe_allow_html=True)

    if live_s or live_l:
        cumulative_ai_subs = (live_s.get("net_subs", 0) + live_l.get("net_subs", 0))
        span_weeks = max(
            live_s.get("weeks_since_launch", 0),
            live_l.get("weeks_since_launch", 0), 1,
        )
        avg_per_week = round(cumulative_ai_subs / span_weeks, 1)

        c1, c2, c3 = st.columns(3)
        with c1:
            tgt = OKR["net_new_subs_week"]["target"]
            st.metric(
                f"{light(avg_per_week, 'net_new_subs_week')} Avg New AI Subs / Week",
                f"{avg_per_week:.1f}", f"Target: {tgt}/wk",
            )
            st.progress(pct_of_target(avg_per_week, tgt))
            st.markdown(threshold_note(avg_per_week, "net_new_subs_week"), unsafe_allow_html=True)
            st.caption(f"Avg since first AI video · over {span_weeks:.0f} weeks.")
        with c2:
            tgt = OKR["cumulative_new_ai_subs"]["target"]
            st.metric("🎯 Cumulative New AI Subs", f"{cumulative_ai_subs}", f"Target: {tgt} by Dec 31")
            st.progress(pct_of_target(cumulative_ai_subs, tgt))
            st.caption("Net gained − lost across all AI shorts + longs.")
        with c3:
            st.empty()
    else:
        st.info("Upload both Excel files above to see subscriber metrics.")

    st.markdown('<div class="section-head">CADENCE</div>', unsafe_allow_html=True)
    st.caption(f"This week: {current_week_label()}")

    if not history_df.empty:
        latest = history_df.iloc[-1].to_dict()
    else:
        latest = BASELINE.copy()

    live_shorts = live_s.get("count_this_week") if live_s else None
    live_longs  = live_l.get("count_this_week") if live_l else None
    shorts_count = int(live_shorts if live_shorts is not None else latest.get("shorts_this_week", 0))
    longs_count  = int(live_longs  if live_longs  is not None else latest.get("longs_this_week",  0))

    c1, c2 = st.columns(2)
    with c1:
        target, minimum = 3, 2
        emoji = "✅" if shorts_count >= target else ("⚠️" if shorts_count >= minimum else "🔴")
        note  = f"Target {target} met" if shorts_count >= target else (f"Below target {target}, above min {minimum}" if shorts_count >= minimum else f"Below minimum {minimum}")
        st.metric(f"{emoji} Shorts This Week", f"{shorts_count}", note)
    with c2:
        target, minimum = 2, 2
        emoji = "✅" if longs_count >= target else ("⚠️" if longs_count >= minimum else "🔴")
        note  = f"Target {target} met" if longs_count >= target else (f"Above min {minimum}" if longs_count >= minimum else "Below minimum — LONGS ARE PROTECTED")
        st.metric(f"{emoji} Longs This Week", f"{longs_count}", note)

    # ── SAVE THIS WEEK ────────────────────────────────────────────────────────
    if (live_s or live_l) and not _from_db:
        curr_ai_subs = (
            (live_s.get("net_subs", 0) if live_s else 0) +
            (live_l.get("net_subs", 0)  if live_l else 0)
        )
        prev_ai_subs = int(history_df.iloc[-1].get("cumulative_new_ai_subs", 0)) if not history_df.empty else BASELINE["cumulative_new_ai_subs"]
        net_change   = curr_ai_subs - prev_ai_subs

        s_weeks    = live_s.get("weeks_since_launch", 0) if live_s else 0
        l_weeks    = live_l.get("weeks_since_launch", 0) if live_l else 0
        span_weeks = max(s_weeks, l_weeks, 1)
        combined_avg = round(curr_ai_subs / span_weeks, 1)

        st.markdown("---")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric(
                f"{light(net_change, 'net_new_subs_week')} Net New AI Subs This Week",
                f"{net_change:+d}", f"Cumulative total: {curr_ai_subs}",
            )
        with c2:
            st.metric("Avg AI Subs / Week (since AI launch)", f"{combined_avg:.1f}",
                      f"over {span_weeks:.0f} weeks · OKR target: 22/wk")
        with c3:
            st.caption(f"Prev cumulative: {prev_ai_subs} → Now: {curr_ai_subs}")

        st.markdown("---")
        week_label = date.today().strftime("%Y-%m-%d")
        if st.button(f"💾  Save this week's data  ({week_label})", type="primary"):
            row = {
                "week":                    week_label,
                "shorts_completion_rate":  live_s.get("avg_completion_rate", "") if live_s else "",
                "shorts_avg_pct_viewed":   live_s.get("avg_pct_viewed", "")      if live_s else "",
                "shorts_engaged_views":    live_s.get("avg_engaged_views", "")   if live_s else "",
                "shorts_ctr":              live_s.get("avg_ctr", "")             if live_s else "",
                "shorts_this_week":        live_s.get("count_this_week", "")     if live_s else "",
                "longs_pct_viewed":        live_l.get("avg_pct_viewed", "")      if live_l else "",
                "longs_avg_views":         live_l.get("avg_views", "")           if live_l else "",
                "longs_ctr":               live_l.get("avg_ctr", "")             if live_l else "",
                "longs_this_week":         live_l.get("count_this_week", "")     if live_l else "",
                "net_new_subs_week":       net_change,
                "cumulative_new_ai_subs":  curr_ai_subs,
            }
            if save_week(row):
                st.success("✅ Saved to local database. Trend charts will update.")
            else:
                st.error("Failed to save. Check database path.")

    # ── TREND CHARTS ─────────────────────────────────────────────────────────
    if not history_df.empty and len(history_df) >= 2:
        st.markdown('<div class="section-head">TRENDS</div>', unsafe_allow_html=True)

        def trend_chart(df, col, title, target_val, target_label, amber_val=None):
            if col not in df.columns:
                return
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df["week"], y=pd.to_numeric(df[col], errors="coerce"),
                mode="lines+markers", name=title,
                line=dict(color="#de0f3f", width=2),
                marker=dict(size=7, color="#de0f3f"),
            ))
            fig.add_hline(y=target_val, line_dash="dash", line_color="#00c851",
                          annotation_text=target_label, annotation_position="top right")
            if amber_val is not None:
                fig.add_hline(y=amber_val, line_dash="dot", line_color="#ffbb33",
                              annotation_text="Amber", annotation_position="bottom right")
            fig.update_layout(
                template="plotly_dark", height=260,
                margin=dict(t=40, b=30, l=40, r=20),
                title=dict(text=title, font=dict(size=13)),
                xaxis_title="Week", showlegend=False,
            )
            st.plotly_chart(fig, use_container_width=True)

        c1, c2 = st.columns(2)
        with c1:
            trend_chart(history_df, "shorts_completion_rate", "Shorts Avg Completion Rate (%)", 62, "Target 62%", 45)
            trend_chart(history_df, "longs_ctr",              "Longs Avg CTR (%)",              4.0, "Target 4.0%", 2.0)
        with c2:
            trend_chart(history_df, "shorts_engaged_views",   "Shorts Avg Engaged Views",       600, "Target 600")
            trend_chart(history_df, "cumulative_new_ai_subs", "Cumulative New AI Subscribers",  400, "Target 400")
    elif not history_df.empty:
        st.info("📊 One week saved. Trends appear after two weeks of data.")
    else:
        st.info("📭 No history yet. Save your first week above to start tracking trends.")

    # ── BENCHMARK TABLE ───────────────────────────────────────────────────────
    st.markdown('<div class="section-head">INDUSTRY BENCHMARK — Comparable channels at 8 months</div>', unsafe_allow_html=True)
    st.caption(
        "Estimated benchmarks based on analysis of comparable professional/educational channels "
        "(AI, business, 10K–50K subscribers) relaunching into a new content niche. "
        "Not from a published study — use as directional context only."
    )
    st.markdown("""
    <table class="bench-table">
        <tr>
            <th>Metric</th><th>Healthy at 8 months</th><th>Notes</th>
        </tr>
        <tr>
            <td>Shorts avg engaged views</td><td>400–800</td>
            <td>Comparable AI/professional Shorts channels at 6–8 months with consistent publishing (3/week)
            and strong hooks (55%+ completion) typically land 400–800 engaged views per short.</td>
        </tr>
        <tr>
            <td>Longs avg views</td><td>200–500</td>
            <td>Corrected from 500–1,500 which incorrectly assumed an active 30K subscriber base.
            FunzAI's 30K are legacy math/science. Growth to 200–500 requires CTR ≥3% and LinkedIn driving 50–100 clicks per long.</td>
        </tr>
        <tr>
            <td>Long CTR</td><td>3–4%</td>
            <td>Educational/professional niche content settles at 3–5% once packaging is dialled in.
            FunzAI is at 1.81% — single biggest lever for long-form view growth.</td>
        </tr>
        <tr>
            <td>Net new AI subs / week</td><td>10–20</td>
            <td>Current rate is ~7/week (85 subs over ~12 weeks). Reaching 10–20/week requires vocab
            shorts converting at their 6x rate and LinkedIn driving qualified clicks.</td>
        </tr>
        <tr>
            <td>Cumulative new AI subs</td><td>300–500</td>
            <td>85 current + (21 remaining weeks × 10–20/week) = 295–505.
            FunzAI's OKR target is 400 — sits in the middle of the healthy range.</td>
        </tr>
    </table>
    """, unsafe_allow_html=True)

    # ── YOUTUBE CHANNEL NOTES ─────────────────────────────────────────────────
    st.markdown('<div class="section-head">CHANNEL NOTES</div>', unsafe_allow_html=True)
    st.caption("Log observations, decisions, and actions related to channel performance. Annotate any week's data here.")
    with st.expander("📋 Channel Notes — click to expand", expanded=False):
        _comments_section("youtube_channel")

    # ── NON-YOUTUBE OKRs ─────────────────────────────────────────────────────
    st.markdown('<div class="section-head">NON-YOUTUBE OKRs — Aug–Dec 2026</div>', unsafe_allow_html=True)
    st.caption("Manual progress tracking for the five non-channel OKRs. Expand each card to update and save.")
    for okr in NON_YT_OKRS:
        _okr_progress_section(okr, kr_data)


# ─── TAB 3 — INTELLIGENCE ─────────────────────────────────────────────────────

CAT_COLOURS = {
    "A1": "#4e8cff", "A2": "#4e8cff", "A3": "#4e8cff",
    "B1": "#00b894", "B2": "#00b894", "B3": "#00b894",
    "C1": "#e17055", "C2": "#e17055",
}
SUB_CAT_LABELS = {
    "A1": "A1 Governance", "A2": "A2 Jobs & Economy", "A3": "A3 Indirect Trend",
    "B1": "B1 Meeting Terms", "B2": "B2 Manager Terms", "B3": "B3 Tool Explainers",
    "C1": "C1 Peer Stories", "C2": "C2 Resources",
}

def _bar_chart(sub_perf: dict, metric_key: str, title: str, target: float, unit: str) -> go.Figure:
    cats   = [k for k in sub_perf if sub_perf[k].get(metric_key) is not None]
    vals   = [sub_perf[c][metric_key] for c in cats]
    cols   = [CAT_COLOURS.get(c, "#aaa") for c in cats]
    labels = [SUB_CAT_LABELS.get(c, c) for c in cats]
    counts = [sub_perf[c].get("count", 0) for c in cats]

    fig = go.Figure(go.Bar(
        x=labels, y=vals, marker_color=cols,
        text=[f"{v:.1f}{unit}<br>n={n}" for v, n in zip(vals, counts)],
        textposition="outside", textfont=dict(size=11),
    ))
    fig.add_hline(y=target, line_dash="dash", line_color="#de0f3f",
                  annotation_text=f"Target {target}{unit}",
                  annotation_position="top right",
                  annotation_font_color="#de0f3f")
    fig.update_layout(
        template="plotly_dark", height=300,
        title=dict(text=title, font=dict(size=13)),
        margin=dict(t=50, b=10, l=40, r=20),
        yaxis_title=unit if unit else "count",
        showlegend=False,
    )
    return fig


def _long_guidance(ctr: float, avg_pct: float) -> dict:
    """
    Rubric-based guidance for a single long-form video.
    Uses actual metric values so every video gets specific, not generic, commentary.
    fix_now   = actions on the published video (no re-upload needed)
    next_video = content lessons to carry forward
    priority   = high / medium / low / healthy
    """
    ctr_critical = ctr < 1.5
    ctr_red      = 1.5 <= ctr < 2.0
    ctr_amber    = 2.0 <= ctr < 4.0
    ctr_green    = ctr >= 4.0

    ret_critical = avg_pct < 20.0   # leaving before 1-min mark on typical long
    ret_red      = 20.0 <= avg_pct < 30.0
    ret_amber    = 30.0 <= avg_pct < 35.0
    ret_green    = avg_pct >= 35.0

    fix_now, next_vid, priority = [], [], "low"

    # ── CTR — packaging fixes (all doable without re-upload) ──────────────
    if ctr_critical:
        fix_now.append(
            f"CTR at {ctr:.2f}% is critically low — below 1.5%. "
            "Replace the thumbnail now, do not wait for an A/B test. "
            "Also re-score the title against the 5-dimension rubric: "
            "front-loading, curiosity gap, and SEO are the most likely gaps."
        )
        priority = "high"
    elif ctr_red:
        fix_now.append(
            f"CTR at {ctr:.2f}% is below the 2% floor. "
            "A/B test a new thumbnail — this is the highest-leverage action. "
            "Check whether the title creates a genuine curiosity gap or just names the topic."
        )
        priority = "high"
    elif ctr_amber:
        fix_now.append(
            f"CTR at {ctr:.2f}% is in amber range (2–4%). "
            "A thumbnail refresh or sharper title wording could push this past 4%. "
            "Test one change at a time — thumbnail first."
        )
        priority = "medium"

    # ── Retention — content lessons (cannot fix without re-upload) ─────────
    if ret_critical:
        if ctr_green or ctr_amber:
            next_vid.append(
                f"Packaging is bringing people in (CTR {ctr:.2f}%) but {avg_pct:.0f}% avg viewed "
                "means most viewers left well before the halfway point. "
                "The hook over-promised — content did not deliver on the opening premise."
            )
        else:
            next_vid.append(
                f"At {avg_pct:.0f}% avg viewed, most viewers left in the first minute or two. "
                "The re-hook is not working — after the opening, there is no compelling reason given to stay."
            )
        next_vid.append(
            "Open YouTube Studio → this video's retention graph → find the sharpest drop. "
            "That is the exact moment to fix in the next long."
        )
        if priority == "low":
            priority = "medium"
    elif ret_red:
        next_vid.append(
            f"At {avg_pct:.0f}% avg viewed, retention is below the 30% floor. "
            "Viewers are leaving in the first half — likely a weak re-hook or a mid-video section that stalls. "
            "Check the retention curve for the specific drop point."
        )
        if priority == "low":
            priority = "medium"
    elif ret_amber:
        next_vid.append(
            f"At {avg_pct:.0f}% avg viewed, retention is borderline (target 35%). "
            "You are close — cut the slowest section in the middle of the next long "
            "and ensure every segment advances the story."
        )

    # Special case: strong content, bad packaging = clearest rescue opportunity
    if ctr_red or ctr_critical:
        if ret_green:
            fix_now  = [
                f"High-priority thumbnail A/B test. Content is working ({avg_pct:.0f}% viewed) — "
                "packaging is the only blocker. This video can recover significantly from a thumbnail change alone."
            ]
            next_vid = []
            priority = "high"

    if ctr_green and ret_green:
        return {
            "fix_now":    f"Nothing — CTR {ctr:.2f}%, avg viewed {avg_pct:.0f}%. Replicate this format.",
            "next_video": "—",
            "priority":   "healthy",
        }

    return {
        "fix_now":    " ".join(fix_now)  if fix_now  else "—",
        "next_video": " ".join(next_vid) if next_vid else "—",
        "priority":   priority,
    }


def _tab_intelligence_shorts():
    """Shorts analysis — JSON report viewer."""
    report_files = sorted(glob.glob(os.path.join(INSIGHTS_DIR, "*.json")), reverse=True)

    if not report_files:
        st.info(
            "No insight reports yet.\n\n"
            "**How to generate one:**\n"
            "1. Download your Shorts Analytics Excel from YouTube Studio\n"
            "2. Share it with Claude in this same project\n"
            "3. Ask: *'Run a Shorts analysis report'*\n"
            "4. Claude saves the JSON here → refresh this tab"
        )
        return

    labels = [os.path.basename(f).replace(".json", "") for f in report_files]
    choice = st.selectbox("Select report", labels)
    chosen_file = report_files[labels.index(choice)]

    with open(chosen_file, encoding="utf-8") as fh:
        r = json.load(fh)

    meta = r.get("meta", {})
    st.caption(
        f"Generated {meta.get('generated_date', '?')}  ·  "
        f"Data range: {meta.get('data_range', '?')}  ·  "
        f"{meta.get('total_videos_analyzed', '?')} videos analysed  ·  "
        f"Recent window: {meta.get('recent_window', '?')}"
    )

    # ── OKR Snapshot ─────────────────────────────────────────────────────────
    st.markdown('<div class="section-head">OKR SNAPSHOT</div>', unsafe_allow_html=True)

    STATUS_ICON   = {"green": "🟢", "amber": "🟡", "red": "🔴"}
    okr           = r.get("okr_snapshot", {})
    recent_window = meta.get("recent_window", "last 12")
    okr_defs = [
        ("stayed_to_watch", "Stayed to Watch",   "%"),
        ("avg_pct_viewed",  "Avg % Viewed",       "%"),
        ("engaged_views",   "Avg Engaged Views",  ""),
        ("ctr",             "Avg CTR (non-feed)", "%"),
    ]
    cols = st.columns(4)
    for col, (key, label, unit) in zip(cols, okr_defs):
        d    = okr.get(key, {})
        icon = STATUS_ICON.get(d.get("status", "red"), "🔴")
        recnt = d.get("recent", 0)
        alltt = d.get("alltime", 0)
        tgt   = d.get("target", 0)
        fmt   = ".1f" if unit == "%" else ".0f"
        with col:
            st.metric(
                f"{icon} {label} ({recent_window.split('(')[0].strip()})",
                f"{recnt:{fmt}}{unit}",
                f"{recnt - alltt:+{fmt}}{unit} vs all-time ({alltt:{fmt}}{unit})",
            )
            st.caption(f"Target: **{tgt}{unit}**")

    # ── Category Performance Charts ───────────────────────────────────────────
    st.markdown('<div class="section-head">CATEGORY PERFORMANCE</div>', unsafe_allow_html=True)
    st.markdown("""
| Colour | Category | Sub-categories |
|---|---|---|
| 🔵 Blue | **A — News** | A1 Governance & Safety · A2 Jobs & Economy · A3 Indirect Trend |
| 🟢 Teal | **B — Vocab** | B1 Meeting-survival terms · B2 Manager-decision terms · B3 Tool explainers |
| 🟠 Orange | **C — Someone Did This** | C1 Peer stories · C2 Resource recommendations |
""")
    st.caption("Each bar shows the average for that sub-category. 'n=' is the number of videos. Red dashed line = OKR target.")

    sub_perf = r.get("sub_category_performance", {})

    # Compute subs per 100 engaged views per sub-category from video-level data
    _all_videos = r.get("videos", [])
    if _all_videos:
        from collections import defaultdict
        _scat_subs = defaultdict(float)
        _scat_eng  = defaultdict(float)
        for v in _all_videos:
            sc = v.get("sub_category") or v.get("category")
            if sc:
                _scat_subs[sc] += float(v.get("subscribers_gained") or 0)
                _scat_eng[sc]  += float(v.get("engaged_views") or 0)
        # Inject into sub_perf so _bar_chart can use it
        for sc in sub_perf:
            eng = _scat_eng.get(sc, 0)
            sub_perf[sc]["subs_per_100_engaged"] = (
                round(_scat_subs[sc] / eng * 100, 2) if eng > 0 else 0
            )

    if sub_perf:
        c1, c2 = st.columns(2)
        with c1:
            st.plotly_chart(_bar_chart(sub_perf, "avg_stayed",             "Stayed to Watch (%)",             OKR["shorts_completion_rate"]["target"], "%"), use_container_width=True)
            st.plotly_chart(_bar_chart(sub_perf, "avg_engaged_views",      "Avg Engaged Views",               OKR["shorts_engaged_views"]["target"],   ""),  use_container_width=True)
            st.plotly_chart(_bar_chart(sub_perf, "subs_per_100_engaged",   "Subscribers per 100 Engaged Views", 0, ""),                                       use_container_width=True)
        with c2:
            st.plotly_chart(_bar_chart(sub_perf, "avg_pct_viewed",         "Avg % Viewed (%)",                OKR["shorts_avg_pct_viewed"]["target"],  "%"), use_container_width=True)
            st.plotly_chart(_bar_chart(sub_perf, "avg_ctr",                "Avg CTR — non-feed (%)",          OKR["shorts_ctr"]["target"],             "%"), use_container_width=True)
        st.caption("**Subscribers per 100 engaged views** = subscriber conversion efficiency. Best predictor of which content type is worth making more of. No target line — higher is always better.")
    else:
        st.info("No sub-category performance data in this report.")

    # ── Video-level Table ────────────────────────────────────────────────────
    st.markdown('<div class="section-head">ALL VIDEOS</div>', unsafe_allow_html=True)
    videos = r.get("videos", [])
    if videos:
        vdf = pd.DataFrame(videos)
        vdf["publish_date"] = pd.to_datetime(vdf["publish_date"])
        vdf = vdf.sort_values("publish_date", ascending=False).reset_index(drop=True)

        fc1, fc2 = st.columns(2)
        all_cats  = sorted(vdf["category"].dropna().unique().tolist())
        all_scats = sorted(vdf["sub_category"].dropna().unique().tolist())

        # Build parent lookup: sub-category → category (derived from data, no hardcoding)
        scat_to_cat = dict(zip(vdf["sub_category"], vdf["category"]))

        # Apply any pending category correction queued by the reverse-sync on the previous run
        if "_ins_cat_pending" in st.session_state:
            st.session_state["ins_cat_filter"] = st.session_state.pop("_ins_cat_pending")

        sel_cat = fc1.multiselect("Filter by category", all_cats, default=all_cats, key="ins_cat_filter")

        # Sub-categories available for the selected categories
        valid_scats = sorted(
            vdf[vdf["category"].isin(sel_cat)]["sub_category"].dropna().unique().tolist()
        )

        # Sync sub-category session state — must happen BEFORE scat widget renders.
        # Only touch sub-cats for categories that CHANGED (newly added or newly removed).
        # Categories that were already selected: leave sub-cat selection untouched so
        # the user can remove individual sub-cats without them snapping back.
        prev_cats = st.session_state.get("_ins_cat_prev", set(all_cats))
        newly_added   = set(sel_cat) - set(prev_cats)
        newly_removed = set(prev_cats) - set(sel_cat)
        st.session_state["_ins_cat_prev"] = set(sel_cat)

        if "ins_scat_filter" in st.session_state:
            current_scats = set(st.session_state["ins_scat_filter"])
            for cat in newly_added:
                current_scats |= set(
                    vdf[vdf["category"] == cat]["sub_category"].dropna().unique()
                )
            for cat in newly_removed:
                current_scats -= set(
                    vdf[vdf["category"] == cat]["sub_category"].dropna().unique()
                )
            current_scats &= set(valid_scats)
            st.session_state["ins_scat_filter"] = sorted(current_scats)

        sel_scat = fc2.multiselect(
            "Filter by sub-category", valid_scats, default=valid_scats, key="ins_scat_filter"
        )

        # Reverse: if all sub-categories of a category are removed manually, remove that category.
        # Cannot write to ins_cat_filter after it's rendered — queue via pending key.
        cats_with_active_scats = sorted({scat_to_cat[s] for s in sel_scat if s in scat_to_cat})
        if set(cats_with_active_scats) != set(sel_cat):
            st.session_state["_ins_cat_pending"] = cats_with_active_scats
            st.rerun()

        fdf = vdf[vdf["category"].isin(sel_cat) & vdf["sub_category"].isin(sel_scat)].copy()
        fdf["publish_date"] = fdf["publish_date"].dt.strftime("%Y-%m-%d")
        col_order = [c for c in
            ["title", "publish_date", "category", "sub_category",
             "engaged_views", "ctr", "stayed_to_watch", "avg_pct_viewed"]
            if c in fdf.columns]
        st.dataframe(
            fdf[col_order].rename(columns={
                "title": "Title", "publish_date": "Published",
                "category": "Cat", "sub_category": "Sub-cat",
                "engaged_views": "Engaged Views", "ctr": "CTR %",
                "stayed_to_watch": "Stayed %", "avg_pct_viewed": "Avg % Viewed",
            }),
            use_container_width=True, hide_index=True,
        )
        st.caption(f"Showing {len(fdf)} of {len(vdf)} videos · sorted by publish date (newest first)")
    else:
        st.info("No video-level data in this report.")

    # ── Top & Bottom Performers ───────────────────────────────────────────────
    st.markdown('<div class="section-head">TOP & BOTTOM PERFORMERS</div>', unsafe_allow_html=True)
    weights_desc = " · ".join(
        f"{f.replace('_',' ').title()} {int(w*100)}% (target {OKR[k]['target']}{OKR[k]['unit']})"
        for f, (w, k) in SCORE_WEIGHTS.items()
    )
    st.caption(f"**Composite score:** {weights_desc}")

    # Recompute from current OKR targets — never trust pre-computed JSON values
    all_videos = r.get("videos", [])
    today = date.today()
    for v in all_videos:
        v["_score"] = compute_composite(v)
        v["_age"]   = (today - pd.to_datetime(v["publish_date"]).date()).days

    top3    = sorted(
        [v for v in all_videos if v["_age"] > 21],
        key=lambda v: v["_score"], reverse=True
    )[:3]
    bottom3 = sorted(
        [v for v in all_videos if v["_age"] > 7],
        key=lambda v: v["_score"]
    )[:3]

    def _perf_card(v, rank, card_class=""):
        cat    = v.get("sub_category", v.get("category", "?"))
        title  = v.get("title", "?")
        sc     = v["_score"]
        stayed = float(v.get("stayed_to_watch", 0))
        pct    = float(v.get("avg_pct_viewed", 0))
        eng    = int(v.get("engaged_views", 0))
        ctr    = float(v.get("ctr", 0))
        return f"""
        <div class="perf-card {card_class}">
            <div class="perf-rank">#{rank}</div>
            <span class="perf-cat">{cat}</span>
            <div class="perf-title">{title}</div>
            <div class="perf-metrics">
                <div class="perf-metric">
                    <span class="pm-val">{stayed:.1f}%</span>
                    <span class="pm-lbl">Stayed</span>
                </div>
                <div class="perf-metric">
                    <span class="pm-val">{pct:.1f}%</span>
                    <span class="pm-lbl">Viewed</span>
                </div>
                <div class="perf-metric">
                    <span class="pm-val">{eng:,}</span>
                    <span class="pm-lbl">Engaged</span>
                </div>
                <div class="perf-metric">
                    <span class="pm-val">{ctr:.2f}%</span>
                    <span class="pm-lbl">CTR</span>
                </div>
            </div>
            <div class="perf-score">Composite score: {sc:.3f}</div>
        </div>"""

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**🏆 Top performers** — published more than 21 days ago")
        st.caption("Data has stabilised — safe to compare")
        html = "".join(_perf_card(v, i) for i, v in enumerate(top3, 1))
        st.markdown(html or "*No videos older than 21 days yet.*", unsafe_allow_html=True)
    with c2:
        st.markdown("**⚠️ Bottom performers** — published more than 7 days ago")
        st.caption("Verdict is clear — diagnose and apply learnings")
        html = "".join(_perf_card(v, i, "bottom") for i, v in enumerate(bottom3, 1))
        st.markdown(html or "*No videos older than 7 days yet.*", unsafe_allow_html=True)

    # ── Outliers ──────────────────────────────────────────────────────────────
    outliers = r.get("outliers", {})
    if outliers:
        st.markdown('<div class="section-head">OUTLIERS — SINGLE-METRIC EXTREMES</div>', unsafe_allow_html=True)
        st.caption("Each is a signal worth acting on regardless of overall rank.")

        OUTLIER_META = {
            "best_ctr":            ("", "Best CTR",          ""),
            "best_stayed":         ("", "Best Hook",         ""),
            "best_pct_viewed":     ("", "Best % Viewed",     ""),
            "best_subs":           ("", "Most Subs Gained",  ""),
            "worst_ctr_recent":    ("warn", "Worst CTR",     "recent"),
            "worst_stayed_recent": ("warn", "Worst Hook",    "recent"),
        }

        def _outlier_card(key, ov, css, label, badge):
            val   = f"{ov.get('value')}{ov.get('unit','')}"
            title = ov.get("title", "?")
            cat   = ov.get("sub_category", "")
            note  = ov.get("note", "")
            badge_html = f' <span style="font-size:0.6rem;color:#aaa;background:#2a2a3e;padding:1px 5px;border-radius:3px">{badge}</span>' if badge else ""
            return f"""
            <div class="outlier-card {css}">
                <div class="outlier-label">{label}{badge_html}</div>
                <div class="outlier-value">{val}</div>
                <div class="outlier-title">{title} <span style="color:#555;font-size:0.7rem">[{cat}]</span></div>
                <div class="outlier-note">{note}</div>
            </div>"""

        best_keys  = ["best_ctr", "best_stayed", "best_pct_viewed", "best_subs"]
        worst_keys = ["worst_ctr_recent", "worst_stayed_recent"]

        cols = st.columns(2)
        for i, key in enumerate(best_keys):
            ov = outliers.get(key)
            if not ov: continue
            css, label, badge = OUTLIER_META[key]
            with cols[i % 2]:
                st.markdown(_outlier_card(key, ov, css, label, badge), unsafe_allow_html=True)

        st.markdown('<div style="margin:0.5rem 0;border-top:1px solid #2a2a3e"></div>', unsafe_allow_html=True)
        cols2 = st.columns(2)
        for i, key in enumerate(worst_keys):
            ov = outliers.get(key)
            if not ov: continue
            css, label, badge = OUTLIER_META[key]
            with cols2[i]:
                st.markdown(_outlier_card(key, ov, css, label, badge), unsafe_allow_html=True)

    # ── Patterns & Recommendations ────────────────────────────────────────────
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="section-head">PATTERNS</div>', unsafe_allow_html=True)
        patterns_html = "".join(
            f'<div class="pattern-item">{p}</div>' for p in r.get("patterns", [])
        )
        st.markdown(patterns_html or "*No patterns identified.*", unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="section-head">RECOMMENDATIONS</div>', unsafe_allow_html=True)
        recs_html = "".join(
            f'<div class="rec-item"><span class="rec-num">Action {i}</span>{rec}</div>'
            for i, rec in enumerate(r.get("recommendations", []), 1)
        )
        st.markdown(recs_html or "*No recommendations.*", unsafe_allow_html=True)


def _tab_intelligence_longs():
    """Long-form per-video analysis with rubric-based guidance."""
    PRIORITY_ICON = {"high": "🔴", "medium": "🟡", "low": "🟢", "healthy": "✅"}

    # ── Load from Supabase ─────────────────────────────────────────────────
    db_raw = load_longs_analytics()

    # ── Upload section — collapsed when data exists, expanded when empty ───
    upload_label = (
        "🔄 Refresh data — upload latest YouTube export"
        if not db_raw.empty
        else "📤 Upload YouTube Long Analytics Excel (All time export)"
    )
    with st.expander(upload_label, expanded=db_raw.empty):
        st.caption("YouTube Studio → Analytics → Content tab → Videos → Export as Excel (All time)")
        uploaded = st.file_uploader("Select Excel file", type=["xlsx"], key="longs_upload")
        if uploaded:
            try:
                raw_excel = pd.read_excel(uploaded, sheet_name="Table data")
                to_save   = raw_excel[
                    (raw_excel["Content"] != "Total") & raw_excel["Video title"].notna()
                ]
                save_longs_analytics(to_save)
                db_raw = load_longs_analytics()  # reload inline — avoids infinite rerun loop
                st.success(f"Saved {len(to_save)} videos. Data updated below.")
            except Exception as e:
                st.error(f"Could not process file: {e}")
                return

    if db_raw.empty:
        st.info("No data yet — upload your YouTube Longs Analytics Excel above to get started.")
        return

    # ── Reconstruct df with original column names so the rest of the function is unchanged ──
    df = db_raw.rename(columns={
        "content_id":         "Content",
        "video_title":        "Video title",
        "publish_time":       "Video publish time",
        "views":              "Views",
        "ctr_pct":            "Impressions click-through rate (%)",
        "avg_pct_viewed":     "Average percentage viewed (%)",
        "subscribers_gained": "Subscribers gained",
    }).copy()
    for fmt in ["%b %d, %Y", "%B %d, %Y", "%Y-%m-%d"]:
        parsed = pd.to_datetime(df["Video publish time"], format=fmt, errors="coerce")
        df["publish_date"] = df.get("publish_date", pd.NaT).fillna(parsed) if "publish_date" in df else parsed
    df = df.sort_values("publish_date", ascending=False).reset_index(drop=True)

    if "uploaded_at" in db_raw.columns and db_raw["uploaded_at"].notna().any():
        last_ts = pd.to_datetime(db_raw["uploaded_at"]).max()
        st.caption(f"Data last refreshed: {last_ts.strftime('%d %b %Y %H:%M')}")

    # ── Summary stats ──────────────────────────────────────────────────────
    st.markdown('<div class="section-head">OVERVIEW</div>', unsafe_allow_html=True)
    n_vids   = len(df)
    avg_ctr  = df["Impressions click-through rate (%)"].mean()
    avg_ret  = df["Average percentage viewed (%)"].mean()
    avg_views = df["Views"].mean()
    total_subs = df["Subscribers gained"].sum()

    mc1, mc2, mc3, mc4 = st.columns(4)
    mc1.metric("Videos", n_vids)
    mc2.metric("Avg CTR", f"{avg_ctr:.2f}%", f"Target 4%")
    mc3.metric("Avg % Viewed", f"{avg_ret:.1f}%", f"Target 35%")
    mc4.metric("Total Subs Gained", int(total_subs))

    # ── Per-video table with guidance ─────────────────────────────────────
    st.markdown('<div class="section-head">ALL LONG-FORM VIDEOS</div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="display:flex;gap:2rem;flex-wrap:wrap;background:#1a1a2e;border-radius:8px;
                padding:0.7rem 1rem;margin-bottom:0.8rem;align-items:flex-start">
        <div>
            <div style="font-size:0.62rem;color:#aaa;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:0.35rem">Priority</div>
            <div style="display:flex;gap:1rem;flex-wrap:wrap">
                <span style="font-size:0.78rem;color:#ccc">🔴 <strong style="color:#fff">High</strong> — act now</span>
                <span style="font-size:0.78rem;color:#ccc">🟡 <strong style="color:#fff">Medium</strong> — monitor</span>
                <span style="font-size:0.78rem;color:#ccc">🟢 <strong style="color:#fff">Low</strong></span>
                <span style="font-size:0.78rem;color:#ccc">✅ <strong style="color:#fff">Healthy</strong></span>
            </div>
        </div>
        <div style="width:1px;background:#2a2a3e;align-self:stretch"></div>
        <div>
            <div style="font-size:0.62rem;color:#aaa;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:0.35rem">Guidance (in Action Items below)</div>
            <div style="display:flex;gap:1rem;flex-wrap:wrap">
                <span style="font-size:0.78rem;color:#ccc"><span style="color:#4e8cff;font-weight:700">🔧 Fix now</span> — change on the published video, no re-upload needed</span>
                <span style="font-size:0.78rem;color:#ccc"><span style="color:#00b894;font-weight:700">📝 Next video</span> — content lesson, apply to the next long</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    rows = []
    for _, row in df.iterrows():
        ctr     = float(row.get("Impressions click-through rate (%)", 0) or 0)
        avg_pct = float(row.get("Average percentage viewed (%)", 0) or 0)
        g       = _long_guidance(ctr, avg_pct)
        rows.append({
            "Priority":      PRIORITY_ICON[g["priority"]],
            "Title":         str(row.get("Video title", "?")),
            "Published":     row["publish_date"].strftime("%d %b %Y") if pd.notna(row["publish_date"]) else "—",
            "Views":         int(row.get("Views", 0) or 0),
            "CTR %":         round(ctr, 2),
            "Avg % Viewed":  round(avg_pct, 1),
            "Subs Gained":   int(row.get("Subscribers gained", 0) or 0),
            "fix_now":       g["fix_now"],
            "next_video":    g["next_video"],
            "_priority_raw": g["priority"],
            "_content_id":   str(row.get("Content", "")),
        })

    table_df = pd.DataFrame(rows)
    st.dataframe(
        table_df[["Priority", "Title", "Published", "Views", "CTR %", "Avg % Viewed", "Subs Gained"]],
        use_container_width=True,
        hide_index=True,
        column_config={
            "Priority":     st.column_config.TextColumn("!", width="small"),
            "Title":        st.column_config.TextColumn("Title", width="large"),
            "Published":    st.column_config.TextColumn("Published", width="small"),
            "Views":        st.column_config.NumberColumn("Views", format="%d"),
            "CTR %":        st.column_config.NumberColumn("CTR %", format="%.2f%%"),
            "Avg % Viewed": st.column_config.NumberColumn("Avg % Viewed", format="%.1f%%"),
            "Subs Gained":  st.column_config.NumberColumn("Subs", format="%d"),
        },
    )

    # ── Action items — only videos needing attention ───────────────────────
    action_rows = [r for r in rows if r["_priority_raw"] in ("high", "medium")]
    if action_rows:
        st.markdown('<div class="section-head">ACTION ITEMS</div>', unsafe_allow_html=True)
        st.caption(f"{len(action_rows)} video(s) flagged — high priority first.")
        action_rows.sort(key=lambda r: 0 if r["_priority_raw"] == "high" else 1)

        for r in action_rows:
            icon        = PRIORITY_ICON[r["_priority_raw"]]
            content_id  = r.get("_content_id", "").strip()
            section_key = (
                f"long_{content_id}" if content_id
                else f"long_{''.join(c for c in r['Title'] if c.isalnum())[:24]}"
            )
            is_actioned = load_long_video_status(content_id) if content_id else False

            if is_actioned:
                border = "#00b894"
            elif r["_priority_raw"] == "high":
                border = "#ff6b6b"
            else:
                border = "#f5a623"

            st.markdown(f"""
            <div style="background:#1a1a2e;border-left:4px solid {border};border-radius:8px;
                        padding:0.9rem 1.1rem;margin-bottom:0.4rem">
                <div style="font-size:0.7rem;color:#aaa;margin-bottom:0.25rem">{icon} {r['_priority_raw'].upper()} PRIORITY &nbsp;·&nbsp; {r['Published']}</div>
                <div style="font-weight:700;color:#fff;font-size:0.92rem;margin-bottom:0.6rem">{r['Title']}</div>
                <div style="font-size:0.75rem;color:#aaa">CTR <strong style="color:#fff">{r['CTR %']}%</strong>
                    &nbsp;·&nbsp; Avg % Viewed <strong style="color:#fff">{r['Avg % Viewed']}%</strong>
                    &nbsp;·&nbsp; Views <strong style="color:#fff">{r['Views']:,}</strong></div>
                <div style="margin-top:0.6rem;font-size:0.8rem">
                    <span style="color:#4e8cff;font-weight:600">🔧 Fix now:</span>
                    <span style="color:#ccc"> {r['fix_now']}</span>
                </div>
                {"" if r['next_video'] == "—" else f'''<div style="margin-top:0.3rem;font-size:0.8rem">
                    <span style="color:#00b894;font-weight:600">📝 Next video:</span>
                    <span style="color:#ccc"> {r["next_video"]}</span>
                </div>'''}
            </div>""", unsafe_allow_html=True)
            if is_actioned:
                st.markdown(
                    '<p style="margin:0.1rem 0 0.4rem 0.2rem;font-size:0.72rem;'
                    'color:#00b894;font-weight:600">✅ Action taken</p>',
                    unsafe_allow_html=True,
                )

            new_actioned = st.checkbox(
                "Action taken", value=is_actioned, key=f"chk_{section_key}"
            )
            if new_actioned != is_actioned and content_id:
                save_long_video_status(content_id, new_actioned)
                st.rerun()

            snapshot   = f"[CTR {r['CTR %']:.2f}% | Viewed {r['Avg % Viewed']:.0f}% | Views {r['Views']:,} | Subs {r['Subs Gained']:+d}]"
            existing_n = len(load_okr_comments(section_key))
            exp_label  = (
                f"📋 Audit log — {existing_n} {'entry' if existing_n == 1 else 'entries'}"
                if existing_n else "📋 Audit log — record an observation or action"
            )
            with st.expander(exp_label, expanded=False):
                _comments_section(
                    section_key,
                    snapshot_title=snapshot,
                    status_options=["🔍 Observation", "💡 Lesson"],
                )
    else:
        st.success("All long-form videos are healthy or low priority. Keep the current format going.")


def tab_intelligence():
    os.makedirs(INSIGHTS_DIR, exist_ok=True)
    st.markdown('<div class="main-header">💡 Intelligence</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-header">Shorts: AI-generated weekly analysis reports. '
        'Longs: per-video rubric-based guidance from your YouTube Analytics Excel.</div>',
        unsafe_allow_html=True,
    )
    ins_tab1, ins_tab2 = st.tabs(["📊 Shorts", "🎬 Longs"])
    with ins_tab1:
        _tab_intelligence_shorts()
    with ins_tab2:
        _tab_intelligence_longs()


# ─── TAB 4 — REFERENCE ───────────────────────────────────────────────────────

def tab_reference():
    st.markdown('<div class="main-header">📚 Reference</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Channel knowledge, production rules, and setup guides.</div>', unsafe_allow_html=True)

    ref_tab1, ref_tab2, ref_tab3 = st.tabs(["📖 Knowledge Base", "🔧 How-To & Setup", "📋 Video Metadata"])

    with ref_tab1:
        with st.expander("🎯  Subscriber Growth — How to Find Core Loyal Subscribers", expanded=True):
            st.markdown("""
The 30K total subscriber count is largely irrelevant — built on math/science content over 7 years.
New AI subscribers arrive through exactly three routes:

**Route A — Vocab Shorts**
Vocab content converts subscribers at 6x the rate of news shorts. The viewer learns something
genuinely useful, feels seen, and subscribes for more. Always keep vocab shorts in the weekly mix.

**Route B — LinkedIn click-through**
A LinkedIn click arrives with intent. They already trust <span class="name-hi">Sanjay</span>. They convert at far higher rates
than cold Shorts feed viewers. Every LinkedIn post driving YouTube clicks brings exactly the right audience.

**Route C — Short → Long funnel**
When someone watches a short then watches the long, subscriber conversion is much higher.
"Why Your AI Lies" converted at **4.3%** — 6 subs from only 139 views.
The short pulls them in. The long makes them stay.

> **Rule:** Track *net new AI subscribers since May 2026* — not the total subscriber count.
> The 30K total is for external presentation only.
            """, unsafe_allow_html=True)

        with st.expander("📊  CTR on Shorts — What It Actually Measures"):
            st.markdown("""
Most short views come from the **Shorts feed** — these do not generate impressions in the
traditional sense and are not reflected in the CTR figure shown in Analytics.

The CTR figure applies only to **non-feed sources**: YouTube Home · Search · Suggested alongside longs · External links (LinkedIn)

**Why it still matters:**
- **Longevity:** A short with poor search CTR decays once the initial feed push fades.
- **LinkedIn:** Every LinkedIn click is a CTR event. The LinkedIn strategy directly improves this number.

> **Rule:** Shorts CTR = longevity and discovery quality signal. Not a primary launch metric.
            """)

        with st.expander("✅  What Quality Means — Defined Concretely"):
            st.markdown("""
Quality is not a feeling. Every video is measurable:

| Area | Quality threshold |
|---|---|
| Shorts — completion rate | ≥ 62% |
| Shorts — hook | All 5 rubric checks pass |
| Longs — CTR | ≥ 4% |
| Longs — avg % viewed | ≥ 35% |
| Longs — hook score | ≥ 20/25 |
| Script | No AI tells · pronoun check done · role-play test passed |
| Packaging | Title/thumbnail 1-2 punch confirmed before upload |

> If a video misses a threshold, diagnose *which specific element* failed and fix it in the next video.
            """)

        with st.expander("📅  Cadence Rules — Protected and Flexible"):
            st.markdown("""
**Target:** 2 longs + 3 shorts per week
**Minimum:** 2 longs + 2 shorts

> **If anything must be sacrificed — drop a short. Never a long.**

| Day | Content | Time (ET) |
|---|---|---|
| Monday | Short | 18:00 |
| Tuesday | Long 1 | 18:00 |
| Wednesday | Short | 18:00 |
| Thursday | Short | 18:00 |
| Friday | Long 2 | 18:00 |
            """)

        with st.expander("🎬  Why Longs Matter More Than They Look"):
            st.markdown("""
Current long views are low (~116 avg) but subscriber conversion is high:
- "Why Your AI Lies" — **4.3% conversion** (6 subs from 139 views)
- "Afraid AI Will Obsolete You" — **2.45% conversion** (4 subs from 163 views)
- Shorts convert at <1% on average. Longs convert at 2–4x the rate.

The low views are a **packaging problem** (CTR 1.81%), not a content problem.
Fix the title and thumbnail → views improve → subscriber conversion compounds.

Each long is also a **Category 2 credibility asset** — a 10-minute deep-dive on AI governance
positions Sanjay as a credible expert for speaking and consulting. A single consulting contract
exceeds months of AdSense revenue.
            """)

        with st.expander("⚠️  Why the 30K Subscriber Count is Misleading"):
            st.markdown("""
- Built over 7 years on math/science content — not AI
- Bell notification CTR: **0.2–0.3%** (benchmark: 0.5–2.5%)
- Generates only 2–3 views per video from notifications
- Net new AI subscribers since May 2026: **~85**

Legacy subscribers are gradually unsubscribing. Risk: net loss if new AI subs don't outpace churn.

> **Rule:** 30K total = external credibility only. Internal metric = cumulative new AI subs since May 2026.
            """)

        with st.expander("🔴  Traffic Light Thresholds — When to Act"):
            st.markdown("""
| Metric | 🔴 Red — Act now | 🟡 Amber — Monitor | 🟢 Green — Replicate |
|---|---|---|---|
| Long CTR | < 2% | 2–4% | > 4% |
| Long avg % viewed | < 30% | 30–40% | > 40% |
| Short completion rate | < 45% | 45–58% | > 58% |
| Net new subs/week | Negative | 0–10 | > 10 |

**Red for 2 consecutive weeks = mandatory discussion before next publish.**
            """)

        with st.expander("🔗  LinkedIn — The Subscriber Acquisition Channel"):
            st.markdown("""
LinkedIn is the primary source of high-quality AI subscribers.

**Core principle:** Never lead with the video. Lead with the insight.

**Post types:**
- Written thought leadership — no link in post body (LinkedIn penalises external links)
- Native LinkedIn video — download short from YouTube Studio, upload directly
- Pinned comment — add YouTube link immediately after native video goes live

**Timing:** Reply to every comment in the first hour — LinkedIn algorithm reads comment velocity as a push signal.
            """)

    with ref_tab2:
        with st.expander("📋  Monday Workflow — 5 minutes", expanded=True):
            st.markdown("""
**Do this every Monday morning before planning the week.**

1. Open YouTube Studio → Analytics → Content
2. Filter to **Shorts** → Export as Excel — select **All time**
3. Filter to **Videos (Longs)** → Export as Excel — select **All time**
4. Open this dashboard → go to **OKR Tracker** tab
5. Upload both Excel files
6. Review the metrics — check for anything Red
7. Click **Save this week's data**

> Always use **All time** export — not a date-filtered range.
            """)

        with st.expander("📐  How Metrics Are Calculated"):
            st.markdown(f"""
**Two averages are shown for every metric:**
- **Recent** = last **{N_RECENT_SHORTS} shorts** / last **{N_RECENT_LONGS} longs** (sorted by publish date). Covers ~1 month of shorts and ~5 weeks of longs.
- **All-time** = every video since the May 2026 relaunch.
- The delta arrow shows whether recent videos are performing above or below the all-time average.

**Shorts — Avg Completion Rate:** "Stayed to watch (%)" column in the Shorts Analytics Excel. Binary signal.

**Longs — Avg % Viewed:** "Average percentage viewed (%)" column. Continuous retention signal.

**Net new AI subs / week:** Derived by comparing this week's cumulative total (from the Excel) against the previously saved row in the local database. Baseline: 85 net new AI subs as of Aug 2, 2026.
            """)

        with st.expander("🏠  House Rules"):
            st.markdown("""
1. **Feed data every Monday morning.** Gaps break the trend charts.
2. **Always use All time export** from YouTube Studio.
3. **OKR targets are fixed until Dec 31, 2026.** Only change after a deliberate review session with both <span class="name-hi">Sanjay</span> and <span class="name-hi">Shailee</span>.
4. **Benchmark table = floor, not ceiling.** The OKR targets are more ambitious.
5. **Red for 2 consecutive weeks = discussion before next publish** on that specific metric.
6. **Longs are protected.** Drop a short in a tight week — never a long.
7. **Revenue tracking (Category I + II) will be added Q4 2026** once the first signals arrive.
            """, unsafe_allow_html=True)

        with st.expander("🔧  Deployment — GitHub + Streamlit Cloud"):
            st.markdown("""
**Step 1 — Private GitHub repository**
Push the `dashboard/` folder to a **private** GitHub repository. Source code stays private.

**Step 2 — Deploy to Streamlit Cloud**
1. share.streamlit.io → New app → connect your private GitHub repo → main file: `app.py`
2. Deploy. The SQLite database (`funza.db`) lives on Streamlit Cloud's server — not in the repo.

**Step 3 — Restrict access (Viewer Authentication)**
1. In Streamlit Cloud → your app → Settings → Sharing
2. Set to **"Only specific people can view"**
3. Add: `noronha.sanjay@gmail.com` and Shailee's email
4. Viewers must log in once with a free Streamlit Community account (or Google)

This keeps the app completely private with no code changes required.

**Database persistence:** The `funza.db` file persists on Streamlit Cloud's server between sessions for active apps. No additional setup needed.
            """)

        with st.expander("💡  How to Generate an Intelligence Report"):
            st.markdown("""
1. Download your Shorts Analytics Excel from YouTube Studio → Analytics → Content → Shorts → Export All time
2. In a Claude Code session (same project), say: **"Run a Shorts analysis report"**
3. Claude reads `dashboard/weekly_insights/INSIGHTS_PROTOCOL.md` (the protocol file), processes the Excel, and saves a JSON to `dashboard/weekly_insights/YYYY-MM-DD_shorts.json`
4. Refresh this dashboard → go to **Intelligence** tab → select the new report from the dropdown

No upload to the dashboard required — Claude writes the file directly.
            """)

    with ref_tab3:
        with st.expander("📅  Video Cadence", expanded=True):
            st.markdown("""
**Target:** 2 Longs (L) + 3 Shorts (S) every week &nbsp;·&nbsp; **Minimum:** 2 Longs + 2 Shorts
> If anything must be cut — drop a Short. Never a Long.
""")
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Legend**")
                st.markdown("""
| Code | Meaning |
|---|---|
| L | Long video |
| S | Short video |
| EOD | End of day |
""")
            with col2:
                st.markdown("**Responsibilities**")
                st.markdown("""
| Task | Sanjay | Shailee |
|---|---|---|
| Script writing | L, S | — |
| Script review | — | L, S |
| Video creation | L, S | — |
| Video editing (Descript) | L | S |
| Metadata (excl. title & thumbnail) | L, S | — |
| Title & thumbnail | — | L, S |
| Publishing | L, S | — |
""")
            st.markdown("---")
            col3, col4, col5 = st.columns(3)
            with col3:
                st.markdown("**Script Release**")
                st.markdown("""
| Video | Deadline |
|---|---|
| L1 | Tue EOD |
| L2 | Thu EOD |
| S1 | Sat EOD |
| S2, S3 | Sun EOD |
""")
            with col4:
                st.markdown("**Script Review**")
                st.markdown("""
| Video | Deadline |
|---|---|
| L1 | Wed EOD |
| L2 | Fri EOD |
| S1, S2, S3 | Mon EOD |
""")
            with col5:
                st.markdown("**Publish Schedule (Midnight)**")
                st.markdown("""
| Day | Video |
|---|---|
| Monday | L1 |
| Tuesday | L2 |
| Wednesday | S1 |
| Thursday | S2 |
| Friday | S3 |
""")

        with st.expander("🎯  Topic Selection Workflow", expanded=True):
            st.markdown(
                '<div style="font-size:0.82rem;color:#aaa;margin-bottom:1.2rem">'
                'Every video idea passes through three gates before entering the pipeline. '
                'Work through the steps in order — do not move to packaging until all three are cleared.'
                '</div>', unsafe_allow_html=True,
            )
            # Step 1
            st.markdown(
'<div style="background:#1a2744;border-left:3px solid #4e8cff;border-radius:6px;'
'padding:0.8rem 1rem;margin-bottom:0.8rem">'
'<div style="font-size:0.7rem;color:#4e8cff;font-weight:700;letter-spacing:0.05em;margin-bottom:0.4rem">'
'STEP 1 &nbsp;·&nbsp; TOPIC IDEA &nbsp;·&nbsp; 🧑 Sanjay &amp; Shailee</div>'
'<div style="font-size:0.82rem;color:#ccc;margin-bottom:0.5rem">Generate candidates from any of these sources:</div>'
'<ul style="margin:0;padding-left:1.2rem;color:#ccc;font-size:0.82rem;line-height:1.7">'
'<li><strong style="color:#fff">Persona interviews</strong> — what Marisa and Sevrien tell you they need (target: one meeting per week)</li>'
'<li><strong style="color:#fff">LinkedIn</strong> — what is circulating in professional networks right now</li>'
'<li><strong style="color:#fff">News articles</strong> — curated sources: Economist, NYT, Stanford HAI, The Verge, Ethan Mollick</li>'
'<li><strong style="color:#fff">Competitor channels</strong> — demand signals from Jeff Su, Nate B Jones, MIT Monk</li>'
'<li><strong style="color:#fff">Professional judgment</strong> — emerging topics spotted early from direct AI experience</li>'
'</ul>'
'</div>', unsafe_allow_html=True,
            )
            # Step 2
            st.markdown(
'<div style="background:#2a1f3d;border-left:3px solid #a855f7;border-radius:6px;'
'padding:0.8rem 1rem;margin-bottom:0.6rem">'
'<div style="font-size:0.7rem;color:#a855f7;font-weight:700;letter-spacing:0.05em;margin-bottom:0.4rem">'
'STEP 2 &nbsp;·&nbsp; DRIVER EVALUATION &nbsp;·&nbsp; 🤖 Claude evaluates · 🧑 Sanjay confirms</div>'
'<div style="font-size:0.82rem;color:#ccc">'
'Describe the topic to Claude in chat. Claude returns: which drivers it hits, which lane it sits in, '
'which persona it serves, and a go / no-go. Sanjay confirms before the topic moves forward.'
'</div>'
'</div>', unsafe_allow_html=True,
            )
            st.markdown(
"""**Psychological drivers** — the emotional motivation pulling the viewer in. Topic must hit **≥ 2 of 3** to qualify.

| Driver | The viewer's internal question |
|---|---|
| **Career Advancement** | *If I don't understand this, I fall behind.* Job security, credibility with leadership, ability to perform. |
| **AI Literacy** | *I'm performing confidence I don't have.* A term or concept heard constantly but never understood. |
| **Governance & Operational Security** | *Something could go wrong and I'll be held responsible.* Rules closing in, risks not yet managed. |

> If only 1 driver is present, the topic is rejected — do not proceed to Step 3.
"""
            )
            st.markdown(
"""**The 4 lanes** — what type of value the content delivers. Every video sits in exactly one lane.

| Lane | What it delivers | Home persona |
|---|---|---|
| **Learn** | Vocab terms, current AI news, what is happening and why it matters | Marisa |
| **Use** | How AI fits real work tasks; real peer cases and tool walkthroughs | Marisa |
| **Lead** | Managing AI without doing it — decisions, business cases, guiding a team | Marisa + Sevrien |
| **Guard** | Risk, governance, compliance — what rules are coming and what to do | Sevrien + Marisa |

Assign the lane before moving to Step 3.
"""
            )
            # Step 3
            st.markdown(
'<div style="background:#1a2a1e;border-left:3px solid #00b894;border-radius:6px;'
'padding:0.8rem 1rem;margin-top:0.6rem">'
'<div style="font-size:0.7rem;color:#00b894;font-weight:700;letter-spacing:0.05em;margin-bottom:0.4rem">'
'STEP 3 &nbsp;·&nbsp; DEMAND CHECK &nbsp;·&nbsp; 🧑 Sanjay</div>'
'<div style="font-size:0.82rem;color:#ccc;margin-bottom:0.6rem">'
'The science step. Check as many signals as apply — the more that confirm, the stronger the topic.'
'</div>'
'<ol style="margin:0;padding-left:1.2rem;color:#ccc;font-size:0.82rem;line-height:1.9">'
'<li><strong style="color:#fff">YouTube autocomplete (incognito)</strong> — open YouTube in incognito and type the topic. '
'Autocomplete = proven search demand. Note: incognito shows you <em>title/keyword competition</em> — '
'how other creators packaged this topic — not total demand. Use Google Trends for demand.</li>'
'<li><strong style="color:#fff">Google Trends (Web Search)</strong> — is volume rising, flat, or declining? '
'Rising = get in now. Declining = moment has passed. '
'Also check <em>Related queries</em> — breakout or +500%+ terms reveal what adjacent angle is spiking.</li>'
'<li><strong style="color:#fff">Small channel breakout check</strong> — search YouTube for the topic and look for '
'channels under 20K subscribers that earned 100K+ views on this topic. '
'That is the algorithm pushing the content, not the subscriber base. Demand is proven.</li>'
'<li><strong style="color:#fff">Content gap check</strong> — zero YouTube videos on a topic with strong Google Trends '
'web search volume = open lane. Win it by framing around a forced operational decision '
'(e.g. "Open Weights vs. Closed APIs: The Enterprise Decision Guide") — never a dry overview.</li>'
'<li><strong style="color:#fff">Own channel data</strong> — has a related short already performed? '
'The strongest signal of all — your specific audience responding.</li>'
'</ol>'
'<div style="margin-top:0.9rem;padding:0.6rem 0.85rem;background:#162030;border:1px solid #2a4a6a;border-radius:6px">'
'<div style="font-size:0.7rem;color:#4e8cff;font-weight:700;letter-spacing:0.05em;margin-bottom:0.5rem">✅ GREENLIGHT GATE — all 3 must pass</div>'
'<div style="font-size:0.8rem;color:#ccc;line-height:1.85">'
'<strong style="color:#fff">1. Google Trends Y-axis</strong> — sustained score above <strong style="color:#fff">20</strong>, '
'or relative height ≥ 20% of a known industry anchor term (e.g. "artificial intelligence").<br>'
'<strong style="color:#fff">2. Rising queries</strong> — at least 1–2 <span style="background:#1a5276;color:#7fc8f8;'
'font-size:0.68rem;font-weight:700;padding:0.05rem 0.3rem;border-radius:3px">BREAKOUT</span> '
'or <strong style="color:#fff">+100%</strong> rising terms in Google Trends Related queries for this topic.<br>'
'<strong style="color:#fff">3. YouTube competition</strong> — at least one competitor video with a '
'<strong style="color:#fff">&gt; 5× view-to-subscriber ratio</strong> '
'(e.g. 29K views on a 1.6K channel = 18×). Algorithm pushed it beyond the subscriber base — demand is real.'
'</div>'
'</div>'
'<div style="margin-top:0.6rem;padding:0.5rem 0.75rem;background:#1e2a20;border-radius:4px;'
'font-size:0.78rem;color:#aaa;line-height:1.6">'
'<strong style="color:#00b894">Short-first vs. long-first:</strong> Short first is ideal for testing demand cheaply. '
'Going straight to a long is fine if (a) bandwidth is limited and (b) the topic is framed around an evergreen '
'decision — not a 48-hour news trend. News trends require a short to catch the wave; evergreen decisions can wait for the long.'
'</div>'
'<div style="margin-top:0.5rem;padding:0.5rem 0.75rem;background:#2a1a1a;border-radius:4px;'
'font-size:0.78rem;color:#ff6b6b;font-weight:600">'
'⚠️&nbsp; Step 3 fails → topic is dropped. Not parked. Not revisited. Start fresh with a new idea.'
'</div>'
'</div>', unsafe_allow_html=True,
            )

        with st.expander("✅  Production Checklist — Shorts & Long-Form"):
            st.markdown("""
**Run this checklist before every upload — shorts and long-form.**

---

**📝 Script**
- [ ] Script has been reviewed
- [ ] Hook has been scored against the hook rubric

---

**🎥 Recording**
- [ ] No disturbing background e.g. red lighting, unnecessary objects
- [ ] Sanjay is presentable
- [ ] Rule of thirds applied
- [ ] Sanjay in full frame — head not touching border of frame
- [ ] Eye contact with camera lens maintained
- [ ] Audio levels checked before recording

---

**✂️ Editing**
- [ ] No gaps at start and end of video
- [ ] Video speed is correct
- [ ] Video lighting is correct
- [ ] No long word gaps
- [ ] Studio sound enabled
- [ ] Scene transitions are clean — no caption jumps
- [ ] B-roll used is appropriate
- [ ] Captions are consistent — font, size
- [ ] Captions are positioned correctly in the frame
- [ ] Like and Subscribe GIF is consistent
- [ ] Audiogram text is correct — size, font, bold
- [ ] Hook stands out

---

**🏷️ Video Metadata**
- [ ] Description is complete and formatted correctly
- [ ] Tags are added in YouTube Studio
- [ ] Title is finalised and matches rubric score

---

**🚀 Pre-Upload**
- [ ] Video is uploaded as Unlisted at least 2 hours before go-live
- [ ] Scheduled to go Public at 18:00 ET (New York)

---

**📺 Long-Form Only**
- [ ] Chapter markers are accurate and timestamped correctly
- [ ] End screen is set up
- [ ] Cards are added
- [ ] A/B test set up for title and thumbnail — YouTube Test & Compare
            """)

        with st.expander("🏷️  Title Rubric — Long-Form", expanded=False):
            st.markdown(
                '<div style="background:#1e3a2f;border-left:3px solid #f5a623;padding:0.5rem 1rem;border-radius:4px;margin-bottom:1rem">'
                '🔑 <strong>Ownership:</strong> Claude scores · <span class="name-hi">Sanjay</span> scores &amp; finalises · <span class="name-hi">Shailee</span> approves before publishing'
                '</div>', unsafe_allow_html=True,
            )
            st.markdown("""
**Both gates must PASS before scoring. A title that fails either gate goes back for a rewrite.** *(Full rubric: long_rubrics.md Part 8)*

---

**🚦 Gate 1 — Persona Framing (hard pass/fail)**

Every title must signal professional context. Two valid patterns:
- **Pattern A (default):** role or scenario named in the core phrase — *"ChatGPT for Managers: The AI Policy IT Hasn't Told You"*
- **Pattern B (aspirational):** scenario so inherently professional only the right person clicks — *"What Your IT Policy Isn't Telling You About ChatGPT"*

**PASS:** unambiguously for a working professional — named role, workplace scenario, or situation only a professional recognises.
**FAIL:** could attract a developer, student, or general AI enthusiast equally → rewrite.

Anti-pattern — never: bracketed suffixes "(For Non-Technical Professionals)" — wastes characters, looks academic, gets truncated on mobile.

---

**🚦 Gate 2 — Existing-Meaning Gate (hard pass/fail)**

Before publishing, search every coined term or acronym in the title on YouTube.
- **PASS:** existing meaning matches the video's topic → YouTube files it correctly.
- **FAIL:** term already means something else → YouTube classifies the video by the wrong meaning → wrong audience → low CTR → rewrite.

*Example:* "FOBO" alone → anxiety/neurodivergence content. Anchor it: "AI Is About to Make You Obsolete — The New Career Fear."

---

**📊 Scoring — 5 dimensions, 1–5 each. Target 20+/25.**

| Dimension | What it measures | Who scores |
|---|---|---|
| Clarity | Stranger understands instantly? | Claude + Sanjay |
| Curiosity Gap | Creates "I need to know this" without misleading? | Claude + Sanjay |
| SEO / Searchability | Would someone type this into YouTube search? | Sanjay (YouTube Autocomplete) |
| Front-loading | Key words in first 50–60 characters? | Claude (counts characters) |
| Thumbnail Compatibility | Title and thumbnail say different things? | Sanjay only |

**1-2 Punch:** title = credible promise. Thumbnail = emotional hook. They must say different things.
            """)

        with st.expander("🏷️  Title Rubric — Shorts"):
            st.markdown(
                '<div style="background:#1e3a2f;border-left:3px solid #f5a623;padding:0.5rem 1rem;border-radius:4px;margin-bottom:1rem">'
                '🔑 <strong>Ownership:</strong> <span class="name-hi">Shailee</span> chooses the title · <span class="name-hi">Sanjay</span> approves before publishing'
                '</div>', unsafe_allow_html=True,
            )
            st.markdown("""
**Hard limit: under 50 characters.** Every top performer complies. *(Full rubric: Packaging_Guide_Titles_Thumbnails.md)*

A strong title does **at least two** of these three:
1. **Names a specific actor** — person, company, country, institution. Never "experts" or "a CEO".
2. **Creates an open loop** — raises a question only watching answers. Close with tension, not the answer.
3. **Personal stakes in the final words** — last 3 words put the viewer inside the story.

**Same Persona Framing Rule applies** — professional context via named role/scenario or inherently professional situation. No bracketed suffixes.

**Anti-patterns (confirmed by channel data):**

| Pattern | Example | Result |
|---|---|---|
| Listicle framing | "3 Checks Before You Trust AI" | 12% stayed — worst on channel |
| Educational/dry | "What Is an LLM?" | Buried in feed |
| Title answers itself | "Why AI Wealth Isn't For You" | 21.4% stayed — viewer's brain says "already know" |
| Metaphor as concept | "AI Agents Work Exactly Like James Bond" | Classified as spy content |
| Hashtag in title | "AI Literacy #ailiteracy" | Suppresses feed reach |
            """)

        with st.expander("🖼️  Thumbnail Rubric — Long-Form"):
            st.markdown(
                '<div style="background:#1e3a2f;border-left:3px solid #f5a623;padding:0.5rem 1rem;border-radius:4px;margin-bottom:1rem">'
                '🔑 <strong>Ownership:</strong> <span class="name-hi">Sanjay</span> creates the thumbnail · <span class="name-hi">Shailee</span> approves before publishing'
                '</div>', unsafe_allow_html=True,
            )
            st.markdown("""
**Five steps in order — do not skip to design until all five are answered.** *(Full rubric: long_rubrics.md Part 9)*

1. **Dominant sentiment** — what is the single emotional core? Not the topic — the feeling.
2. **Professional Context Check** — would Marisa or Sevrien see this on their phone in 0.5 seconds and know it's for them? If the visual could be mistaken for a tech/developer or entertainment channel, it's wrong.
3. **Imagery** — office environments, laptops, corporate documents, business analogies (locked briefcase, open postcard, signed contract). Image must communicate the feeling without text.
4. **Text** — **2–4 words maximum.** Impact font, white + `#de0f3f` accent on the key word. Creates tension or asks a question. Examples: "THEY KNOW" / "IS IT SAFE?" / "THE LEAK" / "ALREADY RUNNING". Never explains.
5. **Sanjay's portrait** — only if it adds energy or reaction. Never required. Two valid approaches:
   - **Real photo** (rear iPhone, chest up) → background removed in remove.bg → placed in Canva
   - **AI-generated portrait** using a real photo of Sanjay as reference → generated to match the background style and lighting → placed in Canva. AI quality is now indistinguishable at thumbnail size and ensures visual consistency with an AI-generated background.
   - **Never:** a generic AI avatar with no reference to Sanjay's actual appearance.

**Visual anti-patterns — never use:**
- Matrix code / cascading green numbers — developer/hacker signal
- Cartoonish or humanoid robots — tech enthusiast signal
- Gamer aesthetics (neon, explosive effects, dramatic dark sci-fi)
- Sci-fi or futuristic imagery — abstract, not professionally relevant

**Canvas:** 1280×720 PNG. A/B test variants with YouTube Test & Compare.
            """)

        with st.expander("🖼️  Thumbnail Rubric — Shorts"):
            st.markdown(
                '<div style="background:#1e3a2f;border-left:3px solid #f5a623;padding:0.5rem 1rem;border-radius:4px;margin-bottom:1rem">'
                '🔑 <strong>Ownership:</strong> <span class="name-hi">Shailee</span> creates the thumbnail · <span class="name-hi">Sanjay</span> approves before publishing'
                '</div>', unsafe_allow_html=True,
            )
            st.markdown("""
**Shorts thumbnails govern the long tail** — not the initial feed push (~80% of views come from the swipe feed where thumbnails aren't shown). They matter for Search, the Shorts shelf, and the channel page. *(Full guide: Packaging_Guide_Titles_Thumbnails.md)*

**Design checklist:**
- **Impact** font · accent red `#de0f3f` · readable at 320px wide
- **Centre-weighted** — YouTube crops both left and right edges in the Shorts feed
- **Word budget: 1–3 words**
- Visual must signal professional/workplace context
- Sanjay's portrait: real photo (rear iPhone, chest up, background removed) OR AI-generated portrait using a real photo as reference — matched to background style. Never a generic AI avatar.

**Same visual anti-patterns apply:** no matrix code, no robots, no gamer aesthetics, no sci-fi.

**How to set the thumbnail (Baked-In Technique):**
1. Design the frame in Canva (9:16)
2. Insert as a 1-second still at the END of the video in Descript
3. On upload in YouTube mobile app, slide frame selector to that frame
            """)

        with st.expander("📄  Description Rubric — Long-Form"):
            st.markdown(
                '<div style="background:#1e3a2f;border-left:3px solid #f5a623;padding:0.5rem 1rem;border-radius:4px;margin-bottom:1rem">'
                '🔑 <strong>Ownership:</strong> <span class="name-hi">Sanjay</span> drafts (with Claude from transcript) · <span class="name-hi">Shailee</span> approves before publishing'
                '</div>', unsafe_allow_html=True,
            )
            st.markdown("""
**Built from the finished transcript — never written from scratch.** *(Full format: long_rubrics.md Part 10)*

**Structure (in order):**

**1. Opening hook — 2 lines max, visible before "Show More"**
- State the core tension or counterintuitive premise
- **Embed the top 2–3 Google Trends breakout terms for this topic naturally in these lines** — this is what the algorithm indexes before "Show More". Check Google Trends related queries before writing.
- Do **not** start with "In this video…"

**2. Viewer's situation** — 2–3 sentences, second person, no jargon. Who this is for in their own words.

**3. How you approached the topic** — what work you did so they didn't have to.

**4. Chapter markers** — pulled from transcript timestamps
```
━━━━━━━━━━━━━━━━━━━━
CHAPTERS
━━━━━━━━━━━━━━━━━━━━
00:00 — Introduction
01:15 — [Key point 1]
```

**5. Resources & links** — every course, tool, or resource mentioned. Include price or "free".

**6. About FunzAI** — one-sentence channel promise + subscribe + LinkedIn links.

**7. Hashtags** — 8–10 minimum, up to 15.
Always include: `#ArtificialIntelligence #AILiteracy #AIForProfessionals #FutureOfWork #AIExplained`

> **Front-end vs back-end split:** The title and thumbnail are written for human psychology (persona + tension). The description is written for the algorithm — keywords here tell YouTube what the video is about and which viewer cohort to route it to.

**Division of labour:** Claude drafts from transcript · Sanjay adds actual resource links before publishing.
            """)

        with st.expander("📄  Description Rubric — Shorts"):
            st.markdown(
                '<div style="background:#1e3a2f;border-left:3px solid #f5a623;padding:0.5rem 1rem;border-radius:4px;margin-bottom:1rem">'
                '🔑 <strong>Ownership:</strong> <span class="name-hi">Shailee</span> drafts the description · <span class="name-hi">Sanjay</span> approves before publishing'
                '</div>', unsafe_allow_html=True,
            )
            st.markdown("""
**Structure: promise + subscribe nudge first, then overview.** *(Full format: Funza_Shorts_Production_Rubric.md Section 2)*

**Line 1:** The core benefit or insight in one line — what the viewer just learned or will learn. **Include the 1–2 highest-volume search terms for this topic naturally** — this is what the algorithm indexes first.

**Line 2:** Subscribe nudge — "Follow for more AI explained for professionals."

**Then:** 1–2 sentence video overview.

**Then:** One-sentence FunzAI blurb.

**Hashtags:** Exactly **3 hashtags** — highly targeted, no clutter. The Tags field in YouTube Studio handles broader discovery.

Always include `#AILiteracy` as one of the three. Add two topic-specific tags.

**Do not start with "In this video…"**
            """)

        with st.expander("🏷️  Tags — Long-Form"):
            st.markdown("""
**Hard limit: 500 characters. Do not pad to the limit — quality over quantity.**

**Priority order (front-load the list in this order):**

1. **Exact search phrases** — what someone would type into YouTube to find this video. These lead. E.g. `what is an AI agent`, `AI agents explained`, `AI agent vs chatbot`.
2. **Named entities in the video** — courses, tools, people, platforms, institutions mentioned by name. E.g. `ChatGPT`, `Harvard Business School`, `Andrew Ng`.
3. **Audience-specific phrases** — `ai for professionals`, `ai for non-technical professionals`, `ai for managers`.
4. **Standard misspelling** — `artifical intelligence` (missing first *i*). Goes on every AI video. This is intentional.
5. **Broader topic tags** — `artificial intelligence`, `ai literacy`, `future of work`, `ai explained`.

**Standard tags — include on every long-form video:**
```
ai literacy, artificial intelligence, artifical intelligence, future of work, ai for professionals
```

**Target:** 15–20 tags. Do not include tags with no realistic search volume (e.g. channel name, creator name, year tags like `AI 2026`).
            """)

        with st.expander("🏷️  Tags — Shorts"):
            st.markdown("""
**Hard limit: 500 characters. Target: 8–12 tags.**

**Same priority order as long-form — but lead more sharply on the specific topic.**

For a **vocabulary short** (RAG, tokens, guardrails, etc.):
- Lead with the exact term and its search variants: `what is RAG`, `RAG explained`, `retrieval augmented generation`
- Then audience phrases, then the standard set

For a **news or trend short**:
- Lead with the named entity or event: `OpenAI`, `EU AI Act`, `ChatGPT update`
- Then the AI angle phrases, then the standard set

**Standard tags — include on every short:**
```
ai literacy, artificial intelligence, artifical intelligence, future of work, ai for professionals
```

**Do not include:** the channel name, year tags (`AI 2026`), or generic tags that don't match the specific video topic.
            """)

        with st.expander("🔍  Algorithm Indexing — Front-End vs Back-End"):
            st.markdown(
                '<div style="background:#1e3a2f;border-left:3px solid #f5a623;padding:0.5rem 1rem;border-radius:4px;margin-bottom:1rem">'
                '🔑 <strong>Applies to every video.</strong> Title/thumbnail = human psychology. Description/script = algorithm indexing. Both matter. Neither substitutes for the other.'
                '</div>', unsafe_allow_html=True,
            )
            st.markdown("""
**The split:**

| Layer | Written for | Goal |
|---|---|---|
| **Title + Thumbnail** | Human psychology — persona relevance + tension | Drive CTR from the right viewer |
| **Description + Script** | YouTube's algorithm — keyword indexing | Route the video to the right audience cohort |

These are different jobs. A title optimised for keywords loses the click. A description optimised for tension loses the algorithm. Never confuse the two.

---

**Description — keyword rule:**
Before writing the opening hook, check Google Trends → Related queries for the video's topic. The top 2–3 breakout or rising terms go into the **first 2 visible lines** (before "Show More") — naturally embedded in the tension sentence, not listed as keywords.

*Example for a video on AI models going rogue:*
> "Four AI models escaped their sandboxes in two weeks — OpenAI, Anthropic, Meta, and the UK's AISI all confirmed incidents. Open weights restrictions and autonomous hacking are no longer theoretical."

`OpenAI`, `Anthropic`, `open weights`, `autonomous hacking` are all indexed before the viewer clicks "Show More."

---

**Script — first 60 seconds rule:**
YouTube transcribes every video with speech-to-text and uses the transcript to semantically index the content and map viewer cohorts. The first 60 seconds carry the most weight.

**Before finalising the script hook, check:** do the top 2–3 Google Trends terms for this topic appear naturally in the first 60 seconds of spoken content?

This does not mean keyword-stuffing the hook. It means ensuring the natural story you tell in the opening mentions the specific named entities and terms people are actually searching for.

*Example:* a hook about AI hacking incidents that naturally names OpenAI, Anthropic, and "open weights" in the first 30 seconds serves both the human viewer (concrete, specific) and the algorithm (indexed for the right search terms) simultaneously.

---

**Tags:** Secondary signal only. YouTube gives minimal weight to the tag box compared to spoken transcripts and description metadata. Fill tags per the rubric above — but do not rely on them for discovery.
""")


# ─── MAIN ─────────────────────────────────────────────────────────────────────

def tab_pipeline():
    st.markdown('<div class="main-header">🎬 Pipeline</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Plan and track every video — 3 shorts + 2 longs per week.</div>', unsafe_allow_html=True)

    pipe_tab1, pipe_tab2 = st.tabs(["➕  Plan a Video", "📋  Pipeline View"])

    # ── PLAN A VIDEO ─────────────────────────────────────────────────────────
    with pipe_tab1:
        okr_periods_df = load_okr_periods()
        week_opts      = get_week_options()

        # Type selector outside form so category list updates reactively
        col_type, col_id = st.columns([2, 2])
        with col_type:
            video_type = st.selectbox(
                "Video type", ["Short", "Long"],
                key="pipe_type_sel",
            )
        with col_id:
            suggested_id = get_next_video_id(video_type)
            video_id = st.text_input(
                "Video ID (auto-suggested — override if needed)",
                value=suggested_id,
                key=f"pipe_vid_id_{video_type}",  # resets default when type changes
            )

        cats = SHORT_CATS if video_type == "Short" else LONG_CATS

        with st.form("add_video_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                week_labels  = [lbl for _, lbl in week_opts]
                week_sel_idx = st.selectbox(
                    "Publishing week",
                    range(len(week_opts)),
                    format_func=lambda i: week_opts[i][1],
                )
                week_key_sel = week_opts[week_sel_idx][0]
            with c2:
                category = st.selectbox(
                    "Category",
                    list(cats.keys()),
                    format_func=lambda k: cats[k],
                )

            c3, c4 = st.columns(2)
            with c3:
                suitable_for = st.selectbox(
                    "Suitable for",
                    list(PERSONA_OPTS.keys()),
                    format_func=lambda k: PERSONA_OPTS[k],
                )
            with c4:
                recommended_by = st.selectbox("Recommended by", ["Sanjay", "Shailee"])

            title = st.text_input("Video title ✱")

            c5, c6 = st.columns(2)
            with c5:
                source = st.text_input("Video source (optional — article, event, data)")
            with c6:
                okr_period_label = st.selectbox(
                    "OKR Period",
                    okr_periods_df["label"].tolist() if not okr_periods_df.empty else ["Aug–Dec 2026"],
                )

            ch1, ch2 = st.columns(2)
            with ch1:
                demand_checked = st.checkbox("Demand checked")
            with ch2:
                video_approved = st.checkbox("Video approved")
            details = st.text_area("Additional details (optional)")

            submitted = st.form_submit_button("💾  Add to pipeline", type="primary")

        if submitted:
            if not title.strip():
                st.warning("Title is required.")
            elif not video_id.strip():
                st.warning("Video ID is required.")
            else:
                period_id = None
                if not okr_periods_df.empty:
                    match = okr_periods_df[okr_periods_df["label"] == okr_period_label]
                    if not match.empty:
                        period_id = int(match.iloc[0]["id"])
                if save_pipeline_entry(
                    video_id.strip(), week_key_sel, video_type, category,
                    source.strip(), demand_checked, suitable_for,
                    title.strip(), details.strip(), period_id,
                    recommended_by, video_approved,
                ):
                    st.success(f"✅ {video_id.strip()} added to pipeline.")
                    # Clear outside-form widgets so they reset on the next render
                    for k in [f"pipe_vid_id_{video_type}", "pipe_type_sel"]:
                        st.session_state.pop(k, None)
                    st.rerun()

    # ── PIPELINE VIEW ─────────────────────────────────────────────────────────
    with pipe_tab2:
        all_df = load_pipeline()

        if all_df.empty:
            st.info("No videos in the pipeline yet. Use 'Plan a Video' to add the first one.")
            return

        # ── Cadence check ──────────────────────────────────────────────────
        st.markdown('<div class="section-head">CADENCE CHECK — 3 shorts + 2 longs per week</div>',
                    unsafe_allow_html=True)

        weeks_in_pipeline = sorted(all_df["week_key"].unique())
        cadence_cols = st.columns(min(len(weeks_in_pipeline), 4))

        for i, wk in enumerate(weeks_in_pipeline[:4]):
            wk_df   = all_df[all_df["week_key"] == wk]
            n_short = int((wk_df["video_type"] == "Short").sum())
            n_long  = int((wk_df["video_type"] == "Long").sum())
            n_pub   = int((wk_df["status"] == "Published").sum())
            s_ok    = n_short >= 3
            l_ok    = n_long  >= 2
            overall = "🟢" if (s_ok and l_ok) else ("🟡" if (n_short + n_long > 0) else "🔴")
            with cadence_cols[i]:
                st.markdown(
                    f'<div class="sb-card"><strong>{overall} {week_key_to_label(wk)}</strong><br>'
                    f'Shorts {"✅" if s_ok else "🟡"} {n_short}/3 &nbsp;|&nbsp; '
                    f'Longs {"✅" if l_ok else "🟡"} {n_long}/2<br>'
                    f'<span style="font-size:0.75rem;color:#aaa">✅ Published: {n_pub}</span></div>',
                    unsafe_allow_html=True,
                )

        # ── Filter & table ─────────────────────────────────────────────────
        st.markdown('<div class="section-head">ALL PIPELINE ENTRIES</div>', unsafe_allow_html=True)

        fc1, fc2, fc3 = st.columns(3)
        with fc1:
            wk_filter_opts = ["All weeks"] + [week_key_to_label(w) for w in weeks_in_pipeline]
            wk_filter = st.selectbox("Filter by week", wk_filter_opts, key="pipe_wk_filter")
        with fc2:
            type_filter = st.selectbox("Filter by type", ["All", "Short", "Long"], key="pipe_type_filter")
        with fc3:
            status_filter = st.selectbox("Filter by status",
                                         ["All"] + PIPELINE_STATUSES, key="pipe_status_filter")

        display_df = all_df.copy()
        if wk_filter != "All weeks":
            sel_wk = weeks_in_pipeline[[week_key_to_label(w) for w in weeks_in_pipeline].index(wk_filter)]
            display_df = display_df[display_df["week_key"] == sel_wk]
        if type_filter != "All":
            display_df = display_df[display_df["video_type"] == type_filter]
        if status_filter != "All":
            display_df = display_df[display_df["status"] == status_filter]

        display_df["Week"]      = display_df["week_key"].apply(week_key_to_label)
        display_df["Demand ✓"]  = display_df["demand_checked"].apply(lambda x: "✅" if x else "—")
        display_df["Approved"]  = display_df["video_approved"].apply(lambda x: "✅" if x else "—")
        display_df["Status"]    = display_df["status"].apply(lambda s: f"{STATUS_EMOJI.get(s,'')} {s}")

        st.dataframe(
            display_df[["video_id", "Week", "video_type", "category",
                         "suitable_for", "recommended_by", "title",
                         "Demand ✓", "Approved", "Status"]].rename(columns={
                "video_id": "Video ID", "video_type": "Type",
                "category": "Category", "suitable_for": "Persona",
                "recommended_by": "Rec. by", "title": "Title",
            }),
            use_container_width=True, hide_index=True,
        )

        # ── Update / Delete ────────────────────────────────────────────────
        st.markdown('<div class="section-head">UPDATE OR DELETE AN ENTRY</div>', unsafe_allow_html=True)

        if display_df.empty:
            st.caption("No entries match the current filter.")
        else:
            entry_options = {
                row["id"]: f"{row['video_id']} · {row['title'][:50]}"
                for _, row in display_df.iterrows()
            }
            selected_id = st.selectbox(
                "Select entry to update/delete",
                list(entry_options.keys()),
                format_func=lambda eid: entry_options[eid],
                key="pipe_entry_sel",
            )
            sel_row = all_df[all_df["id"] == selected_id].iloc[0]

            st.caption(f"Recommended by: **{sel_row['recommended_by']}**")

            with st.form("update_pipeline_form"):
                upd_title    = st.text_input("Title", value=str(sel_row["title"]))
                # Week selector — past 8 weeks + next 4 weeks
                today = date.today()
                edit_week_opts = []
                for delta in range(-8, 5):
                    d = today + timedelta(weeks=delta)
                    iso = d.isocalendar()
                    wk = f"{iso[0]}-W{iso[1]:02d}"
                    if wk not in [w for w, _ in edit_week_opts]:
                        edit_week_opts.append((wk, week_key_to_label(wk)))
                cur_wk = sel_row["week_key"]
                cur_wk_idx = next(
                    (i for i, (w, _) in enumerate(edit_week_opts) if w == cur_wk), 0
                )
                upd_week_idx = st.selectbox(
                    "Week",
                    range(len(edit_week_opts)),
                    index=cur_wk_idx,
                    format_func=lambda i: edit_week_opts[i][1],
                )
                upd_week_key = edit_week_opts[upd_week_idx][0]
                upd_status   = st.selectbox(
                    "Status", PIPELINE_STATUSES,
                    index=PIPELINE_STATUSES.index(sel_row["status"]),
                )
                chk_col1, chk_col2 = st.columns(2)
                with chk_col1:
                    upd_demand = st.checkbox(
                        "Demand checked",
                        value=bool(sel_row["demand_checked"]),
                    )
                with chk_col2:
                    upd_approved = st.checkbox(
                        "Video approved",
                        value=bool(sel_row["video_approved"]),
                    )
                upd_detail   = st.text_area("Details", value=str(sel_row["details"] or ""))
                u1, u2 = st.columns(2)
                with u1:
                    save_btn = st.form_submit_button("💾 Save changes", type="primary")
                with u2:
                    del_btn = st.form_submit_button("🗑️ Delete entry")

            if save_btn:
                if upd_status == "Published" and not upd_approved:
                    st.error("Cannot mark as Published — video hasn't been approved yet. "
                             "Tick 'Video approved' first.")
                elif update_pipeline_entry(selected_id, upd_title, upd_status,
                                           upd_detail, upd_approved, upd_demand,
                                           upd_week_key):
                    st.success("Updated.")
                    st.rerun()
            if del_btn:
                if delete_pipeline_entry(selected_id):
                    st.success("Deleted.")
                    st.rerun()


def tab_issues():
    st.markdown('<div class="section-head">🔧 Dashboard Issues</div>', unsafe_allow_html=True)
    st.caption("Use this tab to log bugs, improvement requests, or questions about the dashboard. Both Sanjay and Shailee can raise and resolve issues here.")

    issues_df = load_issues()
    open_df     = issues_df[issues_df["status"] == "Open"]
    resolved_df = issues_df[issues_df["status"] == "Resolved"]

    PRIORITY_COLOUR = {"High": "#de0f3f", "Medium": "#f5a623", "Low": "#00b894"}

    # ── Open issues ──────────────────────────────────────────────────────────
    st.markdown(f"**Open issues — {len(open_df)}**")
    if open_df.empty:
        st.success("No open issues. All clear!")
    else:
        for _, row in open_df.iterrows():
            issue_id  = int(row["id"])
            priority  = str(row["priority"])
            colour    = PRIORITY_COLOUR.get(priority, "#aaa")
            created   = str(row["created_at"])[:10]
            desc      = str(row.get("description") or "").strip()

            with st.container():
                st.markdown(
                    f'<div style="background:#1a1a2e;border-left:4px solid {colour};'
                    f'border-radius:8px;padding:0.75rem 1rem;margin-bottom:0.5rem">'
                    f'<span style="font-size:0.7rem;font-weight:700;color:{colour};'
                    f'text-transform:uppercase;letter-spacing:0.08em">{priority} priority</span>'
                    f'<div style="font-size:0.95rem;font-weight:700;color:#fff;margin:0.2rem 0">'
                    f'{row["title"]}</div>'
                    f'{"<div style=\'font-size:0.83rem;color:#ccc;margin-bottom:0.3rem\'>" + desc + "</div>" if desc else ""}'
                    f'<span style="font-size:0.75rem;color:#888">Raised by {row["raised_by"]} · {created}</span>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
                col_res, col_del, _ = st.columns([1, 1, 6])
                with col_res:
                    if st.button("✅ Resolve", key=f"res_{issue_id}"):
                        resolve_issue(issue_id)
                        st.rerun()
                with col_del:
                    if st.button("🗑️ Delete", key=f"del_{issue_id}"):
                        delete_issue(issue_id)
                        st.rerun()

    st.divider()

    # ── Resolved issues ───────────────────────────────────────────────────────
    if not resolved_df.empty:
        with st.expander(f"Resolved issues — {len(resolved_df)}", expanded=False):
            for _, row in resolved_df.iterrows():
                issue_id = int(row["id"])
                desc     = str(row.get("description") or "").strip()
                created  = str(row["created_at"])[:10]
                st.markdown(
                    f'<div style="background:#12121e;border-left:4px solid #00b894;'
                    f'border-radius:8px;padding:0.65rem 1rem;margin-bottom:0.4rem;opacity:0.75">'
                    f'<div style="font-size:0.9rem;font-weight:700;color:#ccc">{row["title"]}</div>'
                    f'{"<div style=\'font-size:0.8rem;color:#888\'>" + desc + "</div>" if desc else ""}'
                    f'<span style="font-size:0.72rem;color:#666">Raised by {row["raised_by"]} · {created} · ✅ Resolved</span>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
                if st.button("🗑️", key=f"del_res_{issue_id}", help="Delete"):
                    delete_issue(issue_id)
                    st.rerun()

    st.divider()

    # ── Raise new issue ───────────────────────────────────────────────────────
    st.markdown("**➕ Raise a new issue**")
    with st.form("new_issue_form", clear_on_submit=True):
        new_title = st.text_input("Title ✱", placeholder="e.g. Pipeline week selector not saving correctly")
        new_desc  = st.text_area("Description (optional)", placeholder="Steps to reproduce, what you expected, what happened…")
        c1, c2 = st.columns(2)
        with c1:
            new_raised_by = st.selectbox("Raised by", ["Sanjay", "Shailee"])
        with c2:
            new_priority = st.selectbox("Priority", ["High", "Medium", "Low"], index=1)
        submitted = st.form_submit_button("Submit issue", type="primary")

    if submitted:
        if new_title.strip():
            save_issue(new_title.strip(), new_desc.strip(), new_raised_by, new_priority)
            st.success("Issue raised.")
            st.rerun()
        else:
            st.warning("Title is required.")


def main():
    sidebar()
    history_df = load_history()
    kr_data    = load_kr_progress()

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "🎯  Mission",
        "📊  OKR Tracker",
        "🎬  Pipeline",
        "💡  Intelligence",
        "📚  Reference",
        "🔧  Issues",
    ])

    with tab1:
        tab_mission()
    with tab2:
        tab_performance(history_df, kr_data)
    with tab3:
        tab_pipeline()
    with tab4:
        tab_intelligence()
    with tab5:
        tab_reference()
    with tab6:
        tab_issues()


if __name__ == "__main__":
    main()
