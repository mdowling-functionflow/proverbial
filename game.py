import datetime
import streamlit as st

# -------------------------
# Data Setup: Ten Proverbs
# -------------------------
PUZZLES = [
    {
        "acronym": "A B I T H I W T I T B",
        "phrase": "A Bird In The Hand Is Worth Two In The Bush",
        "hint": "What you already have is more valuable than what you hope to get."
    },
    {
        "acronym": "B L T N",
        "phrase": "Better Late Than Never",
        "hint": "It's preferable to do something eventually than not at all."
    },
    {
        "acronym": "D C Y C B T H",
        "phrase": "Don't Count Your Chickens Before They Hatch",
        "hint": "Don't assume success or outcomes before they are certain."
    },
    {
        "acronym": "E C H A S L",
        "phrase": "Every Cloud Has A Silver Lining",
        "hint": "There's some good in every bad situation."
    },
    {
        "acronym": "T M C S T B",
        "phrase": "Too Many Cooks Spoil The Broth",
        "hint": "Having too many people involved can ruin a task."
    },
    {
        "acronym": "W I R D A T R D",
        "phrase": "When In Rome Do As The Romans Do",
        "hint": "Adapt to the customs of the place you're visiting."
    },
    {
        "acronym": "W T I A W T I A W",
        "phrase": "Where There Is A Will There Is A Way",
        "hint": "Determination can overcome obstacles."
    },
    {
        "acronym": "A P I W A T W",
        "phrase": "A Picture Is Worth A Thousand Words",
        "hint": "Visual images convey meaning more effectively than lengthy descriptions."
    },
    {
        "acronym": "A S L T W",
        "phrase": "Actions Speak Louder Than Words",
        "hint": "What you do matters more than what you say."
    },
    {
        "acronym": "P M P",
        "phrase": "Practice Makes Perfect",
        "hint": "Repeated practice leads to improvement."
    }
]


def get_daily_puzzle():
    today = datetime.date.today()
    index = (today.year + today.month + today.day) % len(PUZZLES)
    return PUZZLES[index]


def evaluate_guess(guess, solution_words):
    guess_words = guess.strip().split()
    result = []
    solution_copy = solution_words[:]

    # First pass: mark greens (✓)
    for i, word in enumerate(guess_words):
        if i < len(solution_words) and word.lower() == solution_words[i].lower():
            result.append("✓")
            solution_copy[i] = None
        else:
            result.append(None)

    # Second pass: mark yellows (~) and grays (X)
    for i, word in enumerate(guess_words):
        if result[i] is None:
            lw = word.lower()
            if lw in [w.lower() for w in solution_copy if w is not None]:
                result[i] = "~"
                for si, sw in enumerate(solution_copy):
                    if sw and sw.lower() == lw:
                        solution_copy[si] = None
                        break
            else:
                result[i] = "X"

    return result


def format_feedback_line(guess, feedback):
    """Format a single guess line with colored background for each word."""
    guess_words = guess.strip().split()
    styled_words = []
    for word, mark in zip(guess_words, feedback):
        if mark == "✓":
            # Green background
            styled_words.append(
                f"<span style='background-color:#c7f9cc;padding:0.2em 0.4em;border-radius:0.3em;'>{word}</span>")
        elif mark == "~":
            # Yellow background
            styled_words.append(
                f"<span style='background-color:#fff3b0;padding:0.2em 0.4em;border-radius:0.3em;'>{word}</span>")
        else:
            # Gray background
            styled_words.append(
                f"<span style='background-color:#f4cccc;padding:0.2em 0.4em;border-radius:0.3em;'>{word}</span>")
    return " ".join(styled_words)


# -------------------------
# Streamlit App
# -------------------------
st.set_page_config(page_title="The Proverbial Challenge", page_icon="🧩")

st.markdown("<h1 style='text-align:center; font-family:Georgia;'>The Proverbial Challenge</h1>", unsafe_allow_html=True)
st.markdown(
    "<p style='text-align:center; font-size:1.2em; font-family:Georgia;'>Decode the daily proverb from its acronym. You have 6 attempts!</p>",
    unsafe_allow_html=True)

if "puzzle" not in st.session_state:
    st.session_state.puzzle = get_daily_puzzle()
    st.session_state.solution = st.session_state.puzzle["phrase"]
    st.session_state.acronym = st.session_state.puzzle["acronym"]
    st.session_state.solution_words = st.session_state.solution.split()
    st.session_state.attempts_left = 6
    st.session_state.guesses = []
    st.session_state.feedbacks = []
    st.session_state.hint_used = False
    st.session_state.game_over = False

# Display puzzle info
st.markdown(f"<h3 style='font-family:Georgia;'>Acronym: {st.session_state.acronym}</h3>", unsafe_allow_html=True)
st.write(f"**Attempts left:** {st.session_state.attempts_left}")

# Display previous attempts
if st.session_state.guesses:
    st.markdown("<h4 style='font-family:Georgia;'>Previous Attempts</h4>", unsafe_allow_html=True)
    for i, (g, f) in enumerate(zip(st.session_state.guesses, st.session_state.feedbacks), start=1):
        formatted_line = format_feedback_line(g, f)
        st.markdown(f"**Attempt {i}:**", unsafe_allow_html=True)
        st.markdown(formatted_line, unsafe_allow_html=True)


def check_game_status():
    if st.session_state.attempts_left <= 0 and not st.session_state.game_over:
        st.error("No attempts left! The solution was:")
        st.info(st.session_state.solution)
        st.session_state.game_over = True
    elif st.session_state.feedbacks and all(
            m == "✓" for m in st.session_state.feedbacks[-1]) and not st.session_state.game_over:
        st.success("Congratulations! You solved it!")
        st.balloons()
        st.session_state.game_over = True


check_game_status()

if not st.session_state.game_over:
    with st.form("guess_form"):
        guess = st.text_input("Enter your full guess (complete proverb):", "")
        submit = st.form_submit_button("Submit Guess")

        if submit:
            guess_words = guess.strip().split()
            if len(guess_words) != len(st.session_state.solution_words):
                st.warning(f"Your guess must have {len(st.session_state.solution_words)} words. Try again!")
            else:
                feedback = evaluate_guess(guess, st.session_state.solution_words)
                st.session_state.guesses.append(guess)
                st.session_state.feedbacks.append(feedback)
                st.session_state.attempts_left -= 1

                # Offer hint after 3 attempts if not used
                if len(st.session_state.guesses) == 3 and not st.session_state.hint_used:
                    st.info(f"**Hint:** {st.session_state.puzzle['hint']}")
                    st.session_state.hint_used = True

                check_game_status()

# If game over, no new guesses. Could offer a "Restart" button for demo/testing.
if st.session_state.game_over:
    if st.button("Try Another Random Proverb"):
        for key in ["puzzle", "solution", "acronym", "solution_words", "attempts_left", "guesses", "feedbacks",
                    "hint_used", "game_over"]:
            if key in st.session_state:
                del st.session_state[key]
        st.experimental_rerun()

