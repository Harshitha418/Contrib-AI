import { useCallback, useEffect, useState } from "react";
import {
  Search,
  RefreshCw,
  ExternalLink,
  SlidersHorizontal,
  AlertCircle,
  X,
} from "lucide-react";

import { fetchIssues } from "../services/githubService";

function ExploreIssues() {
  const [issues, setIssues] = useState([]);
  const [language, setLanguage] = useState("Java");
  const [label, setLabel] = useState("good first issue");
  const [sortBy, setSortBy] = useState("created");

  const [keyword, setKeyword] = useState("");
  const [activeKeyword, setActiveKeyword] = useState("");

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const loadIssues = useCallback(async () => {
    setLoading(true);
    setError("");

    try {
      const data = await fetchIssues({
        perPage: 30,
        language,
        label,
        sortBy,
        keyword: activeKeyword,
      });

      setIssues(data.issues || []);
    } catch (err) {
      if (err.response?.status === 403) {
        setError("GitHub API rate limit reached. Please try again later.");
      } else if (err.response?.status === 503) {
        setError("Unable to connect to GitHub. Please try again.");
      } else {
        setError("Something went wrong while fetching issues.");
      }

      setIssues([]);
    } finally {
      setLoading(false);
    }
  }, [language, label, sortBy, activeKeyword]);

  useEffect(() => {
    loadIssues();
  }, [loadIssues]);

  const handleSearch = (event) => {
    event.preventDefault();
    setActiveKeyword(keyword.trim());
  };

  const clearSearch = () => {
    setKeyword("");
    setActiveKeyword("");
  };

  return (
    <div className="explore-page">

      {/* Page heading */}
      <div className="page-heading">
        <div>
          <p className="page-eyebrow">DISCOVER OPPORTUNITIES</p>
          <h1>Explore Issues</h1>
          <p className="page-description">
            Find beginner-friendly open-source issues and start contributing.
          </p>
        </div>

        <button
          className="primary-button"
          onClick={loadIssues}
          disabled={loading}
        >
          <RefreshCw size={16} />
          {loading ? "Loading..." : "Refresh"}
        </button>
      </div>

      {/* Keyword search */}
      <form className="explore-search" onSubmit={handleSearch}>
        <Search size={19} />

        <input
          type="text"
          value={keyword}
          onChange={(event) => setKeyword(event.target.value)}
          placeholder="Search issues by keyword (e.g. Spring Boot, REST API)..."
        />

        {keyword && (
          <button
            type="button"
            className="clear-search"
            onClick={clearSearch}
            aria-label="Clear search"
          >
            <X size={17} />
          </button>
        )}

        <button type="submit" className="primary-button" disabled={loading}>
          Search
        </button>
      </form>

      {/* Filters */}
      <div className="explore-filters">
        <div className="filter-heading">
          <SlidersHorizontal size={18} />
          <span>Filters</span>
        </div>

        <div className="filter-controls">
          <div className="filter-group">
            <label htmlFor="language-filter">Language</label>
            <select
              id="language-filter"
              value={language}
              onChange={(event) => setLanguage(event.target.value)}
            >
              <option value="Java">Java</option>
              <option value="Python">Python</option>
              <option value="JavaScript">JavaScript</option>
              <option value="C++">C++</option>
            </select>
          </div>

          <div className="filter-group">
            <label htmlFor="label-filter">Issue Type</label>
            <select
              id="label-filter"
              value={label}
              onChange={(event) => setLabel(event.target.value)}
            >
              <option value="good first issue">Good First Issue</option>
              <option value="help wanted">Help Wanted</option>
            </select>
          </div>

          <div className="filter-group">
            <label htmlFor="sort-filter">Sort By</label>
            <select
              id="sort-filter"
              value={sortBy}
              onChange={(event) => setSortBy(event.target.value)}
            >
              <option value="created">Recently Created</option>
              <option value="updated">Recently Updated</option>
              <option value="comments">Most Discussed</option>
            </select>
          </div>
        </div>
      </div>

      {/* Results heading */}
      <div className="explore-results-heading">
        <div>
          <h2>Available Issues</h2>
          <p>
            {loading
              ? "Searching GitHub..."
              : `${issues.length} issues found`}
          </p>
        </div>
      </div>

      {/* Issues */}
      {loading ? (
        <div className="empty-state">
          <RefreshCw className="loading-icon" size={28} />
          <h3>Finding opportunities</h3>
          <p>Searching GitHub for suitable issues...</p>
        </div>
      ) : error ? (
        <div className="empty-state">
          <AlertCircle size={28} />
          <h3>Unable to load issues</h3>
          <p>{error}</p>

          <button className="primary-button" onClick={loadIssues}>
            Try Again
          </button>
        </div>
      ) : issues.length === 0 ? (
        <div className="empty-state">
          <Search size={28} />
          <h3>No issues found</h3>
          <p>Try changing your keyword or filters.</p>
        </div>
      ) : (
        <div className="issue-list">
          {issues.map((issue) => (
            <article
              className="issue-card"
              key={`${issue.repository}-${issue.issue_number}`}
            >
              <div className="issue-card-top">
                <div>
                  <p className="issue-repository">
                    {issue.repository} #{issue.issue_number}
                  </p>

                  <h3>{issue.title}</h3>
                </div>

                <div className="recommendation-score">
                  <strong>
                    {issue.score ?? issue.recommendation_score ?? 0}
                  </strong>
                  <span>Score</span>
                </div>
              </div>

              {issue.recommendation && (
                <div className="recommendation-info">
                  <span className="recommendation-level">
                    {issue.recommendation}
                  </span>
                </div>
              )}

              {issue.reasons?.length > 0 && (
                <ul className="recommendation-reasons">
                  {issue.reasons.map((reason, index) => (
                    <li key={index}>{reason}</li>
                  ))}
                </ul>
              )}

              <div className="issue-labels">
                {issue.labels?.map((item) => (
                  <span className="issue-label" key={item}>
                    {item}
                  </span>
                ))}
              </div>

              <div className="issue-card-footer">
                <span>
                  Updated:{" "}
                  {issue.updated_at
                    ? new Date(issue.updated_at).toLocaleDateString()
                    : "Unknown"}
                </span>

                <a
                  className="issue-link"
                  href={issue.url}
                  target="_blank"
                  rel="noreferrer"
                >
                  View on GitHub
                  <ExternalLink size={14} />
                </a>
              </div>
            </article>
          ))}
        </div>
      )}
    </div>
  );
}

export default ExploreIssues;