import streamlit as st
import time, pandas as pd, sys
sys.path.insert(0, 'src')
from telemetry import get_live_telemetry, simulate_attack
from detector  import AnomalyDetector
from explainer import IncidentExplainer

st.set_page_config(page_title='AIOps Assistant', page_icon='🔒', layout='wide')
st.title('AIOps Incident Assistant')
st.caption('Dragonfly SDN  |  ML Detection  |  RAG Explainer')

# ── Load models once ─────────────────────────────────────────
@st.cache_resource
def load_models():
    return AnomalyDetector(), IncidentExplainer()

detector, explainer = load_models()

# ── Persist everything across reruns ─────────────────────────
if 'alert_history'   not in st.session_state:
    st.session_state.alert_history   = []
if 'last_report'     not in st.session_state:
    st.session_state.last_report     = None
if 'last_result'     not in st.session_state:
    st.session_state.last_result     = None
if 'last_alert_time' not in st.session_state:
    st.session_state.last_alert_time = {}

# ── Sidebar ───────────────────────────────────────────────────
with st.sidebar:
    st.header('Test Controls')
    attack_type = st.selectbox('Attack type:',
                               ['none', 'ddos', 'dos', 'portscan', 'camoverflow'])
    inject = st.button('Inject Attack')
    st.divider()
    if st.button('Clear History'):
        st.session_state.alert_history = []
        st.session_state.last_report   = None
        st.session_state.last_result   = None

# ── Get telemetry this tick ───────────────────────────────────
if inject and attack_type != 'none':
    telemetry = simulate_attack(attack_type)
else:
    telemetry = get_live_telemetry()

result = detector.predict(telemetry)

# ── Alert cooldown — same switch cannot alert twice in 30s ────
COOLDOWN    = 30
switch      = result['switch_id']
now         = time.time()
last        = st.session_state.last_alert_time.get(switch, 0)
in_cooldown = (now - last) < COOLDOWN

# ── Fire alert and generate report ───────────────────────────
if result['is_alert'] and not in_cooldown:
    with st.spinner('Generating AI incident report...'):
        report = explainer.explain(result, telemetry)

    # Save to session_state — survives rerun
    st.session_state.last_report   = report
    st.session_state.last_result   = result
    st.session_state.last_alert_time[switch] = now

    st.session_state.alert_history.append({
        'time':       time.strftime('%H:%M:%S'),
        'switch':     result['switch_id'],
        'label':      result['label'],
        'confidence': f"{result['confidence']*100:.1f}%",
        'status':     'ALERTED',
    })

# ── Layout ────────────────────────────────────────────────────
col1, col2, col3 = st.columns([1, 1, 2])

with col1:
    st.subheader('Live Telemetry')
    display = {k: v for k, v in telemetry.items()
               if k not in ['timestamp', 'switch_id']}
    st.dataframe(pd.DataFrame([display]).T, use_container_width=True)

with col2:
    st.subheader('Detection')
    color = 'red' if result['is_alert'] else 'green'
    st.markdown(f"""
**Switch:** `{result['switch_id']}`

**Label:** :{color}[{result['label']}]

**Confidence:** {result['confidence']*100:.1f}%

**Status:** {'🚨 ALERT' if result['is_alert'] else '✅ Normal'}
    """)

    # Show cooldown status so user knows why alert did not fire
    if result['is_alert'] and in_cooldown:
        remaining = int(COOLDOWN - (now - last))
        st.warning(f'Cooldown active — {remaining}s remaining')

with col3:
    st.subheader('AI Incident Report')
    # Reads from session_state — persists across every rerun
    if st.session_state.last_report:
        r = st.session_state.last_result
        st.error(
            f"Last alert: **{r['label']}** on `{r['switch_id']}` "
            f"— {r['confidence']*100:.1f}% confidence"
        )
        st.markdown(st.session_state.last_report)
    else:
        st.info('No active alerts — system normal.')

# ── Alert history — persists because it lives in session_state ─
st.divider()
st.subheader(f"Alert History ({len(st.session_state.alert_history)} total)")

if st.session_state.alert_history:
    # Show newest first
    history_df = pd.DataFrame(st.session_state.alert_history[::-1])
    st.dataframe(history_df, use_container_width=True)
else:
    st.info('No alerts fired yet. Inject an attack from the sidebar to test.')

# ── Auto refresh every 2 seconds ─────────────────────────────
time.sleep(2)
st.rerun()
