# NEETPrep (Streamlit)

A browser-based NEET preparation app with AI-generated, NCERT-aligned practice questions. You do not need to install anything on your computer: deploy this GitHub repository on Streamlit Community Cloud and use the website it gives you.

## Deploy it in your browser

1. Sign in to [Streamlit Community Cloud](https://share.streamlit.io/) with GitHub.
2. Select **Create app** and choose the `75neel-ops/neet-Prep` repository, the `main` branch, and `app.py` as the main file.
3. Before launching, open the app's **Advanced settings → Secrets** and paste one provider's settings (replace the example text with your own API key):

   For OpenAI:
   ```toml
   AI_PROVIDER = "openai"
   OPENAI_API_KEY = "paste-your-OpenAI-key-here"
   OPENAI_MODEL = "gpt-4o-mini"
   ```

   Or for Gemini:
   ```toml
   AI_PROVIDER = "gemini"
   GEMINI_API_KEY = "paste-your-Gemini-key-here"
   GEMINI_MODEL = "gemini-2.0-flash"
   ```

4. Click **Deploy**. When deployment finishes, open the Streamlit URL shown on the page.
5. In the app, select **Practice test**, choose a subject and chapter, then click **Generate my test**.

You can also add or edit secrets later from the app's Streamlit Cloud settings. Keep API keys in the Streamlit Secrets settings—never paste them into source code, a public chat, or a committed file. AI providers may charge for API use.

## Run locally (optional)

You do not need to do this to use the hosted app. If you choose to run it locally, install Python, then run `pip install -r requirements.txt` and `streamlit run app.py`.

## About the questions

Questions are AI-generated practice material and are not claimed to be real or past NEET exam questions. Please verify important information against current NCERT materials.
