import html
import os
from io import BytesIO
from zipfile import ZIP_DEFLATED, ZipFile

import assemblyai as aai
import streamlit as st

ENGLISH_US_LABEL = "English (US) - recommended"
AUTO_DETECT_LABEL = "Auto-detect language"
LANGUAGE_CHOICES = [
    (ENGLISH_US_LABEL, "en_us"),
    (AUTO_DETECT_LABEL, "auto"),
]
LANGUAGE_OPTIONS = dict(LANGUAGE_CHOICES)
AUTO_DETECT_ERROR_HINT = "Try a longer spoken clip or select a specific language instead of auto-detect."
RECORDED_AUDIO_TRANSCRIPT_FILENAME = "recorded-audio-transcript.docx"

_CSS = """
<style>
/* ── Page background ───────────────────────────────────────────── */
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
    min-height: 100vh;
}
[data-testid="stHeader"] { background: transparent; }

/* ── Hero banner ───────────────────────────────────────────────── */
.hero {
    text-align: center;
    padding: 2.5rem 1rem 1.5rem;
}
.hero h1 {
    font-size: 2.6rem;
    font-weight: 800;
    background: linear-gradient(90deg, #a78bfa, #60a5fa);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.3rem;
}
.hero p {
    color: #cbd5e1;
    font-size: 1.05rem;
    margin-top: 0;
}

/* ── Tab bar ───────────────────────────────────────────────────── */
[data-testid="stTabs"] [role="tablist"] {
    gap: 0.5rem;
    border-bottom: 2px solid #3730a3;
}
[data-testid="stTabs"] [role="tab"] {
    background: rgba(255,255,255,0.05);
    border-radius: 10px 10px 0 0;
    padding: 0.5rem 1.4rem;
    color: #a5b4fc !important;
    font-weight: 600;
    border: none;
    transition: background 0.2s;
}
[data-testid="stTabs"] [role="tab"][aria-selected="true"] {
    background: linear-gradient(135deg, #6d28d9, #3b82f6);
    color: #fff !important;
}

/* ── Transcript result card ────────────────────────────────────── */
.transcript-card {
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(167,139,250,0.35);
    border-radius: 14px;
    padding: 1.4rem 1.6rem;
    color: #e2e8f0;
    font-size: 1rem;
    line-height: 1.7;
    white-space: pre-wrap;
    word-break: break-word;
    margin-top: 1rem;
}
.transcript-label {
    font-size: 0.78rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #a78bfa;
    margin-bottom: 0.4rem;
}

/* ── Error card ────────────────────────────────────────────────── */
.error-card {
    background: rgba(239,68,68,0.12);
    border: 1px solid rgba(239,68,68,0.45);
    border-radius: 14px;
    padding: 1.2rem 1.6rem;
    color: #fca5a5;
    font-size: 0.97rem;
    margin-top: 1rem;
}

/* ── Buttons ───────────────────────────────────────────────────── */
[data-testid="stDownloadButton"] button,
[data-testid="stButton"] button {
    background: linear-gradient(135deg, #7c3aed, #2563eb) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 0.45rem 1.2rem !important;
    font-weight: 600 !important;
    transition: opacity 0.2s !important;
}
[data-testid="stDownloadButton"] button:hover,
[data-testid="stButton"] button:hover { opacity: 0.85 !important; }

/* ── Sidebar ───────────────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: rgba(15,12,41,0.85);
    border-right: 1px solid rgba(167,139,250,0.2);
}
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] div { color: #cbd5e1 !important; }
[data-testid="stSidebar"] h2 {
    color: #a78bfa !important;
    font-size: 1.1rem;
}

/* ── Warning text ──────────────────────────────────────────────── */
[data-testid="stAlert"] p { color: #ffffff !important; }

/* ── Spinner text ──────────────────────────────────────────────── */
[data-testid="stSpinner"] p { color: #a5b4fc !important; }

/* ── File uploader ─────────────────────────────────────────────── */
[data-testid="stFileUploaderDropzone"] {
    background: rgba(255,255,255,0.04) !important;
    border: 2px dashed rgba(167,139,250,0.4) !important;
    border-radius: 12px !important;
}
</style>
"""


def get_configured_api_key():
    if "ASSEMBLYAI_API_KEY" in st.secrets:
        return st.secrets["ASSEMBLYAI_API_KEY"]
    return os.getenv("ASSEMBLYAI_API_KEY", "")


def transcribe_file(file, api_key, language_option):
    aai.settings.api_key = api_key
    transcriber = aai.Transcriber()
    if language_option == "auto":
        config = aai.TranscriptionConfig(language_detection=True)
    else:
        config = aai.TranscriptionConfig(language_detection=False, language_code=language_option)
    transcript = transcriber.transcribe(file, config=config)
    if transcript.status == aai.TranscriptStatus.error:
        if language_option == "auto":
            return {
                "text": f"Error: {transcript.error}. {AUTO_DETECT_ERROR_HINT}",
                "has_error": True,
            }
        return {"text": f"Error: {transcript.error}", "has_error": True}
    return {"text": transcript.text, "has_error": False}


def build_word_document(transcript_text):
    """Return a minimal Word .docx payload for transcript text.

    Args:
        transcript_text: Transcript content to place in the document.

    Returns:
        Bytes for a .docx file download.
    """
    document_buffer = BytesIO()
    transcript_lines = (transcript_text or "").splitlines()
    paragraph_xml_parts = [
        (
            "<w:p><w:r><w:t xml:space=\"preserve\">"
            f"{html.escape(line)}"
            "</w:t></w:r></w:p>"
        )
        for line in transcript_lines
    ]
    paragraph_xml = "".join(paragraph_xml_parts)
    document_xml = (
        "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>"
        "<w:document xmlns:w=\"http://schemas.openxmlformats.org/wordprocessingml/2006/main\">"
        f"<w:body>{paragraph_xml}<w:sectPr/></w:body>"
        "</w:document>"
    )
    with ZipFile(document_buffer, "w", ZIP_DEFLATED) as document:
        document.writestr(
            "[Content_Types].xml",
            "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>"
            "<Types xmlns=\"http://schemas.openxmlformats.org/package/2006/content-types\">"
            "<Default Extension=\"rels\" ContentType=\"application/vnd.openxmlformats-package.relationships+xml\"/>"
            "<Default Extension=\"xml\" ContentType=\"application/xml\"/>"
            "<Override PartName=\"/word/document.xml\" "
            "ContentType=\"application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml\"/>"
            "</Types>",
        )
        document.writestr(
            "_rels/.rels",
            "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>"
            "<Relationships xmlns=\"http://schemas.openxmlformats.org/package/2006/relationships\">"
            "<Relationship Id=\"rId1\" "
            "Type=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument\" "
            "Target=\"word/document.xml\"/>"
            "</Relationships>",
        )
        document.writestr("word/document.xml", document_xml)
    return document_buffer.getvalue()


def main():
    st.set_page_config(
        page_title="Transcription App",
        page_icon="🎙️",
        layout="centered",
    )
    st.markdown(_CSS, unsafe_allow_html=True)

    # ── Hero header ────────────────────────────────────────────────
    st.markdown(
        """
        <div class="hero">
            <h1>🎙️ Transcription App</h1>
            <p>Record or upload audio and get an accurate transcript in seconds.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Sidebar ────────────────────────────────────────────────────
    st.sidebar.header("Settings")
    api_key_input = st.sidebar.text_input(
        "AssemblyAI API Key",
        type="password",
        help="Add your API key here, or configure ASSEMBLYAI_API_KEY in Streamlit secrets/environment.",
    )
    st.sidebar.markdown(
        "<small><a href='https://www.assemblyai.com/app/account' target='_blank' "
        "style='color:#a78bfa;text-decoration:none;'>🔑 Get your API key</a></small>",
        unsafe_allow_html=True,
    )
    language_label = st.sidebar.selectbox(
        "Transcription Language",
        [label for label, _ in LANGUAGE_CHOICES],
        index=0,
        help="Use a fixed language for better reliability on short clips. Auto-detect works best on longer spoken audio.",
    )
    stripped_api_key = api_key_input.strip()
    api_key = stripped_api_key if stripped_api_key else get_configured_api_key()
    selected_language = LANGUAGE_OPTIONS[language_label]

    if not api_key:
        st.warning("Please enter your AssemblyAI API key in the sidebar to continue.", icon=None)
        st.stop()

    if "reset_counter" not in st.session_state:
        st.session_state.reset_counter = 0

    def clear_transcription():
        st.session_state.reset_counter += 1

    def show_transcription(audio_source, download_filename=None):
        with st.spinner("Transcribing… this may take a moment ✨"):
            transcription_result = transcribe_file(audio_source, api_key, selected_language)

        if transcription_result["has_error"]:
            st.markdown(
                f'<div class="error-card">⚠️ {html.escape(transcription_result["text"])}</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown('<div class="transcript-label">📝 Transcript</div>', unsafe_allow_html=True)
            st.markdown(
                f'<div class="transcript-card">{html.escape(transcription_result["text"])}</div>',
                unsafe_allow_html=True,
            )
            if download_filename:
                st.download_button(
                    "⬇️ Download transcript (.docx)",
                    data=build_word_document(transcription_result["text"]),
                    file_name=download_filename,
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                )

    # ── Tabs ───────────────────────────────────────────────────────
    record_tab, upload_tab = st.tabs(["Record Audio", "Upload File"])
    reset_key = st.session_state.reset_counter

    with record_tab:
        recorded_audio = st.audio_input("Click the microphone to start recording", key=f"record_{reset_key}")
        if recorded_audio is not None:
            show_transcription(recorded_audio, RECORDED_AUDIO_TRANSCRIPT_FILENAME)
            st.button("🗑️ Clear", key="clear_record", on_click=clear_transcription)

    with upload_tab:
        uploaded_file = st.file_uploader(
            "Drag & drop an audio file, or click to browse",
            type=["mp3", "wav", "m4a"],
            key=f"upload_{reset_key}",
        )
        if uploaded_file is not None:
            show_transcription(uploaded_file)
            st.button("🗑️ Clear", key="clear_upload", on_click=clear_transcription)

if __name__ == "__main__":
    main()