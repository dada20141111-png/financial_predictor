import sys
import os
import streamlit as st

# Ensure src is in path so we can import dashboard
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.dashboard.main import run_dashboard

if __name__ == "__main__":
    run_dashboard()
