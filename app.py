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
)

# ---------------------------------------------------------------
# СЕССИОННОЕ СОСТОЯНИЕ
# ---------------------------------------------------------------
def init_state():
    defaults = {
        "page": "menu",          # menu | quiz | result
        "theme_key": None,       # ключ темы
        "questions": [],         # подготовленные вопросы (перемешанные)
        "idx": 0,                # текущий индекс
        "answers": {},           # {idx: set(индексов выбранных opts)}
        "show_feedback": False,  # показывать ли разбор текущего вопроса
        "shuffle_opts": True,
        "shuffle_q": True,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


init_state()

# ---------------------------------------------------------------
# ПОДГОТОВКА ВОПРОСОВ
# ---------------------------------------------------------------
def prepare_questions(theme_key, shuffle_q: bool, shuffle_opts: bool):
    """
    Возвращает список вопросов в формате:
    {
      "q": "...",
      "opts": [текст1, текст2, ...],   # уже перемешанные
      "ans": {индексы правильных в новом opts},
    }
    """
    raw = THEMES[theme_key]["questions"]
    prepared = []

    for item in raw:
        q_text = item["q"]
        # список (текст, флаг_правильный)
        pairs = [(opt, i in item["ans"]) for i, opt in enumerate(item["opts"])]
        if shuffle_opts:
            random.shuffle(pairs)
        new_opts = [t for t, _ in pairs]
        new_ans = {i for i, (_, flag) in enumerate(pairs) if flag}
        prepared.append({
            "q": q_text,
            "opts": new_opts,
            "ans": new_ans,
        })

    if shuffle_q:
        random.shuffle(prepared)

    return prepared


# ---------------------------------------------------------------
# ЭКРАН: МЕНЮ
# ---------------------------------------------------------------
def render_menu():
    st.title("🩺 Тренажёр по топографической анатомии")
    st.caption("Оперативная хирургия · тесты для педиатрического факультета")

    st.subheader("Настройки")
    col1, col2 = st.columns(2)
    with col1:
        st.session_state.shuffle_opts = st.toggle(
            "Перемешивать варианты ответов",
            value=st.session_state.shuffle_opts,
        )
    with col2:
        st.session_state.shuffle_q = st.toggle(
            "Перемешивать порядок вопросов",
            value=st.session_state.shuffle_q,
        )

    st.subheader("Выбор темы")
    theme_keys = sorted(THEMES.keys(), key=lambda x: int(x))
    labels = [f"{k}. {THEMES[k]['title']} ({len(THEMES[k]['questions'])} вопр.)"
              for k in theme_keys]
    choice = st.selectbox("Тема", labels, index=0)
    theme_key = theme_keys[labels.index(choice)]

    col_a, col_b = st.columns([1, 1])
    with col_a:
        if st.button("▶ Начать тему", type="primary", use_container_width=True):
            start_quiz(theme_key)
    with col_b:
        if st.button("🔀 Пройти всё подряд", use_container_width=True):
            start_all()

    st.divider()
    st.caption("Совет: включи перемешивание — так честнее тренироваться.")


# ---------------------------------------------------------------
# ЗАПУСК ТЕСТА
# ---------------------------------------------------------------
def start_quiz(theme_key):
    st.session_state.theme_key = theme_key
    st.session_state.questions = prepare_questions(
        theme_key,
        shuffle_q=st.session_state.shuffle_q,
        shuffle_opts=st.session_state.shuffle_opts,
    )
    st.session_state.idx = 0
    st.session_state.answers = {}
    st.session_state.show_feedback = False
    st.session_state.page = "quiz"
    st.rerun()


def start_all():
    # Собираем вопросы из всех тем
    all_questions = []
    for key in sorted(THEMES.keys(), key=lambda x: int(x)):
        all_questions.extend(THEMES[key]["questions"])
    # Перемешиваем
    if st.session_state.shuffle_q:
        random.shuffle(all_questions)

    prepared = []
    for item in all_questions:
        pairs = [(opt, i in item["ans"]) for i, opt in enumerate(item["opts"])]
        if st.session_state.shuffle_opts:
            random.shuffle(pairs)
        new_opts = [t for t, _ in pairs]
        new_ans = {i for i, (_, flag) in enumerate(pairs) if flag}
        prepared.append({"q": item["q"], "opts": new_opts, "ans": new_ans})

    st.session_state.theme_key = "__all__"
    st.session_state.questions = prepared
    st.session_state.idx = 0
    st.session_state.answers = {}
    st.session_state.show_feedback = False
    st.session_state.page = "quiz"
    st.rerun()


# ---------------------------------------------------------------
# ЭКРАН: ВОПРОС
# ---------------------------------------------------------------
LETTERS = ["А", "Б", "В", "Г", "Д", "Е", "Ж", "З"]


def render_quiz():
    qs = st.session_state.questions
    idx = st.session_state.idx
    total = len(qs)

    if idx >= total:
        st.session_state.page = "result"
        st.rerun()
        return

    q = qs[idx]

    # Прогресс
    st.progress((idx) / total)
    theme_title = (
        "Все темы подряд"
        if st.session_state.theme_key == "__all__"
        else THEMES[st.session_state.theme_key]["title"]
    )
    st.caption(f"{theme_title} · Вопрос {idx + 1} из {total}")

    # Текст вопроса
    st.markdown(f"### {q['q']}")

    # Варианты
    key = f"q_{idx}"
    current = st.session_state.answers.get(idx, set())

    # Мультивыбор: используем чекбоксы в контейнере
    selected = set()
    for i, opt in enumerate(q["opts"]):
        checked = i in current
        if st.checkbox(f"{LETTERS[i]}) {opt}", value=checked, key=f"{key}_{i}"):
            selected.add(i)

    st.divider()
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("✅ Ответить", type="primary", use_container_width=True):
            st.session_state.answers[idx] = selected
            st.session_state.show_feedback = True
            st.rerun()
    with col2:
        if st.button("⏭ Пропустить", use_container_width=True):
            st.session_state.answers[idx] = selected
            st.session_state.show_feedback = True
            st.rerun()

    # Разбор ответа
    if st.session_state.show_feedback:
        st.divider()
        user_ans = st.session_state.answers.get(idx, set())
        correct = q["ans"]
        ok = user_ans == correct

        if ok:
            st.success("✅ Верно!")
        else:
            st.error("❌ Неверно.")

        # показываем разметку
        for i, opt in enumerate(q["opts"]):
            mark = ""
            if i in correct and i in user_ans:
                mark = "  ✅ выбрано верно"
            elif i in correct:
                mark = "  ✔ правильный"
            elif i in user_ans:
                mark = "  ✘ ваш ошибочный"
            st.markdown(f"- **{LETTERS[i]})** {opt}{mark}")

        if st.button("➡ Следующий вопрос", type="primary", use_container_width=True):
            st.session_state.idx += 1
            st.session_state.show_feedback = False
            st.rerun()


# ---------------------------------------------------------------
# ЭКРАН: РЕЗУЛЬТАТ
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
            mistakes.append((i, q["q"]))

    total = len(qs)
    pct = round(correct_count / total * 100, 1) if total else 0

    st.title("📊 Результат")
    st.metric("Верно", f"{correct_count} / {total}", f"{pct}%")
    st.progress(correct_count / total if total else 0)

    if mistakes:
        st.subheader("Вопросы с ошибками")
        for n, text in mistakes:
            short = text if len(text) <= 100 else text[:97] + "..."
            st.markdown(f"- **№{n + 1}:** {short}")
    else:
        st.success("🎉 Отлично! Ни одной ошибки.")

    st.divider()
    if st.button("🔁 Пройти ещё раз", use_container_width=True):
        if st.session_state.theme_key == "__all__":
            start_all()
        else:
            start_quiz(st.session_state.theme_key)
    if st.button("🏠 В меню", use_container_width=True):
        st.session_state.page = "menu"
        st.rerun()


# ---------------------------------------------------------------
# РОУТИНГ
# ---------------------------------------------------------------
if st.session_state.page == "menu":
    render_menu()
elif st.session_state.page == "quiz":
    render_quiz()
elif st.session_state.page == "result":
    render_result()