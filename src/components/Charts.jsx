import React from 'react';
import { ResponsiveContainer, PieChart, Pie, Cell, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar, Tooltip } from 'recharts';

export const ScoreRing = ({ score, size = '32' }) => {
    const data = [{ value: score }, { value: 100 - score }];
    const color = score >= 80 ? '#10b981' : score >= 50 ? '#f59e0b' : '#f43f5e';
    const large = size === '32';
    // Explicit pixel size: dynamic Tailwind classes like w-${size} are purged at build time
    const px = large ? 128 : 112;
    const innerR = large ? 48 : 40;
    const outerR = large ? 60 : 52;

    return (
        <div className="relative flex items-center justify-center" style={{ width: px, height: px }}>
            <PieChart width={px} height={px}>
                <Pie data={data} cx="50%" cy="50%" innerRadius={innerR} outerRadius={outerR}
                    startAngle={90} endAngle={-270} dataKey="value" stroke="none" isAnimationActive={false}>
                    <Cell fill={color} />
                    <Cell fill="rgba(255,255,255,0.25)" />
                </Pie>
            </PieChart>
            <div className="absolute inset-0 flex flex-col items-center justify-center">
                <span className={`${large ? 'text-4xl' : 'text-2xl'} font-bold text-white leading-none`}>{score}</span>
                <span className="mt-1 text-[10px] font-bold uppercase text-white/70 tracking-wider">of 100</span>
            </div>
        </div>
    );
};

export const RadarViz = ({ currentData }) => {
    if (!currentData) return null;
    const data = [
        { subject: 'Problem', A: currentData.scores.problem, fullMark: 100 },
        { subject: 'Market', A: currentData.scores.market, fullMark: 100 },
        { subject: 'Solution', A: currentData.scores.solution, fullMark: 100 },
        { subject: 'Competition', A: currentData.scores.moat, fullMark: 100 },
        { subject: 'Business', A: currentData.scores.feasibility, fullMark: 100 },
    ];

    return (
        <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
                <RadarChart cx="50%" cy="50%" outerRadius="62%" margin={{ top: 10, right: 30, bottom: 10, left: 30 }} data={data}>
                    <PolarGrid stroke="#e2e8f0" />
                    <PolarAngleAxis dataKey="subject" tick={{ fill: '#64748b', fontSize: 11, fontWeight: 600 }} />
                    <PolarRadiusAxis angle={30} domain={[0, 100]} tick={false} axisLine={false} />
                    <Radar
                        name="Score"
                        dataKey="A"
                        stroke="#6366f1"
                        strokeWidth={3}
                        fill="#6366f1"
                        fillOpacity={0.2}
                    />
                    <Tooltip contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 10px 15px -3px rgb(0 0 0 / 0.1)' }} />
                </RadarChart>
            </ResponsiveContainer>
        </div>
    );
};

export const LeanCanvasCard = ({ title, content, icon, color }) => (
    <div className="bg-white p-4 rounded-xl border border-slate-100 shadow-sm h-full flex flex-col hover:shadow-md transition-shadow duration-300 group">
        <div className={`flex items-center gap-2 mb-3 ${color} opacity-80 group-hover:opacity-100 transition-opacity`}>
            {icon}
            <h4 className="font-bold text-xs uppercase tracking-wider">{title}</h4>
        </div>
        <div className="flex-grow overflow-y-auto custom-scrollbar pr-2">
            <p className="text-sm text-slate-600 leading-relaxed">
                {content || <span className="text-slate-300 italic">Generating...</span>}
            </p>
        </div>
    </div>
);
