import React, { useState } from 'react';
import { ChevronDown, ChevronUp, ExternalLink, MessageSquare, Download } from 'lucide-react';

/**
 * PatternBadge - Hero component showing archetype + conviction dots
 */
export function PatternBadge({ pattern, onDiscuss, onExport }) {
    const glowColors = {
        emerald: 'from-emerald-900/50 to-slate-900 border-emerald-500/30',
        amber: 'from-amber-900/50 to-slate-900 border-amber-500/30',
        rose: 'from-rose-900/50 to-slate-900 border-rose-500/30',
        slate: 'from-slate-800 to-slate-900 border-slate-600/30'
    };

    const iconColors = {
        emerald: 'text-emerald-400',
        amber: 'text-amber-400',
        rose: 'text-rose-400',
        slate: 'text-slate-400'
    };

    return (
        <div className={`bg-gradient-to-br ${glowColors[pattern.glow_color] || glowColors.slate} rounded-2xl p-6 border shadow-xl`}>
            <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-4">
                    <span className="text-5xl">{pattern.icon}</span>
                    <div>
                        <div className="text-xs text-blue-400 uppercase tracking-wider mb-1">AI Verdict</div>
                        <div className="text-2xl font-bold text-white">{pattern.name.toUpperCase()}</div>
                        <div className={`${iconColors[pattern.glow_color]} mt-1`}>{pattern.tagline}</div>
                    </div>
                </div>
                <div className="text-right">
                    <div className="text-xs text-slate-400 mb-2">Conviction</div>
                    <div className="flex gap-1 justify-end">
                        {[1, 2, 3, 4].map(i => (
                            <div
                                key={i}
                                className={`w-3 h-3 rounded-full ${i <= pattern.conviction
                                        ? iconColors[pattern.glow_color]?.replace('text-', 'bg-') || 'bg-blue-400'
                                        : 'bg-slate-600'
                                    }`}
                            />
                        ))}
                    </div>
                    <div className="text-xs text-slate-500 mt-1">{pattern.conviction_label}</div>
                </div>
            </div>

            <div className="bg-black/20 rounded-lg p-4 mb-5">
                <p className="text-slate-300 text-sm leading-relaxed">{pattern.description}</p>
            </div>

            <div className="flex gap-3">
                <button
                    onClick={onDiscuss}
                    className="bg-blue-500 hover:bg-blue-600 px-5 py-2.5 rounded-lg flex items-center gap-2 text-sm font-medium text-white transition"
                >
                    <MessageSquare className="w-4 h-4" />
                    Discuss Strategy
                </button>
                <button
                    onClick={onExport}
                    className="bg-slate-700 hover:bg-slate-600 px-5 py-2.5 rounded-lg flex items-center gap-2 text-sm font-medium text-white transition"
                >
                    <Download className="w-4 h-4" />
                    Export Report
                </button>
            </div>
        </div>
    );
}

/**
 * SignalCard - Individual dimension with expandable details
 */
export function SignalCard({ signal, onClick }) {
    const [expanded, setExpanded] = useState(false);

    const levelStyles = {
        strong: {
            badge: 'text-green-400 bg-green-400/10',
            bar: 'bg-green-500'
        },
        moderate: {
            badge: 'text-yellow-400 bg-yellow-400/10',
            bar: 'bg-yellow-500'
        },
        weak: {
            badge: 'text-red-400 bg-red-400/10',
            bar: 'bg-red-500'
        }
    };

    const styles = levelStyles[signal.level] || levelStyles.moderate;

    return (
        <div
            className="bg-slate-900 rounded-xl p-5 border border-slate-800 hover:border-slate-700 transition cursor-pointer"
            onClick={() => setExpanded(!expanded)}
        >
            <div className="flex items-center justify-between mb-3">
                <span className="text-sm font-medium text-slate-300 capitalize">{signal.name}</span>
                <span className={`text-xs font-medium ${styles.badge} px-2 py-1 rounded capitalize`}>
                    {signal.level}
                </span>
            </div>

            <div className="text-lg font-semibold text-white mb-1">{signal.label}</div>

            {signal.value && (
                <div className="text-slate-400 text-sm mb-3">{signal.value}</div>
            )}

            <div className="h-1.5 bg-slate-800 rounded-full overflow-hidden">
                <div
                    className={`h-full ${styles.bar} rounded-full transition-all duration-500`}
                    style={{ width: `${signal.progress || 50}%` }}
                />
            </div>

            {signal.source && (
                <div className="text-xs text-slate-500 mt-2 flex items-center gap-1">
                    <span>📎</span> {signal.source}
                </div>
            )}

            {expanded && signal.details && (
                <div className="mt-4 pt-4 border-t border-slate-800 animate-in fade-in duration-200">
                    <div className="text-xs text-slate-400 mb-2">WHY THIS IS {signal.level.toUpperCase()}:</div>
                    <ul className="text-sm text-slate-300 space-y-1">
                        {signal.details.map((detail, i) => (
                            <li key={i} className="flex items-start gap-2">
                                <span className="text-green-500">✓</span>
                                {detail}
                            </li>
                        ))}
                    </ul>
                </div>
            )}
        </div>
    );
}

/**
 * MarketIntelCard - Live market data with sources
 */
export function MarketIntelCard({ marketData, trends }) {
    if (!marketData) return null;

    return (
        <div className="bg-slate-900 rounded-xl p-5 border border-slate-800">
            <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2">
                    <span>📊</span>
                    <span className="font-semibold text-white">Market Intel</span>
                </div>
                {marketData.source && (
                    <div className="flex items-center gap-1 text-xs text-green-400">
                        <span className="w-1.5 h-1.5 bg-green-400 rounded-full animate-pulse" />
                        Live
                    </div>
                )}
            </div>

            <div className="space-y-4">
                {marketData.tam && (
                    <div className="flex justify-between items-baseline">
                        <span className="text-slate-400 text-sm">TAM</span>
                        <div className="text-right">
                            <span className="text-xl font-bold text-white">{marketData.tam}</span>
                            {marketData.growth_rate && (
                                <span className="text-green-400 text-xs ml-2">↑ {marketData.growth_rate}</span>
                            )}
                        </div>
                    </div>
                )}

                {marketData.sam && (
                    <div className="flex justify-between items-baseline">
                        <span className="text-slate-400 text-sm">SAM</span>
                        <span className="font-semibold text-white">{marketData.sam}</span>
                    </div>
                )}

                {marketData.som && (
                    <div className="flex justify-between items-baseline">
                        <span className="text-slate-400 text-sm">SOM</span>
                        <span className="font-semibold text-white">{marketData.som}</span>
                    </div>
                )}

                {/* Simple trend bars */}
                {trends && trends.length > 0 && (
                    <div className="border-t border-slate-800 pt-4 mt-4">
                        <div className="text-xs text-slate-400 mb-2">Trends</div>
                        {trends.map((trend, i) => (
                            <div key={i} className="text-sm text-slate-300 flex items-center gap-2 mb-1">
                                <span className={trend.direction === 'up' ? 'text-green-400' : 'text-red-400'}>
                                    {trend.direction === 'up' ? '↑' : '↓'}
                                </span>
                                {trend.trend}
                            </div>
                        ))}
                    </div>
                )}

                {marketData.source && (
                    <div className="text-xs text-slate-500 flex flex-wrap gap-2 pt-2">
                        <span className="bg-slate-800 px-2 py-1 rounded">{marketData.source}</span>
                    </div>
                )}
            </div>
        </div>
    );
}

/**
 * CompetitorCard - Funded competitors with gaps
 */
export function CompetitorCard({ competitors, wedge }) {
    if (!competitors || competitors.length === 0) return null;

    return (
        <div className="bg-slate-900 rounded-xl p-5 border border-slate-800">
            <div className="flex items-center gap-2 mb-4">
                <span>⚔️</span>
                <span className="font-semibold text-white">Competitors</span>
            </div>

            <div className="space-y-3">
                {competitors.map((comp, i) => (
                    <div key={i} className="p-3 bg-slate-800/50 rounded-lg">
                        <div className="flex items-center justify-between mb-1">
                            <span className="font-medium text-white">{comp.name}</span>
                            {comp.funding_total && (
                                <span className="text-xs text-green-400">{comp.funding_total}</span>
                            )}
                        </div>
                        {comp.focus && (
                            <div className="text-xs text-slate-400 mb-2">{comp.focus}</div>
                        )}
                        {comp.gap && (
                            <div className="text-xs text-yellow-400">Gap: {comp.gap}</div>
                        )}
                    </div>
                ))}
            </div>

            {wedge && (
                <div className="mt-4 p-3 bg-blue-500/10 border border-blue-500/30 rounded-lg">
                    <div className="text-xs text-blue-400 font-medium mb-1">💡 Your Potential Wedge</div>
                    <div className="text-sm text-blue-200">{wedge}</div>
                </div>
            )}
        </div>
    );
}

/**
 * NextStepsCard - 3 actionable items with resources
 */
export function NextStepsCard({ steps, patternName }) {
    if (!steps || steps.length === 0) return null;

    return (
        <div className="bg-slate-900 rounded-xl p-6 border border-slate-800">
            <div className="flex items-center gap-2 mb-4">
                <span className="text-lg">🎯</span>
                <span className="font-semibold text-white">Your Next 3 Moves</span>
                <span className="text-xs text-slate-500 ml-auto">Based on: {patternName}</span>
            </div>

            <div className="space-y-4">
                {steps.map((step, i) => (
                    <div
                        key={i}
                        className="flex items-start gap-3 p-3 bg-slate-800/50 rounded-lg hover:bg-slate-800 transition"
                    >
                        <div className="w-6 h-6 rounded bg-blue-500/20 flex items-center justify-center text-blue-400 text-sm font-bold mt-0.5 shrink-0">
                            {step.number || i + 1}
                        </div>
                        <div className="flex-1">
                            <div className="font-medium text-white mb-1">{step.action}</div>
                            <div className="text-sm text-slate-400">{step.detail}</div>
                            {step.resources && step.resources.length > 0 && (
                                <div className="flex gap-2 mt-2">
                                    {step.resources.map((res, j) => (
                                        <button
                                            key={j}
                                            className="text-xs bg-slate-700 hover:bg-slate-600 px-3 py-1.5 rounded flex items-center gap-1 text-slate-300 transition"
                                        >
                                            {res.icon || '📋'} {res.label}
                                        </button>
                                    ))}
                                </div>
                            )}
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}

/**
 * HistoryTimeline - Pattern progression over time
 */
export function HistoryTimeline({ history, onSelect }) {
    if (!history || history.length === 0) {
        return (
            <div className="text-xs text-slate-400 italic pl-2">No history yet.</div>
        );
    }

    const glowColors = {
        emerald: 'border-emerald-500',
        amber: 'border-amber-500',
        rose: 'border-rose-500',
        blue: 'border-blue-500'
    };

    return (
        <div className="space-y-3">
            {history.map((item, i) => {
                const isFirst = i === 0;
                return (
                    <button
                        key={item.id}
                        onClick={() => onSelect(item)}
                        className={`w-full p-3 rounded-lg border-l-2 text-left transition ${isFirst
                                ? 'bg-slate-800/50 border-blue-500'
                                : 'bg-slate-800/30 border-slate-600 hover:bg-slate-800/50'
                            }`}
                    >
                        <div className="flex items-center gap-2 mb-1">
                            <span>{item.icon}</span>
                            <span className={`font-medium ${isFirst ? 'text-blue-400' : 'text-slate-400'}`}>
                                {item.archetype_name}
                            </span>
                            <div className="flex gap-0.5 ml-auto">
                                {[1, 2, 3, 4].map(j => (
                                    <div
                                        key={j}
                                        className={`w-2 h-2 rounded-full ${j <= item.conviction ? 'bg-blue-400' : 'bg-slate-600'
                                            }`}
                                    />
                                ))}
                            </div>
                        </div>
                        <div className="text-xs text-slate-500">
                            {item.title} • {new Date(item.timestamp).toLocaleDateString()}
                        </div>
                    </button>
                );
            })}
        </div>
    );
}

export default {
    PatternBadge,
    SignalCard,
    MarketIntelCard,
    CompetitorCard,
    NextStepsCard,
    HistoryTimeline
};
