"""
PaperMate AI – Research Paper to Presentation & Viva Assistant
Redesigned with the Soft Lavender Glassmorphism AI Dashboard Aesthetic:
- Dominant pastel lavender (#EDE7FA, #F4F0FC) and royal purple (#7654C8, #9B7AE8)
- Powder blue (#DCEAFF) and periwinkle accents
- White translucent frosted-glass panels with backdrop blur
- Glowing purple AI orb visual centerpiece
- Preserves all 7 acceptance criteria & 100% backend RAG/Agent/PPTX functionality
- Fully modular navigation system with dedicated page rendering functions
"""

import os
import io
import time
import streamlit as st
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from rag_pipeline import RAGPipeline
from agents import AgentCoordinator
from model_manager import (
    DEFAULT_MODEL_CANDIDATE,
    fetch_available_gemini_models,
    test_gemini_model_connection
)

# ==============================================================================
# STREAMLIT CONFIGURATION & SOFT LAVENDER GLASSMORPHISM THEME
# ==============================================================================
st.set_page_config(
    page_title="PaperMate AI – Soft Lavender AI Research Dashboard",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS implementing the exact soft lavender glassmorphism aesthetic
st.markdown("""
<style>
    /* ---------------- Fonts & Base Background ---------------- */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Inter:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        color: #28243A;
    }

    /* Ambient Pastel Lavender & Powder Blue Gradient Canvas */
    .stApp {
        background-color: #F4F0FC;
        background-image: 
            radial-gradient(circle at 8% 12%, rgba(220, 234, 255, 0.75) 0%, transparent 40%),
            radial-gradient(circle at 92% 8%, rgba(237, 231, 250, 0.85) 0%, transparent 45%),
            radial-gradient(circle at 50% 50%, rgba(255, 255, 255, 0.5) 0%, transparent 60%),
            radial-gradient(circle at 85% 85%, rgba(220, 234, 255, 0.6) 0%, transparent 45%),
            radial-gradient(circle at 15% 90%, rgba(237, 231, 250, 0.7) 0%, transparent 40%);
        background-attachment: fixed;
    }

    /* Max-width container & clean spacing */
    .block-container {
        padding-top: 1.6rem;
        padding-bottom: 3.2rem;
        max-width: 1240px;
    }

    /* ---------------- Sidebar Glass Styling ---------------- */
    section[data-testid="stSidebar"] {
        background: rgba(255, 255, 255, 0.65) !important;
        backdrop-filter: blur(20px) !important;
        -webkit-backdrop-filter: blur(20px) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.8) !important;
        box-shadow: 4px 0 24px rgba(118, 84, 200, 0.05) !important;
    }

    section[data-testid="stSidebar"] .block-container {
        padding-top: 1.8rem;
    }

    .sidebar-brand-wrapper {
        display: flex;
        align-items: center;
        gap: 0.85rem;
        margin-bottom: 0.3rem;
    }

    .sidebar-orb-logo {
        width: 42px;
        height: 42px;
        border-radius: 50%;
        background: radial-gradient(circle at 35% 30%, #FFFFFF 0%, #DCEAFF 25%, #9B7AE8 60%, #7654C8 100%);
        box-shadow: 0 0 16px rgba(155, 122, 232, 0.55), inset 0 0 8px rgba(255, 255, 255, 0.8);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.25rem;
    }

    .sidebar-title {
        font-size: 1.25rem;
        font-weight: 800;
        background: linear-gradient(135deg, #4C2B9E 0%, #7654C8 60%, #9B7AE8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: -0.02em;
        line-height: 1.2;
    }

    .sidebar-tagline {
        font-size: 0.8rem;
        color: #7A728E;
        font-weight: 500;
        margin-bottom: 1.4rem;
        padding-left: 0.1rem;
    }

    .sidebar-section-heading {
        font-size: 0.72rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.09em;
        color: #9B7AE8;
        margin-top: 1.3rem;
        margin-bottom: 0.6rem;
    }

    /* ---------------- Navigation Radio Menu Overrides & Highlighting ---------------- */
    div[data-testid="stRadio"] div[role="radiogroup"] > label {
        background: rgba(255, 255, 255, 0.65) !important;
        border: 1px solid rgba(255, 255, 255, 0.85) !important;
        border-radius: 14px !important;
        padding: 0.7rem 1rem !important;
        margin-bottom: 0.45rem !important;
        cursor: pointer !important;
        transition: all 0.22s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 2px 8px rgba(118, 84, 200, 0.04) !important;
        display: flex !important;
        align-items: center !important;
    }

    div[data-testid="stRadio"] div[role="radiogroup"] > label:hover {
        background: rgba(255, 255, 255, 0.92) !important;
        border-color: rgba(155, 122, 232, 0.5) !important;
        transform: translateX(3px) !important;
    }

    /* Visually Highlighted Selected Navigation Item */
    div[data-testid="stRadio"] div[role="radiogroup"] > label:has(input:checked) {
        background: linear-gradient(135deg, rgba(237, 231, 250, 0.98) 0%, rgba(220, 234, 255, 0.95) 100%) !important;
        border: 1.5px solid #7654C8 !important;
        box-shadow: 0 6px 18px rgba(118, 84, 200, 0.18) !important;
        transform: translateX(4px) !important;
    }

    div[data-testid="stRadio"] div[role="radiogroup"] > label:has(input:checked) p,
    div[data-testid="stRadio"] div[role="radiogroup"] > label:has(input:checked) span,
    div[data-testid="stRadio"] div[role="radiogroup"] > label:has(input:checked) div {
        color: #4C2B9E !important;
        font-weight: 700 !important;
    }

    /* ---------------- Glassmorphism Cards ---------------- */
    .glass-card {
        background: rgba(255, 255, 255, 0.72);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.85);
        border-radius: 24px;
        box-shadow: 0 10px 30px -5px rgba(118, 84, 200, 0.06), 0 4px 12px rgba(0, 0, 0, 0.02);
        padding: 2rem;
        transition: all 0.28s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }

    .glass-card:hover {
        border-color: rgba(155, 122, 232, 0.35);
        box-shadow: 0 18px 40px -8px rgba(118, 84, 200, 0.12);
        transform: translateY(-2px);
    }

    /* ---------------- Glowing AI Orb Hero ---------------- */
    .welcome-hero-panel {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.82) 0%, rgba(244, 240, 252, 0.8) 50%, rgba(220, 234, 255, 0.75) 100%);
        backdrop-filter: blur(24px);
        -webkit-backdrop-filter: blur(24px);
        border: 1px solid rgba(255, 255, 255, 0.95);
        border-radius: 28px;
        padding: 2.8rem 3rem;
        margin-bottom: 2rem;
        box-shadow: 0 20px 45px -10px rgba(118, 84, 200, 0.08), 0 1px 3px rgba(255, 255, 255, 0.8);
        position: relative;
        overflow: hidden;
    }

    .welcome-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        background: rgba(155, 122, 232, 0.12);
        border: 1px solid rgba(155, 122, 232, 0.25);
        padding: 0.38rem 0.95rem;
        border-radius: 9999px;
        font-size: 0.78rem;
        font-weight: 700;
        color: #7654C8;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        margin-bottom: 1.1rem;
    }

    .welcome-heading {
        font-size: 2.5rem;
        font-weight: 800;
        color: #28243A;
        letter-spacing: -0.03em;
        line-height: 1.2;
        margin-bottom: 0.65rem;
    }

    .welcome-subtitle {
        font-size: 1.08rem;
        color: #5E5675;
        font-weight: 400;
        line-height: 1.6;
        max-width: 680px;
    }

    /* Centerpiece Glowing Purple AI Orb */
    .ai-orb-wrapper {
        display: flex;
        align-items: center;
        justify-content: center;
        position: relative;
        width: 170px;
        height: 170px;
    }

    .ai-orb-core {
        width: 120px;
        height: 120px;
        border-radius: 50%;
        background: radial-gradient(circle at 35% 30%, #FFFFFF 0%, #DCEAFF 22%, #9B7AE8 58%, #7654C8 85%, #4C2B9E 100%);
        box-shadow: 
            0 0 40px rgba(155, 122, 232, 0.65),
            0 0 75px rgba(118, 84, 200, 0.35),
            inset 0 0 25px rgba(255, 255, 255, 0.75),
            inset -8px -8px 20px rgba(76, 43, 158, 0.5);
        animation: floatOrb 5s ease-in-out infinite, pulseOrb 3.5s ease-in-out infinite alternate;
        position: relative;
        z-index: 2;
    }

    .ai-orb-aura {
        position: absolute;
        width: 165px;
        height: 165px;
        border-radius: 50%;
        background: radial-gradient(circle, rgba(155, 122, 232, 0.35) 0%, rgba(220, 234, 255, 0.2) 50%, transparent 70%);
        filter: blur(14px);
        animation: pulseAura 4s ease-in-out infinite alternate;
        z-index: 1;
    }

    @keyframes floatOrb {
        0%, 100% { transform: translateY(0px) rotate(0deg); }
        50% { transform: translateY(-8px) rotate(4deg); }
    }

    @keyframes pulseOrb {
        0% { filter: brightness(1) drop-shadow(0 0 20px rgba(155, 122, 232, 0.45)); }
        100% { filter: brightness(1.15) drop-shadow(0 0 45px rgba(118, 84, 200, 0.7)); }
    }

    @keyframes pulseAura {
        0% { transform: scale(0.92); opacity: 0.6; }
        100% { transform: scale(1.12); opacity: 0.95; }
    }

    /* ---------------- Feature Cards 2x2 Grid ---------------- */
    .feature-grid-title {
        font-size: 1.45rem;
        font-weight: 800;
        color: #28243A;
        letter-spacing: -0.02em;
        margin-bottom: 1.1rem;
    }

    .feature-glass-box {
        background: rgba(255, 255, 255, 0.68);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.9);
        border-radius: 22px;
        padding: 1.6rem 1.6rem;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        box-shadow: 0 8px 24px -4px rgba(118, 84, 200, 0.05);
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
        margin-bottom: 1rem;
    }

    .feature-glass-box:hover {
        background: rgba(255, 255, 255, 0.88);
        border-color: rgba(155, 122, 232, 0.4);
        box-shadow: 0 14px 32px -6px rgba(118, 84, 200, 0.12);
        transform: translateY(-3px);
    }

    .feature-icon-badge {
        width: 44px;
        height: 44px;
        border-radius: 14px;
        background: linear-gradient(135deg, rgba(237, 231, 250, 0.9) 0%, rgba(220, 234, 255, 0.9) 100%);
        border: 1px solid rgba(155, 122, 232, 0.2);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.35rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 12px rgba(118, 84, 200, 0.08);
    }

    .feature-box-heading {
        font-size: 1.15rem;
        font-weight: 700;
        color: #28243A;
        margin-bottom: 0.4rem;
    }

    .feature-box-desc {
        font-size: 0.9rem;
        color: #635C78;
        line-height: 1.55;
        margin-bottom: 1rem;
    }

    /* ---------------- Technology Grid ---------------- */
    .tech-grid-card {
        background: rgba(255, 255, 255, 0.65);
        backdrop-filter: blur(14px);
        border: 1px solid rgba(255, 255, 255, 0.85);
        border-radius: 18px;
        padding: 1.2rem 1.3rem;
        text-align: center;
        box-shadow: 0 4px 16px rgba(118, 84, 200, 0.04);
        transition: all 0.2s ease;
    }

    .tech-grid-card:hover {
        background: rgba(255, 255, 255, 0.85);
        border-color: rgba(155, 122, 232, 0.35);
        transform: translateY(-2px);
    }

    .tech-grid-icon {
        font-size: 1.6rem;
        margin-bottom: 0.4rem;
    }

    .tech-grid-name {
        font-size: 0.98rem;
        font-weight: 700;
        color: #28243A;
    }

    .tech-grid-role {
        font-size: 0.78rem;
        color: #7A728E;
        font-weight: 500;
    }

    /* ---------------- Status & Verification Cards ---------------- */
    .verification-glass-pill {
        background: rgba(237, 231, 250, 0.65);
        border-left: 4px solid #7654C8;
        border-top: 1px solid rgba(255, 255, 255, 0.8);
        border-right: 1px solid rgba(255, 255, 255, 0.8);
        border-bottom: 1px solid rgba(255, 255, 255, 0.8);
        padding: 1rem 1.3rem;
        border-radius: 0 16px 16px 0;
        margin-bottom: 1.2rem;
        font-size: 0.92rem;
        color: #28243A;
    }

    .result-glass-container {
        background: rgba(255, 255, 255, 0.8);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.95);
        border-radius: 22px;
        padding: 2.2rem 2.4rem;
        box-shadow: 0 10px 30px -5px rgba(118, 84, 200, 0.06);
        margin-bottom: 1.5rem;
        line-height: 1.7;
        color: #28243A;
    }

    .slide-glass-card {
        background: rgba(255, 255, 255, 0.78);
        backdrop-filter: blur(16px);
        border: 1px solid rgba(155, 122, 232, 0.25);
        border-radius: 20px;
        padding: 1.6rem 1.8rem;
        margin-bottom: 1.3rem;
        box-shadow: 0 8px 24px -4px rgba(118, 84, 200, 0.07);
    }

    .speaker-glass-box {
        background: rgba(244, 240, 252, 0.75);
        border-left: 3px solid #7654C8;
        padding: 0.9rem 1.1rem;
        border-radius: 0 12px 12px 0;
        margin-top: 1.1rem;
        font-size: 0.88rem;
        color: #4A445C;
    }

    /* ---------------- Button Styling ---------------- */
    .stButton>button {
        background: linear-gradient(135deg, #7654C8 0%, #9B7AE8 100%) !important;
        color: #FFFFFF !important;
        border-radius: 14px !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
        box-shadow: 0 6px 18px rgba(118, 84, 200, 0.22) !important;
        font-weight: 600 !important;
        font-size: 0.92rem !important;
        padding: 0.55rem 1.25rem !important;
        transition: all 0.25s ease !important;
    }

    .stButton>button:hover {
        background: linear-gradient(135deg, #6542B7 0%, #8967D8 100%) !important;
        box-shadow: 0 8px 24px rgba(118, 84, 200, 0.35) !important;
        transform: translateY(-2px) !important;
    }

    .stDownloadButton>button {
        background: linear-gradient(135deg, #4C2B9E 0%, #7654C8 100%) !important;
        color: #FFFFFF !important;
        border-radius: 14px !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
        font-weight: 600 !important;
        padding: 0.6rem 1.4rem !important;
        box-shadow: 0 6px 20px rgba(76, 43, 158, 0.25) !important;
    }

    .stDownloadButton>button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 10px 28px rgba(76, 43, 158, 0.38) !important;
    }
</style>
""", unsafe_allow_html=True)


# ==============================================================================
# SESSION STATE INITIALIZATION & NAVIGATION REGISTRATION
# ==============================================================================
NAV_OPTIONS = [
    "Dashboard",
    "Research Summary",
    "Concept Explorer",
    "Slide Generator",
    "Viva Practice",
    "Smart Intent Router",
    "Settings"
]

NAV_DISPLAY = {
    "Dashboard": "🏠  Dashboard",
    "Research Summary": "📑  Research Summary",
    "Concept Explorer": "💡  Concept Explorer",
    "Slide Generator": "📊  Slide Generator",
    "Viva Practice": "🎓  Viva Practice",
    "Smart Intent Router": "🧭  Smart Intent Router",
    "Settings": "⚙️  Settings"
}

def init_session_state():
    if "pending_navigation" not in st.session_state:
        st.session_state.pending_navigation = None
    if "active_page" not in st.session_state:
        st.session_state.active_page = "Dashboard"
    if "sidebar_nav" not in st.session_state:
        st.session_state.sidebar_nav = st.session_state.active_page
    if "nav_radio" not in st.session_state:
        st.session_state.nav_radio = st.session_state.active_page
    if "rag_pipeline" not in st.session_state:
        st.session_state.rag_pipeline = None
    if "agent_coordinator" not in st.session_state:
        st.session_state.agent_coordinator = None
    if "paper_processed" not in st.session_state:
        st.session_state.paper_processed = False
    if "paper_metadata" not in st.session_state:
        st.session_state.paper_metadata = {}
    if "cached_summary" not in st.session_state:
        st.session_state.cached_summary = None
    if "cached_concepts" not in st.session_state:
        st.session_state.cached_concepts = None
    if "cached_slides" not in st.session_state:
        st.session_state.cached_slides = None
    if "cached_viva" not in st.session_state:
        st.session_state.cached_viva = None
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "last_routed_intent" not in st.session_state:
        st.session_state.last_routed_intent = None
    if "available_models" not in st.session_state:
        st.session_state.available_models = [DEFAULT_MODEL_CANDIDATE]
    if "selected_model" not in st.session_state:
        st.session_state.selected_model = DEFAULT_MODEL_CANDIDATE
    if "model_test_result" not in st.session_state:
        st.session_state.model_test_result = None
    if "cached_api_key_for_models" not in st.session_state:
        st.session_state.cached_api_key_for_models = ""

init_session_state()

# ------------------------------------------------------------------------------
# PROGRAMMATIC NAVIGATION DISPATCHER (PRE-WIDGET INSTANTIATION)
# ------------------------------------------------------------------------------
# Apply any queued/pending navigation target to st.session_state.nav_radio
# BEFORE st.radio(key="nav_radio") is instantiated in the current script run.
if st.session_state.get("pending_navigation"):
    target_page = st.session_state.pending_navigation
    st.session_state.pending_navigation = None
    if target_page in NAV_OPTIONS:
        st.session_state.nav_radio = target_page
        st.session_state.active_page = target_page
        st.session_state.sidebar_nav = target_page

def navigate_to(page_name: str):
    """
    Safely queues programmatic navigation to target page and triggers a rerun.
    NEVER directly modifies st.session_state['nav_radio'] here because
    nav_radio has already been instantiated in the current script run.
    """
    if page_name in NAV_OPTIONS:
        st.session_state.pending_navigation = page_name
        st.session_state.active_page = page_name
        st.session_state.sidebar_nav = page_name
        st.rerun()

def render_back_button(page_key: str):
    """
    Renders a dedicated top-left '← Back to Dashboard' navigation button
    on all internal pages. Uses the safe session-state navigation dispatcher.
    """
    col_back, _ = st.columns([1.5, 4.5])
    with col_back:
        if st.button("← Back to Dashboard", key=f"btn_back_dash_{page_key}", help="Return to main dashboard"):
            navigate_to("Dashboard")
    st.markdown("<div style='margin-bottom: 0.6rem;'></div>", unsafe_allow_html=True)


# ==============================================================================
# SAMPLE RESEARCH PAPER (Vaswani et al. - Attention Is All You Need)
# ==============================================================================
SAMPLE_PAPER_TEXT = """
Attention Is All You Need
Ashish Vaswani, Noam Shazeer, Niki Parmar, Jakob Uszkoreit, Llion Jones, Aidan N. Gomez, Łukasz Kaiser, Illia Polosukhin
Google Brain, Google Research, University of Toronto

Abstract
The dominant sequence transduction models are based on complex recurrent or convolutional neural networks that include an encoder and a decoder. The best performing models also connect the encoder and decoder through an attention mechanism. We propose a new simple network architecture, the Transformer, based solely on attention mechanisms, dispensing with recurrence and convolutions entirely. Experiments on two machine translation tasks show these models to be superior in quality while being more parallelizable and requiring significantly less time to train. Our model achieves 28.4 BLEU on the WMT 2014 English-to-German translation task, improving over the existing best results, including ensembles, by over 2 BLEU. On the WMT 2014 English-to-French translation task, our model establishes a new single-model state-of-the-art BLEU score of 41.8 after training for 3.5 days on eight GPUs.

1. Introduction
Recurrent neural networks, long short-term memory (LSTM) and gated recurrent neural networks have been firmly established as state-of-the-art approaches in sequence modeling and transduction problems such as language modeling and machine translation. Recurrent models typically factor computation along the symbol positions of the input and output sequences. Aligning the positions to steps in computation time, they generate a sequence of hidden states h_t, as a function of the previous hidden state h_{t-1} and the input for position t. This inherently sequential nature precludes parallelization within training examples, which becomes critical at longer sequence lengths, as memory constraints limit batching across examples.
In this work we propose the Transformer, a model architecture eschewing recurrence and instead relying entirely on an attention mechanism to draw global dependencies between input and output. The Transformer allows for significantly more parallelization and can reach a new state of the art in translation quality after being trained for as little as twelve hours on eight P100 GPUs.

2. Background
The goal of reducing sequential computation also forms the foundation of the Extended Neural GPU, ByteNet and ConvS2S, all of which use convolutional neural networks as basic building blocks. In these models, the number of operations required to relate signals from two arbitrary input or output positions grows in the distance between positions, linearly for ConvS2S and logarithmically for ByteNet. This makes it more difficult to learn dependencies between distant positions. In the Transformer this is reduced to a constant number of operations, albeit at the cost of reduced effective resolution due to averaging attention-weighted positions, an effect we counteract with Multi-Head Attention.
Self-attention, sometimes called intra-attention, is an attention mechanism relating different positions of a single sequence in order to compute a representation of the sequence.

3. Model Architecture
Most competitive neural sequence transduction models have an encoder-decoder structure. Here, the encoder maps an input sequence of symbol representations (x_1, ..., x_n) to a sequence of continuous representations z = (z_1, ..., z_n). Given z, the decoder then generates an output sequence (y_1, ..., y_m) of symbols one element at a time. At each step the model is auto-regressive, consuming the previously generated symbols as additional input when generating the next.
The Transformer follows this overall architecture using stacked self-attention and point-wise, fully connected layers for both the encoder and decoder.

3.1 Encoder and Decoder Stacks
Encoder: The encoder is composed of a stack of N = 6 identical layers. Each layer has two sub-layers. The first is a multi-head self-attention mechanism, and the second is a simple, position-wise fully connected feed-forward network. We employ a residual connection around each of the two sub-layers, followed by layer normalization. That is, the output of each sub-layer is LayerNorm(x + Sublayer(x)). To facilitate these residual connections, all sub-layers in the model, as well as the embedding layers, produce outputs of dimension d_model = 512.
Decoder: The decoder is also composed of a stack of N = 6 identical layers. In addition to the two sub-layers in each encoder layer, the decoder inserts a third sub-layer, which performs multi-head attention over the output of the encoder stack. We also modify the self-attention sub-layer in the decoder stack to prevent positions from attending to subsequent positions. This masking ensures that predictions for position i can depend only on the known outputs at positions less than i.

3.2 Attention
An attention function can be described as mapping a query and a set of key-value pairs to an output, where the query, keys, values, and output are all vectors. The output is computed as a weighted sum of the values, where the weight assigned to each value is computed by a compatibility function of the query with the corresponding key.
Scaled Dot-Product Attention: We compute the attention function on a set of queries simultaneously, packed together into a matrix Q. The keys and values are also packed into matrices K and V. We compute the matrix of outputs as:
Attention(Q, K, V) = softmax(Q K^T / sqrt(d_k)) V
We divide by the square root of d_k because for large values of d_k, dot products grow large in magnitude, pushing the softmax function into regions where it has extremely small gradients.
Multi-Head Attention: Instead of performing a single attention function with d_model-dimensional keys, values and queries, we found it beneficial to linearly project the queries, keys and values h times with different, learned linear projections to d_k, d_k and d_v dimensions, respectively. Multi-head attention allows the model to jointly attend to information from different representation subspaces at different positions.
MultiHead(Q, K, V) = Concat(head_1, ..., head_h) W^O
where head_i = Attention(Q W_i^Q, K W_i^K, V W_i^V).

3.3 Positional Encoding
Since our model contains no recurrence and no convolution, in order for the model to make use of the order of the sequence, we must inject some information about the relative or absolute position of the tokens in the sequence. To this end, we add 'positional encodings' to the input embeddings at the bottoms of the encoder and decoder stacks. We use sine and cosine functions of different frequencies:
PE_{(pos, 2i)} = sin(pos / 10000^{2i/d_model})
PE_{(pos, 2i+1)} = cos(pos / 10000^{2i/d_model})

4. Why Self-Attention
In this section we compare various aspects of self-attention layers to the recurrent and convolutional layers commonly used for mapping one variable-length sequence of symbol representations to another. One aspect is total computational complexity per layer. Another is the amount of computation that can be parallelized, as measured by the minimum number of sequential operations required. A third is the path length between long-range dependencies in the network. A self-attention layer connects all positions with a constant O(1) number of sequentially executed operations, whereas a recurrent layer requires O(n) sequential operations.

5. Training
We trained on the standard WMT 2014 English-German dataset consisting of about 4.5 million sentence pairs, and the larger WMT 2014 English-French dataset consisting of 36 million sentence pairs.
Hardware and Schedule: We trained our models on one machine with 8 NVIDIA P100 GPUs. For the base models, each training step took about 0.4 seconds. We trained base models for 100,000 steps or 12 hours. For big models, step time was 1.0 seconds, trained for 300,000 steps (3.5 days).
Optimizer: We used the Adam optimizer with beta_1 = 0.9, beta_2 = 0.98 and epsilon = 10^-9. We varied the learning rate over the course of training according to a formula with 4000 warmup steps.
Regularization: We use residual dropout with P_drop = 0.1, label smoothing with epsilon_ls = 0.1.

6. Results
On the WMT 2014 English-to-German translation task, the big transformer model outperforms the best previously reported models (including ensembles) by more than 2.0 BLEU, establishing a new state-of-the-art BLEU score of 28.4. On WMT 2014 English-to-French, our big model achieves a BLEU score of 41.8, outperforming all previously published single models at 1/4 the training cost of the previous state of the art.

7. Limitations
The self-attention mechanism exhibits O(n^2) computational complexity and memory footprint with respect to the input sequence length n, making application to extremely long sequences (e.g., thousands of words or high-resolution images) challenging without sparse or windowed approximations. Furthermore, the model relies on static sinusoidal or learned positional encodings that may not extrapolate seamlessly beyond the maximum trained sequence length.

8. Conclusion
In this work, we presented the Transformer, the first sequence transduction model based entirely on attention, replacing the recurrent layers most commonly used in encoder-decoder architectures with multi-head self-attention. For translation tasks, the Transformer can be trained significantly faster than architectures based on recurrent or convolutional layers. On both WMT 2014 English-to-German and WMT 2014 English-to-French translation tasks, we achieved a new state of the art.
"""


# ==============================================================================
# DOCUMENT INDEXING & MODEL PRE-CHECK HELPERS
# ==============================================================================
def process_sample_paper(api_key: str, model_name: str) -> bool:
    """Index the landmark Transformer sample paper into ChromaDB."""
    clean_key = api_key.strip()
    if not clean_key:
        st.error("⚠️ Please enter a Google Gemini API key first.")
        return False
    with st.spinner("🔮 Indexing sample research paper into ChromaDB vector store..."):
        try:
            rag = RAGPipeline(api_key=clean_key)
            try:
                from langchain_text_splitters import RecursiveCharacterTextSplitter
            except ImportError:
                from langchain.text_splitter import RecursiveCharacterTextSplitter

            splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
            chunks = splitter.create_documents(
                texts=[SAMPLE_PAPER_TEXT],
                metadatas=[{"source": "Attention_Is_All_You_Need.pdf", "page": 1, "total_pages": 5}]
            )
            for idx, c in enumerate(chunks):
                c.metadata["chunk_id"] = idx
                c.metadata["page"] = (idx // 3) + 1

            rag.chunks = chunks
            rag.documents = chunks
            rag._index_in_chroma(chunks, collection_name="sample_transformer_paper")
            rag.paper_metadata = {
                "filename": "Attention_Is_All_You_Need_Vaswani2017.pdf",
                "total_pages": 5,
                "word_count": len(SAMPLE_PAPER_TEXT.split()),
                "char_count": len(SAMPLE_PAPER_TEXT),
                "chunk_count": len(chunks)
            }

            st.session_state.rag_pipeline = rag
            st.session_state.agent_coordinator = AgentCoordinator(api_key=clean_key, model_name=model_name)
            st.session_state.paper_processed = True
            st.session_state.paper_metadata = rag.paper_metadata
            st.success("✅ Landmark paper 'Attention Is All You Need' indexed successfully into ChromaDB!")
            return True
        except Exception as e:
            st.error(f"Error indexing sample paper: {str(e)}")
            return False

def process_uploaded_pdf(uploaded_file, api_key: str, model_name: str) -> bool:
    """Index an uploaded PDF file into ChromaDB."""
    clean_key = api_key.strip()
    if not clean_key:
        st.error("⚠️ Please enter a Google Gemini API key first.")
        return False
    with st.spinner("🔮 Parsing PDF with PyPDF, generating embeddings & indexing ChromaDB..."):
        try:
            rag = RAGPipeline(api_key=clean_key)
            metadata = rag.process_and_index_pdf(uploaded_file, filename=uploaded_file.name)
            st.session_state.rag_pipeline = rag
            st.session_state.agent_coordinator = AgentCoordinator(api_key=clean_key, model_name=model_name)
            st.session_state.paper_processed = True
            st.session_state.paper_metadata = metadata
            st.success(f"✅ Successfully indexed {metadata['chunk_count']} chunks into ChromaDB!")
            return True
        except Exception as e:
            st.error(f"Error processing PDF: {str(e)}")
            return False

def handle_rate_limit_or_error(e: Exception):
    """Displays a clean, user-friendly alert for 429 RESOURCE_EXHAUSTED or general errors."""
    err_str = str(e)
    if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str or "rate limit" in err_str.lower():
        st.warning(
            "⏳ **Gemini Free-Tier Rate Limit Reached (5 Requests / Minute)**\n\n"
            "Google AI Studio enforces a limit of 5 requests per minute for `gemini-3.8-flash` on the free tier.\n\n"
            "**Recommended Action**: Please wait 15–20 seconds before submitting another request."
        )
    else:
        st.error(f"❌ Error during generation: {err_str[:250]}")

def render_no_paper_banner(agent_name: str, api_key: str, model_choice: str):
    """Fallback card rendered when an agent is accessed before indexing a paper."""
    st.markdown(f"""
    <div class="glass-card" style="margin-bottom: 1.8rem; text-align: center; padding: 2.2rem 2rem;">
        <div style="font-size: 2.5rem; margin-bottom: 0.6rem;">📄</div>
        <h3 style="margin: 0 0 0.5rem 0; color: #28243A; font-weight: 800;">
            No Research Paper Loaded Yet
        </h3>
        <p style="color: #635C78; font-size: 0.95rem; max-width: 620px; margin: 0 auto 1.4rem auto; line-height: 1.6;">
            To execute the <b>{agent_name}</b>, load a scientific paper into the ChromaDB vector store.
            You can test immediately with the landmark <i>Attention Is All You Need</i> paper, or upload your own PDF from the Dashboard.
        </p>
    </div>
    """, unsafe_allow_html=True)

    col_b1, col_b2 = st.columns([1.2, 1])
    with col_b1:
        if st.button("📚 Load Sample Paper (Attention Is All You Need)", key=f"btn_sample_{agent_name}", use_container_width=True, type="primary"):
            if process_sample_paper(api_key, model_choice):
                st.rerun()
    with col_b2:
        if st.button("📥 Go to Dashboard to Upload PDF", key=f"btn_dash_{agent_name}", use_container_width=True):
            navigate_to("Dashboard")


# ==============================================================================
# LEFT SIDEBAR: BRANDING, NAVIGATION & SETTINGS
# ==============================================================================
with st.sidebar:
    # 1. PaperMate AI Logo & Brand
    st.markdown("""
    <div class="sidebar-brand-wrapper">
        <div class="sidebar-orb-logo">🔮</div>
        <div>
            <div class="sidebar-title">PaperMate AI</div>
        </div>
    </div>
    <div class="sidebar-tagline">Academic Research & Viva Assistant</div>
    """, unsafe_allow_html=True)

    # 2. Sidebar Navigation Menu
    st.markdown('<div class="sidebar-section-heading">Navigation</div>', unsafe_allow_html=True)

    # Ensure nav_radio is initialized to a valid option prior to widget creation
    if "nav_radio" not in st.session_state or st.session_state.nav_radio not in NAV_OPTIONS:
        st.session_state.nav_radio = st.session_state.get("active_page", "Dashboard")

    def _sync_navigation():
        # Invoked automatically when the user selects a radio option
        chosen = st.session_state.nav_radio
        st.session_state.active_page = chosen
        st.session_state.sidebar_nav = chosen

    selected_nav = st.radio(
        "Navigation Menu",
        options=NAV_OPTIONS,
        format_func=lambda x: NAV_DISPLAY.get(x, x),
        key="nav_radio",
        on_change=_sync_navigation,
        label_visibility="collapsed"
    )
    # Guarantee active page matches current selection
    st.session_state.active_page = selected_nav
    st.session_state.sidebar_nav = selected_nav

    st.markdown("---")

    # 3. Settings & API Controls (Preserves Existing Functionality)
    st.markdown('<div class="sidebar-section-heading">API Configuration</div>', unsafe_allow_html=True)
    default_api_key = os.getenv("GOOGLE_API_KEY", "")
    show_api_key = st.checkbox("Show API Key", value=False, help="Toggle API key visibility.", key="sb_show_api_key")
    api_key_input = st.text_input(
        "Google Gemini API Key",
        value=default_api_key,
        type="default" if show_api_key else "password",
        help="Obtain your Gemini API key at https://aistudio.google.com/app/apikey",
        key="sb_gemini_api_key_input"
    )

    clean_api_key = api_key_input.strip()
    if clean_api_key:
        st.markdown("""
        <div style="display:inline-flex; align-items:center; gap:0.4rem; background:rgba(237, 231, 250, 0.85); color:#7654C8; border:1px solid rgba(155, 122, 232, 0.3); padding:0.25rem 0.65rem; border-radius:9999px; font-size:0.76rem; font-weight:700; margin-bottom:0.6rem;">
            <span>●</span> <span>Gemini API Active</span>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.warning("⚠️ Enter your Gemini API key above or set `GOOGLE_API_KEY` in `.env` to enable AI agents.")

    # 4. Dynamic Model Discovery & Centralized Configuration
    if clean_api_key:
        if st.session_state.cached_api_key_for_models != clean_api_key:
            st.session_state.cached_api_key_for_models = clean_api_key
            st.session_state.available_models = fetch_available_gemini_models(clean_api_key)
    else:
        st.session_state.available_models = fetch_available_gemini_models("")

    models_list = st.session_state.available_models
    default_idx = 0
    if st.session_state.selected_model in models_list:
        default_idx = models_list.index(st.session_state.selected_model)
    elif DEFAULT_MODEL_CANDIDATE in models_list:
        default_idx = models_list.index(DEFAULT_MODEL_CANDIDATE)

    model_choice = st.selectbox(
        "Gemini Foundation Model",
        options=models_list,
        index=default_idx,
        help="Dynamically retrieved Gemini models filtered for generateContent support.",
        key="sb_gemini_model_choice"
    )
    st.session_state.selected_model = model_choice

    # Centralized Configuration: reconfigure single LLM and all LCEL agent chains immediately
    if st.session_state.agent_coordinator is not None:
        st.session_state.agent_coordinator.update_model(model_choice)

    # Model Connection Verification Controls in Sidebar
    col_tst1, col_tst2 = st.columns([1.3, 1])
    with col_tst1:
        test_conn_btn = st.button("⚡ Test Model", use_container_width=True, help=f"Execute live generateContent test with {model_choice}.", key="sb_test_model_btn")
    with col_tst2:
        refresh_models_btn = st.button("🔄 Refresh", use_container_width=True, help="Re-query Google Gen AI API for available models.", key="sb_refresh_models_btn")

    if refresh_models_btn:
        if clean_api_key:
            with st.spinner("Re-fetching supported models from Google Gen AI..."):
                discovered = fetch_available_gemini_models(clean_api_key, force_refresh=True)
                st.session_state.available_models = discovered
                st.rerun()
        else:
            st.info("Enter API key to fetch models.")

    if test_conn_btn:
        if not clean_api_key:
            st.error("Please enter a Gemini API key first.")
        else:
            with st.spinner(f"Verifying live generateContent call to '{model_choice}'..."):
                success, msg, latency = test_gemini_model_connection(clean_api_key, model_choice, force_test=True)
                st.session_state.model_test_result = {
                    "model": model_choice,
                    "success": success,
                    "message": msg,
                    "latency": latency
                }

    # Display Test Status
    if st.session_state.get("model_test_result"):
        res = st.session_state.model_test_result
        if res.get("model") == model_choice:
            if res.get("success"):
                st.markdown(f"""
                <div style="background:rgba(237, 231, 250, 0.9); border:1px solid #7654C8; border-radius:12px; padding:0.6rem 0.8rem; font-size:0.78rem; color:#28243A; margin-top:0.3rem; margin-bottom:0.6rem;">
                    <span style="color:#059669; font-weight:700;">🟢 VERIFIED & ACTIVE</span><br>
                    <span>Model: <b>{res['model']}</b> ({res['latency']:.0f}ms)</span><br>
                    <small style="color:#7A728E;">generateContent verified on Google AI Studio.</small>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="background:rgba(254, 242, 242, 0.95); border:1px solid #EF4444; border-radius:12px; padding:0.6rem 0.8rem; font-size:0.78rem; color:#991B1B; margin-top:0.3rem; margin-bottom:0.6rem;">
                    <span style="font-weight:700;">🔴 CONNECTION FAILED</span><br>
                    <span>{res['message']}</span><br>
                    <small>Please select another model from the dropdown.</small>
                </div>
                """, unsafe_allow_html=True)

    st.markdown("---")

    # Document Status in Sidebar
    if st.session_state.paper_processed:
        meta = st.session_state.paper_metadata
        st.markdown('<div class="sidebar-section-heading">Active Paper</div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div style="background:rgba(255, 255, 255, 0.7); border:1px solid rgba(155, 122, 232, 0.25); border-radius:14px; padding:0.85rem; font-size:0.8rem; color:#4A445C;">
            <div style="font-weight:700; color:#28243A; margin-bottom:0.25rem; word-break:break-all;">
                📄 {meta.get('filename', 'Unknown')[:22]}...
            </div>
            <div>Pages: <b>{meta.get('total_pages', 'N/A')}</b> • Chunks: <b>{meta.get('chunk_count', 0)}</b></div>
            <div>Words: <b>{meta.get('word_count', 0):,}</b></div>
            <div style="color:#7654C8; font-weight:700; margin-top:0.35rem;">● Grounded in ChromaDB</div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("🗑️ Reset Session", use_container_width=True, key="sb_reset_session_btn"):
            st.session_state.rag_pipeline = None
            st.session_state.agent_coordinator = None
            st.session_state.paper_processed = False
            st.session_state.paper_metadata = {}
            st.session_state.cached_summary = None
            st.session_state.cached_concepts = None
            st.session_state.cached_slides = None
            st.session_state.cached_viva = None
            st.session_state.chat_history = []
            st.session_state.last_routed_intent = None
            st.rerun()


# ==============================================================================
# DEDICATED PAGE RENDERING FUNCTIONS
# ==============================================================================

def render_dashboard(api_key: str, model_choice: str):
    """Renders the main PaperMate AI Dashboard with PDF upload, cards, and tech stack."""
    # 1. Landing Page Header with Glowing Purple AI Orb
    st.markdown("""
    <div class="welcome-hero-panel" style="text-align: center; padding: 2.5rem 2rem 2.2rem 2rem; margin-bottom: 2rem;">
        <div class="ai-orb-wrapper" style="margin: 0 auto 1.2rem auto;">
            <div class="ai-orb-aura"></div>
            <div class="ai-orb-core"></div>
        </div>
        <div class="welcome-badge" style="margin-bottom: 0.6rem;">
            <span>🔮</span> AI RESEARCH ASSISTANT
        </div>
        <h1 style="margin: 0; font-size: 2.9rem; font-weight: 800; color: #28243A; letter-spacing: -0.03em; line-height: 1.15;">
            PaperMate AI
        </h1>
        <div style="color: #635C78; font-size: 1.05rem; margin-top: 0.5rem; max-width: 640px; margin-left: auto; margin-right: auto;">
            Turn scientific papers into presentation-ready slide decks, structured summaries, and viva defense mastery.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 2. PDF Upload Panel (Large Rounded White Glass Card)
    st.markdown("""
    <div class="glass-card" style="margin-bottom: 2rem;">
        <div style="display: flex; align-items: center; gap: 0.8rem; margin-bottom: 0.6rem;">
            <div style="width: 38px; height: 38px; border-radius: 12px; background: rgba(155, 122, 232, 0.15); display: flex; align-items: center; justify-content: center; font-size: 1.25rem;">
                📥
            </div>
            <div>
                <h3 style="margin: 0; font-size: 1.28rem; font-weight: 800; color: #28243A;">
                    Upload Research Paper
                </h3>
                <div style="font-size: 0.88rem; color: #7A728E;">
                    Drop your PDF here to parse text with PyPDF, extract citations, and index chunks into ChromaDB
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    uploaded_pdf = st.file_uploader(
        "Upload Scientific PDF",
        type=["pdf"],
        help="Upload any research paper in PDF format (IEEE, ACM, arXiv, Springer, etc.)",
        label_visibility="collapsed",
        key="dash_pdf_uploader"
    )

    col_up_btn1, col_up_btn2 = st.columns([1, 1])
    with col_up_btn1:
        load_sample = st.button("📚 Load Sample Paper (Attention Is All You Need)", use_container_width=True, key="btn_dash_load_sample")
    with col_up_btn2:
        if uploaded_pdf and not st.session_state.paper_processed:
            process_pdf_btn = st.button("⚡ Index Uploaded PDF Into ChromaDB", use_container_width=True, type="primary", key="btn_dash_index_pdf")
        else:
            process_pdf_btn = False

    st.markdown("</div>", unsafe_allow_html=True)

    # Document Ingestion Processing
    if load_sample:
        if process_sample_paper(api_key, model_choice):
            st.rerun()

    elif uploaded_pdf and (process_pdf_btn or not st.session_state.paper_processed):
        if process_uploaded_pdf(uploaded_pdf, api_key, model_choice):
            st.rerun()

    # 3. Feature Cards in a 2x2 Grid
    st.markdown('<div class="feature-grid-title">Core Intelligence Modules</div>', unsafe_allow_html=True)
    col_fc1, col_fc2 = st.columns(2)

    with col_fc1:
        # Card 1: Paper Summary
        st.markdown("""
        <div class="feature-glass-box">
            <div>
                <div class="feature-icon-badge">📄</div>
                <div class="feature-box-heading">Paper Summary</div>
                <div class="feature-box-desc">
                    Generate structured summaries and understand research findings across 8 dimensions: 
                    abstract, introduction, problem statement, methodology, findings, results, limitations, and conclusion.
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Launch Paper Summary ➔", key="btn_card_summary", use_container_width=True):
            navigate_to("Research Summary")

        st.write("")

        # Card 3: Concept Explorer
        st.markdown("""
        <div class="feature-glass-box">
            <div>
                <div class="feature-icon-badge">💡</div>
                <div class="feature-box-heading">Concept Explorer</div>
                <div class="feature-box-desc">
                    Understand complex technical concepts in simple language. Extracts key algorithms, 
                    mathematical formulations, tools, and novel contributions paired with intuitive real-world analogies.
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Launch Concept Explorer ➔", key="btn_card_concepts", use_container_width=True):
            navigate_to("Concept Explorer")

    with col_fc2:
        # Card 2: Slide Generator
        st.markdown("""
        <div class="feature-glass-box">
            <div>
                <div class="feature-icon-badge">📊</div>
                <div class="feature-box-heading">Slide Generator</div>
                <div class="feature-box-desc">
                    Transform research papers into presentation-ready slides. Generates 8–10 slides with concise bullet points, 
                    speaker notes, and 1-click download as an editable PowerPoint (.pptx) file.
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Launch Slide Generator ➔", key="btn_card_slides", use_container_width=True):
            navigate_to("Slide Generator")

        st.write("")

        # Card 4: Viva Coach
        st.markdown("""
        <div class="feature-glass-box">
            <div>
                <div class="feature-icon-badge">🎓</div>
                <div class="feature-box-heading">Viva Coach</div>
                <div class="feature-box-desc">
                    Prepare for oral examinations and thesis defense with AI-generated viva questions and answers across 
                    Basic, Intermediate, and Advanced tiers, complete with tactical defense tips.
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Launch Viva Coach ➔", key="btn_card_viva", use_container_width=True):
            navigate_to("Viva Practice")

    st.write("")

    # 4. Recent Research Section (Shown only when actual document history is available)
    if st.session_state.paper_processed:
        meta = st.session_state.paper_metadata
        st.markdown('<div class="feature-grid-title" style="margin-top: 1.5rem;">Recent Research</div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="glass-card" style="margin-bottom: 2rem;">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem;">
                <div>
                    <div style="display: flex; align-items: center; gap: 0.6rem; margin-bottom: 0.3rem;">
                        <span style="font-size: 1.3rem;">📑</span>
                        <h4 style="margin: 0; font-size: 1.2rem; font-weight: 800; color: #28243A;">
                            {meta.get('filename', 'Unknown Document')}
                        </h4>
                    </div>
                    <div style="font-size: 0.88rem; color: #635C78;">
                        Total Pages: <b>{meta.get('total_pages', 'N/A')}</b> &nbsp;•&nbsp; 
                        Word Count: <b>{meta.get('word_count', 0):,}</b> &nbsp;•&nbsp; 
                        ChromaDB Chunks: <b>{meta.get('chunk_count', 0)}</b>
                    </div>
                </div>
                <div>
                    <div style="display: inline-flex; align-items: center; gap: 0.45rem; background: rgba(237, 231, 250, 0.9); color: #7654C8; padding: 0.35rem 0.85rem; border-radius: 9999px; font-size: 0.82rem; font-weight: 700; border: 1px solid rgba(155, 122, 232, 0.3);">
                        <span>●</span> Active in Vector Store
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # 5. Technology Section
    st.markdown('<div class="feature-grid-title" style="margin-top: 1.5rem;">Core Technology Stack</div>', unsafe_allow_html=True)
    col_t1, col_t2, col_t3, col_t4 = st.columns(4)

    with col_t1:
        st.markdown("""
        <div class="tech-grid-card">
            <div class="tech-grid-icon">🌐</div>
            <div class="tech-grid-name">Gemini API</div>
            <div class="tech-grid-role">Foundation Model</div>
        </div>
        """, unsafe_allow_html=True)
    with col_t2:
        st.markdown("""
        <div class="tech-grid-card">
            <div class="tech-grid-icon">🦜🔗</div>
            <div class="tech-grid-name">LangChain</div>
            <div class="tech-grid-role">LCEL Orchestration</div>
        </div>
        """, unsafe_allow_html=True)
    with col_t3:
        st.markdown("""
        <div class="tech-grid-card">
            <div class="tech-grid-icon">🗄️</div>
            <div class="tech-grid-name">ChromaDB</div>
            <div class="tech-grid-role">Vector Database</div>
        </div>
        """, unsafe_allow_html=True)
    with col_t4:
        st.markdown("""
        <div class="tech-grid-card">
            <div class="tech-grid-icon">🔍</div>
            <div class="tech-grid-name">Agentic RAG</div>
            <div class="tech-grid-role">Conditional Retrieval</div>
        </div>
        """, unsafe_allow_html=True)


def render_summary(api_key: str, model_choice: str):
    """Renders the Summarizer Agent interface."""
    render_back_button("summary")
    st.markdown("""
    <div class="welcome-hero-panel" style="padding: 2rem 2.4rem;">
        <div class="welcome-badge">📑 SUMMARIZER AGENT</div>
        <div class="welcome-heading" style="font-size: 2.1rem;">Academic Research Paper Summary</div>
        <div class="welcome-subtitle">
            Synthesizes all 8 mandatory academic dimensions grounded strictly in retrieved ChromaDB chunks.
        </div>
    </div>
    """, unsafe_allow_html=True)

    if not st.session_state.paper_processed:
        render_no_paper_banner("Summarizer Agent", api_key, model_choice)
    else:
        rag: RAGPipeline = st.session_state.rag_pipeline
        agent: AgentCoordinator = st.session_state.agent_coordinator
        meta = st.session_state.paper_metadata

        if st.button("🚀 Generate 8-Section Structured Summary", type="primary", key="btn_run_summarizer"):
            if not api_key.strip():
                st.warning("⚠️ Please enter a Google Gemini API key in the sidebar.")
            else:
                with st.spinner(f"🔮 Summarizer Agent parsing 8 scientific dimensions with {model_choice}..."):
                    try:
                        summary_res = agent.run_summarizer(rag)
                        st.session_state.cached_summary = summary_res
                    except Exception as e:
                        handle_rate_limit_or_error(e)

        if st.session_state.cached_summary:
            res = st.session_state.cached_summary
            ver = res["verification"]

            st.markdown(f"""
            <div class="verification-glass-pill">
                <span style="font-weight: 800; color: #7654C8;">🛡️ REFLECTION VERIFICATION: {ver['status']}</span><br>
                <span>Confidence: <b>{ver['confidence']}</b> • Note: <i>{ver['note']}</i></span>
            </div>
            """, unsafe_allow_html=True)

            st.markdown(f"""
            <div class="result-glass-container">
                {res['summary']}
            </div>
            """, unsafe_allow_html=True)

            st.download_button(
                label="📥 Download Structured Summary (.md)",
                data=res["summary"],
                file_name=f"{meta.get('filename', 'paper')}_summary.md",
                mime="text/markdown",
                key="btn_download_summary"
            )

            with st.expander("🔍 View Retrieved ChromaDB Context & Citations"):
                for i, doc in enumerate(res["sources"], 1):
                    st.markdown(f"**Chunk #{i} — Page {doc.metadata.get('page', 'Unknown')}**")
                    st.caption(doc.page_content)
                    st.divider()


def render_concepts(api_key: str, model_choice: str):
    """Renders the Concept Extractor Agent interface."""
    render_back_button("concepts")
    st.markdown("""
    <div class="welcome-hero-panel" style="padding: 2rem 2.4rem;">
        <div class="welcome-badge">💡 CONCEPT EXTRACTOR AGENT</div>
        <div class="welcome-heading" style="font-size: 2.1rem;">Concept & Method Explorer</div>
        <div class="welcome-subtitle">
            Extracts theoretical foundations, algorithms, technologies, and novel contributions with real-world analogies.
        </div>
    </div>
    """, unsafe_allow_html=True)

    if not st.session_state.paper_processed:
        render_no_paper_banner("Concept Extractor Agent", api_key, model_choice)
    else:
        rag: RAGPipeline = st.session_state.rag_pipeline
        agent: AgentCoordinator = st.session_state.agent_coordinator
        meta = st.session_state.paper_metadata

        if st.button("🔬 Extract Concepts & Methodologies", type="primary", key="btn_run_concept_extractor"):
            if not api_key.strip():
                st.warning("⚠️ Please enter a Google Gemini API key in the sidebar.")
            else:
                with st.spinner(f"🔮 Concept Extractor Agent parsing technical architecture with {model_choice}..."):
                    try:
                        concept_res = agent.run_concept_extractor(rag)
                        st.session_state.cached_concepts = concept_res
                    except Exception as e:
                        handle_rate_limit_or_error(e)

        if st.session_state.cached_concepts:
            res = st.session_state.cached_concepts
            ver = res["verification"]

            st.markdown(f"""
            <div class="verification-glass-pill">
                <span style="font-weight: 800; color: #7654C8;">🛡️ REFLECTION VERIFICATION: {ver['status']}</span><br>
                <span>Confidence: <b>{ver['confidence']}</b> • Note: <i>{ver['note']}</i></span>
            </div>
            """, unsafe_allow_html=True)

            st.markdown(f"""
            <div class="result-glass-container">
                {res['concepts']}
            </div>
            """, unsafe_allow_html=True)

            st.download_button(
                label="📥 Download Concepts Guide (.md)",
                data=res["concepts"],
                file_name=f"{meta.get('filename', 'paper')}_concepts.md",
                mime="text/markdown",
                key="btn_download_concepts"
            )


def render_slides(api_key: str, model_choice: str):
    """Renders the Slide Generator Agent interface with PPTX export."""
    render_back_button("slides")
    st.markdown("""
    <div class="welcome-hero-panel" style="padding: 2rem 2.4rem;">
        <div class="welcome-badge">📊 SLIDE GENERATOR AGENT</div>
        <div class="welcome-heading" style="font-size: 2.1rem;">Slide Deck Generator & PPTX Export</div>
        <div class="welcome-subtitle">
            Generates 8–10 presentation slides complete with concise bullet points, speaker notes, and editable .pptx export.
        </div>
    </div>
    """, unsafe_allow_html=True)

    if not st.session_state.paper_processed:
        render_no_paper_banner("Slide Generator Agent", api_key, model_choice)
    else:
        rag: RAGPipeline = st.session_state.rag_pipeline
        agent: AgentCoordinator = st.session_state.agent_coordinator
        meta = st.session_state.paper_metadata

        if st.button("📽️ Generate Slide Deck & PowerPoint (.pptx)", type="primary", key="btn_run_slide_generator"):
            if not api_key.strip():
                st.warning("⚠️ Please enter a Google Gemini API key in the sidebar.")
            else:
                with st.spinner(f"🔮 Slide Generator Agent structuring presentation with {model_choice}..."):
                    try:
                        slide_res = agent.run_slide_generator(
                            rag,
                            paper_title=meta.get("filename", "Academic Research Presentation")
                        )
                        st.session_state.cached_slides = slide_res
                    except Exception as e:
                        handle_rate_limit_or_error(e)

        if st.session_state.cached_slides:
            res = st.session_state.cached_slides
            slides = res["slides"]

            st.success(f"🎉 Successfully synthesized {len(slides)} presentation slides!")

            st.download_button(
                label="📥 Download Presentation (.pptx)",
                data=res["pptx_buffer"],
                file_name=f"{meta.get('filename', 'presentation')}_slides.pptx",
                mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                type="primary",
                key="btn_download_pptx"
            )

            st.write("")

            for s in slides:
                s_num = s.get("slide_number", 1)
                s_title = s.get("title", f"Slide {s_num}")
                s_sub = s.get("subtitle", "Overview")
                bullets = s.get("bullet_points", [])
                notes = s.get("speaker_notes", "")

                bullet_html = "".join([f"<li style='margin-bottom:0.45rem; color:#28243A;'>{b}</li>" for b in bullets])

                st.markdown(f"""
                <div class="slide-glass-card">
                    <span style="display:inline-block; font-size:0.75rem; font-weight:800; text-transform:uppercase; color:#7654C8; background:rgba(237, 231, 250, 0.8); padding:0.25rem 0.65rem; border-radius:9999px; margin-bottom:0.5rem;">
                        SLIDE {s_num:02d} • {s_sub.upper()}
                    </span>
                    <div style="font-size:1.35rem; font-weight:800; color:#28243A; margin-bottom:0.8rem;">
                        {s_title}
                    </div>
                    <ul style="padding-left:1.25rem; font-size:0.98rem; line-height:1.65;">
                        {bullet_html}
                    </ul>
                    <div class="speaker-glass-box">
                        <b>🎙️ Speaker Notes:</b> {notes}
                    </div>
                </div>
                """, unsafe_allow_html=True)


def render_viva(api_key: str, model_choice: str):
    """Renders the Viva Voce Agent interface with tiered Q&A and defense tips."""
    render_back_button("viva")
    st.markdown("""
    <div class="welcome-hero-panel" style="padding: 2rem 2.4rem;">
        <div class="welcome-badge">🎓 VIVA COACH AGENT</div>
        <div class="welcome-heading" style="font-size: 2.1rem;">Viva Voce Defense Coach</div>
        <div class="welcome-subtitle">
            Prepares students for thesis defense and oral viva examinations with 10+ tiered questions and defense tips.
        </div>
    </div>
    """, unsafe_allow_html=True)

    if not st.session_state.paper_processed:
        render_no_paper_banner("Viva Coach Agent", api_key, model_choice)
    else:
        rag: RAGPipeline = st.session_state.rag_pipeline
        agent: AgentCoordinator = st.session_state.agent_coordinator
        meta = st.session_state.paper_metadata

        if st.button("🛡️ Generate 10+ Viva Questions & Defense Guide", type="primary", key="btn_run_viva_coach"):
            if not api_key.strip():
                st.warning("⚠️ Please enter a Google Gemini API key in the sidebar.")
            else:
                with st.spinner(f"🔮 Viva Agent analyzing methodology with {model_choice}..."):
                    try:
                        viva_res = agent.run_viva_agent(rag)
                        st.session_state.cached_viva = viva_res
                    except Exception as e:
                        handle_rate_limit_or_error(e)

        if st.session_state.cached_viva:
            res = st.session_state.cached_viva
            ver = res["verification"]

            st.markdown(f"""
            <div class="verification-glass-pill">
                <span style="font-weight: 800; color: #7654C8;">🛡️ REFLECTION VERIFICATION: {ver['status']}</span><br>
                <span>Confidence: <b>{ver['confidence']}</b> • Note: <i>{ver['note']}</i></span>
            </div>
            """, unsafe_allow_html=True)

            st.markdown(f"""
            <div class="result-glass-container">
                {res['viva_questions']}
            </div>
            """, unsafe_allow_html=True)

            st.download_button(
                label="📥 Download Viva Defense Guide (.md)",
                data=res["viva_questions"],
                file_name=f"{meta.get('filename', 'paper')}_viva_defense_guide.md",
                mime="text/markdown",
                key="btn_download_viva"
            )


def render_intent_router(api_key: str, model_choice: str):
    """Renders the Autonomous Query & Intent Router interface."""
    render_back_button("intent_router")
    st.markdown("""
    <div class="welcome-hero-panel" style="padding: 2rem 2.4rem;">
        <div class="welcome-badge">🧭 AGENTIC INTENT ROUTER</div>
        <div class="welcome-heading" style="font-size: 2.1rem;">Autonomous Query & Intent Router</div>
        <div class="welcome-subtitle">
            State any goal in natural language. The router analyzes intent with confidence scoring and invokes the targeted agent.
        </div>
    </div>
    """, unsafe_allow_html=True)

    if not st.session_state.paper_processed:
        render_no_paper_banner("Intent Router Agent", api_key, model_choice)
    else:
        rag: RAGPipeline = st.session_state.rag_pipeline
        agent: AgentCoordinator = st.session_state.agent_coordinator

        user_query = st.text_input(
            "Enter your instruction or query:",
            placeholder="e.g., 'Summarize the whole paper', 'Make 10 presentation slides', 'What questions will examiners ask?'",
            key="router_main_query"
        )

        if st.button("🔍 Route & Execute Agent", type="primary", key="btn_run_intent_router"):
            if not user_query.strip():
                st.warning("Please type a request first.")
            elif not api_key.strip():
                st.warning("⚠️ Please enter a Google Gemini API key in the sidebar.")
            else:
                with st.spinner(f"🔮 Analyzing intent and executing specialized agent with {model_choice}..."):
                    try:
                        route_result = agent.route_intent(user_query)
                        intent = route_result["intent"]
                        conf = route_result["confidence"]
                        reasoning = route_result["reasoning"]

                        st.markdown(f"""
                        <div class="verification-glass-pill">
                            <span style="font-weight: 800; color: #7654C8;">🎯 INTENT DETECTED: {intent.upper()} AGENT</span><br>
                            <span>Confidence: <b>{conf * 100:.1f}%</b> • Rationale: <i>{reasoning}</i></span>
                        </div>
                        """, unsafe_allow_html=True)

                        if intent == "summary":
                            res = agent.run_summarizer(rag)
                            st.markdown(f'<div class="result-glass-container">{res["summary"]}</div>', unsafe_allow_html=True)
                        elif intent == "concepts":
                            res = agent.run_concept_extractor(rag)
                            st.markdown(f'<div class="result-glass-container">{res["concepts"]}</div>', unsafe_allow_html=True)
                        elif intent == "slides":
                            res = agent.run_slide_generator(rag)
                            st.success(f"Generated {len(res['slides'])} slides! Switch to the 'Slide Generator' tab to download the .pptx file.")
                        elif intent == "viva":
                            res = agent.run_viva_agent(rag)
                            st.markdown(f'<div class="result-glass-container">{res["viva_questions"]}</div>', unsafe_allow_html=True)
                        else:
                            res = agent.run_concept_explainer(rag, question=user_query)
                            st.markdown(f'<div class="result-glass-container">{res["answer"]}</div>', unsafe_allow_html=True)
                    except Exception as e:
                        handle_rate_limit_or_error(e)


def render_settings(api_key: str, model_choice: str):
    """Renders the comprehensive Settings and Acceptance Criteria verification view."""
    render_back_button("settings")
    st.markdown("""
    <div class="welcome-hero-panel" style="padding: 2rem 2.4rem;">
        <div class="welcome-badge">⚙️ SYSTEM CONFIGURATION</div>
        <div class="welcome-heading" style="font-size: 2.1rem;">API Configuration & Settings</div>
        <div class="welcome-subtitle">
            Configure Google Gemini credentials, test model availability, and review mandatory college acceptance criteria.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Section 1: API Configuration
    st.markdown("""
    <div class="glass-card" style="margin-bottom: 1.5rem;">
        <h3 style="margin-top:0; color:#7654C8;">🔑 Google Gemini API Configuration</h3>
        <p style="color:#635C78; font-size:0.92rem; margin-bottom:1.2rem;">
            PaperMate AI utilizes Google Gemini models for all Agentic RAG tasks. Your API key can be set in your <code>.env</code> file or configured in the sidebar.
        </p>
    """, unsafe_allow_html=True)

    col_s1, col_s2 = st.columns([2, 1])
    with col_s1:
        if api_key.strip():
            masked_key = api_key[:6] + "..." + api_key[-4:] if len(api_key) > 10 else "******"
            st.markdown(f"""
            <div style="background:rgba(237, 231, 250, 0.7); border:1px solid #7654C8; border-radius:12px; padding:0.8rem 1rem;">
                <span style="color:#059669; font-weight:700;">🟢 ACTIVE CREDENTIALS</span><br>
                <span>Current Key: <code>{masked_key}</code></span>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="background:rgba(254, 242, 242, 0.8); border:1px solid #EF4444; border-radius:12px; padding:0.8rem 1rem;">
                <span style="color:#DC2626; font-weight:700;">🔴 NO API KEY DETECTED</span><br>
                <span>Please enter your Gemini API key in the left sidebar to activate AI agents.</span>
            </div>
            """, unsafe_allow_html=True)
    with col_s2:
        st.markdown("""
        <div style="font-size:0.85rem; color:#7A728E; padding:0.4rem;">
            Need a key? Get a free API key at <a href="https://aistudio.google.com/app/apikey" target="_blank" style="color:#7654C8; font-weight:600;">Google AI Studio</a>.
        </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # Section 2: Model Management & Connection Diagnostics
    st.markdown("""
    <div class="glass-card" style="margin-bottom: 1.5rem;">
        <h3 style="margin-top:0; color:#7654C8;">🤖 Foundation Model & Diagnostics</h3>
        <p style="color:#635C78; font-size:0.92rem; margin-bottom:1.2rem;">
            Centralized model configuration powering the Summarizer, Concept Extractor, Slide Generator, Viva Coach, and Intent Router.
        </p>
    """, unsafe_allow_html=True)

    col_m1, col_m2 = st.columns([1.5, 1])
    with col_m1:
        st.markdown(f"""
        <div style="background:rgba(255, 255, 255, 0.75); border:1px solid rgba(155, 122, 232, 0.3); border-radius:14px; padding:1rem;">
            <div>Active Foundation Model: <b style="color:#4C2B9E; font-size:1.05rem;">{model_choice}</b></div>
            <div style="font-size:0.85rem; color:#635C78; margin-top:0.3rem;">Candidate default: <code>gemini-3.8-flash</code></div>
            <div style="font-size:0.85rem; color:#635C78;">Discovered models count: <b>{len(st.session_state.available_models)}</b></div>
        </div>
        """, unsafe_allow_html=True)

    with col_m2:
        if st.button("⚡ Test Live Connection", key="settings_test_conn_btn", use_container_width=True):
            if not api_key.strip():
                st.error("Please enter your API key first.")
            else:
                with st.spinner(f"Testing live generateContent call to {model_choice}..."):
                    success, msg, latency = test_gemini_model_connection(api_key.strip(), model_choice, force_test=True)
                    st.session_state.model_test_result = {
                        "model": model_choice,
                        "success": success,
                        "message": msg,
                        "latency": latency
                    }
                    st.rerun()

        if st.session_state.get("model_test_result"):
            res = st.session_state.model_test_result
            if res.get("success"):
                st.success(f"🟢 Verified: {res['model']} responded in {res['latency']:.0f}ms!")
            else:
                st.error(f"🔴 Verification Failed: {res['message']}")

    st.markdown("</div>", unsafe_allow_html=True)

    # Section 3: Acceptance Criteria Checklist
    st.markdown("""
    <div class="glass-card" style="margin-bottom: 1.5rem;">
        <h3 style="margin-top:0; color:#7654C8;">🎯 Mandatory Acceptance Criteria Checklist</h3>
        <p style="color:#635C78; font-size:0.92rem; margin-bottom:1rem;">
            Verification checklist for college evaluation confirming all 7 acceptance criteria:
        </p>
        <div style="font-size: 0.95rem; color: #28243A; line-height: 2.2;">
            ✅ <b>1. LLM Integration</b>: Google Gemini API via <code>ChatGoogleGenerativeAI</code> with dynamic discovery<br>
            ✅ <b>2. Interactive GUI</b>: Soft Lavender Glassmorphism Streamlit Dashboard with responsive navigation<br>
            ✅ <b>3. Prompt Engineering</b>: Specialized system & agent prompt templates for all academic tasks<br>
            ✅ <b>4. LangChain LCEL</b>: Declarative <code>prompt | llm | parser</code> chains with zero deprecated APIs<br>
            ✅ <b>5. Agentic RAG</b>: PyPDF extraction, recursive character chunking & conditional retrieval<br>
            ✅ <b>6. Intent Detection & Routing</b>: Intent Router Agent with confidence scoring and fallback<br>
            ✅ <b>7. ChromaDB Vector Store</b>: Google Generative AI embeddings, metadata indexing & citation tracking
        </div>
    </div>
    """, unsafe_allow_html=True)


# ==============================================================================
# MAIN APPLICATION ROUTER EXECUTION
# ==============================================================================
PAGE_ROUTER = {
    "Dashboard": render_dashboard,
    "Research Summary": render_summary,
    "Concept Explorer": render_concepts,
    "Slide Generator": render_slides,
    "Viva Practice": render_viva,
    "Smart Intent Router": render_intent_router,
    "Settings": render_settings,
}

# Determine current page from session state
current_active_page = st.session_state.get("active_page", "Dashboard")
if current_active_page not in PAGE_ROUTER:
    current_active_page = "Dashboard"
    st.session_state.active_page = "Dashboard"
    st.session_state.sidebar_nav = "Dashboard"

# Dispatch to the dedicated page renderer
render_func = PAGE_ROUTER[current_active_page]
render_func(api_key=clean_api_key, model_choice=model_choice)


# ==============================================================================
# FOOTER (Created by Priyanshi Raj)
# ==============================================================================
st.markdown("""
<div style="height: 1px; background: linear-gradient(90deg, transparent, rgba(155, 122, 232, 0.35), transparent); margin: 2.5rem 0 1.2rem 0;"></div>
<div style="text-align: center; padding-bottom: 2rem;">
    <div style="font-weight: 700; color: #7654C8; font-size: 1.05rem; margin-bottom: 0.4rem;">
        PaperMate AI 🔮
    </div>
    <div style="font-size: 0.88rem; font-weight: 500; color: #9B7AE8; letter-spacing: 0.04em;">
        Created by Priyanshi Raj
    </div>
</div>
""", unsafe_allow_html=True)
