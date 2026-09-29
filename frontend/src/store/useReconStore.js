import { create } from "zustand";
import { api } from "../services/api";

export const useReconStore = create((set, get) => ({
  domains: [],
  currentDomain: null,
  assets: [],
  stats: null,
  filters: {
    status: null,
    newOnly: false,
    starred: false,
    hideGone: true,
    search: "",
  },
  scanning: false,
  scanState: null,

  loadDomains: async () => {
    const domains = await api.listDomains();
    set({ domains });
    if (domains.length && !get().currentDomain)
      get().selectDomain(domains[0].id);
  },

  addDomain: async (name) => {
    const d = await api.addDomain(name);
    set((s) => ({ domains: [...s.domains, d], currentDomain: d.id }));
    get().refresh();
  },

  selectDomain: (id) => {
    set({ currentDomain: id });
    get().refresh();
  },

  setFilter: (patch) => {
    set((s) => ({ filters: { ...s.filters, ...patch } }));
    get().refresh();
  },

  resetFilters: () => {
    set({
      filters: {
        status: null,
        newOnly: false,
        starred: false,
        hideGone: true,
        search: "",
      },
    });
    get().refresh();
  },

  refresh: async () => {
    const { currentDomain, filters } = get();
    if (!currentDomain) return;

    const params = {
      domain_id: currentDomain,
      hide_gone: String(filters.hideGone),
    };
    if (filters.status) params.status = filters.status;
    if (filters.newOnly) params.is_new = "true";
    if (filters.search) params.search = filters.search;

    let rows = await api.assets(params);
    if (filters.starred) rows = rows.filter((r) => r.is_starred); // client-side for now

    const stats = await api.stats(currentDomain);
    set({ assets: rows, stats });
  },

  toggleStar: async (id) => {
    await api.toggleStar(id);
    get().refresh();
  },

  runScan: async (mode) => {
    const { currentDomain } = get();
    if (!currentDomain) return;
    set({ scanning: true });

    const { scan_id } = await api.startScan(currentDomain, mode);

    // TEACH POINT: polling every 3s for now. Phase 6 replaces this with a
    // WebSocket push so the UI reacts the instant the server progresses.
    const poll = setInterval(async () => {
      const st = await api.scanStatus(scan_id);
      set({ scanState: st });
      if (st.status === "completed" || st.status === "failed") {
        clearInterval(poll);
        set({ scanning: false, scanState: null });
        get().refresh();
      }
    }, 3000);
  },
}));
