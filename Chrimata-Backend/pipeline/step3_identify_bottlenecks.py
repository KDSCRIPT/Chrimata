from helper import call_gemini_api

def identify_bottlenecks(selected_task, inputs):
    """Step 3: Identify Bottlenecks with No User Input (AI-Inferred or Input-Based)"""
    task_name = selected_task.get("task_name")
    team_name = selected_task.get("team")

    print(f"\n--- Step 3: Bottleneck Analysis for Task: {task_name} ({team_name}) ---")

    # Find optional clue for this task
    optional_clue = ""
    for clue in inputs.get("optional_bottleneck_clues", []):
        if clue["task"].strip().lower() == task_name.strip().lower():
            optional_clue = clue["description"].strip()
            break

    # Construct AI prompt
    inference_prompt = (
        f"You are analyzing a business task to identify workflow bottlenecks and AI-based improvements.\n\n"
        f"Task Details:\n"
        f"- Name: {task_name}\n"
        f"- Frequency: {selected_task.get('frequency')}\n"
        f"- Characteristics: {selected_task.get('characteristics')}\n"
        f"- Tools Used: {selected_task.get('tools_used')}\n"
        f"- Dependencies: {selected_task.get('dependencies')}\n"
    )

    if optional_clue:
        inference_prompt += f"- User-noted delay: {optional_clue}\n"

    inference_prompt += (
        "\nAnalyze the above and return:\n"
        "- bottleneck_category: Choose from ['Repetitive', 'Delayed by others/dependencies', 'Ambiguous/Complex', "
        "'Data-heavy/Info Access', 'System Limitations', 'Multiple', 'Other']\n"
        "- reasoning: Why is this the key bottleneck?\n"
        "- ai_recommendation: Suggest a smart way to address it\n"
        "- ai_tools_or_methods: Recommend tools or automation types (RPA, LLMs, integrations, etc.)\n"
        "- expected_effort: Low / Medium / High\n"
        "- expected_impact: Low / Medium / High"
    )

    schema = {
        "type": "OBJECT",
        "properties": {
            "bottleneck_category": {
                "type": "STRING",
                "enum": [
                    "Repetitive", "Delayed by others/dependencies", "Ambiguous/Complex",
                    "Data-heavy/Info Access", "System Limitations", "Multiple", "Other"
                ]
            },
            "reasoning": {"type": "STRING"},
            "ai_recommendation": {"type": "STRING"},
            "ai_tools_or_methods": {"type": "STRING"},
            "expected_effort": {"type": "STRING", "enum": ["Low", "Medium", "High"]},
            "expected_impact": {"type": "STRING", "enum": ["Low", "Medium", "High"]}
        },
        "required": ["bottleneck_category", "reasoning", "ai_recommendation", "ai_tools_or_methods", "expected_effort", "expected_impact"]
    }

    result = call_gemini_api(inference_prompt, schema=schema, instruction_type=f"bottleneck analysis for {task_name}")

    if result:
        selected_task.update({
            "bottleneck_category": result["bottleneck_category"],
            "bottleneck_reasoning": result["reasoning"],
            "bottleneck_ai_recommendation": result["ai_recommendation"],
            "bottleneck_ai_tools_or_methods": result["ai_tools_or_methods"],
            "bottleneck_expected_effort": result["expected_effort"],
            "bottleneck_expected_impact": result["expected_impact"]
        })

        print(f"  🧠 Bottleneck Category: {result['bottleneck_category']}")
        print(f"  📋 Reason: {result['reasoning']}")
        print(f"  💡 Recommendation: {result['ai_recommendation']}")
        print(f"  🛠 Tools: {result['ai_tools_or_methods']}")
        print(f"  🧮 Effort: {result['expected_effort']}, 📈 Impact: {result['expected_impact']}")
    else:
        print("⚠️ AI inference failed. You may retry or enter data manually.")
