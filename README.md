# NEETPrep — browser-based NEET study app

This repository is deployed as a Streamlit app. You do not need to install software on your computer to use the hosted app.

## Deploy / update the hosted app

Changes pushed to the `main` branch are normally picked up by the Streamlit deployment. If the page does not update, open the app's Streamlit Cloud dashboard and choose **Reboot app**.

To deploy it yourself, sign in at [Streamlit Community Cloud](https://share.streamlit.io/), choose **Create app**, select this repository and the `main` branch, and set the main file to `app.py`. Add a provider key in **Advanced settings → Secrets** before using AI features:

OpenAI:
```toml
AI_PROVIDER = "openai"
OPENAI_API_KEY = "your-key"
OPENAI_MODEL = "gpt-4o-mini"
```

Or Gemini:
```toml
AI_PROVIDER = "gemini"
GEMINI_API_KEY = "your-key"
GEMINI_MODEL = "gemini-2.0-flash"
```

Keep keys only in Streamlit Secrets; never commit them to GitHub or share them in chat. Your AI provider may charge for API use.

## Available sections

- **NCERT chapters:** AI-generated chapter overviews and revision guidance.
- **Chapter keywords:** AI-generated key terms and explanations.
- **Past papers:** links to official NTA and NCERT websites; download files from their source pages.
- **Mock exams:** chapter-wise or selected-subject/full-syllabus practice, selectable timer and marking settings, score and answer explanations.
- **Ask NCERT:** AI study answers guided by the selected subject and chapter.
- **Videos & news:** YouTube chapter searches and official NTA update links.

Generated questions are practice material, not actual previous-year NEET questions. Past-paper links point to source websites because availability and reuse permissions vary. The app does not claim to predict All India Rank: a trustworthy estimate requires real comparable exam/candidate data.
