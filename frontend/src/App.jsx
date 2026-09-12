import { useState } from "react";
import "./App.css";
function App() {
  const [question, setQuestion] = useState("");
  const [response, setResponse] = useState("");
  const [loading, setLoading] = useState(false);

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
          <button className="nav-item active">🏠 Dashboard</button>
          <button className="nav-item">📚 Study Materials</button>
          <button className="nav-item">📝 Quiz</button>
          <button className="nav-item">📅 Study Plan</button>
          <button className="nav-item">📊 Progress</button>
          <button className="nav-item">🕘 History</button>
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
                  if (e.key === "Enter") {
                    askAI();
                  }
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
            <div className="action-card">
              <div className="action-icon">💡</div>
              <h3>Ask a Question</h3>
              <p>Get simple explanations for difficult topics.</p>
            </div>

            <div className="action-card">
              <div className="action-icon">📝</div>
              <h3>Generate Quiz</h3>
              <p>Test your knowledge with an AI-generated quiz.</p>
            </div>

            <div className="action-card">
              <div className="action-icon">📅</div>
              <h3>Create Study Plan</h3>
              <p>Build a study plan based on your available time.</p>
            </div>
          </div>
        </section>

        <section className="section">
          <div className="section-header">
            <h2>Recent Activity</h2>
            <span>View all</span>
          </div>

          <div className="activity-card">
            <div className="activity-item">
              <span>🧠</span>
              <div>
                <strong>Operating Systems</strong>
                <p>Process Management</p>
              </div>
              <small>Today</small>
            </div>

            <div className="activity-item">
              <span>📝</span>
              <div>
                <strong>DBMS Quiz</strong>
                <p>Normalization · 4/5</p>
              </div>
              <small>Today</small>
            </div>

            <div className="activity-item">
              <span>💻</span>
              <div>
                <strong>C++</strong>
                <p>Inheritance</p>
              </div>
              <small>Today</small>
            </div>
          </div>
        </section>
      </main>
    </div>
  );
}

export default App;