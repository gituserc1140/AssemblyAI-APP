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
    """Create a minimal .docx payload from transcript text."""
    document_buffer = BytesIO()
    transcript_lines = transcript_text.splitlines() if transcript_text else [" "]
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
    st.sidebar.markdown("---")
    st.sidebar.markdown("[![GitHub](https://img.shields.io/badge/View%20on-GitHub-181717?logo=github)](https://github.com/gituserc1140/AssemblyAI-APP)")

    stripped_api_key = api_key_input.strip()
    if stripped_api_key:
        api_key = stripped_api_key
    else:
        api_key = get_configured_api_key()
    selected_language = LANGUAGE_OPTIONS[language_label]

    if not api_key:
        st.warning("Please enter your AssemblyAI API key in the sidebar to continue.")
        st.stop()

    if "reset_counter" not in st.session_state:
        st.session_state.reset_counter = 0

    def clear_transcription():
        st.session_state.reset_counter += 1

    def show_transcription(audio_source, output_filename=None):
        transcription_result = transcribe_file(audio_source, api_key, selected_language)
        st.write("Transcription:")
        st.write(transcription_result["text"])
        if output_filename and not transcription_result["has_error"]:
            st.download_button(
                "Download transcript (.docx)",
                data=build_word_document(transcription_result["text"]),
                file_name=output_filename,
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )

    record_tab, upload_tab = st.tabs(["Record Audio", "Upload File"])

    reset_key = st.session_state.reset_counter

    with record_tab:
        recorded_audio = st.audio_input("Click to record", key=f"record_{reset_key}")
        if recorded_audio is not None:
            show_transcription(recorded_audio, RECORDED_AUDIO_TRANSCRIPT_FILENAME)
            st.button("Clear", key="clear_record", on_click=clear_transcription)

    with upload_tab:
        uploaded_file = st.file_uploader(
            "Upload an audio file",
            type=["mp3", "wav", "m4a"],
            key=f"upload_{reset_key}",
        )
        if uploaded_file is not None:
            show_transcription(uploaded_file)
            st.button("Clear", key="clear_upload", on_click=clear_transcription)

if __name__ == "__main__":
    main()