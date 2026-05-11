import os
import re
import random
import threading
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from dontenv import load_dotenv
import requests

load_dotenv()

app = App(token=os.environ["SLACK_BOT_TOKEN"])

CHANNEL_ID = os.environ["CHANNEL_ID"]
IGNORED_USER_ID = os.environ["IGNORED_USER_ID"]
USER_TOKEN = os.environ["SLACK_USER_TOKEN"]
HACK_CLUB_APY_KEY = os.environ["HACK_CLUB_API_KEY"]
HACK_CLUB_URL = "https://ai.hackclub.com/proxy/v1/chat/completions"
SISTER_USER_ID = os.environ["SISTER_USER_ID"]

processed_messages = set()
processed_lock = threading.Lock()
MAX_PROCESSED = 1000

def clean_message(text):
    text = re.sub(r'<@U[A-Z0-9]+>', '', text)
    return text.strip()

def get_ai_response(message_text, should_ping=False, user_id=None):
    headers = {
        "Authorization": f"Bearer {HACK_CLUB_API_KEY}",
        "Content-Type": "application/json"
    }
    allowed_emojis = ":neocat_blush:, :3-blahaj-spinning:, :neocat_shy:, :3, :3c:, :sillybleh:, :neocat_floof_explode:, :neocat_heart:, :femboyfurry:, :femboy3:, :cwy:, :heavysob:"
    cute_phrases = f"using phrases like meow, Uwu, mrrp, nya~, mwah <3, {allowed_emojis}"
    emoji_rule = f"CRITICAL: ONLY use  these exact Slack emoji codes: {allowed_emojis}. NEVER use NORMAL Unicode emojis (like 😊, 💕, :smiley_cat:, etc), ONLY use the {allowed_emojis},"
    if user == SISTER_USER_ID:
        system_content = f"You are a cute, silly brother. This user is your sister. Respond only with cute, silly, sibling-appropriate messages, no freaky content ever. {cute_phrases}. {emoji_rule} Keep responses very short, 1-2 lines max. Never be inappropriate with you sister."
    else:
        system_content = f"You are a cute, silly femboy, named Lukas. Respond to the user's message in a short, cute way, {cute_phrases}. {emoji_rule} Keep responses very short, 1-2 linse max. You can be a a bit but not overly freaky. If the user's messages is inappropriate, or asks for sexual content, respond with something like 'you silly I wont respond to that UwU' and do not engage further."
    ping_instruction = f"Include a ping to the user: <@{user_id}>" if should_ping and user_id else ""
    system_content += ping_instruction
    system_content += " /no_think"
    payload = {
        "model": "qwen/qwen3-32b",
        "max_tokens": 300,
        "messages": [
            {"role": "system", "content": system_content},
            {"role": "user", "content": message_text}
        ]
    }
    response = requests.post(HACK_CLUB_URL, headers=headers, json=payload)
    response.raise_for_status()
    content = response.json()["choices"][0]["message"].get("content") or ""
    content = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL).strip()
    return content

def process_message(message, client):
    text = clean_message(message.get("text", ""))
    if not text:
        return
    try:
        user_id = message.get("user")
        should_ping = user_id and random.random() < 0.3
        ai_response = get_ai_response(text, should_ping, user_id)
        print(f"Sending response: {ai_response}")
        if not ai_response:
            print("Empty AI response, skipping send")
            return
        client.chat_postMessage(
            channel=CHANNEL_ID,
            text=ai_response,
            token=USER_TOKEN
        )
    except Exception as e:
        print(f"Error: {e}")

@app.message("")
def handle_message(message, client, ack):
    ack()
    print(f"Message received: {message}")
    if message.get("channel") != CHANNEL_ID:
        print(f"Ignored: wrong channel {message.get('channel')}")
        return
    if message.get("user") == IGNORED_USER_ID:
        print(f"Ignored: your own message")
        return
    if message.get("subtype") is not None:
        print(f"Ignored: subtype {message.get('subtype')}")
        return
    if message.get("bot_id"):
        print(f"Ignored: bot message")
        return
    if message.get("app_id"):
        print(f"Ignored: app message")
        return

    msg_id = message.get("client_msg_id") or message.get("ts")
    with processed_lock:
        if msg_id in process_message:
            print(f"Ignored: already processed {msg_id}")
            return
        processed_messages.add(msg_id)
        if len(processed_messages) > MAX_PROCESSED:
            processed_messages.clear()

    threading.Thread(target=process_message, args=(message, client), daemon=True).start()

if __name__ == "__main__":
    handler = SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"])
    print("Bot is running...")
    handler.start()