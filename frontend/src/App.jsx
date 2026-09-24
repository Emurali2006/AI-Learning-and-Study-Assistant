import { useState, useEffect } from "react";
import "./App.css";

function App() {
  const [question, setQuestion] = useState("");
  const [response, setResponse] = useState("");
  const [loading, setLoading] = useState(false);
  const [recentHistory, setRecentHistory] = useState([]);
  
  const [activeTab, setActiveTab] = useState("dashboard");

  const [quizTopic, setQuizTopic] = useState("");
  const [quizResponse, setQuizResponse] = useState("");
  const [isQuizLoading, setIsQuizLoading] = useState(false);

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
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: question }),
      });

      if (!res.ok) throw new Error(`Server returned status: ${res.status}`);

      const data = await res.json();
      setResponse(data.response);
      fetchHistory();
    } catch (error) {
      setResponse(`Diagnostic Error: ${error.message}`);
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateQuiz = async () => {
    if (!quizTopic.trim()) return;

    setIsQuizLoading(true);
    setQuizResponse("");

    try {
      const res = await fetch("http://127.0.0.1:8000/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: `Generate a multiple choice quiz about: ${quizTopic}.` }),
      });

      if (!res.ok) throw new Error(`Server returned status: ${res.status}`);

      const data = await res.json();
      setQuizResponse(data.response);
      fetchHistory();
    } catch (error) {
      setQuizResponse(`Error: ${error.message}`);
      console.error(error);
    } finally {
      setIsQuizLoading(false);
    }
  };

  // NEW: Helper function to beautifully render the raw __QUIZ__ JSON data
  const renderQuizContent = (text) => {
    if (text.includes("__QUIZ__")) {
      try {
        const jsonString = text.split("__QUIZ__")[1].trim();
        const quizData = JSON.parse(jsonString);

        return (
          <div style={{ textAlign: "left", marginTop: "1rem" }}>
            <h4 style={{ color: "#2563eb", marginBottom: "1rem" }}>Subject: {quizData.subject}</h4>
            {quizData.quiz.map((q, index) => (
              <div key={index} style={{ marginBottom: "1.5rem", padding: "1.5rem", backgroundColor: "#f8f9fa", borderRadius: "8px", border: "1px solid #e5e7eb" }}>
                <p style={{ fontWeight: "bold", marginBottom: "1rem", fontSize: "1.1rem" }}>
                  {index + 1}. {q.question}
                </p>
                <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem", paddingLeft: "1rem" }}>
                  {Object.entries(q.options).map(([letter, answer]) => (
                    <div key={letter} style={{ padding: "0.5rem", backgroundColor: "white", borderRadius: "4px", border: "1px solid #e5e7eb" }}>
                      <strong>{letter}:</strong> {answer}
                    </div>
                  ))}
                </div>
                <details style={{ marginTop: "1rem", cursor: "pointer", backgroundColor: "#e0f2fe", padding: "0.5rem", borderRadius: "4px" }}>
                  <summary style={{ fontWeight: "bold", color: "#0369a1" }}>Show Answer</summary>
                  <div style={{ marginTop: "0.5rem" }}>
                    <p style={{ color: "#16a34a", fontWeight: "bold" }}>Correct Answer: {q.correct}</p>
                    <p style={{ fontSize: "0.9rem", marginTop: "0.25rem", color: "#4b5563" }}>{q.explanation}</p>
                  </div>
                </details>
              </div>
            ))}
          </div>
        );
      } catch (e) {
        // Fallback if JSON parsing fails
        return <pre style={{ whiteSpace: "pre-wrap", fontFamily: "inherit" }}>{text}</pre>;
      }
    }
    // Fallback for normal text responses
    return <pre style={{ whiteSpace: "pre-wrap", fontFamily: "inherit" }}>{text}</pre>;
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
          <button className={`nav-item ${activeTab === "dashboard" ? "active" : ""}`} onClick={() => setActiveTab("dashboard")}>🏠 Dashboard</button>
          <button className={`nav-item ${activeTab === "materials" ? "active" : ""}`} onClick={() => setActiveTab("materials")}>📚 Study Materials</button>
          <button className={`nav-item ${activeTab === "quiz" ? "active" : ""}`} onClick={() => setActiveTab("quiz")}>📝 Quiz</button>
          <button className={`nav-item ${activeTab === "plan" ? "active" : ""}`} onClick={() => setActiveTab("plan")}>📅 Study Plan</button>
          <button className={`nav-item ${activeTab === "progress" ? "active" : ""}`} onClick={() => setActiveTab("progress")}>📊 Progress</button>
          <button className={`nav-item ${activeTab === "history" ? "active" : ""}`} onClick={() => setActiveTab("history")}>🕘 History</button>
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

        {activeTab === "dashboard" && (
          <>
            <section className="hero">
              <div>
                <span className="badge">AI STUDY ASSISTANT</span>
                <h2>What do you want to learn today?</h2>
                <p>Ask questions, generate quizzes, create study plans, and track your learning progress.</p>
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
                    onKeyDown={(e) => { if (e.key === "Enter") askAI(); }}
                  />
                  <button onClick={askAI} disabled={loading}>{loading ? "Thinking..." : "Ask AI →"}</button>
                </div>
                {response && (
                  <div className="ai-response">
                    <strong>AI Tutor</strong>
                    <pre style={{ whiteSpace: "pre-wrap", fontFamily: "inherit", marginTop: "10px" }}>{response}</pre>
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
                <div className="action-card" onClick={() => { setActiveTab("dashboard"); document.querySelector('input').focus(); }}>
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
                <span style={{cursor: "pointer", color: "#2563eb"}} onClick={() => setActiveTab("history")}>View all</span>
              </div>
              <div className="activity-card">
                {recentHistory.length > 0 ? (
                  recentHistory.slice(0, 5).map((item, index) => (
                    <div className="activity-item" key={index}>
                      <span>🧠</span>
                      <div>
                        <strong>{item.query ? (item.query.length > 40 ? item.query.substring(0, 40) + "..." : item.query) : "AI Chat"}</strong>
                        <p>Study Session</p>
                      </div>
                      <small>{item.timestamp ? new Date(item.timestamp).toLocaleDateString() : "Recently"}</small>
                    </div>
                  ))
                ) : (
                  <p style={{ padding: "1rem", color: "#666" }}>No recent activity yet.</p>
                )}
              </div>
            </section>
          </>
        )}

        {activeTab === "quiz" && (
          <section className="section">
            <div className="section-header">
              <h2>📝 AI Quiz Generator</h2>
            </div>
            
            <div className="ask-card" style={{ marginTop: "20px" }}>
              <div className="ask-icon">📝</div>
              <div className="ask-content" style={{ width: "100%" }}>
                <h3>What topic do you want to test yourself on?</h3>
                
                <div className="input-row">
                  <input
                    type="text"
                    placeholder="e.g., Database Normalization, Python Basics, Physics..."
                    value={quizTopic}
                    onChange={(e) => setQuizTopic(e.target.value)}
                    onKeyDown={(e) => { if (e.key === "Enter") handleGenerateQuiz(); }}
                  />
                  <button onClick={handleGenerateQuiz} disabled={isQuizLoading}>
                    {isQuizLoading ? "Generating..." : "Generate Quiz"}
                  </button>
                </div>

                {quizResponse && (
                  <div className="ai-response" style={{ marginTop: "20px" }}>
                    <strong>Your Quiz on: {quizTopic}</strong>
                    {/* NEW: Using our helper function to render the UI */}
                    {renderQuizContent(quizResponse)}
                  </div>
                )}
              </div>
            </div>
          </section>
        )}

        {activeTab === "materials" && (
          <section className="section">
            <h2>📚 Study Materials</h2>
            <p>Your uploaded PDFs and study content will appear here.</p>
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
            <div className="section-header">
              <h2>🕘 Full Study History</h2>
            </div>
            <div className="activity-card" style={{ marginTop: "20px" }}>
              {recentHistory.length > 0 ? (
                recentHistory.map((item, index) => (
                  <div className="activity-item" key={index}>
                    <span>🧠</span>
                    <div>
                      <strong>{item.query || "AI Chat"}</strong>
                      <p>{item.response ? item.response.substring(0, 80) + "..." : "Study Session"}</p>
                    </div>
                    <small>{item.timestamp ? new Date(item.timestamp).toLocaleString() : "Recently"}</small>
                  </div>
                ))
              ) : (
                <p style={{ padding: "1rem" }}>No history available.</p>
              )}
            </div>
          </section>
        )}

      </main>
    </div>
  );
}

export default App;