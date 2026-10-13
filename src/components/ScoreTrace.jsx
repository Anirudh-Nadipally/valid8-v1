import React from 'react';
import { ShieldCheck } from 'lucide-react';

const barColor = (s) => (s >= 80 ? 'bg-emerald-500' : s >= 50 ? 'bg-amber-500' : 'bg-rose-500');

// Every point on the scorecard, traced to the rule that produced it. No LLM involved in this view.
export const ScoreTrace = ({ trace }) => {
    if (!trace) {
        return <p className="text-sm text-slate-500">No score trace for this analysis. Run a new validation to see one.</p>;
    }
    return (
        <div className="space-y-5 animate-in fade-in duration-300">
            <div className="flex items-start gap-3 rounded-xl bg-indigo-50 border border-indigo-100 p-4">
                <ShieldCheck className="w-5 h-5 text-indigo-600 shrink-0 mt-0.5" />
                <p className="text-xs text-indigo-900 leading-relaxed">
                    <strong>Scored by rules, not by the model.</strong> The LLM only extracts facts from your idea.
                    Rules v{trace.rulesVersion} and the <code className="font-mono">{trace.weightProfile}</code> weights decide every point,
                    so the same input always gets the same score.
                </p>
            </div>

            <div className="space-y-4">
                {trace.dimensions.map((d) => (
                    <div key={d.key}>
                        <div className="flex items-baseline justify-between mb-1.5">
                            <span className="text-sm font-bold text-slate-800">{d.label}</span>
                            <span className="text-xs text-slate-500 tabular-nums">
                                <span className="text-base font-bold text-slate-900">{d.score}</span>/100 · weight {Math.round(d.weight * 100)}%
                            </span>
                        </div>
                        <div className="h-1.5 rounded-full bg-slate-100 overflow-hidden">
                            <div className={`h-full rounded-full ${barColor(d.score)}`} style={{ width: `${d.score}%` }} />
                        </div>
                        <div className="mt-2 flex flex-wrap gap-1.5">
                            {d.rules.length === 0 && <span className="text-[11px] text-slate-400">Base score, no rule fired</span>}
                            {d.rules.map((r) => (
                                <span key={r.id} title={r.reason}
                                    className={`inline-flex items-center gap-1 rounded-md border px-2 py-0.5 text-[11px] ${r.points < 0 ? 'border-rose-200 bg-rose-50 text-rose-700' : 'border-slate-200 bg-white text-slate-600'}`}>
                                    <span className="font-mono font-semibold">{r.id}</span>
                                    <span className="tabular-nums">{r.points > 0 ? `+${r.points}` : r.points}</span>
                                    <span className="text-slate-400">·</span>
                                    <span>{r.reason}</span>
                                </span>
                            ))}
                        </div>
                    </div>
                ))}
            </div>

            <div className="flex items-center justify-between border-t border-slate-100 pt-4 text-sm">
                <span className="text-slate-500">Weighted total</span>
                <span className="font-bold text-slate-900 tabular-nums">{trace.finalScore} · {trace.grade}</span>
            </div>
        </div>
    );
};
