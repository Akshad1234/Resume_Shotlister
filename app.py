import os
import traceback
from flask import Flask, render_template, request, jsonify
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from model import extract_and_highlight_keywords, extract_text

# Initialize Flask App
app = Flask(__name__, static_folder='static')

# Enable CORS (Allows frontend JavaScript to communicate with Flask)
CORS(app)

# Secret Key Configuration
app.config['SECRET_KEY'] = 'supersecretkey'

# Initialize Extensions
bcrypt = Bcrypt(app)

# Folder to store uploaded resumes
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'png', 'jpg', 'jpeg'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Fixed User Credentials
FIXED_USERNAME = "admin"
FIXED_PASSWORD_HASH = bcrypt.generate_password_hash("password123").decode("utf-8")

# ---------------- ROUTES ---------------- #

@app.route('/')
def home():
    return render_template('Home.html')

@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template('Login.html')

    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if username == FIXED_USERNAME and bcrypt.check_password_hash(FIXED_PASSWORD_HASH, password):
        return jsonify({"message": "Login successful"}), 200
    else:
        return jsonify({"message": "Invalid credentials"}), 401

@app.route('/selection')
def selection():
    return render_template('Selection.html')

@app.route('/construction')
def construction():
    return render_template('ConstructionPage.html')

# -------------- FILE UPLOAD ---------------- #
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({"status": "Failed", "message": "No file part"}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({"status": "Failed", "message": "No selected file"}), 400

        if not allowed_file(file.filename):
            return jsonify({"status": "Failed", "message": "Invalid file format. Allowed: PDF, DOCX, PNG, JPG, JPEG"}), 400

        # Save file
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)

        # Call resume analysis function
        try:
            file_ext = file.filename.split(".")[-1].lower()
            text = extract_text(file_path, file_ext)
            status, matched_keywords, feedback, ats_friendly, suggested_companies = extract_and_highlight_keywords(text)

            return jsonify({
                'status': status,
                'matched_keywords': matched_keywords,
                'feedback': feedback,
                'ATS Compliance': ats_friendly,
                'Suggested Companies': suggested_companies
            }), 200
        except Exception as e:
            print("Error processing file:", str(e))
            traceback.print_exc()  # Print full error details
            return jsonify({'status': 'Failed', 'message': f'Error processing file: {str(e)}'}), 500

    except Exception as e:
        print("Unexpected Error:", str(e))
        traceback.print_exc()  # Print full error details
        return jsonify({"status": "Failed", "message": f"Server error: {str(e)}"}), 500

# -------------- RUN FLASK APP ---------------- #
if __name__ == '__main__':
    app.run(debug=True)
