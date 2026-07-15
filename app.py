import streamlit as st
import assemblyai as aai
import os

def get_configured_api_key():
    if "ASSEMBLYAI_API_KEY" in st.secrets:
        return st.secrets["ASSEMBLYAI_API_KEY"]
    return os.getenv("ASSEMBLYAI_API_KEY", "")

def transcribe_file(file, api_key):
    aai.settings.api_key = api_key
    transcriber = aai.Transcriber()
    transcript = transcriber.transcribe(file)
    if transcript.status == aai.TranscriptStatus.error:
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
    stripped_api_key = api_key_input.strip()
    if stripped_api_key:
        api_key = stripped_api_key
    else:
        api_key = get_configured_api_key()

    if not api_key:
        st.warning("Please enter your AssemblyAI API key in the sidebar to continue.")
        st.stop()

    uploaded_file = st.file_uploader("Upload an audio file", type=["mp3", "wav", "m4a"])
    if uploaded_file is not None:
        transcript = transcribe_file(uploaded_file, api_key)
        st.write("Transcription:")
        st.write(transcript)

if __name__ == "__main__":
    main()