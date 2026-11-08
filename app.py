# app.py
# -*- coding: utf-8 -*-
"""
Веб-тренажёр по топографической анатомии и оперативной хирургии.
Запуск: streamlit run app.py
"""

import random
import streamlit as st

from questions import THEMES

# ---------------------------------------------------------------
# НАСТРОЙКИ СТРАНИЦЫ
# ---------------------------------------------------------------
st.set_page_config(
    page_title="Тренажёр · Топографическая анатомия",
    page_icon="🩺",
    layout="centered",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------
# CSS — аккуратный вид, крупные кнопки
# ---------------------------------------------------------------
st.markdown("""
<style>
    .stButton > button {
        width: 100%;
        border-radius: 10px;
        padding: 0.6em 1em;
        font-size: 1rem;
    }
    div[data-testid="stCheckbox"] {
        padding: 6px 0;
    }
    h1, h2, h3 { margin-top: 0.4em; }
    .block-container { padding-top: 2rem; }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------
# СЕССИОННОЕ СОСТОЯНИЕ
# ---------------------------------------------------------------
def init_state():
    defaults = {
        "page": "menu",           # menu | quiz | result
        "theme_key": None,
        "questions": [],
        "idx": 0,
        "answers": {},            # {idx: set(индексов)}
        "show_feedback": False,
        "shuffle_opts": True,
        "shuffle_q": True,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


init_state()

LETTERS = ["А", "Б", "В", "Г", "Д", "Е", "Ж", "З"]


# ---------------------------------------------------------------
# ПОДГОТОВКА ВОПРОСОВ (с перемешиванием)
# ---------------------------------------------------------------
def prepare_questions(raw_questions, shuffle_q: bool, shuffle_opts: bool):
    prepared = []
    for item in raw_questions:
        pairs = [(opt, i in item["ans"]) for i, opt in enumerate(item["opts"])]
        if shuffle_opts:
            random.shuffle(pairs)
        new_opts = [t for t, _ in pairs]
        new_ans = {i for i, (_, flag) in enumerate(pairs) if flag}
        prepared.append({"q": item["q"], "opts": new_opts, "ans": new_ans})
    if shuffle_q:
        random.shuffle(prepared)
    return prepared


def start_quiz(theme_key):
    st.session_state.theme_key = theme_key
    st.session_state.questions = prepare_questions(
        THEMES[theme_key]["questions"],
        shuffle_q=st.session_state.shuffle_q,
        shuffle_opts=st.session_state.shuffle_opts,
    )
    st.session_state.idx = 0
    st.session_state.answers = {}
    st.session_state.show_feedback = False
    st.session_state.page = "quiz"
    st.rerun()


def start_all():
    all_q = []
    for key in sorted(THEMES.keys(), key=lambda x: int(x)):
        all_q.extend(THEMES[key]["questions"])
    st.session_state.theme_key = "__all__"
    st.session_state.questions = prepare_questions(
        all_q,
        shuffle_q=st.session_state.shuffle_q,
        shuffle_opts=st.session_state.shuffle_opts,
    )
    st.session_state.idx = 0
    st.session_state.answers = {}
    st.session_state.show_feedback = False
    st.session_state.page = "quiz"
    st.rerun()


# ---------------------------------------------------------------
# САЙДБАР
# ---------------------------------------------------------------
def render_sidebar():
    with st.sidebar:
        st.header("⚙️ Настройки")
        st.session_state.shuffle_opts = st.toggle(
            "Перемешивать варианты ответов",
            value=st.session_state.shuffle_opts,
        )
        st.session_state.shuffle_q = st.toggle(
            "Перемешивать порядок вопросов",
            value=st.session_state.shuffle_q,
        )
        st.divider()
        st.caption(
            f"Всего тем: {len(THEMES)}\n\n"
            f"Всего вопросов: {sum(len(t['questions']) for t in THEMES.values())}"
        )
        st.divider()
        if st.session_state.page != "menu":
            if st.button("🏠 В меню", use_container_width=True):
                st.session_state.page = "menu"
                st.rerun()


# ---------------------------------------------------------------
# МЕНЮ
# ---------------------------------------------------------------
def render_menu():
    st.title("🩺 Тренажёр по топографической анатомии")
    st.caption("Оперативная хирургия · тесты для педиатрического факультета")

    st.subheader("Выбор темы")
    theme_keys = sorted(THEMES.keys(), key=lambda x: int(x))
    labels = [
        f"{k}. {THEMES[k]['title']} — {len(THEMES[k]['questions'])} вопр."
        for k in theme_keys
    ]
    choice = st.selectbox("Тема", labels, index=0, label_visibility="collapsed")
    theme_key = theme_keys[labels.index(choice)]

    col1, col2 = st.columns(2)
    with col1:
        if st.button("▶ Начать тему", type="primary", use_container_width=True):
            start_quiz(theme_key)
    with col2:
        if st.button("🔀 Все темы подряд", use_container_width=True):
            start_all()


# ---------------------------------------------------------------
# ЭКРАН ВОПРОСА
# ---------------------------------------------------------------
def render_quiz():
    qs = st.session_state.questions
    idx = st.session_state.idx
    total = len(qs)

    if idx >= total:
        st.session_state.page = "result"
        st.rerun()
        return

    q = qs[idx]

    # --- Шапка ---
    theme_title = (
        "Все темы подряд"
        if st.session_state.theme_key == "__all__"
        else THEMES[st.session_state.theme_key]["title"]
    )
    st.caption(theme_title)

    progress_val = (idx + (1 if st.session_state.show_feedback else 0)) / total
    st.progress(progress_val)

    correct_so_far = sum(
        1 for i, a in st.session_state.answers.items() if a == qs[i]["ans"]
    )
    if st.session_state.answers:
        st.markdown(f"**Вопрос {idx + 1} из {total}** · ✅ верно: {correct_so_far}")
    else:
        st.markdown(f"**Вопрос {idx + 1} из {total}**")

    # --- Текст вопроса ---
    st.markdown(f"### {q['q']}")

    current = st.session_state.answers.get(idx, set())
    key_prefix = f"q_{idx}"

    # --- Режим выбора ---
    if not st.session_state.show_feedback:
        selected = set()
        for i, opt in enumerate(q["opts"]):
            checked = i in current
            if st.checkbox(f"{LETTERS[i]}) {opt}", value=checked, key=f"{key_prefix}_{i}"):
                selected.add(i)

        st.divider()
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("✅ Ответить", type="primary", use_container_width=True):
                st.session_state.answers[idx] = selected
                st.session_state.show_feedback = True
                st.rerun()
        with col2:
            if st.button("➡️ Далее", use_container_width=True):
                st.session_state.answers[idx] = selected
                st.session_state.idx += 1
                st.session_state.show_feedback = False
                st.rerun()

    # --- Режим разбора ---
    else:
        user_ans = current
        correct = q["ans"]
        ok = user_ans == correct

        if ok:
            st.success("✅ Верно!")
        else:
            st.error("❌ Неверно.")

        for i, opt in enumerate(q["opts"]):
            mark = ""
            if i in correct and i in user_ans:
                mark = "  ✅ выбрано верно"
            elif i in correct:
                mark = "  ✔ правильный"
            elif i in user_ans:
                mark = "  ✘ ваш ошибочный"
            st.markdown(f"- **{LETTERS[i]})** {opt}{mark}")

        st.divider()
        if st.button("➡️ Следующий вопрос", type="primary", use_container_width=True):
            st.session_state.idx += 1
            st.session_state.show_feedback = False
            st.rerun()


# ---------------------------------------------------------------
# РЕЗУЛЬТАТ
# ---------------------------------------------------------------
def render_result():
    qs = st.session_state.questions
    answers = st.session_state.answers

    correct_count = 0
    mistakes = []
    for i, q in enumerate(qs):
        user = answers.get(i, set())
        if user == q["ans"]:
            correct_count += 1
        else:
            mistakes.append((i, q, user))

    total = len(qs)
    pct = round(correct_count / total * 100, 1) if total else 0

    st.title("📊 Результат")
    col1, col2, col3 = st.columns(3)
    col1.metric("Верно", f"{correct_count}")
    col2.metric("Всего", f"{total}")
    col3.metric("Процент", f"{pct}%")
    st.progress(correct_count / total if total else 0)

    if mistakes:
        st.subheader("Вопросы с ошибками")
        for n, q, user in mistakes:
            short = q["q"] if len(q["q"]) <= 80 else q["q"][:77] + "..."
            with st.expander(f"№{n + 1}. {short}"):
                for i, opt in enumerate(q["opts"]):
                    mark = ""
                    if i in q["ans"] and i in user:
                        mark = "  ✅ выбрано верно"
                    elif i in q["ans"]:
                        mark = "  ✔ правильный"
                    elif i in user:
                        mark = "  ✘ ваш ошибочный"
                    st.markdown(f"- **{LETTERS[i]})** {opt}{mark}")
    else:
        st.success("🎉 Отлично! Ни одной ошибки.")

    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔁 Пройти ещё раз", use_container_width=True):
            if st.session_state.theme_key == "__all__":
                start_all()
            else:
                start_quiz(st.session_state.theme_key)
    with col2:
        if st.button("🏠 В меню", use_container_width=True):
            st.session_state.page = "menu"
            st.rerun()


# ---------------------------------------------------------------
# РОУТИНГ
# ---------------------------------------------------------------
render_sidebar()

if st.session_state.page == "menu":
    render_menu()
elif st.session_state.page == "quiz":
    render_quiz()
elif st.session_state.page == "result":
    render_result()
