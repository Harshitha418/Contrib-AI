import { useCallback, useEffect, useState } from "react";
import "./App.css";
import ExploreIssues from "./pages/ExploreIssues";

import {
  GitBranch,
  LayoutDashboard,
  Search,
  GitPullRequest,
  BookOpen,
  Settings,
  Bell,
  Sparkles,
  CircleDot,
  Star,
  GitFork,
  ArrowUpRight,
  Code2,
  Menu,
  X,
  ExternalLink,
  RefreshCw
} from "lucide-react";

import {
  fetchRepositories,
  fetchIssues
} from "./services/githubService";

const navigation = [
  { name: "Dashboard", icon: LayoutDashboard },
  { name: "Explore Issues", icon: Search },
  { name: "Repositories", icon: GitBranch },
  { name: "My Contributions", icon: GitPullRequest },
  { name: "Learning Hub", icon: BookOpen }
];

function App() {
  const [activePage, setActivePage] = useState("Dashboard");
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const [repositories, setRepositories] = useState([]);
  const [issues, setIssues] = useState([]);

  const [loading, setLoading] = useState(true);
  const [issueError, setIssueError] = useState("");
  const [repositoryError, setRepositoryError] = useState("");

  // Fetch repositories and issues independently
  const loadDashboardData = useCallback(async () => {
    setLoading(true);
    setIssueError("");
    setRepositoryError("");

    const results = await Promise.allSettled([
      fetchRepositories(10),
      fetchIssues({
        perPage: 10,
        language: "Java"
      })
    ]);

    // Handle repository response
    if (results[0].status === "fulfilled") {
      const repositoryData = results[0].value;
      setRepositories(repositoryData.repositories || []);
    } else {
      console.error("Repository API error:", results[0].reason);
      setRepositories([]);
      setRepositoryError(
        "Unable to load repositories. Please try again later."
      );
    }

    // Handle issue response
    if (results[1].status === "fulfilled") {
      const issueData = results[1].value;
      setIssues(issueData.issues || []);
    } else {
      const error = results[1].reason;

      console.error("Issue API error:", error);
      setIssues([]);

      if (error.response?.status === 403) {
        setIssueError(
          "GitHub is temporarily limiting requests. Please wait a few minutes before trying again."
        );
      } else if (error.response?.status === 503) {
        setIssueError(
          "Unable to connect to GitHub right now. Please try again later."
        );
      } else {
        setIssueError(
          "Unable to load GitHub issues. Please try again later."
        );
      }
    }

    setLoading(false);
  }, []);

  useEffect(() => {
    loadDashboardData();
  }, [loadDashboardData]);

  // Render recommended issue cards
  const renderIssues = () => {
    if (loading) {
      return (
        <div className="empty-state">
          <RefreshCw size={28} className="purple-text" />
          <h3>Finding opportunities...</h3>
          <p>
            Fetching real GitHub issues and calculating recommendation scores.
          </p>
        </div>
      );
    }

    if (issueError) {
      return (
        <div className="empty-state">
          <CircleDot size={30} className="purple-text" />
          <h3>Unable to load issues</h3>
          <p>{issueError}</p>

          <button
            className="primary-button"
            onClick={loadDashboardData}
          >
            <RefreshCw size={16} />
            Try again
          </button>
        </div>
      );
    }

    if (issues.length === 0) {
      return (
        <div className="empty-state">
          <GitFork size={30} />
          <h3>No issues found</h3>
          <p>
            Try again later to discover more open-source opportunities.
          </p>
          <button
            className="primary-button"
            onClick={loadDashboardData}
          >
            <RefreshCw size={16} />
            Refresh
          </button>
        </div>
      );
    }

    return (
      <div className="issue-list">
        {issues.slice(0, 5).map((issue) => {
          const score =
            issue.score ??
            issue.recommendation_score ??
            0;

          const recommendation =
            issue.recommendation ??
            issue.recommendation_level ??
            "Not scored";

          const reasons =
            issue.reasons ??
            issue.recommendation_reasons ??
            [];

          return (
            <div className="issue-card" key={issue.url}>
              <div className="issue-card-top">
                <div>
                  <h3>{issue.title}</h3>

                  <p className="issue-repository">
                    <GitBranch size={14} />
                    {issue.repository}
                    <span>#{issue.issue_number}</span>
                  </p>
                </div>

                <div className="recommendation-score">
                  <strong>{score}</strong>
                  <span>/100</span>
                </div>
              </div>

              <div className="issue-labels">
                {issue.labels?.map((label) => (
                  <span className="issue-label" key={label}>
                    {label}
                  </span>
                ))}
              </div>

              <div className="recommendation-info">
                <span className="recommendation-level">
                  <Sparkles size={14} />
                  {recommendation}
                </span>
              </div>

              {reasons.length > 0 && (
                <ul className="recommendation-reasons">
                  {reasons.map((reason, index) => (
                    <li key={index}>{reason}</li>
                  ))}
                </ul>
              )}

              <a
                href={issue.url}
                target="_blank"
                rel="noopener noreferrer"
                className="issue-link"
              >
                View issue <ExternalLink size={14} />
              </a>
            </div>
          );
        })}
      </div>
    );
  };

  return (
    <div className="app-container">

      {/* Sidebar */}
      <aside className={`sidebar ${sidebarOpen ? "sidebar-open" : ""}`}>
        <div className="brand">
          <div className="brand-icon">
            <Code2 size={22} />
          </div>

          <span>
            Contrib<span className="purple-text">AI</span>
          </span>

          <button
            className="mobile-close"
            onClick={() => setSidebarOpen(false)}
          >
            <X size={20} />
          </button>
        </div>

        <div className="sidebar-section">
          <p className="sidebar-label">WORKSPACE</p>

          {navigation.map((item) => {
            const Icon = item.icon;

            return (
              <button
                key={item.name}
                className={`nav-item ${
                  activePage === item.name ? "active" : ""
                }`}
                onClick={() => {
                  setActivePage(item.name);
                  setSidebarOpen(false);
                }}
              >
                <Icon size={19} />
                <span>{item.name}</span>
              </button>
            );
          })}
        </div>

        <div className="sidebar-bottom">
          <div className="help-card">
            <Sparkles size={20} />
            <h4>AI Contribution Assistant</h4>
            <p>
              Find issues that match your skills and grow as a developer.
            </p>
          </div>

          <button
            className="nav-item"
            onClick={() => setActivePage("Settings")}
          >
            <Settings size={19} />
            <span>Settings</span>
          </button>

          <div className="profile">
            <div className="avatar">H</div>
            <div>
              <h4>Developer</h4>
              <p>Open Source Explorer</p>
            </div>
          </div>
        </div>
      </aside>

      {/* Main content */}
      <main className="main-content">

        <header className="topbar">
          <button
            className="mobile-menu"
            onClick={() => setSidebarOpen(true)}
          >
            <Menu size={22} />
          </button>

          <div className="breadcrumb">
            Workspace <span>/</span> {activePage}
          </div>

          <div className="topbar-actions">
            <button className="icon-button">
              <Bell size={19} />
            </button>

            <div className="top-avatar">H</div>
          </div>
        </header>

        <div className="dashboard-content">
          {activePage === "Explore Issues" ? (
            <ExploreIssues />
          ) : (
            <>
              {/* Welcome */}
              <section className="welcome-section">
                <div>
                  <p className="eyebrow">
                    <Sparkles size={15} />
                    YOUR OPEN SOURCE JOURNEY
                  </p>

                  <h1>
                    Find your next{" "}
                    <span className="purple-text">contribution.</span>
                  </h1>

                  <p className="welcome-description">
                    Discover open-source opportunities, find beginner-friendly
                    issues and build something meaningful.
                  </p>
                </div>

                <button
                  className="primary-button"
                  onClick={() => setActivePage("Explore Issues")}
                >
                  <Search size={17} />
                  Explore Issues
                  <ArrowUpRight size={16} />
                </button>
              </section>

              {/* Statistics */}
              <section className="stats-grid">

                <div className="stat-card">
                  <div className="stat-icon purple-bg">
                    <GitBranch size={21} />
                  </div>
                  <p>Repositories Discovered</p>
                  <h2>{loading ? "..." : repositories.length}</h2>
                  <span>Fetched from GitHub</span>
                </div>

                <div className="stat-card">
                  <div className="stat-icon blue-bg">
                    <CircleDot size={21} />
                  </div>
                  <p>Open Issues</p>
                  <h2>{loading ? "..." : issues.length}</h2>
                  <span>Matching issues fetched</span>
                </div>

                <div className="stat-card">
                  <div className="stat-icon green-bg">
                    <GitPullRequest size={21} />
                  </div>
                  <p>Contributions</p>
                  <h2>0</h2>
                  <span>Start contributing</span>
                </div>

                <div className="stat-card">
                  <div className="stat-icon orange-bg">
                    <Star size={21} />
                  </div>
                  <p>Recommended Issues</p>
                  <h2>{loading ? "..." : issues.length}</h2>
                  <span>Scored by ContribAI</span>
                </div>

              </section>

              {/* Search */}
              <section className="search-section">
                <div>
                  <h2>Discover opportunities</h2>
                  <p>Find repositories and issues worth contributing to.</p>
                </div>

                <div className="search-box">
                  <Search size={19} />

                  <input
                    type="text"
                    placeholder="Search repositories, issues or technologies..."
                  />

                  <button onClick={() => setActivePage("Explore Issues")}>
                    Search
                  </button>
                </div>
              </section>

              {/* Recommendations */}
              <section className="issues-section">

                <div className="section-heading">
                  <div>
                    <h2>
                      <Sparkles size={20} className="purple-text" />
                      Recommended for you
                    </h2>

                    <p>
                      Issues selected based on recommendation scoring.
                    </p>
                  </div>

                  <button
                    className="text-button"
                    onClick={() => setActivePage("Explore Issues")}
                  >
                    View all <ArrowUpRight size={15} />
                  </button>
                </div>

                {renderIssues()}

              </section>

              {/* Repositories */}
              <section className="issues-section repository-section">

                <div className="section-heading">
                  <div>
                    <h2>
                      <GitBranch size={20} className="purple-text" />
                      Discover repositories
                    </h2>

                    <p>Recently updated Java repositories.</p>
                  </div>
                </div>

                {loading ? (
                  <div className="empty-state">
                    <RefreshCw size={25} className="purple-text" />
                    <p>Loading repositories...</p>
                  </div>
                ) : repositoryError ? (
                  <div className="empty-state">
                    <GitBranch size={28} className="purple-text" />
                    <p>{repositoryError}</p>
                    <button
                      className="primary-button"
                      onClick={loadDashboardData}
                    >
                      <RefreshCw size={16} />
                      Try again
                    </button>
                  </div>
                ) : (
                  <div className="repository-list">
                    {repositories.slice(0, 5).map((repo) => (
                      <a
                        href={repo.html_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="repository-card"
                        key={repo.full_name}
                      >
                        <div>
                          <h3>{repo.full_name}</h3>
                          <p>
                            {repo.description || "No description available."}
                          </p>
                        </div>

                        <ArrowUpRight size={17} />
                      </a>
                    ))}
                  </div>
                )}

              </section>

              {/* Footer */}
              <footer className="footer">
                <span>ContribAI © 2026</span>

                <span>
                  Built for the open-source community <Sparkles size={14} />
                </span>
              </footer>
            </>
          )}
        </div>
      </main>
    </div>
  );
}

export default App;