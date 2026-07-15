# Transcription App
Transcription App using AssemblyAI API

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://aslyapi.streamlit.app/)
[![Sponsor me on GitHub](https://img.shields.io/badge/Sponsor%20me%20on-GitHub-EA4AAA?logo=githubsponsors&style=flat-square)](https://github.com/sponsors/gituserc1140)

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
