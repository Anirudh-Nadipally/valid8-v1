import React, { useState } from 'react';
import { TestTube2, ArrowRight, AlertTriangle, TrendingUp, Loader2, Sparkles } from 'lucide-react';
import { api } from '../api';

export function ScenarioLab({ analysisId, persona }) {
    const [scenarioInput, setScenarioInput] = useState('');
    const [analysis, setAnalysis] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const runScenario = async () => {
        if (!scenarioInput.trim() || !analysisId) return;
        setLoading(true);
        setError(null);
        try {
            const result = await api.runScenario(analysisId, scenarioInput, persona);
            setAnalysis(result);
        } catch (err) {
            console.error("Scenario analysis failed:", err);
            setError("Failed to run scenario analysis. Please try again.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="max-w-4xl mx-auto space-y-8 animate-in fade-in duration-500">
            <div className="text-center space-y-2">
                <h2 className="text-3xl font-bold text-slate-900">Pivot Scenario Lab</h2>
                <p className="text-slate-500">Test "What If" scenarios before you commit resources.</p>
            </div>

            <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-8">
                <div className="mb-8">
                    <label className="block text-sm font-bold text-slate-700 mb-2">Describe a Scenario</label>
                    <div className="relative">
                        <textarea
                            value={scenarioInput}
                            onChange={(e) => setScenarioInput(e.target.value)}
                            className="w-full h-32 bg-slate-50 border border-slate-200 rounded-xl p-4 text-sm focus:ring-2 focus:ring-indigo-500 focus:bg-white transition-all resize-none"
                            placeholder="e.g., What if we switched from B2B to B2C? What if a major competitor lowers their price by 50%?"
                        />
                        <button
                            onClick={runScenario}
                            disabled={loading || !scenarioInput.trim()}
                            className="absolute right-4 bottom-4 bg-indigo-600 text-white px-4 py-2 rounded-lg text-xs font-bold flex items-center gap-2 hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                        >
                            {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Sparkles className="w-4 h-4" />}
                            Simulate Outcome
                        </button>
                    </div>
                    {error && <p className="text-xs text-rose-500 mt-2 font-medium">{error}</p>}
                </div>

                {analysis && (
                    <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                            <div className="bg-slate-50 rounded-xl p-5 border border-slate-200">
                                <h4 className="text-xs font-bold text-slate-500 uppercase mb-2 flex items-center gap-2"><TrendingUp className="w-4 h-4" /> Viability Score</h4>
                                <div className="text-3xl font-bold text-slate-900">{analysis.viabilityScore}/100</div>
                                <p className="text-xs text-slate-500 mt-1">Estimated success probability</p>
                            </div>
                            <div className="bg-rose-50 rounded-xl p-5 border border-rose-100">
                                <h4 className="text-xs font-bold text-rose-600 uppercase mb-2 flex items-center gap-2"><AlertTriangle className="w-4 h-4" /> Primary Risk</h4>
                                <p className="text-sm font-medium text-rose-900">{analysis.primaryRisk}</p>
                            </div>
                            <div className="bg-emerald-50 rounded-xl p-5 border border-emerald-100">
                                <h4 className="text-xs font-bold text-emerald-600 uppercase mb-2 flex items-center gap-2"><ArrowRight className="w-4 h-4" /> Key Opportunity</h4>
                                <p className="text-sm font-medium text-emerald-900">{analysis.keyOpportunity}</p>
                            </div>
                        </div>

                        <div className="bg-slate-900 rounded-xl p-6 text-slate-300">
                            <h3 className="text-white font-bold text-lg mb-3">Strategic Analysis</h3>
                            <p className="leading-relaxed">{analysis.analysis}</p>
                        </div>

                        <div>
                            <h4 className="font-bold text-slate-900 mb-3">Recommended Actions</h4>
                            <div className="space-y-2">
                                {analysis.actions && analysis.actions.map((action, i) => (
                                    <div key={i} className="flex items-start gap-3 p-3 bg-slate-50 rounded-lg border border-slate-100">
                                        <div className="bg-indigo-100 text-indigo-600 w-6 h-6 rounded-full flex items-center justify-center font-bold text-xs shrink-0 mt-0.5">{i + 1}</div>
                                        <p className="text-sm text-slate-700">{action}</p>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                )}

                {!analysis && !loading && (
                    <div className="text-center py-12 border-2 border-dashed border-slate-100 rounded-xl">
                        <TestTube2 className="w-12 h-12 text-slate-200 mx-auto mb-4" />
                        <h3 className="text-slate-400 font-bold">No Scenario Active</h3>
                        <p className="text-xs text-slate-300">Enter a hypothesis above to start the simulation engine.</p>
                    </div>
                )}
            </div>
        </div>
    );
}
