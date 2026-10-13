const API_BASE_URL = "/api";

export const api = {
  analyze: async (formData) => {
    const response = await fetch(`${API_BASE_URL}/analyze`, {
      method: "POST",
      body: formData,
    });
    if (!response.ok) throw new Error("Analysis failed");
    return response.json();
  },

  getHistory: async () => {
    const response = await fetch(`${API_BASE_URL}/history`);
    if (!response.ok) throw new Error("Failed to fetch history");
    return response.json();
  },

  chat: async (analysisId, message, persona) => {
    const response = await fetch(`${API_BASE_URL}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ analysisId, message, persona }),
    });
    if (!response.ok) throw new Error("Chat failed");
    return response.json();
  },

  runScenario: async (analysisId, scenario, persona) => {
    const response = await fetch(`${API_BASE_URL}/scenario`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ analysisId, scenario, persona }),
    });
    if (!response.ok) throw new Error("Scenario analysis failed");
    return response.json();
  },

  pitchArchitect: async (analysisId) => {
    const response = await fetch(`${API_BASE_URL}/pitch-architect`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ analysisId }),
    });
    if (!response.ok) throw new Error("Pitch Architect failed");
    return response.json();
  },

  legalCheck: async (analysisId) => {
    const response = await fetch(`${API_BASE_URL}/legal-check`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ analysisId }),
    });
    if (!response.ok) throw new Error("Legal check failed");
    return response.json();
  },

  generateNames: async (problem, solution) => {
    const response = await fetch(`${API_BASE_URL}/generate-names`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ problem, solution }),
    });
    if (!response.ok) throw new Error("Name generation failed");
    return response.json();
  },

  analyzeCompetitor: async (analysisId, competitorName, persona) => {
    const response = await fetch(`${API_BASE_URL}/competitor-weakness`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ analysisId, competitorName, persona }),
    });
    if (!response.ok) throw new Error("Competitor analysis failed");
    return response.json();
  },

  generateMarketIntel: async (analysisId) => {
    const response = await fetch(`${API_BASE_URL}/market-intel`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ analysisId }),
    });
    if (!response.ok) throw new Error("Market Intel generation failed");
    return response.json();
  },

  generateLeanCanvas: async (analysisId) => {
    const response = await fetch(`${API_BASE_URL}/lean-canvas`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ analysisId }),
    });
    if (!response.ok) throw new Error("Lean Canvas generation failed");
    return response.json();
  },

  generateStrategyFlow: async (analysisId, section) => {
    const response = await fetch(`${API_BASE_URL}/strategy-flow`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ analysisId, section }),
    });
    if (!response.ok) throw new Error("Strategy Flow generation failed");
    return response.json();
  },

  getReportUrl: (id) => `${API_BASE_URL}/report/${id}`
};
