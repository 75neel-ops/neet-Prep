import json
import os
import re
from datetime import datetime
from urllib.parse import quote_plus
from typing import Any

import requests
import streamlit as st
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="NEETPrep", page_icon="📘", layout="wide")

SUBJECTS = ["Physics", "Chemistry", "Botany", "Zoology"]
CHAPTERS = {
    "Physics": ["Physical World and Measurement", "Kinematics", "Laws of Motion", "Work, Energy and Power", "Rotational Motion", "Gravitation", "Properties of Matter", "Thermodynamics", "Oscillations and Waves", "Electrostatics", "Current Electricity", "Magnetic Effects of Current", "Electromagnetic Induction", "Optics", "Modern Physics", "Electronic Devices"],
    "Chemistry": ["Some Basic Concepts", "Structure of Atom", "Periodic Classification", "Chemical Bonding", "States of Matter", "Thermodynamics", "Equilibrium", "Redox Reactions", "Organic Chemistry Basics", "Hydrocarbons", "Solutions", "Electrochemistry", "Chemical Kinetics", "Coordination Compounds", "Biomolecules"],
    "Botany": ["The Living World", "Biological Classification", "Plant Kingdom", "Morphology of Flowering Plants", "Anatomy of Flowering Plants", "Cell: The Unit of Life", "Cell Cycle and Cell Division", "Photosynthesis", "Respiration in Plants", "Plant Growth and Development", "Sexual Reproduction in Flowering Plants", "Principles of Inheritance", "Molecular Basis of Inheritance", "Biotechnology", "Organisms and Populations", "Ecosystem"],
    "Zoology": ["Animal Kingdom", "Structural Organisation in Animals", "Digestion and Absorption", "Breathing and Exchange of Gases", "Body Fluids and Circulation", "Excretory Products", "Locomotion and Movement", "Neural Control", "Chemical Coordination", "Human Reproduction", "Reproductive Health", "Evolution", "Human Health and Disease", "Biotechnology", "Biodiversity"],
}
PAGES = ["Dashboard", "NCERT chapters", "Chapter keywords", "Past papers", "Mock exams", "Ask NCERT", "Videos & news"]

st.markdown("""
<style>
.stApp { background: #f6f7fb; }
.block-container { max-width: 1150px; padding-top: 2rem; }
[data-testid="stMetric"] { background: white; padding: 1rem; border-radius: 12px; }
div.stButton > button[kind="primary"] { border-radius: 10px; }
</style>
""", unsafe_allow_html=True)


def secret(name: str, default: str = "") -> str:
    try:
        value = st.secrets.get(name, default)
    except (FileNotFoundError, AttributeError):
        value = os.environ.get(name, default)
    return str(value or default)


def provider_text(prompt: str) -> str:
    provider = secret("AI_PROVIDER", "openai").lower()
    if provider == "openai":
        key = secret("OPENAI_API_KEY")
        if not key:
            raise ValueError("To use AI features, add OPENAI_API_KEY in Streamlit app settings → Secrets.")
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {key}"},
            json={"model": secret("OPENAI_MODEL", "gpt-4o-mini"),
                  "messages": [{"role": "system", "content": "You are a careful NEET tutor. Follow NCERT and say when uncertain."},
                               {"role": "user", "content": prompt}],
                  "temperature": 0.4}, timeout=90)
        if not response.ok:
            raise ValueError(f"OpenAI returned an error ({response.status_code}). Check your API key and account.")
        return response.json()["choices"][0]["message"]["content"].strip()
    if provider == "gemini":
        key = secret("GEMINI_API_KEY")
        if not key:
            raise ValueError("To use AI features, add GEMINI_API_KEY in Streamlit app settings → Secrets.")
        model = secret("GEMINI_MODEL", "gemini-2.0-flash")
        response = requests.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
            params={"key": key},
            json={"contents": [{"parts": [{"text": prompt}]}],
                  "generationConfig": {"temperature": 0.4}}, timeout=90)
        if not response.ok:
            raise ValueError(f"Gemini returned an error ({response.status_code}). Check your API key and account.")
        return response.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
    raise ValueError('AI_PROVIDER must be "openai" or "gemini".')


def parse_json(text: str) -> dict[str, Any]:
    clean = re.sub(r"```(?:json)?|```", "", text).strip()
    start, end = clean.find("{"), clean.rfind("}")
    if start < 0 or end < start:
        raise ValueError("The AI response was not in the expected format. Please try again.")
    data = json.loads(clean[start:end + 1])
    if not isinstance(data, dict):
        raise ValueError("The AI response was not in the expected format.")
    return data


def make_questions(scope: str, count: int) -> list[dict[str, Any]]:
    prompt = (f'Create {count} original NEET-UG multiple-choice practice questions for {scope}, aligned with NCERT. '
              'These must be newly generated practice questions, NOT claimed to be past or real exam questions. '
              'Return only JSON: {"questions":[{"question":"...","options":["A...","B...","C...","D..."],'
              '"answer":"exact option text","explanation":"...","source":"NCERT chapter/topic"}]}. '
              'Every question must have exactly four options and one answer matching an option exactly.')
    questions = parse_json(provider_text(prompt)).get("questions", [])
    valid = [q for q in questions if isinstance(q, dict) and q.get("question") and
             isinstance(q.get("options"), list) and len(q["options"]) == 4 and q.get("answer") in q["options"]]
    if not valid:
        raise ValueError("No valid questions were returned. Please try again.")
    return valid


def subject_chapter_picker(key: str = "") -> tuple[str, str]:
    subject = st.selectbox("Subject", SUBJECTS, key=f"subject_{key}")
    chapter = st.selectbox("Chapter", CHAPTERS[subject], key=f"chapter_{key}")
    return subject, chapter


for key, value in {"questions": [], "answers": {}, "exam_started": None, "exam_finished": False,
                   "nav": "Dashboard"}.items():
    if key not in st.session_state:
        st.session_state[key] = value

with st.sidebar:
    st.title("📘 NEETPrep")
    page = st.radio("Go to", PAGES, key="nav", label_visibility="collapsed")
    st.divider()
    st.caption("NEET preparation • Class 11 & 12")

st.title(page)
st.caption("NCERT-guided preparation. AI-generated questions are practice material, not authentic past-paper questions.")

if page == "Dashboard":
    st.success("Welcome! Choose a section from the menu on the left to study, practice, or find official resources.")
    cols = st.columns(4)
    for col, subject, icon in zip(cols, SUBJECTS, ["⚡", "🧪", "🌿", "🫀"]):
        with col:
            st.metric(f"{icon} {subject}", f"{len(CHAPTERS[subject])} chapters")
    st.subheader("What you can do")
    st.markdown("- **NCERT chapters:** get a chapter overview and important concepts.\n- **Chapter keywords:** review key terms and definitions.\n- **Past papers:** visit official NTA sources for papers, answer keys and notices.\n- **Mock exams:** choose chapter-wise or full-syllabus practice, time and marks.\n- **Ask NCERT:** ask a study question and receive a guided explanation.\n- **Videos & news:** find chapter videos and official exam updates.")
    st.info("Add your AI provider key in Streamlit app settings → Secrets to enable AI-generated study guides, keywords, mock questions and answers.")

elif page == "NCERT chapters":
    st.subheader("Chapter study guide")
    subject, chapter = subject_chapter_picker("guide")
    if st.button("Create NCERT-guided overview", type="primary"):
        with st.spinner("Preparing a chapter guide…"):
            try:
                guide = provider_text(f"For NEET-UG, explain the NCERT chapter {chapter} in {subject}. Give: (1) a concise overview, (2) core concepts in simple language, (3) formulas or processes if relevant, (4) common misconceptions, and (5) a short revision checklist. Do not invent quotations or exact textbook page references. Clearly advise checking the current NCERT textbook.")
                st.session_state.chapter_guide = guide
                st.session_state.chapter_guide_title = f"{subject}: {chapter}"
            except (ValueError, KeyError, IndexError, requests.RequestException) as error:
                st.error(str(error))
    if st.session_state.get("chapter_guide"):
        st.markdown(f"### {st.session_state.chapter_guide_title}")
        st.markdown(st.session_state.chapter_guide)
    st.markdown("[Open official NCERT textbook downloads](https://ncert.nic.in/textbook.php)")

elif page == "Chapter keywords":
    st.subheader("Key terms and quick definitions")
    subject, chapter = subject_chapter_picker("keywords")
    if st.button("Show chapter keywords", type="primary"):
        with st.spinner("Finding key terms…"):
            try:
                raw = provider_text(f'For the NEET NCERT chapter "{chapter}" in {subject}, provide 12 high-value keywords with one-sentence accurate definitions and why each matters. Return only JSON as {{"keywords":[{{"term":"...","definition":"...","importance":"..."}}]}}. Do not claim exact textbook quotes.')
                items = parse_json(raw).get("keywords", [])
                st.session_state.keyword_items = items
                st.session_state.keyword_heading = f"{subject}: {chapter}"
            except (ValueError, KeyError, IndexError, requests.RequestException) as error:
                st.error(str(error))
    if st.session_state.get("keyword_items"):
        st.markdown(f"### {st.session_state.keyword_heading}")
        for item in st.session_state.keyword_items:
            if isinstance(item, dict) and item.get("term"):
                with st.expander(item["term"]):
                    st.write(item.get("definition", ""))
                    if item.get("importance"):
                        st.caption(item["importance"])

elif page == "Past papers":
    st.subheader("Official and freely available study materials")
    st.info("Use the source websites to view or download their files. We link to official sources rather than copying or redistributing papers whose reuse rights may be unclear.")
    st.markdown("#### NEET exam papers, answer keys and announcements")
    st.markdown("- [NTA NEET official portal — notices and exam updates](https://neet.nta.nic.in/)\n- [NTA exam portal for NEET — exam materials and notices](https://exams.nta.ac.in/NEET/)")
    st.markdown("#### NCERT textbooks")
    st.markdown("- [Official NCERT textbook PDF page](https://ncert.nic.in/textbook.php)\n- [NCERT e-books](https://ncert.nic.in/ebooks.php?ln=en)")
    st.markdown("#### How to save a paper for later")
    st.write("Open a source link, choose the exam year and paper/answer key when available, then use the PDF viewer's download icon. Availability and archive pages can change; rely on the issuing organization for the latest files.")

elif page == "Mock exams":
    st.subheader("Build a timed mock exam")
    mode = st.radio("Exam type", ["Chapter-wise", "Full syllabus"], horizontal=True)
    if mode == "Chapter-wise":
        subject, chapter = subject_chapter_picker("mock")
        scope = f"the {subject} chapter {chapter}"
    else:
        chosen = st.multiselect("Subjects", SUBJECTS, default=SUBJECTS)
        scope = "the NEET-UG full syllabus across " + (", ".join(chosen) if chosen else "the selected subjects")
    c1, c2, c3 = st.columns(3)
    with c1:
        count = st.selectbox("Questions", [5, 10, 20, 45, 90, 180], index=1)
    with c2:
        minutes = st.selectbox("Time (minutes)", [15, 30, 60, 180], index=1)
    with c3:
        marks_correct = st.number_input("Marks per correct answer", min_value=1, max_value=10, value=4)
    negative = st.number_input("Marks deducted per wrong answer", min_value=0.0, max_value=10.0, value=1.0, step=0.25)
    st.caption("Questions are AI-generated practice questions, not real past NEET questions. Check current official exam rules for actual marking schemes.")
    if st.button("Generate and start exam", type="primary", disabled=(mode == "Full syllabus" and not chosen)):
        with st.spinner("Generating your mock exam…"):
            try:
                st.session_state.questions = make_questions(scope, count)
                st.session_state.answers = {}
                st.session_state.exam_started = datetime.now().timestamp()
                st.session_state.exam_finished = False
                st.session_state.exam_settings = {"minutes": minutes, "correct": marks_correct, "negative": negative, "scope": scope}
                st.rerun()
            except (ValueError, KeyError, IndexError, requests.RequestException) as error:
                st.error(str(error))

    questions = st.session_state.questions
    if questions and st.session_state.exam_started is not None:
        settings = st.session_state.exam_settings
        expires = st.session_state.exam_started + settings["minutes"] * 60
        remaining = max(0, int(expires - datetime.now().timestamp()))
        if not st.session_state.exam_finished and remaining > 0:
            st_autorefresh(interval=1000, key="exam_timer")
            st.warning(f"Time remaining: **{remaining // 60:02d}:{remaining % 60:02d}**")
        elif remaining == 0:
            st.session_state.exam_finished = True
            st.warning("Time is up. Your submitted answers are shown below.")
        st.progress(min(1.0, len(st.session_state.answers) / len(questions)), text=f"Answered {len(st.session_state.answers)} of {len(questions)}")
        if not st.session_state.exam_finished:
            with st.form("exam_answer_form"):
                for i, question in enumerate(questions):
                    st.markdown(f"**{i + 1}. {question['question']}**")
                    st.radio("Choose an answer", ["— Not answered —"] + question["options"], key=f"exam_answer_{i}", label_visibility="collapsed")
                submitted = st.form_submit_button("Submit exam", type="primary", use_container_width=True)
            if submitted:
                st.session_state.answers = {i: st.session_state.get(f"exam_answer_{i}") for i in range(len(questions))}
                st.session_state.exam_finished = True
                st.rerun()
        if st.session_state.exam_finished:
            answers = st.session_state.answers
            correct = sum(1 for i, q in enumerate(questions) if answers.get(i) == q["answer"])
            wrong = sum(1 for i, q in enumerate(questions) if answers.get(i) not in (None, "— Not answered —", q["answer"]))
            unanswered = len(questions) - correct - wrong
            score = correct * settings["correct"] - wrong * settings["negative"]
            st.subheader("Your result")
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Score", f"{score:g} marks")
            m2.metric("Correct", correct)
            m3.metric("Wrong", wrong)
            m4.metric("Unanswered", unanswered)
            st.info("A reliable All India Rank estimate needs real, comparable candidate results and exam-year data. This practice score alone cannot provide a trustworthy AIR.")
            with st.expander("Review answers and explanations", expanded=True):
                for i, q in enumerate(questions):
                    st.markdown(f"**{i + 1}. {q['question']}**")
                    st.write(f"Your answer: {answers.get(i, '— Not answered —')}")
                    st.write(f"Correct answer: {q['answer']}")
                    st.caption(f"{q.get('explanation', '')} | NCERT: {q.get('source', 'Reference not provided')}")
            if st.button("Start a new exam"):
                st.session_state.questions = []
                st.session_state.exam_started = None
                st.session_state.exam_finished = False
                st.session_state.answers = {}
                st.rerun()

elif page == "Ask NCERT":
    st.subheader("Ask a question, get an NCERT-guided explanation")
    subject, chapter = subject_chapter_picker("ask")
    question = st.text_area("What would you like help understanding?", placeholder="For example: Why does the resistance of a conductor change with temperature?")
    if st.button("Get an explanation", type="primary", disabled=not question.strip()):
        with st.spinner("Preparing an NCERT-guided explanation…"):
            try:
                answer = provider_text(f"Answer this NEET student's question using NCERT-level explanations and the current NCERT chapter {chapter} in {subject} as the guide. Student question: {question}\nExplain step by step in clear language, define key terms, include an equation/example if useful, and flag uncertainty. Do not fabricate textbook quotations or page numbers. Encourage checking the current NCERT text.")
                st.session_state.last_answer = answer
                st.session_state.last_question = question
            except (ValueError, KeyError, IndexError, requests.RequestException) as error:
                st.error(str(error))
    if st.session_state.get("last_answer"):
        st.markdown("#### Explanation")
        st.markdown(st.session_state.last_answer)
        st.caption("AI-generated study help; verify important details against the current NCERT textbook.")

elif page == "Videos & news":
    st.subheader("Chapter videos")
    subject, chapter = subject_chapter_picker("video")
    query = quote_plus(f"{subject} {chapter} NCERT NEET explanation")
    st.markdown(f"[Search YouTube for {subject} — {chapter} NCERT/NEET lessons](https://www.youtube.com/results?search_query={query})")
    st.caption("YouTube search results are provided by YouTube; check each creator and video for accuracy.")
    st.divider()
    st.subheader("NEET news and official updates")
    st.write("For current application dates, admit cards, results and exam notices, use the official NTA websites:")
    st.markdown("- [NTA NEET official portal — latest notices](https://neet.nta.nic.in/)\n- [NTA main website](https://www.nta.ac.in/)")
    st.caption("This app links to official notice pages; it does not republish or independently verify breaking news.")
