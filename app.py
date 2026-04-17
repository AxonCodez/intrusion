import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import joblib
import numpy as np

@st.cache_resource
def load_models():
    rf_model = joblib.load('rf_model.joblib')
    xgb_model = joblib.load('xgb_model.joblib')
    scaler = joblib.load('scaler.joblib')
    features = joblib.load('features.joblib')
    # Load dynamically built class list from train.py
    try:
        class_names = joblib.load('classes.joblib')
    except (FileNotFoundError, Exception):
        class_names = ["Safe", "DDoS", "DoS", "Infiltration", "Brute-Force", "Web-Attack"]
    return rf_model, xgb_model, scaler, features, class_names

rf_model, xgb_model, scaler, features, class_names = load_models()

st.set_page_config(page_title="IDS Engine", layout="wide", page_icon="🛡️")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600&family=Space+Grotesk:wght@500;700&display=swap');
    
    html, body, [class*="css"]  {
        font-family: 'Outfit', sans-serif;
        background-color: #0b0c10;
        color: #c5c6c7;
    }
    h1, h2, h3 {
        font-family: 'Space Grotesk', sans-serif;
        font-weight: 700;
        color: #66fcf1;
        letter-spacing: -0.02em;
    }
    .main-header {
        font-size: 3.5rem;
        border-bottom: 1px solid #1f2833;
        padding-bottom: 20px;
        margin-bottom: 40px;
        color: #66fcf1;
        font-family: 'Space Grotesk', sans-serif;
    }
    .metric-card {
        background: #1f2833;
        border-left: 4px solid #45a29e;
        padding: 20px;
        margin: 10px 0;
        border-radius: 4px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }
    .stButton>button {
        background-color: transparent;
        border: 1px solid #66fcf1;
        color: #66fcf1;
        transition: all 0.3s ease;
        border-radius: 2px;
        padding: 0.5rem 2rem;
        font-family: 'Inter', sans-serif;
    }
    .stButton>button:hover {
        background-color: #66fcf1;
        color: #0b0c10;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("<div class='main-header'>Real-time Intrusion Detection System</div>", unsafe_allow_html=True)
st.markdown("Upload network flow telemetry (CSV) for threat analysis via Random Forest inference.")

uploaded_file = st.file_uploader("Select Network Flow Data", type=['csv'])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    df.columns = df.columns.str.strip()
    import numpy as np
    df.replace([np.inf, -np.inf], np.nan, inplace=True)
    df.fillna(0, inplace=True)
    with st.expander("🔍 View Raw Telemetry Preview", expanded=False):
        st.dataframe(df.head(), use_container_width=True)
    
    
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns([1, 2])
    with col1:
        engine_choice = st.selectbox("Select ML Inference Engine", ["Random Forest", "XGBoost"])
        model_to_use = rf_model if engine_choice == "Random Forest" else xgb_model
        
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        init_btn = st.button("🛡️ Initialize Threat Analysis")
        
    if init_btn:
        with st.status("Analyzing traffic signatures...", expanded=True) as status:
            try:
                st.write("Processing telemetry locally...")
                
                missing_cols = [col for col in features if col not in df.columns]
                if missing_cols:
                    st.error(f"Missing columns required by the model: {missing_cols}")
                else:
                    X = df[features].copy()
                    X.replace([np.inf, -np.inf], np.nan, inplace=True)
                    X.fillna(0, inplace=True)
                    
                    st.write(f"Running {engine_choice} Multi-Class Inference...")
                    X_scaled = scaler.transform(X)
                    
                    # Convert to float to avoid XGBoost feature_names mismatch or internal dtype issues
                    # Or just run predict since it's an array now due to scaler
                    predictions = model_to_use.predict(X_scaled)
                    probabilities = model_to_use.predict_proba(X_scaled)
                    
                    results = []
                    for pred, prob in zip(predictions, probabilities):
                        classification = CLASS_NAMES.get(int(pred), "Unknown Threat")
                        confidence = float(max(prob) * 100)
                        results.append({"classification": classification, "confidence": confidence})
                        
                    status.update(label="Analysis Complete!", state="complete", expanded=False)
                    df['Classification'] = [r['classification'] for r in results]
                    df['Confidence (%)'] = [r['confidence'] for r in results]
                    st.session_state['report_df'] = df

            except Exception as e:
                st.error(f"Inference error: {str(e)}")

    if 'report_df' in st.session_state and len(st.session_state['report_df']) == len(df):
        report_df = st.session_state['report_df']
        st.markdown("---")
        st.markdown("### 📋 Threat Intelligence Report")
        
        malicious_count = len(report_df[report_df['Classification'] != 'Safe'])
        benign_count = len(report_df) - malicious_count
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"<div class='metric-card'><h4>📡 Flows Scanned</h4><h2>{len(report_df)}</h2></div>", unsafe_allow_html=True)
        with col2:
            st.markdown(f"<div class='metric-card' style='border-left-color: #4CAF50;'><h4>✅ Safe</h4><h2 style='color: #4CAF50;'>{benign_count}</h2></div>", unsafe_allow_html=True)
        with col3:
            st.markdown(f"<div class='metric-card' style='border-left-color: #f44336;'><h4>🚨 Threats Detected</h4><h2 style='color: #f44336;'>{malicious_count}</h2></div>", unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["📊 Threat Distribution", "🚨 High Confidence Alerts"])
        
        with tab1:
            fig = px.pie(report_df, names='Classification', color='Classification', 
                         color_discrete_map={
                             'Safe': '#4CAF50', 
                             'DDoS': '#f44336', 
                             'DoS': '#ff9800', 
                             'Infiltration': '#9c27b0', 
                             'Brute-Force': '#e91e63', 
                             'Web-Attack': '#3f51b5',
                             'Unknown Threat': '#607d8b'
                         },
                         hole=0.7)
            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', 
                              font_color='#c5c6c7', showlegend=False,
                              margin=dict(t=20, b=20, l=10, r=10))
            st.plotly_chart(fig, use_container_width=True)
        
        with tab2:
            threats = report_df[report_df['Classification'] != 'Safe'].sort_values(by='Confidence (%)', ascending=False)
            st.markdown("<br>", unsafe_allow_html=True)
            if not threats.empty:
                st.dataframe(threats[['Classification', 'Confidence (%)']].head(20), use_container_width=True)
            else:
                st.success("Analysis returned clear. No threats detected.")
                
        st.markdown("<br>", unsafe_allow_html=True)
        st.download_button(
            label="📥 Export Full Analysis Report (CSV)",
            data=report_df.to_csv(index=False).encode('utf-8'),
            file_name='threat_analysis_report.csv',
            mime='text/csv',
        )
