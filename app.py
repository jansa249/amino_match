import streamlit as st
from logic import create_card_pair, load_df, DIFFICULTIES

# --- 1. PAGE CONFIG & STYLE ---
st.set_page_config(page_title="AminoMatch", layout="wide")

CARD_COLORS = {'A': '#4a7c9e', 'B': '#7a4a6e'}

DIFF_LABELS = {
    'easy':   'Student/ka',
    'medium': 'Doktorand/ka',
    'hard':   'Profesor/ka',
}

# --- 2. SESSION STATE ---
if 'df' not in st.session_state:
    st.session_state.df = load_df()
    st.session_state.score = 0
    st.session_state.difficulty = 'easy'
    st.session_state.first_click = None
    st.session_state.mobile = False

if 'round_data' not in st.session_state:
    st.session_state.round_data = create_card_pair(st.session_state.df, st.session_state.difficulty)

# --- 3. STYLES ---
# Read mobile state once at top so styles are always in sync
mobile = st.session_state.mobile
btn_font    = "16px" if mobile else "22px"
btn_padding = "2px 8px" if mobile else "8px 16px"

st.markdown(f"""
    <style>
    div.stButton > button p {{
        font-size: {btn_font} !important;
        font-weight: bold;
    }}
    div.stButton > button {{
        padding: {btn_padding} !important;
    }}
    div.stButton {{
        margin-bottom: -8px !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 4. HELPER FUNCTIONS ---
def reset_game(new_diff):
    st.session_state.difficulty = new_diff
    st.session_state.round_data = create_card_pair(st.session_state.df, new_diff)
    st.session_state.first_click = None

def reset_selection():
    st.session_state.first_click = None

def toggle_mobile():
    st.session_state.mobile = not st.session_state.mobile

def handle_click(clicked_name, card_id):
    winner_id = st.session_state.round_data[0]
    if st.session_state.first_click is None:
        st.session_state.first_click = {'name': clicked_name, 'card': card_id}
    else:
        first = st.session_state.first_click
        if first['card'] != card_id:
            if clicked_name == first['name'] and clicked_name == winner_id:
                st.session_state.score += 1
                st.balloons()
                # st.success("✅ Správně!")
                st.session_state.round_data = create_card_pair(st.session_state.df, st.session_state.difficulty)
            else:
                st.snow()
        st.session_state.first_click = None

def render_card(card_items, side_id, col):
    color = CARD_COLORS[side_id]
    locked_side = st.session_state.first_click['card'] if st.session_state.first_click else None
    with col:
        st.markdown(
            f'<div style="background:{color};padding:8px 14px 14px 14px;border-radius:12px;">',
            unsafe_allow_html=True
        )
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
        st.markdown('</div>', unsafe_allow_html=True)

# --- 5. UI ---
st.title("🧬 AminoMatch")

# Row 1: difficulty buttons
d_cols = st.columns(3)
for col, (diff_key, diff_label) in zip(d_cols, DIFF_LABELS.items()):
    with col:
        is_active = st.session_state.difficulty == diff_key
        st.button(
            f"{'▶ ' if is_active else ''}{diff_label}",
            use_container_width=True,
            type="primary" if is_active else "secondary",
            on_click=reset_game,
            args=(diff_key,),
            key=f"diff_{diff_key}",
        )

# Row 2: status + zrušit | score | mobile toggle
row2_left, row2_mid, row2_right = st.columns([3, 1, 1])
with row2_left:
    something_selected = st.session_state.first_click is not None
    status_cols = st.columns([3, 1])
    # with status_cols[0]:
    #     if something_selected:
    #         st.markdown("✅ **Vybrána první kartička** — najdi shodu na druhé!")
    #     else:
    #         st.markdown("Najdi jedinou aminokyselinu, která je na obou kartách!")
    with status_cols[1]:
        st.button("↩️ Zrušit", on_click=reset_selection,
                  use_container_width=True, disabled=not something_selected)
with row2_mid:
    st.metric("BODY", st.session_state.score)
with row2_right:
    # on_change fires before rerun so styles are in sync on the same render
    st.toggle("📱 Mobil", value=st.session_state.mobile,
              on_change=toggle_mobile, key="mobile_toggle")

st.divider()

winner_id, card1, card2 = st.session_state.round_data

if mobile:
    render_card(card1, 'A', st.container())
    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
    render_card(card2, 'B', st.container())
else:
    col_left, col_right = st.columns(2)
    render_card(card1, 'A', col_left)
    render_card(card2, 'B', col_right)
