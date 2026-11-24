import { useState } from 'react';
import { ShieldAlert, Zap, AlertTriangle, XCircle, CheckCircle2, ServerCrash, X } from 'lucide-react';
import { FailureSimulationPreset } from '../types';

interface SimulationPanelProps {
  simulationHeader: string | null;
  onSetSimulationHeader: (value: string | null) => void;
  onClose: () => void;
}

export function SimulationPanel({
  simulationHeader,
  onSetSimulationHeader,
  onClose,
}: SimulationPanelProps) {
  const [customValue, setCustomValue] = useState(simulationHeader || '');

  const presets: { id: FailureSimulationPreset; label: string; header: string | null; desc: string; icon: 'check' | 'zap' | 'exhaust' | 'crash' }[] = [
    {
      id: 'none',
      label: 'Live Inference (Default)',
      header: null,
      desc: 'Normal production traffic. No artificial failure injection.',
      icon: 'check',
    },
    {
      id: 'key_1=429',
      label: 'Primary Failover (key_1=429)',
      header: 'key_1=429',
      desc: 'Simulates HTTP 429 Rate Limit on primary NVIDIA key. Verifies automatic instant failover to secondary Google Gemini key.',
      icon: 'zap',
    },
    {
      id: 'key_1=429,key_2=500',
      label: 'Cascading Fallback (429 & 500)',
      header: 'key_1=429,key_2=500',
      desc: 'Simulates cascading provider failures across multiple keys in the pool.',
      icon: 'crash',
    },
    {
      id: '*=429',
      label: 'Pool Exhaustion (*=429)',
      header: '*=429',
      desc: 'Simulates all keys exhausted. Verifies clean HTTP 503 "all providers unavailable" handling without database pollution.',
      icon: 'exhaust',
    },
  ];

  const handleSelectPreset = (header: string | null) => {
    onSetSimulationHeader(header);
    if (header) {
      setCustomValue(header);
    } else {
      setCustomValue('');
    }
  };

  const handleApplyCustom = () => {
    const trimmed = customValue.trim();
    onSetSimulationHeader(trimmed.length > 0 ? trimmed : null);
  };

  return (
    <div className="bg-slate-900/98 border-b border-amber-500/30 p-4 shadow-2xl transition-all animate-in fade-in slide-in-from-top-2">
      <div className="max-w-6xl mx-auto space-y-3.5">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2.5">
            <div className="h-7 w-7 rounded-lg bg-amber-500/20 border border-amber-500/30 flex items-center justify-center text-amber-400">
              <ShieldAlert className="h-4 w-4" />
            </div>
            <div>
              <h3 className="text-sm font-semibold text-slate-100 flex items-center gap-2">
                Failover & Chaos Testing Panel
                <span className="text-[10px] font-mono font-medium px-2 py-0.5 rounded-full bg-amber-500/10 text-amber-300 border border-amber-500/30">
                  PRD Section 4
                </span>
              </h3>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-slate-200 p-1.5 rounded-lg hover:bg-slate-800 transition-colors"
            title="Close Panel"
          >
            <X className="h-4 w-4" />
          </button>
        </div>

        <p className="text-xs text-slate-400 leading-relaxed max-w-3xl">
          Injects artificial HTTP status codes via the <code className="font-mono text-amber-300 bg-slate-950 px-1 py-0.5 rounded border border-slate-800">X-Simulate-Failure</code> header.
          Use this controller during the demo to show seamless real-time failover without depleting actual provider quota limits.
        </p>

        {/* Preset Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
          {presets.map((preset) => {
            const isSelected = simulationHeader === preset.header;
            return (
              <button
                key={preset.id}
                onClick={() => handleSelectPreset(preset.header)}
                className={`text-left p-3.5 rounded-xl border text-xs transition-all flex flex-col justify-between ${
                  isSelected
                    ? 'bg-amber-500/15 border-amber-500 text-slate-100 ring-2 ring-amber-500/30 shadow-lg shadow-amber-950/20'
                    : 'bg-slate-950/60 border-slate-800 text-slate-300 hover:bg-slate-850 hover:border-slate-700'
                }`}
              >
                <div>
                  <div className="flex items-center justify-between mb-1.5">
                    <span className="font-semibold flex items-center gap-1.5 text-xs">
                      {preset.icon === 'check' && <CheckCircle2 className="h-3.5 w-3.5 text-emerald-400" />}
                      {preset.icon === 'zap' && <Zap className="h-3.5 w-3.5 text-amber-400" />}
                      {preset.icon === 'crash' && <ServerCrash className="h-3.5 w-3.5 text-orange-400" />}
                      {preset.icon === 'exhaust' && <XCircle className="h-3.5 w-3.5 text-rose-400" />}
                      {preset.label}
                    </span>
                    {isSelected && (
                      <span className="h-2 w-2 rounded-full bg-amber-400 animate-pulse" />
                    )}
                  </div>
                  <p className="text-[11px] text-slate-400 leading-normal">{preset.desc}</p>
                </div>

                {preset.header && (
                  <div className="mt-2.5 pt-2 border-t border-slate-800/80 font-mono text-[10px] text-amber-300/90 truncate">
                    X-Simulate-Failure: {preset.header}
                  </div>
                )}
              </button>
            );
          })}
        </div>

        {/* Custom Header Input & Actions */}
        <div className="pt-1 flex flex-wrap items-center gap-2">
          <span className="text-xs text-slate-400 font-mono">Custom Header:</span>
          <input
            type="text"
            value={customValue}
            onChange={(e) => setCustomValue(e.target.value)}
            placeholder="e.g. key_1=502 or key_1=429,key_2=503"
            className="flex-1 min-w-[220px] bg-slate-950 border border-slate-800 rounded-lg px-3 py-1.5 text-xs text-slate-200 font-mono placeholder:text-slate-600 focus:outline-none focus:border-amber-500"
          />
          <button
            onClick={handleApplyCustom}
            className="text-xs px-3 py-1.5 rounded-lg bg-amber-600 hover:bg-amber-500 text-white font-medium transition-colors"
          >
            Set Custom
          </button>
          {simulationHeader && (
            <button
              onClick={() => handleSelectPreset(null)}
              className="text-xs px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 font-medium transition-colors"
            >
              Reset to Live
            </button>
          )}
        </div>

        {/* Active Simulation Status Alert */}
        {simulationHeader && (
          <div className="flex items-center gap-2 bg-amber-500/10 border border-amber-500/30 rounded-lg px-3 py-2 text-xs text-amber-300 animate-pulse">
            <AlertTriangle className="h-4 w-4 shrink-0 text-amber-400" />
            <span>
              <strong>Chaos Hook Armed:</strong> Next chat request will send{' '}
              <code className="font-mono bg-amber-950/80 px-1.5 py-0.5 rounded border border-amber-500/40 text-amber-200">
                X-Simulate-Failure: {simulationHeader}
              </code>
            </span>
          </div>
        )}
      </div>
    </div>
  );
}
