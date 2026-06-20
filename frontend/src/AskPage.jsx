import { useState } from "react";
import { API_BASE_URL } from "./config";

function AskPage() {
  const [question, setQuestion] = useState("");
  const [history, setHistory] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");

  async function handleAsk() {
    if (!question.trim()) {
      setErrorMessage("Please type a question first.");
      return;
    }

    setErrorMessage("");
    setIsLoading(true);

    try {
      const response = await fetch(`${API_BASE_URL}/ask`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: question }),
      });

      const data = await response.json();

      if (!response.ok) {
        setErrorMessage(data.detail || "Something went wrong. Please try again.");
        setIsLoading(false);
        return;
      }

      setHistory([
        {
          question: question,
          answer: data.answer,
          sources: data.sources,
          answerFound: data.answer_found,
          responseTimeMs: data.response_time_ms,
        },
        ...history,
      ]);

      setQuestion("");
    } catch (error) {
      setErrorMessage("Could not reach the backend. Is the FastAPI server running on port 8000?");
    } finally {
      setIsLoading(false);
    }
  }

  function handleKeyDown(event) {
    if (event.key === "Enter" && !isLoading) {
      handleAsk();
    }
  }

  return (
    <div className="ask-page">
      <h2>Ask a question about the AWS Customer Agreement</h2>

      <div className="ask-input-row">
        <input
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="e.g. How are fees and charges billed?"
          disabled={isLoading}
        />
        <button onClick={handleAsk} disabled={isLoading}>
          {isLoading ? "Thinking..." : "Ask"}
        </button>
      </div>

      {errorMessage && <p className="error-text">{errorMessage}</p>}

      <div className="chat-history">
        {history.length === 0 && !isLoading && (
          <p className="empty-hint">No questions asked yet. Try asking something above.</p>
        )}

        {history.map((item, index) => (
          <div key={index} className="chat-item">
            <p className="chat-question">
              <strong>You:</strong> {item.question}
            </p>

            <p className={item.answerFound ? "chat-answer" : "chat-answer not-found"}>
              <strong>Assistant:</strong> {item.answer}
            </p>

            <p className="chat-meta">
              {item.answerFound ? "Answer found in document" : "Not found in document"} ·{" "}
              {item.responseTimeMs} ms
            </p>

            {item.sources && item.sources.length > 0 && (
              <details className="chat-sources">
                <summary>View source chunk(s) used ({item.sources.length})</summary>
                {item.sources.map((source) => (
                  <div key={source.chunk_id} className="source-chunk">
                    <p className="source-label">Chunk {source.chunk_id}</p>
                    <p className="source-text">{source.text}</p>
                  </div>
                ))}
              </details>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

export default AskPage;