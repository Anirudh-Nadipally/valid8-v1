import React, { useState, useEffect } from 'react';
import { Sparkles, Loader2, ArrowRight } from 'lucide-react';
import {
    PatternBadge, SignalCard, MarketIntelCard,
    CompetitorCard, NextStepsCard, HistoryTimeline
} from './index';

export function AnalysisDashboard({ idea, onAnalyze, onBack, initialAnalysis }) {
    const [analysis, setAnalysis] = useState(initialAnalysis || null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [history, setHistory] = useState([]);

    // Load history on mount
    useEffect(() => {
        fetchHistory();
    }, []);

    const fetchHistory = async () => {
        try {
            const res = await fetch('/api/v4/history');
            if (res.ok) {
                const data = await res.json();
                setHistory(data);
            }
        } catch (e) {
            console.error("Failed to load history", e);
        }
    };

    const handleAnalyze = async () => {
        setLoading(true);
        setError(null);
        try {
            const res = await fetch('/api/v4/analyze', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    title: idea.title,
                    problem: idea.problem,
                    solution: idea.solution,
                    targetAudience: idea.targetAudience,
                    uniqueValue: idea.uniqueValue,
                    geography: 'global',
                    includeGrounding: true
                })
            });

            if (!res.ok) {
                const err = await res.json();
                throw new Error(err.detail || 'Analysis failed');
            }

            const data = await res.json();
            setAnalysis(data);
            fetchHistory(); // Refresh history
            if (onAnalyze) onAnalyze(data);
        } catch (e) {
            setError(e.message);
        } finally {
            setLoading(false);
        }
    };

    // If no analysis yet, show empty state or auto-trigger if idea provided
    useEffect(() => {
        if (!analysis && idea.title && idea.problem && !loading) {
            // Optional: Auto-trigger? Maybe wait for user.
        }
    }, []);

    if (!analysis && !loading && !error) {
        return (
            <div className="flex flex-col items-center justify-center h-full p-12 text-center text-slate-500">
                <Sparkles className="w-16 h-16 text-indigo-200 mb-6" />
                <h2 className="text-2xl font-bold text-slate-800 mb-3">Ready to Validate</h2>
                <p className="max-w-md mb-8">
                    We'll analyze "{idea.title}" using our new 8-Archetype Pattern System combined with live market intelligence.
                </p>
                <button
                    onClick={handleAnalyze}
                    className="bg-indigo-600 hover:bg-indigo-700 text-white px-8 py-4 rounded-xl font-bold text-lg flex items-center gap-2 shadow-lg hover:shadow-xl transition-all"
                >
                    <Sparkles className="w-5 h-5" />
                    Run V4 Analysis
                </button>
            </div>
        );
    }

    if (loading) {
        return (
            <div className="flex flex-col items-center justify-center h-full p-12 text-center">
                <div className="relative">
                    <div className="w-20 h-20 border-4 border-slate-200 border-t-indigo-600 rounded-full animate-spin"></div>
                    <div className="absolute top-0 left-0 w-full h-full flex items-center justify-center">
                        <Sparkles className="w-8 h-8 text-indigo-600 animate-pulse" />
                    </div>
                </div>
                <h2 className="text-xl font-bold text-slate-800 mt-8 mb-2">Analyzing Patterns...</h2>
                <div className="space-y-1 text-slate-500 text-sm">
                    <p className="animate-pulse duration-1000 delay-0">• Classifying Archetype</p>
                    <p className="animate-pulse duration-1000 delay-300">• Searching Market Data (Live)</p>
                    <p className="animate-pulse duration-1000 delay-500">• Checking Competitors</p>
                    <p className="animate-pulse duration-1000 delay-700">• Calculating Conviction</p>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="flex flex-col items-center justify-center h-full p-12 text-center">
                <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mb-6">
                    <span className="text-2xl">⚠️</span>
                </div>
                <h2 className="text-xl font-bold text-slate-800 mb-2">Analysis Failed</h2>
                <p className="text-red-500 mb-6">{error}</p>
                <button
                    onClick={handleAnalyze}
                    className="bg-slate-800 text-white px-6 py-2 rounded-lg font-medium"
                >
                    Try Again
                </button>
            </div>
        );
    }

    return (
        <div className="flex h-full bg-slate-50">
            {/* Main Content */}
            <div className="flex-1 overflow-y-auto custom-scrollbar">
                {/* Header / Hero */}
                <div className="p-8 pb-0 max-w-5xl mx-auto mb-8">
                    <div className="flex items-center gap-2 text-sm text-slate-400 mb-4">
                        <span className="cursor-pointer hover:text-indigo-600" onClick={onBack}>Home</span>
                        <ArrowRight className="w-3 h-3" />
                        <span>Analysis Results</span>
                    </div>

                    {/* Pattern Badge (Hero) */}
                    <PatternBadge
                        pattern={analysis.pattern}
                        onDiscuss={() => console.log('Discuss')}
                        onExport={() => console.log('Export')}
                    />
                </div>

                {/* Dashboard Grid */}
                <div className="p-8 pt-0 max-w-5xl mx-auto grid grid-cols-1 lg:grid-cols-3 gap-6 pb-24">

                    {/* Left Col: Signals */}
                    <div className="lg:col-span-2 space-y-6">
                        <h3 className="font-bold text-slate-700 flex items-center gap-2">
                            <span>📡</span> Validation Signals
                        </h3>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            {analysis.signals.map((signal, i) => (
                                <SignalCard key={i} signal={signal} />
                            ))}
                        </div>

                        {/* Next Steps */}
                        <NextStepsCard
                            steps={analysis.next_steps}
                            patternName={analysis.pattern.name}
                        />
                    </div>

                    {/* Right Col: Market Intel */}
                    <div className="space-y-6">
                        <h3 className="font-bold text-slate-700 flex items-center gap-2">
                            <span>🌍</span> Market Intelligence
                        </h3>

                        <MarketIntelCard
                            marketData={analysis.market_intel}
                            trends={analysis.trends}
                        />

                        <CompetitorCard
                            competitors={analysis.competitors}
                            wedge={analysis.idea?.uniqueValue}
                        />

                        {/* Metadata */}
                        <div className="text-xs text-slate-400 mt-8 text-center">
                            Analyzed in {analysis.processing_time_ms}ms<br />
                            Data sources: {analysis.sources?.length || 0} external sources
                        </div>
                    </div>
                </div>
            </div>

            {/* Right Sidebar: History */}
            <div className="w-80 border-l border-slate-200 bg-white p-6 overflow-y-auto hidden xl:block">
                <h3 className="font-bold text-slate-800 mb-6 flex items-center gap-2">
                    <span>📚</span> Pattern History
                </h3>
                <HistoryTimeline
                    history={history}
                    onSelect={(item) => console.log('Fetch item', item.id)}
                />
            </div>
        </div>
    );
}

// Add this to your style sheet or Tailwind config if missing
// .custom-scrollbar::-webkit-scrollbar { width: 6px; }
// .custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
// .custom-scrollbar::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 10px; }
// .custom-scrollbar::-webkit-scrollbar-thumb:hover { background: #94a3b8; }
