import os
import json
import jwt
import requests
from flask import Flask, request, jsonify,send_file
from rlhf_basic import build_final_prompt
from flask_cors import CORS
from dotenv import load_dotenv
from supabase import create_client, Client
from functools import wraps
from main import main
from rag_implementation import main1
from qanda import initialize_chatbot, get_chatbot_response
from werkzeug.utils import secure_filename
from io import BytesIO
import agentops
from jose import jwt
from jose.exceptions import JWTError, ExpiredSignatureError
from jwt.algorithms import RSAAlgorithm  # from PyJWT, for key decoding


def decode_file(file):
    try:
        return file.decode("utf-8")
    except UnicodeDecodeError:
        try:
            return file.decode("windows-1252")
        except UnicodeDecodeError:
            return file.decode("latin-1")  # last resort
# Load environment variables
load_dotenv()


app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": ["http://localhost:3000", "https://chrimata-frontend-xi.vercel.app"]}},  
      supports_credentials=True,
    allow_headers="*",
    methods=["GET", "POST", "OPTIONS"]
     )

# Clerk configuration
CLERK_SECRET_KEY = os.getenv("CLERK_SECRET_KEY")
CLERK_PUBLISHABLE_KEY = os.getenv("CLERK_PUBLISHABLE_KEY")

if not CLERK_SECRET_KEY:
    raise ValueError("CLERK_SECRET_KEY must be set in environment variables")

# Supabase configuration (for storage only)
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
    raise ValueError("Supabase URL and Service Role Key must be set in environment variables")

# Create Supabase client (for storage operations only)
supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)


CLERK_PUBLISHABLE_KEY = os.getenv("CLERK_PUBLISHABLE_KEY", "")
CLERK_FRONTEND_API = CLERK_PUBLISHABLE_KEY.split("_")[1]  # e.g. 'test', 'abcd123'
CLERK_ISSUER = "https://working-ram-26.clerk.accounts.dev"
JWKS_URL = "https://working-ram-26.clerk.accounts.dev/.well-known/jwks.json"


def verify_clerk_token(token: str):
    """Verify Clerk JWT token and return user claims"""
    try:
        # Remove 'Bearer ' prefix if present
        if token.startswith("Bearer "):
            token = token[len("Bearer "):]

        # Decode header to get 'kid'
        unverified_header = jwt.get_unverified_header(token)
        kid = unverified_header.get("kid")
        if not kid:
            print("No 'kid' found in token header")
            return None

        # Fetch JWKS from Clerk
        jwks_response = requests.get(JWKS_URL)
        jwks_response.raise_for_status()
        jwks = jwks_response.json()

        # Find the JWK with the correct 'kid'
        key_data = next((key for key in jwks["keys"] if key["kid"] == kid), None)
        if not key_data:
            print("No matching key found in JWKS")
            return None

        # Convert JWK to public RSA key
        public_key = RSAAlgorithm.from_jwk(key_data)

        # Decode and verify token
        payload = jwt.decode(
            token,
            key=public_key,
            algorithms=["RS256"],
            issuer=CLERK_ISSUER,
            options={"verify_aud": False}  # Set to True if you need audience check
        )

        return payload

    except ExpiredSignatureError:
        print("Token expired")
        return None
    except JWTError as e:
        print(f"JWT verification failed: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error during verification: {e}")
        return None


def auth_required(f):
    """Decorator to ensure that the user is authenticated using Clerk token."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Extract the token from the Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return jsonify({"message": "Authorization header required"}), 401
        
        # Verify the Clerk token
        user_data = verify_clerk_token(auth_header)
        if not user_data:
            return jsonify({"message": "Invalid or expired token"}), 401
        
        # Add user info to the request context
        request.user = {
            'id': user_data.get('sub'),  # Clerk user ID
            'email': user_data.get('email'),
            'name': user_data.get('name', ''),
            'first_name': user_data.get('given_name', ''),
            'last_name': user_data.get('family_name', '')
        }
        
        return f(*args, **kwargs)
    
    return decorated_function

@app.route("/api/user/profile", methods=["GET"])
@auth_required
def profile():
    """Get user profile from Clerk token"""
    try:
        user = request.user
        return jsonify({
            "id": user['id'],
            "email": user['email'],
            "name": user['name'],
            "first_name": user['first_name'],
            "last_name": user['last_name']
        }), 200
    except Exception as e:
        print(f"Profile error: {e}")
        return jsonify({"message": "Failed to fetch profile"}), 500

@app.route("/api/user/update-profile", methods=["PUT"])
@auth_required
def update_profile():
    """Update user profile via Clerk API"""
    try:
        data = request.json
        user_id = request.user['id']
        
        # Prepare update data
        update_data = {}
        if data.get('first_name'):
            update_data['first_name'] = data['first_name']
        if data.get('last_name'):
            update_data['last_name'] = data['last_name']
        
        if not update_data:
            return jsonify({"message": "No valid fields to update"}), 400
        
        # Make API call to Clerk to update user
        headers = {
            'Authorization': f'Bearer {CLERK_SECRET_KEY}',
            'Content-Type': 'application/json'
        }
        
        response = requests.patch(
            f'https://api.clerk.com/v1/users/{user_id}',
            headers=headers,
            json=update_data
        )
        
        if response.status_code == 200:
            return jsonify({"message": "Profile updated successfully"}), 200
        else:
            return jsonify({"message": "Failed to update profile"}), 400
            
    except Exception as e:
        print(f"Update profile error: {e}")
        return jsonify({"message": "Failed to update profile"}), 500

@app.route('/api/run-workflow', methods=['POST'])
@auth_required
def run_workflow():
    agentops.init(os.getenv("AGENTOPS_API_KEY"),default_tags=['custom integration'])
    """Run workflow with Clerk user authentication and file uploads"""
    try:
        user = request.user
        
        # Create uploads directory if it doesn't exist
        uploads_dir = os.path.join(os.getcwd(), 'uploads')
        if not os.path.exists(uploads_dir):
            os.makedirs(uploads_dir)
        
        # Create user-specific subdirectory
        user_uploads_dir = os.path.join(uploads_dir)
        if not os.path.exists(user_uploads_dir):
            os.makedirs(user_uploads_dir)
        
        # Handle file uploads
        uploaded_files = []
        if request.files:
            upload_counter = 1
            for key, file in request.files.items():
                if file and file.filename:
                    # Get original file extension
                    original_filename = file.filename
                    file_extension = os.path.splitext(original_filename)[1]  # Gets .pdf, .docx, etc.
                    
                    # Create hardcoded filename
                    hardcoded_filename = f"upload{upload_counter}{file_extension}"
                    
                    # Create full file path
                    file_path = os.path.join(user_uploads_dir, hardcoded_filename)
                    
                    # Save file locally
                    file.save(file_path)
                    
                    # Get file size
                    file_size = os.path.getsize(file_path)
                    
                    uploaded_files.append({
                        'original_filename': original_filename,
                        'stored_filename': hardcoded_filename,
                        'path': file_path,
                        'relative_path': f"uploads/{hardcoded_filename}",
                        'size': file_size
                    })
                    
                    upload_counter += 1
        
        # Get form data (non-file fields)
        form_data = {}
        for key, value in request.form.items():
            # Handle arrays (like departments_str)
            if key.endswith('[]'):
                key_name = key[:-2]  # Remove '[]' suffix
                if key_name not in form_data:
                    form_data[key_name] = []
                form_data[key_name].append(value)
            else:
                form_data[key] = value
        
        # Combine form data with file information
        data = {
            **form_data,
            'uploaded_files': uploaded_files
        }
        
        print("Received data:", data)
        print("Uploaded files:", uploaded_files)
        
        print(data)
        if not data:
            return jsonify({"error": "No data received"}), 400

        # Pass data with file information to your workflow
        main(data)
        report_name = main1(user)
        agentops.end_session("Success")
        return jsonify({
            "filename": f"{report_name}",
            "uploaded_files": uploaded_files
        }), 200
        
    
    except Exception as e:
        print(f"Workflow error: {e}")
        return jsonify({"message": f"Workflow failed: {str(e)}"}), 500




def ensure_user_bucket(user_id):
    """Ensure user-specific folders exist in Supabase storage"""
    try:
        # Create user folder structure in each bucket if it doesn't exist
        buckets = ['reports', 'chathistory', 'documents']  # Added documents bucket
        for bucket_name in buckets:
            try:
                # Try to create a placeholder file to ensure the folder exists
                placeholder_path = f"{user_id}/.placeholder"
                supabase.storage.from_(bucket_name).upload(
                    placeholder_path,
                    b"",
                    file_options={"upsert": "true"}
                )
            except Exception as e:
                # Folder might already exist, which is fine
                print(f"Folder creation for {bucket_name}/{user_id}: {e}")
                pass
    except Exception as e:
        print(f"Error ensuring user bucket: {e}")


@app.route("/api/reports/list", methods=["GET"])
@auth_required
def list_user_reports():
    """List reports for the authenticated Clerk user"""
    try:
        user = request.user
        bucket_name = "reports"
        folder = user['id']
        
        # List files in user's reports folder
        files = supabase.storage.from_(bucket_name).list(path=folder)
        if not files:
            return jsonify([]), 200

        file_urls = []
        for file in files:
            # Skip placeholder files
            if file['name'] == '.placeholder':
                continue
                
            file_path = f"{folder}/{file['name']}"

            # Generate signed URL
            signed_url_resp = supabase.storage.from_(bucket_name).create_signed_url(file_path, expires_in=3600)
            if signed_url_resp.get("signedURL"):
                file_urls.append({
                    "name": file['name'],
                    "url": signed_url_resp["signedURL"]
                })
            else:
                print(f"Error generating signed URL for {file_path}: {signed_url_resp.get('error')}")

        return jsonify(file_urls), 200

    except Exception as e:
        print(f"List reports error: {e}")
        return jsonify({"message": "Failed to list reports", "error": str(e)}), 500

@app.route('/api/ask-chatbot/<file_name>', methods=['POST'])
@auth_required
def ask_chatbot(file_name):
    """Ask chatbot questions about a specific report"""
    try:
        data = request.get_json()
        if not data or "question" not in data:
            return jsonify({"error": "Missing 'question' in JSON"}), 400

        question = data["question"]
        include_context = data.get("include_report_context", True)

        user_id = request.user['id']
        filename_without_ext = file_name.rsplit('.', 1)[0]
        history_path = f"{user_id}/{filename_without_ext}.json"

        # Load chat history
        try:
            res = supabase.storage.from_("chathistory").download(history_path)
            chat_history = json.loads(res.decode("utf-8"))
        except Exception:
            chat_history = []

        # Load report content
        report_path = f"{user_id}/{file_name}.md"
        try:
            report_res = supabase.storage.from_("reports").download(report_path)
            report_content = decode_file(report_res)
        except Exception as e:
            print(f"Report load error: {e}")
            report_content = ""

        # If include_context is requested but report is empty
        if include_context and not report_content:
            return jsonify({
                "error": "No report found for this chat.",
                "details": "Cannot answer questions without the associated workflow report."
            }), 400

        # Call chatbot model
        result = get_chatbot_response(
            user_question=question,
            chat_history=chat_history,
            include_report_context=include_context,
            report_context=report_content
        )

        if result.get("status") != "success":
            return jsonify({"error": "Chatbot failed", "details": result.get("message", "")}), 500

        # Save new Q&A pair
        chat_history.append({"role": "user", "content": question})
        chat_history.append({"role": "assistant", "content": result["response"]})

        supabase.storage.from_("chathistory").upload(
            history_path,
            json.dumps(chat_history).encode("utf-8"),
            file_options={"upsert": "true"}
        )

        return jsonify({"answer": result["response"]})

    except Exception as e:
        print(f"Chatbot error: {e}")
        return jsonify({"error": "Chatbot request failed", "details": str(e)}), 500

@app.route('/api/chat-history/<file_name>', methods=['GET'])
@auth_required
def get_chat_history(file_name):
    """Get chat history for a specific report"""
    try:
        user_id = request.user['id']
        history_path = f"{user_id}/{file_name}.json"

        try:
            response = supabase.storage.from_("chathistory").download(history_path)
            history = json.loads(response.decode("utf-8"))
        except Exception as e:
            print("Chat history is empty")
            history = []

        return jsonify(history)

    except Exception as e:
        return jsonify({"error": "Unable to retrieve chat history", "details": str(e)}), 500

@app.route("/api/report-content/<filename>", methods=["GET"])
@auth_required
def get_report_content(filename):
    """Get report content for authenticated user"""
    try:
        user_id = request.user['id']
        report_path = f"{user_id}/{filename}.md"
        file = supabase.storage.from_("reports").download(report_path)
        content = decode_file(file)
        return jsonify({"content": content})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "auth_provider": "clerk"}), 200

@app.route('/api/generate-prompt/<filename>', methods=['POST'])
@auth_required
def generate_prompt(filename):
    try:
        user_id = request.user['id']
        data = request.get_json()
        print("request data", data)

        # ✅ Step 1: Check if feedback already exists
        existing = supabase.table("feedbacks").select("*").eq("user_id", user_id).eq("filename", filename).execute()

        if existing.data:
            return jsonify({"error": "Feedback already submitted for this document."}), 400

        # ✅ Step 2: Proceed if not submitted
        report_path = f"{user_id}/{filename}.md"
        file = supabase.storage.from_("reports").download(report_path)
        content = file.decode("utf-8")

        feedback = data.get("improvement_suggestions", "")
        final_prompt = build_final_prompt(content, feedback)

        # ✅ Step 3: Store feedback metadata in Supabase
        supabase.table("feedbacks").insert({
            "user_id": user_id,
            "filename": filename,
            "feedback":feedback
        }).execute()

        return jsonify({
            "status": "success",
            "prompt": final_prompt
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/has-submitted-feedback/<filename>', methods=['GET'])
@auth_required
def has_submitted_feedback(filename):
    try:
        user_id = request.user['id']
        result = supabase.table("feedbacks") \
            .select("filename") \
            .eq("user_id", user_id) \
            .eq("filename", filename) \
            .limit(1) \
            .execute()

        return jsonify({"has_submitted": bool(result.data)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route("/api/download-report/<filename>", methods=["GET"])
@auth_required
def download_report(filename):
    try:
        user_id = request.user['id']  # from your auth system
        file_format = request.args.get("format", "markdown")

        # Validate format, only allow markdown for now
        if file_format not in ("markdown", "md"):
            return jsonify({"error": "Unsupported format"}), 400

        # Build path in Supabase Storage, e.g. user-specific folder
        file_path = f"{user_id}/{filename}.md"

        # Download file as bytes
        file_response = supabase.storage.from_("reports").download(file_path)
        if file_response is None:
            return jsonify({"error": "File not found"}), 404

        # file_response is bytes, wrap in BytesIO for send_file
        file_bytes = BytesIO(file_response)

        # Send the file as attachment to trigger download in browser
        return send_file(
            file_bytes,
            as_attachment=True,
            download_name=f"{filename}.md",
            mimetype="text/markdown"
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)