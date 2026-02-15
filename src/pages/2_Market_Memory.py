import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.market_memory import MarketMemory
from src.data_provider import YahooFinanceProvider

def render_memory_page():
    st.set_page_config(page_title="Market Memory | Financial Predictor", layout="wide")
    st.title("🧠 Market Memory Analysis")
    st.markdown("Visualize how historical events correlated with asset price movements.")

    # Sidebar Controls
    st.sidebar.header("Analysis Settings")
    symbol = st.sidebar.text_input("Asset Symbol", "BTC-USD")
    period = st.sidebar.selectbox("Time Period", ["1 Month", "3 Months", "6 Months", "1 Year", "YTD", "All Time"])
    
    # Calculate Dates
    end_date = datetime.now()
    if period == "1 Month":
        start_date = end_date - timedelta(days=30)
    elif period == "3 Months":
        start_date = end_date - timedelta(days=90)
    elif period == "6 Months":
        start_date = end_date - timedelta(days=180)
    elif period == "1 Year":
        start_date = end_date - timedelta(days=365)
    elif period == "YTD":
        start_date = datetime(end_date.year, 1, 1)
    else:
        start_date = end_date - timedelta(days=365*5) # All Time (Approx 5y)

    start_str = start_date.strftime('%Y-%m-%d')
    end_str = end_date.strftime('%Y-%m-%d')

    # Load Data
    with st.spinner("Fetching Market Data & Memories..."):
        # 1. Price Data
        provider = YahooFinanceProvider()
        try:
            df = provider.fetch_history(symbol, start=start_str, end=end_str)
        except Exception as e:
            st.error(f"Failed to fetch data for {symbol}: {e}")
            return

        # 2. Memory Events
        mm = MarketMemory()
        events = mm.get_events(start_str, end_str)

    # --- Visualization ---
    
    # --- Visualization Tabs ---
    tab1, tab2 = st.tabs(["📉 Event Timeline", "📊 Pattern Recognition"])
    
    with tab1:
        # Create Chart
        fig = go.Figure()

        # Price Line
        fig.add_trace(go.Scatter(
            x=df.index, 
            y=df['Close'],
            mode='lines',
            name=symbol,
            line=dict(color='#1f77b4', width=2)
        ))

        # Add Event Markers
        for event in events:
            evt_date = pd.to_datetime(event['date'])
            
            # Only plot if date exists in range (roughly)
            if evt_date >= df.index[0] and evt_date <= df.index[-1]:
                # Find closest price for y-axis placement
                # We can use 'nearest' search on index
                try:
                    price_at_idx = df.index.get_indexer([evt_date], method='nearest')[0]
                    price = df['Close'].iloc[price_at_idx]
                    
                    # Color code by sentiment
                    color = 'green' if event['sentiment'] > 0.1 else 'red' if event['sentiment'] < -0.1 else 'gray'
                    symbol_marker = 'triangle-up' if event['sentiment'] > 0 else 'triangle-down' if event['sentiment'] < 0 else 'circle'
                    
                    fig.add_trace(go.Scatter(
                        x=[evt_date],
                        y=[price],
                        mode='markers',
                        name='Event',
                        marker=dict(color=color, size=12, symbol=symbol_marker),
                        text=f"<b>{event['description']}</b><br>Impact: {event['impact']}",
                        hoverinfo='text',
                        showlegend=False
                    ))
                    
                except:
                    pass

        fig.update_layout(
            title=f"{symbol} Price vs Market Events",
            xaxis_title="Date",
            yaxis_title="Price",
            hovermode="x unified",
            height=600,
            clickmode='event+select'
        )

        st.info("💡 **Tip:** Click on any triangle marker 🔺🔻 to see event details below!")

        # Interactive Chart
        selection = st.plotly_chart(fig, use_container_width=True, on_select="rerun", selection_mode="points")
        
        # --- Drill-down Detail Card ---
        if selection and selection['selection']['points']:
            try:
                selected_point = selection['selection']['points'][0]
                
                # Check if it's an event (curve_number > 0)
                # Or just match by X-axis (Date)
                x_val = selected_point['x']
                sel_date = pd.to_datetime(x_val).strftime('%Y-%m-%d')
                
                # Match events
                matched_events = [e for e in events if e['date'] == sel_date]
                
                if matched_events:
                    st.divider()
                    st.subheader(f"📅 Daily Insight: {sel_date}")
                    
                    for evt in matched_events:
                        # Styling
                        color = "green" if evt['sentiment'] > 0 else "red" if evt['sentiment'] < 0 else "gray"
                        bg_color = "rgba(0, 128, 0, 0.1)" if evt['sentiment'] > 0 else "rgba(255, 0, 0, 0.1)" if evt['sentiment'] < 0 else "rgba(128, 128, 128, 0.1)"
                        
                        st.markdown(f"""
                        <div style="border-left: 5px solid {color}; background-color: {bg_color}; padding: 15px; border-radius: 5px; margin-bottom: 10px;">
                            <h3 style="margin:0; padding:0; color: {color}">{evt['description']}</h3>
                            <p style="margin-top:5px;">
                                <strong>Category:</strong> {evt.get('category', 'General')} | 
                                <strong>Impact:</strong> {evt['impact']} | 
                                <strong>Sentiment:</strong> {evt['sentiment']:.2f}
                            </p>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                     # Maybe clicked on the line but not on a specific event
                     pass
            except Exception as e:
                st.error(f"Error displaying details: {e}")

        # --- Event Table ---
        st.subheader("📜 Event Log")
        if events:
            event_df = pd.DataFrame(events)
            # Reorder cols
            if 'category' not in event_df.columns:
                event_df['category'] = 'General'
            cols = ['date', 'description', 'category', 'impact', 'sentiment']
            # Filter cols that exist
            cols = [c for c in cols if c in event_df.columns]
            st.dataframe(event_df[cols].style.applymap(
                lambda x: 'color: green' if x > 0 else 'color: red' if x < 0 else 'color: gray', 
                subset=['sentiment']
            ), use_container_width=True)
        else:
            st.info("No recorded market memory events for this period.")

    with tab2:
        from src.pattern_analyzer import EventPatternAnalyzer
        st.subheader("🔍 Event Impact Analysis")
        st.markdown("Analyze how specific types of events historically affect price.")
        
        col_pa1, col_pa2 = st.columns(2)
        target_cat = col_pa1.selectbox("Event Category", ["Fed", "Crypto", "Macro", "Regulation", "Politics", "Earnings"])
        horizon_input = col_pa2.selectbox("Horizon", ["1 Day", "1 Week", "1 Month"])
        
        h_map = {"1 Day": 1, "1 Week": 7, "1 Month": 30}
        
        if st.button("Analyze Patterns"):
            analyzer = EventPatternAnalyzer()
            with st.spinner(f"Analyzing impact of '{target_cat}' events on {symbol}..."):
                res = analyzer.analyze_impact(symbol, target_cat, horizon_days=h_map[horizon_input])
                
                if "error" in res:
                    st.warning(res['error'])
                else:
                    # Metrics
                    m1, m2, m3 = st.columns(3)
                    avg_ret = res['avg_return'] * 100
                    win_rate = res['win_rate'] * 100
                    
                    m1.metric("Events Analyzed", res['events_count'])
                    m2.metric("Avg Return", f"{avg_ret:+.2f}%", delta_color="normal")
                    m3.metric("Win Rate (Positive Returns)", f"{win_rate:.0f}%")
                    
                    # Chart
                    msg = "Bullish Bias" if avg_ret > 0.5 else "Bearish Bias" if avg_ret < -0.5 else "Neutral"
                    st.info(f"Historical Trend: **{msg}**")
                    
                    # Detailed Table
                    if res['details']:
                        st.write("### detailed outcomes")
                        det_df = pd.DataFrame(res['details'])
                        st.dataframe(det_df.style.format({"return": "{:+.2%}"}))

if __name__ == "__main__":
    render_memory_page()
