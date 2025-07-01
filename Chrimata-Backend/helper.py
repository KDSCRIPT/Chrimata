import requests,json
import os
from dotenv import load_dotenv
load_dotenv()

GEMINI_API_URL=f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={os.getenv('GEMINI_API_KEY')}"

def call_gemini_api(prompt_text, schema=None, instruction_type="text generation"):
    """
    Calls the Gemini API with the given prompt and optional schema for JSON output.
    """
    print(f"\n🤖 Calling Gemini API for {instruction_type}...")
    payload = {
        "contents": [{"role": "user", "parts": [{"text": prompt_text}]}]
    }
    if schema:
        payload["generationConfig"] = {
            "responseMimeType": "application/json",
            "responseSchema": schema
        }
    
    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(GEMINI_API_URL, json=payload, headers=headers)
        response.raise_for_status()  # Raises an HTTPError for bad responses (4XX or 5XX)
        
        result = response.json()

        if not result.get('candidates') or not result['candidates'][0].get('content') or not result['candidates'][0]['content'].get('parts'):
            print("❌ Error: Unexpected API response format or no content.")
            print(f"Full API Response: {result}")
            return None

        api_response_text = result['candidates'][0]['content']['parts'][0]['text']
        
        if schema:
            try:
                return json.loads(api_response_text)
            except json.JSONDecodeError as e:
                print(f"❌ Error: Could not decode JSON response from API: {e}")
                print(f"Raw API text: {api_response_text}")
                return None
        else:
            return api_response_text

    except requests.exceptions.RequestException as e:
        print(f"❌ Error calling Gemini API: {e}")
        if hasattr(e, 'response') and e.response is not None:
            try:
                print(f"API Error Response: {e.response.json()}")
            except json.JSONDecodeError:
                print(f"API Error Response (not JSON): {e.response.text}")
        return None
    except Exception as e:
        print(f"❌ An unexpected error occurred during API call: {e}")
        return None
    

