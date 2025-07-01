from helper import call_gemini_api
import os
import pandas as pd

def roi_feasibility_and_implementation(upload_folder_path):
    """
    Extracts headers and content from upload1.csv to upload4.csv (if available),
    sends to Gemini to infer ROI-related inputs and generate a plain-English financial summary.
    """
    all_headers = {}
    combined_data = {}
    files_checked = []

    # Read each uploaded file if it exists
    for i in range(1, 5):
        file_name = f"upload{i}.csv"
        file_path = os.path.join(upload_folder_path, file_name)
        exists = os.path.exists(file_path)
        files_checked.append((file_name, exists))

        if exists:
            try:
                df = pd.read_csv(file_path)
                headers = df.columns.tolist()
                all_headers[file_name] = headers

                # Add first 3 rows of each column for more insight
                for row_index in range(min(3, len(df))):
                    for col in headers:
                        key = f"{file_name}::Row{row_index+1}::{col.strip()}"
                        value = df.at[row_index, col]
                        combined_data[key] = str(value)
            except Exception as e:
                print(f"Error reading {file_path}: {e}")

    # ROI-specific inference prompt
    roi_prompt = (
        f"The following CSV files were uploaded with their headers and first few rows:\n\n"
        f"{combined_data}\n\n"
        "Please infer and return the following as JSON:\n"
        "- tasks_per_month\n"
        "- current_time_per_task_minutes\n"
        "- people_involved_count\n"
        "- avg_hourly_cost_per_employee\n"
        "- notes on any assumptions or confidence level.\n"
        "Respond only with a JSON object."
    )

    inferred_inputs = call_gemini_api(prompt_text=roi_prompt)

    # Natural language summary prompt
    summary_prompt = (
        f"The following are data points extracted from uploaded CSVs:\n\n"
        f"{combined_data}\n\n"
        "Please analyze and provide a detailed plain-English summary of key financial insights, including:\n"
        "- Revenue patterns, cost distributions, profitability insights\n"
        "- Cash flow or resource usage trends\n"
        "- Any anomalies or areas worth attention\n"
        "- General context on financial health and AI-readiness if derivable\n"
        "- Return your output as a structured bullet-pointed summary."
    )

    summary_response = call_gemini_api(prompt_text=summary_prompt)

    # Final output
    return {
        "headers_extracted": all_headers,
        "file_presence_report": files_checked,
        "inferred_inputs": inferred_inputs,
        "roi_prompt_used": roi_prompt,
        "summary_prompt_used": summary_prompt,
        "summary": summary_response
    }
