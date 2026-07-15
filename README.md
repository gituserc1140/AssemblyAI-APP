# Transcription App
Transcription App using AssemblyAI API

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://aslyapi.streamlit.app/)
[![Sponsor me on GitHub](https://img.shields.io/badge/Sponsor%20me%20on-GitHub-EA4AAA?logo=githubsponsors&style=flat-square)](https://github.com/sponsors/gituserc1140)

## About

A simple Streamlit web app that turns spoken audio into text using the [AssemblyAI](https://www.assemblyai.com/) speech-to-text API. You can either **record audio directly in your browser** via the built-in microphone, or **upload an existing audio file** (MP3, WAV, or M4A). The transcript is displayed on screen and can be downloaded as a Word document (`.docx`). A language selector lets you choose between English (US) for best accuracy on short clips, or automatic language detection for longer recordings.

## API key setup

You can provide your `ASSEMBLYAI_API_KEY` in any of these ways:
- Enter it in the Streamlit sidebar input field at runtime
- Add it to `.streamlit/secrets.toml`:
  - `ASSEMBLYAI_API_KEY = "your_key"`
- Set it as an environment variable:
  - `ASSEMBLYAI_API_KEY=your_key`

## Transcription language setting

Use the sidebar language setting:
- **English (US) - recommended**: better reliability for short spoken clips
- **Auto-detect language**: best for longer files with clear speech
