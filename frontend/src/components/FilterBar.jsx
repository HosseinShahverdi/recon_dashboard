import { useReconStore } from "../store/useReconStore";

const CHIPS = ["2xx", "3xx", "4xx", "5xx", "dead"];

function Toggle({ label, on, onClick }) {
  return (
    <button
      onClick={onClick}
      className="flex items-center gap-2 text-xs text-dim hover:text-ink"
    >
      <span
        className={`w-8 h-4 rounded-full relative transition ${on ? "bg-violet" : "bg-edge"}`}
      >
        <span
          className={`absolute top-0.5 w-3 h-3 rounded-full bg-ink transition-all ${on ? "left-4" : "left-0.5"}`}
        />
      </span>
      {label}
    </button>
  );
}

export default function FilterBar() {
  const { filters, setFilter, resetFilters, assets } = useReconStore();

  return (
    <div className="flex flex-wrap items-center gap-3 mt-4 text-sm">
      {CHIPS.map((c) => (
        <button
          key={c}
          onClick={() => setFilter({ status: filters.status === c ? null : c })}
          className={`px-3 py-1 rounded-full border text-xs transition ${
            filters.status === c
              ? "border-violet bg-violet/20 text-violet"
              : "border-edge text-dim hover:text-ink hover:border-dim"
          }`}
        >
          {c}
        </button>
      ))}

      <div className="w-px h-5 bg-edge" />

      <Toggle
        label="new only"
        on={filters.newOnly}
        onClick={() => setFilter({ newOnly: !filters.newOnly })}
      />
      <Toggle
        label="starred"
        on={filters.starred}
        onClick={() => setFilter({ starred: !filters.starred })}
      />
      <Toggle
        label="hide gone"
        on={filters.hideGone}
        onClick={() => setFilter({ hideGone: !filters.hideGone })}
      />

      <input
        value={filters.search}
        onChange={(e) => setFilter({ search: e.target.value })}
        placeholder="/ search host, title, ip…"
        className="ml-auto bg-panel border border-edge rounded px-3 py-1.5 text-xs w-64 placeholder:text-dim outline-none focus:border-violet"
      />

      <span className="text-dim text-xs">{assets.length} hosts</span>
      <button
        onClick={resetFilters}
        className="text-xs text-dim hover:text-ink border border-edge rounded px-2 py-1"
      >
        reset
      </button>
    </div>
  );
}
