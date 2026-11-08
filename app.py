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
# CSS — единый стиль вариантов «до» и «после» ответа
# ---------------------------------------------------------------
st.markdown("""
<style>
    .stButton > button {
        width: 100%;
        border-radius: 10px;
        padding: 0.6em 1em;
        font-size: 1rem;
    }
    h1, h2, h3 { margin-top: 0.4em; }
    .block-container { padding-top: 2rem; }

    /* ==========================================
       ДО ОТВЕТА: Стилизация чекбоксов под карточки
       ========================================== */
    
    /* 1. Контейнер чекбокса занимает всю ширину */
    div[data-testid="stCheckbox"] {
        width: 100% !important;
        display: block !important;
    }

    /* 2. Сама кликабельная область (label) становится карточкой */
    div[data-testid="stCheckbox"] label {
        display: flex !important;
        align-items: center !important;
        width: 100% !important; /* Растягиваем на всю ширину */
        box-sizing: border-box !important;
        padding: 12px 16px !important;
        margin: 0 0 8px 0 !important;
        border-radius: 10px !important;
        border-left: 6px solid #9e9e9e !important;
        background: #eceff1 !important;
        color: #1a1a1a !important;
        font-size: 1rem !important;
        line-height: 1.4 !important;
        cursor: pointer !important;
        transition: background 0.2s;
    }

    /* Убираем лишние отступы у текста внутри */
    div[data-testid="stCheckbox"] label p,
    div[data-testid="stCheckbox"] label span {
        color: inherit !important;
        font-size: 1rem !important;
        margin: 0 !important;
        padding: 0 !important;
    }

    /* Убираем стандартные отступы Streamlit, из-за которых появляются зазоры */
    div[data-testid="stCheckbox"] > div {
        width: 100% !important;
    }


    /* ==========================================
       ПОСЛЕ ОТВЕТА: HTML-карточки
       ========================================== */
    .opt-card {
        width: 100% !important;
        box-sizing: border-box !important;
        padding: 12px 16px !important;
        margin: 0 0 8px 0 !important; /* Такой же отступ, как у чекбоксов */
        border-radius: 10px !important;
        border-left: 6px solid #9e9e9e !important;
        background: #eceff1 !important;
        color: #1a1a1a !important;
        font-size: 1rem !important;
        line-height: 1.4 !important;
    }
    .opt-card b { color: inherit; }
    .opt-tag {
        font-weight: 700;
        margin-left: 8px;
        font-size: 0.9em;
    }

    /* Цвета (светлая тема) */
    .opt-green  { background: #c8e6c9 !important; border-left-color: #2e7d32 !important; color: #1b5e20 !important; }
    .opt-red    { background: #ffcdd2 !important; border-left-color: #c62828 !important; color: #b71c1c !important; }
    .opt-yellow { background: #fff59d !important; border-left-color: #f9a825 !important; color: #6d4c00 !important; }
    .opt-plain  { background: #eceff1 !important; border-left-color: #9e9e9e !important; color: #263238 !important; }

    /* ==========================================
       ТЁМНАЯ ТЕМА
       ========================================== */
    @media (prefers-color-scheme: dark) {
        div[data-testid="stCheckbox"] label,
        .opt-card {
            background: #2b2f36 !important;
            color: #e6e6e6 !important;
            border-left-color: #616161 !important;
        }
        
        .opt-green  { background: #1b3a20 !important; border-left-color: #66bb6a !important; color: #b9f6ca !important; }
        .opt-red    { background: #3a1b1b !important; border-left-color: #ef5350 !important; color: #ffcdd2 !important; }
        .opt-yellow { background: #3a331a !important; border-left-color: #fbc02d !important; color: #fff59d !important; }
        .opt-plain  { background: #2b2f36 !important; border-left-color: #616161 !important; color: #e6e6e6 !important; }
    }
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
        "answers": {},
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
# ПОДГОТОВКА ВОПРОСОВ
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
# ЦВЕТНОЙ РАЗБОР (после ответа)
# ---------------------------------------------------------------
def render_options_feedback(q, user_ans):
    correct = q["ans"]
    for i, opt in enumerate(q["opts"]):
        letter = LETTERS[i]
        chosen = i in user_ans
        is_correct = i in correct

        if chosen and is_correct:
            css = "opt-green"
            tag = "✅ выбрано верно"
        elif chosen and not is_correct:
            css = "opt-red"
            tag = "✘ ваш ошибочный"
        elif is_correct and not chosen:
            css = "opt-yellow"
            tag = "✔ правильный (не выбран)"
        else:
            css = "opt-plain"
            tag = ""

        html = (
            f'<div class="opt-card {css}">'
            f'<b>{letter})</b> {opt}'
            f'<span class="opt-tag">{tag}</span>'
            f'</div>'
        )
        st.markdown(html, unsafe_allow_html=True)


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

    st.markdown(f"### {q['q']}")

    current = st.session_state.answers.get(idx, set())
    key_prefix = f"q_{idx}"

    # --- Режим выбора: чекбоксы, стилизованные под те же карточки ---
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

        render_options_feedback(q, user_ans)

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
                render_options_feedback(q, user)
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
