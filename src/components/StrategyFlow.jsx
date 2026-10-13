import React, { useState } from 'react';
import { Target, Flag, Calendar, CheckCircle2, Plus, Trash2, ArrowRight, Save, Sparkles, Loader2 } from 'lucide-react';
import { api } from '../api';

export function StrategyFlow({ idea, analysisId }) {
    const [activeTab, setActiveTab] = useState('vision');
    const [loading, setLoading] = useState(false);

    const [vision, setVision] = useState({
        mission: '',
        vision: '',
        values: ['']
    });
    const [okrs, setOkrs] = useState([
        { id: 1, objective: 'Launch MVP', keyResults: ['Complete core features', 'Onboard 10 beta users'] }
    ]);
    const [roadmap, setRoadmap] = useState([
        { id: 1, phase: 'Phase 1: Validation', items: ['Customer Interviews', 'Landing Page', 'Pre-sales'], status: 'current' },
        { id: 2, phase: 'Phase 2: Build', items: ['MVP Development', 'Internal Testing'], status: 'upcoming' },
        { id: 3, phase: 'Phase 3: Launch', items: ['Public Beta', 'Marketing Campaign'], status: 'upcoming' }
    ]);

    const addValue = () => setVision({ ...vision, values: [...vision.values, ''] });
    const updateValue = (index, val) => {
        const newValues = [...vision.values];
        newValues[index] = val;
        setVision({ ...vision, values: newValues });
    };
    const removeValue = (index) => {
        const newValues = vision.values.filter((_, i) => i !== index);
        setVision({ ...vision, values: newValues });
    };

    const addOkr = () => setOkrs([...okrs, { id: Date.now(), objective: '', keyResults: [''] }]);
    const updateOkr = (id, field, val) => setOkrs(okrs.map(o => o.id === id ? { ...o, [field]: val } : o));
    const addKeyResult = (okrId) => setOkrs(okrs.map(o => o.id === okrId ? { ...o, keyResults: [...o.keyResults, ''] } : o));
    const updateKeyResult = (okrId, index, val) => setOkrs(okrs.map(o => o.id === okrId ? { ...o, keyResults: o.keyResults.map((k, i) => i === index ? val : k) } : o));

    const handleGenerate = async () => {
        if (!analysisId) return;
        setLoading(true);
        try {
            const result = await api.generateStrategyFlow(analysisId, activeTab);

            if (activeTab === 'vision') {
                setVision(prev => ({
                    ...prev,
                    vision: result.vision || prev.vision,
                    mission: result.mission || prev.mission
                }));
            } else if (activeTab === 'okrs') {
                if (result.objectives) {
                    setOkrs(result.objectives.map((o, i) => ({
                        id: Date.now() + i,
                        objective: o.objective,
                        keyResults: o.keyResults || []
                    })));
                }
            } else if (activeTab === 'roadmap') {
                if (result.roadmap) {
                    setRoadmap(result.roadmap.map((p, i) => ({
                        id: Date.now() + i,
                        phase: p.phase,
                        items: p.milestones || [],
                        status: i === 0 ? 'current' : 'upcoming'
                    })));
                }
            }
        } catch (err) {
            console.error("Failed to generate strategy", err);
            alert("Failed to generate strategy. Please try again.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="max-w-5xl mx-auto space-y-8 animate-in fade-in duration-500">
            <div className="text-center space-y-2 relative">
                <h2 className="text-3xl font-bold text-slate-900">Strategy Flow</h2>
                <p className="text-slate-500">Define your North Star and map the path to success.</p>
                <button
                    onClick={handleGenerate}
                    disabled={loading || !analysisId}
                    className="absolute right-0 top-0 bg-indigo-600 text-white px-4 py-2 rounded-lg text-xs font-bold flex items-center gap-2 hover:bg-indigo-700 disabled:opacity-50 transition-all shadow-lg shadow-indigo-200"
                >
                    {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Sparkles className="w-4 h-4" />}
                    Auto-Generate {activeTab === 'okrs' ? 'OKRs' : activeTab === 'roadmap' ? 'Roadmap' : 'Vision'}
                </button>
            </div>

            <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
                <div className="flex border-b border-slate-200 bg-slate-50/50">
                    <button onClick={() => setActiveTab('vision')} className={`flex-1 py-4 text-sm font-bold border-b-2 transition-colors ${activeTab === 'vision' ? 'border-indigo-600 text-indigo-600' : 'border-transparent text-slate-500 hover:text-slate-800'}`}>Vision & Mission</button>
                    <button onClick={() => setActiveTab('okrs')} className={`flex-1 py-4 text-sm font-bold border-b-2 transition-colors ${activeTab === 'okrs' ? 'border-indigo-600 text-indigo-600' : 'border-transparent text-slate-500 hover:text-slate-800'}`}>Objectives (OKRs)</button>
                    <button onClick={() => setActiveTab('roadmap')} className={`flex-1 py-4 text-sm font-bold border-b-2 transition-colors ${activeTab === 'roadmap' ? 'border-indigo-600 text-indigo-600' : 'border-transparent text-slate-500 hover:text-slate-800'}`}>Strategic Roadmap</button>
                </div>

                <div className="p-8">
                    {activeTab === 'vision' && (
                        <div className="space-y-8 animate-in fade-in duration-300">
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                                <div className="space-y-3">
                                    <label className="block text-xs font-bold text-slate-400 uppercase tracking-wider">Mission Statement</label>
                                    <textarea
                                        value={vision.mission}
                                        onChange={(e) => setVision({ ...vision, mission: e.target.value })}
                                        className="w-full h-32 bg-slate-50 border border-slate-200 rounded-xl p-4 text-sm focus:ring-2 focus:ring-indigo-500 focus:bg-white transition-all resize-none"
                                        placeholder="What do you do, for whom, and why? (e.g., To organize the world's information...)"
                                    />
                                </div>
                                <div className="space-y-3">
                                    <label className="block text-xs font-bold text-slate-400 uppercase tracking-wider">Vision Statement</label>
                                    <textarea
                                        value={vision.vision}
                                        onChange={(e) => setVision({ ...vision, vision: e.target.value })}
                                        className="w-full h-32 bg-slate-50 border border-slate-200 rounded-xl p-4 text-sm focus:ring-2 focus:ring-indigo-500 focus:bg-white transition-all resize-none"
                                        placeholder="What does the world look like if you succeed? (e.g., A computer on every desk...)"
                                    />
                                </div>
                            </div>

                            <div className="space-y-4">
                                <div className="flex items-center justify-between">
                                    <label className="block text-xs font-bold text-slate-400 uppercase tracking-wider">Core Values</label>
                                    <button onClick={addValue} className="text-xs font-bold text-indigo-600 hover:text-indigo-700 flex items-center gap-1"><Plus className="w-3 h-3" /> Add Value</button>
                                </div>
                                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                                    {vision.values.map((val, idx) => (
                                        <div key={idx} className="relative group">
                                            <input
                                                value={val}
                                                onChange={(e) => updateValue(idx, e.target.value)}
                                                className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 text-sm focus:ring-2 focus:ring-indigo-500 focus:bg-white transition-all"
                                                placeholder={`Value #${idx + 1}`}
                                            />
                                            <button onClick={() => removeValue(idx)} className="absolute right-2 top-1/2 -translate-y-1/2 text-slate-300 hover:text-rose-500 opacity-0 group-hover:opacity-100 transition-opacity">
                                                <Trash2 className="w-4 h-4" />
                                            </button>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        </div>
                    )}

                    {activeTab === 'okrs' && (
                        <div className="space-y-6 animate-in fade-in duration-300">
                            {okrs.map((okr, idx) => (
                                <div key={okr.id} className="bg-slate-50 rounded-xl border border-slate-200 p-6 space-y-4">
                                    <div className="flex items-start gap-4">
                                        <div className="bg-indigo-100 text-indigo-700 w-8 h-8 rounded-lg flex items-center justify-center font-bold shrink-0">{idx + 1}</div>
                                        <div className="flex-1 space-y-4">
                                            <input
                                                value={okr.objective}
                                                onChange={(e) => updateOkr(okr.id, 'objective', e.target.value)}
                                                className="w-full bg-white border border-slate-200 rounded-lg px-4 py-2 font-bold text-slate-900 placeholder:font-normal focus:ring-2 focus:ring-indigo-500 transition-all"
                                                placeholder="Objective: What do you want to achieve?"
                                            />
                                            <div className="space-y-2 pl-4 border-l-2 border-slate-200">
                                                {okr.keyResults.map((kr, kIdx) => (
                                                    <div key={kIdx} className="flex items-center gap-2">
                                                        <Target className="w-4 h-4 text-slate-400" />
                                                        <input
                                                            value={kr}
                                                            onChange={(e) => updateKeyResult(okr.id, kIdx, e.target.value)}
                                                            className="flex-1 bg-transparent border-b border-transparent hover:border-slate-300 focus:border-indigo-500 px-2 py-1 text-sm outline-none transition-colors"
                                                            placeholder="Key Result: How will you measure it?"
                                                        />
                                                    </div>
                                                ))}
                                                <button onClick={() => addKeyResult(okr.id)} className="text-xs font-medium text-slate-400 hover:text-indigo-600 flex items-center gap-1 mt-2"><Plus className="w-3 h-3" /> Add Key Result</button>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            ))}
                            <button onClick={addOkr} className="w-full py-4 border-2 border-dashed border-slate-200 rounded-xl text-slate-400 font-bold hover:border-indigo-400 hover:text-indigo-600 transition-all flex items-center justify-center gap-2">
                                <Plus className="w-5 h-5" /> Add New Objective
                            </button>
                        </div>
                    )}

                    {activeTab === 'roadmap' && (
                        <div className="space-y-8 animate-in fade-in duration-300">
                            <div className="relative">
                                <div className="absolute left-8 top-0 bottom-0 w-0.5 bg-slate-200"></div>
                                <div className="space-y-8">
                                    {roadmap.map((phase, idx) => (
                                        <div key={phase.id} className="relative flex gap-8">
                                            <div className={`w-16 h-16 rounded-2xl flex items-center justify-center shrink-0 z-10 border-4 border-white shadow-sm ${phase.status === 'current' ? 'bg-indigo-600 text-white' : 'bg-slate-100 text-slate-400'}`}>
                                                <Flag className="w-6 h-6" />
                                            </div>
                                            <div className="flex-1 bg-slate-50 rounded-xl border border-slate-200 p-6">
                                                <div className="flex justify-between items-start mb-4">
                                                    <h3 className="font-bold text-lg text-slate-900">{phase.phase}</h3>
                                                    <span className={`text-[10px] font-bold uppercase px-2 py-1 rounded-full ${phase.status === 'current' ? 'bg-indigo-100 text-indigo-700' : 'bg-slate-200 text-slate-500'}`}>{phase.status}</span>
                                                </div>
                                                <ul className="space-y-2">
                                                    {phase.items.map((item, i) => (
                                                        <li key={i} className="flex items-center gap-2 text-sm text-slate-600">
                                                            <CheckCircle2 className="w-4 h-4 text-emerald-500" />
                                                            {item}
                                                        </li>
                                                    ))}
                                                </ul>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        </div>
                    )}
                </div>

                <div className="bg-slate-50 p-4 border-t border-slate-200 flex justify-end">
                    <button className="bg-slate-900 text-white px-6 py-2 rounded-lg font-bold text-sm flex items-center gap-2 hover:bg-slate-800 transition-colors">
                        <Save className="w-4 h-4" /> Save Strategy
                    </button>
                </div>
            </div>
        </div>
    );
}
