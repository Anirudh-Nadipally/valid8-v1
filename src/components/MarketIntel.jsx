import React, { useState } from 'react';
import { Users, Megaphone, DollarSign, Plus, Trash2, TrendingUp, Target, BarChart3, Loader2, Sparkles, CheckCircle2 } from 'lucide-react';
import { api } from '../api';

export function MarketIntel({ idea, analysisId }) {
    const [activeTab, setActiveTab] = useState('segments');
    const [loading, setLoading] = useState(false);

    // Mock data for initial state
    const [segments, setSegments] = useState([
        { id: 1, name: 'Early Adopters', size: '10k-50k', pain: 'High', willingness: 'High', description: 'Tech-savvy users looking for new solutions.' }
    ]);

    const [channels, setChannels] = useState([
        { id: 1, name: 'Content Marketing', type: 'Inbound', cost: 'Low', reach: 'Medium', conversion: 'Medium' },
        { id: 2, name: 'LinkedIn Ads', type: 'Paid', cost: 'High', reach: 'High', conversion: 'High' }
    ]);

    const [pricing, setPricing] = useState([
        { id: 1, tier: 'Starter', price: '0', period: 'month', features: ['Basic Access', '1 Project'] },
        { id: 2, tier: 'Pro', price: '29', period: 'month', features: ['Unlimited Projects', 'Priority Support', 'Analytics'] }
    ]);

    const addSegment = () => setSegments([...segments, { id: Date.now(), name: '', size: '', pain: 'Medium', willingness: 'Medium', description: '' }]);
    const updateSegment = (id, field, val) => setSegments(segments.map(s => s.id === id ? { ...s, [field]: val } : s));
    const removeSegment = (id) => setSegments(segments.filter(s => s.id !== id));

    const handleGenerate = async () => {
        if (!analysisId) return;
        setLoading(true);
        try {
            const result = await api.generateMarketIntel(analysisId);
            if (result.segments) setSegments(result.segments.map((s, i) => ({ ...s, id: i })));
            if (result.channels) setChannels(result.channels.map((c, i) => ({ ...c, id: i })));
            if (result.pricing) setPricing(result.pricing.map((p, i) => ({ ...p, id: i })));
        } catch (err) {
            console.error("Failed to generate market intel", err);
            alert("Failed to generate market intelligence. Please try again.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="max-w-5xl mx-auto space-y-8 animate-in fade-in duration-500">
            <div className="text-center space-y-2 relative">
                <h2 className="text-3xl font-bold text-slate-900">Go-to-Market Intel</h2>
                <p className="text-slate-500">Analyze your audience and plan your attack.</p>
                <button
                    onClick={handleGenerate}
                    disabled={loading || !analysisId}
                    className="absolute right-0 top-0 bg-indigo-600 text-white px-4 py-2 rounded-lg text-xs font-bold flex items-center gap-2 hover:bg-indigo-700 disabled:opacity-50 transition-all shadow-lg shadow-indigo-200"
                >
                    {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Sparkles className="w-4 h-4" />}
                    Auto-Generate
                </button>
            </div>

            <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
                <div className="flex border-b border-slate-200 bg-slate-50/50">
                    <button onClick={() => setActiveTab('segments')} className={`flex-1 py-4 text-sm font-bold border-b-2 transition-colors ${activeTab === 'segments' ? 'border-indigo-600 text-indigo-600' : 'border-transparent text-slate-500 hover:text-slate-800'}`}>Market Segments</button>
                    <button onClick={() => setActiveTab('channels')} className={`flex-1 py-4 text-sm font-bold border-b-2 transition-colors ${activeTab === 'channels' ? 'border-indigo-600 text-indigo-600' : 'border-transparent text-slate-500 hover:text-slate-800'}`}>Acquisition Channels</button>
                    <button onClick={() => setActiveTab('pricing')} className={`flex-1 py-4 text-sm font-bold border-b-2 transition-colors ${activeTab === 'pricing' ? 'border-indigo-600 text-indigo-600' : 'border-transparent text-slate-500 hover:text-slate-800'}`}>Pricing Strategy</button>
                </div>

                <div className="p-8">
                    {activeTab === 'segments' && (
                        <div className="space-y-6 animate-in fade-in duration-300">
                            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                                {segments.map((seg) => (
                                    <div key={seg.id} className="bg-slate-50 rounded-xl border border-slate-200 p-5 space-y-4 relative group hover:shadow-md transition-all">
                                        <button onClick={() => removeSegment(seg.id)} className="absolute right-2 top-2 text-slate-300 hover:text-rose-500 opacity-0 group-hover:opacity-100 transition-opacity"><Trash2 className="w-4 h-4" /></button>
                                        <div className="flex items-center gap-3 mb-2">
                                            <div className="w-10 h-10 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center shrink-0"><Users className="w-5 h-5" /></div>
                                            <input value={seg.name} onChange={(e) => updateSegment(seg.id, 'name', e.target.value)} className="w-full bg-transparent font-bold text-slate-900 focus:outline-none border-b border-transparent focus:border-blue-500" placeholder="Segment Name" />
                                        </div>
                                        <div className="space-y-3">
                                            <div>
                                                <label className="text-[10px] uppercase font-bold text-slate-400">Market Size</label>
                                                <input value={seg.size} onChange={(e) => updateSegment(seg.id, 'size', e.target.value)} className="w-full bg-white border border-slate-200 rounded px-2 py-1 text-xs" placeholder="e.g. 1M users" />
                                            </div>
                                            <div className="grid grid-cols-2 gap-2">
                                                <div>
                                                    <label className="text-[10px] uppercase font-bold text-slate-400">Pain Level</label>
                                                    <select value={seg.pain} onChange={(e) => updateSegment(seg.id, 'pain', e.target.value)} className="w-full bg-white border border-slate-200 rounded px-2 py-1 text-xs">
                                                        <option>Low</option><option>Medium</option><option>High</option>
                                                    </select>
                                                </div>
                                                <div>
                                                    <label className="text-[10px] uppercase font-bold text-slate-400">Willingness</label>
                                                    <select value={seg.willingness} onChange={(e) => updateSegment(seg.id, 'willingness', e.target.value)} className="w-full bg-white border border-slate-200 rounded px-2 py-1 text-xs">
                                                        <option>Low</option><option>Medium</option><option>High</option>
                                                    </select>
                                                </div>
                                            </div>
                                            <textarea value={seg.description} onChange={(e) => updateSegment(seg.id, 'description', e.target.value)} className="w-full bg-white border border-slate-200 rounded p-2 text-xs resize-none h-20" placeholder="Description..." />
                                        </div>
                                    </div>
                                ))}
                                <button onClick={addSegment} className="border-2 border-dashed border-slate-200 rounded-xl flex flex-col items-center justify-center text-slate-400 hover:border-blue-400 hover:text-blue-600 transition-all min-h-[300px]">
                                    <Plus className="w-8 h-8 mb-2" />
                                    <span className="font-bold text-sm">Add Segment</span>
                                </button>
                            </div>
                        </div>
                    )}

                    {activeTab === 'channels' && (
                        <div className="space-y-6 animate-in fade-in duration-300">
                            <div className="overflow-x-auto">
                                <table className="w-full text-sm text-left">
                                    <thead className="text-xs text-slate-500 uppercase bg-slate-50 border-b border-slate-200">
                                        <tr>
                                            <th className="px-6 py-3 font-bold">Channel</th>
                                            <th className="px-6 py-3 font-bold">Type</th>
                                            <th className="px-6 py-3 font-bold">Cost</th>
                                            <th className="px-6 py-3 font-bold">Reach</th>
                                            <th className="px-6 py-3 font-bold">Conversion</th>
                                            <th className="px-6 py-3 font-bold text-right">Action</th>
                                        </tr>
                                    </thead>
                                    <tbody className="divide-y divide-slate-100">
                                        {channels.map((ch) => (
                                            <tr key={ch.id} className="hover:bg-slate-50/50">
                                                <td className="px-6 py-4 font-bold text-slate-900">{ch.name}</td>
                                                <td className="px-6 py-4"><span className="bg-slate-100 text-slate-600 px-2 py-1 rounded text-xs font-bold">{ch.type}</span></td>
                                                <td className="px-6 py-4">{ch.cost}</td>
                                                <td className="px-6 py-4">{ch.reach}</td>
                                                <td className="px-6 py-4">{ch.conversion}</td>
                                                <td className="px-6 py-4 text-right"><button className="text-slate-400 hover:text-rose-500"><Trash2 className="w-4 h-4" /></button></td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                            <button className="w-full py-3 bg-slate-50 border border-slate-200 rounded-lg text-sm font-bold text-slate-600 hover:bg-slate-100 flex items-center justify-center gap-2">
                                <Plus className="w-4 h-4" /> Add Channel
                            </button>
                        </div>
                    )}

                    {activeTab === 'pricing' && (
                        <div className="space-y-8 animate-in fade-in duration-300">
                            <div className="grid grid-cols-1 md:grid-cols-3 gap-8 items-center">
                                {pricing.map((tier) => (
                                    <div key={tier.id} className="bg-white rounded-2xl border border-slate-200 p-8 shadow-sm hover:shadow-lg hover:-translate-y-1 transition-all relative">
                                        <div className="text-center mb-6">
                                            <h3 className="font-bold text-slate-900 text-lg mb-2">{tier.tier}</h3>
                                            <div className="flex items-center justify-center gap-1">
                                                <span className="text-3xl font-bold text-slate-900">${tier.price}</span>
                                                <span className="text-slate-500">/{tier.period}</span>
                                            </div>
                                        </div>
                                        <ul className="space-y-3 mb-8">
                                            {tier.features.map((feat, i) => (
                                                <li key={i} className="flex items-center gap-2 text-sm text-slate-600">
                                                    <CheckCircle2 className="w-4 h-4 text-emerald-500 shrink-0" />
                                                    {feat}
                                                </li>
                                            ))}
                                        </ul>
                                        <button className="w-full py-2 rounded-lg border border-slate-200 font-bold text-sm hover:bg-slate-50 transition-colors">Edit Tier</button>
                                    </div>
                                ))}
                                <button className="h-full min-h-[300px] border-2 border-dashed border-slate-200 rounded-2xl flex flex-col items-center justify-center text-slate-400 hover:border-indigo-400 hover:text-indigo-600 transition-all">
                                    <Plus className="w-8 h-8 mb-2" />
                                    <span className="font-bold">Add Tier</span>
                                </button>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
