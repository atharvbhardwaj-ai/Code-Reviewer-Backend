import os
import requests
import difflib
import streamlit as st

# -------------------------------------------------------------
# PAGE CONFIGURATION
# -------------------------------------------------------------
st.set_page_config(
    page_title="PRISM - AI Code Auditor",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded"
)

API_BASE_URL = os.getenv("BACKEND_API_URL", "http://127.0.0.1:8000")

LANGUAGES = [
    "Auto-detect",
    "Python",
    "C++",
    "C",
    "Java",
    "JavaScript",
    "TypeScript",
    "React JSX",
    "React TSX",
    "Go",
    "Rust",
    "C#",
    "PHP",
    "Ruby"
]

DEMO_PRESETS = {
    "Custom Input (Write or Paste Own Code)": "",
    "Demo 1: Python SQL Injection (Security Flaw)": (
        "import sqlite3\n\n"
        "def get_user_profile(request_data):\n"
        "    # Fetch user record from local database\n"
        "    connection = sqlite3.connect(\"users.db\")\n"
        "    cursor = connection.cursor()\n"
        "    account_id = request_data.get(\"id\")\n"
        "    query = f\"SELECT * FROM profiles WHERE id = '{account_id}'\"\n"
        "    cursor.execute(query)\n"
        "    return cursor.fetchall()"
    ),
    "Demo 2: Python O(N^2) Duplicate Search (Complexity Bottleneck)": (
        "def find_duplicates(items):\n"
        "    # Compare every pair to find duplicate elements\n"
        "    duplicates = []\n"
        "    for i in range(len(items)):\n"
        "        for j in range(i + 1, len(items)):\n"
        "            if items[i] == items[j] and items[i] not in duplicates:\n"
        "                duplicates.append(items[i])\n"
        "    return duplicates"
    ),
    "Demo 3: C++ Unreleased Heap Allocation (Memory Leak)": (
        "#include <iostream>\n\n"
        "int process_sensor_buffer(int size) {\n"
        "    // Allocate dynamic array on the heap\n"
        "    int* buffer = new int[size];\n"
        "    buffer[0] = 42;\n"
        "    if (size < 10) {\n"
        "        return -1; // Early exit leaks memory\n"
        "    }\n"
        "    return buffer[0];\n"
        "}"
    )
}

def render_code_diff(orig_code: str, refactored_code: str):
    """Generates line-by-line red and green diff highlighting with line numbers."""
    orig_lines = orig_code.splitlines()
    refactored_lines = refactored_code.splitlines()

    diff = list(difflib.ndiff(orig_lines, refactored_lines))

    orig_html = []
    refactored_html = []

    orig_line_num = 1
    refactored_line_num = 1

    for line in diff:
        if line.startswith("? "):
            continue

        code_content = line[2:]
        safe_content = (
            code_content.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            or "&nbsp;"
        )

        if line.startswith("- "):
            orig_html.append(
                f'<div class="diff-line diff-remove"><span class="line-num">{orig_line_num}</span><span class="line-content">- {safe_content}</span></div>'
            )
            orig_line_num += 1
        elif line.startswith("+ "):
            refactored_html.append(
                f'<div class="diff-line diff-add"><span class="line-num">{refactored_line_num}</span><span class="line-content">+ {safe_content}</span></div>'
            )
            refactored_line_num += 1
        elif line.startswith("  "):
            orig_html.append(
                f'<div class="diff-line diff-unchanged"><span class="line-num">{orig_line_num}</span><span class="line-content">&nbsp;&nbsp;{safe_content}</span></div>'
            )
            refactored_html.append(
                f'<div class="diff-line diff-unchanged"><span class="line-num">{refactored_line_num}</span><span class="line-content">&nbsp;&nbsp;{safe_content}</span></div>'
            )
            orig_line_num += 1
            refactored_line_num += 1

    return "".join(orig_html), "".join(refactored_html)

# -------------------------------------------------------------
# SIDEBAR CONTROLS
# -------------------------------------------------------------
with st.sidebar:
    st.markdown("## PRISM Controls")

    # Fetch Backend Engine Health
    engine_status_html = '<span class="status-pill status-offline">Backend Offline (Port 8000)</span>'
    try:
        health_resp = requests.get(f"{API_BASE_URL}/", timeout=2)
        if health_resp.status_code == 200:
            server_info = health_resp.json()
            model_name = server_info.get("engine_model", "Online")
            engine_status_html = f'<span class="status-pill status-online">Online ({model_name})</span>'
        else:
            engine_status_html = '<span class="status-pill status-degraded">Reachable (Degraded)</span>'
    except Exception:
        pass

    st.markdown(f"**Engine Status:** &nbsp; {engine_status_html}", unsafe_allow_html=True)
    st.markdown("---")

    ui_theme = st.radio(
        "UI Theme Mode",
        options=["Vibrant Light (Presentation)", "Cyber Dark"],
        index=0
    )
    is_light = ui_theme.startswith("Vibrant Light")

    st.markdown("---")

    selected_language = st.selectbox(
        "Target Language",
        options=LANGUAGES,
        index=0
    )

    user_comments = st.text_area(
        "Hardware / Context Constraints",
        placeholder="e.g. Optimize for memory consumption, O(N) linear time constraint.",
        height=100
    )

    st.markdown("---")
    st.caption("PRISM v1.0 • Built with Streamlit & FastAPI")

# -------------------------------------------------------------
# DYNAMIC THEME PALETTE DEFINITIONS
# -------------------------------------------------------------
if is_light:
    # Frosted Daylight Glass Palette (High Contrast for Projectors & Faculty)
    app_bg = """
        radial-gradient(circle at 10% 10%, rgba(255, 0, 122, 0.12) 0%, transparent 45%),
        radial-gradient(circle at 90% 15%, rgba(147, 51, 234, 0.14) 0%, transparent 45%),
        radial-gradient(circle at 50% 85%, rgba(0, 184, 217, 0.12) 0%, transparent 50%),
        linear-gradient(180deg, #F8FAFC 0%, #EEF2F6 100%)
    """
    sidebar_bg = "linear-gradient(180deg, #FFFFFF 0%, #F1F5F9 100%)"
    sidebar_border = "rgba(147, 51, 234, 0.16)"
    hr_color = "rgba(148, 163, 184, 0.35)"
    text_primary = "#0F172A"
    text_secondary = "#475569"
    placeholder_color = "#64748B"
    card_bg = "rgba(255, 255, 255, 0.88)"
    card_border = "rgba(147, 51, 234, 0.22)"
    card_shadow = "0 10px 28px -4px rgba(147, 51, 234, 0.08), 0 4px 12px rgba(15, 23, 42, 0.04)"
    health_bg = "radial-gradient(circle at center, rgba(168, 85, 247, 0.12) 0%, rgba(255, 255, 255, 0.98) 100%)"
    input_bg = "#FFFFFF"
    input_border = "rgba(147, 51, 234, 0.32)"
    input_focus_border = "#9333EA"
    diff_bg = "#FFFFFF"
    diff_border = "#CBD5E1"
    diff_unchanged_text = "#334155"
    diff_remove_bg = "#FFE4E6"
    diff_remove_text = "#9F1239"
    diff_add_bg = "#DCFCE7"
    diff_add_text = "#166534"
    line_badge_bg = "rgba(147, 51, 234, 0.10)"
    line_badge_text = "#6B21A8"
    status_online_bg = "rgba(34, 197, 94, 0.12)"
    status_online_text = "#15803D"
    status_online_border = "rgba(34, 197, 94, 0.35)"
    comp_bad = "#DC2626"
    comp_good = "#16A34A"
    delta_color = "#7C3AED"
else:
    # Cyber Dark Palette
    app_bg = """
        radial-gradient(circle at 15% 15%, rgba(126, 87, 194, 0.22) 0%, transparent 45%),
        radial-gradient(circle at 85% 20%, rgba(255, 0, 122, 0.18) 0%, transparent 40%),
        radial-gradient(circle at 50% 80%, rgba(0, 229, 255, 0.15) 0%, transparent 50%),
        #0b0d14
    """
    sidebar_bg = "#131622"
    sidebar_border = "rgba(255, 255, 255, 0.08)"
    hr_color = "rgba(255, 255, 255, 0.12)"
    text_primary = "#F8FAFC"
    text_secondary = "#94A3B8"
    placeholder_color = "#64748B"
    card_bg = "rgba(255, 255, 255, 0.03)"
    card_border = "rgba(255, 255, 255, 0.08)"
    card_shadow = "0 8px 32px 0 rgba(0, 0, 0, 0.37)"
    health_bg = "radial-gradient(circle at center, rgba(168, 85, 247, 0.15) 0%, rgba(255, 255, 255, 0.02) 100%)"
    input_bg = "#161B26"
    input_border = "rgba(255, 255, 255, 0.15)"
    input_focus_border = "#A855F7"
    diff_bg = "#0d1117"
    diff_border = "rgba(255, 255, 255, 0.12)"
    diff_unchanged_text = "#8B949E"
    diff_remove_bg = "rgba(255, 69, 58, 0.22)"
    diff_remove_text = "#FF6B6B"
    diff_add_bg = "rgba(48, 209, 88, 0.22)"
    diff_add_text = "#4EFE85"
    line_badge_bg = "rgba(168, 85, 247, 0.2)"
    line_badge_text = "#D8B4FE"
    status_online_bg = "rgba(48, 209, 88, 0.15)"
    status_online_text = "#4EFE85"
    status_online_border = "rgba(48, 209, 88, 0.35)"
    comp_bad = "#FF6B6B"
    comp_good = "#4EFE85"
    delta_color = "#00E5FF"

# Inject Scoped CSS
st.markdown(f"""
<style>
    /* 1. Header & Top Spacing */
    header[data-testid="stHeader"] {{
        display: none !important;
    }}
    .block-container {{
        padding-top: 1.5rem !important;
    }}

    /* 2. Sidebar Alignment & Boundaries */
    div[data-testid="stSidebarHeader"] {{
        height: 0px !important;
        min-height: 0px !important;
        padding: 0px !important;
        overflow: hidden !important;
    }}
    section[data-testid="stSidebar"] {{
        background: {sidebar_bg} !important;
        border-right: 1px solid {sidebar_border} !important;
    }}
    section[data-testid="stSidebar"] > div:first-child,
    div[data-testid="stSidebarUserContent"] {{
        padding-top: 1.2rem !important;
    }}
    section[data-testid="stSidebar"] h2 {{
        margin-top: 0px !important;
        padding-top: 0px !important;
        color: {text_primary} !important;
    }}
    hr {{
        border: none !important;
        border-top: 1px solid {hr_color} !important;
        margin: 1.1rem 0 !important;
    }}

    /* 3. Engine Status Pill Badge */
    .status-pill {{
        display: inline-block;
        padding: 3px 10px;
        border-radius: 12px;
        font-size: 0.82rem;
        font-family: 'Fira Code', monospace;
        font-weight: 700;
        vertical-align: middle;
    }}
    .status-online {{
        background-color: {status_online_bg};
        color: {status_online_text};
        border: 1px solid {status_online_border};
    }}
    .status-degraded {{
        background-color: rgba(234, 179, 8, 0.15);
        color: #CA8A04;
        border: 1px solid rgba(234, 179, 8, 0.35);
    }}
    .status-offline {{
        background-color: rgba(239, 68, 68, 0.15);
        color: #DC2626;
        border: 1px solid rgba(239, 68, 68, 0.35);
    }}

    /* 4. Canvas & Typography Contrast */
    .stApp {{
        background: {app_bg} !important;
        background-attachment: fixed !important;
        color: {text_primary} !important;
    }}
    h1, h2, h3, h4, h5, h6, p, label, .stMarkdown, span {{
        color: {text_primary};
    }}
    div[data-testid="stCaptionContainer"] p {{
        color: {text_secondary} !important;
    }}

    /* 5. Input Boxes, BaseWeb Selects & Visible Placeholder Styling */
    div[data-baseweb="textarea"],
    div[data-baseweb="input"],
    div[data-baseweb="base-input"],
    div[data-baseweb="select"] > div {{
        background-color: {input_bg} !important;
        border: 1px solid {input_border} !important;
        border-radius: 10px !important;
        box-shadow: none !important;
        outline: none !important;
    }}
    div[data-baseweb="textarea"]:focus-within,
    div[data-baseweb="input"]:focus-within,
    div[data-baseweb="select"] > div:focus-within {{
        border: 1.5px solid {input_focus_border} !important;
    }}
    textarea, input {{
        color: {text_primary} !important;
        background-color: transparent !important;
    }}
    ::placeholder,
    ::-webkit-input-placeholder,
    ::-moz-placeholder,
    :-ms-input-placeholder {{
        color: {placeholder_color} !important;
        opacity: 0.95 !important;
        font-weight: 400 !important;
    }}

    /* 6. Header Title Glow */
    .prism-title {{
        font-size: 3.4rem;
        font-weight: 900;
        letter-spacing: 3px;
        background: linear-gradient(135deg, #FF007A 0%, #9333EA 50%, #00B8D9 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        width: fit-content;
        margin: 0 auto 4px auto;
        text-align: center;
        filter: drop-shadow(0px 4px 18px rgba(147, 51, 234, 0.28));
    }}
    .prism-tagline {{
        font-size: 1.05rem;
        color: {text_secondary};
        font-weight: 500;
        margin-bottom: 25px;
        text-align: center;
    }}

    /* 7. Frosted Glass Metric Cards */
    .glass-metric {{
        background: {card_bg};
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid {card_border};
        border-radius: 16px;
        padding: 18px;
        text-align: center;
        box-shadow: {card_shadow};
    }}
    .metric-label {{
        font-size: 0.78rem;
        color: {text_secondary};
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1.2px;
        margin-bottom: 6px;
    }}
    .metric-value {{
        font-size: 1.35rem;
        font-weight: 800;
        color: {text_primary};
    }}

    /* 8. Health Gauge Box */
    .health-glass {{
        background: {health_bg};
        backdrop-filter: blur(16px);
        border: 2px solid rgba(147, 51, 234, 0.35);
        border-radius: 16px;
        padding: 20px;
        text-align: center;
        box-shadow: {card_shadow};
    }}

    /* 9. Findings Box */
    .finding-glass {{
        background: {card_bg};
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid {card_border};
        border-radius: 14px;
        padding: 20px;
        margin-bottom: 16px;
        box-shadow: {card_shadow};
        border-left: 6px solid #9333EA;
    }}
    .finding-HIGH {{ border-left-color: #EF4444 !important; }}
    .finding-MEDIUM {{ border-left-color: #F59E0B !important; }}
    .finding-LOW {{ border-left-color: #10B981 !important; }}

    .line-badge {{
        background: {line_badge_bg};
        color: {line_badge_text};
        border: 1px solid rgba(147, 51, 234, 0.35);
        padding: 4px 10px;
        border-radius: 6px;
        font-family: 'Fira Code', monospace;
        font-weight: 700;
        font-size: 0.82rem;
        margin-left: 8px;
    }}
    .badge-HIGH {{
        background: rgba(239, 68, 68, 0.15);
        color: #DC2626;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: 800;
        font-size: 0.8rem;
        border: 1px solid rgba(239, 68, 68, 0.35);
    }}
    .badge-MEDIUM {{
        background: rgba(245, 158, 11, 0.15);
        color: #D97706;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: 800;
        font-size: 0.8rem;
        border: 1px solid rgba(245, 158, 11, 0.35);
    }}
    .badge-LOW {{
        background: rgba(16, 185, 129, 0.15);
        color: #059669;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: 800;
        font-size: 0.8rem;
        border: 1px solid rgba(16, 185, 129, 0.35);
    }}

    /* 10. Code Diff Container */
    .diff-container {{
        font-family: 'Fira Code', 'Courier New', Courier, monospace;
        font-size: 0.88rem;
        background: {diff_bg};
        border: 1px solid {diff_border};
        border-radius: 12px;
        padding: 14px;
        height: 460px;
        overflow-y: auto;
        white-space: pre-wrap;
        word-wrap: break-word;
        line-height: 1.55;
        box-shadow: {card_shadow};
    }}
    .diff-line {{
        padding: 2px 6px;
        border-radius: 4px;
        display: flex;
        align-items: flex-start;
    }}
    .line-num {{
        display: inline-block;
        width: 38px;
        min-width: 38px;
        color: {text_secondary};
        user-select: none;
        text-align: right;
        padding-right: 12px;
        font-size: 0.8rem;
    }}
    .line-content {{
        flex-grow: 1;
    }}
    .diff-remove {{
        background-color: {diff_remove_bg} !important;
        color: {diff_remove_text} !important;
        border-left: 3px solid #EF4444;
        font-weight: 600;
    }}
    .diff-add {{
        background-color: {diff_add_bg} !important;
        color: {diff_add_text} !important;
        border-left: 3px solid #10B981;
        font-weight: 600;
    }}
    .diff-unchanged {{
        color: {diff_unchanged_text};
    }}

    /* 11. Primary Refract Action Button */
    div.stButton > button[kind="primary"] {{
        background: linear-gradient(135deg, #FF007A 0%, #9333EA 55%, #00B8D9 100%) !important;
        border: none !important;
        border-radius: 10px !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        font-size: 1.05rem !important;
        padding: 12px 24px !important;
        box-shadow: 0 6px 20px rgba(147, 51, 234, 0.35) !important;
        transition: all 0.25s ease !important;
    }}
    div.stButton > button[kind="primary"]:hover {{
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 28px rgba(255, 0, 122, 0.45) !important;
    }}
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------
# MAIN HEADER & INPUT WORKSPACE
# -------------------------------------------------------------
st.markdown('<div class="prism-title">PRISM</div>', unsafe_allow_html=True)
st.markdown('<div class="prism-tagline">Refracting your codebase into distinct security, quality, and algorithmic performance beams.</div>', unsafe_allow_html=True)

col_mode, col_preset = st.columns([1.2, 1.8])

with col_mode:
    input_choice = st.radio(
        "Choose Input Method:",
        options=["Paste Code Snippet", "Upload Source File"],
        horizontal=True
    )

with col_preset:
    if input_choice == "Paste Code Snippet":
        selected_preset = st.selectbox(
            "Quick-Load Demo Sample (Optional):",
            options=list(DEMO_PRESETS.keys()),
            index=0
        )
    else:
        selected_preset = "Custom Input (Write or Paste Own Code)"

raw_code = ""
uploaded_file = None
input_mode = None

if input_choice == "Paste Code Snippet":
    default_code = DEMO_PRESETS[selected_preset]
    raw_code = st.text_area(
        "Paste Source Code:",
        value=default_code,
        height=250,
        placeholder="// Paste Python, C++, Java, JS, Go, or Rust code here..."
    )
    if raw_code.strip():
        input_mode = "text"
else:
    uploaded_file = st.file_uploader(
        "Upload Source File:",
        type=["py", "cpp", "cc", "cxx", "c", "h", "hpp", "java", "js", "ts", "jsx", "tsx", "go", "rs", "cs", "php", "rb"]
    )
    if uploaded_file is not None:
        input_mode = "file"
        try:
            raw_code = uploaded_file.getvalue().decode("utf-8")
        except Exception:
            raw_code = uploaded_file.getvalue().decode("latin-1")
        st.info(f"Selected File: **{uploaded_file.name}** ({len(raw_code.splitlines())} lines)")

st.markdown("<br>", unsafe_allow_html=True)
trigger_audit = st.button("Refract & Audit Codebase", use_container_width=True, type="primary")

# -------------------------------------------------------------
# AUDIT PROCESSING & DASHBOARD DISPLAY
# -------------------------------------------------------------
if trigger_audit:
    if not input_mode or not raw_code.strip():
        st.error("Please paste code in the text box or upload a source file first.")
    else:
        report_data = None
        with st.spinner("Refracting codebase through PRISM AI Engine..."):
            try:
                if input_mode == "text":
                    payload = {
                        "code": raw_code,
                        "language": selected_language,
                        "user_comments": user_comments
                    }
                    response = requests.post(f"{API_BASE_URL}/api/v1/audit", json=payload, timeout=45)
                elif input_mode == "file":
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type or "application/octet-stream")}
                    data = {"language": selected_language, "user_comments": user_comments}
                    response = requests.post(f"{API_BASE_URL}/api/v1/audit-file", files=files, data=data, timeout=45)

                if response.status_code == 200:
                    report_data = response.json()
                else:
                    st.error(f"Backend API Error ({response.status_code}): {response.text}")

            except Exception as e:
                st.error(f"Failed to connect to FastAPI backend: {str(e)}")

        if report_data:
            if not report_data.get("is_valid_code", False):
                st.error(f"Code Rejected: {report_data.get('rejection_reason', 'Provided input is not valid code.')}")
            else:
                st.markdown("---")

                health_score = report_data.get("health_score", 0)
                lang_detected = report_data.get("language_detected") or "Code"
                passed_checks = report_data.get("passed_checks", 0)

                safe_lang = lang_detected.lower() if lang_detected not in [None, "Auto-detect", "Code"] else "python"

                orig_time_complexity = report_data.get("time_complexity_current") or "N/A"
                refactored_time_complexity = report_data.get("time_complexity_optimized") or "N/A"

                orig_space_complexity = report_data.get("space_complexity_current") or "N/A"
                refactored_space_complexity = report_data.get("space_complexity_optimized") or "N/A"

                col_metrics, col_summary = st.columns([1.2, 2])

                with col_metrics:
                    score_color = "#16A34A" if health_score >= 80 else ("#D97706" if health_score >= 50 else "#DC2626")
                    st.markdown(f"""
                    <div class="health-glass">
                        <div style="font-size: 0.85rem; color: {text_secondary}; font-weight: 700; text-transform: uppercase; letter-spacing: 1.2px;">Overall Code Health</div>
                        <div style="font-size: 3.2rem; font-weight: 900; color: {score_color};">{health_score} <span style="font-size:1.2rem; color:{text_secondary};">/ 100</span></div>
                    </div>
                    """, unsafe_allow_html=True)
                    st.progress(health_score / 100)

                with col_summary:
                    st.markdown("### Executive Summary")
                    st.info(report_data.get("summary", "Code audit completed successfully."))

                st.markdown("<br>", unsafe_allow_html=True)

                s1, s2, s3, s4 = st.columns(4)

                if orig_time_complexity == refactored_time_complexity and orig_time_complexity != "N/A":
                    time_display = f'<span style="color:{comp_good};">{orig_time_complexity} (Optimal)</span>'
                else:
                    time_display = f'<span style="color:{comp_bad};">{orig_time_complexity}</span> ➔ <span style="color:{comp_good};">{refactored_time_complexity}</span>'

                if orig_space_complexity == refactored_space_complexity and orig_space_complexity != "N/A":
                    space_display = f'<span style="color:{comp_good};">{orig_space_complexity} (Optimal)</span>'
                else:
                    space_display = f'<span style="color:{comp_bad};">{orig_space_complexity}</span> ➔ <span style="color:{comp_good};">{refactored_space_complexity}</span>'

                with s1:
                    st.markdown(f"""
                    <div class="glass-metric">
                        <div class="metric-label">Language / Checks</div>
                        <div class="metric-value">{lang_detected} ({passed_checks} Passed)</div>
                    </div>
                    """, unsafe_allow_html=True)
                with s2:
                    st.markdown(f"""
                    <div class="glass-metric">
                        <div class="metric-label">Time Complexity</div>
                        <div class="metric-value">{time_display}</div>
                    </div>
                    """, unsafe_allow_html=True)
                with s3:
                    st.markdown(f"""
                    <div class="glass-metric">
                        <div class="metric-label">Space Complexity</div>
                        <div class="metric-value">{space_display}</div>
                    </div>
                    """, unsafe_allow_html=True)
                with s4:
                    st.markdown(f"""
                    <div class="glass-metric">
                        <div class="metric-label">Efficiency Delta</div>
                        <div class="metric-value" style="color: {delta_color};">Analyzed</div>
                    </div>
                    """, unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)

                st.markdown("### Side-by-Side Code Refactoring & Diff")

                refactored_code = report_data.get("refactored_code") or raw_code

                col_orig, col_refactored = st.columns(2)
                orig_diff_html, refactored_diff_html = render_code_diff(raw_code, refactored_code)

                with col_orig:
                    st.markdown("#### 🔴 Original Code (Removed / Modified)")
                    st.markdown(f'<div class="diff-container">{orig_diff_html}</div>', unsafe_allow_html=True)

                with col_refactored:
                    st.markdown("#### 🟢 PRISM Refactored Code (Optimized Patch)")
                    st.markdown(f'<div class="diff-container">{refactored_diff_html}</div>', unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)
                with st.expander("Download Refactored Code", expanded=False):
                    st.code(refactored_code, language=safe_lang)
                    st.download_button(
                        label="Download Refactored Code",
                        data=refactored_code,
                        file_name=f"prism_refactored.{safe_lang if safe_lang != 'python' else 'py'}",
                        mime="text/plain",
                        use_container_width=True
                    )

                st.markdown("<br>", unsafe_allow_html=True)

                st.markdown("### Audited Findings & Recommendations")
                findings = report_data.get("findings", [])

                if not findings:
                    st.balloons()
                    st.success("No vulnerabilities or anti-patterns detected! Code is production ready.")
                else:
                    high_count = sum(1 for f in findings if str(f.get("severity", "")).upper() == "HIGH")
                    med_count = sum(1 for f in findings if str(f.get("severity", "")).upper() == "MEDIUM")
                    low_count = sum(1 for f in findings if str(f.get("severity", "")).upper() == "LOW")

                    st.markdown(
                        f"**Detected Issues Breakdown:** &nbsp; "
                        f"<span class='badge-HIGH'>HIGH: {high_count} (-{high_count * 15} pts)</span> &nbsp; "
                        f"<span class='badge-MEDIUM'>MEDIUM: {med_count} (-{med_count * 5} pts)</span> &nbsp; "
                        f"<span class='badge-LOW'>LOW: {low_count} (-{low_count * 2} pts)</span>",
                        unsafe_allow_html=True
                    )
                    st.markdown("<br>", unsafe_allow_html=True)

                    for i, item in enumerate(findings, 1):
                        severity = str(item.get("severity", "LOW")).upper()
                        category = item.get("category", "Code Quality")
                        title = item.get("title", "Issue Found")
                        raw_line = item.get("line_number")
                        line_str = f"Line {raw_line}" if raw_line is not None else "Global Scope"
                        description = item.get("description", "")
                        fix = item.get("suggested_fix", "")

                        badge_class = f"badge-{severity}" if severity in ["HIGH", "MEDIUM", "LOW"] else "badge-LOW"

                        st.markdown(f"""
                        <div class="finding-glass finding-{severity}">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <span style="font-size: 1.15rem; font-weight: 800; color: {text_primary};">#{i}. {title}</span>
                                <div>
                                    <span class="{badge_class}">{severity}</span>
                                    <span class="line-badge">📍 {line_str}</span>
                                    <span style="color: {text_secondary}; font-size: 0.85rem; font-weight: 600; margin-left: 10px;">Category: {category}</span>
                                </div>
                            </div>
                            <p style="color: {text_secondary}; margin-top: 12px; font-size: 0.96rem; line-height: 1.55;">{description}</p>
                        </div>
                        """, unsafe_allow_html=True)

                        if fix:
                            with st.expander(f"View Suggested Fix for #{i} ({line_str})", expanded=False):
                                st.code(fix, language=safe_lang)