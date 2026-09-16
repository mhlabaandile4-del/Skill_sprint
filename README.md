# Skill_sprint
SPA where students take on a new Ai-generated project brief every week.

## Streamlit deployment

1. Copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml` locally.
2. Fill in the Firebase settings from Firebase Project Settings, create a new Gemini API key, and generate a long random `JWT_SECRET_KEY`.
3. In Streamlit Community Cloud, add the same values under **App settings > Secrets**. Never commit or upload `secrets.toml`.
4. Deploy with `main.py` as the entrypoint.

The Gemini key previously present in the source was exposed and must be revoked. Firebase web API keys are client configuration, but storing them as deployment secrets keeps configuration centralized.
