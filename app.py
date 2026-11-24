import json
import os
import re
from datetime import datetime
from urllib.parse import quote_plus
from typing import Any

import requests
import streamlit as st

st.set_page_config(page_title="NEETPrep by NilanjanC", page_icon="📘", layout="wide")

SUBJECTS = ["Physics", "Chemistry", "Biology", "Mathematics"]
CHAPTERS = {
    "Physics": ["Physical World and Measurement", "Kinematics", "Laws of Motion", "Work, Energy and Power", "Rotational Motion", "Gravitation", "Properties of Matter", "Thermodynamics", "Oscillations and Waves", "Electrostatics", "Current Electricity", "Magnetic Effects of Current", "Electromagnetic Induction", "Optics", "Modern Physics", "Electronic Devices"],
    "Chemistry": ["Some Basic Concepts", "Structure of Atom", "Periodic Classification", "Chemical Bonding", "States of Matter", "Thermodynamics", "Equilibrium", "Redox Reactions", "Organic Chemistry Basics", "Hydrocarbons", "Solutions", "Electrochemistry", "Chemical Kinetics", "Coordination Compounds", "Biomolecules"],
    "Biology": ["The Living World", "Biological Classification", "Plant Kingdom", "Morphology and Anatomy of Flowering Plants", "Cell Biology", "Cell Cycle and Cell Division", "Photosynthesis", "Respiration in Plants", "Plant Growth", "Animal Kingdom", "Structural Organisation in Animals", "Digestion and Absorption", "Breathing and Circulation", "Excretion", "Locomotion and Movement", "Neural Control", "Human Reproduction", "Reproductive Health", "Genetics", "Molecular Basis of Inheritance", "Evolution", "Human Health and Disease", "Biotechnology", "Biodiversity and Ecology"],
    "Mathematics": ["Sets", "Relations and Functions", "Trigonometry", "Complex Numbers", "Sequences and Series", "Permutations and Combinations", "Binomial Theorem", "Matrices", "Determinants", "Calculus", "Coordinate Geometry", "Vectors", "Probability", "Statistics"],
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
            raise ValueError("Add OPENAI_API_KEY in Streamlit app settings → Secrets.")
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {key}"},
            json={"model": secret("OPENAI_MODEL", "gpt-4o-mini"),
                  "messages": [{"role": "system", "content": "You are a careful NEET and NCERT tutor. Say when uncertain and follow the current NCERT syllabus."},
                               {"role": "user", "content": prompt}],
                  "temperature": 0.4}, timeout=90)
        if not response.ok:
            raise ValueError(f"OpenAI returned an error ({response.status_code}). Check the API key and account.")
        return response.json()["choices"][0]["message"]["content"].strip()

    if provider == "gemini":
        key = secret("GEMINI_API_KEY")
        if not key:
            raise ValueError("Add GEMINI_API_KEY in Streamlit app settings → Secrets.")
        model = secret("GEMINI_MODEL", "gemini-2.0-flash")
        response = requests.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
            params={"key": key},
            json={"contents": [{"parts": [{"text": prompt}]}],
                  "generationConfig": {"temperature": 0.4}}, timeout=90)
        if not response.ok:
            raise ValueError(f"Gemini returned an error ({response.status_code}). Check the API key and account.")
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
    prompt = (
        f'Create {count} original NEET/entrance-practice multiple-choice questions for {scope}, aligned with NCERT. '
        'Clearly label them as newly generated practice questions, not real or previous-year exam questions. '
        'Return only JSON: {"questions":[{"question":"...","options":["A...","B...","C...","D..."],'
        '"answer":"exact option text","explanation":"...","source":"NCERT chapter/topic"}]}. '
        'Every question must have exactly four options and one answer matching an option exactly.'
    )
    questions = parse_json(provider_text(prompt)).get("questions", [])
    valid = [q for q in questions if isinstance(q, dict) and q.get("question") and
             isinstance(q.get("options"), list) and len(q["options"]) == 4 and q.get("answer") in q["options"]]
    if not valid:
        raise ValueError("No valid questions were returned. Please try again.")
    return valid


def subject_chapter_picker(key: str) -> tuple[str, str]:
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
    st.caption("App owner: **NilanjanC**")

st.title(page)
st.caption("NCERT-guided preparation. AI-generated questions are practice material, not authentic past-paper questions.")

if page == "Dashboard":
    st.success("Choose a section from the menu to study, practice, or find official resources.")
    cols = st.columns(4)
    for col, subject, icon in zip(cols, SUBJECTS, ["⚡", "🧪", "🌿", "∑"]):
        with col:
            st.metric(f"{icon} {subject}", f"{len(CHAPTERS[subject])} chapters")
    st.markdown("### What you can do")
    st.markdown("- NCERT-guided chapter overviews\n- Key terms and definitions\n- Official past-paper and answer-key links\n- Chapter-wise or full-syllabus timed mock exams\n- NCERT-guided answers to study questions\n- YouTube searches and official NEET news")

elif page == "NCERT chapters":
    st.subheader("Chapter study guide")
    subject, chapter = subject_chapter_picker("guide")
    if st.button("Create NCERT-guided overview", type="primary"):
        with st.spinner("Preparing a chapter guide…"):
            try:
                prompt = (f"Explain the NCERT chapter '{chapter}' in {subject} for entrance exam preparation. "
                          "Give: (1) a concise overview, (2) core concepts, (3) formulas or processes if relevant, "
                          "(4) common misconceptions, and (5) a short revision checklist. Do not invent quotations or page numbers.")
                guide = provider_text(prompt)
                st.session_state.chapter_guide_result = guide
                st.session_state.chapter_guide_title = f"{subject}: {chapter}"
            except (ValueError, KeyError, IndexError, requests.RequestException) as error:
                st.error(str(error))
    if st.session_state.get("chapter_guide_result"):
        st.markdown(f"### {st.session_state.chapter_guide_title}")
        st.markdown(st.session_state.chapter_guide_result)
    st.markdown("[Open official NCERT textbook downloads](https://ncert.nic.in/textbook.php)")

elif page == "Chapter keywords":
    st.subheader("Key terms and quick definitions")
    subject, chapter = subject_chapter_picker("keywords")
    if st.button("Show chapter keywords", type="primary"):
        with st.spinner("Finding key terms…"):
            try:
                prompt = (f'For the NCERT chapter "{chapter}" in {subject}, return 12 high-value keywords and concise definitions. '
                          'Return only JSON: {"keywords":[{"term":"...","definition":"...","importance":"..."}]}.')
                items = parse_json(provider_text(prompt)).get("keywords", [])
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
    st.info("Download or view files from the issuing organization. External archive pages and download permissions can change.")
    st.markdown("#### NEET exam papers, answer keys and announcements")
    st.markdown("- [NTA NEET official portal](https://neet.nta.nic.in/)\n- [NTA exam portal for NEET](https://exams.nta.ac.in/NEET/)")
    st.markdown("#### NCERT textbooks")
    st.markdown("- [Official NCERT textbook PDFs](https://ncert.nic.in/textbook.php)\n- [NCERT e-books](https://ncert.nic.in/ebooks.php?ln=en)")

elif page == "Mock exams":
    st.subheader("Build a timed mock exam")
    mode = st.radio("Exam type", ["Chapter-wise", "Full syllabus"], horizontal=True)
    if mode == "Chapter-wise":
        subject, chapter = subject_chapter_picker("mock")
        scope = f"the {subject} chapter {chapter}"
    else:
        chosen = st.multiselect("Subjects", SUBJECTS, default=["Physics", "Chemistry", "Biology"])
        scope = "the full syllabus across " + (", ".join(chosen) if chosen else "the selected subjects")

    c1, c2, c3 = st.columns(3)
    with c1:
        count = st.selectbox("Questions", [5, 10, 20, 45, 90, 180], index=1)
    with c2:
        minutes = st.selectbox("Time (minutes)", [15, 30, 60, 180], index=1)
    with c3:
        marks_correct = st.number_input("Marks per correct answer", min_value=1, max_value=10, value=4)
    negative = st.number_input("Marks deducted per wrong answer", min_value=0.0, max_value=10.0, value=1.0, step=0.25)

    if st.button("Generate and start exam", type="primary", disabled=(mode == "Full syllabus" and not chosen)):
        with st.spinner("Generating your mock exam…"):
            try:
                st.session_state.questions = make_questions(scope, count)
                st.session_state.answers = {}
                st.session_state.exam_started = datetime.now().timestamp()
                st.session_state.exam_finished = False
                st.session_state.exam_settings = {"minutes": minutes, "correct": marks_correct, "negative": negative}
                st.rerun()
            except (ValueError, KeyError, IndexError, requests.RequestException) as error:
                st.error(str(error))

    questions = st.session_state.questions
    if questions and st.session_state.exam_started is not None:
        settings = st.session_state.exam_settings
        if not st.session_state.exam_finished:
            remaining = max(0, int(settings["minutes"] * 60 - (datetime.now().timestamp() - st.session_state.exam_started)))
            st.warning(f"Time remaining: {remaining // 60:02d}:{remaining % 60:02d}")
            with st.form("exam_answer_form"):
                for i, question in enumerate(questions):
                    st.markdown(f"**{i + 1}. {question['question']}**")
                    st.radio("Answer", ["— Not answered —"] + question["options"], key=f"exam_answer_{i}", label_visibility="collapsed")
                submitted = st.form_submit_button("Submit exam", type="primary")
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
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Score", f"{score:g}")
            m2.metric("Correct", correct)
            m3.metric("Wrong", wrong)
            m4.metric("Unanswered", unanswered)
            st.info("A trustworthy All India Rank estimate needs real, comparable exam results. A practice score alone cannot provide a reliable AIR.")
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
                st.rerun()

elif page == "Ask NCERT":
    st.subheader("Ask a question")
    subject, chapter = subject_chapter_picker("ask")
    question = st.text_area("What would you like help understanding?")
    if st.button("Get an explanation", type="primary", disabled=not question.strip()):
        with st.spinner("Preparing an NCERT-guided explanation…"):
            try:
                prompt = (f"For {subject}, {chapter}, answer this student's question using an NCERT-guided entrance-exam explanation: {question}. "
                          "Explain step by step, define terms, include formulas/examples when useful, and say if verification against the current NCERT text is needed.")
                st.session_state.ncq_answer = provider_text(prompt)
                st.session_state.ncq_question = question
            except (ValueError, KeyError, IndexError, requests.RequestException) as error:
                st.error(str(error))
    if st.session_state.get("ncq_answer"):
        st.markdown("#### Explanation")
        st.markdown(st.session_state.ncq_answer)
        st.caption("AI-generated study help; verify important details against current NCERT materials.")

elif page == "Videos & news":
    st.subheader("Chapter videos")
    subject, chapter = subject_chapter_picker("video")
    query = quote_plus(f"{subject} {chapter} NCERT entrance exam explanation")
    st.markdown(f"[Search YouTube for {subject} — {chapter} lessons](https://www.youtube.com/results?search_query={query})")
    st.caption("Check each creator and video for accuracy.")
    st.divider()
    st.subheader("Exam news and official updates")
    st.markdown("- [NTA NEET official portal](https://neet.nta.nic.in/)\n- [NTA main website](https://www.nta.ac.in/)")
