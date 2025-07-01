from generate_summary import generate_final_summary
# --- Workflow Steps ---
from pipeline.step1_collect_business_context import collect_business_context
from pipeline.step2_identify_team_specific_workflows import identify_team_specific_workflows
from pipeline.step3_identify_bottlenecks import identify_bottlenecks
from pipeline.step4_match_to_ai_primitives import match_to_ai_primitives
from pipeline.step5_human_in_the_loop_check_and_data import human_in_the_loop_check_and_data
from pipeline.step6_roi_feasibility_and_implementation import roi_feasibility_and_implementation
from pipeline.step7_monitoring_feedback_integration_strategy import monitoring_feedback_integration_strategy
import time

# --- Main Application Logic ---
def main(inputs):
    """Main function to run the AI Workflow Discovery Framework."""
    print("🚀 Welcome to the AI Workflow Discovery Framework (Industrialist Edition)! 🚀")
    print("This tool will guide you through 7 steps to identify and analyze workflows for AI improvement, focusing on practical and strategic insights.")
    
    business_context = collect_business_context(inputs)
    
    # selected_task_for_analysis = step2_identify_team_specific_workflows(business_context, inputs)
    all_tasks = identify_team_specific_workflows(business_context, inputs)
    summary = 0
    if all_tasks:
        print(f"\nTotal tasks identified: {len(all_tasks)}")
        # You can then loop over all_tasks for further processing or next steps
        for task in all_tasks[:1]:
            print(f"Task: {task['task_name']} ({task['team']}) - Frequency: {task['frequency']}")
            identify_bottlenecks(task, inputs)
            time.sleep(10)

            match_to_ai_primitives(task)
            time.sleep(10)

            human_in_the_loop_check_and_data(task) # Renamed and enhanced
            time.sleep(10)

            roi_feasibility_and_implementation("upload") # Renamed and enhanced
            time.sleep(10)

            monitoring_feedback_integration_strategy(task, business_context, inputs) # Renamed and enhanced
            time.sleep(10)

            summary = generate_final_summary(business_context, task)

    else:
        print("No tasks identified.")
    return summary
