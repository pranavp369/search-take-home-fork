import { type FormEvent, useState } from "react";
import { SearchError, type SearchResult, search } from "../../lib/api";
import {
  addToHistory,
  getRecentQueries,
  type SearchHistory,
} from "../../lib/searchHistory";

export const SearchPage = () => {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<SearchResult[]>();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>();
  const [history, setHistory] = useState<SearchHistory>([]);

  async function handleSearch(rawQuery: string) {
    const trimmed = rawQuery.trim();
    if (!trimmed) {
      return;
    }
    // Keep input in sync when triggered from RecentSearches
    setQuery(trimmed);

    setLoading(true);
    setError(null);

    try {
      const nextResults = await search(trimmed);
      setResults(nextResults);
      setHistory((prev) => addToHistory(prev, trimmed, { maxEntries: 5 }));
    } catch (err) {
      if (err instanceof SearchError) {
        setError(err.message);
      } else if (err instanceof Error) {
        setError(err.message);
      } else {
        setError("Unexpected error while searching.");
      }
      setResults(undefined);
    } finally {
      setLoading(false);
    }
  }

  const handleSubmit = (event: FormEvent) => {
    event.preventDefault();
    void handleSearch(query);
  };

  return (
    <div>
      <form
        onSubmit={handleSubmit}
        style={{ display: "flex", gap: "0.5rem", marginBottom: "1rem" }}
      >
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search documents..."
          style={{ flex: 1, padding: "0.5rem" }}
        />
        <button type="submit" disabled={loading || !query.trim()}>
          {loading ? "Searching..." : "Search"}
        </button>
      </form>

      {error && (
        <div style={{ color: "red", marginBottom: "0.5rem" }}>{error}</div>
      )}

      {history.length > 0 && (
        <div style={{ marginBottom: "0.75rem", fontSize: "0.9rem" }}>
          <div style={{ marginBottom: "0.25rem" }}>Recent searches:</div>
          <div style={{ display: "flex", flexWrap: "wrap", gap: "0.5rem" }}>
            {getRecentQueries(history).map((q, index) => (
              <button
                key={`${q}-${
                  //
                  index
                }`}
                type="button"
                onClick={() => void handleSearch(q)}
                disabled={loading}
                style={{
                  border: "1px solid #ccc",
                  borderRadius: "999px",
                  padding: "0.25rem 0.75rem",
                  background: "#f5f5f5",
                  cursor: "pointer",
                }}
              >
                {q}
              </button>
            ))}
          </div>
        </div>
      )}

      {results?.length === 0 && !loading && !error && (
        <div>No results yet. Try searching for something.</div>
      )}

      {results && results.length > 0 && (
        <ul>
          {results.map((r) => (
            <li
              key={r.document.metadata.id}
              style={{ marginBottom: "0.5rem" }}
            >
              <strong>{r.document.metadata.title}</strong> (score:{" "}
              {r.score.toFixed(3)})
              {r.reason && (
                <div style={{ fontSize: "0.85rem", color: "#555" }}>
                  {r.reason}
                </div>
              )}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};
