import { useReconStore } from "../store/useReconStore";

const TEXT = {
  "2xx": "text-ok",
  "3xx": "text-redirect",
  "4xx": "text-warn",
  "5xx": "text-err",
  dead: "text-dim",
};
const STRIP = {
  "2xx": "border-l-ok",
  "3xx": "border-l-redirect",
  "4xx": "border-l-warn",
  "5xx": "border-l-err",
  dead: "border-l-edge",
};

function classify(a) {
  if (a.status_code == null) return "dead";
  return (
    { 2: "2xx", 3: "3xx", 4: "4xx", 5: "5xx" }[
      Math.floor(a.status_code / 100)
    ] ?? "dead"
  );
}

const fmtDate = (iso) => (iso ? new Date(iso).toISOString().slice(0, 10) : "—");

export default function ResultsTable() {
  const { assets, toggleStar } = useReconStore();
  const stats = useReconStore((s) => s.stats);

  return (
    <div className="mt-4 border border-edge rounded-lg overflow-hidden">
      <table className="w-full text-sm border-collapse">
        <thead>
          <tr className="bg-panel text-dim text-xs uppercase tracking-wider">
            <th className="w-1" />
            <th className="text-left px-3 py-2.5">#</th>
            <th className="text-left px-3 py-2.5">subdomain</th>
            <th className="text-left px-3 py-2.5">status</th>
            <th className="text-right px-3 py-2.5">length</th>
            <th className="text-left px-3 py-2.5">ip</th>
            <th className="text-left px-3 py-2.5">port</th>
            <th className="text-left px-3 py-2.5">cdn</th>
            <th className="text-left px-3 py-2.5">title</th>
            <th className="text-left px-3 py-2.5">webserver</th>
            <th className="text-left px-3 py-2.5">technologies</th>
            <th className="text-left px-3 py-2.5">first seen</th>
            <th className="px-3 py-2.5">★</th>
          </tr>
        </thead>
        <tbody>
          {assets.map((a, i) => {
            const cls = classify(a);
            const isNew = a.first_scan_id === stats?.latest_scan_id;
            return (
              <tr
                key={a.id}
                className={`border-t border-edge border-l-2 ${STRIP[cls]} hover:bg-panel2 transition ${a.is_gone ? "opacity-40" : ""}`}
              >
                <td className="bg-panel/50" />
                <td className="px-3 py-2 text-dim">{i + 1}</td>
                <td className="px-3 py-2">
                  {a.subdomain}
                  {isNew && (
                    <span className="ml-2 px-1.5 py-0.5 rounded bg-new text-void text-[10px] font-bold">
                      NEW
                    </span>
                  )}
                </td>
                <td className={`px-3 py-2 font-bold ${TEXT[cls]}`}>
                  {a.status_code ?? "—"}
                </td>
                <td className="px-3 py-2 text-right text-dim">
                  {a.length?.toLocaleString() ?? "—"}
                </td>
                <td className="px-3 py-2 text-dim">{a.ip ?? "—"}</td>
                <td className="px-3 py-2 text-dim">{a.port ?? "—"}</td>
                <td className="px-3 py-2">
                  {a.cdn ? (
                    <span className="px-1.5 py-0.5 rounded border border-edge text-xs text-warn">
                      {a.cdn}
                    </span>
                  ) : (
                    "—"
                  )}
                </td>
                <td className="px-3 py-2 max-w-[220px] truncate">
                  {a.title ?? "—"}
                </td>
                <td className="px-3 py-2 text-dim">{a.webserver ?? "—"}</td>
                <td className="px-3 py-2">
                  <div className="flex flex-wrap gap-1 max-w-[260px]">
                    {(a.tech_stack || []).slice(0, 4).map((t) => (
                      <span
                        key={t}
                        className="px-1.5 py-0.5 rounded border border-edge text-[10px] text-dim"
                      >
                        {t}
                      </span>
                    ))}
                  </div>
                </td>
                <td className="px-3 py-2 text-dim text-xs">
                  {fmtDate(a.first_seen_at)}
                </td>
                <td className="px-3 py-2 text-center">
                  <button
                    onClick={() => toggleStar(a.id)}
                    className={
                      a.is_starred ? "text-new" : "text-edge hover:text-dim"
                    }
                  >
                    ★
                  </button>
                </td>
              </tr>
            );
          })}
          {assets.length === 0 && (
            <tr>
              <td colSpan={13} className="px-3 py-16 text-center text-dim">
                no assets — select a scope and hit ⚡ quick
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}
