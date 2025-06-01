from helper import call_gemini_api

def step5_human_in_the_loop_check_and_data(selected_task):
    """Step 5: Human-in-the-Loop & Data Sensitivity Analysis (AI-inferred)"""
    print(f"\n--- Step 5: Human-in-the-Loop & Data Sensitivity for Task: {selected_task.get('task_name')} ---")

    # Compose AI prompt using only collected metadata
    prompt_to_gemini = (
        f"Analyze the following task and return a risk and governance assessment:\n\n"
        f"Task Name: {selected_task.get('task_name')}\n"
        f"Characteristics: {selected_task.get('characteristics', 'N/A')}\n"
        f"AI Categories: {', '.join(selected_task.get('ai_categories', []))}\n"
        f"AI Readiness Score: {selected_task.get('ai_readiness_score', 'N/A')}\n"
        f"Automation Complexity: {selected_task.get('automation_complexity', 'N/A')}\n"
        f"Task Segmentation: AI handles - {selected_task.get('task_segmentation', {}).get('ai_part', '')}; "
        f"Human handles - {selected_task.get('task_segmentation', {}).get('human_part', '')}\n"
        f"Bottleneck Reason: {selected_task.get('bottleneck_reasoning', 'N/A')}\n"
        f"Tools Used: {selected_task.get('tools_used', 'N/A')}\n\n"
        "Return a JSON object with:\n"
        "- risk_level: 'Low', 'Medium', or 'High' (based on potential harm from AI errors)\n"
        "- human_in_loop_design: e.g. 'Supervise', 'Approve', 'Fallback Only', 'None'\n"
        "- explanation_of_risk\n"
        "- feedback_loop_quality: 'Strong', 'Weak', or 'None'\n"
        "- feedback_capture_method: e.g., 'audit log review', 'ratings', 'manual comments'\n"
        "- data_sensitivity: {\n"
        "    contains_sensitive_data: true/false,\n"
        "    data_types: e.g. ['PII', 'Internal Financials'],\n"
        "    regulations: e.g. ['GDPR', 'HIPAA'],\n"
        "    recommended_mitigation: e.g. 'encryption, access control'\n"
        "}"
    )

    schema = {
        "type": "object",
        "properties": {
            "risk_level": {
                "type": "string",
                "enum": ["Low", "Medium", "High"]
            },
            "human_in_loop_design": {
                "type": "string",
                "enum": ["Supervise", "Approve", "Fallback Only", "None"]
            },
            "explanation_of_risk": {
                "type": "string"
            },
            "feedback_loop_quality": {
                "type": "string",
                "enum": ["Strong", "Weak", "None"]
            },
            "feedback_capture_method": {
                "type": "string"
            },
            "data_sensitivity": {
                "type": "object",
                "properties": {
                    "contains_sensitive_data": {
                        "type": "boolean"
                    },
                    "data_types": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "regulations": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "recommended_mitigation": {
                        "type": "string"
                    }
                },
                "required": [
                    "contains_sensitive_data",
                    "data_types",
                    "regulations",
                    "recommended_mitigation"
                ]
            }
        },
        "required": [
            "risk_level",
            "human_in_loop_design",
            "explanation_of_risk",
            "feedback_loop_quality",
            "feedback_capture_method",
            "data_sensitivity"
        ]
    }

    insights = call_gemini_api(
        prompt_text=prompt_to_gemini,
        schema=schema,
        instruction_type="Human loop & sensitivity assessment"
    )

    if insights:
        selected_task.update({
            'risk_level': insights['risk_level'],
            'human_in_loop_design': insights['human_in_loop_design'],
            'explanation_of_risk': insights['explanation_of_risk'],
            'feedback_loop_quality': insights['feedback_loop_quality'],
            'feedback_capture_method': insights['feedback_capture_method'],
            'data_sensitivity': insights['data_sensitivity'],
        })

        print(f"\n🤖 AI Risk Level: {insights['risk_level']}")
        print(f"🤖 Human-in-the-Loop Model: {insights['human_in_loop_design']}")
        print(f"🤖 Risk Reason: {insights['explanation_of_risk']}")
        print(f"🤖 Feedback Loop Quality: {insights['feedback_loop_quality']}")
        print(f"🤖 Feedback Capture: {insights['feedback_capture_method']}")
        print(f"🤖 Data Sensitivity: {', '.join(insights['data_sensitivity']['data_types'])}")
        print(f"🤖 Regulations: {', '.join(insights['data_sensitivity']['regulations'])}")
        print(f"🤖 Mitigation Strategy: {insights['data_sensitivity']['recommended_mitigation']}")
    else:
        print("⚠️ AI analysis failed. Please enter these details manually.")
