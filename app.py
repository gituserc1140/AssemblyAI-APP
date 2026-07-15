import streamlit as st
import assemblyai as aai
import os

# Set your AssemblyAI API key
ASSEMBLYAI_API_KEY = st.secrets["ASSEMBLYAI_API_KEY"]
aai.settings.api_key = ASSEMBLYAI_API_KEY

def transcribe_file(file):
    transcriber = aai.Transcriber()
    transcript = transcriber.transcribe(file)
    if transcript.status == aai.TranscriptStatus.error:
        return f"Error: {transcript.error}"
    return transcript.text

def main():
    st.title("AssemblyAI Transcription App")
    uploaded_file = st.file_uploader("Upload an audio file", type=["mp3", "wav", "m4a"])
    if uploaded_file is not None:
        transcript = transcribe_file(uploaded_file)
        st.write("Transcription:")
        st.write(transcript)

if __name__ == "__main__":
    main()