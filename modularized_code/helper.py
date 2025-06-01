import requests,json
from constants import API_KEY,GEMINI_API_URL

def get_user_input(prompt_message, multi_line=False):
    """Gets input from the user."""
    print(f"\n{prompt_message}")
    if multi_line:
        lines = []
        while True:
            line = input()
            if line:
                lines.append(line)
            else:
                break
        return "\n".join(lines)
    return input(">> ")

def get_numerical_input(prompt_message, data_type=float):
    """Gets numerical input from the user and validates it."""
    while True:
        raw_input = get_user_input(prompt_message)
        try:
            return data_type(raw_input)
        except ValueError:
            print(f"Invalid input. Please enter a valid number ({data_type.__name__}).")


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
    

def get_validated_input(prompt, allow_empty=False, multi_line=False):
    while True:
        response = get_user_input(prompt, multi_line=multi_line)
        if response.strip() or allow_empty:
            return response.strip()
        print("Please provide a valid response.")
