import { ShieldAlert } from 'lucide-react';

interface SimulationBannerProps {
  simulationHeader: string;
  onOpenPanel: () => void;
  onDisarm: () => void;
}

export function SimulationBanner({
  simulationHeader,
  onOpenPanel,
  onDisarm,
}: SimulationBannerProps) {
  return (
    <div className="bg-amber-950/70 border-b border-amber-500/30 px-4 py-1.5 text-xs text-amber-200 flex items-center justify-between shrink-0">
      <div className="flex items-center gap-2 truncate">
        <ShieldAlert className="h-3.5 w-3.5 text-amber-400 animate-pulse shrink-0" />
        <span className="truncate">
          <strong>Failover Simulation Active:</strong>{' '}
          <code className="font-mono bg-amber-900/50 px-1.5 py-0.5 rounded text-amber-100 border border-amber-500/20 text-[11px]">
            X-Simulate-Failure: {simulationHeader}
          </code>
        </span>
      </div>
      <div className="flex items-center gap-2.5 shrink-0 ml-2">
        <button
          onClick={onOpenPanel}
          className="underline hover:text-white text-[11px]"
        >
          Change
        </button>
        <span className="text-amber-500/60">|</span>
        <button
          onClick={onDisarm}
          className="hover:text-white font-medium text-[11px]"
        >
          Disarm
        </button>
      </div>
    </div>
  );
}
