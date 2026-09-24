import { useState, useEffect } from "react";
import "./App.css";

function App() {
  const [question, setQuestion] = useState("");
  const [response, setResponse] = useState("");
  const [loading, setLoading] = useState(false);
  const [recentHistory, setRecentHistory] = useState([]);
  
  // NEW: State to track which page we are on
  const [activeTab, setActiveTab] = useState("dashboard");

  const fetchHistory = async () => {
    try {
      const res = await fetch("http://127.0.0.1:8000/api/history");
      const data = await res.json();
      if (data.status === "success" && data.data) {
        setRecentHistory(data.data);
      }
    } catch (error) {
      console.error("Failed to fetch history:", error);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, []);

  const askAI = async () => {
    if (!question.trim()) return;

    setLoading(true);
    setResponse("");

    try {
      const res = await fetch("http://127.0.0.1:8000/api/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message: question,
        }),
      });

      const data = await res.json();
      setResponse(data.response);
      fetchHistory();
    } catch (error) {
      setResponse("Unable to connect to the AI server.");
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <aside className="sidebar">
        <div className="logo">
          <div className="logo-icon">AI</div>
          <div>
            <h2>StudyAI</h2>
            <p>Learning Assistant</p>
          </div>
        </div>

        <nav>
          {/* NEW: Clickable sidebar buttons with dynamic active classes */}
          <button 
            className={`nav-item ${activeTab === "dashboard" ? "active" : ""}`}
            onClick={() => setActiveTab("dashboard")}
          >🏠 Dashboard</button>
          
          <button 
            className={`nav-item ${activeTab === "materials" ? "active" : ""}`}
            onClick={() => setActiveTab("materials")}
          >📚 Study Materials</button>
          
          <button 
            className={`nav-item ${activeTab === "quiz" ? "active" : ""}`}
            onClick={() => setActiveTab("quiz")}
          >📝 Quiz</button>
          
          <button 
            className={`nav-item ${activeTab === "plan" ? "active" : ""}`}
            onClick={() => setActiveTab("plan")}
          >📅 Study Plan</button>
          
          <button 
            className={`nav-item ${activeTab === "progress" ? "active" : ""}`}
            onClick={() => setActiveTab("progress")}
          >📊 Progress</button>
          
          <button 
            className={`nav-item ${activeTab === "history" ? "active" : ""}`}
            onClick={() => setActiveTab("history")}
          >🕘 History</button>
        </nav>

        <div className="sidebar-bottom">
          <p>Powered by</p>
          <strong>Qwen2.5 + LangGraph + MCP</strong>
        </div>
      </aside>

      <main className="main-content">
        <header className="topbar">
          <div>
            <p className="greeting">Good morning 👋</p>
            <h1>Ready to learn?</h1>
          </div>

          <div className="profile">
            <div className="avatar">S</div>
            <span>Student</span>
          </div>
        </header>

        {/* --- VIEW ROUTING STARTS HERE --- */}

        {activeTab === "dashboard" && (
          <>
            <section className="hero">
              <div>
                <span className="badge">AI STUDY ASSISTANT</span>
                <h2>What do you want to learn today?</h2>
                <p>
                  Ask questions, generate quizzes, create study plans,
                  and track your learning progress.
                </p>
              </div>
            </section>

            <section className="ask-card">
              <div className="ask-icon">✨</div>
              <div className="ask-content">
                <h3>Ask your AI tutor</h3>
                <div className="input-row">
                  <input
                    type="text"
                    placeholder="Ask anything about your studies..."
                    value={question}
                    onChange={(e) => setQuestion(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === "Enter") askAI();
                    }}
                  />
                  <button onClick={askAI} disabled={loading}>
                    {loading ? "Thinking..." : "Ask AI →"}
                  </button>
                </div>
                {response && (
                  <div className="ai-response">
                    <strong>AI Tutor</strong>
                    <p>{response}</p>
                  </div>
                )}
              </div>
            </section>

            <section className="section">
              <div className="section-header">
                <h2>Quick Actions</h2>
                <span>Start learning</span>
              </div>
              <div className="quick-actions">
                <div className="action-card" onClick={() => document.querySelector('input').focus()}>
                  <div className="action-icon">💡</div>
                  <h3>Ask a Question</h3>
                  <p>Get simple explanations for difficult topics.</p>
                </div>
                <div className="action-card" onClick={() => setActiveTab("quiz")}>
                  <div className="action-icon">📝</div>
                  <h3>Generate Quiz</h3>
                  <p>Test your knowledge with an AI-generated quiz.</p>
                </div>
                <div className="action-card" onClick={() => setActiveTab("plan")}>
                  <div className="action-icon">📅</div>
                  <h3>Create Study Plan</h3>
                  <p>Build a study plan based on your available time.</p>
                </div>
              </div>
            </section>

            <section className="section">
              <div className="section-header">
                <h2>Recent Activity</h2>
                <span style={{cursor: "pointer", color: "#2563eb"}} onClick={() => setActiveTab("history")}>
                  View all
                </span>
              </div>
              <div className="activity-card">
                {recentHistory.length > 0 ? (
                  recentHistory.slice(0, 5).map((item, index) => (
                    <div className="activity-item" key={index}>
                      <span>🧠</span>
                      <div>
                        <strong>
                          {item.query 
                            ? (item.query.length > 40 ? item.query.substring(0, 40) + "..." : item.query) 
                            : "AI Chat"}
                        </strong>
                        <p>Study Session</p>
                      </div>
                      <small>
                        {item.timestamp 
                          ? new Date(item.timestamp).toLocaleDateString() 
                          : "Recently"}
                      </small>
                    </div>
                  ))
                ) : (
                  <p style={{ padding: "1rem", color: "#666" }}>
                    No recent activity yet. Ask a question to get started!
                  </p>
                )}
              </div>
            </section>
          </>
        )}

        {/* PLACEHOLDER VIEWS */}
        {activeTab === "materials" && (
          <section className="section">
            <h2>📚 Study Materials</h2>
            <p>Your uploaded PDFs and study content will appear here.</p>
          </section>
        )}

        {activeTab === "quiz" && (
          <section className="section">
            <h2>📝 AI Quiz Generator</h2>
            <p>Feature coming soon! You will be able to generate quizzes based on your topics.</p>
          </section>
        )}

        {activeTab === "plan" && (
          <section className="section">
            <h2>📅 Study Planner</h2>
            <p>Feature coming soon! Generate structured study schedules.</p>
          </section>
        )}

        {activeTab === "progress" && (
          <section className="section">
            <h2>📊 Your Progress</h2>
            <p>Feature coming soon! View your quiz scores and completion stats.</p>
          </section>
        )}

        {activeTab === "history" && (
          <section className="section">
            <h2>🕘 Full Study History</h2>
            <p>Feature coming soon! A detailed list of all your past conversations and study plans.</p>
          </section>
        )}

      </main>
    </div>
  );
}

export default App;