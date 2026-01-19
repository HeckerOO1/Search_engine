import streamlit as st
import time
from src.data_loader import DataLoader
from src.emergency_detector import EmergencyDetector
from src.search_engine import SearchEngine
from src.feedback_loop import FeedbackLoop
from src.styles import get_css
from src.audio_utils import generate_high_pitch_siren
from src.views import render_article_view, render_search_header, render_result_card, render_empty_state


st.set_page_config(
    page_title="SatyaDrishti",
    page_icon="👁️",
    layout="wide",
    initial_sidebar_state="collapsed"
)


if 'data_loader' not in st.session_state:
    st.session_state.data_loader = DataLoader('data.json')
    st.session_state.df = st.session_state.data_loader.load_data()
    st.session_state.search_engine = SearchEngine(st.session_state.df)
    st.session_state.detector = EmergencyDetector()
    st.session_state.feedback = FeedbackLoop()
    st.session_state.siren_played = False
    st.session_state.viewing_article_id = None
    st.session_state.view_start_time = None



query = st.session_state.get('query_input', '')
is_emergency, confidence = st.session_state.detector.is_emergency(query)
current_mode = "Emergency" if is_emergency else "Standard"


st.markdown(get_css(current_mode), unsafe_allow_html=True)


if current_mode == "Emergency" and not st.session_state.get('siren_played', False):
    siren = generate_high_pitch_siren()
    st.audio(siren, format='audio/wav', autoplay=True)
    st.session_state.siren_played = True
elif current_mode == "Standard":
    st.session_state.siren_played = False



def go_back():
    
    if st.session_state.view_start_time:
        duration = time.time() - st.session_state.view_start_time
        article_id = st.session_state.viewing_article_id
        
        if duration < 5.0:  
            st.session_state.feedback.record(article_id, 'pogo_stick')
            st.toast(f"📉 Pogo-sticking detected ({duration:.1f}s). Result demoted.", icon="📉")
        else:
            st.session_state.feedback.record(article_id, 'click_good')
            st.toast(f"📈 Dwell time good ({duration:.1f}s). Result boosted.", icon="📈")
            
    st.session_state.viewing_article_id = None
    st.session_state.view_start_time = None


def on_result_click(article_id):
    
    st.session_state.viewing_article_id = article_id
    st.session_state.view_start_time = time.time()


def update_query():
    st.session_state.query_input = st.session_state.widget_query




if st.session_state.viewing_article_id is not None:
    article = st.session_state.df[st.session_state.df['id'] == st.session_state.viewing_article_id].iloc[0]
    render_article_view(article, go_back)
else:
    render_search_header(current_mode, query, confidence)
    
    st.text_input("Enter search query", key="widget_query", on_change=update_query, 
                  placeholder="SEARCH..", label_visibility="collapsed")
    
    if st.session_state.get('query_input'):
        results = st.session_state.search_engine.search(st.session_state.query_input, mode=current_mode)
        st.write(f"Found {len(results)} results")
        
        for idx, row in results.iterrows():
            render_result_card(row, on_result_click)
    else:
        render_empty_state()
