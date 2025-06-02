from flask import Flask, request, jsonify
from main import main  # assuming main() is in main.py
from inputs import InputData
from rag_implementation import main1
from qanda import initialize_chatbot, get_chatbot_response  # <-- Import your chatbot logic
import os

app = Flask(__name__)

# Helper to build InputData from JSON
def build_input_data_from_json(data):
    inputs = InputData()
    inputs.industry_model = data.get("industry_model", "")
    inputs.company_size = data.get("company_size", "")
    inputs.goals = data.get("goals", "")
    inputs.top_challenges = data.get("top_challenges", "")
    inputs.tools_platforms = data.get("tools_platforms", "")
    inputs.departments_str = data.get("departments_str", "")
    inputs.team_summaries = data.get("team_summaries", {})
    inputs.task_number = data.get("task_number", 1)
    inputs.optional_bottleneck_clues = data.get("optional_bottleneck_clues", {})
    inputs.roi_inputs = data.get("roi_inputs", {})
    inputs.step7_inputs = data.get("step7_inputs", {})
    return inputs

@app.route('/run-workflow', methods=['POST'])
def run_workflow():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid or missing JSON"}), 400

    inputs = build_input_data_from_json(data)
    summary = main(inputs)  # Call your workflow
    main1()

    return jsonify(summary)

@app.route('/ask-chatbot', methods=['POST'])
def ask_chatbot():
    data = request.get_json()
    if not data or "question" not in data:
        return jsonify({"error": "Missing 'question' in JSON"}), 400

    question = data["question"]
    chat_history = data.get("chat_history", [])
    include_context = data.get("include_report_context", True)

    # Ensure chatbot is initialized
    init_result = initialize_chatbot()
    if init_result.get("status") != "success":
        return jsonify({"error": "Chatbot initialization failed", "details": init_result}), 500

    # Get chatbot response
    response = get_chatbot_response(question, chat_history, include_context)
    return jsonify(response)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

