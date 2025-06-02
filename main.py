from generate_summary import generate_final_summary
# --- Workflow Steps ---
from step1 import step1_collect_business_context
from step2 import step2_identify_team_specific_workflows
from step3 import step3_identify_bottlenecks
from step4 import step4_match_to_ai_primitives
from step5 import step5_human_in_the_loop_check_and_data
from step6 import step6_roi_feasibility_and_implementation
from step7 import step7_monitoring_feedback_integration_strategy
from inputs import InputData
import time

# --- Main Application Logic ---
def main(inputs):
    """Main function to run the AI Workflow Discovery Framework."""
    print("🚀 Welcome to the AI Workflow Discovery Framework (Industrialist Edition)! 🚀")
    print("This tool will guide you through 7 steps to identify and analyze workflows for AI improvement, focusing on practical and strategic insights.")
    
    business_context = step1_collect_business_context(inputs)
    
    # selected_task_for_analysis = step2_identify_team_specific_workflows(business_context, inputs)
    all_tasks = step2_identify_team_specific_workflows(business_context, inputs)
    summary = 0
    if all_tasks:
        print(f"\nTotal tasks identified: {len(all_tasks)}")
        # You can then loop over all_tasks for further processing or next steps
        for task in all_tasks[:1]:
            print(f"Task: {task['task_name']} ({task['team']}) - Frequency: {task['frequency']}")
            step3_identify_bottlenecks(task, inputs)
            time.sleep(10)

            step4_match_to_ai_primitives(task)
            time.sleep(10)

            step5_human_in_the_loop_check_and_data(task) # Renamed and enhanced
            time.sleep(10)

            step6_roi_feasibility_and_implementation(task, business_context, inputs) # Renamed and enhanced
            time.sleep(10)

            step7_monitoring_feedback_integration_strategy(task, business_context, inputs) # Renamed and enhanced
            time.sleep(10)

            summary = generate_final_summary(business_context, task)

    else:
        print("No tasks identified.")
    return summary


if __name__ == "__main__":
    inputs = InputData()
    main(inputs)