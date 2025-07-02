# integration/llm_router.py

import os
from config.settings import GPT_API_KEY, GEMINI_API_KEY, CLAUDE_API_KEY, GROK_API_KEY

import openai
import google.generativeai as genai
from anthropic import Anthropic

# Configure OpenAI
openai.api_key = GPT_API_KEY

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)

# Configure Claude
anthropic_client = Anthropic(api_key=CLAUDE_API_KEY)


def run_gpt(query):
    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",  # Change to "gpt-4" if needed
            messages=[{"role": "user", "content": query}]
        )
        return {"model": "GPT", "response": response.choices[0].message.content}
    except Exception as e:
        return {"model": "GPT", "error": f"API call failed: {e}"}


def run_gemini(query):
    try:
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(query)
        return {"model": "Gemini", "response": response.text}
    except Exception as e:
        return {"model": "Gemini", "error": f"API call failed: {e}"}


def run_claude(query):
    try:
        message = anthropic_client.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=1024,
            messages=[
                {"role": "user", "content": query}
            ]
        )
        return {"model": "Claude", "response": message.content[0].text}
    except Exception as e:
        return {"model": "Claude", "error": f"API call failed: {e}"}


def run_grok(query):
    # NOTE: As of now, Grok/XAI doesn't publicly offer a Python SDK or API access.
    # You must skip this or use mock responses until official support is released.
    return {"model": "Grok", "response": f"Mock Grok response for: {query}"}


def run_with_model(model_name, query):
    model_name = model_name.lower()
    if model_name == "gpt":
        return run_gpt(query)
    elif model_name == "gemini":
        return run_gemini(query)
    elif model_name == "claude":
        return run_claude(query)
    elif model_name == "grok":
        return run_grok(query)
    else:
        return {"error": f"Unsupported LLM model: {model_name}"}
