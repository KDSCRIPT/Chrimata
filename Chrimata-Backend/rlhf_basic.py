import json
import google.generativeai as genai
import requests

from dotenv import load_dotenv
import os
load_dotenv()

# Step 1: Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.0-flash")

def load_base_prompt(file_path="prompts/base_prompt.txt"):
    # Check if the improved prompt file exists
    improved_file_path = "prompts/improved_prompts.txt"
    # Choose the appropriate file to load
    file_to_load = improved_file_path if os.path.exists(improved_file_path) else file_path
    
    # Load the content from the chosen file
    with open(file_to_load, "r", encoding="utf-8") as file:
        return file.read()

  

# Step 3: Check if feedback is relevant to AI cost optimization
def is_feedback_relevant(feedback):
    relevance_check_prompt = f"""
You are an AI assistant. A user has given feedback on a report-generating agent related to AI architecture and cost optimization.

Determine if the feedback is relevant to optimizing AI agent architecture, tool selection, or cost considerations (e.g., ROI, inference cost, implementation cost, scaling, efficiency, etc.).

Feedback:
\"\"\"{feedback}\"\"\"

Answer only "yes" or "no".
"""
    response = model.generate_content(relevance_check_prompt)
    return response.text.strip().lower().startswith("yes")

# Step 4: Optimize prompt if needed
def optimize_prompt(original_prompt, feedback, result):
    prompt_optimizer = f"""
You are a prompt optimizer AI. Improve the following prompt based on the user's feedback while preserving its structure and professional tone.

Original Prompt:
\"\"\"{original_prompt}\"\"\"

User Feedback:
\"\"\"{feedback}\"\"\"

Only improve it if the feedback is relevant to the AI cost optimization use case. Add details, clarify instructions, or reframe wording as needed. If it is for a perticular use case add the wording that if this use case do so and all.

Return ONLY the improved prompt.
"""
    response = model.generate_content(prompt_optimizer)
    return response.text.strip()

# Step 5: Generate final prompt (optimized if relevant)
def build_final_prompt(result, feedback):
    base_prompt = load_base_prompt()

    if feedback and is_feedback_relevant(feedback):
        improved_prompt = optimize_prompt(base_prompt, feedback, result)
        print("✅ Prompt optimized based on relevant feedback.\n")
        with open("prompts/improved_prompt.txt", "w") as file:
            file.write(improved_prompt)
        return improved_prompt + "\n\nWorkflow Analysis Data:\n" #+ json.dumps(result, indent=2)
    

    else:
        print("ℹ️ Feedback not relevant — using base prompt.\n")
        return base_prompt #+ "\n\nWorkflow Analysis Data:\n" + json.dumps(result, indent=2)

