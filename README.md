# Nya~ bot

A Slack bot that responds to messages in cute/femboy-style responses in a Slack channel, ignoring your own messages.

## Setup

1. Create a Slack app at https://api.slack.com/apps
2. Enable Socket Mode (Settings > Socket Mode)
3. Enable Event Subscriptions (Features > Event Subscriptions)
   - Add bot event: `message.channels`
4. Add OAuth scopes: `channels:history`, `chat:write`, `app_mentions:read`
5. Install app to workspace
6. Invite bot to your channel: `/invite @your-bot-name`

## Install & Run

```bash
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your Slack tokens
python bot.py
```

## Responses

Sends random cute responses including: meow, UwU, mrrp, :neocat_blush:, :3-blahaj-spinning:, etc.
