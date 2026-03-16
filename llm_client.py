import os
import json
import requests
import google.genai as genai
from openai import OpenAI
from anthropic import Anthropic

def get_api_key(environment_keys: list[str]) -> str | None:
    """
    Checks a prioritized list of environment variables for an API key.
    Returns the first one that exists.
    """
    for key in environment_keys:
        val = os.environ.get(key)
        if val:
            return val
    return None

def analyze_readme(provider: str, model: str, readme_content: str) -> dict:
    """
    Calls the specified LLM provider to analyze the README.
    Returns a dictionary with 'tag' and 'tech_stack'.
    
    Raises ValueError if API Key is missing or generation fails.
    """
    system_prompt = (
        "You are an expert software architect. Analyze the provided README file. "
        "Your task is to identify from an extremely high level what the codebase does. "
        "Assign the codebase a 1 to 3 word 'tag' that will assist in quickly identifying its use. "
        "Examples of tags: 'multilanguage translation', 'web scraping', 'multi-agent scaffolding'. "
        "Also, try to identify the primary 'tech stack' (e.g., 'Python, React', 'Rust', etc.). "
        "Respond ONLY in valid JSON format with exactly two keys: 'tag' and 'tech_stack'. "
        "Do not include markdown blocks or any other text outside the JSON."
    )
    
    user_prompt = f"Here is the README content:\n\n{readme_content}"
    
    provider = provider.lower()
    
    try:
        if provider == "openai":
            key_names = [f"{model.upper().replace('-', '_')}_API_KEY", "OPENAI_API_KEY"]
            api_key = get_api_key(key_names)
            if not api_key:
                raise ValueError(f"Missing API key. Please set one of: {', '.join(key_names)}")
                
            client = OpenAI(api_key=api_key)
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"}
            )
            return json.loads(response.choices[0].message.content)
            
        elif provider == "anthropic":
            key_names = [f"{model.upper().replace('-', '_')}_API_KEY", "ANTHROPIC_API_KEY"]
            api_key = get_api_key(key_names)
            if not api_key:
                raise ValueError(f"Missing API key. Please set one of: {', '.join(key_names)}")
                
            client = Anthropic(api_key=api_key)
            response = client.messages.create(
                model=model,
                max_tokens=256,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}]
            )
            return _parse_json_from_text(response.content[0].text)
            
        elif provider == "google":
            key_names = [f"{model.upper().replace('-', '_')}_API_KEY", "GEMINI_API_KEY", "GOOGLE_API_KEY"]
            api_key = get_api_key(key_names)
            if not api_key:
                raise ValueError(f"Missing API key. Please set one of: {', '.join(key_names)}")
                
            client = genai.Client(api_key=api_key)
            response = client.models.generate_content(
                model=model,
                contents=f"{system_prompt}\n\n{user_prompt}",
            )
            return _parse_json_from_text(response.text)
            
        elif provider == "openrouter":
            key_names = [f"{model.upper().replace('-', '_')}_API_KEY", "OPENROUTER_API_KEY"]
            api_key = get_api_key(key_names)
            if not api_key:
                raise ValueError(f"Missing API key. Please set one of: {', '.join(key_names)}")
                
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            data = {
                "model": model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
            }
            res = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
            res.raise_for_status()
            content = res.json()["choices"][0]["message"]["content"]
            return _parse_json_from_text(content)
            
        elif provider == "ollama":
            host = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
            data = {
                "model": model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "format": "json",
                "stream": False
            }
            res = requests.post(f"{host}/api/chat", json=data)
            res.raise_for_status()
            content = res.json()["message"]["content"]
            return json.loads(content)
            
        elif provider == "lmstudio":
            host = os.environ.get("LMSTUDIO_HOST", "http://localhost:1234/v1")
            client = OpenAI(base_url=host, api_key="lm-studio")
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
            )
            return _parse_json_from_text(response.choices[0].message.content)
            
        else:
            raise ValueError(f"Unknown provider: {provider}")

    except Exception as e:
        raise RuntimeError(f"Failed to analyze README with {provider}: {e}")

def _parse_json_from_text(text: str) -> dict:
    """
    Helper to extract JSON if the LLM wraps it in markdown blocks.
    """
    text = text.strip()
    if text.startswith("```json"):
        text = text.split("```json", 1)[1]
    if text.startswith("```"):
        text = text.split("```", 1)[1]
    
    if text.endswith("```"):
        text = text.rsplit("```", 1)[0]
        
    text = text.strip()
    return json.loads(text)
