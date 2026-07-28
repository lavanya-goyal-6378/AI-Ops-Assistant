
import os
from groq import Groq
from dotenv import load_dotenv
from knowledge_base import load_knowledge_base
 
load_dotenv()
 
SYSTEM_PROMPT = '''
You are a network operations assistant for a Dragonfly SDN environment.
When given an alert and relevant documentation, you:
1. Explain what the anomaly means in plain English
2. Identify the likely root cause from the metrics
3. Give 3 concrete numbered steps to resolve it
4. Note any related risks to watch for
Be specific. Use the exact metric values provided. Be concise.
'''
 
class IncidentExplainer:
    def __init__(self):
        self.client = Groq(api_key=os.getenv('GROQ_API_KEY'))
        self.db     = load_knowledge_base()
        print('Explainer ready')
 
    def _build_query(self, alert, telemetry):
        return (
            f"{alert['label']} attack on switch {alert['switch_id']} "
            f"flood_score {telemetry.get('flood_score',0):.2f} "
            f"pps {telemetry.get('pps',0):.0f} "
            f"mac_fill {telemetry.get('mac_fill',0):.2f}"
        )
 
    def _retrieve_context(self, query, k=3):
        results = self.db.similarity_search(query, k=k)
        return '\n\n---\n\n'.join(doc.page_content for doc in results)
 
    def explain(self, alert, telemetry):
        query   = self._build_query(alert, telemetry)
        context = self._retrieve_context(query)
 
        user_msg = f'''
ALERT DETAILS:
  Type:        {alert['label']}
  Confidence:  {alert['confidence']*100:.1f}%
  Switch:      {alert['switch_id']}
 
TELEMETRY AT TIME OF ALERT:
  PPS:          {telemetry.get('pps','N/A')}
  FloodScore:   {telemetry.get('flood_score','N/A')}
  MAC fill:     {telemetry.get('mac_fill','N/A')}
  New MAC rate: {telemetry.get('new_mac_rate','N/A')}
  Mean pkt size:{telemetry.get('mean_pkt_size','N/A')} bytes
 
RELEVANT DOCUMENTATION:
{context}
 
Generate an incident report with root cause and fix steps.
        '''
 
        response = self.client.chat.completions.create(
            model='llama-3.1-8b-instant',
            messages=[
                {'role':'system','content':SYSTEM_PROMPT},
                {'role':'user',  'content':user_msg}
            ],
            temperature=0.3,
            max_tokens=600
        )
        return response.choices[0].message.content
 
if __name__ == '__main__':
    from telemetry import simulate_attack
    from detector  import AnomalyDetector
    det = AnomalyDetector()
    exp = IncidentExplainer()
    flow  = simulate_attack('ddos')
    alert = det.predict(flow)
    print(exp.explain(alert, flow))

