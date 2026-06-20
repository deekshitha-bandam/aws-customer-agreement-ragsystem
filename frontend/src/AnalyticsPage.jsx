import { useEffect, useState } from "react";
import { API_BASE_URL } from "./config";


function AnalyticsPage() {
  const [analytics, setAnalytics] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState("");

  async function fetchAnalytics() {
    setIsLoading(true);
    setErrorMessage("");

    try {
      const response = await fetch(`${API_BASE_URL}/analytics`);
      const data = await response.json();

      if (!response.ok) {
        setErrorMessage(data.detail || "Could not load analytics.");
      } else {
        setAnalytics(data);
      }
    } catch (error) {
      setErrorMessage("Could not reach the backend. Is the FastAPI server running on port 8000?");
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    fetchAnalytics();
  }, []);

  return (
    <div className="analytics-page">
      <div className="analytics-header">
        <h2>Usage Analytics</h2>
        <button onClick={fetchAnalytics} disabled={isLoading}>
          {isLoading ? "Refreshing..." : "Refresh"}
        </button>
      </div>

      {errorMessage && <p className="error-text">{errorMessage}</p>}

      {isLoading && !analytics && <p>Loading analytics...</p>}

      {analytics && (
        <>
          <div className="stat-cards">
            <div className="stat-card">
              <p className="stat-number">{analytics.total_queries}</p>
              <p className="stat-label">Total questions asked</p>
            </div>
            <div className="stat-card">
              <p className="stat-number">{analytics.average_response_time_ms} ms</p>
              <p className="stat-label">Average response time</p>
            </div>
            <div className="stat-card">
              <p className="stat-number">{analytics.unanswered_queries.length}</p>
              <p className="stat-label">Unanswered queries (recent)</p>
            </div>
          </div>

          <section className="analytics-section">
            <h3>Most Frequently Asked Questions</h3>
            {analytics.most_frequent_questions.length === 0 ? (
              <p className="empty-hint">No questions logged yet.</p>
            ) : (
              <table>
                <thead>
                  <tr>
                    <th>Question</th>
                    <th>Times Asked</th>
                  </tr>
                </thead>
                <tbody>
                  {analytics.most_frequent_questions.map((item, index) => (
                    <tr key={index}>
                      <td>{item.question}</td>
                      <td>{item.times_asked}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </section>

          <section className="analytics-section">
            <h3>Queries Where No Answer Was Found</h3>
            {analytics.unanswered_queries.length === 0 ? (
              <p className="empty-hint">None so far - every question has been answered from the document.</p>
            ) : (
              <table>
                <thead>
                  <tr>
                    <th>Question</th>
                    <th>Asked At</th>
                  </tr>
                </thead>
                <tbody>
                  {analytics.unanswered_queries.map((item, index) => (
                    <tr key={index}>
                      <td>{item.question}</td>
                      <td>{new Date(item.asked_at).toLocaleString()}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </section>
        </>
      )}
    </div>
  );
}

export default AnalyticsPage;