import { useReconStore } from "../store/useReconStore";

const CARDS = [
  ["assets", "text-ink"],
  ["new", "text-new"],
  ["responding", "text-ok"],
  ["gone", "text-dim"],
  ["unique_ips", "text-redirect"],
  ["behind_cdn", "text-warn"],
  ["scans", "text-violet"],
];

export default function StatCards() {
  const stats = useReconStore((s) => s.stats);

  return (
    // TEACH POINT: gap-px + bg-edge = hairline dividers between cards, zero borders needed
    <div className="grid grid-cols-7 gap-px bg-edge border border-edge rounded-lg overflow-hidden mt-6">
      {CARDS.map(([key, color]) => (
        <div key={key} className="bg-panel px-4 py-3">
          <div className={`text-2xl font-bold ${color}`}>
            {stats?.[key] ?? 0}
          </div>
          <div className="text-[11px] text-dim uppercase tracking-wider">
            {key.replace("_", " ")}
          </div>
        </div>
      ))}
    </div>
  );
}
