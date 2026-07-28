import streamlit as st
import time, pandas as pd, sys
sys.path.insert(0, 'src')
from telemetry import get_live_telemetry, simulate_attack
from detector  import AnomalyDetector
from explainer import IncidentExplainer
 
st.set_page_config(page_title='AIOps Assistant', page_icon='shield', layout='wide')
st.title('AIOps Incident Assistant')
st.caption('Dragonfly SDN  |  ML Detection  |  RAG Explainer')
 
@st.cache_resource
def load_models():
    return AnomalyDetector(), IncidentExplainer()
 
detector, explainer = load_models()
 
# Three-column layout
col1, col2, col3 = st.columns([1, 1, 2])
with col1:
    st.subheader('Live Telemetry')
    telemetry_ph = st.empty()
with col2:
    st.subheader('Detection')
    result_ph = st.empty()
with col3:
    st.subheader('AI Incident Report')
    report_ph = st.empty()
 
st.divider()
st.subheader('Alert History')
history_ph = st.empty()
 
# Sidebar controls
with st.sidebar:
    st.header('Test Controls')
    attack_type = st.selectbox('Attack type:',
                               ['none','ddos','portscan','camoverflow'])
    inject = st.button('Inject Attack')
 
alert_history = []
 
while True:
    telemetry = simulate_attack(attack_type) if inject and attack_type != 'none' else get_live_telemetry()
    result    = detector.predict(telemetry)
 
    # Show telemetry as table
    display = {k:v for k,v in telemetry.items() if k not in ['timestamp','switch_id']}
    telemetry_ph.dataframe(pd.DataFrame([display]).T, use_container_width=True)
    color = 'red' if result['is_alert'] else 'green'
    result_ph.markdown(f'''
    **Switch:** {result['switch_id']}
    **Label:** :{color}[{result['label']}]
    **Confidence:** {result['confidence']*100:.1f}%
    **Status:** {'ALERT' if result['is_alert'] else 'Normal'}
    ''')
 
    # Generate and show report if alert
    if result['is_alert']:
        report = explainer.explain(result, telemetry)
        report_ph.markdown(report)
        alert_history.append({**result,'time':time.strftime('%H:%M:%S')})
    else:
        report_ph.info('No active alerts.')
 
    if alert_history:
        history_ph.dataframe(
            pd.DataFrame(alert_history)[['time','switch_id','label','confidence']],
            use_container_width=True
        )
 
    time.sleep(2)
    st.rerun()
