const BASE = "http://localhost:8000/api/v1";

async function req(path, options = {}) {
  const res = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) throw new Error(`${res.status}: ${await res.text()}`);
  return res.json();
}

export const api = {
  listDomains: () => req("/domains/"),
  addDomain: (name) =>
    req("/domains/", { method: "POST", body: JSON.stringify({ name }) }),
  toolHealth: () => req("/tools/health"),
  startScan: (domain_id, mode) =>
    req("/scans/", {
      method: "POST",
      body: JSON.stringify({ domain_id, mode }),
    }),
  scanStatus: (id) => req(`/scans/${id}`),
  assets: (params) => req(`/assets/?${new URLSearchParams(params)}`),
  stats: (domainId) => req(`/stats/${domainId}`),
  toggleStar: (id) => req(`/assets/${id}/star`, { method: "PATCH" }),
};
