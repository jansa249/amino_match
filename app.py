import streamlit as st
from logic import create_card_pair, load_df, DIFFICULTIES

# --- 1. PAGE CONFIG & STYLE ---
st.set_page_config(page_title="DOBBLE aminových kyselin", layout="wide")

# Custom CSS for Big, Readable Buttons (Great for a touchscreen booth!)
st.markdown("""
    <style>
    /* Make the button text large and bold */
    div.stButton > button p {
        font-size: 32px !important;
        font-weight: bold;
    }
    /* Optional: Make the cards look like distinct sections */
    [data-testid="stVerticalBlock"] > div:has(div.stButton) {
        background-color: #7495ad;
        padding: 20px;
        border-radius: 15px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. SESSION STATE (The Game's Memory) ---
if 'df' not in st.session_state:
    st.session_state.df = load_df()
    st.session_state.score = 0
    st.session_state.difficulty = 'easy'
    st.session_state.first_click = None # Stores {'name': 'Alanine', 'card': 'A'}

# Only generate a new round if one doesn't exist
if 'round_data' not in st.session_state:
    st.session_state.round_data = create_card_pair(st.session_state.df, st.session_state.difficulty)

# Pull the current round data
winner_id, card1, card2 = st.session_state.round_data

# --- 3. HELPER FUNCTIONS ---
def reset_game(new_diff):
    """Changes difficulty and resets the board."""
    st.session_state.difficulty = new_diff
    st.session_state.round_data = create_card_pair(st.session_state.df, new_diff)
    st.session_state.first_click = None

def handle_click(clicked_name, card_id):
    """Handles the two-click matching logic."""
    if st.session_state.first_click is None:
        # First click: Save it and lock the card
        st.session_state.first_click = {'name': clicked_name, 'card': card_id}
    else:
        first = st.session_state.first_click
        # Second click must be on the OTHER card
        if first['card'] != card_id:
            if clicked_name == first['name'] and clicked_name == winner_id:
                st.session_state.score += 1
                st.balloons()
                # Correct! Move to next round
                st.session_state.round_data = create_card_pair(st.session_state.df, st.session_state.difficulty)
            else:
                # st.toast(f"Not a match! ({first['name']} vs {clicked_name})", icon="❌")
                pass
        
        # Reset selection regardless of outcome
        st.session_state.first_click = None

# --- 4. THE USER INTERFACE ---
st.title("🧬 DOBBLE aminových kyselin")
st.write("Najdi **jedinou** aminokyselinu, která je na obou kartách!")

# Difficulty Selection Row
d_cols = st.columns(3)
with d_cols[0]:
    if st.button("🟢 Bc. student", use_container_width=True): reset_game('easy')
with d_cols[1]:
    if st.button("🟡 PhD student", use_container_width=True): reset_game('medium')
with d_cols[2]:
    if st.button("🔴 Profesor", use_container_width=True): reset_game('hard')

st.divider()

# Layout: Card A | Stats | Card B
col_left, col_mid, col_right = st.columns([2, 1, 2])

# Check if a card is currently "locked"
locked_side = st.session_state.first_click['card'] if st.session_state.first_click else None

def render_card(card_items, side_id, column_obj):
    with column_obj:
        st.header(f"Kartička {side_id}")
        for i, item in enumerate(card_items):
            desc = str(item['desc'])
            
            # IMAGE SUPPORT: If the description looks like a file path, show the image
            if desc.lower().endswith(('.png', '.jpg', '.jpeg')):
                st.image(desc, use_container_width=True)
                btn_label = "SELECT STRUCTURE"
            else:
                btn_label = desc.replace('[', r'\[').replace(']', r'\]')

            # THE BUTTON: Unique key includes side, index, and name to prevent DuplicateKeyError
            st.button(
                btn_label,
                key=f"btn_{side_id}_{i}_{item['name']}",
                disabled=(locked_side == side_id),
                use_container_width=True,
                on_click=handle_click,
                args=(item['name'], side_id)
            )

# Render Card A and Card B
render_card(card1, 'A', col_left)
render_card(card2, 'B', col_right)

# Center Column: Score and Status
with col_mid:
    st.metric("BODY", st.session_state.score)
    if st.session_state.first_click:
        # st.info(f"Selected **{st.session_state.first_click['name']}** on Card {st.session_state.first_click['card']}. Match it on the other side!")
        pass
    else:
        st.write("Vyber popis")
    
    # if st.checkbox("Nápověda"):
    #     st.write(f"**{winner_id}**")
