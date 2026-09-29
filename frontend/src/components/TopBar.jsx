import { useState } from "react";
import { useReconStore } from "../store/useReconStore";

export default function Topbar() {
  const {
    domains,
    currentDomain,
    selectDomain,
    addDomain,
    runScan,
    scanning,
    scanState,
  } = useReconStore();
  const [name, setName] = useState("");

  return (
    <header className="sticky top-0 z-20 border-b border-edge bg-void/80 backdrop-blur">
      <div className="max-w-[1600px] mx-auto px-6 h-14 flex items-center gap-4">
        <div className="text-violet font-bold tracking-[0.2em]">RECON//OS</div>

        <select
          value={currentDomain ?? ""}
          onChange={(e) => selectDomain(Number(e.target.value))}
          className="bg-panel border border-edge rounded px-3 py-1.5 text-sm outline-none focus:border-violet"
        >
          <option value="" disabled>
            select scope…
          </option>
          {domains.map((d) => (
            <option key={d.id} value={d.id}>
              {d.name}
            </option>
          ))}
        </select>

        <form
          onSubmit={(e) => {
            e.preventDefault();
            if (name.trim()) {
              addDomain(name.trim());
              setName("");
            }
          }}
        >
          <input
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="+ new scope (example.com)"
            className="bg-panel border border-edge rounded px-3 py-1.5 text-sm w-56 placeholder:text-dim outline-none focus:border-violet"
          />
        </form>

        <div className="ml-auto flex items-center gap-2">
          {scanning && (
            <span className="text-new text-xs animate-pulse">
              ● scanning… {scanState?.status}
            </span>
          )}
          <button
            onClick={() => runScan("quick")}
            disabled={scanning || !currentDomain}
            className="px-4 py-1.5 rounded bg-violet/15 text-violet border border-violet/40 text-sm hover:bg-violet/25 disabled:opacity-40"
          >
            ⚡ quick
          </button>
          <button
            onClick={() => runScan("deep")}
            disabled={scanning || !currentDomain}
            className="px-4 py-1.5 rounded bg-new/10 text-new border border-new/40 text-sm hover:bg-new/20 disabled:opacity-40"
          >
            🔥 deep
          </button>
        </div>
      </div>
    </header>
  );
}
