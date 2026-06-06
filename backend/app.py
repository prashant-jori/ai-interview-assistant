from PyPDF2 import PdfReader
from flask import Flask, request, jsonify
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import google.generativeai as genai
import os
import speech_recognition as sr
import re

# ---------------- LOAD ENV ----------------

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

print("API Key Loaded:", GEMINI_API_KEY)

# ---------------- GEMINI CONFIG ----------------

genai.configure(api_key=GEMINI_API_KEY)
# Models list
model = genai.GenerativeModel("gemini-1.5-flash")


# ---------------- FLASK ----------------

app = Flask(__name__)

CORS(app, origins=["http://localhost:5173", "http://127.0.0.1:5173"])

bcrypt = Bcrypt(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///interview.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    email = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )

    password = db.Column(
        db.String(200),
        nullable=False
    )
class InterviewQuestion(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    question = db.Column(
        db.Text,
        nullable=False
    )

class InterviewResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100))
    question = db.Column(db.Text)
    answer = db.Column(db.Text)
    result = db.Column(db.Text)
    score = db.Column(db.Integer)
# ---------------- HOME ----------------
def extract_score(text):
    match = re.search(r"Score:\s*(\d+)/10", text)
    if match:
        return int(match.group(1))
    return None
@app.route('/')
def home():
    return jsonify({
        "message": "Backend is running successfully"
    })

# ---------------- REGISTER ----------------

@app.route('/register', methods=['POST'])
def register():

    data = request.get_json()

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({
            "message": "Email and Password required"
        }), 400

    existing_user = User.query.filter_by(
        email=email
    ).first()

    if existing_user:
        return jsonify({
            "message": "User already exists"
        }), 400

    hashed_password = bcrypt.generate_password_hash(
        password
    ).decode("utf-8")

    new_user = User(
        email=email,
        password=hashed_password
    )

    db.session.add(new_user)
    db.session.commit()

    return jsonify({
        "message": "User Registered Successfully"
    })

# ---------------- LOGIN ----------------

@app.route('/login', methods=['POST'])
def login():

    data = request.get_json()

    email = data.get("email")
    password = data.get("password")

    print("EMAIL:", email)

    user = User.query.filter_by(email=email).first()

    print("USER:", user)

    if not user:
        return jsonify({
            "message": "User not found"
        }), 404

    print("DB PASSWORD:", user.password)

    if bcrypt.check_password_hash(user.password, password):
        print("LOGIN SUCCESS")
        return jsonify({
            "message": "Login Successful"
        })

    print("WRONG PASSWORD")

    return jsonify({
        "message": "Wrong Password"
    }), 401
# ---------------- DASHBOARD ----------------

@app.route('/dashboard')
def dashboard():

    return jsonify({
        "message": "Welcome to AI Interview Dashboard"
    })
# ---------------- Upload PDF Route ----------------
@app.route('/upload-pdf', methods=['POST'])
def upload_pdf():

    global uploaded_pdf_path

    if 'pdf' not in request.files:
        return jsonify({
            "message": "No PDF file part in request"
        }), 400

    pdf = request.files['pdf']
    if pdf.filename == "":
        return jsonify({
            "message": "No PDF file selected"
        }), 400

    uploads_dir = os.path.join(os.path.dirname(__file__), "uploads")
    os.makedirs(uploads_dir, exist_ok=True)

    filename = secure_filename(pdf.filename)
    save_path = os.path.join(uploads_dir, filename)

    try:
        pdf.save(save_path)
    except OSError as e:
        app.logger.error("PDF upload failed: %s", e)
        return jsonify({
            "message": "Unable to save PDF. Check disk space and folder permissions."
        }), 507
    except Exception as e:
        app.logger.error("PDF upload failed: %s", e)
        return jsonify({
            "message": "Unable to save PDF."
        }), 500

    uploaded_pdf_path = save_path

    return jsonify({
        "message": "PDF Uploaded Successfully",
        "path": save_path
    })

# ---------------- Read PDF Route ----------------
@app.route('/read-pdf')
def read_pdf():

    try:

        global uploaded_pdf_path

        reader = PdfReader(uploaded_pdf_path)

        text = ""

        for page in reader.pages:
            page_text = page.extract_text()

            if page_text:
                text += page_text

        return jsonify({
            "pdf_text": text
        })

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500
# ---------------- GENERATE QUESTIONS ----------------

@app.route('/generate-questions', methods=['POST'])
def generate_questions():

    try:
        global uploaded_pdf_path

        if not uploaded_pdf_path:
            return jsonify({"error": "No PDF uploaded"}), 400

        reader = PdfReader(uploaded_pdf_path)

        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""

        model = genai.GenerativeModel("gemini-2.5-flash")

        prompt = f"""
        Generate 5 interview questions:

        {text}
        """

        response = model.generate_content(prompt)

        return jsonify({
            "questions": response.text
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500




# ---------------- EVALUATE ANSWER ----------------

@app.route('/evaluate-answer', methods=['POST'])
def evaluate_answer():

    data = request.get_json()

    answer = data.get("answer", "")

    return jsonify({
        "answer": answer,
        "score": 8,
        "feedback": "Good attempt. Add more technical details."
    })

# ---------------- GEMINI TEST ----------------

@app.route('/ai-test')
def ai_test():

    try:

        model = genai.GenerativeModel(
            "gemini-2.5-flash"
        )

        response = model.generate_content(
            "Tell me about Python in 3 lines."
        )

        return jsonify({
            "response": response.text
        })

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500


# ---------------- Voice Text Route ----------------
@app.route('/voice-to-text', methods=['POST'])
def voice_to_text():

    recognizer = sr.Recognizer()

    audio_file = request.files['audio']
    path = "uploads/audio.wav"
    audio_file.save(path)

    with sr.AudioFile(path) as source:
        audio = recognizer.record(source)

    try:
        text = recognizer.recognize_google(audio)

        return jsonify({
            "text": text
        })

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500
    
# ---------------- evaluate-voice-answer----------------
@app.route('/evaluate-voice-answer', methods=['POST'])
def evaluate_voice_answer():

    data = request.get_json()

    answer = data.get("text") or data.get("answer")
    email = data.get("email")
    question = data.get("question")

    if not answer:
        return jsonify({"error": "No text provided"}), 400

    model = genai.GenerativeModel("gemini-2.5-flash")

    prompt = f"""
    You are an AI interviewer.

    Evaluate this interview answer:

    {answer}

    Return ONLY in this format:

    Score: X/10

    Strengths:
    - Point 1
    - Point 2

    Improvements:
    - Point 1
    - Point 2

    Feedback:
    Short feedback here.
    """

    try:
        response = model.generate_content(prompt)
        result_text = getattr(response, "text", str(response))
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    result_text = getattr(response, "text", str(response))
    score = extract_score(result_text)

    new_result = InterviewResult(
    email=email,
    question=question,
    answer=answer,
    result=result_text,
    score=score
    )
    try:
        db.session.add(new_result)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "DB error", "details": str(e)}), 500

    return jsonify({
        "result": result_text
    })

def extract_score(text):
    match = re.search(r"Score:\s*(\d+)/10", text)
    if match:
        return int(match.group(1))
    return None
@app.route('/questions-history')
def questions_history():

    questions = InterviewQuestion.query.order_by(InterviewQuestion.id.desc()).all()

    data = []

    for q in questions:
        data.append({
            "id": q.id,
            "question": q.question
        })

    return jsonify(data)

    

@app.route('/results-history')
def results_history():

    try:
        results = InterviewResult.query.all()

        data = []

        for r in results:
            data.append({
                "id": r.id,
                "email": r.email if r.email else "",
                "answer": r.answer if r.answer else "",
                "result": r.result if r.result else "",
                "score": r.score if r.score is not None else 0
            })

        return jsonify(data)

    except Exception as e:
        print("ERROR:", str(e))
        return jsonify({"error": str(e)}), 500


@app.route('/analytics/<email>')
def analytics(email):

    results = InterviewResult.query.filter_by(email=email).all()

    scores = []

    for r in results:
        match = re.search(r"Score:\s*(\d+)/10", r.result)
        if match:
            scores.append(int(match.group(1)))

    if not scores:
        return jsonify({"avg_score": 0})

    return jsonify({
        "total_tests": len(scores),
        "average_score": round(sum(scores)/len(scores), 2),
        "best_score": max(scores),
        "worst_score": min(scores)
    })


@app.route('/create-test-user')
def create_test_user():

    hashed = bcrypt.generate_password_hash(
        "123456"
    ).decode("utf-8")

    user = User(
        email="test@test.com",
        password=hashed
    )

    db.session.add(user)
    db.session.commit()

    return "User Created"
@app.route('/all-users')
def all_users():

    users = User.query.all()

    data = []

    for u in users:
        data.append({
            "id": u.id,
            "email": u.email
        })

    return jsonify(data)

@app.route('/upload-resume', methods=['POST'])
def upload_resume():

    resume = request.files.get("resume")

    if not resume:
        return jsonify({"error": "No Resume"}), 400

    os.makedirs("resumes", exist_ok=True)

    path = f"resumes/{resume.filename}"

    resume.save(path)

    return jsonify({
        "message": "Resume Uploaded",
        "path": path
    })
@app.route('/analyze-resume', methods=['POST'])
def analyze_resume():

    try:

        resume = request.files.get("resume")

        if not resume:
            return jsonify({"error": "No Resume"}), 400

        text = ""

        reader = PdfReader(resume)

        for page in reader.pages:
            page_text = page.extract_text()

            if page_text:
                text += page_text

        model = genai.GenerativeModel(
            "gemini-2.5-flash"
        )

        prompt = f"""
        Analyze this resume.

        Give:

        Skills
        Strengths
        Weaknesses
        Improvement Suggestions

        {text}
        """

        response = model.generate_content(prompt)

        return jsonify({
            "analysis": response.text
        })

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500
# ---------------- RUN ----------------
with app.app_context():
    db.create_all()

print(app.url_map)

if __name__ == '__main__':
    app.run(
        debug=True,
        host='0.0.0.0',
        port=5000,
        use_reloader=False
    )