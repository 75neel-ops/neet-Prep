import json
import os
import re
from typing import Any

import requests
import streamlit as st

st.set_page_config(page_title="NEETPrep", page_icon="📘", layout="wide")

SUBJECTS = ["Physics", "Chemistry", "Botany", "Zoology"]
CHAPTERS = {
    "Physics": ["Electrostatics", "Current Electricity", "Optics", "Modern Physics"],
    "Chemistry": ["Organic Chemistry", "Chemical Bonding", "Equilibrium", "Thermodynamics"],
    "Botany": ["Genetics", "Plant Physiology", "Cell Biology", "Ecology"],
    "Zoology": ["Human Physiology", "Animal Kingdom", "Reproduction", "Evolution"],
}

st.markdown(
    """
    <style>
      .stApp { background: #f6f7fb; }
      .block-container { max-width: 1150px; padding-top: 2rem; }
      [data-testid="stMetric"] { background: white; padding: 1rem; border-radius: 12px; }
      div.stButton > button[kind="primary"] { border-radius: 10px; }
    </style>
    """,
    unsafe_allow_html=True,
)


def get_secret(name: str, default: str = "") -> str:
    """Read Streamlit Cloud secrets, falling back to environment variables."""
    try:
        value = st.secrets.get(name, default)
    except (FileNotFoundError, AttributeError):
        value = os.environ.get(name, default)
    return str(value or default)


def extract_json(text: str) -> dict[str, Any]:
    text = re.sub(r"```(?:json)?|```", "", text).strip()
    start = text.find("{")
    end = text.rfind("}")
    if start < 0 or end < start:
        raise ValueError("The AI did not return valid JSON. Please try again.")
    result = json.loads(text[start : end + 1])
    if not isinstance(result, dict):
        raise ValueError("The AI response was not in the expected format.")
    return result


def generate_questions(subject: str, chapter: str, count: int) -> list[dict[str, Any]]:
    provider = get_secret("AI_PROVIDER", "openai").lower()
    prompt = (
        f'Generate {count} fresh multiple-choice NEET practice questions for the subject "{subject}" '
        f'and chapter "{chapter}". Follow the current NCERT syllabus. Each question must have exactly '
        'four plausible options, one correct answer that exactly matches one option, a concise explanation, '
        'and an NCERT source reference. These are practice questions, not real or past NEET exam questions. '
        'Return only valid JSON in this format: {"questions":[{"question":"...","options":["...",'
        '"...","...","..."],"answer":"...","explanation":"...","source":"..."}]}.'
    )

    if provider == "openai":
        api_key = get_secret("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("Add OPENAI_API_KEY to your Streamlit app's Secrets settings first.")
        model = get_secret("OPENAI_MODEL", "gpt-4o-mini")
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "model": model,
                "messages": [
                    {"role": "system", "content": "You create accurate NCERT-aligned NEET practice questions."},
                    {"role": "user", "content": prompt},
                ],
                "response_format": {"type": "json_object"},
                "temperature": 0.7,
            },
            timeout=90,
        )
        if not response.ok:
            raise ValueError(f"OpenAI error ({response.status_code}): {response.text[:500]}")
        text = response.json()["choices"][0]["message"]["content"]
    elif provider == "gemini":
        api_key = get_secret("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("Add GEMINI_API_KEY to your Streamlit app's Secrets settings first.")
        model = get_secret("GEMINI_MODEL", "gemini-2.0-flash")
        response = requests.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
            params={"key": api_key},
            json={
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"responseMimeType": "application/json", "temperature": 0.7},
            },
            timeout=90,
        )
        if not response.ok:
            raise ValueError(f"Gemini error ({response.status_code}): {response.text[:500]}")
        text = response.json()["candidates"][0]["content"]["parts"][0]["text"]
    else:
        raise ValueError('AI_PROVIDER must be either "openai" or "gemini".')

    data = extract_json(text)
    questions = data.get("questions", [])
    valid_questions = [
        question
        for question in questions
        if isinstance(question, dict)
        and question.get("question")
        and isinstance(question.get("options"), list)
        and len(question["options"]) == 4
        and question.get("answer") in question["options"]
    ]
    if not valid_questions:
        raise ValueError("The AI did not return usable questions. Please try again.")
    return valid_questions


if "questions" not in st.session_state:
    st.session_state.questions = []
if "question_index" not in st.session_state:
    st.session_state.question_index = 0

with st.sidebar:
    st.title("📘 NEETPrep")
    page = st.radio("Go to", ["Dashboard", "Practice test", "Study resources"], label_visibility="collapsed")
    st.divider()
    st.caption("NEET preparation • Class 12")

st.title(page)
st.caption("Your friendly space to prepare for NEET, one concept at a time.")

if page == "Dashboard":
    st.success("Welcome! You can use this app directly in your browser—there is nothing to install on your computer.")
    st.subheader("Choose what you want to do")
    cols = st.columns(4)
    for col, subject, icon in zip(cols, SUBJECTS, ["⚡", "🧪", "🌿", "🫀"]):
        with col:
            st.metric(f"{icon} {subject}", "Ready to study")
    st.markdown("### Start practicing")
    st.write("Open **Practice test** from the left menu, choose a subject and chapter, then press **Generate my test**.")
    st.info("Practice questions are generated by AI and are not represented as real or past NEET exam questions.")
elif page == "Practice test":
    st.subheader("Create a practice test")
    left, right = st.columns([1, 1])
    with left:
        subject = st.selectbox("Subject", SUBJECTS)
    with right:
        chapter = st.selectbox("Chapter", CHAPTERS[subject])
    col1, col2 = st.columns(2)
    with col1:
        count = st.selectbox("Number of questions", [5, 10, 20, 50], index=0)
    with col2:
        minutes = st.selectbox("Time allowed (minutes)", [15, 30, 60, 180], index=1)

    if st.button("✨ Generate my test", type="primary", use_container_width=True):
        with st.spinner("Making your practice questions… This can take a little while."):
            try:
                st.session_state.questions = generate_questions(subject, chapter, count)
                st.session_state.question_index = 0
                st.session_state.test_minutes = minutes
                st.rerun()
            except requests.RequestException as error:
                st.error(f"Could not connect to the AI service. Check your internet connection and try again. Details: {error}")
            except (ValueError, KeyError, IndexError, json.JSONDecodeError) as error:
                st.error(str(error))

    questions = st.session_state.questions
    if questions:
        st.divider()
        index = st.session_state.question_index
        question = questions[index]
        st.progress((index + 1) / len(questions), text=f"Question {index + 1} of {len(questions)}")
        st.markdown(f"### {question['question']}")
        answer_key = f"answer_{index}"
        choice = st.radio("Choose your answer", question["options"], key=answer_key)
        if st.button("Check answer", key=f"check_{index}"):
            st.session_state[f"checked_{index}"] = True
        if st.session_state.get(f"checked_{index}"):
            if choice == question["answer"]:
                st.success("Correct! Well done.")
            else:
                st.warning(f"Not quite. The correct answer is: {question['answer']}")
            st.markdown(f"**Explanation:** {question.get('explanation', 'No explanation was provided.')}")
            st.caption(f"NCERT alignment: {question.get('source', 'Reference not provided')}")
        prev_col, next_col = st.columns(2)
        with prev_col:
            if st.button("← Previous", disabled=index == 0, use_container_width=True):
                st.session_state.question_index -= 1
                st.rerun()
        with next_col:
            if index < len(questions) - 1:
                if st.button("Next →", use_container_width=True):
                    st.session_state.question_index += 1
                    st.rerun()
            elif st.button("Finish test", type="primary", use_container_width=True):
                st.success("You reached the end of the test. Review your answers above.")

elif page == "Study resources":
    st.subheader("Study resources")
    st.write("Pick a subject in the Practice test section to generate NCERT-aligned practice questions.")
    st.info("This app currently focuses on AI-generated practice tests. Other study modules can be added later.")
