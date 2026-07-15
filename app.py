import streamlit as st
import assemblyai as aai
import os

ENGLISH_US_LABEL = "English (US) - recommended"
AUTO_DETECT_LABEL = "Auto-detect language"
LANGUAGE_CHOICES = [
    (ENGLISH_US_LABEL, "en_us"),
    (AUTO_DETECT_LABEL, "auto"),
]
LANGUAGE_OPTIONS = dict(LANGUAGE_CHOICES)
AUTO_DETECT_ERROR_HINT = "Try a longer spoken clip or select a specific language instead of auto-detect."


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
            return f"Error: {transcript.error}. {AUTO_DETECT_ERROR_HINT}"
        return f"Error: {transcript.error}"
    return transcript.text


def main():
    st.title("AssemblyAI Transcription App")
    st.sidebar.header("Settings")
    api_key_input = st.sidebar.text_input(
        "AssemblyAI API Key",
        type="password",
        help="Add your API key here, or configure ASSEMBLYAI_API_KEY in Streamlit secrets/environment.",
    )
    language_label = st.sidebar.selectbox(
        "Transcription Language",
        [label for label, _ in LANGUAGE_CHOICES],
        index=0,
        help="Use a fixed language for better reliability on short clips. Auto-detect works best on longer spoken audio.",
    )
    stripped_api_key = api_key_input.strip()
    if stripped_api_key:
        api_key = stripped_api_key
    else:
        api_key = get_configured_api_key()
    selected_language = LANGUAGE_OPTIONS[language_label]

    if not api_key:
        st.warning("Please enter your AssemblyAI API key in the sidebar to continue.")
        st.stop()

    def show_transcription(audio_source):
        transcript = transcribe_file(audio_source, api_key, selected_language)
        st.write("Transcription:")
        st.write(transcript)

    upload_tab, record_tab = st.tabs(["Upload File", "Record Audio"])

    with upload_tab:
        uploaded_file = st.file_uploader("Upload an audio file", type=["mp3", "wav", "m4a"])
        if uploaded_file is not None:
            show_transcription(uploaded_file)

    with record_tab:
        recorded_audio = st.audio_input("Click to record")
        if recorded_audio is not None:
            show_transcription(recorded_audio)

if __name__ == "__main__":
    main()