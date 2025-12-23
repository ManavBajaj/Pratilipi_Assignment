# extractor.py
import json
import requests

# OPTION 1: Groq (FREE, FAST, RELIABLE)
# Get free API key at: https://console.groq.com/
# 14,400 requests/day free tier

def build_prompt(story, tags):
    """Simple, focused prompt for better JSON output"""
    return f"""Extract story signals as JSON only. No explanation.

Story: "{story}"
Tags: {tags}

Return this exact format:
{{
  "primary_theme": "romance|thriller|horror|scifi|instructional|other",
  "relationship_dynamic": "enemies_to_lovers|second_chance|none",
  "thriller_type": "espionage|legal|psychological|none",
  "horror_type": "gothic|psychological|slasher|none",
  "scifi_type": "hard_scifi|cyberpunk|space_opera|none",
  "setting_era": "past|present|future",
  "technology_level": "basic|modern|advanced|futuristic",
  "location_type": "mansion|urban|space|courtroom|domestic|other",
  "conflict_nature": "physical_violence|psychological|legal|romantic|none",
  "tone": "scary|tense|melancholic|romantic|technical|instructional|none"
}}"""

def call_groq_api(api_key, prompt):
    """Call Groq API - FREE and reliable"""
    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "llama-3.3-70b-versatile",  # Fast and accurate
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.1,
                "max_tokens": 500
            },
            timeout=10
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        raise Exception(f"Groq API error: {str(e)}")

def call_together_api(api_key, prompt):
    """Alternative: Together AI - also FREE"""
    try:
        response = requests.post(
            "https://api.together.xyz/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.1,
                "max_tokens": 500
            },
            timeout=10
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        raise Exception(f"Together API error: {str(e)}")

def heuristic_fallback(story, tags):
    """Robust fallback using pattern matching"""
    text = story.lower()
    tag_str = " ".join(tags).lower()
    
    # Detect instructional/non-fiction
    if any(word in text for word in ["how to", "mix", "bake at", "degrees", "instructions", "steps", "recipe"]):
        return {
            "primary_theme": "instructional",
            "relationship_dynamic": "none",
            "thriller_type": "none",
            "horror_type": "none",
            "scifi_type": "none",
            "setting_era": "present",
            "technology_level": "basic",
            "location_type": "other",
            "conflict_nature": "none",
            "tone": "instructional"
        }
    
    # Relationship dynamics
    relationship = "none"
    if "hated each other" in text or "enemies" in text:
        relationship = "enemies_to_lovers"
    elif any(phrase in text for phrase in ["met again", "years after", "could have been", "second chance"]):
        relationship = "second_chance"
    
    # Thriller detection
    thriller = "none"
    if any(word in text for word in ["agent", "spy", "kremlin", "espionage"]) or "spies" in tag_str:
        thriller = "espionage"
    elif any(word in text for word in ["lawyer", "judge", "court", "cross-examination"]):
        thriller = "legal"
    elif "psychological" in text or "mind" in text:
        thriller = "psychological"
    
    # Horror detection  
    horror = "none"
    if any(phrase in text for phrase in ["victorian mansion", "gothic", "dark past", "corridors whispering"]):
        horror = "gothic"
    elif any(word in text for word in ["masked killer", "stalks", "camp"]):
        horror = "slasher"
    elif "psychological" in tag_str or ("scary" in tag_str and "mind" in text):
        horror = "psychological"
    
    # Sci-fi detection
    scifi = "none"
    if any(phrase in text for phrase in ["ftl travel", "physics of", "stasis", "metabolic needs"]):
        scifi = "hard_scifi"
    elif any(word in text for word in ["neon", "cyberpunk", "ai operating system"]):
        scifi = "cyberpunk"
    elif "space opera" in text or ("space" in tag_str and "epic" in text):
        scifi = "space_opera"
    
    # Setting and tech
    setting = "present"
    if "future" in tag_str or any(word in text for word in ["ai", "neon-drenched"]):
        setting = "future"
    elif any(word in text for word in ["war", "victorian"]):
        setting = "past"
    
    tech = "modern"
    if any(word in text for word in ["ftl", "stasis"]):
        tech = "futuristic"
    elif any(word in text for word in ["ai", "robot"]):
        tech = "advanced"
    
    # Primary theme
    theme = "other"
    if horror != "none":
        theme = "horror"
    elif thriller != "none":
        theme = "thriller"
    elif relationship != "none" or "love" in tag_str:
        theme = "romance"
    elif scifi != "none":
        theme = "scifi"
    
    return {
        "primary_theme": theme,
        "relationship_dynamic": relationship,
        "thriller_type": thriller,
        "horror_type": horror,
        "scifi_type": scifi,
        "setting_era": setting,
        "technology_level": tech,
        "location_type": "mansion" if "mansion" in text else "urban" if "tokyo" in text else "courtroom" if "court" in text else "other",
        "conflict_nature": "physical_violence" if "killer" in text else "legal" if "lawyer" in text else "romantic" if "love" in tag_str else "psychological" if "psychological" in text else "none",
        "tone": "scary" if "scary" in tag_str else "melancholic" if "sad" in tag_str else "tense" if thriller != "none" else "romantic" if relationship != "none" else "instructional"
    }

def extract_signals(api_key, story, tags, api_type="groq"):
    """Extract semantic signals using free LLM API"""
    prompt = build_prompt(story, tags)
    
    try:
        # Try LLM first
        if api_type == "groq":
            text = call_groq_api(api_key, prompt)
        elif api_type == "together":
            text = call_together_api(api_key, prompt)
        else:
            raise ValueError(f"Unknown API type: {api_type}")
        
        # Extract JSON from response
        start = text.find("{")
        end = text.rfind("}") + 1
        
        if start == -1 or end == 0:
            raise ValueError("No JSON found")
        
        json_str = text[start:end]
        signals = json.loads(json_str)
        
        # Validate required fields
        required = ["primary_theme", "relationship_dynamic", "thriller_type", 
                   "horror_type", "scifi_type", "tone"]
        if not all(k in signals for k in required):
            raise ValueError("Missing required fields")
        
        print("✓ LLM extraction successful")
        return signals
        
    except Exception as e:
        print(f"⚠️ LLM failed ({str(e)}), using heuristic fallback")
        return heuristic_fallback(story, tags)