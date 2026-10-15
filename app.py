import os
import requests
import difflib
import streamlit as st

# -------------------------------------------------------------
# PAGE CONFIGURATION & GLASSMORPHISM THEMING
# -------------------------------------------------------------
st.set_page_config(
    page_title="PRISM - AI Code Auditor",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Glassmorphism, Code Diff, and Enunciated Line Numbers
st.markdown("""
<style>
    /* Mesh Gradient Background */
    .stApp {
        background: radial-gradient(circle at 15% 15%, rgba(126, 87, 194, 0.22) 0%, transparent 45%),
                    radial-gradient(circle at 85% 20%, rgba(255, 0, 122, 0.18) 0%, transparent 40%),
                    radial-gradient(circle at 50% 80%, rgba(0, 229, 255, 0.15) 0%, transparent 50%),
                    #0b0d14;
        background-attachment: fixed;
        color: #f1f5f9;
    }

    /* Header Title Glow */
    .prism-title {
        font-size: 3.2rem;
        font-weight: 900;
        letter-spacing: 2px;
        background: linear-gradient(135deg, #FF007A 0%, #A855F7 50%, #00E5FF 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px;
        filter: drop-shadow(0px 0px 25px rgba(168, 85, 247, 0.4));
    }
    
    .prism-tagline {
        font-size: 1.05rem;
        color: #94A3B8;
        font-weight: 400;
        margin-bottom: 25px;
    }

    /* Glass Metric Card */
    .glass-metric {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 18px;
        text-align: center;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
    }

    .metric-label {
        font-size: 0.8rem;
        color: #94A3B8;
        text-transform: uppercase;
        letter-spacing: 1.2px;
        margin-bottom: 6px;
    }

    .metric-value {
        font-size: 1.35rem;
        font-weight: 700;
        color: #F8FAFC;
    }

    /* Health Gauge Box */
    .health-glass {
        background: radial-gradient(circle at center, rgba(168, 85, 247, 0.15) 0%, rgba(255, 255, 255, 0.02) 100%);
        backdrop-filter: blur(16px);
        border: 1px solid rgba(168, 85, 247, 0.3);
        border-radius: 16px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 0 25px rgba(168, 85, 247, 0.15);
    }

    /* Glass Findings Box */
    .finding-glass {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        padding: 20px;
        margin-bottom: 16px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.25);
        border-left: 5px solid #A855F7;
    }
    .finding-HIGH { border-left-color: #FF453A !important; }
    .finding-MEDIUM { border-left-color: #FF9F0A !important; }
    .finding-LOW { border-left-color: #30D158 !important; }

    /* Enunciated Line Number Badge */
    .line-badge {
        background: rgba(168, 85, 247, 0.2);
        color: #D8B4FE;
        border: 1px solid rgba(168, 85, 247, 0.4);
        padding: 4px 10px;
        border-radius: 6px;
        font-family: 'Fira Code', monospace;
        font-weight: 700;
        font-size: 0.82rem;
        margin-left: 8px;
    }

    /* Severity Badges */
    .badge-HIGH {
        background: rgba(255, 69, 58, 0.15);
        color: #FF453A;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.8rem;
        border: 1px solid rgba(255, 69, 58, 0.3);
    }
    .badge-MEDIUM {
        background: rgba(255, 159, 10, 0.15);
        color: #FF9F0A;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.8rem;
        border: 1px solid rgba(255, 159, 10, 0.3);
    }
    .badge-LOW {
        background: rgba(48, 209, 88, 0.15);
        color: #30D158;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.8rem;
        border: 1px solid rgba(48, 209, 88, 0.3);
    }

    /* Custom Code Diff Styling with Line Numbers */
    .diff-container {
        font-family: 'Fira Code', 'Courier New', Courier, monospace;
        font-size: 0.88rem;
        background: #0d1117;
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 10px;
        padding: 14px;
        height: 480px;
        overflow-y: auto;
        white-space: pre-wrap;
        word-wrap: break-word;
        line-height: 1.5;
    }
    .diff-line {
        padding: 2px 6px;
        border-radius: 3px;
        display: flex;
        align-items: flex-start;
    }
    .line-num {
        display: inline-block;
        width: 38px;
        min-width: 38px;
        color: #484f58;
        user-select: none;
        text-align: right;
        padding-right: 12px;
        font-size: 0.8rem;
    }
    .line-content {
        flex-grow: 1;
    }
    .diff-remove {
        background-color: rgba(255, 69, 58, 0.22) !important;
        color: #FF6B6B !important;
        border-left: 3px solid #FF453A;
    }
    .diff-add {
        background-color: rgba(48, 209, 88, 0.22) !important;
        color: #4EFE85 !important;
        border-left: 3px solid #30D158;
    }
    .diff-unchanged {
        color: #8B949E;
    }

    /* Glowing Primary Button */
    div.stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #FF007A 0%, #A855F7 100%) !important;
        border: none !important;
        border-radius: 10px !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        font-size: 1.05rem !important;
        padding: 12px 24px !important;
        box-shadow: 0 4px 20px rgba(255, 0, 122, 0.35) !important;
        transition: all 0.3s ease !important;
    }
    div.stButton > button[kind="primary"]:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 28px rgba(168, 85, 247, 0.5) !important;
    }
</style>
""", unsafe_allow_html=True)

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

def render_code_diff(orig_code: str, refactored_code: str):
    """Generates line-by-line red and green diff highlighting with line numbers for side-by-side review."""
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
        safe_content = code_content.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;") or "&nbsp;"
        
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
# SIDEBAR
# -------------------------------------------------------------
with st.sidebar:
    st.markdown("## PRISM Controls")
    
    # Server Connection Check
    try:
        health_resp = requests.get(f"{API_BASE_URL}/", timeout=2)
        if health_resp.status_code == 200:
            server_info = health_resp.json()
            model_name = server_info.get('engine_model', 'Online')
            st.markdown(f"🟢 **Engine Status:** `Online ({model_name})`")
        else:
            st.markdown("🟡 **Engine Status:** `Reachable (Degraded)`")
    except Exception:
        st.markdown("🔴 **Engine Status:** `Backend Offline` (Port 8000)")

    st.markdown("---")
    
    selected_language = st.selectbox(
        "🎯 Target Language",
        options=LANGUAGES,
        index=0
    )
    
    user_comments = st.text_area(
        "⚙️ Hardware / Context Constraints",
        placeholder="e.g. Optimize for memory consumption, O(N) linear time constraint.",
        height=100
    )
    
    st.markdown("---")
    st.caption("PRISM v1.0 • Built with Streamlit & FastAPI")

# -------------------------------------------------------------
# MAIN HEADER
# -------------------------------------------------------------
st.markdown('<div class="prism-title">PRISM</div>', unsafe_allow_html=True)
st.markdown('<div class="prism-tagline">Refracting your codebase into distinct security, quality, and algorithmic performance beams.</div>', unsafe_allow_html=True)

# -------------------------------------------------------------
# INPUT SECTION (STATE-ISOLATED SELECTOR)
# -------------------------------------------------------------
input_choice = st.radio(
    "Choose Input Method:",
    options=["📝 Paste Code Snippet", "📁 Upload Source File"],
    horizontal=True
)

raw_code = ""
uploaded_file = None
input_mode = None

if input_choice == "📝 Paste Code Snippet":
    raw_code = st.text_area(
        "Paste Source Code:",
        height=260,
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
        st.info(f"📁 Selected File: **{uploaded_file.name}** ({len(raw_code.splitlines())} lines)")

st.markdown("<br>", unsafe_allow_html=True)
trigger_audit = st.button("🚀 Refract & Audit Codebase", use_container_width=True, type="primary")

# -------------------------------------------------------------
# AUDIT PROCESSING & DISPLAY
# -------------------------------------------------------------
if trigger_audit:
    if not input_mode or not raw_code.strip():
        st.error("Please paste code in the text box or upload a source file first.")
    else:
        report_data = None
        with st.spinner("✨ Refracting codebase through PRISM AI Engine..."):
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

        # -------------------------------------------------------------
        # REPORT DASHBOARD
        # -------------------------------------------------------------
        if report_data:
            if not report_data.get("is_valid_code", False):
                st.error(f"⚠️ Code Rejected: {report_data.get('rejection_reason', 'Provided input is not valid code.')}")
            else:
                st.markdown("---")
                
                # Top Score & Executive Banner
                health_score = report_data.get("health_score", 0)
                lang_detected = report_data.get("language_detected") or "Code"
                passed_checks = report_data.get("passed_checks", 0)
                
                # Safe language token for syntax highlighters
                safe_lang = lang_detected.lower() if lang_detected not in [None, "Auto-detect", "Code"] else "python"
                
                # Complexity info
                orig_time_complexity = report_data.get("time_complexity_current") or "N/A"
                refactored_time_complexity = report_data.get("time_complexity_optimized") or "N/A"
                
                orig_space_complexity = report_data.get("space_complexity_current") or "N/A"
                refactored_space_complexity = report_data.get("space_complexity_optimized") or "N/A"

                col_metrics, col_summary = st.columns([1.2, 2])

                with col_metrics:
                    score_color = "#30D158" if health_score >= 80 else ("#FF9F0A" if health_score >= 50 else "#FF453A")
                    st.markdown(f"""
                    <div class="health-glass">
                        <div style="font-size: 0.85rem; color: #94A3B8; text-transform: uppercase; letter-spacing: 1.2px;">Overall Code Health</div>
                        <div style="font-size: 3.2rem; font-weight: 800; color: {score_color};">{health_score} <span style="font-size:1.2rem; color:#64748B;">/ 100</span></div>
                    </div>
                    """, unsafe_allow_html=True)
                    st.progress(health_score / 100)

                with col_summary:
                    st.markdown("### 💡 Executive Summary")
                    st.info(report_data.get("summary", "Code audit completed successfully."))

                st.markdown("<br>", unsafe_allow_html=True)

                # Secondary Quick Stats Grid (Time & Space Complexity)
                s1, s2, s3, s4 = st.columns(4)
                
                # Format time complexity display
                if orig_time_complexity == refactored_time_complexity and orig_time_complexity != "N/A":
                    time_display = f'<span style="color:#4EFE85;">{orig_time_complexity} (Optimal)</span>'
                else:
                    time_display = f'<span style="color:#FF6B6B;">{orig_time_complexity}</span> ➔ <span style="color:#4EFE85;">{refactored_time_complexity}</span>'

                # Format space complexity display
                if orig_space_complexity == refactored_space_complexity and orig_space_complexity != "N/A":
                    space_display = f'<span style="color:#4EFE85;">{orig_space_complexity} (Optimal)</span>'
                else:
                    space_display = f'<span style="color:#FF6B6B;">{orig_space_complexity}</span> ➔ <span style="color:#4EFE85;">{refactored_space_complexity}</span>'

                with s1:
                    st.markdown(f"""
                    <div class="glass-metric">
                        <div class="metric-label">Language / Checks</div>
                        <div class="metric-value">🔤 {lang_detected} ({passed_checks} Passed)</div>
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
                        <div class="metric-value" style="color: #00E5FF;">⚡ Analyzed</div>
                    </div>
                    """, unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)

                # -------------------------------------------------------------
                # SIDE-BY-SIDE CODE COMPARISON (ORIGINAL VS REFACTORED)
                # -------------------------------------------------------------
                st.markdown("### 🔀 Side-by-Side Code Refactoring & Diff")
                
                refactored_code = report_data.get("refactored_code") or raw_code

                col_orig, col_refactored = st.columns(2)
                orig_diff_html, refactored_diff_html = render_code_diff(raw_code, refactored_code)

                with col_orig:
                    st.markdown("#### 🔴 Original Code (Removed / Modified)")
                    st.markdown(f'<div class="diff-container">{orig_diff_html}</div>', unsafe_allow_html=True)

                with col_refactored:
                    st.markdown("#### 🟢 PRISM Refactored Code (Optimized Patch)")
                    st.markdown(f'<div class="diff-container">{refactored_diff_html}</div>', unsafe_allow_html=True)

                # -------------------------------------------------------------
                # CLEAN COPY & DOWNLOAD TAB
                # -------------------------------------------------------------
                st.markdown("<br>", unsafe_allow_html=True)
                with st.expander("📋 Copy / Inspect Pure Refactored Code", expanded=False):
                    st.code(refactored_code, language=safe_lang)
                    st.download_button(
                        label="📥 Download Refactored Code",
                        data=refactored_code,
                        file_name=f"prism_refactored.{safe_lang if safe_lang != 'python' else 'py'}",
                        mime="text/plain",
                        use_container_width=True
                    )

                st.markdown("<br>", unsafe_allow_html=True)

                # -------------------------------------------------------------
                # DETAILED FINDINGS SECTION
                # -------------------------------------------------------------
                st.markdown("### 🔍 Audited Findings & Recommendations")
                findings = report_data.get("findings", [])

                if not findings:
                    st.balloons()
                    st.success("🎉 No vulnerabilities or anti-patterns detected! Code is production ready.")
                else:
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
                                <span style="font-size: 1.15rem; font-weight: 700; color: #F8FAFC;">#{i}. {title}</span>
                                <div>
                                    <span class="{badge_class}">{severity}</span>
                                    <span class="line-badge">📍 {line_str}</span>
                                    <span style="color: #94A3B8; font-size: 0.85rem; margin-left: 10px;">Category: {category}</span>
                                </div>
                            </div>
                            <p style="color: #CBD5E1; margin-top: 12px; font-size: 0.95rem; line-height: 1.5;">{description}</p>
                        </div>
                        """, unsafe_allow_html=True)

                        if fix:
                            with st.expander(f"🛠️ View Suggested Fix for #{i} ({line_str})", expanded=False):
                                st.code(fix, language=safe_lang)