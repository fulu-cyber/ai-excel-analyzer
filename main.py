import streamlit as st
import pandas as pd
import tempfile
import os
import json
from pathlib import Path
from typing import Optional, Dict, Any

from core import (
    ExcelLoader,
    DataProfiler,
    DataProfile,
    AIAnalyzer,
    AIAnalyzerError,
    NetworkError,
    RateLimitError,
    APIError,
    ReportGenerator,
    ReportGeneratorError,
)
from config import Config
from i18n import t


st.set_page_config(
    page_title=Config.APP_TITLE,
    page_icon=Config.APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded",
)


def inject_custom_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    @import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css');

    :root {
        --primary: #6366f1;
        --primary-dark: #4f46e5;
        --primary-light: #818cf8;
        --accent: #06b6d4;
        --accent-dark: #0891b2;
        --success: #10b981;
        --success-dark: #059669;
        --warning: #f59e0b;
        --danger: #ef4444;
        --bg-dark: #0f172a;
        --bg-darker: #020617;
        --bg-card: #1e293b;
        --bg-card-hover: #334155;
        --bg-card-light: #2d3748;
        --text-primary: #f1f5f9;
        --text-secondary: #94a3b8;
        --text-muted: #64748b;
        --border: #334155;
        --border-light: #475569;
        --glow-primary: 0 0 20px rgba(99, 102, 241, 0.3);
        --glow-accent: 0 0 20px rgba(6, 182, 212, 0.3);
        --glow-success: 0 0 20px rgba(16, 185, 129, 0.3);
        --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.3);
        --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
        --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.3);
        --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.3);
    }

    * {
        box-sizing: border-box;
    }

    .stApp {
        background: linear-gradient(135deg, var(--bg-dark) 0%, #1a1a2e 50%, #16213e 100%);
        min-height: 100vh;
    }

    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1200px;
    }

    h1, h2, h3, h4, h5, h6 {
        font-family: 'Inter', sans-serif !important;
        color: var(--text-primary) !important;
        letter-spacing: -0.02em;
    }

    .stMarkdown p {
        color: var(--text-secondary);
        line-height: 1.6;
    }

    div[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
        border-right: 1px solid var(--border);
    }

    div[data-testid="stSidebar"] .stMarkdown h1,
    div[data-testid="stSidebar"] .stMarkdown h2,
    div[data-testid="stSidebar"] .stMarkdown h3 {
        color: var(--text-primary) !important;
    }

    .stButton > button {
        background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.6rem 1.5rem;
        font-weight: 600;
        font-size: 0.9rem;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: var(--glow-primary);
        position: relative;
        overflow: hidden;
    }

    .stButton > button::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
        transition: left 0.5s;
    }

    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 0 40px rgba(99, 102, 241, 0.5);
    }

    .stButton > button:hover::before {
        left: 100%;
    }

    .stButton > button:active {
        transform: translateY(-1px);
    }

    .stDownloadButton > button {
        background: linear-gradient(135deg, var(--accent) 0%, var(--accent-dark) 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.6rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: var(--glow-accent);
    }

    .stDownloadButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 0 40px rgba(6, 182, 212, 0.5);
    }

    div[data-testid="stFileUploader"] {
        background: var(--bg-card);
        border: 2px dashed var(--border);
        border-radius: 16px;
        padding: 1.5rem;
        transition: all 0.3s ease;
    }

    div[data-testid="stFileUploader"]:hover {
        border-color: var(--primary);
        box-shadow: var(--glow-primary);
        background: var(--bg-card-hover);
    }



    div[data-testid="stSelectbox"] > div {
        background: var(--bg-card);
        border-radius: 10px;
        border: 1px solid var(--border);
    }

    div[data-testid="stDataFrame"] {
        background: var(--bg-card);
        border-radius: 16px;
        overflow: hidden;
        box-shadow: var(--shadow-lg);
        border: 1px solid var(--border);
    }

    .metric-card {
        background: linear-gradient(135deg, var(--bg-card) 0%, var(--bg-card-light) 100%);
        border: 1px solid var(--border);
        border-radius: 16px;
        padding: 1.5rem;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }

    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, var(--primary), var(--accent), var(--success));
        background-size: 200% 100%;
        animation: gradientShift 3s ease infinite;
    }

    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    .metric-card::after {
        content: '';
        position: absolute;
        top: -50%;
        right: -50%;
        width: 100%;
        height: 100%;
        background: radial-gradient(circle, rgba(99, 102, 241, 0.08) 0%, transparent 70%);
        transition: all 0.3s ease;
    }

    .metric-card:hover {
        transform: translateY(-8px) scale(1.02);
        box-shadow: var(--shadow-xl), var(--glow-primary);
        border-color: var(--primary);
    }

    .metric-card:hover::after {
        top: -30%;
        right: -30%;
    }

    .metric-card .metric-icon {
        font-size: 2rem;
        margin-bottom: 0.75rem;
        opacity: 0.9;
    }

    .metric-card .metric-label {
        font-size: 0.85rem;
        color: var(--text-secondary);
        margin-bottom: 0.5rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    .metric-card .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: var(--text-primary);
        line-height: 1.2;
        background: linear-gradient(135deg, var(--text-primary), var(--primary-light));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    .metric-card .metric-detail {
        font-size: 0.8rem;
        color: var(--text-muted);
        margin-top: 0.75rem;
        padding-top: 0.75rem;
        border-top: 1px solid var(--border);
    }

    .metric-card .metric-trend {
        display: inline-flex;
        align-items: center;
        gap: 0.25rem;
        font-size: 0.75rem;
        padding: 0.25rem 0.5rem;
        border-radius: 20px;
        margin-top: 0.5rem;
    }

    .metric-trend.up {
        background: rgba(16, 185, 129, 0.1);
        color: var(--success);
    }

    .metric-trend.down {
        background: rgba(239, 68, 68, 0.1);
        color: var(--danger);
    }

    .info-card {
        background: linear-gradient(135deg, var(--bg-card) 0%, var(--bg-card-light) 100%);
        border: 1px solid var(--border);
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        transition: all 0.3s ease;
    }

    .info-card:hover {
        border-color: var(--border-light);
        box-shadow: var(--shadow-md);
    }

    .info-card h4 {
        color: var(--accent) !important;
        margin-bottom: 1rem;
        font-size: 1.1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    .info-card h4 i {
        font-size: 1rem;
    }

    .warning-box {
        background: linear-gradient(135deg, rgba(245, 158, 11, 0.1) 0%, rgba(245, 158, 11, 0.05) 100%);
        border: 1px solid rgba(245, 158, 11, 0.3);
        border-radius: 12px;
        padding: 1rem 1.25rem;
        margin: 0.5rem 0;
        display: flex;
        align-items: flex-start;
        gap: 0.75rem;
    }

    .warning-box .warning-icon {
        color: var(--warning);
        font-size: 1.2rem;
        flex-shrink: 0;
    }

    .warning-box .warning-text {
        color: var(--warning);
        font-size: 0.9rem;
        line-height: 1.5;
    }

    .success-box {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(16, 185, 129, 0.05) 100%);
        border: 1px solid rgba(16, 185, 129, 0.3);
        border-radius: 12px;
        padding: 1rem 1.25rem;
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }

    .success-box i {
        color: var(--success);
        font-size: 1.2rem;
    }

    .error-box {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.1) 0%, rgba(239, 68, 68, 0.05) 100%);
        border: 1px solid rgba(239, 68, 68, 0.3);
        border-radius: 12px;
        padding: 1rem 1.25rem;
        display: flex;
        align-items: flex-start;
        gap: 0.75rem;
    }

    .error-box i {
        color: var(--danger);
        font-size: 1.2rem;
        flex-shrink: 0;
    }

    .ai-result-box {
        background: linear-gradient(135deg, var(--bg-card) 0%, var(--bg-card-light) 100%);
        border: 1px solid var(--border);
        border-radius: 16px;
        padding: 1.5rem;
        margin-top: 1rem;
        position: relative;
        overflow: hidden;
    }

    .ai-result-box::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, var(--primary), var(--accent));
    }

    .ai-result-box h4 {
        color: var(--primary) !important;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    div[data-testid="stTabs"] {
        background: var(--bg-card);
        border-radius: 16px;
        padding: 1.5rem;
        border: 1px solid var(--border);
    }

    div[data-testid="stTabs"] button {
        color: var(--text-secondary) !important;
        font-weight: 500;
        transition: all 0.3s ease;
    }

    div[data-testid="stTabs"] button:hover {
        color: var(--text-primary) !important;
    }

    div[data-testid="stTabs"] button[aria-selected="true"] {
        color: var(--primary) !important;
        border-bottom-color: var(--primary) !important;
        font-weight: 600;
    }

    .stProgress > div > div {
        background: linear-gradient(90deg, var(--primary), var(--accent), var(--success));
        background-size: 200% 100%;
        animation: gradientShift 2s ease infinite;
        border-radius: 10px;
    }

    .header-container {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.15) 0%, rgba(6, 182, 212, 0.15) 100%);
        border: 1px solid var(--border);
        border-radius: 20px;
        padding: 2.5rem;
        margin-bottom: 2rem;
        position: relative;
        overflow: hidden;
    }

    .header-container::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(99, 102, 241, 0.15) 0%, transparent 50%);
        animation: pulse 4s ease-in-out infinite;
    }

    .header-container::after {
        content: '';
        position: absolute;
        bottom: -50%;
        right: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(6, 182, 212, 0.1) 0%, transparent 50%);
        animation: pulse 4s ease-in-out infinite 2s;
    }

    @keyframes pulse {
        0%, 100% { transform: scale(1); opacity: 0.5; }
        50% { transform: scale(1.05); opacity: 0.8; }
    }

    .header-container .header-content {
        position: relative;
        z-index: 1;
    }

    .header-container h1 {
        position: relative;
        z-index: 1;
        display: flex;
        align-items: center;
        gap: 1rem;
    }

    .header-container .logo-icon {
        font-size: 2.5rem;
        background: linear-gradient(135deg, var(--primary), var(--accent));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    .stSpinner > div {
        border-top-color: var(--primary) !important;
    }

    div[data-testid="stTooltipIcon"] {
        color: var(--text-secondary);
    }

    .pagination-info {
        color: var(--text-secondary);
        font-size: 0.85rem;
        text-align: center;
        margin-top: 0.5rem;
        padding: 0.5rem;
        background: var(--bg-card);
        border-radius: 8px;
    }

    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    @keyframes fadeInLeft {
        from {
            opacity: 0;
            transform: translateX(-30px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }

    @keyframes fadeInRight {
        from {
            opacity: 0;
            transform: translateX(30px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }

    @keyframes scaleIn {
        from {
            opacity: 0;
            transform: scale(0.9);
        }
        to {
            opacity: 1;
            transform: scale(1);
        }
    }

    @keyframes slideDown {
        from {
            opacity: 0;
            transform: translateY(-20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    .animate-in {
        animation: fadeInUp 0.6s ease-out forwards;
    }

    .animate-in-left {
        animation: fadeInLeft 0.6s ease-out forwards;
    }

    .animate-in-right {
        animation: fadeInRight 0.6s ease-out forwards;
    }

    .animate-scale {
        animation: scaleIn 0.5s ease-out forwards;
    }

    .animate-slide-down {
        animation: slideDown 0.4s ease-out forwards;
    }

    .stSelectbox label,
    .stFileUploader label,
    .stSlider label,
    .stCheckbox label {
        color: var(--text-primary) !important;
        font-weight: 500;
    }

    div[data-testid="stTextInput"] label,
    div[data-testid="stTextArea"] label {
        color: var(--text-primary) !important;
        font-weight: 500;
    }

    div[data-testid="stTextInput"] input,
    div[data-testid="stTextArea"] textarea {
        background: var(--bg-card) !important;
        color: var(--text-primary) !important;
        border: 1px solid var(--border) !important;
        border-radius: 10px !important;
        transition: all 0.3s ease;
    }

    div[data-testid="stTextInput"] input:focus,
    div[data-testid="stTextArea"] textarea:focus {
        border-color: var(--primary) !important;
        box-shadow: var(--glow-primary);
    }

    .logo-container {
        display: flex;
        align-items: center;
        gap: 1rem;
    }

    .logo-icon-large {
        width: 60px;
        height: 60px;
        background: linear-gradient(135deg, var(--primary), var(--accent));
        border-radius: 16px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 2rem;
        box-shadow: var(--glow-primary);
    }

    .logo-text h1 {
        margin: 0;
        font-size: 1.8rem;
        background: linear-gradient(135deg, var(--text-primary), var(--primary-light));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    .logo-text p {
        margin: 0;
        color: var(--text-secondary);
        font-size: 0.9rem;
    }

    .feature-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.5rem 1rem;
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 20px;
        font-size: 0.8rem;
        color: var(--text-secondary);
        margin: 0.25rem;
    }

    .feature-badge i {
        color: var(--primary);
    }

    .loading-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 3rem;
    }

    .loading-spinner {
        width: 50px;
        height: 50px;
        border: 3px solid var(--border);
        border-top: 3px solid var(--primary);
        border-radius: 50%;
        animation: spin 1s linear infinite;
        margin-bottom: 1rem;
    }

    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }

    .loading-text {
        color: var(--text-secondary);
        font-size: 1rem;
        animation: pulse 2s ease-in-out infinite;
    }

    .stats-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 1rem;
    }

    .help-section {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1rem;
    }

    .help-section h4 {
        color: var(--primary) !important;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    .help-step {
        display: flex;
        align-items: flex-start;
        gap: 1rem;
        padding: 1rem;
        background: var(--bg-card-light);
        border-radius: 12px;
        margin-bottom: 0.75rem;
        transition: all 0.3s ease;
    }

    .help-step:hover {
        background: var(--bg-card-hover);
        transform: translateX(5px);
    }

    .help-step-number {
        width: 30px;
        height: 30px;
        background: linear-gradient(135deg, var(--primary), var(--accent));
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.8rem;
        font-weight: 700;
        color: white;
        flex-shrink: 0;
    }

    .help-step-content h5 {
        margin: 0 0 0.25rem 0;
        color: var(--text-primary) !important;
        font-size: 0.95rem;
    }

    .help-step-content p {
        margin: 0;
        color: var(--text-secondary);
        font-size: 0.85rem;
    }

    .tooltip-custom {
        position: relative;
        display: inline-block;
    }

    .tooltip-custom .tooltip-text {
        visibility: hidden;
        width: 200px;
        background: var(--bg-card);
        color: var(--text-primary);
        text-align: center;
        border-radius: 8px;
        padding: 0.5rem;
        position: absolute;
        z-index: 10;
        bottom: 125%;
        left: 50%;
        margin-left: -100px;
        opacity: 0;
        transition: opacity 0.3s;
        border: 1px solid var(--border);
        font-size: 0.8rem;
    }

    .tooltip-custom:hover .tooltip-text {
        visibility: visible;
        opacity: 1;
    }

    @media (max-width: 768px) {
        .main .block-container {
            padding: 1rem;
        }

        .header-container {
            padding: 1.5rem;
            border-radius: 16px;
        }

        .header-container h1 {
            font-size: 1.5rem;
        }

        .metric-card {
            padding: 1rem;
        }

        .metric-card .metric-value {
            font-size: 1.5rem;
        }

        div[data-testid="stTabs"] {
            padding: 1rem;
        }

        .info-card {
            padding: 1rem;
        }

        .help-step {
            flex-direction: column;
        }

        .logo-icon-large {
            width: 50px;
            height: 50px;
            font-size: 1.5rem;
        }
    }

    @media (max-width: 480px) {
        .main .block-container {
            padding: 0.75rem;
        }

        .header-container {
            padding: 1rem;
        }

        .header-container h1 {
            font-size: 1.25rem;
            flex-direction: column;
            text-align: center;
        }

        .metric-card .metric-value {
            font-size: 1.25rem;
        }

        .stButton > button {
            width: 100%;
        }
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
    }

    .stTabs [data-baseweb="tab"] {
        padding: 0.75rem 1.5rem;
        border-radius: 10px 10px 0 0;
    }

    div[data-testid="stExpander"] {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 12px;
        overflow: hidden;
    }

    div[data-testid="stExpander"] summary {
        color: var(--text-primary);
        font-weight: 500;
    }

    div[data-testid="stMetric"] {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 1rem;
    }

    div[data-testid="stMetric"] label {
        color: var(--text-secondary) !important;
    }

    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
        color: var(--text-primary) !important;
    }

    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }

    ::-webkit-scrollbar-track {
        background: var(--bg-dark);
    }

    ::-webkit-scrollbar-thumb {
        background: var(--border);
        border-radius: 4px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: var(--border-light);
    }

    .stAlert {
        border-radius: 12px;
    }

    </style>
    """, unsafe_allow_html=True)

    lang = st.session_state.get("lang", "zh")
    if lang == "zh":
        st.markdown("""
    <script>
    (function() {
        if (window.__i18nHeaderDone) return;
        window.__i18nHeaderDone = true;

        var MAP = [
            ["Deploy this app to Streamlit Cloud", "部署应用到 Streamlit 云服务"],
            ["Deploy this app", "部署应用"],
            ["Edit in Playground", "在 Playground 中编辑"],
            ["Edit in", "编辑于"],
            ["Record a screencast", "录制屏幕"],
            ["Rerun the app", "重新运行应用"],
            ["Always rerun", "自动刷新"],
            ["Clear cache data", "清除缓存数据"],
            ["Clear app cache", "清除应用缓存"],
            ["Clear cache", "清除缓存"],
            ["Main menu", "主菜单"],
            ["Developer options", "开发者选项"],
            ["Settings", "设置"],
            ["About", "关于"],
            ["Rerun", "重新运行"],
            ["Print", "打印"],
            ["Theme", "主题"],
        ];

        function findZh(text) {
            var trimmed = text.trim();
            for (var i = 0; i < MAP.length; i++) {
                if (trimmed === MAP[i][0]) return MAP[i][1];
            }
            for (var i = 0; i < MAP.length; i++) {
                if (trimmed.indexOf(MAP[i][0]) !== -1) return trimmed.replace(MAP[i][0], MAP[i][1]);
            }
            return null;
        }

        function translateNode(node) {
            if (node.nodeType === 3) {
                var zh = findZh(node.textContent);
                if (zh) node.textContent = zh;
            }
        }

        function translateEl(el) {
            var i, child;
            for (i = 0; i < el.childNodes.length; i++) {
                child = el.childNodes[i];
                if (child.nodeType === 3) {
                    var zh = findZh(child.textContent);
                    if (zh) child.textContent = zh;
                } else if (child.nodeType === 1) {
                    translateEl(child);
                }
            }
            var aria = el.getAttribute("aria-label");
            if (aria) {
                var zh = findZh(aria);
                if (zh) el.setAttribute("aria-label", zh);
            }
            if (el.title) {
                var zh = findZh(el.title);
                if (zh) el.title = zh;
            }
        }

        var running = false;
        function run() {
            if (running) return;
            running = true;
            try {
                var selectors = '[data-baseweb="tooltip"], [role="tooltip"], [role="menuitem"], [data-baseweb="menu"] li, [data-baseweb="menu"] [role="option"]';
                document.querySelectorAll(selectors).forEach(translateEl);
                document.querySelectorAll('header button, header a, [data-testid="stHeader"] button, [data-testid="stHeader"] a').forEach(translateEl);
                document.querySelectorAll('button[data-testid], a[data-testid]').forEach(function(el) {
                    var tid = el.getAttribute("data-testid") || "";
                    if (tid.indexOf("stApp") !== -1 || tid.indexOf("stHeader") !== -1 || tid.indexOf("stTheme") !== -1 || tid.indexOf("stMain") !== -1) {
                        translateEl(el);
                    }
                });
            } catch(e) {}
            running = false;
        }

        run();
        new MutationObserver(run).observe(document.body, {childList:true, subtree:true, characterData:true});
    })();
    </script>
    """, unsafe_allow_html=True)


def init_session_state():
    defaults = {
        'lang': 'zh',
        'uploaded_file': None,
        'file_path': None,
        'loader': None,
        'current_sheet': None,
        'df': None,
        'profile': None,
        'ai_analyzer': None,
        'ai_result': None,
        'report_content': None,
        'page': 0,
        'page_size': 50,
        'is_analyzing': False,
        'error_message': None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def save_uploaded_file(uploaded_file) -> Optional[str]:
    try:
        suffix = Path(uploaded_file.name).suffix
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(uploaded_file.getbuffer())
            return tmp.name
    except Exception as e:
        st.error(t("save_file_failed", e))
        return None


def load_excel_data(file_path: str, sheet_name: str) -> Optional[pd.DataFrame]:
    try:
        loader = ExcelLoader(file_path)
        df = loader.load(sheet_name=sheet_name)
        return df
    except Exception as e:
        st.error(t("load_data_failed", e))
        return None


def get_data_profile(df: pd.DataFrame) -> Optional[DataProfile]:
    try:
        profiler = DataProfiler(df)
        return profiler.generate_profile()
    except Exception as e:
        st.error(t("gen_profile_failed", e))
        return None


def render_header():
    st.markdown(f"""
    <div class="header-container animate-in">
        <div class="header-content">
            <div class="logo-container">
                <div class="logo-icon-large">
                    <i class="fas fa-chart-line"></i>
                </div>
                <div class="logo-text">
                    <h1>AI Excel Analyzer</h1>
                    <p>{t("app_subtitle")}</p>
                </div>
            </div>
            <p style="color: #94a3b8; margin: 1rem 0 0; font-size: 1rem;">
                {t("app_desc")}
            </p>
            <div style="margin-top: 1rem;">
                <span class="feature-badge"><i class="fas fa-robot"></i> {t("badge_ai")}</span>
                <span class="feature-badge"><i class="fas fa-bolt"></i> {t("badge_fast")}</span>
                <span class="feature-badge"><i class="fas fa-file-alt"></i> {t("badge_report")}</span>
                <span class="feature-badge"><i class="fas fa-chart-bar"></i> {t("badge_chart")}</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_metric_card(label: str, value: str, detail: str = "", icon: str = ""):
    detail_html = f'<div class="metric-detail">{detail}</div>' if detail else ""
    icon_html = f'<div class="metric-icon"><i class="{icon}"></i></div>' if icon else ""
    st.markdown(f"""
    <div class="metric-card">
        {icon_html}
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
        {detail_html}
    </div>
    """, unsafe_allow_html=True)


def render_sidebar():
    with st.sidebar:
        st.markdown(f"""
        <div style="text-align: center; padding: 1rem 0;">
            <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">
                <i class="fas fa-chart-line" style="background: linear-gradient(135deg, var(--primary), var(--accent)); -webkit-background-clip: text; -webkit-text-fill-color: transparent;"></i>
            </div>
            <h2 style="margin: 0; font-size: 1.2rem;">{t("sidebar_control")}</h2>
        </div>
        """, unsafe_allow_html=True)

        lang_options = {"中文": "zh", "English": "en"}
        current_lang = st.session_state.get("lang", "zh")
        current_label = "中文" if current_lang == "zh" else "English"
        selected_lang_label = st.selectbox(
            t("lang_label"),
            options=list(lang_options.keys()),
            index=list(lang_options.keys()).index(current_label),
        )
        selected_lang = lang_options[selected_lang_label]
        if selected_lang != st.session_state.get("lang"):
            st.session_state["lang"] = selected_lang
            st.rerun()

        st.markdown("---")

        st.markdown(f"### <i class='fas fa-upload'></i> {t('sidebar_upload')}", unsafe_allow_html=True)
        uploaded_file = st.file_uploader(
            t("upload_label"),
            type=['xlsx', 'xls'],
            help=t("upload_help"),
        )

        if uploaded_file is not None:
            if st.session_state.uploaded_file != uploaded_file.name:
                st.session_state.uploaded_file = uploaded_file.name
                st.session_state.file_path = save_uploaded_file(uploaded_file)
                st.session_state.loader = None
                st.session_state.current_sheet = None
                st.session_state.df = None
                st.session_state.profile = None
                st.session_state.ai_result = None
                st.session_state.report_content = None
                st.session_state.page = 0

            if st.session_state.file_path:
                try:
                    loader = ExcelLoader(st.session_state.file_path)
                    st.session_state.loader = loader
                    sheet_names = loader.get_sheet_names()

                    st.markdown(f"### <i class='fas fa-file-spreadsheet'></i> {t('sheet_select')}", unsafe_allow_html=True)
                    selected_sheet = st.selectbox(
                        t("sheet_label"),
                        options=sheet_names,
                        index=0,
                        label_visibility="collapsed",
                    )

                    if selected_sheet != st.session_state.current_sheet:
                        st.session_state.current_sheet = selected_sheet
                        st.session_state.df = None
                        st.session_state.profile = None
                        st.session_state.ai_result = None
                        st.session_state.report_content = None
                        st.session_state.page = 0

                except Exception as e:
                    st.markdown(f"""
                    <div class="error-box">
                        <i class="fas fa-file-excel" style="color: var(--danger);"></i>
                        <span class="warning-text">{t("file_read_error", e)}</span>
                    </div>
                    """, unsafe_allow_html=True)

        st.markdown("---")

        st.markdown(f"### <i class='fas fa-list'></i> {t('pagination')}", unsafe_allow_html=True)
        page_size = st.slider(
            t("page_rows"),
            min_value=10,
            max_value=100,
            value=st.session_state.page_size,
            step=10,
        )
        st.session_state.page_size = page_size

        st.markdown("---")

        st.markdown(f"### <i class='fas fa-key'></i> {t('api_config')}", unsafe_allow_html=True)
        api_key = st.text_input(
            t("api_key_label"),
            value=st.session_state.get('api_key_input', ''),
            type="password",
            help=t("api_key_help"),
            placeholder=t("api_key_placeholder"),
        )
        if api_key:
            st.session_state['api_key_input'] = api_key

        model_options = ["deepseek-v4-flash", "deepseek-v4-pro"]
        current_model = st.session_state.get('model_input', 'deepseek-v4-flash')
        selected_model = st.selectbox(
            "选择模型",
            options=model_options,
            index=model_options.index(current_model) if current_model in model_options else 0,
            help="deepseek-v4-flash: 快速响应，适合日常分析\ndeepseek-v4-pro: 更高级的推理能力",
        )
        st.session_state['model_input'] = selected_model

        st.markdown("---")

        st.markdown(f"### <i class='fas fa-book'></i> {t('usage_guide')}", unsafe_allow_html=True)

        with st.expander(t("quick_start"), expanded=False):
            st.markdown(f"""
            <div class="help-section">
                <div class="help-step">
                    <div class="help-step-number">1</div>
                    <div class="help-step-content">
                        <h5>{t("step1_title")}</h5>
                        <p>{t("step1_desc")}</p>
                    </div>
                </div>
                <div class="help-step">
                    <div class="help-step-number">2</div>
                    <div class="help-step-content">
                        <h5>{t("step2_title")}</h5>
                        <p>{t("step2_desc")}</p>
                    </div>
                </div>
                <div class="help-step">
                    <div class="help-step-number">3</div>
                    <div class="help-step-content">
                        <h5>{t("step3_title")}</h5>
                        <p>{t("step3_desc")}</p>
                    </div>
                </div>
                <div class="help-step">
                    <div class="help-step-number">4</div>
                    <div class="help-step-content">
                        <h5>{t("step4_title")}</h5>
                        <p>{t("step4_desc")}</p>
                    </div>
                </div>
                <div class="help-step">
                    <div class="help-step-number">5</div>
                    <div class="help-step-content">
                        <h5>{t("step5_title")}</h5>
                        <p>{t("step5_desc")}</p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        with st.expander(t("faq"), expanded=False):
            st.markdown(f"""
            **{t("faq_q1")}**
            {t("faq_a1")}

            **{t("faq_q2")}**
            {t("faq_a2")}

            **{t("faq_q3")}**
            {t("faq_a3")}

            **{t("faq_q4")}**
            {t("faq_a4")}
            """)


def render_data_preview(df: pd.DataFrame):
    st.markdown(f"### <i class='fas fa-table'></i> {t('data_preview')}", unsafe_allow_html=True)

    total_rows = len(df)
    total_pages = max(1, (total_rows + st.session_state.page_size - 1) // st.session_state.page_size)

    if st.session_state.page >= total_pages:
        st.session_state.page = 0

    start_idx = st.session_state.page * st.session_state.page_size
    end_idx = min(start_idx + st.session_state.page_size, total_rows)

    df_display = df.iloc[start_idx:end_idx]

    st.dataframe(
        df_display,
        use_container_width=True,
        height=400,
    )

    col1, col2, col3 = st.columns([1, 3, 1])

    with col1:
        if st.button(t("prev_page"), disabled=st.session_state.page == 0):
            st.session_state.page -= 1
            st.rerun()

    with col3:
        if st.button(t("next_page"), disabled=st.session_state.page >= total_pages - 1):
            st.session_state.page += 1
            st.rerun()

    with col2:
        st.markdown(
            f'<p class="pagination-info">{t("page_info", st.session_state.page + 1, total_pages, start_idx + 1, end_idx, f"{total_rows:,}")}</p>',
            unsafe_allow_html=True
        )


def render_basic_info(profile: DataProfile, df: pd.DataFrame):
    st.markdown(f"### <i class='fas fa-chart-pie'></i> {t('basic_info')}", unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        render_metric_card(t("metric_rows"), f"{profile.row_count:,}", t("metric_rows_detail"), "fas fa-database")

    with col2:
        render_metric_card(t("metric_cols"), f"{profile.column_count}", t("metric_cols_detail"), "fas fa-columns")

    with col3:
        total_cells = profile.row_count * profile.column_count
        render_metric_card(t("metric_cells"), f"{total_cells:,}", t("metric_cells_detail"), "fas fa-th")

    with col4:
        total_null = sum(col.null_count for col in profile.columns)
        null_ratio = total_null / total_cells if total_cells > 0 else 0
        render_metric_card(t("metric_null"), f"{null_ratio:.1%}", t("metric_null_detail", f"{total_null:,}"), "fas fa-exclamation-triangle")

    st.markdown("")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"""
        <div class="info-card">
            <h4><i class="fas fa-list"></i> {t("col_info")}</h4>
        </div>
        """, unsafe_allow_html=True)

        col_data = []
        for col in profile.columns:
            col_data.append({
                t("col_name"): col.name,
                t("col_type"): col.dtype,
                t("col_non_null"): col.non_null_count,
                t("col_null"): col.null_count,
                t("col_null_ratio"): f"{col.null_ratio:.1%}",
            })

        col_df = pd.DataFrame(col_data)
        st.dataframe(col_df, use_container_width=True, height=300)

    with col2:
        st.markdown(f"""
        <div class="info-card">
            <h4><i class="fas fa-chart-bar"></i> {t("type_dist")}</h4>
        </div>
        """, unsafe_allow_html=True)

        type_counts = {}
        for col in profile.columns:
            dtype = col.dtype
            type_counts[dtype] = type_counts.get(dtype, 0) + 1

        type_df = pd.DataFrame([
            {t("type_label"): k, t("type_count"): v} for k, v in type_counts.items()
        ])
        st.dataframe(type_df, use_container_width=True)

    if profile.warnings:
        st.markdown("")
        st.markdown(f"""
        <div class="info-card">
            <h4><i class="fas fa-exclamation-circle"></i> {t("quality_warning")}</h4>
        </div>
        """, unsafe_allow_html=True)

        for warning in profile.warnings:
            st.markdown(f"""
            <div class="warning-box">
                <span class="warning-icon"><i class="fas fa-exclamation-triangle"></i></span>
                <span class="warning-text">{warning}</span>
            </div>
            """, unsafe_allow_html=True)


def render_ai_analysis(profile: DataProfile, df: pd.DataFrame):
    st.markdown(f"### <i class='fas fa-robot'></i> {t('ai_analysis')}", unsafe_allow_html=True)

    api_key = st.session_state.get('api_key_input', '')

    if not api_key:
        st.markdown(f"""
        <div class="warning-box">
            <span class="warning-icon"><i class="fas fa-key"></i></span>
            <span class="warning-text">{t("api_key_required")}</span>
        </div>
        """, unsafe_allow_html=True)
        return

    col1, col2 = st.columns(2)

    with col1:
        analyze_button = st.button(
            t("btn_overview"),
            use_container_width=True,
            help=t("btn_overview_help"),
        )

    with col2:
        insight_button = st.button(
            t("btn_insight"),
            use_container_width=True,
            help=t("btn_insight_help"),
        )

    if analyze_button or insight_button:
        st.session_state.is_analyzing = True
        st.session_state.ai_result = None

        try:
            progress_bar = st.progress(0)
            status_text = st.empty()

            status_text.markdown(f"""
            <div class="loading-container">
                <div class="loading-spinner"></div>
                <div class="loading-text">{t("ai_analyzing")}</div>
            </div>
            """, unsafe_allow_html=True)

            progress_bar.progress(20)

            selected_model = st.session_state.get('model_input', 'deepseek-v4-flash')
            analyzer = AIAnalyzer(api_key=api_key, model=selected_model)
            st.session_state.ai_analyzer = analyzer

            sample_data = df.head(20).to_string()

            progress_bar.progress(40)

            if analyze_button:
                result = analyzer.analyze_data_overview(
                    profile=profile,
                    sample_data=sample_data,
                    stream=False,
                )
            else:
                result = analyzer.analyze_insights(
                    profile=profile,
                    sample_data=sample_data,
                    stream=False,
                )

            progress_bar.progress(80)

            st.session_state.ai_result = result
            st.session_state.is_analyzing = False

            progress_bar.progress(100)
            status_text.empty()
            progress_bar.empty()

        except NetworkError as e:
            st.markdown(f"""
            <div class="error-box">
                <i class="fas fa-wifi" style="color: var(--danger);"></i>
                <span class="warning-text">{t("error_network", e)}</span>
            </div>
            """, unsafe_allow_html=True)
        except RateLimitError as e:
            st.markdown(f"""
            <div class="error-box">
                <i class="fas fa-clock" style="color: var(--danger);"></i>
                <span class="warning-text">{t("error_rate_limit", e)}</span>
            </div>
            """, unsafe_allow_html=True)
        except APIError as e:
            st.markdown(f"""
            <div class="error-box">
                <i class="fas fa-exclamation-circle" style="color: var(--danger);"></i>
                <span class="warning-text">{t("error_api", e)}</span>
            </div>
            """, unsafe_allow_html=True)
        except AIAnalyzerError as e:
            st.markdown(f"""
            <div class="error-box">
                <i class="fas fa-bug" style="color: var(--danger);"></i>
                <span class="warning-text">{t("error_analysis", e)}</span>
            </div>
            """, unsafe_allow_html=True)
        except Exception as e:
            st.markdown(f"""
            <div class="error-box">
                <i class="fas fa-times-circle" style="color: var(--danger);"></i>
                <span class="warning-text">{t("error_unknown", e)}</span>
            </div>
            """, unsafe_allow_html=True)

    if st.session_state.ai_result:
        st.markdown("")
        st.markdown(f"""
        <div class="ai-result-box">
            <h4><i class="fas fa-file-alt"></i> {t("ai_result_title")}</h4>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(st.session_state.ai_result)

    st.markdown("---")

    st.markdown(f"### <i class='fas fa-question-circle'></i> {t('free_question')}", unsafe_allow_html=True)
    question = st.text_area(
        t("question_label"),
        placeholder=t("question_placeholder"),
        height=100,
    )

    if st.button(t("btn_ask"), use_container_width=True):
        if not question.strip():
            st.warning(t("warn_empty_question"))
            return

        if not api_key:
            st.warning(t("warn_no_api_key"))
            return

        try:
            progress_bar = st.progress(0)
            status_text = st.empty()

            status_text.markdown(f"""
            <div class="loading-container">
                <div class="loading-spinner"></div>
                <div class="loading-text">{t("ai_thinking")}</div>
            </div>
            """, unsafe_allow_html=True)

            progress_bar.progress(30)

            selected_model = st.session_state.get('model_input', 'deepseek-v4-flash')
            analyzer = AIAnalyzer(api_key=api_key, model=selected_model)
            sample_data = df.head(20).to_string()

            progress_bar.progress(50)

            result = analyzer.query(
                question=question,
                profile=profile,
                sample_data=sample_data,
                stream=False,
            )

            progress_bar.progress(100)
            status_text.empty()
            progress_bar.empty()

            st.markdown("")
            st.markdown(f"""
            <div class="ai-result-box">
                <h4><i class="fas fa-lightbulb"></i> {t("ai_answer_title")}</h4>
            </div>
            """, unsafe_allow_html=True)
            st.markdown(result)

        except Exception as e:
            st.markdown(f"""
            <div class="error-box">
                <i class="fas fa-times-circle" style="color: var(--danger);"></i>
                <span class="warning-text">{t("ask_failed", e)}</span>
            </div>
            """, unsafe_allow_html=True)


def render_report_section(profile: DataProfile):
    st.markdown(f"### <i class='fas fa-file-download'></i> {t('generate_report')}", unsafe_allow_html=True)

    ai_insights = st.session_state.ai_result

    if st.button(t("btn_generate"), use_container_width=True):
        try:
            progress_bar = st.progress(0)
            status_text = st.empty()

            status_text.markdown(f"""
            <div class="loading-container">
                <div class="loading-spinner"></div>
                <div class="loading-text">{t("generating")}</div>
            </div>
            """, unsafe_allow_html=True)

            progress_bar.progress(50)

            generator = ReportGenerator()
            content, filename = generator.generate_download(
                profile=profile,
                ai_insights=ai_insights,
            )
            st.session_state.report_content = content
            st.session_state.report_filename = filename

            progress_bar.progress(100)
            status_text.empty()
            progress_bar.empty()

            st.markdown(f"""
            <div class="success-box">
                <i class="fas fa-check-circle"></i>
                <span>{t("report_success")}</span>
            </div>
            """, unsafe_allow_html=True)

        except ReportGeneratorError as e:
            st.markdown(f"""
            <div class="error-box">
                <i class="fas fa-file-excel" style="color: var(--danger);"></i>
                <span class="warning-text">{t("report_gen_failed", e)}</span>
            </div>
            """, unsafe_allow_html=True)
        except Exception as e:
            st.markdown(f"""
            <div class="error-box">
                <i class="fas fa-times-circle" style="color: var(--danger);"></i>
                <span class="warning-text">{t("report_gen_error", e)}</span>
            </div>
            """, unsafe_allow_html=True)

    if st.session_state.report_content:
        st.markdown("")
        st.markdown(f"#### <i class='fas fa-eye'></i> {t('report_preview')}", unsafe_allow_html=True)

        with st.expander(t("report_preview_toggle"), expanded=False):
            st.markdown(st.session_state.report_content)

        st.download_button(
            label=t("btn_download"),
            data=st.session_state.report_content,
            file_name=st.session_state.get('report_filename', 'analysis_report.md'),
            mime="text/markdown",
            use_container_width=True,
        )


def main():
    inject_custom_css()
    init_session_state()

    render_header()
    render_sidebar()

    if st.session_state.file_path and st.session_state.loader:
        if st.session_state.current_sheet:
            if st.session_state.df is None:
                progress_bar = st.progress(0)
                status_text = st.empty()

                status_text.markdown(f"""
                <div class="loading-container">
                    <div class="loading-spinner"></div>
                    <div class="loading-text">{t("loading_data")}</div>
                </div>
                """, unsafe_allow_html=True)

                progress_bar.progress(30)
                df = load_excel_data(st.session_state.file_path, st.session_state.current_sheet)
                if df is not None:
                    st.session_state.df = df
                    progress_bar.progress(100)
                    status_text.empty()
                    progress_bar.empty()

            if st.session_state.df is not None:
                df = st.session_state.df

                if st.session_state.profile is None:
                    progress_bar = st.progress(0)
                    status_text = st.empty()

                    status_text.markdown(f"""
                    <div class="loading-container">
                        <div class="loading-spinner"></div>
                        <div class="loading-text">{t("loading_profile")}</div>
                    </div>
                    """, unsafe_allow_html=True)

                    progress_bar.progress(50)
                    profile = get_data_profile(df)
                    if profile is not None:
                        st.session_state.profile = profile
                        progress_bar.progress(100)
                        status_text.empty()
                        progress_bar.empty()

                if st.session_state.profile is not None:
                    profile = st.session_state.profile

                    tab1, tab2, tab3 = st.tabs([t("tab_preview"), t("tab_ai"), t("tab_report")])

                    with tab1:
                        render_data_preview(df)
                        st.markdown("")
                        render_basic_info(profile, df)

                    with tab2:
                        render_ai_analysis(profile, df)

                    with tab3:
                        render_report_section(profile)
    else:
        st.markdown(f"""
        <div style="text-align: center; padding: 4rem 2rem;">
            <div style="font-size: 5rem; margin-bottom: 1.5rem; opacity: 0.8;">
                <i class="fas fa-cloud-upload-alt" style="background: linear-gradient(135deg, var(--primary), var(--accent)); -webkit-background-clip: text; -webkit-text-fill-color: transparent;"></i>
            </div>
            <h2 style="color: var(--text-primary); margin-bottom: 1rem; font-size: 1.8rem;">{t("upload_title")}</h2>
            <p style="color: var(--text-secondary); font-size: 1.1rem; line-height: 1.6;">
                {t("upload_desc")}
            </p>
            <div style="margin-top: 2rem;">
                <span class="feature-badge"><i class="fas fa-file-excel"></i> {t("badge_excel")}</span>
                <span class="feature-badge"><i class="fas fa-shield-alt"></i> {t("badge_secure")}</span>
                <span class="feature-badge"><i class="fas fa-magic"></i> {t("badge_magic")}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
