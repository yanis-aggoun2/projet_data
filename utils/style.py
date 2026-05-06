import streamlit as st
import os

_BG    = "#0c1928"
_PAPER = "#060e1c"
_GRID  = "#162035"
_TICK  = "#3f5470"

#  CSS et thème graphique

# charge style.css
def load_css():
    """Charge le fichier CSS global depuis assets/style.css"""
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    css_path = os.path.join(root, "assets", "style.css")
    with open(css_path, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# thème sombre pour les graphiques Plotly
def dark_layout(title="", height=400):
    """Retourne un dict de layout Plotly avec le thème sombre."""
    return dict(
        title=dict(text=title, font=dict(color="#c5d4e8", size=14), x=0.01),
        plot_bgcolor=_BG, paper_bgcolor=_PAPER,
        font=dict(color=_TICK, family="Inter, sans-serif", size=12),
        xaxis=dict(gridcolor=_GRID, linecolor=_GRID, tickfont=dict(color=_TICK), zeroline=False),
        yaxis=dict(gridcolor=_GRID, linecolor=_GRID, tickfont=dict(color=_TICK), zeroline=False),
        legend=dict(bgcolor="rgba(12,25,40,0.95)", bordercolor=_GRID, borderwidth=1,
                    font=dict(color="#7a90a8", size=12)),
        hovermode="x unified",
        hoverlabel=dict(bgcolor="#0e2038", bordercolor=_GRID, font=dict(color="#f1f5f9")),
        height=height, margin=dict(l=0, r=0, t=44, b=0),
    )
