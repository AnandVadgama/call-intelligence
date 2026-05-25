import os
import time
import json
import tempfile
import streamlit as st
from dotenv import load_dotenv

# Load default environment variables
load_dotenv()

# Import our models
from models import GeminiModel, WhisperModel

# --- PAGE CONFIGURATION & THEME ---
st.set_page_config(
    page_title="Payment Intelligence Engine",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject Custom Google Fonts and CSS for premium Glassmorphism Dark Mode
st.markdown("""
<style>
/* Font Imports */
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap');

/* Global Font Override */
html, body, [class*="css"], .stApp {
    font-family: 'Plus Jakarta Sans', sans-serif;
}

/* Glowing Title */
.title-gradient {
    background: linear-gradient(135deg, #c084fc 0%, #6366f1 50%, #38bdf8 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-family: 'Outfit', sans-serif;
    font-weight: 800;
    font-size: 2.8rem;
    margin-bottom: 2px;
    letter-spacing: -0.02em;
}

.subtitle-custom {
    color: #94a3b8;
    font-size: 1.1rem;
    font-weight: 400;
    margin-bottom: 30px;
}

/* Glassmorphism Cards */
.glass-card {
    background: rgba(30, 41, 59, 0.45);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 20px;
    padding: 28px;
    margin-bottom: 24px;
    box-shadow: 0 10px 30px 0 rgba(0, 0, 0, 0.25);
}

/* Badge Color Codes */
.badge {
    display: inline-block;
    padding: 8px 18px;
    border-radius: 30px;
    font-weight: 700;
    font-family: 'Outfit', sans-serif;
    letter-spacing: 0.05em;
    font-size: 0.95rem;
    text-align: center;
    text-transform: uppercase;
}

.badge-ptp {
    background: rgba(16, 185, 129, 0.15);
    color: #10b981;
    border: 1px solid rgba(16, 185, 129, 0.3);
    box-shadow: 0 0 15px rgba(16, 185, 129, 0.15);
}

.badge-rtp {
    background: rgba(239, 68, 68, 0.15);
    color: #ef4444;
    border: 1px solid rgba(239, 68, 68, 0.3);
    box-shadow: 0 0 15px rgba(239, 68, 68, 0.15);
}

.badge-exc {
    background: rgba(245, 158, 11, 0.15);
    color: #f59e0b;
    border: 1px solid rgba(245, 158, 11, 0.3);
    box-shadow: 0 0 15px rgba(245, 158, 11, 0.15);
}

.badge-ppc {
    background: rgba(59, 130, 246, 0.15);
    color: #3b82f6;
    border: 1px solid rgba(59, 130, 246, 0.3);
    box-shadow: 0 0 15px rgba(59, 130, 246, 0.15);
}

.badge-nr {
    background: rgba(107, 114, 128, 0.15);
    color: #9ca3af;
    border: 1px solid rgba(107, 114, 128, 0.3);
    box-shadow: 0 0 15px rgba(107, 114, 128, 0.15);
}

/* Detail Call Cards */
.detail-card {
    border-left: 5px solid;
    padding: 18px 24px;
    border-radius: 4px 16px 16px 4px;
    background: rgba(15, 23, 42, 0.25);
    margin-bottom: 20px;
}

.detail-card-ptp { border-left-color: #10b981; }
.detail-card-rtp { border-left-color: #ef4444; }
.detail-card-exc { border-left-color: #f59e0b; }
.detail-card-ppc { border-left-color: #3b82f6; }
.detail-card-nr { border-left-color: #9ca3af; }

.section-label {
    font-size: 0.75rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: #64748b;
    margin-bottom: 8px;
}

.quote-text {
    font-style: italic;
    color: #e2e8f0;
    font-size: 1.05rem;
    line-height: 1.6;
}

.summary-text {
    color: #cbd5e1;
    font-size: 1rem;
    line-height: 1.6;
}

/* Metrics and latency display */
.metric-box {
    text-align: center;
    padding: 12px;
    border-radius: 12px;
    background: rgba(30, 41, 59, 0.3);
    border: 1px solid rgba(255, 255, 255, 0.05);
}

.metric-num {
    font-size: 1.5rem;
    font-weight: 700;
    font-family: 'Outfit', sans-serif;
    color: #e2e8f0;
}

/* Glowing analyze button styles */
div.stButton > button {
    background: linear-gradient(135deg, #8b5cf6 0%, #3b82f6 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 10px 28px !important;
    font-weight: 600 !important;
    font-family: 'Outfit', sans-serif !important;
    box-shadow: 0 4px 15px rgba(59, 130, 246, 0.3) !important;
    transition: all 0.3s ease !important;
    width: 100% !important;
}

div.stButton > button:hover {
    box-shadow: 0 6px 20px rgba(139, 92, 246, 0.5) !important;
    transform: translateY(-2px) !important;
}

/* Clean sidebar styling */
[data-testid="stSidebar"] {
    background-color: #0f172a;
    border-right: 1px solid rgba(255, 255, 255, 0.08);
}
</style>
""", unsafe_allow_html=True)

# --- DEMO CALL PRESETS DATA ---
DEMO_PRESETS = {
    "📞 Sabarmati Gas - Bill Dispute (Gujarati)": {
        "file_name": "demo1.mp3",
        "result": {
            "transcript": "लिख दिन प्यारेच दिर्भा वाला बाजे से आत्र रिपारेच दिर्भा में ज्ञाना पारेच दिर्भा वाला वाला क्या लोको मने हैरेस करेचे मैं चेला डौट बचती तमारू साबरमती वालू बील जमारू तमारू जे मीटर वाई ऐसी बंद कराई दितू चे तो भी तमे मात्रा फोन करे जाओ चो के बैन बील बाखी चे आतो बाखी चे नहीं पास नी, क्लिकीचे मारी गाफ मेणान बंद आपको चीनेज डाल दिया स्कूल ना मारी गाफी तम्हाम पान एक नौरे घावलान ना पावश्यक रावेज स्कूल्पर ना उठाना देते हैं। तो देते वक़ते मास्क मीटर बंद करेच तर ये लोपई सूर्ण शासी चेर खालेच चेर जेवं दिया चेर जेवं देशा जेवं अबों अच्छा बगेच ता बुकर मास्क मास्क माला हैस करेच चेर पारिद जाओ",
            "language": "Gujarati",
            "code": "RTP",
            "label": "Refuse to Pay",
            "confidence": 95,
            "key_phrase": "तमारू साबरमती वालू बील जमारू तमारू जे मीटर वाई ऐसी बंद कराई दितू चे तो भी तमे मात्रा फोन करे जाओ चो",
            "summary": "Customer is highly frustrated and disputes the payment request, claiming that their Sabarmati Gas bill is already settled. They state that the meter was even disconnected but they still receive repeated collection calls, which they describe as harassment."
        }
    },
    "📞 Payment Request - Online Transfer (Hindi)": {
        "file_name": "demo2.mp3",
        "result": {
            "transcript": "एक बीच वो एलो हेलो है जाना आधार इतनी ओर से बोल रही हूं आवस वॉट ज़राके पास से यह क्या हुआ क्या हुआ केस नती लेता तो आप किसी को देके ओल्लाइन करवा दीजिए हाँ हाँ हाँ",
            "language": "Hindi",
            "code": "PPC",
            "label": "Partial Pay Commitment",
            "confidence": 88,
            "key_phrase": "आप किसी को देके ओल्लाइन करवा दीजिए",
            "summary": "Short conversational exchange where the speaker mentions that if cash/case is not accepted, someone should be asked to make the payment online."
        }
    },
    "📞 Sabarmati Gas - Overdue Promise (Urdu/Hindi)": {
        "file_name": "demo3.mp3",
        "result": {
            "transcript": "مرحبا بھاویت بھائی ہاں کون سابر مٹی گیس سے بات کریں ریپائمنٹ ہو گئے سابر مٹی گیس کا بات کریں بات کریں بات کریں چیک کرنا کوئی گا سر پیمنٹ کروا دیجئے نا چار مہینہ ہوگی ابھی تک پیمنٹ نہیں ہوا ہے آپ کا نہیں ہوا ہے کتنا ہے نہیں تیس سو سترہ روپے ہیں کتنا تیس سو سترہ ہاں اور آج لازم دیتے ہیں آپ کو پھر جارہے سی چمتے ہیں ہاں تو دو پیر میں دو پیر में करवा दीजिए ठीक है",
            "language": "Urdu",
            "code": "PTP",
            "label": "Promise to Pay",
            "confidence": 97,
            "key_phrase": "آج لازم دیتے ہیں آپ کو",
            "summary": "Agent calls regarding a 4-month outstanding Sabarmati Gas bill of Rs. 3017. The customer (Bhavit Bhai) acknowledges the bill and commits to paying it today in the afternoon, promising to send the receipt screenshot on WhatsApp."
        }
    },
    "📞 Credit Bank - EMI Pending (English/Gujarati)": {
        "file_name": "demo4.mp3",
        "result": {
            "transcript": "Call me at the credit bank. Yes. Call me at the credit bank. Your EMI is still pending. When will you pay? Yes. I will pay it tomorrow. Your EMI is still pending. Yes. I will pay it tomorrow. The loan has been closed in 1568. And you have paid one EMI. So, one EMI is coming to you. Yes. I have paid it in the previous month. Rs.3598. Yes. And the loan... I have paid it. What? I have paid it. How much was it? One week you have 3598 rupees and you have closed the loan in the previous 5 years. No, no, no, I will talk to you. Yes. I had paid it in the previous 5 years. It is 3898 rupees. Take the amount of 3598 rupees",
            "language": "English",
            "code": "PTP",
            "label": "Promise to Pay",
            "confidence": 96,
            "key_phrase": "Yes. I will pay it tomorrow.",
            "summary": "Agent calls regarding a pending loan EMI. The customer explicitly promises to pay tomorrow, but also raises active inquiries regarding past payments of Rs. 3598 / 3898 and whether the loan was closed in previous cycles."
        }
    },
    "📞 Sabarmati Gas - Verification (Hindi)": {
        "file_name": "demo5.mp3",
        "result": {
            "transcript": "भूलते हैं कि अब अ हेलो हेलो शावर मति गैस से बात कर रही सर पेमेंट बाकी है कब करेंगे आज करने वाले थे कि प्रणाद हो गया हो गया सर स्क्रीन सोट भेज दीजिए ना वह तुम मुझे डिल देख दो करने के लिए आप जो आप मुझे स्क्रीनसड वेश कर अगर आपने पेमेंट किया है तो नहीं देखेंगे तब पहले भी भेजो मेरे पॉइंट आप ऑनलाइन चेक कर लीजिए तो आप भी चेक कर लीजिए बिल हो गया है कर दिया है यहां पर नहीं बता रहा नाम क्या है बिल में नाम क्या है कस्टमबल नाम क्या है वन निट सर सेधा जी मकवाना 468 रुपए बाकी है सर अगर मेरे नाम से कोई गेस का कनेक्शन है ही नहीं हाँ तो पहले आपने क्यों बोला कि मैं भर दूँगा आदम, वो मेरे गर में कनेक्शन है पर वो मेरे नाम से नहीं है चार सा और साथ रुपए बाकिये भरवा दीजिए सर पर हो गया देख लेना आप स्क्रीन सोट बेज दाना",
            "language": "Hindi",
            "code": "EXC",
            "label": "Excuse or Delay",
            "confidence": 94,
            "key_phrase": "हो गया देख लेना आप स्क्रीन सोट बेज दाना",
            "summary": "Agent calls regarding an outstanding Sabarmati Gas bill of Rs. 468/407 for customer Sidhaji Makwana. The customer claims they have already paid and will send a screenshot of the payment receipt on WhatsApp, but also notes that the connection is in someone else's name."
        }
    }
}

# Helper for mapping badges and classes
COLOR_CLASSES = {
    "PTP": "ptp",
    "RTP": "rtp",
    "EXC": "exc",
    "PPC": "ppc",
    "NR": "nr"
}

# --- SIDEBAR CONFIGURATION ---
with st.sidebar:
    st.image("https://img.icons8.com/nolan/96/voice-recognition.png", width=70)
    st.markdown("<h2 style='font-family: Outfit; font-weight: 700; color: white;'>Engine settings</h2>", unsafe_allow_html=True)
    st.markdown("---")

    # Helper to check key validity
    def has_valid_key(key_name: str) -> bool:
        val = os.getenv(key_name, "")
        return bool(val and "your_" not in val.lower() and "placeholder" not in val.lower())

    st.markdown("<p style='color: #94a3b8; font-weight: 600; font-size: 0.85rem;'>API CONNECTION STATUS</p>", unsafe_allow_html=True)
    
    if has_valid_key("GROQ_API_KEY"):
        st.markdown("<div style='padding: 6px 12px; border-radius: 8px; background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.2); color: #10b981; font-weight: 600; font-size: 0.85rem; margin-bottom: 8px;'>🟢 Groq API: Connected (.env)</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div style='padding: 6px 12px; border-radius: 8px; background: rgba(239, 68, 68, 0.1); border: 1px solid rgba(239, 68, 68, 0.2); color: #ef4444; font-weight: 600; font-size: 0.85rem; margin-bottom: 8px;'>🔴 Groq API: Offline (.env empty)</div>", unsafe_allow_html=True)
        
    if has_valid_key("GEMINI_API_KEY"):
        st.markdown("<div style='padding: 6px 12px; border-radius: 8px; background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.2); color: #10b981; font-weight: 600; font-size: 0.85rem; margin-bottom: 12px;'>🟢 Gemini API: Connected (.env)</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div style='padding: 6px 12px; border-radius: 8px; background: rgba(148, 163, 184, 0.1); border: 1px solid rgba(148, 163, 184, 0.2); color: #94a3b8; font-weight: 600; font-size: 0.85rem; margin-bottom: 12px;'>⚪ Gemini API: Offline (Optional)</div>", unsafe_allow_html=True)
    
    st.markdown("---")

    # Model Selection
    st.markdown("<p style='color: #94a3b8; font-weight: 600; font-size: 0.85rem;'>MODEL ARCHITECTURE</p>", unsafe_allow_html=True)
    model_choice = st.selectbox(
        "Select Core Model",
        ["Gemini 1.5 Pro", "Whisper API (Groq)"],
        help="Switch engines cleanly via unified abstract interface."
    )

    # Dynamic explanation of selected model behavior
    if model_choice == "Gemini 1.5 Pro":
        st.info(
            "⚡ **Gemini 1.5 Pro Mode**\n\n"
            "Sends audio directly to Gemini 1.5 Pro. Performs transcription AND classification in "
            "a single API call. Highly efficient, ultra-fast latency."
        )
        whisper_size = None
    else:
        st.warning(
            "🧠 **Whisper Cloud Mode (Groq)**\n\n"
            "Performs hyper-fast cloud speech-to-text transcription using OpenAI Whisper Large-v3 on Groq's LPU. "
            "Then, makes a separate Gemini API call to classify the text transcript (two separate steps)."
        )
        # Advanced options for Whisper
        whisper_size = st.selectbox(
            "Whisper Model ID",
            ["whisper-large-v3", "distil-whisper-large-v3-en"],
            index=0,
            help="Select whisper-large-v3 for maximum accuracy, or distil-whisper-large-v3-en for faster English transcription."
        )

    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #64748b; font-size: 0.8rem;'>"
        "Payment Intelligence Engine v1.0.0<br/>"
        "Model Abstraction Active"
        "</div>",
        unsafe_allow_html=True
    )

# --- MAIN DASHBOARD INTERFACE ---
st.markdown("<div class='title-gradient'>Payment Intelligence Engine</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle-custom'>Analyze call recordings, transcribe dialogue, and categorize customer commitments using advanced speech-to-text models.</div>", unsafe_allow_html=True)

# Layout: Main columns
col_inputs, col_results = st.columns([1, 1.2])

with col_inputs:
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown("<h3 style='font-family: Outfit; font-weight: 600; color: white; margin-top:0px;'>🎙️ Call Audio Input</h3>", unsafe_allow_html=True)
    
    # Selection of Input Type
    input_mode = st.radio("Choose Input Mode", ["📁 Process Custom Upload", "💡 Explore Demo Presets"])
    
    selected_preset = None
    uploaded_file = None
    audio_path = None
    
    if input_mode == "💡 Explore Demo Presets":
        selected_preset = st.selectbox("Select Predefined Payment Collection Call", list(DEMO_PRESETS.keys()))
        preset_info = DEMO_PRESETS[selected_preset]
        preset_file = preset_info["file_name"]
        
        # Audio player for pre-generated audio presets
        base_dir = os.path.dirname(os.path.abspath(__file__))
        audio_path = os.path.join(base_dir, "samples", preset_file)
        if os.path.exists(audio_path):
            # Detect audio format
            audio_format = "audio/mp3" if preset_file.endswith(".mp3") else "audio/wav"
            st.audio(audio_path, format=audio_format)
        else:
            st.error(f"Sample audio preset {preset_file} not found in samples directory.")
            
        st.markdown(
            f"<p style='color: #94a3b8; font-size: 0.9rem;'><i>This preset contains a real call log. "
            f"Expected code: <b>{preset_info['result']['code']} ({preset_info['result']['label']})</b>.</i></p>",
            unsafe_allow_html=True
        )
        
    else:
        uploaded_file = st.file_uploader("Upload audio file", type=["mp3", "wav", "m4a"])
        if uploaded_file:
            st.audio(uploaded_file)
            st.success(f"Successfully staged: {uploaded_file.name} ({uploaded_file.size/1024:.1f} KB)")

    st.markdown("<br/>", unsafe_allow_html=True)
    
    # Action Button
    analyze_btn = st.button("🚀 Analyze Call Recording")
    st.markdown("</div>", unsafe_allow_html=True)

    # Key Code Information Guide
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown("<h4 style='font-family: Outfit; font-weight: 600; color: white; margin-top:0px;'>🏷️ Payment Classification Lexicon</h4>", unsafe_allow_html=True)
    
    guide_cols = st.columns(2)
    with guide_cols[0]:
        st.markdown("""
        - <span style='color: #10b981; font-weight: 700;'>PTP</span>: **Promise to Pay**<br/>Commitment to full settlement on a set date.
        - <span style='color: #ef4444; font-weight: 700;'>RTP</span>: **Refuse to Pay**<br/>Explicit refusal to settle the balance/invoice.
        - <span style='color: #f59e0b; font-weight: 700;'>EXC</span>: **Excuse or Delay**<br/>Temporary excuse, asking for extension.
        """, unsafe_allow_html=True)
    with guide_cols[1]:
        st.markdown("""
        - <span style='color: #3b82f6; font-weight: 700;'>PPC</span>: **Partial Pay Commitment**<br/>Paying a segment now and drafting plans.
        - <span style='color: #9ca3af; font-weight: 700;'>NR</span>: **No Clear Response**<br/>Ambiguous answers, deflection, or hang-ups.
        """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# Store results in Streamlit session state to keep results displayed on screen
if "last_analysis" not in st.session_state:
    st.session_state.last_analysis = None

# --- ANALYSIS PIPELINE EXECUTION ---
if analyze_btn:
    if input_mode == "💡 Explore Demo Presets" and selected_preset:
        preset_info = DEMO_PRESETS[selected_preset]
        
        # Interactive Premium Loading Animation
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        status_steps = [
            ("🔌 Opening audio channel to preset log...", 0.1),
            ("🎙️ Extracting vocal wavelengths...", 0.3),
            ("🤖 Running speech-to-text parsing via unified interface...", 0.6),
            ("🧠 Executing payment intent categorization neural nodes...", 0.8),
            ("✨ Finalizing intelligence metrics and logs...", 1.0)
        ]
        
        start_time = time.time()
        for i, (step_msg, step_prog) in enumerate(status_steps):
            status_text.markdown(f"<p style='color:#a78bfa; font-weight:600;'>{step_msg}</p>", unsafe_allow_html=True)
            time.sleep(0.4)
            progress_bar.progress(step_prog)
            
        latency = time.time() - start_time
        
        # Save results in state
        st.session_state.last_analysis = {
            "result": preset_info["result"],
            "model_used": f"Preset Demo ({model_choice})",
            "latency": f"{latency:.2f}s",
            "source": selected_preset
        }
        
        status_text.empty()
        progress_bar.empty()
        
    elif input_mode == "📁 Process Custom Upload" and uploaded_file:
        # Validate based on chosen model
        if model_choice == "Gemini 1.5 Pro":
            gemini_key_val = os.getenv("GEMINI_API_KEY", "").strip()
            if not gemini_key_val or "your_" in gemini_key_val.lower() or "placeholder" in gemini_key_val.lower():
                st.error("🔑 Gemini API Key Missing or Invalid! Please enter a valid Gemini API Key in the sidebar to activate direct Gemini 1.5 Pro analysis.")
                st.stop()
        else:
            groq_key_val = os.getenv("GROQ_API_KEY", "").strip()
            if not groq_key_val or "your_" in groq_key_val.lower() or "placeholder" in groq_key_val.lower():
                st.error("🔑 Groq API Key Missing or Invalid! Please enter a valid Groq API Key in the sidebar to activate Whisper + Llama analysis.")
                st.stop()

        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # 1. Save uploaded file to local temp file to feed path into models
            status_text.markdown("<p style='color:#38bdf8; font-weight:600;'>💾 Caching uploaded audio file locally...</p>", unsafe_allow_html=True)
            progress_bar.progress(0.1)
            
            file_suffix = os.path.splitext(uploaded_file.name)[1]
            with tempfile.NamedTemporaryFile(delete=False, suffix=file_suffix) as temp_file:
                temp_file.write(uploaded_file.getvalue())
                temp_audio_path = temp_file.name
                
            # 2. Instantiating Selected Model via abstract interface
            status_text.markdown(f"<p style='color:#8b5cf6; font-weight:600;'>⚙️ Booting model provider: {model_choice}...</p>", unsafe_allow_html=True)
            progress_bar.progress(0.2)
            
            if model_choice == "Gemini 1.5 Pro":
                model = GeminiModel()
            else:
                model = WhisperModel(model_size=whisper_size)
                
            start_time = time.time()
            
            # 3. Step 1: Speech-to-Text Transcription
            status_text.markdown(f"<p style='color:#c084fc; font-weight:600;'>🎙️ Transcribing audio file (Model: {model_choice}). Please wait...</p>", unsafe_allow_html=True)
            progress_bar.progress(0.4)
            
            # This call uses our abstract BaseSTTModel interface cleanly
            transcript = model.transcribe(temp_audio_path)
            
            progress_bar.progress(0.7)
            
            # 4. Step 2: Semantic Intent Classification
            status_text.markdown("<p style='color:#a78bfa; font-weight:600;'>🧠 Generating payment commitment semantics & labels...</p>", unsafe_allow_html=True)
            progress_bar.progress(0.85)
            
            # This call also uses our abstract BaseSTTModel interface cleanly
            analysis = model.classify(transcript)
            
            latency = time.time() - start_time
            progress_bar.progress(1.0)
            
            # 5. Save results in state
            st.session_state.last_analysis = {
                "result": analysis,
                "model_used": model_choice if model_choice == "Gemini 1.5 Pro" else f"Whisper {whisper_size} + Gemini",
                "latency": f"{latency:.2f}s",
                "source": uploaded_file.name
            }
            
            # Clean up local temporary file
            os.unlink(temp_audio_path)
            
            status_text.empty()
            progress_bar.empty()
            
        except Exception as e:
            status_text.empty()
            progress_bar.empty()
            st.error(f"❌ Error during model execution: {str(e)}")
            st.info("Check that your API keys are correct and that you have active network connectivity.")
    else:
        st.warning("⚠️ Please upload an audio file first or select explore presets!")

# --- DISPLAY ANALYSIS RESULTS ---
with col_results:
    if st.session_state.last_analysis:
        analysis_data = st.session_state.last_analysis
        res = analysis_data["result"]
        
        # Determine styling parameters based on code
        code = res.get("code", "NR").upper()
        color_class = COLOR_CLASSES.get(code, "nr")
        badge_class = f"badge-{color_class}"
        detail_class = f"detail-card-{color_class}"
        
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        
        # Header Row
        header_cols = st.columns([1, 1])
        with header_cols[0]:
            st.markdown("<h3 style='font-family: Outfit; font-weight: 700; color: white; margin-top:0px; margin-bottom: 2px;'>📊 AI Insights</h3>", unsafe_allow_html=True)
            st.markdown(f"<p style='color: #64748b; font-size:0.85rem; margin-bottom: 20px;'>File: {analysis_data['source']}</p>", unsafe_allow_html=True)
        with header_cols[1]:
            st.markdown(
                f"<div style='text-align: right;'><span class='badge {badge_class}'>{code} - {res.get('label', 'Unknown')}</span></div>",
                unsafe_allow_html=True
            )
            
        # Metrics Strip
        metric_cols = st.columns(3)
        with metric_cols[0]:
            st.markdown(
                f"<div class='metric-box'>"
                f"<div class='section-label'>Confidence</div>"
                f"<div class='metric-num'>{res.get('confidence', 0)}%</div>"
                f"</div>",
                unsafe_allow_html=True
            )
        with metric_cols[1]:
            st.markdown(
                f"<div class='metric-box'>"
                f"<div class='section-label'>Latency</div>"
                f"<div class='metric-num'>{analysis_data['latency']}</div>"
                f"</div>",
                unsafe_allow_html=True
            )
        with metric_cols[2]:
            st.markdown(
                f"<div class='metric-box'>"
                f"<div class='section-label'>Language</div>"
                f"<div class='metric-num'>{res.get('language', 'English')}</div>"
                f"</div>",
                unsafe_allow_html=True
            )
            
        st.markdown("<br/>", unsafe_allow_html=True)
        
        # Key Phrase card
        st.markdown(
            f"<div class='detail-card {detail_class}'>"
            f"<div class='section-label'>🔑 Supporting Key Phrase</div>"
            f"<div class='quote-text'>“{res.get('key_phrase', 'No matching phrase')}”</div>"
            f"</div>",
            unsafe_allow_html=True
        )
        
        # Summary card
        st.markdown(
            f"<div class='detail-card {detail_class}'>"
            f"<div class='section-label'>📝 Executive Summary</div>"
            f"<div class='summary-text'>{res.get('summary', 'No summary provided')}</div>"
            f"</div>",
            unsafe_allow_html=True
        )
        
        # Full Transcript Expander
        with st.expander("🎙️ Show Full Dialogue Transcript", expanded=True):
            raw_transcript = res.get("transcript", "No transcript found.")
            key_phrase = res.get("key_phrase", "")
            
            # Attempt to highlight key phrase in transcript for visual flair!
            if key_phrase and key_phrase in raw_transcript:
                highlighted_transcript = raw_transcript.replace(
                    key_phrase, 
                    f"<span style='background: rgba(167, 139, 250, 0.3); border-bottom: 2px solid #a78bfa; font-weight: 600; padding: 2px 4px; border-radius: 4px;'>{key_phrase}</span>"
                )
                st.markdown(f"<p style='line-height: 1.7; color: #cbd5e1;'>{highlighted_transcript}</p>", unsafe_allow_html=True)
            else:
                st.markdown(f"<p style='line-height: 1.7; color: #cbd5e1;'>{raw_transcript}</p>", unsafe_allow_html=True)
                
        # Model Abstraction Metadata Footer
        st.markdown(
            f"<div style='border-top: 1px solid rgba(255,255,255,0.06); padding-top: 12px; margin-top: 20px; font-size: 0.8rem; color: #64748b;'>"
            f"⚙️ Category analysis rendered using <b>{analysis_data['model_used']}</b> Core."
            f"</div>",
            unsafe_allow_html=True
        )
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        # Initial Placeholder State
        st.markdown("<div class='glass-card' style='text-align: center; padding: 60px 40px;'>", unsafe_allow_html=True)
        st.image("https://img.icons8.com/nolan/96/artificial-intelligence.png", width=90)
        st.markdown("<h3 style='font-family: Outfit; font-weight: 600; color: white;'>Awaiting Audio Analysis</h3>", unsafe_allow_html=True)
        st.markdown("<p style='color: #64748b;'>Stage a custom recording or select a predefined demo call preset, then click 'Analyze Call Recording' to extract payment commitments, confidence scoring, key phrases, and transcripts.</p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
