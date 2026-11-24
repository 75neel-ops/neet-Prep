# NEETPrep

A browser-based NCERT-guided NEET preparation app built with Streamlit.

## Subjects

The app now includes **Physics, Chemistry, Biology, and Mathematics**. Biology combines the Botany and Zoology areas; Botany and Zoology are no longer separate subject choices.

## Deploy

Streamlit Community Cloud settings:

- Repository: `75neel-ops/neet-Prep`
- Branch: `main`
- Main file: `app.py`

Add one provider under app settings → Secrets:

```toml
AI_PROVIDER = "openai"
OPENAI_API_KEY = "your-key"
OPENAI_MODEL = "gpt-4o-mini"
```

Or:

```toml
AI_PROVIDER = "gemini"
GEMINI_API_KEY = "your-key"
GEMINI_MODEL = "gemini-2.0-flash"
```

Never commit or share the API key.

## Features

- NCERT-guided chapter guides
- Chapter keywords
- Official NCERT and NTA links
- Chapter-wise and full-syllabus timed practice exams
- Custom marks and negative marking
- Score and answer review
- NCERT-guided question help
- YouTube chapter searches and official exam news links

AI-generated questions are practice material, not real or previous-year NEET questions. A practice score alone cannot produce a trustworthy All India Rank.
