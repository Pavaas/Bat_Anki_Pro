import streamlit as st
import random
import time
import datetime
import pandas as pd
import plotly.express as px

# Initialize session state variables
def init_session_state():
    if 'decks' not in st.session_state:
        st.session_state.decks = {
            "Mathematics": [
                {"front": "Pythagorean theorem", "back": "a² + b² = c²", "interval": 1, "ease": 2.5, "reps": 0, "last_review": None},
                {"front": "Derivative of sin(x)", "back": "cos(x)", "interval": 1, "ease": 2.5, "reps": 0, "last_review": None},
                {"front": "Quadratic formula", "back": "x = [-b ± √(b² - 4ac)] / 2a", "interval": 1, "ease": 2.5, "reps": 0, "last_review": None},
            ],
            "Spanish Vocabulary": [
                {"front": "Hello", "back": "Hola", "interval": 1, "ease": 2.5, "reps": 0, "last_review": None},
                {"front": "Goodbye", "back": "Adiós", "interval": 1, "ease": 2.5, "reps": 0, "last_review": None},
                {"front": "Thank you", "back": "Gracias", "interval": 1, "ease": 2.5, "reps": 0, "last_review": None},
            ]
        }
    
    if 'current_deck' not in st.session_state:
        st.session_state.current_deck = "Mathematics"
    
    if 'study_mode' not in st.session_state:
        st.session_state.study_mode = False
    
    if 'current_card_index' not in st.session_state:
        st.session_state.current_card_index = 0
    
    if 'card_flipped' not in st.session_state:
        st.session_state.card_flipped = False
    
    if 'new_deck_name' not in st.session_state:
        st.session_state.new_deck_name = ""
    
    if 'new_card_front' not in st.session_state:
        st.session_state.new_card_front = ""
    
    if 'new_card_back' not in st.session_state:
        st.session_state.new_card_back = ""
    
    if 'study_history' not in st.session_state:
        st.session_state.study_history = []

# Spaced repetition algorithm
def update_card(card, rating):
    if rating == "again":
        card["ease"] = max(1.3, card["ease"] - 0.2)
        card["interval"] = 1
    elif rating == "hard":
        card["ease"] = max(1.3, card["ease"] - 0.15)
        card["interval"] = max(1, card["interval"] * 1.2)
    elif rating == "good":
        card["interval"] = card["interval"] * card["ease"]
    elif rating == "easy":
        card["ease"] = card["ease"] + 0.15
        card["interval"] = card["interval"] * card["ease"] * 1.3
    
    card["reps"] += 1
    card["last_review"] = datetime.datetime.now()
    return card

# Calculate deck statistics
def deck_stats(deck_name):
    deck = st.session_state.decks.get(deck_name, [])
    if not deck:
        return 0, 0, 0
    
    total_cards = len(deck)
    mastered = sum(1 for card in deck if card.get("reps", 0) >= 3)
    due_cards = sum(1 for card in deck if card.get("last_review") is None or 
                 (datetime.datetime.now() - card["last_review"]).days >= card["interval"])
    
    return total_cards, mastered, due_cards

# Card styling
def card_style(content, flipped=False):
    bg_color = "#4361ee" if not flipped else "#3f37c9"
    text_color = "#ffffff"
    border_radius = "20px"
    padding = "40px"
    font_size = "1.8rem" if len(content) < 50 else "1.2rem"
    
    return f"""
    <div style="
        background: linear-gradient(135deg, {bg_color}, #4cc9f0);
        color: {text_color};
        border-radius: {border_radius};
        padding: {padding};
        text-align: center;
        box-shadow: 0 15px 35px rgba(67, 97, 238, 0.3);
        margin: 20px auto;
        min-height: 300px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: {font_size};
        font-weight: bold;
    ">
        {content}
    </div>
    """

# Main app
def main():
    st.set_page_config(
        page_title="BatAnkiPro - Advanced Flashcards",
        page_icon="🧠",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    init_session_state()
    
    # Custom CSS
    st.markdown("""
    <style>
    /* Main styling */
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    
    /* Sidebar styling */
    .st-emotion-cache-6qob1r {
        background: linear-gradient(135deg, #4361ee 0%, #3f37c9 100%);
        color: white;
    }
    
    /* Button styling */
    .stButton>button {
        border-radius: 50px;
        padding: 10px 20px;
        font-weight: bold;
        transition: all 0.3s ease;
        border: none;
    }
    
    .stButton>button:first-child {
        background-color: #4361ee;
        color: white;
    }
    
    .stButton>button:hover {
        transform: translateY(-3px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    }
    
    /* Card styling */
    .deck-card {
        border-radius: 15px;
        padding: 20px;
        background: white;
        box-shadow: 0 5px 15px rgba(0,0,0,0.05);
        margin-bottom: 20px;
        transition: all 0.3s ease;
        border: 2px solid #e2e8f0;
    }
    
    .deck-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        border-color: #4361ee;
    }
    
    /* Progress bar styling */
    .stProgress>div>div>div {
        background: linear-gradient(90deg, #4361ee, #4cc9f0);
    }
    
    /* Section headers */
    h1, h2, h3 {
        color: #3f37c9;
    }
    
    /* Difficulty buttons */
    .difficulty-btn {
        margin: 5px;
        border-radius: 50px !important;
        padding: 10px 20px !important;
    }
    
    #again-btn {
        background-color: #f72585 !important;
        color: white !important;
    }
    
    #hard-btn {
        background-color: #ff9e00 !important;
        color: white !important;
    }
    
    #good-btn {
        background-color: #4361ee !important;
        color: white !important;
    }
    
    #easy-btn {
        background-color: #06d6a0 !important;
        color: white !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.title("🧠 BatAnkiPro")
        st.markdown("Smart flashcards with spaced repetition")
        
        # Navigation
        app_mode = st.radio("Navigation", ["🏠 Dashboard", "📚 Study", "🆕 Create Cards", "📊 Statistics"])
        
        st.markdown("---")
        st.subheader("Your Decks")
        
        # Deck selection
        for deck in st.session_state.decks.keys():
            total, mastered, due = deck_stats(deck)
            selected = st.button(f"{deck} ({due} due)", key=f"select_{deck}",
                                use_container_width=True,
                                type="primary" if st.session_state.current_deck == deck else "secondary")
            if selected:
                st.session_state.current_deck = deck
                st.session_state.study_mode = False
                st.experimental_rerun()
        
        # Create new deck
        st.markdown("---")
        st.subheader("Create New Deck")
        new_deck = st.text_input("Deck name", key="new_deck_name")
        if st.button("Create Deck", key="create_deck"):
            if new_deck and new_deck not in st.session_state.decks:
                st.session_state.decks[new_deck] = []
                st.session_state.current_deck = new_deck
                st.success(f"Deck '{new_deck}' created!")
                st.experimental_rerun()
            elif new_deck in st.session_state.decks:
                st.error("Deck name already exists")
    
    # Main content
    if app_mode == "🏠 Dashboard":
        st.title("Dashboard")
        st.markdown("Welcome to BatAnkiPro - Your smart flashcard learning system")
        
        # Deck statistics
        col1, col2, col3 = st.columns(3)
        total_decks = len(st.session_state.decks)
        total_cards = sum(len(deck) for deck in st.session_state.decks.values())
        total_mastered = sum(deck_stats(deck)[1] for deck in st.session_state.decks)
        
        with col1:
            st.metric("Total Decks", total_decks)
        with col2:
            st.metric("Total Cards", total_cards)
        with col3:
            st.metric("Mastered Cards", total_mastered)
        
        st.subheader("Your Decks")
        
        # Deck cards
        for deck in st.session_state.decks.keys():
            total, mastered, due = deck_stats(deck)
            progress = mastered / total if total > 0 else 0
            
            with st.container():
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"### {deck}")
                    st.markdown(f"**{due}** cards due for review | **{mastered}/{total}** mastered")
                    st.progress(progress)
                with col2:
                    if st.button(f"Study {deck}", key=f"study_{deck}"):
                        st.session_state.current_deck = deck
                        st.session_state.study_mode = True
                        st.session_state.current_card_index = 0
                        st.session_state.card_flipped = False
                        st.experimental_rerun()
        
        # Quick actions
        st.subheader("Quick Actions")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Add New Cards", use_container_width=True):
                app_mode = "🆕 Create Cards"
                st.experimental_rerun()
        with col2:
            if st.button("Review Statistics", use_container_width=True):
                app_mode = "📊 Statistics"
                st.experimental_rerun()
    
    elif app_mode == "📚 Study":
        st.title(f"Studying: {st.session_state.current_deck}")
        
        deck = st.session_state.decks.get(st.session_state.current_deck, [])
        if not deck:
            st.warning("This deck is empty. Add some cards first.")
            return
        
        # Get current card
        card = deck[st.session_state.current_card_index]
        
        # Display card
        if st.session_state.card_flipped:
            st.markdown(card_style(card["back"], flipped=True), unsafe_allow_html=True)
        else:
            st.markdown(card_style(card["front"]), unsafe_allow_html=True)
        
        # Card navigation
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Flip Card", use_container_width=True):
                st.session_state.card_flipped = not st.session_state.card_flipped
        with col2:
            if st.button("Shuffle Deck", use_container_width=True):
                random.shuffle(deck)
                st.session_state.current_card_index = 0
                st.session_state.card_flipped = False
                st.experimental_rerun()
        
        # Difficulty buttons (only shown when card is flipped)
        if st.session_state.card_flipped:
            st.subheader("How well did you know this?")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                if st.button("Again", key="again-btn", use_container_width=True):
                    card = update_card(card, "again")
                    st.session_state.study_history.append({
                        "deck": st.session_state.current_deck,
                        "card": card["front"],
                        "rating": "again",
                        "timestamp": datetime.datetime.now()
                    })
                    next_card()
            with col2:
                if st.button("Hard", key="hard-btn", use_container_width=True):
                    card = update_card(card, "hard")
                    st.session_state.study_history.append({
                        "deck": st.session_state.current_deck,
                        "card": card["front"],
                        "rating": "hard",
                        "timestamp": datetime.datetime.now()
                    })
                    next_card()
            with col3:
                if st.button("Good", key="good-btn", use_container_width=True):
                    card = update_card(card, "good")
                    st.session_state.study_history.append({
                        "deck": st.session_state.current_deck,
                        "card": card["front"],
                        "rating": "good",
                        "timestamp": datetime.datetime.now()
                    })
                    next_card()
            with col4:
                if st.button("Easy", key="easy-btn", use_container_width=True):
                    card = update_card(card, "easy")
                    st.session_state.study_history.append({
                        "deck": st.session_state.current_deck,
                        "card": card["front"],
                        "rating": "easy",
                        "timestamp": datetime.datetime.now()
                    })
                    next_card()
        
        # Progress
        progress = (st.session_state.current_card_index + 1) / len(deck)
        st.progress(progress)
        st.caption(f"Card {st.session_state.current_card_index + 1} of {len(deck)}")
    
    elif app_mode == "🆕 Create Cards":
        st.title("Create New Cards")
        
        # Deck selection
        current_deck = st.selectbox(
            "Select deck to add cards to:",
            options=list(st.session_state.decks.keys()),
            index=list(st.session_state.decks.keys()).index(st.session_state.current_deck)
        )
        
        # Card creation form
        with st.form("card_form"):
            col1, col2 = st.columns(2)
            with col1:
                front = st.text_area("Front (Question)", height=150, key="new_card_front")
            with col2:
                back = st.text_area("Back (Answer)", height=150, key="new_card_back")
            
            if st.form_submit_button("Add Card", use_container_width=True):
                if front and back:
                    new_card = {
                        "front": front,
                        "back": back,
                        "interval": 1,
                        "ease": 2.5,
                        "reps": 0,
                        "last_review": None
                    }
                    st.session_state.decks[current_deck].append(new_card)
                    st.success("Card added successfully!")
                    st.session_state.new_card_front = ""
                    st.session_state.new_card_back = ""
                else:
                    st.error("Please fill in both front and back of the card")
        
        # Current deck cards
        st.subheader(f"Cards in {current_deck}")
        if st.session_state.decks[current_deck]:
            for i, card in enumerate(st.session_state.decks[current_deck]):
                with st.expander(f"Card {i+1}: {card['front']}"):
                    st.markdown(f"**Answer:** {card['back']}")
                    st.markdown(f"**Repetitions:** {card['reps']} | **Ease Factor:** {card['ease']:.2f}")
        else:
            st.info("No cards in this deck yet. Add some cards above.")
    
    elif app_mode == "📊 Statistics":
        st.title("Learning Statistics")
        
        # Overall stats
        col1, col2, col3 = st.columns(3)
        total_decks = len(st.session_state.decks)
        total_cards = sum(len(deck) for deck in st.session_state.decks.values())
        total_reviews = len(st.session_state.study_history)
        
        with col1:
            st.metric("Total Decks", total_decks)
        with col2:
            st.metric("Total Cards", total_cards)
        with col3:
            st.metric("Total Reviews", total_reviews)
        
        # Deck-specific stats
        st.subheader("Deck Performance")
        deck_data = []
        for deck in st.session_state.decks:
            total, mastered, due = deck_stats(deck)
            deck_data.append({
                "Deck": deck,
                "Total Cards": total,
                "Mastered Cards": mastered,
                "Due Cards": due,
                "Mastery %": (mastered / total * 100) if total > 0 else 0
            })
        
        if deck_data:
            df = pd.DataFrame(deck_data)
            st.dataframe(df, hide_index=True)
            
            # Plot mastery
            fig = px.bar(df, x='Deck', y='Mastery %', title='Deck Mastery Percentage')
            st.plotly_chart(fig, use_container_width=True)
        
        # Review history
        st.subheader("Review History")
        if st.session_state.study_history:
            history_df = pd.DataFrame(st.session_state.study_history)
            history_df['timestamp'] = pd.to_datetime(history_df['timestamp'])
            history_df['date'] = history_df['timestamp'].dt.date
            
            # Daily reviews
            daily_reviews = history_df.groupby('date').size().reset_index(name='Reviews')
            fig = px.line(daily_reviews, x='date', y='Reviews', title='Daily Reviews')
            st.plotly_chart(fig, use_container_width=True)
            
            # Rating distribution
            rating_counts = history_df['rating'].value_counts().reset_index()
            rating_counts.columns = ['Rating', 'Count']
            fig = px.pie(rating_counts, names='Rating', values='Count', title='Rating Distribution')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No review history yet. Start studying to collect data.")

# Move to next card
def next_card():
    deck = st.session_state.decks[st.session_state.current_deck]
    st.session_state.current_card_index = (st.session_state.current_card_index + 1) % len(deck)
    st.session_state.card_flipped = False
    st.experimental_rerun()

if __name__ == "__main__":
    main()
