import React from 'react';
import { BrainCircuit } from 'lucide-react';
import { ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';

export const ReportCard = React.forwardRef(({ analysis, idea, persona }, ref) => {
    if (!analysis) return null;
    const color = analysis.overallScore >= 80 ? 'border-t-emerald-500' : analysis.overallScore >= 50 ? 'border-t-amber-500' : 'border-t-rose-500';

    return (
        <div
            ref={ref}
            id="report-card"
            className={`w-[600px] h-[338px] bg-white border border-slate-200 rounded-2xl overflow-hidden shadow-2xl relative p-8 flex flex-col justify-between ${color} border-t-8`}
            style={{ fontFamily: "'Inter', sans-serif" }}
        >
            <div className="absolute inset-0 bg-gradient-to-br from-white via-white to-slate-50 z-0"></div>

            <div className="relative z-10">
                <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                        <span className="bg-slate-900 p-2 rounded-lg"><BrainCircuit className="w-5 h-5 text-white" /></span>
                        <span className="font-bold text-xl text-slate-900">Valid8 Pro</span>
                    </div>
                    <div className="text-right">
                        <p className="text-xs font-medium text-slate-400">Analyzed By</p>
                        <p className={`font-bold text-sm ${persona.color}`}>{persona.name}</p>
                    </div>
                </div>
            </div>

            <div className="relative z-10">
                <h2 className="text-lg font-bold text-slate-800 truncate mb-1">{idea.title}</h2>
                <p className="text-2xl font-bold text-slate-900 leading-tight">"{analysis.verdict}"</p>
            </div>

            <div className="relative z-10 flex items-end justify-between">
                <div className="flex gap-4">
                    <div className="text-center">
                        <p className="text-xs font-bold uppercase text-slate-400">Problem</p>
                        <p className="text-2xl font-bold text-slate-800">{analysis.scores.problem}</p>
                    </div>
                    <div className="text-center">
                        <p className="text-xs font-bold uppercase text-slate-400">Solution</p>
                        <p className="text-2xl font-bold text-slate-800">{analysis.scores.solution}</p>
                    </div>
                    <div className="text-center">
                        <p className="text-xs font-bold uppercase text-slate-400">Market</p>
                        <p className="text-2xl font-bold text-slate-800">{analysis.scores.market}</p>
                    </div>
                    <div className="text-center">
                        <p className="text-xs font-bold uppercase text-slate-400">Moat</p>
                        <p className="text-2xl font-bold text-slate-800">{analysis.scores.moat}</p>
                    </div>
                </div>

                <div className="relative w-28 h-28 flex items-center justify-center">
                    <ResponsiveContainer width="100%" height="100%">
                        <PieChart>
                            <Pie
                                data={[{ v: analysis.overallScore }, { v: 100 - analysis.overallScore }]}
                                cx="50%"
                                cy="50%"
                                innerRadius={38}
                                outerRadius={50}
                                startAngle={90}
                                endAngle={-270}
                                dataKey="v"
                                stroke="none"
                            >
                                <Cell fill={analysis.overallScore >= 80 ? '#10b981' : analysis.overallScore >= 50 ? '#f59e0b' : '#f43f5e'} />
                                <Cell fill="#f1f5f9" />
                            </Pie>
                        </PieChart>
                    </ResponsiveContainer>
                    <div className="absolute inset-0 flex flex-col items-center justify-center">
                        <span className="text-3xl font-bold text-slate-800">{analysis.overallScore}</span>
                        <span className="text-[10px] font-bold uppercase text-slate-400 tracking-wider">Score</span>
                    </div>
                </div>
            </div>

        </div>
    );
});
