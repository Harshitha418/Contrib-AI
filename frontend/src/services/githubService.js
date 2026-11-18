import api from "./api";

// Fetch Java repositories
export const fetchRepositories = async (perPage = 10) => {
  const response = await api.get("/github/repositories", {
    params: {
      per_page: perPage,
    },
  });

  return response.data;
};

// Fetch beginner-friendly GitHub issues
export const fetchIssues = async (options = {}) => {
  const response = await api.get("/github/issues", {
    params: {
      per_page: options.perPage ?? 10,
      language: options.language ?? "Java",
      label: options.label ?? "good first issue",
      sort_by: options.sortBy ?? "created",
      keyword: options.keyword ?? "",
    },
  });

  return response.data;
};

// Fetch repository cache statistics
export const fetchCacheStats = async () => {
  const response = await api.get("/github/cache/stats");

  return response.data;
};