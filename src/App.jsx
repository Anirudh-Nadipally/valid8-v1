import React, { useState, useEffect, useRef } from 'react';
import {
    LayoutDashboard, Lightbulb, Target, TrendingUp, ShieldAlert, ArrowRight, CheckCircle2, AlertTriangle,
    BarChart3, History, Loader2, Users, Grid, Swords, BrainCircuit, Sparkles, MessageSquare, Send,
    Download, TestTube2, GitBranch, FileText, Workflow, UploadCloud, Share2, DownloadCloud, Rocket,
    UserCheck, Megaphone, Copy, SearchCheck, Scale, Gavel, Presentation, Minimize2, Maximize2, Mic, X, Image, ShieldCheck
} from 'lucide-react';
import VisionGenerator from './components/VisionEngine/VisionGenerator';
import { api } from './api';
import { PERSONAS, DEMO_ANALYSIS } from './constants.jsx';
import { ScoreRing, RadarViz, LeanCanvasCard } from './components/Charts';
import { ReportCard } from './components/ReportCard';
import { StrategyFlow } from './components/StrategyFlow';
import { MarketIntel } from './components/MarketIntel';
import { ScenarioLab } from './components/ScenarioLab';
import { LeanCanvas } from './components/LeanCanvas';
import { ScoreTrace } from './components/ScoreTrace';
import { AnalysisDashboard } from './components/v4/AnalysisDashboard';

export default function App() {
    const [loading, setLoading] = useState(false); // Initial loading if needed
    const [analyzing, setAnalyzing] = useState(false);
    const [activeSection, setActiveSection] = useState('dashboard');
    const [selectedPersona, setSelectedPersona] = useState('vc');
    const [showDemo, setShowDemo] = useState(false);

    const [activeAnalysisTab, setActiveAnalysisTab] = useState('analysis');
    const [v4Mode, setV4Mode] = useState(false);

    const [inputMode, setInputMode] = useState('manual');
    const [uploadedFile, setUploadedFile] = useState(null);
    const [fileError, setFileError] = useState(null);

    const [idea, setIdea] = useState({
        title: '',
        problem: '',
        solution: '',
        targetAudience: '',
        uniqueValue: ''
    });

    const [iterations, setIterations] = useState([]);
    const [currentAnalysis, setCurrentAnalysis] = useState(null);
    const [currentAnalysisId, setCurrentAnalysisId] = useState(null);

    const [chatHistory, setChatHistory] = useState([]);
    const [chatInput, setChatInput] = useState('');
    const [chatLoading, setChatLoading] = useState(false);
    const chatEndRef = useRef(null);


    const [legalAnalysis, setLegalAnalysis] = useState(null);
    const [legalLoading, setLegalLoading] = useState(false);

    const [pitchAnalysis, setPitchAnalysis] = useState(null);
    const [pitchLoading, setPitchLoading] = useState(false);

    const reportCardRef = useRef(null);
    const [copyStatus, setCopyStatus] = useState(null);

    const [nameSuggestions, setNameSuggestions] = useState([]);
    const [nameLoading, setNameLoading] = useState(false);
    const [competitorAnalysis, setCompetitorAnalysis] = useState(null);
    const [competitorLoading, setCompetitorLoading] = useState(null);

    useEffect(() => {
        loadHistory();
        // Inject html-to-image script
        const script = document.createElement('script');
        script.src = 'https://cdnjs.cloudflare.com/ajax/libs/html-to-image/1.11.11/html-to-image.min.js';
        script.async = true;
        document.body.appendChild(script);
        return () => {
            if (document.body.contains(script)) document.body.removeChild(script);
        };
    }, []);

    const loadHistory = async () => {
        try {
            const history = await api.getHistory();
            setIterations(history);
            if (history.length > 0 && !currentAnalysis) {
                const latest = history[0];
                setCurrentAnalysis(latest.analysis);
                setCurrentAnalysisId(latest.id);
                setIdea(latest.idea);
                setSelectedPersona(latest.persona);
            }
        } catch (e) {
            console.error("Failed to load history", e);
        }
    };

    const runAnalysis = async () => {
        const isManualValid = inputMode === 'manual' && idea.problem && idea.solution;
        const isUploadValid = inputMode === 'upload' && uploadedFile;
        if (!idea.title || (!isManualValid && !isUploadValid)) return;

        if (showDemo) {
            setAnalyzing(true);
            setTimeout(() => {
                setCurrentAnalysis(DEMO_ANALYSIS);
                setActiveAnalysisTab('analysis');
                setAnalyzing(false);
                setActiveSection('dashboard');
            }, 1500);
            return;
        }

        setAnalyzing(true);
        setNameSuggestions([]);
        setCompetitorAnalysis(null);
        setPitchAnalysis(null);
        setLegalAnalysis(null);


        try {
            const formData = new FormData();
            formData.append('title', idea.title);
            formData.append('persona', selectedPersona);

            if (inputMode === 'manual') {
                formData.append('problem', idea.problem);
                formData.append('solution', idea.solution);
                formData.append('targetAudience', idea.targetAudience);
                formData.append('uniqueValue', idea.uniqueValue);
            } else {
                formData.append('file', uploadedFile);
            }

            const result = await api.analyze(formData);

            setCurrentAnalysis(result.analysis);
            setCurrentAnalysisId(result.id);
            setIdea(result.idea); // Update idea with extracted data if PDF
            setSelectedPersona(result.persona);

            loadHistory(); // Refresh history list
            setActiveSection('dashboard');

        } catch (error) {
            console.error("Analysis Failed", error);
            alert("Analysis failed. Please try again.");
        } finally {
            setAnalyzing(false);
        }
    };

    const runLegalAnalysis = async () => {
        if (!currentAnalysisId) return;
        setLegalLoading(true);
        try {
            const result = await api.legalCheck(currentAnalysisId);
            setLegalAnalysis(result);
        } catch (err) {
            console.error("Legal analysis failed", err);
        } finally {
            setLegalLoading(false);
        }
    };

    const runPitchArchitect = async () => {
        if (!currentAnalysisId) return;
        setPitchLoading(true);
        try {
            const result = await api.pitchArchitect(currentAnalysisId);
            setPitchAnalysis(result);
        } catch (err) {
            console.error("Pitch Architect failed", err);
        } finally {
            setPitchLoading(false);
        }
    };


    const handleChatSubmit = async (e) => {
        e.preventDefault();
        if (!chatInput.trim() || !currentAnalysisId) return;

        const newMessage = { role: 'user', content: chatInput };
        setChatHistory(prev => [...prev, newMessage]);
        setChatInput('');
        setChatLoading(true);

        try {
            const result = await api.chat(currentAnalysisId, newMessage.content, selectedPersona);
            setChatHistory(prev => [...prev, result]);
        } catch (err) {
            console.error("Chat failed", err);
            setChatHistory(prev => [...prev, { role: 'assistant', content: "Error connecting to AI." }]);
        } finally {
            setChatLoading(false);
        }
    };

    const generateVentureNames = async () => {
        if (!idea.problem || !idea.solution) {
            alert("Please fill out the Problem and Solution fields first.");
            return;
        }
        setNameLoading(true);
        try {
            const result = await api.generateNames(idea.problem, idea.solution);
            setNameSuggestions(result.names);
        } catch (err) {
            console.error("Name generation failed:", err);
        } finally {
            setNameLoading(false);
        }
    };

    const analyzeCompetitorWeakness = async (competitorName) => {
        if (!currentAnalysisId) return;
        setCompetitorLoading(competitorName);
        try {
            const result = await api.analyzeCompetitor(currentAnalysisId, competitorName, selectedPersona);
            setCompetitorAnalysis(result);
        } catch (err) {
            console.error("Competitor analysis failed:", err);
        } finally {
            setCompetitorLoading(null);
        }
    };

    const handleDownloadPdf = () => {
        if (currentAnalysisId) {
            window.open(api.getReportUrl(currentAnalysisId), '_blank');
        }
    }

    // ... (Keep UI rendering logic mostly same, just update data sources)
    // Due to length, I will focus on the structure and key UI elements.
    // The render method is large, so I will try to be efficient.

    return (
        <div className="flex h-screen bg-[#f8fafc] text-slate-900 font-sans overflow-hidden selection:bg-indigo-100 selection:text-indigo-900">
            <aside className="w-72 bg-white border-r border-slate-200 flex flex-col z-20 shadow-[4px_0_24px_-12px_rgba(0,0,0,0.1)] no-print">
                <div className="p-6">
                    <div className="flex items-center gap-3 mb-8">
                        <div className="bg-slate-900 p-2 rounded-xl">
                            <BrainCircuit className="w-6 h-6 text-white" />
                        </div>
                        <div>
                            <h1 className="font-bold text-xl tracking-tight text-slate-900">Valid8 Pro</h1>
                            <div className="flex items-center gap-2">
                                <button
                                    onClick={() => setV4Mode(!v4Mode)}
                                    className={`text-[10px] font-bold px-1.5 py-0.5 rounded uppercase tracking-wider transition-all ${v4Mode ? 'bg-emerald-100 text-emerald-700' : 'text-indigo-600 bg-indigo-50'}`}
                                >
                                    {v4Mode ? 'V4 BETA' : 'V3'}
                                </button>
                                <label className="flex items-center gap-1 cursor-pointer">
                                    <input type="checkbox" checked={showDemo} onChange={e => setShowDemo(e.target.checked)} className="w-3 h-3 accent-indigo-600 rounded" />
                                    <span className="text-[10px] text-slate-400 font-medium">Demo Mode</span>
                                </label>
                            </div>
                        </div>
                    </div>

                    <nav className="space-y-1">
                        {[
                            { id: 'dashboard', icon: LayoutDashboard, label: 'Overview' },
                            { id: 'flow', icon: Workflow, label: 'Strategy Flow' },
                            { id: 'canvas', icon: Grid, label: 'Lean Canvas' },
                            { id: 'market', icon: Rocket, label: 'Go-to-Market' },
                            { id: 'pitch', icon: Presentation, label: 'Pitch Architect', badge: 'New' },
                            { id: 'vision', icon: Image, label: 'Vision Engine', badge: 'Pro' },
                            { id: 'scenario', icon: TestTube2, label: 'Scenario Lab' },
                            { id: 'legal', icon: Gavel, label: 'Legal Check' },
                            { id: 'consult', icon: MessageSquare, label: 'Consultant Chat' },
                            { id: 'share', icon: Share2, label: 'Share Report' },
                        ].map((item) => (
                            <button
                                key={item.id}
                                onClick={() => {
                                    if (item.id === 'dashboard' || currentAnalysis) setActiveSection(item.id);
                                }}
                                disabled={!currentAnalysis && item.id !== 'dashboard'}
                                className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all duration-200 relative group ${activeSection === item.id
                                    ? 'bg-slate-900 text-white shadow-lg shadow-slate-200'
                                    : !currentAnalysis && item.id !== 'dashboard'
                                        ? 'opacity-40 cursor-not-allowed'
                                        : 'text-slate-500 hover:bg-slate-50 hover:text-slate-900'
                                    }`}
                            >
                                <item.icon className={`w-4 h-4 ${activeSection === item.id ? 'text-indigo-400' : 'group-hover:text-indigo-600 transition-colors'}`} />
                                {item.label}
                                {item.badge && activeSection !== item.id && (
                                    <span className="absolute right-3 text-[10px] font-bold bg-indigo-100 text-indigo-700 px-1.5 py-0.5 rounded-full">{item.badge}</span>
                                )}
                            </button>
                        ))}
                    </nav>
                </div>

                <div className="mt-auto border-t border-slate-100 p-4">
                    <div className="bg-slate-50/50 rounded-xl p-4 border border-slate-100">
                        <h3 className="text-[10px] font-bold text-slate-400 uppercase mb-3 flex items-center gap-2 tracking-wider">
                            <History className="w-3 h-3" /> Previous Iterations
                        </h3>
                        <div className="space-y-2 max-h-40 overflow-y-auto pr-1 custom-scrollbar">
                            {iterations.map((it) => (
                                <button
                                    key={it.id}
                                    onClick={() => {
                                        setCurrentAnalysis(it.analysis);
                                        setCurrentAnalysisId(it.id);
                                        setIdea(it.idea);
                                        setSelectedPersona(it.persona || 'vc');
                                        setChatHistory([]); // Reset chat for new selection

                                        setLegalAnalysis(null);
                                        setPitchAnalysis(null);
                                        setNameSuggestions([]);
                                        setCompetitorAnalysis(null);
                                    }}
                                    className="w-full text-left p-2 rounded-lg hover:bg-white hover:shadow-sm transition-all group border border-transparent hover:border-slate-100"
                                >
                                    <div className="flex justify-between items-center mb-1">
                                        <span className="font-semibold text-xs text-slate-700 truncate max-w-[120px]">{it.idea.title || 'Untitled'}</span>
                                        <span className={`text-[10px] font-bold px-1.5 rounded ${it.analysis.overallScore >= 70 ? 'bg-emerald-100 text-emerald-700' : 'bg-rose-100 text-rose-700'}`}>
                                            {it.analysis.overallScore}
                                        </span>
                                    </div>
                                    <p className="text-[10px] text-slate-400 truncate">{new Date(it.timestamp).toLocaleDateString()}</p>
                                </button>
                            ))}
                            {iterations.length === 0 && <p className="text-xs text-slate-400 italic pl-2">No history yet.</p>}
                        </div>
                    </div>
                </div>
            </aside>

            <main className="flex-1 overflow-hidden flex flex-col relative no-print">
                {v4Mode ? (
                    <AnalysisDashboard
                        idea={idea}
                        initialAnalysis={null}
                        onBack={() => setV4Mode(false)}
                    />
                ) : (
                    <>
                        {/* Header */}
                        <header className="bg-white/80 backdrop-blur-md border-b border-slate-200 px-8 py-4 flex items-center justify-between z-10 shrink-0 no-print">
                            <div className="flex items-center gap-4">
                                <h2 className="text-xl font-bold text-slate-800">
                                    {activeSection === 'dashboard' && 'Validation Console'}
                                    {activeSection === 'flow' && 'Strategy Flow'}
                                    {activeSection === 'canvas' && 'Business Model Canvas'}
                                    {activeSection === 'market' && 'Go-to-Market Intel'}
                                    {activeSection === 'scenario' && 'Pivot Scenario Lab'}
                                    {activeSection === 'legal' && 'Legal & IP Risk Check'}
                                    {activeSection === 'pitch' && 'Pitch Architect'}
                                    {activeSection === 'vision' && 'Venture Vision Engine'}
                                    {activeSection === 'consult' && 'Strategic Consultation'}
                                    {activeSection === 'share' && 'Share Your Report'}
                                </h2>
                                {currentAnalysis && (
                                    <span className="text-xs font-medium text-slate-400 border-l border-slate-200 pl-4">
                                        Analyzing: <span className="text-slate-700 font-bold">{idea.title}</span>
                                    </span>
                                )}
                            </div>

                            <div className="flex items-center gap-4">
                                <div className="flex bg-slate-100 p-1 rounded-xl">
                                    {Object.values(PERSONAS).map(p => (
                                        <button
                                            key={p.id}
                                            onClick={() => setSelectedPersona(p.id)}
                                            className={`group relative p-2 rounded-lg transition-all ${selectedPersona === p.id ? 'bg-white shadow-sm ring-1 ring-black/5' : 'hover:bg-slate-200/50'}`}
                                        >
                                            <div className={selectedPersona === p.id ? p.color : 'text-slate-400 group-hover:text-slate-600'}>{p.icon}</div>
                                        </button>
                                    ))}
                                </div>

                                <button
                                    onClick={runAnalysis}
                                    disabled={analyzing || !idea.title || (inputMode === 'manual' && !idea.problem) || (inputMode === 'upload' && !uploadedFile)}
                                    className={`relative overflow-hidden px-6 py-2.5 rounded-xl text-sm font-bold text-white shadow-lg shadow-indigo-200 transition-all active:scale-95 disabled:opacity-70 disabled:active:scale-100 flex items-center gap-2 ${analyzing ? 'bg-slate-800 cursor-wait' : 'bg-indigo-600 hover:bg-indigo-700'}`}
                                >
                                    {analyzing ? <><Loader2 className="w-4 h-4 animate-spin" /><span>Processing...</span></> : <><Sparkles className="w-4 h-4" /><span>Validate Idea</span></>}
                                </button>
                            </div>
                        </header>

                        <div className="flex-1 overflow-y-auto p-8 scroll-smooth">
                            <div className="max-w-7xl mx-auto pb-24">

                                {activeSection === 'dashboard' && (
                                    <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
                                        <div className="lg:col-span-5 space-y-6 h-fit">
                                            {/* Input Form */}
                                            <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 transition-all hover:shadow-md">
                                                <div className="flex items-center justify-between mb-6">
                                                    <h3 className="font-bold text-slate-800 flex items-center gap-2"><Target className="w-5 h-5 text-indigo-600" /> Mission Parameters</h3>
                                                </div>
                                                <div className="space-y-5">
                                                    <div>
                                                        <label className="block text-[11px] font-bold text-slate-400 uppercase tracking-wider mb-2">Venture Name*</label>
                                                        <div className="relative">
                                                            <input value={idea.title} onChange={(e) => setIdea({ ...idea, title: e.target.value })} className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 text-slate-900 font-semibold focus:ring-2 focus:ring-indigo-500 focus:bg-white transition-all outline-none placeholder:font-normal pr-10" placeholder="Project X" />
                                                            <button onClick={generateVentureNames} disabled={nameLoading || !(idea.problem && idea.solution)} className="absolute right-2 top-1/2 -translate-y-1/2 p-1.5 text-slate-400 hover:text-indigo-600 disabled:opacity-30 disabled:hover:text-slate-400 transition-colors">
                                                                {nameLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Sparkles className="w-4 h-4" />}
                                                            </button>
                                                        </div>
                                                        {nameSuggestions.length > 0 && (
                                                            <div className="mt-2 flex flex-wrap gap-2">
                                                                {nameSuggestions.map(name => (
                                                                    <button key={name} onClick={() => { setIdea({ ...idea, title: name }); setNameSuggestions([]); }} className="text-xs font-medium bg-indigo-50 text-indigo-700 px-2 py-1 rounded-full hover:bg-indigo-100">{name}</button>
                                                                ))}
                                                            </div>
                                                        )}
                                                    </div>

                                                    <div className="flex bg-slate-50 p-1 rounded-xl border border-slate-200">
                                                        <button onClick={() => { setInputMode('manual'); setFileError(null); }} className={`flex-1 text-sm font-bold py-2 rounded-lg transition-all ${inputMode === 'manual' ? 'bg-white text-indigo-600 shadow-sm' : 'text-slate-500 hover:bg-slate-100'}`}>Fill Manually</button>
                                                        <button onClick={() => setInputMode('upload')} className={`flex-1 text-sm font-bold py-2 rounded-lg transition-all ${inputMode === 'upload' ? 'bg-white text-indigo-600 shadow-sm' : 'text-slate-500 hover:bg-slate-100'}`}>Upload PDF</button>
                                                    </div>

                                                    {inputMode === 'manual' && (
                                                        <div className="space-y-5 animate-in fade-in duration-300">
                                                            <div><label className="block text-[11px] font-bold text-slate-400 uppercase tracking-wider mb-2">The Pain (Problem)*</label><textarea value={idea.problem} onChange={(e) => setIdea({ ...idea, problem: e.target.value })} className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 text-sm focus:ring-2 focus:ring-indigo-500 focus:bg-white transition-all outline-none h-24 resize-none" placeholder="Who is suffering? Why does it matter?" /></div>
                                                            <div><label className="block text-[11px] font-bold text-slate-400 uppercase tracking-wider mb-2">The Fix (Solution)*</label><textarea value={idea.solution} onChange={(e) => setIdea({ ...idea, solution: e.target.value })} className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 text-sm focus:ring-2 focus:ring-indigo-500 focus:bg-white transition-all outline-none h-24 resize-none" placeholder="How do you solve it 10x better?" /></div>
                                                            <div className="grid grid-cols-2 gap-4">
                                                                <div><label className="block text-[11px] font-bold text-slate-400 uppercase tracking-wider mb-2">Customer</label><input value={idea.targetAudience} onChange={(e) => setIdea({ ...idea, targetAudience: e.target.value })} className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 text-sm focus:ring-2 focus:ring-indigo-500 focus:bg-white outline-none" placeholder="Ideally specific." /></div>
                                                                <div><label className="block text-[11px] font-bold text-slate-400 uppercase tracking-wider mb-2">Unfair Advantage</label><input value={idea.uniqueValue} onChange={(e) => setIdea({ ...idea, uniqueValue: e.target.value })} className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 text-sm focus:ring-2 focus:ring-indigo-500 focus:bg-white outline-none" placeholder="Why you?" /></div>
                                                            </div>
                                                        </div>
                                                    )}

                                                    {inputMode === 'upload' && (
                                                        <div className="space-y-2 animate-in fade-in duration-300">
                                                            <label htmlFor="file-upload" className={`relative block w-full border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-colors ${fileError ? 'border-rose-300' : 'border-slate-300 hover:border-indigo-500'} ${uploadedFile ? 'border-emerald-500 bg-emerald-50/50' : 'bg-slate-50/50 hover:bg-indigo-50/30'}`}>
                                                                <UploadCloud className={`mx-auto w-10 h-10 ${uploadedFile ? 'text-emerald-600' : 'text-slate-400'}`} />
                                                                {uploadedFile ? <span className="mt-2 block text-sm font-bold text-emerald-700">{uploadedFile.name}</span> : <span className="mt-2 block text-sm font-medium text-slate-500">Drag & drop a PDF<span className="block text-xs text-slate-400">Max 10MB</span></span>}
                                                                <input id="file-upload" type="file" className="hidden" accept="application/pdf" onChange={(e) => {
                                                                    const file = e.target.files[0];
                                                                    if (file) {
                                                                        if (file.type !== 'application/pdf') { setFileError('Invalid file type. Please upload a PDF.'); setUploadedFile(null); return; }
                                                                        if (file.size > 10 * 1024 * 1024) { setFileError('File is too large. Max 10MB.'); setUploadedFile(null); return; }
                                                                        setFileError(null); setUploadedFile(file);
                                                                    }
                                                                }} />
                                                            </label>
                                                            {fileError && <p className="text-sm text-rose-600 px-1">{fileError}</p>}
                                                        </div>
                                                    )}
                                                </div>
                                            </div>
                                        </div>

                                        <div className="lg:col-span-7 space-y-6">
                                            {currentAnalysis ? (
                                                <div className="space-y-6 animate-in fade-in slide-in-from-right-4 duration-700">
                                                    {/* Verdict Card */}
                                                    <div className={`rounded-3xl p-8 shadow-xl relative overflow-hidden bg-gradient-to-br ${PERSONAS[selectedPersona].gradient} text-white`}>
                                                        <div className="relative z-10 flex flex-col md:flex-row items-center md:items-start gap-8">
                                                            <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-4 border border-white/20 shadow-inner">
                                                                <ScoreRing score={currentAnalysis.overallScore} />
                                                            </div>
                                                            <div className="flex-1 text-center md:text-left">
                                                                <div className="flex flex-wrap items-center justify-center md:justify-start gap-2 mb-3">
                                                                    <span className="whitespace-nowrap bg-black/20 px-3 py-1 rounded-full text-[10px] font-bold uppercase tracking-widest backdrop-blur-sm border border-white/10">AI Verdict</span>
                                                                    <span className="whitespace-nowrap flex items-center gap-1 text-xs font-medium opacity-80">by {PERSONAS[selectedPersona].name}</span>
                                                                    {currentAnalysis.scoreTrace && <button onClick={() => setActiveAnalysisTab('trace')} className="whitespace-nowrap flex items-center gap-1 text-[10px] font-bold uppercase tracking-widest bg-white/15 hover:bg-white/25 px-2.5 py-1 rounded-full border border-white/20"><ShieldCheck className="w-3 h-3" /> Rules-scored · {currentAnalysis.scoreTrace.grade}</button>}
                                                                </div>
                                                                <h2 className="text-2xl font-bold leading-snug mb-4 text-white text-shadow-sm">"{currentAnalysis.verdict}"</h2>
                                                                <div className="flex flex-wrap gap-2 justify-center md:justify-start">
                                                                    <button onClick={() => setActiveSection('consult')} className="bg-white text-indigo-600 hover:bg-indigo-50 px-4 py-2 rounded-lg text-xs font-bold shadow-lg shadow-black/10 transition-transform active:scale-95 flex items-center gap-2"><MessageSquare className="w-3 h-3" /> Discuss Strategy</button>
                                                                    <button onClick={handleDownloadPdf} className="bg-black/20 hover:bg-black/30 text-white px-4 py-2 rounded-lg text-xs font-bold backdrop-blur-sm transition-colors flex items-center gap-2"><Download className="w-3 h-3" /> Export Report</button>
                                                                </div>
                                                            </div>
                                                        </div>
                                                    </div>

                                                    {/* Analysis Tabs */}
                                                    <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
                                                        <div className="flex border-b border-slate-200 bg-slate-50/50">
                                                            <button onClick={() => setActiveAnalysisTab('analysis')} className={`flex-1 flex items-center justify-center gap-2 px-4 py-3 text-sm font-bold border-b-2 transition-colors ${activeAnalysisTab === 'analysis' ? 'border-indigo-600 text-indigo-600' : 'border-transparent text-slate-500 hover:text-slate-800'}`}><FileText className="w-4 h-4" /> Analysis</button>
                                                            <button onClick={() => setActiveAnalysisTab('trace')} className={`flex-1 flex items-center justify-center gap-2 px-4 py-3 text-sm font-bold border-b-2 transition-colors ${activeAnalysisTab === 'trace' ? 'border-indigo-600 text-indigo-600' : 'border-transparent text-slate-500 hover:text-slate-800'}`}><ShieldCheck className="w-4 h-4" /> Score Trace</button>
                                                            <button onClick={() => setActiveAnalysisTab('competitors')} className={`flex-1 flex items-center justify-center gap-2 px-4 py-3 text-sm font-bold border-b-2 transition-colors ${activeAnalysisTab === 'competitors' ? 'border-indigo-600 text-indigo-600' : 'border-transparent text-slate-500 hover:text-slate-800'}`}><Swords className="w-4 h-4" /> Competitors</button>
                                                            <button onClick={() => setActiveAnalysisTab('pivot')} className={`flex-1 flex items-center justify-center gap-2 px-4 py-3 text-sm font-bold border-b-2 transition-colors ${activeAnalysisTab === 'pivot' ? 'border-indigo-600 text-indigo-600' : 'border-transparent text-slate-500 hover:text-slate-800'}`}><GitBranch className="w-4 h-4" /> Pivot</button>
                                                        </div>

                                                        <div className="p-6">
                                                            {activeAnalysisTab === 'analysis' && (
                                                                <div className="animate-in fade-in duration-300">
                                                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                                                        <div className="space-y-4">
                                                                            <div className="bg-emerald-50 rounded-2xl p-5 border border-emerald-100">
                                                                                <h4 className="text-xs font-bold text-emerald-800 uppercase mb-3 flex items-center gap-2"><CheckCircle2 className="w-4 h-4" /> Winning Factors</h4>
                                                                                <ul className="space-y-2">{currentAnalysis.strengths.slice(0, 3).map((s, i) => <li key={i} className="text-sm text-emerald-900 font-medium flex items-start gap-2"><span className="mt-1.5 w-1.5 h-1.5 rounded-full bg-emerald-500 shrink-0"></span>{s}</li>)}</ul>
                                                                            </div>
                                                                            <div className="bg-rose-50 rounded-2xl p-5 border border-rose-100">
                                                                                <h4 className="text-xs font-bold text-rose-800 uppercase mb-3 flex items-center gap-2"><AlertTriangle className="w-4 h-4" /> Critical Risks</h4>
                                                                                <ul className="space-y-2">{currentAnalysis.weaknesses.slice(0, 3).map((s, i) => <li key={i} className="text-sm text-rose-900 font-medium flex items-start gap-2"><span className="mt-1.5 w-1.5 h-1.5 rounded-full bg-rose-500 shrink-0"></span>{s}</li>)}</ul>
                                                                            </div>
                                                                        </div>
                                                                        <div><h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider text-center mb-2">Dimension Scores</h4><RadarViz currentData={currentAnalysis} /></div>
                                                                    </div>
                                                                </div>
                                                            )}
                                                            {activeAnalysisTab === 'trace' && <ScoreTrace trace={currentAnalysis.scoreTrace} />}
                                                            {/* ... Competitors and Pivot tabs ... */}
                                                            {activeAnalysisTab === 'competitors' && (
                                                                <div className="animate-in fade-in duration-300 space-y-3">
                                                                    {currentAnalysis.competitors.map((comp, idx) => (
                                                                        <div key={idx} className="bg-slate-50 rounded-xl border border-slate-100 p-3 flex items-center gap-4">
                                                                            <div className="w-10 h-10 rounded-full bg-white border border-slate-200 flex items-center justify-center font-bold text-slate-600 shrink-0 shadow-sm">{comp.name.charAt(0)}</div>
                                                                            <div className="flex-1 min-w-0">
                                                                                <div className="flex items-center justify-between"><h4 className="font-bold text-slate-900 text-sm truncate">{comp.name}</h4><span className="text-[10px] font-bold uppercase bg-slate-200 text-slate-600 px-2 py-0.5 rounded-full">{comp.type}</span></div>
                                                                                <p className="text-xs text-slate-500 truncate">{comp.reason}</p>
                                                                            </div>
                                                                            <button onClick={() => analyzeCompetitorWeakness(comp.name)} disabled={competitorLoading === comp.name} className="text-xs font-bold text-indigo-600 hover:text-indigo-800 p-1 disabled:opacity-50">{competitorLoading === comp.name ? <Loader2 className="w-4 h-4 animate-spin" /> : <Sparkles className="w-4 h-4" />}</button>
                                                                        </div>
                                                                    ))}
                                                                    {competitorAnalysis && (
                                                                        <div className="p-3 border-t border-indigo-100 bg-indigo-50 animate-in fade-in duration-300 rounded-xl">
                                                                            <div className="flex items-start gap-2"><SearchCheck className="w-4 h-4 text-indigo-600 shrink-0 mt-0.5" /><p className="text-xs text-indigo-900 leading-relaxed"><strong className="block">Exploitable Weakness of {competitorAnalysis.competitorName}:</strong>{competitorAnalysis.analysis}</p></div>
                                                                        </div>
                                                                    )}
                                                                </div>
                                                            )}
                                                            {activeAnalysisTab === 'pivot' && (
                                                                <div className="animate-in fade-in duration-300">
                                                                    <div className="bg-slate-900 rounded-2xl p-6 text-slate-300 border border-slate-800 flex items-start gap-4 shadow-lg">
                                                                        <div className="bg-indigo-500/20 p-2.5 rounded-xl shrink-0"><Lightbulb className="w-5 h-5 text-indigo-400" /></div>
                                                                        <div><h4 className="text-sm font-bold text-white uppercase tracking-wide mb-1">{currentAnalysis.overallScore < 70 ? 'Recommended Pivot' : 'Growth Opportunity'}</h4><p className="text-sm leading-relaxed">{currentAnalysis.pivotSuggestion}</p></div>
                                                                    </div>
                                                                </div>
                                                            )}
                                                        </div>
                                                    </div>
                                                </div>
                                            ) : (
                                                <div className="h-full min-h-[500px] flex flex-col items-center justify-center text-center p-12 border-2 border-dashed border-slate-200 rounded-3xl bg-slate-50/50 group">
                                                    <div className="w-20 h-20 bg-white rounded-full shadow-sm border border-slate-100 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-500"><Sparkles className="w-8 h-8 text-indigo-400" /></div>
                                                    <h3 className="text-slate-900 font-bold text-lg mb-2">Awaiting Mission Data</h3>
                                                    <p className="text-sm text-slate-500 max-w-xs leading-relaxed">Enter your startup parameters on the left to initialize the validation engine.</p>
                                                </div>
                                            )}
                                        </div>
                                    </div>
                                )}

                                {/* Other Sections (Simplified for brevity but functional) */}
                                {activeSection === 'canvas' && currentAnalysis && <LeanCanvas currentAnalysis={currentAnalysis} idea={idea} analysisId={currentAnalysisId} />}

                                {activeSection === 'consult' && currentAnalysis && (
                                    <div className="max-w-4xl mx-auto h-[600px] flex flex-col bg-white rounded-2xl border border-slate-200 shadow-lg overflow-hidden animate-in fade-in duration-500">
                                        <div className={`p-4 border-b border-slate-100 flex items-center gap-3 bg-slate-50/50`}>
                                            <div className={`w-10 h-10 rounded-full flex items-center justify-center ${PERSONAS[selectedPersona].bgColor} ${PERSONAS[selectedPersona].color}`}>{PERSONAS[selectedPersona].icon}</div>
                                            <div><h3 className="font-bold text-slate-900">{PERSONAS[selectedPersona].name}</h3><p className="text-xs text-slate-500">{PERSONAS[selectedPersona].role}</p></div>
                                        </div>
                                        <div className="flex-1 overflow-y-auto p-6 space-y-6 bg-slate-50/30">
                                            {chatHistory.map((msg, i) => (
                                                <div key={i} className={`flex gap-4 ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}>
                                                    <div className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 ${msg.role === 'user' ? 'bg-indigo-600 text-white' : `${PERSONAS[selectedPersona].bgColor} ${PERSONAS[selectedPersona].color}`}`}>{msg.role === 'user' ? <Users className="w-4 h-4" /> : PERSONAS[selectedPersona].icon}</div>
                                                    <div className={`p-4 rounded-2xl shadow-sm max-w-[80%] text-sm ${msg.role === 'user' ? 'bg-indigo-600 text-white rounded-tr-none' : 'bg-white border border-slate-200 text-slate-700 rounded-tl-none'}`}>{msg.content}</div>
                                                </div>
                                            ))}
                                            {chatLoading && <div className="flex gap-4"><div className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 ${PERSONAS[selectedPersona].bgColor} ${PERSONAS[selectedPersona].color}`}><Loader2 className="w-4 h-4 animate-spin" /></div></div>}
                                            <div ref={chatEndRef} />
                                        </div>
                                        <div className="p-4 bg-white border-t border-slate-100">
                                            <form onSubmit={handleChatSubmit} className="relative">
                                                <input value={chatInput} onChange={(e) => setChatInput(e.target.value)} disabled={chatLoading} placeholder={`Ask ${PERSONAS[selectedPersona].name}...`} className="w-full bg-slate-50 border border-slate-200 rounded-xl pl-4 pr-12 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-all" />
                                                <button type="submit" disabled={!chatInput.trim() || chatLoading} className="absolute right-2 top-1/2 -translate-y-1/2 p-1.5 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:hover:bg-indigo-600 transition-colors"><Send className="w-4 h-4" /></button>
                                            </form>
                                        </div>
                                    </div>
                                )}

                                {/* New Sections */}
                                {activeSection === 'flow' && currentAnalysis && <StrategyFlow idea={idea} analysisId={currentAnalysisId} />}
                                {activeSection === 'market' && currentAnalysis && <MarketIntel idea={idea} analysisId={currentAnalysisId} />}
                                {activeSection === 'scenario' && currentAnalysis && <ScenarioLab analysisId={currentAnalysisId} persona={selectedPersona} />}

                                {/* Pitch Architect, Legal, Scenario, Share, Flow, Market - Implemented similarly or placeholders for brevity */}
                                {activeSection === 'pitch' && currentAnalysis && (
                                    <div className="max-w-4xl mx-auto animate-in fade-in duration-500 text-center">
                                        <h2 className="text-3xl font-bold text-slate-900 mb-4">Pitch Architect</h2>
                                        {!pitchAnalysis && !pitchLoading && <button onClick={runPitchArchitect} className="bg-slate-900 text-white px-8 py-4 rounded-2xl font-bold">Deconstruct & Build Pitch</button>}
                                        {pitchLoading && <Loader2 className="w-10 h-10 animate-spin mx-auto text-indigo-600" />}
                                        {pitchAnalysis && (
                                            <div className="text-left space-y-6 mt-8">
                                                <div className="bg-white p-6 rounded-2xl border border-slate-200">
                                                    <h3 className="font-bold">The Axiom</h3>
                                                    <p className="text-xl italic text-slate-700">"{pitchAnalysis.axiom}"</p>
                                                </div>
                                                <div className="bg-slate-900 p-6 rounded-2xl text-white">
                                                    <h3 className="font-bold">The Hook</h3>
                                                    <p className="text-lg">"{pitchAnalysis.hook}"</p>
                                                </div>
                                            </div>
                                        )}
                                    </div>
                                )}

                                {activeSection === 'legal' && currentAnalysis && (
                                    <div className="max-w-4xl mx-auto animate-in fade-in duration-500">
                                        <h2 className="text-3xl font-bold text-slate-900 mb-4 text-center">Legal Check</h2>
                                        {!legalAnalysis && !legalLoading && <button onClick={runLegalAnalysis} className="w-full py-4 bg-slate-800 text-white font-bold rounded-xl">Run Compliance Check</button>}
                                        {legalLoading && <Loader2 className="w-8 h-8 animate-spin mx-auto" />}
                                        {legalAnalysis && (
                                            <div className="space-y-4 mt-6">
                                                {legalAnalysis.risks.map((r, i) => (
                                                    <div key={i} className="p-4 bg-rose-50 border-l-4 border-rose-500 rounded-r-xl">
                                                        <h4 className="font-bold text-rose-900">{r.title} ({r.severity})</h4>
                                                        <p className="text-rose-800">{r.description}</p>
                                                    </div>
                                                ))}
                                                <div className="p-4 bg-emerald-50 border border-emerald-200 rounded-xl">
                                                    <h4 className="font-bold text-emerald-900">Safe Harbor Tip</h4>
                                                    <p className="text-emerald-800">{legalAnalysis.tip}</p>
                                                </div>
                                            </div>
                                        )}
                                    </div>
                                )}

                                {activeSection === 'vision' && currentAnalysis && (
                                    <VisionGenerator
                                        validationData={{
                                            ventureName: idea.title,
                                            painPoint: idea.problem,
                                            solution: idea.solution,
                                            sector: 'Technology' // Defaulting or could extract from analysis
                                        }}
                                        analysisResults={currentAnalysis}
                                    />
                                )}

                                {activeSection === 'share' && currentAnalysis && (
                                    <div className="max-w-4xl mx-auto animate-in fade-in duration-500 flex flex-col items-center">
                                        <ReportCard ref={reportCardRef} analysis={currentAnalysis} idea={idea} persona={PERSONAS[selectedPersona]} />
                                        <div className="mt-8 flex gap-4">
                                            <button onClick={() => {
                                                if (reportCardRef.current) {
                                                    // Use html-to-image global
                                                    window.htmlToImage.toPng(reportCardRef.current).then(dataUrl => {
                                                        const link = document.createElement('a');
                                                        link.download = 'report.png';
                                                        link.href = dataUrl;
                                                        link.click();
                                                    });
                                                }
                                            }} className="bg-indigo-600 text-white px-6 py-3 rounded-xl font-bold flex items-center gap-2"><DownloadCloud className="w-5 h-5" /> Download PNG</button>
                                        </div>
                                    </div>
                                )}

                            </div>
                        </div>
                    </>
                )}
            </main>
        </div>
    );
}
