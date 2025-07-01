import json
import os
import numpy as np
import faiss
import google.generativeai as genai
import re
import time
import logging
import agentops
from agentops.sdk.decorators import session,operation
from supabase import create_client,Client
import shutil
import os
import time
# import markdown
from dotenv import load_dotenv
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

# Connect to Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

os.makedirs('logs',exist_ok=True)
logging.basicConfig(
    filename='logs/gemini_requests.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

REQUEST_SIZE_THRESHOLD = 10240  # 10KB
LATENCY_THRESHOLD = 2.0         # 2 seconds

# Setup Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))  # Replace with your Gemini API key
chat_model = genai.GenerativeModel("gemini-2.0-flash")



# -----------------------------
# Enhanced Monitoring Wrapper
# -----------------------------
@operation
def monitored_generate_content(prompt, context="general"):
    start_time = time.time()
    response = None
    try:
        response = chat_model.generate_content(prompt)
        end_time = time.time()

        request_size = len(prompt)
        response_size = len(response.text) if hasattr(response, "text") else 0
        latency = end_time - start_time

        logging.info(f"Context: {context} | Request Size: {request_size} | Response Size: {response_size} | Latency: {latency:.2f}s")

        if request_size > REQUEST_SIZE_THRESHOLD:
            print(f"⚠️ Request size exceeded 10KB: {request_size} bytes for {context}")

        if latency > LATENCY_THRESHOLD:
            print(f"⚠️ Latency exceeded 2 seconds: {latency:.2f}s for {context}")

        return response
    except Exception as e:
        logging.error(f"Error in {context}: {str(e)}")
        raise

# -----------------------------
# Enhanced Agent Matching with Workflow Analysis
# -----------------------------
@operation
def analyze_workflow_requirements(workflow_description):
    """Extract detailed requirements from complex workflow description"""
    prompt = f"""
    You are an AI workflow architect. Analyze the following complex workflow description and extract structured requirements.

    Workflow Description:
    {workflow_description}

    Extract and return a JSON object with the following structure:
    {{
        "workflow_name": "string",
        "business_context": "string",
        "monthly_budget": "extract budget amount as number",
        "monthly_volume": "extract volume metrics",
        "key_steps": [
            {{
                "step_name": "string",
                "description": "string",
                "ai_capabilities_needed": ["list of specific AI capabilities"],
                "estimated_volume": "number or range",
                "priority": "high/medium/low"
            }}
        ],
        "technical_requirements": {{
            "latency_requirements": "string",
            "integration_needs": ["list of integrations"],
            "scalability_needs": "string",
            "compliance_requirements": ["list of compliance needs"]
        }},
        "success_metrics": ["list of success metrics"],
        "quality_standards": ["list of quality requirements"]
    }}

    Be specific and detailed in your analysis. Extract numbers where possible.
    """
    
    response = monitored_generate_content(prompt, context="workflow_analysis")
    if not response:
        return None
    
    try:
        # Extract JSON from response
        json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
    except json.JSONDecodeError:
        print("⚠️ Failed to parse workflow analysis JSON")
        return None

@operation
def find_agents_for_workflow_step(step_requirements, all_agents):
    """Find best matching agents for a specific workflow step"""
    prompt = f"""
    You are an AI agent matching specialist. Find the best AI agents from the provided list for the following workflow step.

    Workflow Step Requirements:
    Step Name: {step_requirements['step_name']}
    Description: {step_requirements['description']}
    AI Capabilities Needed: {step_requirements['ai_capabilities_needed']}
    Estimated Volume: {step_requirements.get('estimated_volume', 'Not specified')}
    Priority: {step_requirements['priority']}

    Available AI Agents:
    {json.dumps(all_agents, indent=2)}

    Analyze each agent and return a JSON array of the top 3 most suitable agents with this structure:
    [
        {{
            "agent_name": "string",
            "suitability_score": "number 1-10",
            "reasons": ["list of specific reasons why this agent fits"],
            "estimated_usage": "how this agent would be used in this step",
            "potential_limitations": ["any limitations or concerns"]
        }}
    ]

    Consider use cases, pricing, latency, integration capabilities, and quality fit.
    """
    
    response = monitored_generate_content(prompt, context="agent_matching")
    if not response:
        return []
    
    try:
        json_match = re.search(r'\[.*\]', response.text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
    except json.JSONDecodeError:
        print("⚠️ Failed to parse agent matching JSON")
        return []

@operation
def calculate_workflow_costs(workflow_analysis, agent_assignments):
    """Calculate detailed costs for the entire workflow"""
    prompt = f"""
    You are a cost analysis expert for AI workflows. Calculate detailed costs for the following workflow.

    Workflow Analysis:
    {json.dumps(workflow_analysis, indent=2)}

    Agent Assignments:
    {json.dumps(agent_assignments, indent=2)}

    Perform detailed cost calculations and return a JSON object with this structure:
    {{
        "total_monthly_cost": "number",
        "cost_breakdown": [
            {{
                "step_name": "string",
                "agents_used": ["list of agent names"],
                "input_costs": "number",
                "output_costs": "number",
                "step_total": "number",
                "volume_assumptions": "string explaining calculations"
            }}
        ],
        "cost_per_operation": "number",
        "budget_analysis": {{
            "budget_available": "number from workflow",
            "budget_utilization": "percentage",
            "cost_optimization_suggestions": ["list of suggestions"]
        }},
        "scaling_projections": {{
            "at_2x_volume": "number",
            "at_5x_volume": "number",
            "at_10x_volume": "number"
        }}
    }}

    Be specific with your calculations. Show your work for volume-based pricing.
    Extract pricing information from the agent data (InputPrice, OutputPrice fields).
    Consider that pricing might be in various formats (per token, per request, per minute, etc.).
    """
    
    response = monitored_generate_content(prompt, context="cost_calculation")
    if not response:
        return None
    
    try:
        json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
    except json.JSONDecodeError:
        print("⚠️ Failed to parse cost calculation JSON")
        return None

@operation
def generate_workflow_implementation_plan(workflow_analysis, agent_assignments, cost_analysis):
    """Generate a detailed implementation plan"""
    prompt = f"""
    You are a workflow implementation specialist. Create a detailed implementation plan.

    Workflow Analysis: {json.dumps(workflow_analysis, indent=2)}
    Agent Assignments: {json.dumps(agent_assignments, indent=2)}
    Cost Analysis: {json.dumps(cost_analysis, indent=2)}

    Create a comprehensive implementation plan with:
    1. Architecture overview
    2. Integration sequence
    3. Timeline and milestones
    4. Risk assessment
    5. Performance monitoring plan
    6. Optimization opportunities

    Return a detailed markdown document.
    """
    
    response = monitored_generate_content(prompt, context="implementation_planning")
    return response.text if response else "Implementation plan generation failed."

# -----------------------------
# Main Workflow Processing Function
# -----------------------------
@operation
def process_complex_workflow(workflow_description):
    print("🔍 Step 1: Analyzing workflow requirements...")
    workflow_analysis = analyze_workflow_requirements(workflow_description)
    if not workflow_analysis:
        print("❌ Failed to analyze workflow requirements")
        return None

    print("📊 Step 2: Loading agents from Supabase...")
    try:
        response = supabase.table("agents").select("*").execute()
        all_agents = response.data
    except Exception as e:
        print("❌ Error fetching agents:", e)
        return None

    print("🎯 Step 3: Matching agents to workflow steps...")
    agent_assignments = {}
    for step in workflow_analysis.get("key_steps", []):
        print(f"   Processing step: {step['step_name']}")
        matched_agents = find_agents_for_workflow_step(step, all_agents)
        agent_assignments[step['step_name']] = matched_agents
        time.sleep(1)

    print("💰 Step 4: Calculating costs...")
    cost_analysis = calculate_workflow_costs(workflow_analysis, agent_assignments)

    print("📋 Step 5: Generating implementation plan...")
    implementation_plan = generate_workflow_implementation_plan(
        workflow_analysis, agent_assignments, cost_analysis
    )

    return {
        "workflow_analysis": workflow_analysis,
        "agent_assignments": agent_assignments,
        "cost_analysis": cost_analysis,
        "implementation_plan": implementation_plan,
    }


# -----------------------------
# Original Functions (Restored)
# -----------------------------
@operation
def enrich_agent_data(agent):
    prompt = f"""
You are an AI product expert.

Take the following basic AI tool data and enhance each field with more clarity and detail. Make sure to elaborate the 'Use Case' by listing specific tasks. Also, make each field useful for cost estimation and quality assessment.

Example data:
Name: {agent['Name']}
Provider: {agent['Provider']}
Use Case: {agent['UseCase']}
Category: {agent['Category']}
Input Price: {agent['InputPrice']}
Output Price: {agent['OutputPrice']}
Integration: {agent['Integration']}
Free Tier: {agent['FreeTier']}
Latency: {agent['Latency']}
Website: {agent['Website']}
Alternatives: {agent['Alternatives']}
This is a JSON object with keys:
Name, Provider, UseCase, Category, InputPrice, OutputPrice, Integration, FreeTier, Latency, Website, Alternatives.
Return updated fields in JSON format with the same keys.
No need to give anything else other than the JSON object.
"""

    response = monitored_generate_content(prompt, context="data_enrichment")
    if not response:
        return agent  # fallback

    print(f"\n📨 Gemini raw response:\n{response.text}")

    pattern = r'"?(Name|Provider|UseCase|Category|InputPrice|OutputPrice|Integration|FreeTier|Latency|Website|Alternatives)"?\s*:\s*[""]?(.+?)[""]?(?:,|\n|$)'
    matches = re.findall(pattern, response.text, re.DOTALL)

    enriched = {key: agent.get(key, "") for key in agent}
    for key, value in matches:
        enriched[key.strip()] = value.strip().rstrip(',')

    return enriched

@operation
def enrich_all_agents():
    print("📥 Fetching agents that are not enriched...")
    try:
        response = supabase.table("agents").select("*").eq("Enriched", False).execute()
        agents = response.data
    except Exception as e:
        print("❌ Failed to fetch agents:", e)
        return False

    enriched_rows = []
    for agent in agents:
        enriched = enrich_agent_data(agent)
        enriched["Enriched"] = True
        enriched_rows.append(enriched)

    print(f"✨ Enriching {len(enriched_rows)} agents...")

    for enriched_agent in enriched_rows:
        try:
            supabase.table("agents").update(enriched_agent).eq("Name", enriched_agent["Name"]).execute()
            print(f"✅ Updated agent: {enriched_agent['Name']}")
        except Exception as e:
            print(f"❌ Failed to update agent {enriched_agent['Name']}:", e)

    return True


@operation
def get_embedding(text):
    response = genai.embed_content(
        model="models/embedding-001",
        content=text,
        task_type="retrieval_document"
    )
    return response["embedding"]

@operation
def build_faiss_index():
    print("📥 Fetching agents for FAISS indexing...")
    try:
        response = supabase.table("agents").select("Name, UseCase, Category").execute()
        rows = response.data
    except Exception as e:
        print("❌ Failed to fetch agents for FAISS:", e)
        return

    embeddings = []
    agent_map = {}

    for i, agent in enumerate(rows):
        name = agent["Name"]
        use_case = agent["UseCase"]
        category = agent["Category"]
        combined_text = f"{use_case}. Category: {category}"

        embedding = get_embedding(combined_text)
        embeddings.append(embedding)
        agent_map[i] = name

    vectors = np.array(embeddings).astype("float32")
    index = faiss.IndexFlatL2(len(vectors[0]))
    index.add(vectors)

    faiss.write_index(index, "data/agents_faiss.index")
    with open("data/index_map.json", "w") as f:
        json.dump(agent_map, f)

    print("✅ FAISS index built and saved.")


# -----------------------------
# Output Generation Functions
# -----------------------------
@operation
def generate_ai_selection_summary(result):
    """Generate a focused summary of AI agents to be used"""
    prompt = f"""
You are an AI architecture consultant. Based on the workflow analysis, create a focused summary document listing all AI agents that will be used in this workflow.

Workflow Analysis Data:
{json.dumps(result, indent=2)}

Create a structured summary with:

1. AI AGENTS SELECTION OVERVIEW
   - Total number of AI agents recommended
   - Categories of AI tools being used
   - Key selection criteria applied

2. DETAILED AI AGENT LIST
   For each selected AI agent, provide:
   - Agent Name and Provider
   - Primary Use Case in this workflow
   - Expected Usage Volume
   - Cost per operation/month
   - Key capabilities being leveraged
   - Integration requirements

3. ARCHITECTURE DECISION RATIONALE
   - Why these specific AI agents were chosen
   - How they work together in the workflow
   - Alternative options considered and rejected
   - Technical compatibility considerations

4. FINANCIAL BREAKDOWN BY AI AGENT
   - Individual cost contribution
   - Volume-based pricing analysis
   - Scaling cost projections

Format as a clear, technical document that AI developers, product managers, and tech leads can use for implementation planning.
"""
    
    response = monitored_generate_content(prompt, context="ai_selection_summary")
    return response.text if response else "AI selection summary generation failed."

@operation
def generate_formal_report(result):
    file_path="prompts/base_prompt.txt"
    improved_file_path = "prompts/improved_prompts.txt"
    # Choose the appropriate file to load
    file_to_load = improved_file_path if os.path.exists(improved_file_path) else file_path
    with open(file_to_load, "r", encoding="utf-8") as file:
        base_prompt = file.read()
    prompt = f"{base_prompt}\n\nWorkflow Analysis Data:\n{json.dumps(result, indent=2)}"
    
    response = monitored_generate_content(prompt, context="formal_report_generation")
    return response.text if response else "Report generation failed."


# -----------------------------
# Enhanced Main Execution
# -----------------------------

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def ensure_bucket_exists(bucket_name: str):
    """Create bucket if it doesn't exist"""
    try:
        existing = supabase.storage.list_buckets()
        if not any(b.name == bucket_name for b in existing):#check this 
            supabase.storage.create_bucket(bucket_name, options={
            "public": False
        })
            print(f"📦 Created new bucket: {bucket_name}")
        else:
            print(f"📦 Bucket already exists: {bucket_name}")
    except Exception as e:
        print(f"❌ Error ensuring bucket exists: {e}")


def upload_to_supabase(bucket_name, file_path, subfolder):
    """Upload file to Supabase under subfolder in user bucket if not already present"""
    file_name = os.path.basename(file_path)
    storage_path = f"{subfolder}/{file_name}"

    try:
        with open(file_path, "rb") as f:
            res = supabase.storage.from_(bucket_name).upload(
                path=storage_path,
                file=f,
                file_options={"cache-control": "3600", "upsert": False}
            )
        print(f"✅ Uploaded: {bucket_name}/{storage_path}")
           
    except Exception as e:
        print(f"❌ Upload failed: {e}")
        


@session
def main1(user):
    os.makedirs('summaries', exist_ok=True)
    os.makedirs('reports', exist_ok=True)
    os.makedirs('data', exist_ok=True)
    os.makedirs("chathistory",exist_ok=True)

    with open('summaries/industrial_workflow_summary.json') as f:
        data = json.load(f)

    COMPLEX_WORKFLOW_EXAMPLES = {
        "content_creation_pipeline": data,
        "ecommerce_automation": data,
        "research_development": data
    }

    print("🚀 AI Workflow Solution Generator")
    print("=" * 50)

    print("📥 Step 1: Enriching agent data from Gemini...")
    # enrich_all_agents()

    print("📊 Step 2: Building FAISS index...")
    # build_faiss_index()

    workflow_type = "content_creation_pipeline"
    workflow_description = COMPLEX_WORKFLOW_EXAMPLES[workflow_type]

    print(f"📝 Step 3: Processing workflow: {workflow_type}")
    print(f"📄 Workflow description length: {len(str(workflow_description))} characters")

    result = process_complex_workflow(workflow_description)

    if not result:
        print("❌ Failed to process workflow")
        return False

    print("\n" + "="*50)
    print("📊 WORKFLOW ANALYSIS COMPLETE")
    print("="*50)

    if result['workflow_analysis']:
        print(f"🎯 Workflow: {result['workflow_analysis'].get('workflow_name', 'Unknown')}")
        print(f"💰 Budget: ${result['workflow_analysis'].get('monthly_budget', 'Not specified')}/month")
        print(f"📈 Volume: {result['workflow_analysis'].get('monthly_volume', 'Not specified')}")

    if result['cost_analysis']:
        print(f"\n💵 TOTAL ESTIMATED COST: ${result['cost_analysis'].get('total_monthly_cost', 'Not calculated')}/month")
        if 'budget_analysis' in result['cost_analysis']:
            budget_util = result['cost_analysis']['budget_analysis'].get('budget_utilization', 'N/A')
            print(f"📊 Budget Utilization: {budget_util}")

    print(f"\n📋 Agent Assignments:")
    for step_name, agents in result['agent_assignments'].items():
        print(f"\n🔹 {step_name}:")
        for agent in agents[:2]:
            print(f"   • {agent.get('agent_name', 'Unknown')} (Score: {agent.get('suitability_score', 'N/A')}/10)")

    print("\n" + "="*50)
    print("📄 GENERATING DETAILED OUTPUTS")
    print("="*50)

    print("📝 Generating formal business report...")
    formal_report = generate_formal_report(result)


    filename=f"{user['id']}_{int(time.time())}_workflow_formal_report"
    md_path = f'reports/{filename}.md'

    chathistory_path=f"chathistory/{filename}.json"

    with open(chathistory_path,'w') as f:
        pass

    with open(md_path, 'w') as f:
        f.write(formal_report)

    print("\n💾 OUTPUTS SAVED LOCALLY")

    # Upload to user-specific bucket
    try:
        ensure_bucket_exists("reports")
        ensure_bucket_exists("chathistory")
        # upload_to_supabase(bucket_name, json_path, "summaries")
        upload_to_supabase("chathistory",chathistory_path,f"{user['id']}")
        upload_to_supabase("reports", md_path,f"{user['id']}")

        print("📤 Supabase upload complete.")
    except Exception as e:
        print(f"❌ Upload to Supabase failed: {e}")

    print("\n" + "="*50)
    print("📄 FORMAL REPORT PREVIEW")
    print("="*50)
    print(formal_report[:1500] + "\n...(continued in report)")

    print("Deleting temporary directories and files for Supabase bucket upload")
    try:
        shutil.rmtree("reports")
        shutil.rmtree("summaries")
        shutil.rmtree("chathistory")
        shutil.rmtree("uploads")
        print(f"✅Deleting temporary directories and files for Supabase bucket upload")
    except Exception as e:
        print("❌Error in deleting local temporary directories and files:",e)
    
    return filename

