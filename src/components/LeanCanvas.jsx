import React, { useState, useEffect } from 'react';
import { Download, ShieldAlert, Lightbulb, Target, Swords, Users, BarChart3, ArrowRight, TrendingUp, Sparkles, Loader2 } from 'lucide-react';
import { LeanCanvasCard } from './Charts';
import { api } from '../api';

export function LeanCanvas({ currentAnalysis, idea, analysisId }) {
    const [loading, setLoading] = useState(false);
    const [canvasData, setCanvasData] = useState({
        problemSummary: '',
        solutionSummary: '',
        uniqueValue: '',
        unfairAdvantage: '',
        customerSegments: '',
        metrics: '',
        channels: '',
        costs: '',
        revenue: ''
    });

    useEffect(() => {
        if (currentAnalysis && currentAnalysis.leanCanvas) {
            setCanvasData({
                problemSummary: currentAnalysis.leanCanvas.problemSummary || '',
                solutionSummary: currentAnalysis.leanCanvas.solutionSummary || '',
                uniqueValue: currentAnalysis.leanCanvas.uniqueValue || idea.uniqueValue || '',
                unfairAdvantage: currentAnalysis.leanCanvas.unfairAdvantage || (currentAnalysis.strengths ? currentAnalysis.strengths[0] : '') || '',
                customerSegments: currentAnalysis.leanCanvas.customerSegments || idea.targetAudience || '',
                metrics: currentAnalysis.leanCanvas.metrics || '',
                channels: currentAnalysis.leanCanvas.channels || '',
                costs: currentAnalysis.leanCanvas.costs || '',
                revenue: currentAnalysis.leanCanvas.revenue || ''
            });
        }
    }, [currentAnalysis, idea]);

    const handleGenerate = async () => {
        if (!analysisId) return;
        setLoading(true);
        try {
            const result = await api.generateLeanCanvas(analysisId);
            setCanvasData({
                problemSummary: result.problemSummary,
                solutionSummary: result.solutionSummary,
                uniqueValue: result.uniqueValue,
                unfairAdvantage: result.unfairAdvantage,
                customerSegments: result.customerSegments,
                metrics: result.metrics,
                channels: result.channels,
                costs: result.costs,
                revenue: result.revenue
            });
        } catch (err) {
            console.error("Failed to generate Lean Canvas", err);
            alert("Failed to generate Lean Canvas. Please try again.");
        } finally {
            setLoading(false);
        }
    };

    const handleDownloadPdf = () => {
        // Placeholder for PDF download logic if needed here, 
        // or we can pass a prop from App.jsx if the logic is complex and centralized.
        // For now, we'll assume the user uses the main "Export Report" button, 
        // but the original UI had a specific button. 
        // We can implement a specific download if the API supports it, or just alert.
        if (analysisId) {
            window.open(api.getReportUrl(analysisId), '_blank');
        }
    };

    return (
        <div className="animate-in fade-in zoom-in-95 duration-300">
            <div className="flex justify-between items-center mb-6 no-print">
                <div className="flex items-center gap-4">
                    <h3 className="font-bold text-slate-800 text-lg">Lean Business Canvas</h3>
                    <button
                        onClick={handleGenerate}
                        disabled={loading || !analysisId}
                        className="bg-indigo-600 text-white px-3 py-1.5 rounded-lg text-xs font-bold flex items-center gap-2 hover:bg-indigo-700 disabled:opacity-50 transition-all shadow-sm"
                    >
                        {loading ? <Loader2 className="w-3 h-3 animate-spin" /> : <Sparkles className="w-3 h-3" />}
                        Auto-Generate
                    </button>
                </div>
                <button onClick={handleDownloadPdf} className="text-xs font-bold text-slate-500 hover:text-slate-800 flex items-center gap-2">
                    <Download className="w-4 h-4" /> Download as PDF
                </button>
            </div>
            <div className="grid grid-cols-5 grid-rows-3 gap-4 h-[650px]">
                <div className="col-span-1 row-span-2"><LeanCanvasCard title="Problem" content={canvasData.problemSummary} icon={<ShieldAlert className="w-4 h-4" />} color="text-rose-600" /></div>
                <div className="col-span-1 row-span-1"><LeanCanvasCard title="Solution" content={canvasData.solutionSummary} icon={<Lightbulb className="w-4 h-4" />} color="text-amber-600" /></div>
                <div className="col-span-1 row-span-2"><LeanCanvasCard title="Unique Value Prop" content={canvasData.uniqueValue} icon={<Target className="w-4 h-4" />} color="text-indigo-600" /></div>
                <div className="col-span-1 row-span-1"><LeanCanvasCard title="Unfair Advantage" content={canvasData.unfairAdvantage} icon={<Swords className="w-4 h-4" />} color="text-purple-600" /></div>
                <div className="col-span-1 row-span-2"><LeanCanvasCard title="Customer Segments" content={canvasData.customerSegments} icon={<Users className="w-4 h-4" />} color="text-blue-600" /></div>
                <div className="col-span-1 row-span-1"><LeanCanvasCard title="Key Metrics" content={canvasData.metrics} icon={<BarChart3 className="w-4 h-4" />} color="text-emerald-600" /></div>
                <div className="col-span-1 row-span-1"><LeanCanvasCard title="Channels" content={canvasData.channels} icon={<ArrowRight className="w-4 h-4" />} color="text-cyan-600" /></div>
                <div className="col-span-2.5 row-span-1"><LeanCanvasCard title="Cost Structure" content={canvasData.costs} icon={<TrendingUp className="w-4 h-4 rotate-180" />} color="text-rose-500" /></div>
                <div className="col-span-2.5 row-span-1"><LeanCanvasCard title="Revenue Streams" content={canvasData.revenue} icon={<TrendingUp className="w-4 h-4" />} color="text-emerald-500" /></div>
            </div>
        </div>
    );
}
