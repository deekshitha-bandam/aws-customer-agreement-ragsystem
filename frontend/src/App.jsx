import { useState } from "react";
import { API_BASE_URL } from "./config";
import AskPage from "./AskPage";
import AnalyticsPage from "./AnalyticsPage";
import "./App.css";

function App() {
  const [activeTab, setActiveTab] = useState("ask");
  const [ingestStatus, setIngestStatus] = useState("");
  const [isIngesting, setIsIngesting] = useState(false);

  async function handleIngest() {
    setIsIngesting(true);
    setIngestStatus("Processing PDF and building embeddings... this can take a little while the first time.");

    try {
      const response = await fetch(`${API_BASE_URL}/ingest`, { method: "POST" });
      const data = await response.json();

      if (!response.ok) {
        setIngestStatus(`Error: ${data.detail}`);
      } else {
        setIngestStatus(`Done! Processed the document into ${data.num_chunks} chunks. You can ask questions now.`);
      }
    } catch (error) {
      setIngestStatus("Could not reach the backend. Is the FastAPI server running on port 8000?");
    } finally {
      setIsIngesting(false);
    }
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1>AWS Agreement Q&A</h1>
        <p className="app-subtitle">A simple RAG-based document Q&A system</p>
      </header>

      <div className="ingest-bar">
        <button onClick={handleIngest} disabled={isIngesting}>
          {isIngesting ? "Processing..." : "1. Ingest Document (run this first)"}
        </button>
        {ingestStatus && <p className="ingest-status">{ingestStatus}</p>}
      </div>

      <nav className="tab-nav">
        <button
          className={activeTab === "ask" ? "tab-button active" : "tab-button"}
          onClick={() => setActiveTab("ask")}
        >
          Ask a Question
        </button>
        <button
          className={activeTab === "analytics" ? "tab-button active" : "tab-button"}
          onClick={() => setActiveTab("analytics")}
        >
          Analytics Dashboard
        </button>
      </nav>

      <main className="app-main">
        {activeTab === "ask" ? <AskPage /> : <AnalyticsPage />}
      </main>
    </div>
  );
}

export default App;