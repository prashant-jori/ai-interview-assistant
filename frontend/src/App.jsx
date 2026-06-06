import { useState } from "react";
import axios from "axios";
import Analytics from "./Analytics";
import './App.css'
import { BACKEND_URL } from "./config";

function App() {

  // ---------------- STATES (सर्व सुरक्षित आहेत) ----------------
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loggedIn, setLoggedIn] = useState(false);

  const [activeTab, setActiveTab] = useState("home");

  const [file, setFile] = useState(null);
  const [uploadMsg, setUploadMsg] = useState("");

  const [questions, setQuestions] = useState("");
  const [loading, setLoading] = useState(false);

  const [question, setQuestion] = useState("");
  const [voiceText, setVoiceText] = useState("");
  const [voiceResult, setVoiceResult] = useState("");
  const [voiceAnswer, setVoiceAnswer] = useState("");
  
  const [results, setResults] = useState([]);
  const [pdfText, setPdfText] = useState("");
  

  // ---------------- FUNCTIONS (सर्व सुरक्षित आहेत) ----------------
  const handleLogin = async () => {
  try {
    const res = await axios.post(
      `${BACKEND_URL}/login`,
      {
        email,
        password
      }
    );

    alert(res.data.message || "Login Success 🚀");
    setLoggedIn(true);

  } catch (err) {
    console.log(err);
    alert(err.response?.data?.message || "Login Failed ❌");
  }
};

  const uploadPDF = async () => {
    if (!file) {
      alert("Select PDF first");
      return;
    }
    const formData = new FormData();
    formData.append("pdf", file);

    try {
      await axios.post(`${BACKEND_URL}/upload-pdf`, formData, {
        headers: { "Content-Type": "multipart/form-data" }
      });
      setUploadMsg("PDF Uploaded Successfully 🚀");
    } catch (err) {
      console.log(err);
      setUploadMsg("Upload Failed ❌");
    }
  };

  const readPDF = async () => {
    try {
      const res = await axios.get(`${BACKEND_URL}/read-pdf`);
      setPdfText(res.data.pdf_text);
    } catch (err) {
      console.log(err);
    }
  };

  const generateQuestions = async () => {
    setLoading(true);
    try {
      const res = await axios.post(`${BACKEND_URL}/generate-questions`, {}, {
        headers: { "Content-Type": "application/json" }
      });
      setQuestions(res.data.questions);
    } catch (err) {
      console.log(err);
      setQuestions("Error generating questions");
    }
    setLoading(false);
  };

  const evaluateVoiceAnswer = async () => {
    try {
      const res = await axios.post(`${BACKEND_URL}/evaluate-voice-answer`, {
        email,
        question,
        answer: voiceAnswer || voiceText,
      });
      setVoiceResult(res.data.result);
    } catch (err) {
      console.log(err);
      alert("Evaluation Failed");
    }
  };
  

  // ---------------- CLEAR VOICE INTERVIEW CONTENT ----------------
  const clearVoiceFields = () => {
    setQuestion("");
    setVoiceText("");
    setVoiceAnswer("");
    setVoiceResult("");
  };

  const getResultsHistory = async () => {
    try {
      const res = await axios.get(`${BACKEND_URL}/results-history`);
      setResults(res.data);
    } catch (err) {
      console.log(err);
    }
  };

  // ---------------- CLEAR RESULTS HISTORY ----------------
  const clearResultsHistory = async () => {
    if (window.confirm("Are you sure you want to clear all history? 📋")) {
      try {
        // तुमच्या Flask बॅकएंडला delete रिक्वेस्ट पाठवण्यासाठी
        await axios.delete(`${BACKEND_URL}/clear-history`); 
        setResults([]); // फ्रंटएंड स्टेट रिकामी करा
        alert("History Cleared Successfully! 🧹");
      } catch (err) {
        console.log(err);
        // जर बॅकएंडला डिलीट राऊट नसेल, तर तात्पुरती फ्रंटएंड स्टेट क्लिअर करण्यासाठी:
        setResults([]);
        alert("Frontend History Cleared! (Make sure to add DELETE route in Flask if needed)");
      }
    }
  };

  const startListening = () => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const recognition = new SpeechRecognition();
    recognition.start();
    recognition.onresult = (event) => {
      setVoiceText(event.results[0][0].transcript);
    };
  };

  // ---------------- LOGIN PAGE (मॉर्डन सेंटर लुक) ----------------
  if (!loggedIn) {
    return (
      <div className="login-wrapper">
        <div className="card login-card shadow-lg">
          <h3 className="text-center mb-4" style={{ color: '#1e293b', fontWeight: '700' }}>
            AI Interview Assistant 🚀
          </h3>
          <input
            className="form-control"
            placeholder="Email Address"
            type="email"
            onChange={(e) => setEmail(e.target.value)}
          />
          <input
            className="form-control"
            type="password"
            placeholder="Password"
            onChange={(e) => setPassword(e.target.value)}
          />
          <button className="btn btn-primary w-100 mt-2" onClick={handleLogin}>
            Sign In
          </button>
        </div>
      </div>
    );
  }

  // ---------------- DASHBOARD ----------------
  return (
    <div className="container mt-4">
      <div className="card p-4 shadow">
        <h2 className="dashboard-title">AI Interview Dashboard 🚀</h2>

        {/* NAV BUTTONS */}
        <div className="nav-buttons mb-3">
          <button className="btn btn-primary m-1" onClick={() => setActiveTab("upload")}>Upload PDF</button>
          <button className="btn btn-success m-1" onClick={() => setActiveTab("questions")}>Generate Questions</button>
          <button className="btn btn-warning m-1" onClick={() => setActiveTab("voice")}>Voice Interview</button>
          <button className="btn btn-secondary m-1" onClick={() => { setActiveTab("history"); getResultsHistory(); }}>Results History</button>
          <button className="btn btn-dark m-1" onClick={() => setActiveTab("profile")}>Profile</button>
          <button className="btn btn-info m-1" onClick={() => setActiveTab("analytics")}>Analytics</button>
          <button className="btn btn-danger m-1" onClick={() => setLoggedIn(false)}>Logout</button>
        </div>

        <hr />

        {/* HOME */}
        {activeTab === "home" && (
          <h5 className="text-center">Welcome to AI Interview System 🚀</h5>
        )}

        {/* UPLOAD PDF (नवीन मॉर्डन टच दिलेला भाग) */}
        {activeTab === "upload" && (
          <div>
            <h4 className="mb-4" style={{ color: '#1e293b', fontWeight: '700' }}>📄 Upload & Analyze Resume</h4>
            
            <div className="pdf-upload-section">
              <p className="text-muted mb-3">Select your PDF interview schedule or resume to get started</p>
              <input
                type="file"
                accept="application/pdf"
                className="form-control mx-auto"
                style={{ maxWidth: '400px' }}
                onChange={(e) => setFile(e.target.files[0])}
              />
              <div className="mt-3">
                <button className="btn btn-primary me-2 shadow-sm" onClick={uploadPDF}>🚀 Upload PDF</button>
                <button className="btn btn-outline-success shadow-sm" onClick={readPDF}>🔍 Show PDF Text</button>
              </div>
            </div>

            {uploadMsg && (
              <div className={`alert ${uploadMsg.includes('Success') ? 'alert-success' : 'alert-danger'} border-0 rounded-3 shadow-sm`}>
                {uploadMsg}
              </div>
            )}

            {pdfText && (
              <div className="mt-4">
                <div className="d-flex justify-content-between align-items-center mb-2">
                  <h5 className="m-0" style={{ color: '#0f172a', fontWeight: '600' }}>Extracted PDF Content</h5>
                  <span className="badge bg-light text-dark border px-2 py-2 rounded-3">
                    {pdfText.split(' ').length} words
                  </span>
                </div>
                <div className="pdf-text-container">
                  <p className="pdf-text-content">{pdfText}</p>
                </div>
              </div>
            )}
          </div>
        )}

        {/* QUESTIONS */}
        {activeTab === "questions" && (
          <div>
            <h4>Generate Questions 🤖</h4>
            <button className="btn btn-success mb-2" onClick={generateQuestions}>Generate</button>
            {loading && <p>Loading...</p>}
            <pre style={{ whiteSpace: "pre-wrap" }}>{questions}</pre>
          </div>
        )}
{/* VOICE */}
        {activeTab === "voice" && (
          <div>
            <h4 className="mb-4" style={{ color: '#1e293b', fontWeight: '700' }}>🎤 Voice Interview Practice</h4>

            {/* प्रश्न इनपुट आणि डिस्प्ले एरिया */}
            <div className="voice-question-box shadow-sm">
              <label className="form-label font-weight-bold" style={{ color: '#475569', fontSize: '0.9rem' }}>
                Current Interview Question:
              </label>
              <input
                className="form-control"
                placeholder="Enter or paste your interview question here..."
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
              />
            </div>

            {/* बोलण्यासाठीचे बटण */}
            <div className="text-center mb-3">
              <button className="btn btn-speak px-4 py-2" onClick={startListening}>
                🎤 Click & Start Speaking Answer
              </button>
            </div>

            {/* युझरचे उत्तर दाखवणारा मॉडर्न बॉक्स */}
            <div className="mb-3">
              <div className="d-flex justify-content-between mb-1">
                <label className="form-label m-0 font-weight-bold" style={{ color: '#475569', fontSize: '0.9rem' }}>
                  Your Speech Transcribed / Answer:
                </label>
                <span className="text-muted small">You can also type below if mic is off</span>
              </div>
              
              <textarea
                className="form-control voice-answer-container"
                rows="4"
                placeholder="Your spoken words will appear here automatically, or you can type your answer manually..."
                value={voiceAnswer || voiceText}
                onChange={(e) => setVoiceAnswer(e.target.value)}
                style={{ resize: 'none' }}
              />
            </div>

            {/* ॲक्शन बटन्स (Evaluate, Clear, Profile) */}
            <div className="d-flex gap-2 flex-wrap mb-4">
              <button className="btn btn-success flex-grow-1 shadow-sm" onClick={evaluateVoiceAnswer}>
                🔍 Evaluate Answer with AI
              </button>
              <button className="btn btn-outline-danger shadow-sm" onClick={clearVoiceFields}>
                🗑️ Clear Content
              </button>
              <button className="btn btn-dark shadow-sm" onClick={() => setActiveTab("profile")}>
                👤 Profile
              </button>
            </div>

            {/* AI फीडबॅकचा सुंदर बॉक्स */}
            {voiceResult && (
              <div className="mt-4">
                <h5 className="font-weight-bold mb-2" style={{ color: '#0f172a' }}>✨ AI Analysis & Feedback</h5>
                <div className="ai-feedback-container shadow-sm">
                  <p className="ai-feedback-content">{voiceResult}</p>
                </div>
              </div>
            )}
          </div>
        )}



        {/* HISTORY */}
        {activeTab === "history" && (
          <div>
            <div className="d-flex justify-content-between align-items-center mb-4">
              <h3 className="m-0" style={{ fontWeight: '700', color: '#1e293b' }}>Results History 📋</h3>
              {results.length > 0 && (
                <button className="btn btn-danger btn-sm shadow-sm px-3" onClick={clearResultsHistory}>
                  🧹 Clear All History
                </button>
              )}
            </div>

            {results.length === 0 ? (
              <div className="text-center py-5 text-muted">
                <h5>No interview records found. 🚫</h5>
                <p>Complete a voice interview to see your scores here.</p>
              </div>
            ) : (
              <div className="table-responsive rounded-3 shadow-sm border">
                <table className="table table-hover m-0">
                  <thead className="table-light">
                    <tr>
                      <th className="py-3 px-4">ID</th>
                      <th className="py-3 px-4">Email</th>
                      <th className="py-3 px-4 text-end">Score</th>
                    </tr>
                  </thead>
                  <tbody>
                    {results.map((item) => (
                      <tr key={item.id}>
                        <td className="py-3 px-4 fw-bold text-secondary">#{item.id}</td>
                        <td className="py-3 px-4">{item.email}</td>
                        <td className="py-3 px-4 text-end fw-bold text-success">{item.score}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}

        {/* PROFILE */}
        {activeTab === "profile" && (
          <div>
            <div className="profile-card">
              <h2>Prashant Jori 👨‍💻</h2>
              <p>AI Engineer | Data Science | Machine Learning</p>
              <hr />
              <p>Building AI Interview Assistant using React + Flask + Gemini AI</p>
              <a href="https://github.com/prashant-jori" target="_blank" rel="noreferrer">GitHub Profile</a>
              <br /><br />
              <a href="https://www.linkedin.com/in/prashant-jori-350a55269/" target="_blank" rel="noreferrer">LinkedIn Profile</a>
              <a href="/resume.pdf" target="_blank" className="btn btn-success m-1">Download Resume</a>
            </div>
            <div className="card p-3 shadow">
              <h5>Skills 🚀</h5>
              <ul>
                <li>Python</li><li>Machine Learning</li><li>Deep Learning</li><li>Generative AI</li><li>Data Science</li><li>SQL</li><li>Flask</li><li>React JS</li>
              </ul>
            </div>
            <div className="card p-3">
              <h5>LinkedIn</h5>
              <a href="https://www.linkedin.com/in/prashant-jori-350a55269/" target="_blank">Open LinkedIn Profile</a>
            </div>
          </div>
        )}

        {/* ANALYTICS */}
        {activeTab === "analytics" && (
          <div><Analytics /></div>
        )}

      </div>
    </div>
  );
}

export default App;