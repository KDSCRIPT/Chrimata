from helper import call_gemini_api

def step4_match_to_ai_primitives(selected_task):
    """Step 4: Fully AI-inferred Mapping to AI Primitives"""
    print(f"\n--- Step 4: Matching to AI Primitives for Task: {selected_task.get('task_name')} ---")

    prompt = (
        f"You are an AI transformation expert. Analyze the following task to determine its alignment with AI primitives and feasibility for automation or augmentation:\n\n"
        f"Task Name: {selected_task.get('task_name')}\n"
        f"Team: {selected_task.get('team')}\n"
        f"Frequency: {selected_task.get('frequency')}\n"
        f"Characteristics: {selected_task.get('characteristics')}\n"
        f"Tools Used: {selected_task.get('tools_used')}\n"
        f"Dependencies: {selected_task.get('dependencies')}\n"
        f"Bottleneck Category: {selected_task.get('bottleneck_category')}\n"
        f"Bottleneck Reasoning: {selected_task.get('bottleneck_reasoning')}\n"
        f"AI Suggestion (prior step): {selected_task.get('bottleneck_ai_recommendation')}\n"
        f"Suggested Tools (prior): {selected_task.get('bottleneck_ai_tools_or_methods')}\n\n"
        "Now return a complete assessment in JSON format with the following:\n"
        "1. ai_categories: List of AI primitives (Content, Automation, Research, Coding, Data Analysis, Ideation, Other)\n"
        "2. why_each_category_applies: List of objects with 'category' and 'explanation'\n"
        "3. suggested_tool_type: General tool type (e.g., RPA, GPT-4, LangChain, SaaS, Zapier)\n"
        "4. example_tools: 3-5 real-world tools\n"
        "5. build_vs_buy_consideration: [Likely Build, Likely Buy, Hybrid, Not clear yet]\n"
        "6. rationale_for_build_vs_buy: Short reason\n"
        "7. task_segmentation: What AI can do vs what humans should do\n"
        "8. ai_readiness_score: 0–10 scale\n"
        "9. automation_complexity: Low, Medium, High"
    )

    schema = {
        "type": "object",
        "properties": {
            "ai_categories": {
                "type": "array",
                "items": {
                    "type": "string",
                    "enum": ["Content", "Automation", "Research", "Coding", "Data Analysis", "Ideation", "Other"]
                }
            },
            "why_each_category_applies": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "category": {"type": "string"},
                        "explanation": {"type": "string"}
                    },
                    "required": ["category", "explanation"]
                }
            },
            "suggested_tool_type": {"type": "string"},
            "example_tools": {
                "type": "array",
                "items": {"type": "string"}
            },
            "build_vs_buy_consideration": {
                "type": "string",
                "enum": ["Likely Build", "Likely Buy", "Hybrid", "Not clear yet"]
            },
            "rationale_for_build_vs_buy": {"type": "string"},
            "task_segmentation": {
                "type": "object",
                "properties": {
                    "ai_part": {"type": "string"},
                    "human_part": {"type": "string"}
                },
                "required": ["ai_part", "human_part"]
            },
            "ai_readiness_score": {"type": "number"},
            "automation_complexity": {
                "type": "string",
                "enum": ["Low", "Medium", "High"]
            }
        },
        "required": [
            "ai_categories",
            "why_each_category_applies",
            "suggested_tool_type",
            "example_tools",
            "build_vs_buy_consideration",
            "rationale_for_build_vs_buy",
            "task_segmentation",
            "ai_readiness_score",
            "automation_complexity"
        ]
    }

    result = call_gemini_api(
        prompt_text=prompt,
        schema=schema,
        instruction_type=f"AI feasibility mapping for {selected_task.get('task_name')}"
    )

    if result:
        # Convert list of {category, explanation} to a dictionary
        why_dict = {item['category']: item['explanation'] for item in result.get('why_each_category_applies', [])}

        selected_task.update({
            'ai_categories': result.get('ai_categories'),
            'why_each_category_applies': why_dict,
            'suggested_tool_type': result.get('suggested_tool_type'),
            'example_tools': result.get('example_tools'),
            'build_vs_buy_consideration': result.get('build_vs_buy_consideration'),
            'rationale_for_build_vs_buy': result.get('rationale_for_build_vs_buy'),
            'task_segmentation': result.get('task_segmentation'),
            'ai_readiness_score': result.get('ai_readiness_score'),
            'automation_complexity': result.get('automation_complexity')
        })

        print(f"\n✅ AI Categories: {', '.join(result['ai_categories'])}")
        for cat, reason in why_dict.items():
            print(f"   • {cat}: {reason}")
        print(f"🛠 Suggested Tool Type: {result['suggested_tool_type']}")
        print(f"🔧 Example Tools: {', '.join(result['example_tools'])}")
        print(f"🏗 Build vs. Buy: {result['build_vs_buy_consideration']} ({result['rationale_for_build_vs_buy']})")
        print(f"🧠 AI handles: {result['task_segmentation']['ai_part']}")
        print(f"🙋 Human handles: {result['task_segmentation']['human_part']}")
        print(f"📈 AI Readiness Score: {result['ai_readiness_score']}/10")
        print(f"⚙️ Automation Complexity: {result['automation_complexity']}")
    else:
        print("❗ AI primitive matching failed. You may retry later or collect inputs manually.")
