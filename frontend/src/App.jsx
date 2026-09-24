import { useState, useEffect } from "react";
import ReactMarkdown from "react-markdown";
import "./App.css";

function App() {
  // --- States ---
  const [activeTab, setActiveTab] = useState("dashboard");
  const [recentHistory, setRecentHistory] = useState([]);

  // Dashboard Chat State
  const [question, setQuestion] = useState("");
  const [response, setResponse] = useState("");
  const [loading, setLoading] = useState(false);

  // Quiz State
  const [quizTopic, setQuizTopic] = useState("");
  const [quizResponse, setQuizResponse] = useState("");
  const [isQuizLoading, setIsQuizLoading] = useState(false);

  // Study Plan State
  const [planTopic, setPlanTopic] = useState("");
  const [planDuration, setPlanDuration] = useState("");
  const [planResponse, setPlanResponse] = useState("");
  const [isPlanLoading, setIsPlanLoading] = useState(false);

  // Study Materials State
  const [materialQuery, setMaterialQuery] = useState("");
  const [materialResponse, setMaterialResponse] = useState("");
  const [isMaterialLoading, setIsMaterialLoading] = useState(false);

  // Progress State
  const [progressResponse, setProgressResponse] = useState("");
  const [isProgressLoading, setIsProgressLoading] = useState(false);

  // --- API Calls ---
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

  const sendToAI = async (message) => {
    const res = await fetch("http://127.0.0.1:8000/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message }),
    });
    if (!res.ok) throw new Error(`Server returned status: ${res.status}`);
    const data = await res.json();
    fetchHistory();
    return data.response;
  };

  // --- Handlers ---
  const askAI = async () => {
    if (!question.trim()) return;
    setLoading(true);
    setResponse("");
    try {
      const reply = await sendToAI(question);
      setResponse(reply);
    } catch (error) {
      setResponse(`Diagnostic Error: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateQuiz = async () => {
    if (!quizTopic.trim()) return;
    setIsQuizLoading(true);
    setQuizResponse("");
    try {
      const reply = await sendToAI(`Generate a multiple choice quiz about: ${quizTopic}.`);
      setQuizResponse(reply);
    } catch (error) {
      setQuizResponse(`Error: ${error.message}`);
    } finally {
      setIsQuizLoading(false);
    }
  };

  const handleGeneratePlan = async () => {
    if (!planTopic.trim() || !planDuration.trim()) return;
    setIsPlanLoading(true);
    setPlanResponse("");
    try {
      const reply = await sendToAI(`Create a study plan for: ${planTopic} lasting ${planDuration} hours.`);
      setPlanResponse(reply);
    } catch (error) {
      setPlanResponse(`Error: ${error.message}`);
    } finally {
      setIsPlanLoading(false);
    }
  };

  const handleSearchMaterials = async () => {
    if (!materialQuery.trim()) return;
    setIsMaterialLoading(true);
    setMaterialResponse("");
    try {
      const reply = await sendToAI(`Search my study materials for: ${materialQuery}`);
      setMaterialResponse(reply);
    } catch (error) {
      setMaterialResponse(`Error: ${error.message}`);
    } finally {
      setIsMaterialLoading(false);
    }
  };

  const handleGetProgress = async () => {
    setIsProgressLoading(true);
    setProgressResponse("");
    try {
      const reply = await sendToAI(`Provide a detailed summary of my learning progress based on my history and quiz results.`);
      setProgressResponse(reply);
    } catch (error) {
      setProgressResponse(`Error: ${error.message}`);
    } finally {
      setIsProgressLoading(false);
    }
  };

  // --- UI Renderers ---
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
        return <div style={{ marginTop: "10px" }}><ReactMarkdown>{text}</ReactMarkdown></div>;
      }
    }
    return <div style={{ marginTop: "10px" }}><ReactMarkdown>{text}</ReactMarkdown></div>;
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
                  <input type="text" placeholder="Ask anything about your studies..." value={question} onChange={(e) => setQuestion(e.target.value)} onKeyDown={(e) => { if (e.key === "Enter") askAI(); }} />
                  <button onClick={askAI} disabled={loading}>{loading ? "Thinking..." : "Ask AI →"}</button>
                </div>
                {response && (
                  <div className="ai-response">
                    <strong>AI Tutor</strong>
                    {/* NEW: Markdown renderer for dashboard chat */}
                    <div style={{ marginTop: "10px", lineHeight: "1.6" }}>
                      <ReactMarkdown>{response}</ReactMarkdown>
                    </div>
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

        {activeTab === "materials" && (
          <section className="section">
            <div className="section-header">
              <h2>📚 Study Materials Search</h2>
            </div>
            <div className="ask-card" style={{ marginTop: "20px" }}>
              <div className="ask-icon">🔍</div>
              <div className="ask-content" style={{ width: "100%" }}>
                <h3>Search your knowledge base</h3>
                <div className="input-row">
                  <input
                    type="text"
                    placeholder="e.g., What are the ACID properties in DBMS?"
                    value={materialQuery}
                    onChange={(e) => setMaterialQuery(e.target.value)}
                    onKeyDown={(e) => { if (e.key === "Enter") handleSearchMaterials(); }}
                  />
                  <button onClick={handleSearchMaterials} disabled={isMaterialLoading}>
                    {isMaterialLoading ? "Searching..." : "Search"}
                  </button>
                </div>
                {materialResponse && (
                  <div className="ai-response" style={{ marginTop: "20px" }}>
                    <strong>Results for: {materialQuery}</strong>
                    {/* NEW: Markdown renderer for study materials */}
                    <div style={{ marginTop: "15px", lineHeight: "1.6" }}>
                      <ReactMarkdown>{materialResponse}</ReactMarkdown>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </section>
        )}

        {activeTab === "quiz" && (
          <section className="section">
            <div className="section-header"><h2>📝 AI Quiz Generator</h2></div>
            <div className="ask-card" style={{ marginTop: "20px" }}>
              <div className="ask-icon">📝</div>
              <div className="ask-content" style={{ width: "100%" }}>
                <h3>What topic do you want to test yourself on?</h3>
                <div className="input-row">
                  <input type="text" placeholder="e.g., Database Normalization, Python Basics..." value={quizTopic} onChange={(e) => setQuizTopic(e.target.value)} onKeyDown={(e) => { if (e.key === "Enter") handleGenerateQuiz(); }} />
                  <button onClick={handleGenerateQuiz} disabled={isQuizLoading}>{isQuizLoading ? "Generating..." : "Generate Quiz"}</button>
                </div>
                {quizResponse && (
                  <div className="ai-response" style={{ marginTop: "20px" }}>
                    <strong>Your Quiz on: {quizTopic}</strong>
                    {renderQuizContent(quizResponse)}
                  </div>
                )}
              </div>
            </div>
          </section>
        )}

        {activeTab === "plan" && (
          <section className="section">
            <div className="section-header"><h2>📅 AI Study Planner</h2></div>
            <div className="ask-card" style={{ marginTop: "20px" }}>
              <div className="ask-icon">📅</div>
              <div className="ask-content" style={{ width: "100%" }}>
                <h3>What do you want to study, and how much time do you have?</h3>
                <div className="input-row" style={{ display: 'flex', gap: '10px' }}>
                  <input type="text" placeholder="Topic (e.g., React Hooks)" value={planTopic} onChange={(e) => setPlanTopic(e.target.value)} style={{ flex: "2" }} />
                  <input type="number" placeholder="Hours" value={planDuration} onChange={(e) => setPlanDuration(e.target.value)} style={{ flex: "1" }} onKeyDown={(e) => { if (e.key === "Enter") handleGeneratePlan(); }} min="1" />
                  <button onClick={handleGeneratePlan} disabled={isPlanLoading}>{isPlanLoading ? "Planning..." : "Create Plan"}</button>
                </div>
                {planResponse && (
                  <div className="ai-response" style={{ marginTop: "20px" }}>
                    <strong>Study Plan: {planTopic} ({planDuration} Hours)</strong>
                    {/* NEW: Markdown renderer for study plan */}
                    <div style={{ marginTop: "15px", lineHeight: "1.6" }}>
                      <ReactMarkdown>{planResponse.replace("__PLAN__", "").trim()}</ReactMarkdown>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </section>
        )}

        {activeTab === "progress" && (
          <section className="section">
            <div className="section-header">
              <h2>📊 Your Learning Progress</h2>
            </div>
            <div className="ask-card" style={{ marginTop: "20px" }}>
              <div className="ask-icon">📈</div>
              <div className="ask-content" style={{ width: "100%" }}>
                <h3>Check how far you've come</h3>
                <p style={{ color: "#666", marginBottom: "15px" }}>
                  Generate an AI summary of your completed quizzes, active study plans, and overall activity.
                </p>
                <button onClick={handleGetProgress} disabled={isProgressLoading} style={{ width: "fit-content", padding: "10px 20px" }}>
                  {isProgressLoading ? "Analyzing Data..." : "Generate Progress Report"}
                </button>
                {progressResponse && (
                  <div className="ai-response" style={{ marginTop: "20px" }}>
                    <strong>AI Progress Summary</strong>
                    {/* NEW: Markdown renderer for progress summary */}
                    <div style={{ marginTop: "15px", lineHeight: "1.6" }}>
                      <ReactMarkdown>{progressResponse}</ReactMarkdown>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </section>
        )}

        {activeTab === "history" && (
          <section className="section">
            <div className="section-header"><h2>🕘 Full Study History</h2></div>
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