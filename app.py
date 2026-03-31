import streamlit as st
from logic import create_card_pair, load_df, DIFFICULTIES

# --- 1. PAGE CONFIG & STYLE ---
st.set_page_config(page_title="DOBBLE aminových kyselin", layout="wide")

st.markdown("""
    <style>
    div.stButton > button p {
        font-size: 22px !important;
        font-weight: bold;
    }
    [data-testid="stVerticalBlock"] > div:has(div.stButton) {
        background-color: #7495ad;
        padding: 20px;
        border-radius: 15px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. SESSION STATE ---
if 'df' not in st.session_state:
    st.session_state.df = load_df()
    st.session_state.score = 0
    st.session_state.difficulty = 'easy'
    st.session_state.first_click = None
    st.session_state.mobile = False

if 'round_data' not in st.session_state:
    st.session_state.round_data = create_card_pair(st.session_state.df, st.session_state.difficulty)

winner_id, card1, card2 = st.session_state.round_data

# --- 3. HELPER FUNCTIONS ---
def reset_game(new_diff):
    st.session_state.difficulty = new_diff
    st.session_state.round_data = create_card_pair(st.session_state.df, new_diff)
    st.session_state.first_click = None

def reset_selection():
    st.session_state.first_click = None

def handle_click(clicked_name, card_id):
    if st.session_state.first_click is None:
        st.session_state.first_click = {'name': clicked_name, 'card': card_id}
    else:
        first = st.session_state.first_click
        if first['card'] != card_id:
            if clicked_name == first['name'] and clicked_name == winner_id:
                st.session_state.score += 1
                st.balloons()
                st.session_state.round_data = create_card_pair(st.session_state.df, st.session_state.difficulty)
        st.session_state.first_click = None

def render_card(card_items, side_id, column_obj):
    with column_obj:
        st.header(f"Kartička {side_id}")
        locked_side = st.session_state.first_click['card'] if st.session_state.first_click else None
        for i, item in enumerate(card_items):
            desc = str(item['desc'])
            if desc.lower().endswith(('.png', '.jpg', '.jpeg')):
                st.image(desc, use_container_width=True)
                btn_label = "SELECT STRUCTURE"
            else:
                btn_label = desc.replace('[', r'\[').replace(']', r'\]')
            st.button(
                btn_label,
                key=f"btn_{side_id}_{i}_{item['name']}",
                disabled=(locked_side == side_id),
                use_container_width=True,
                on_click=handle_click,
                args=(item['name'], side_id)
            )

def render_stats(column_obj):
    """Renders score, status, and the reset-selection button."""
    with column_obj:
        st.metric("BODY", st.session_state.score)

        if st.session_state.first_click:
            selected_name = st.session_state.first_click['name']
            selected_card = st.session_state.first_click['card']
            st.info(f"✅ Vybráno: **{selected_name}** (Kartička {selected_card})")
            st.button(
                "↩️ Zrušit výběr",
                on_click=reset_selection,
                use_container_width=True,
            )
        else:
            st.write("Vyber popis na jedné kartičce, pak ho najdi na druhé.")

# --- 4. UI ---
st.title("🧬 DOBBLE aminových kyselin")
st.write("Najdi **jedinou** aminokyselinu, která je na obou kartách!")

# Top row: difficulty + mobile toggle
top_left, top_right = st.columns([3, 1])
with top_left:
    d_cols = st.columns(3)
    with d_cols[0]:
        if st.button("🟢 Bc. student", use_container_width=True): reset_game('easy')
    with d_cols[1]:
        if st.button("🟡 PhD student", use_container_width=True): reset_game('medium')
    with d_cols[2]:
        if st.button("🔴 Profesor", use_container_width=True): reset_game('hard')
with top_right:
    st.session_state.mobile = st.toggle("📱 Mobil", value=st.session_state.mobile)

st.divider()

# Pull fresh round data (may have changed via handle_click callback)
winner_id, card1, card2 = st.session_state.round_data

if st.session_state.mobile:
    # --- MOBILE: vertical stack ---
    render_card(card1, 'A', st.container())
    st.divider()
    render_stats(st.container())
    st.divider()
    render_card(card2, 'B', st.container())
else:
    # --- DESKTOP: side-by-side ---
    col_left, col_mid, col_right = st.columns([2, 1, 2])
    render_card(card1, 'A', col_left)
    render_stats(col_mid)
    render_card(card2, 'B', col_right)
