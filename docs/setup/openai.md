# OpenAI API Setup

## 1. Create an Account
1. Go to [platform.openai.com](https://platform.openai.com)
2. Sign up and add a payment method

## 2. Generate API Key
1. API Keys page > Create new secret key
2. Copy the key (starts with `sk-`)

```env
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

## 3. Model Used
Nocturn AI uses `gpt-4o-mini` by default:
- Fast response times (~1-2s)
- Low cost (~$0.15/1M input tokens)
- Great for hotel concierge conversations

## 4. Optional: Anthropic Fallback
Add an Anthropic key for automatic failover:

```env
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

Falls back to Claude Haiku if OpenAI fails.

## Required
This is the only **required** integration. Without it, AI responses won't work.
