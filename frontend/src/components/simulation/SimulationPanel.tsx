import { useState } from 'react';
import { X, ShieldAlert, Check } from 'lucide-react';
import { FailureSimulationPreset } from '../../types';

interface SimulationPanelProps {
  simulationHeader: string | null;
  onSetSimulationHeader: (val: string | null) => void;
  onClose: () => void;
}

export function SimulationPanel({
  simulationHeader,
  onSetSimulationHeader,
  onClose,
}: SimulationPanelProps) {
  const [customValue, setCustomValue] = useState(simulationHeader || '');

  const presets: Array<{
    id: FailureSimulationPreset;
    title: string;
    header: string;
    description: string;
  }> = [
    {
      id: 'key_1=429',
      title: 'Primary Failover (key_1=429)',
      header: 'key_1=429',
      description: 'Simulates rate-limit quota exhaustion on primary key_1 (NVIDIA NIM). Fails over to key_2 (Gemini).',
    },
    {
      id: 'key_1=429,key_2=500',
      title: 'Secondary Failover (key_1=429, key_2=500)',
      header: 'key_1=429,key_2=500',
      description: 'Simulates consecutive failures across key_1 and key_2, exercising multi-step fallback.',
    },
    {
      id: '*=429',
      title: 'Full Key Pool Exhaustion (*=429)',
      header: '*=429',
      description: 'Forces all keys to fail simultaneously, demonstrating clean HTTP 503 error handling.',
    },
  ];

  return (
    <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="w-full max-w-xl bg-[#171717] border border-[#262626] rounded-2xl p-5 shadow-2xl space-y-4">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-[#262626] pb-3">
          <div className="flex items-center gap-2">
            <div className="h-8 w-8 rounded-lg bg-amber-500/10 border border-amber-500/20 flex items-center justify-center text-amber-400">
              <ShieldAlert className="h-4 w-4" />
            </div>
            <div>
              <h3 className="text-sm font-semibold text-white">Failover Simulation & Chaos Testing</h3>
              <p className="text-xs text-neutral-400">
                Injects <code className="text-amber-300 font-mono">X-Simulate-Failure</code> header on outgoing requests.
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-neutral-400 hover:text-white hover:bg-[#212121] transition-colors"
          >
            <X className="h-4 w-4" />
          </button>
        </div>

        {/* Presets */}
        <div className="space-y-2">
          {presets.map((preset) => {
            const isSelected = simulationHeader === preset.header;
            return (
              <button
                key={preset.id}
                onClick={() => {
                  onSetSimulationHeader(preset.header);
                  setCustomValue(preset.header);
                }}
                className={`w-full text-left p-3 rounded-xl border transition-all ${
                  isSelected
                    ? 'bg-amber-950/30 border-amber-500/50 text-white'
                    : 'bg-[#121212] border-[#262626] text-neutral-300 hover:bg-[#1c1c1c] hover:border-[#383838]'
                }`}
              >
                <div className="flex items-center justify-between mb-1">
                  <span className="text-xs font-semibold text-neutral-200">
                    {preset.title}
                  </span>
                  {isSelected && (
                    <span className="h-4 w-4 rounded-full bg-amber-400 text-black flex items-center justify-center text-[10px]">
                      <Check className="h-3 w-3 stroke-[3]" />
                    </span>
                  )}
                </div>
                <div className="text-[11px] text-neutral-400 leading-relaxed">
                  {preset.description}
                </div>
              </button>
            );
          })}
        </div>

        {/* Custom Input */}
        <div className="space-y-1.5 pt-2 border-t border-[#262626]">
          <label className="text-xs font-medium text-neutral-300">
            Custom Header Value
          </label>
          <div className="flex gap-2">
            <input
              type="text"
              value={customValue}
              onChange={(e) => setCustomValue(e.target.value)}
              placeholder="e.g. key_1=502, key_2=429"
              className="flex-1 bg-[#0d0d0d] border border-[#262626] rounded-xl px-3 py-1.5 text-xs text-neutral-200 placeholder:text-neutral-500 focus:outline-none focus:border-[#4f4f4f] font-mono"
            />
            <button
              onClick={() => onSetSimulationHeader(customValue.trim() || null)}
              className="px-3 py-1.5 rounded-xl bg-[#262626] hover:bg-[#333333] text-xs text-neutral-200 font-medium transition-colors"
            >
              Apply
            </button>
          </div>
        </div>

        {/* Actions */}
        <div className="flex items-center justify-between pt-2 border-t border-[#262626]">
          <button
            onClick={() => {
              onSetSimulationHeader(null);
              setCustomValue('');
            }}
            className="text-xs text-neutral-400 hover:text-white transition-colors"
          >
            Disarm Simulation
          </button>
          <button
            onClick={onClose}
            className="px-4 py-1.5 rounded-lg bg-white text-black hover:bg-neutral-200 text-xs font-medium transition-colors"
          >
            Done
          </button>
        </div>
      </div>
    </div>
  );
}
