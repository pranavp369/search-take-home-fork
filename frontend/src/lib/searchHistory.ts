export type SearchQuery = {
  /** Raw query string entered by the user. */
  query: string;
  /** Unix timestamp in milliseconds when the query was executed. */
  timestamp: number;
};

export type SearchHistory = SearchQuery[];

export type AddToHistoryOptions = {
  /**
   * Maximum number of entries to keep.
   * Defaults to 10 if not provided.
   */
  maxEntries?: number;
};

/**
 * Add a new query to the existing history and return a new history array.
 *
 * TODO (candidate):
 * - Ignore queries that are empty or only whitespace.
 * - Add the new query as the most recent entry with the current timestamp.
 * - Avoid duplicate *adjacent* queries (if the last query has the same text,
 *   update its timestamp instead of adding a new entry).
 * - Trim the history so it never exceeds `maxEntries` (default 10).
 * - Do not mutate the `history` array; always return a new one.
 */
export function addToHistory(
  history: SearchHistory,
  query: string,
  options: AddToHistoryOptions = {},
): SearchHistory {
  // Stub implementation so the app compiles; replace this with real logic.
  //throw new Error("addToHistory() not implemented yet");
  const { maxEntries } = options;
  console.log("MaxEntries:",maxEntries);
  // Ignore empty or whitespace-only queries
  const trimmedQuery = query.trim();
  if (!trimmedQuery) {
    return [...history];
  }

  // Check if the most recent query is identical (avoid duplicate adjacent entries)
  if (history.length > 0 && history[0].query === trimmedQuery) {
    // Update the timestamp of the most recent entry
    const updatedHistory = [...history];
    updatedHistory[0] = {
      query: trimmedQuery,
      timestamp: Date.now(),
    };
    return updatedHistory;
  }

  // Add new entry at the beginning (most recent first)
  const newEntry: SearchQuery = {
    query: trimmedQuery,
    timestamp: Date.now(),
  };
  
  // Create new history with the new entry prepended
  const newHistory = [newEntry, ...history];
  
  // Trim to maxEntries
  
  //console.log("History:", newHistory.slice(0, maxEntries));
  return newHistory.slice(0, maxEntries);
}

/**
 * Return a list of recent query strings in most-recent-first order.
 *
 * TODO (candidate):
 * - Use the provided `history` array (do not mutate it).
 * - Return only the `query` strings, ordered from newest to oldest.
 * - Optionally deduplicate consecutive identical strings if your
 *   `addToHistory` implementation does not already enforce this.
 */
export function getRecentQueries(history: SearchHistory): string[] {
  // Stub implementation so the app compiles; replace this with real logic.
  //throw new Error("getRecentQueries() not implemented yet");
  return history.map(entry => entry.query);
}

