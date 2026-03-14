from langchain_core.messages import HumanMessage,SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
import json
import re
    
from app.config import settings

llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",  
    google_api_key=settings.GOOGLE_API_KEY
)

def analyze_error(error: dict) -> dict:
    
    prompt = f"""
    Analyze this log error and provide:
    1. Root cause — possible reason why this error occurred
    2. Severity — Critical / High / Medium / Low
    3. Fix suggestion — how to resolve this

    Error Details:
    - Message: {error['message']}
    - Level: {error['level']}
    - Occurred: {error['count']} times
    - First seen: {error['first_seen']}
    - Last seen: {error['last_seen']}
    - Sources: {', '.join(error['sources'])}

    Respond in JSON only:
    {{
        "root_cause": "...",
        "severity": "...",
        "fix": "..."
    }}
    """

    response = llm.invoke([
    SystemMessage(content="You are a senior backend engineer expert in analyzing server logs. Always respond in valid JSON only."),
    HumanMessage(content=prompt)])
  
    # markdown backticks hata do agar hain
    clean = re.sub(r"```json|```", "", response.content).strip()
    parsed = json.loads(clean)
    
    return {**error, **parsed}