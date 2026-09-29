import { useEffect } from "react";
import ParticleField from "./three/ParticleField";
import Topbar from "./components/TopBar";
import StatCards from "./components/StatCards";
import FilterBar from "./components/FilterBar";
import ResultsTable from "./components/ResultTabel";
import { useReconStore } from "./store/useReconStore";

export default function App() {
  const loadDomains = useReconStore((s) => s.loadDomains);
  useEffect(() => {
    loadDomains();
  }, [loadDomains]);

  return (
    <div className="min-h-screen">
      <ParticleField />
      <Topbar />
      <main className="max-w-[1600px] mx-auto px-6 pb-16">
        <StatCards />
        <FilterBar />
        <ResultsTable />
      </main>
    </div>
  );
}
