import urllib.request
import json
import os
import re
import time
from datetime import datetime

ANTHROPIC_API_KEY = os.environ['ANTHROPIC_API_KEY']
CF_ACCOUNT_ID = os.environ['CF_ACCOUNT_ID']
CF_KV_NAMESPACE_ID = os.environ['CF_KV_NAMESPACE_ID']
CF_API_TOKEN = os.environ['CF_API_TOKEN']
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '')

today = datetime.now().strftime('%A, %B %d, %Y')

payload = {
  "model": "claude-sonnet-4-5",
  "max_tokens": 4000,
  "tools": [{"type": "web_search_20250305", "name": "web_search"}],
  "system": f"You are a football journalist covering FIFA World Cup 2026. Today is {today}. Search the web for ALL injured or withdrawn players from official FIFA World Cup 2026 squads. Your ENTIRE response must be ONLY a JSON array. No sentences, no explanation, no markdown. Start your response with [ and end with ].",
  "messages": [{
    "role": "user",
    "content": f"Today is {today}. Search for World Cup 2026 injuries. Return ONLY a JSON array (starting with [ and ending with ]), no other text: [{{\"player\":string,\"team\":string,\"flag\":string,\"pos\":string,\"club\":string,\"status\":\"out\"|\"doubt\",\"injury\":string,\"replacement\":string|null,\"timeline\":string|null,\"link\":string,\"link_label\":string,\"confirmed_date\":string}}]"
  }]
}

req = urllib.request.Request(
  'https://api.anthropic.com/v1/messages',
  data=json.dumps(payload).encode(),
  headers={
    'Content-Type': 'application/json',
    'x-api-key': ANTHROPIC_API_KEY,
    'anthropic-version': '2023-06-01'
  }
)

with urllib.request.urlopen(req, timeout=300) as resp:
  data = json.loads(resp.read())

texts = []
for block in data.get('content', []):
  if block.get('type') == 'text':
    texts.append(block.get('text', ''))

full_text = '\n'.join(texts)
print("Claude response (first 300 chars):", full_text[:300])

# Clean markdown and find JSON - try multiple strategies
clean_text = re.sub(r'```json\s*', '', full_text)
clean_text = re.sub(r'```\s*', '', clean_text)

players = []

# Strategy 1: find first [ to last ]
start = clean_text.find('[')
end = clean_text.rfind(']')
if start != -1 and end != -1 and end > start:
  try:
    players = json.loads(clean_text[start:end+1])
    players = [p for p in players if p.get('status') in ('out', 'doubt')]
    print(f"Strategy 1 found {len(players)} players")
  except Exception as e:
    print(f"Strategy 1 failed: {e}")

if not players:
  print("ERROR: Could not parse any players from response")

# --- Get previous data from KV ---
kv_url = f'https://api.cloudflare.com/client/v4/accounts/{CF_ACCOUNT_ID}/storage/kv/namespaces/{CF_KV_NAMESPACE_ID}/values/injury_data'
kv_headers = {'Authorization': f'Bearer {CF_API_TOKEN}'}

prev_data = []
update_count = 0
try:
  req2 = urllib.request.Request(kv_url, headers=kv_headers)
  with urllib.request.urlopen(req2, timeout=10) as resp:
    cached = json.loads(resp.read())
    prev_data = cached.get('data', [])
    update_count = cached.get('updateCount', 0)
except Exception as e:
  print(f"No previous KV data: {e}")

update_count += 1

# --- Detect changes ---
alerts = []
prev_map = {p['player']: p for p in prev_data}

for p in players:
  old = prev_map.get(p['player'])
  if not old:
    emoji = '🚨' if p['status'] == 'out' else '⚠️'
    status_text = 'CONFIRMED OUT' if p['status'] == 'out' else 'INJURY DOUBT'
    alerts.append(
      f"{emoji} <b>NEW INJURY — {status_text}</b>\n\n"
      f"👤 <b>{p['player']}</b> {p.get('flag','')}\n"
      f"🏳️ {p.get('team','')} · {p.get('pos','')}\n"
      f"🩹 {p.get('injury','')}\n"
      f"⏱ {p.get('timeline','Timeline unknown')}\n"
      + (f"↪️ Replaced by: {p['replacement']}\n" if p.get('replacement') else '')
      + "\n🌐 wc2026-injuries.prohaskajoaquin.workers.dev"
    )
  elif old.get('status') != p.get('status'):
    emoji = '🚨' if p['status'] == 'out' else '✅'
    alerts.append(
      f"{emoji} <b>STATUS CHANGE</b>\n\n"
      f"👤 <b>{p['player']}</b> {p.get('flag','')}\n"
      f"📊 {old.get('status','').upper()} → {p.get('status','').upper()}\n"
      f"🩹 {p.get('injury','')}\n"
      + "\n🌐 wc2026-injuries.prohaskajoaquin.workers.dev"
    )

def send_telegram(text):
  if not TELEGRAM_BOT_TOKEN:
    return
  tg_payload = json.dumps({
    'chat_id': '@wc2026injuryalerts',
    'text': text,
    'parse_mode': 'HTML',
    'disable_web_page_preview': True
  }).encode()
  tg_req = urllib.request.Request(
    f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage',
    data=tg_payload,
    headers={'Content-Type': 'application/json'}
  )
  try:
    with urllib.request.urlopen(tg_req, timeout=10) as r:
      print(f"Telegram sent: {r.status}")
  except Exception as e:
    print(f"Telegram error: {e}")

for alert in alerts:
  send_telegram(alert)

# --- Save to KV ---
kv_value = json.dumps({
  'data': players,
  'lastUpdated': int(time.time() * 1000),
  'updateCount': update_count
}).encode()

put_req = urllib.request.Request(
  kv_url,
  data=kv_value,
  headers={**kv_headers, 'Content-Type': 'application/json'},
  method='PUT'
)
with urllib.request.urlopen(put_req, timeout=10) as resp:
  result = json.loads(resp.read())
  print(f"KV write: {result}")

out_count = len([p for p in players if p.get('status') == 'out'])
doubt_count = len([p for p in players if p.get('status') == 'doubt'])
print(f"✅ Update #{update_count} — {len(players)} players ({out_count} out, {doubt_count} doubt). {len(alerts)} alerts.")

summary = (
  f"🤖 <b>WC2026 Injury Tracker — Update #{update_count}</b>\n\n"
  f"🚨 Confirmed out: <b>{out_count}</b>\n"
  f"⚠️ Doubt: <b>{doubt_count}</b>\n"
  f"📊 Total tracked: <b>{len(players)}</b>\n\n"
  f"🌐 wc2026-injuries.prohaskajoaquin.workers.dev"
)
send_telegram(summary)
