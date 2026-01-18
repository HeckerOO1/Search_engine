"""
View components for SatyaDrishti application.
Contains rendering functions for article and search views.
"""

import streamlit as st
import time


def render_article_view(article, go_back_callback):
    """Render the full article view."""
    st.button("← Back to Results", on_click=go_back_callback)
    
    st.markdown(f"""
    <div class="article-container">
        <div style="margin-bottom: 20px;">
            <span style="background: rgba(255,255,255,0.1); padding: 5px 12px; border-radius: 15px; border: 1px solid rgba(255,255,255,0.2); margin-right: 10px;">{article['source']}</span>
            <span style="opacity: 0.7;">{article['timestamp'].strftime('%Y-%m-%d')}</span>
        </div>
        <h1 style="font-size: 2.5em; margin-bottom: 20px;">{article['title']}</h1>
        <hr style="border-color: rgba(255,255,255,0.1);">
        <p style="font-size: 1.2em; line-height: 1.6; margin-top: 30px;">
            {article['content']}
        </p>
        <div style="margin-top: 50px; padding: 20px; background: rgba(0,0,0,0.2); border-left: 3px solid #666;">
            <p style="font-style: italic; opacity: 0.8;">Full article content would be displayed here. The system has ranked this based on freshness: {article.get('timestamp')}.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_search_header(current_mode, query, confidence):
    """Render the search page header."""
    col1, col2 = st.columns([1, 8])
    with col1:
        st.markdown("<div style='font-size: 50px; text-align: center;'>👁️</div>", unsafe_allow_html=True)
    with col2:
        if current_mode == "Emergency":
            st.markdown("<h1 style='color: #ff9999; text-shadow: 0 0 20px red; margin-bottom: 0px;'>EMERGENCY PROTOCOL ACTIVE</h1>", unsafe_allow_html=True)
            st.markdown(f"<p style='color: #ffcccc;'>DETECTED: <b>{query.upper()}</b> | CONFIDENCE: {int(confidence*100)}%</p>", unsafe_allow_html=True)
        else:
            st.title("SatyaDrishti Search")


def render_result_card(row, on_click_callback):
    """Render a single search result card."""
    trust_score = int(row['trust'] * 100)
    
    with st.container():
        # Visual Card
        st.markdown(f"""
        <div class="result-card">
            <div style="display: flex; justify-content: space-between;">
                <span style="font-size: 0.8em; opacity: 0.7; letter-spacing: 1px;">{row['source_type'].upper()}</span>
                <span style="color: {'#4ade80' if trust_score > 85 else '#facc15' if trust_score > 60 else '#f87171'}; font-weight: bold;">Trust: {trust_score}%</span>
            </div>
            <h3 style="margin: 5px 0 10px 0; font-size: 1.3em;">{row['title']}</h3>
            <p style="font-size: 0.95em; opacity: 0.9; margin-bottom: 15px;">{row['content'][:180]}...</p>
            <div style="font-size: 0.8em; opacity: 0.6;">
                <span>{row['source']}</span> • <span>{row['timestamp'].strftime('%Y-%m-%d')}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Full width button
        if st.button(f"Read Full Report ➤", key=f"read_{row['id']}", use_container_width=True):
            on_click_callback(row['id'])
            st.rerun()
        
        st.write("")  # Spacer


def render_empty_state():
    """Render the empty/hero state when no query."""
    st.markdown("""
    <div style="text-align: center; margin-top: 100px; opacity: 0.5;">
        <h3>Waiting for signal...</h3>
        <p>Enter a query to begin scanning the information stream.</p>
    </div>
    """, unsafe_allow_html=True)
