"""
CSS styles for SatyaDrishti application.
Provides dynamic styling based on mode (Standard/Emergency).
"""

def get_css(mode):
    """Get CSS styles based on application mode."""
    common_css = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600&display=swap');
    html, body, [class*="css"] { font-family: 'Outfit', sans-serif; }
    .stButton > button { border-radius: 8px; font-weight: 600; border: none; transition: 0.2s; }
    
    /* Result Card Styles */
    .result-card {
        padding: 24px;
        border-radius: 16px;
        margin-bottom: 20px;
        transition: transform 0.3s ease;
        cursor: pointer;
    }
    .result-card:hover { transform: translateY(-3px); }
    
    /* Article View Styles */
    .article-container {
        padding: 40px;
        background: rgba(255,255,255,0.05);
        border-radius: 20px;
        margin-top: 20px;
    }
</style>
"""
    
    if mode == "Emergency":
        return common_css + """
<style>
    @keyframes pulse-red {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    .stApp {
        background: linear-gradient(-45deg, #450a0a, #7f1d1d, #991b1b, #450a0a);
        background-size: 400% 400%;
        animation: pulse-red 2s ease infinite;
        color: #ffffff;
    }
    .stTextInput > div > div > input {
        background-color: rgba(0, 0, 0, 0.4);
        color: #ffcccc;
        border: 2px solid #ef4444;
    }
    .result-card {
        background: rgba(0, 0, 0, 0.6);
        border-left: 5px solid #ef4444;
        box-shadow: 0 4px 6px rgba(0,0,0,0.4);
    }
    .stButton > button { background-color: #7f1d1d; color: white; border: 1px solid #ef4444; }
    .stButton > button:hover { background-color: #991b1b; }
</style>
"""
    else:
        return common_css + """
<style>
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
        color: #e2e8f0;
    }
    .stTextInput > div > div > input {
        background-color: rgba(255, 255, 255, 0.1);
        color: white;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    .result-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    .result-card:hover { background: rgba(255, 255, 255, 0.08); }
    .stButton > button { background-color: rgba(62, 126, 235, 0.8); color: white; }
    .stButton > button:hover { background-color: rgba(62, 126, 235, 1.0); }
</style>
"""
