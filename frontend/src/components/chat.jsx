import { useState } from "react";
import ResultsTable from "./ResultsTable";

function Chat() {
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);

  const sendMessage = async () => {
    if (!question.trim() || loading) return;

    const userQuestion = question.trim();
    setMessages((prev) => [...prev, { role: "user", content: userQuestion }]);
    setQuestion("");
    setLoading(true);

    try {
      const response = await fetch("http://localhost:8000/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: userQuestion })
      });

      if (!response.ok) throw new Error(`Request failed (${response.status})`);
      const data = await response.json();
      setMessages((prev) => [...prev, {
        role: "assistant",
        content: data.messages?.[0] || "",
        sql: data.sql,
        result: data.result
      }]);
    } catch (error) {
      setMessages((prev) => [...prev, {
        role: "assistant",
        content: `Error: ${error.message}`
      }]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="brand-lockup">
          <div className="brand-mark" aria-hidden="true">S</div>
          <div><p className="eyebrow">Workspace / Data</p><h1>SQL Agent</h1></div>
        </div>
        <div className="connection-status"><span /> Database connected</div>
      </header>

      <main className="conversation">
        <div className="conversation-inner">
          {messages.length === 0 ? (
            <section className="welcome-panel">
              <p className="section-kicker">Natural language to SQL</p>
              <h2>Explore your data<br /><em>with confidence.</em></h2>
              <p className="welcome-copy">Ask a question and SQL Agent will translate it into a query, run it safely, and return the results.</p>
              <div className="prompt-grid">
                <button className="prompt-card" onClick={() => setQuestion("Give me the status of employees with their name and experience greater than 3 years")}>
                  <span className="prompt-icon">01</span><span>Employee status with experience over 3 years</span>
                </button>
                <button className="prompt-card" onClick={() => setQuestion("Give me all employees")}>
                  <span className="prompt-icon">02</span><span>Show me all employees</span>
                </button>
              </div>
            </section>
          ) : (
            <div className="message-list">
              {messages.map((message, index) => (
                <div key={index} className={`message-row ${message.role}`}>
                  <div className="message-avatar">{message.role === "user" ? "You" : "SA"}</div>
                  <div className={`message-bubble ${message.role}`}>
                    <p className="message-text">{message.content || (message.sql ? "Query complete." : "")}</p>
                    {message.sql && <div className="output-block"><div className="output-heading"><span>Generated SQL</span><span className="output-badge">READ ONLY</span></div><pre>{message.sql}</pre></div>}
                    {message.result && <div className="output-block"><div className="output-heading"><span>Query result</span><span className="output-badge">LIVE DATA</span></div><ResultsTable data={message.result} /></div>}
                  </div>
                </div>
              ))}
              {loading && <div className="message-row assistant"><div className="message-avatar">SA</div><div className="message-bubble assistant loading-bubble"><span className="loading-label">Working on it</span><span className="loading-dots"><i /><i /><i /></span></div></div>}
            </div>
          )}
        </div>
      </main>

      <footer className="composer-wrap">
        <div className="composer">
          <textarea value={question} onChange={(event) => setQuestion(event.target.value)} onKeyDown={handleKeyDown} placeholder="Ask about your database..." rows={1} />
          <button className="send-button" onClick={sendMessage} disabled={loading || !question.trim()} aria-label="Send query">
            <span>{loading ? "..." : "Run query"}</span><span className="send-arrow">&#8594;</span>
          </button>
        </div>
        <div className="composer-meta"><span>Enter to run</span><span>Shift + Enter for a new line</span></div>
      </footer>
    </div>
  );
}

export default Chat;
