"""
Log Analyzer — a simple support tool that parses application log files,
groups issues by pattern, and surfaces the most frequent problems.

Run locally:   streamlit run app.py
Deploy free:   push to GitHub, then deploy on https://share.streamlit.io
"""
import re
from datetime import datetime

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Log Analyzer", page_icon="assets/icon.png", layout="wide")

# ---------- Design tokens ----------
# Muted slate/steel palette — a technical, internal-tool feel rather than a
# bright "demo app" look. Kept flat (hairline borders, no drop shadows).
INK = "#1C2B33"
ACCENT = "#3E5B89"
BORDER = "#DADFE2"
MUTED = "#5B6B73"

# ---------- Small inline icon set (line-style SVGs, not emoji) ----------

def icon(name: str, size: int = 20, color: str = ACCENT) -> str:
    paths = {
        "logs": (
            f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
            f'stroke="{color}" stroke-width="1.6" stroke-linecap="round">'
            '<rect x="4" y="3" width="16" height="18" rx="2"/>'
            '<line x1="8" y1="9" x2="16" y2="9"/>'
            '<line x1="8" y1="13" x2="16" y2="13"/>'
            '<line x1="8" y1="17" x2="13" y2="17"/>'
            "</svg>"
        ),
        "alert": (
            f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
            f'stroke="{color}" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">'
            '<path d="M12 3 L22 20 L2 20 Z"/>'
            '<line x1="12" y1="9" x2="12" y2="14"/>'
            '<line x1="12" y1="16.5" x2="12" y2="16.6"/>'
            "</svg>"
        ),
        "grid": (
            f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
            f'stroke="{color}" stroke-width="1.6" stroke-linecap="round">'
            '<rect x="3" y="3" width="8" height="8" rx="1"/>'
            '<rect x="13" y="3" width="8" height="8" rx="1"/>'
            '<rect x="3" y="13" width="8" height="8" rx="1"/>'
            '<rect x="13" y="13" width="8" height="8" rx="1"/>'
            "</svg>"
        ),
    }
    return paths.get(name, "")


def section_header(icon_name: str, text: str, subtitle: str | None = None):
    st.markdown(
        f"""
        <div style="display:flex;align-items:center;gap:9px;margin:6px 0 2px 0;">
            {icon(icon_name, 19, ACCENT)}
            <span style="font-size:1.05rem;font-weight:600;color:{INK};">{text}</span>
        </div>
        {f'<div style="color:{MUTED};font-size:0.86rem;margin-bottom:8px;">{subtitle}</div>' if subtitle else '<div style="margin-bottom:6px;"></div>'}
        """,
        unsafe_allow_html=True,
    )


st.markdown(
    f"""
    <style>
        hr {{ border-color: {BORDER} !important; }}
        [data-testid="stMetricValue"] {{ color: {INK}; }}
        [data-testid="stMetricLabel"] {{ color: {MUTED}; }}
        .stDataFrame {{ border: 1px solid {BORDER}; border-radius: 4px; }}
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------- Parsing ----------

LOG_PATTERN = re.compile(
    r"^(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\s+"
    r"\[(?P<level>\w+)\]\s+"
    r"\((?P<component>[\w\-]+)\)\s+"
    r"region=(?P<region>[\w\-]+)\s+-\s+"
    r"(?P<message>.+)$"
)


def parse_log(text: str) -> pd.DataFrame:
    rows = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        match = LOG_PATTERN.match(line)
        if match:
            d = match.groupdict()
            try:
                d["timestamp"] = datetime.strptime(d["timestamp"], "%Y-%m-%d %H:%M:%S")
            except ValueError:
                d["timestamp"] = None
            rows.append(d)
        else:
            # Unparsed line — still capture it so nothing silently disappears
            rows.append(
                {
                    "timestamp": None,
                    "level": "UNKNOWN",
                    "component": "unknown",
                    "region": "unknown",
                    "message": line,
                }
            )
    return pd.DataFrame(rows)


def normalize_message(message: str) -> str:
    """Groups similar messages together by stripping obvious variable bits
    (numbers, ids) so 'Timeout after 30s' and 'Timeout after 45s' count as one pattern."""
    normalized = re.sub(r"\d+", "#", message)
    return normalized.strip()


# ---------- UI ----------

st.markdown(
    f"""
    <div style="display:flex;align-items:center;gap:11px;margin-bottom:2px;">
        {icon("logs", 26, ACCENT)}
        <span style="font-size:1.6rem;font-weight:650;color:{INK};letter-spacing:-0.01em;">Log Analyzer</span>
    </div>
    """,
    unsafe_allow_html=True,
)
st.caption(
    "Upload an application log file to see error patterns, frequency, and which "
    "regions and components are affected — a lightweight version of production log monitoring."
)

uploaded = st.file_uploader("Upload a log file (.txt or .log)", type=["txt", "log"])

use_sample = False
if not uploaded:
    use_sample = st.checkbox("No file? Use the bundled sample log instead", value=True)

log_text = None
if uploaded:
    log_text = uploaded.read().decode("utf-8", errors="ignore")
elif use_sample:
    try:
        with open("sample_log.txt", "r") as f:
            log_text = f.read()
    except FileNotFoundError:
        st.warning("sample_log.txt not found — upload a file instead.")

if log_text:
    df = parse_log(log_text)

    if df.empty:
        st.error("No log lines could be parsed from this file.")
    else:
        total = len(df)
        errors = df[df["level"].isin(["ERROR", "CRITICAL"])]
        warnings = df[df["level"] == "WARNING"]

        # --- Top metrics ---
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total log lines", total)
        c2.metric("Errors / Critical", len(errors))
        c3.metric("Warnings", len(warnings))
        c4.metric(
            "Error rate",
            f"{(len(errors) / total * 100):.1f}%" if total else "0%",
        )

        st.divider()

        left, right = st.columns([1, 1])

        with left:
            section_header("grid", "Level breakdown")
            level_counts = df["level"].value_counts()
            st.bar_chart(level_counts)

        with right:
            section_header("grid", "Issues by region")
            if not errors.empty:
                region_counts = errors["region"].value_counts()
                st.bar_chart(region_counts)
            else:
                st.info("No errors found — nothing to break down by region.")

        st.divider()

        # --- Top recurring issues (the "known issues" view) ---
        section_header(
            "alert",
            "Most frequent issues",
            "Similar messages (e.g. varying timeouts or IDs) are grouped together, "
            "mirroring how a support engineer would triage recurring known issues.",
        )

        if not errors.empty:
            errors = errors.copy()
            errors["pattern"] = errors["message"].apply(normalize_message)
            pattern_counts = (
                errors.groupby(["pattern", "component"])
                .size()
                .reset_index(name="count")
                .sort_values("count", ascending=False)
            )
            st.dataframe(
                pattern_counts.rename(
                    columns={"pattern": "Issue pattern", "component": "Component", "count": "Occurrences"}
                ),
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info("No errors or critical issues detected in this log.")

        st.divider()

        # --- Raw data / export ---
        with st.expander("View raw parsed log data"):
            st.dataframe(df, use_container_width=True, hide_index=True)

        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Download parsed data as CSV",
            data=csv,
            file_name="parsed_log_analysis.csv",
            mime="text/csv",
        )
else:
    st.info("Upload a log file or check the sample box above to get started.")
