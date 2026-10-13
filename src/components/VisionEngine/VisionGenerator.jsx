import React, { useState, useRef } from 'react';
import { buildVisionPrompt } from '../../services/promptBuilder';
import { generateImageWithGemini } from '../../services/imageService';
import GenerationProgress from './GenerationProgress';
import VisionCard from './VisionCard';

const STYLES = [
    {
        id: 'cinematic',
        label: 'Cinematic',
        description: 'Editorial photography meets concept art',
        icon: '🎬'
    },
    {
        id: 'minimal',
        label: 'Minimal',
        description: 'Clean, Apple-style product aesthetic',
        icon: '⚪'
    },
    {
        id: 'tech',
        label: 'Tech Forward',
        description: 'Futuristic, data-driven visuals',
        icon: '⚡'
    },
    {
        id: 'illustrated',
        label: 'Illustrated',
        description: 'Modern editorial illustration',
        icon: '🎨'
    }
];

const VisionGenerator = ({ validationData, analysisResults }) => {
    const [selectedStyle, setSelectedStyle] = useState('cinematic');
    const [isGenerating, setIsGenerating] = useState(false);
    const [progress, setProgress] = useState(0);
    const [generatedImage, setGeneratedImage] = useState(null);
    const [error, setError] = useState(null);

    // Ref to hold interval ID so we can clear it reliably
    const progressInterval = useRef(null);

    const handleGenerate = async () => {
        setIsGenerating(true);
        setError(null);
        setProgress(10); // Start

        try {
            // 1. Build Prompt
            const prompt = buildVisionPrompt({
                validationData,
                analysisResults,
                style: selectedStyle
            });
            setProgress(30);

            // 2. Call API
            // Simulate progress for UX while waiting for promise
            if (progressInterval.current) clearInterval(progressInterval.current);
            progressInterval.current = setInterval(() => {
                setProgress(prev => Math.min(prev + 5, 85));
            }, 500);

            const imageUrl = await generateImageWithGemini(prompt);

            setProgress(100);

            // 3. Set Result
            setGeneratedImage({
                url: imageUrl,
                prompt: prompt,
                style: selectedStyle,
                imageType: 'hero',
                generatedAt: new Date().toISOString()
            });

        } catch (err) {
            console.error("Generation failed:", err);
            setError(err.message || "Failed to generate image. Please try again.");
        } finally {
            if (progressInterval.current) {
                clearInterval(progressInterval.current);
                progressInterval.current = null;
            }
            setIsGenerating(false);
        }
    };

    return (
        <div className="w-full max-w-5xl mx-auto my-6 bg-slate-900/50 p-1 rounded-2xl">

            {/* Header Section */}
            <div className="mb-8 p-6 pb-0">
                <div className="flex items-center gap-2 mb-2">
                    <span className="text-2xl">✨</span>
                    <h2 className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-emerald-400">
                        Venture Vision Engine
                    </h2>
                </div>
                <p className="text-slate-400">
                    Transform your validated idea into professional visual assets using Generative AI.
                </p>
            </div>

            {/* Main Content Area */}
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 md:p-8">

                {/* State: Error */}
                {error && (
                    <div className="mb-6 p-4 bg-red-900/20 border border-red-500/50 text-red-200 rounded-lg flex items-center justify-between">
                        <span>{error}</span>
                        <button onClick={() => setError(null)} className="text-sm underline">Dismiss</button>
                    </div>
                )}

                {/* State: Generating */}
                {isGenerating ? (
                    <div className="py-12">
                        <GenerationProgress
                            progress={progress}
                            message={progress < 30 ? "Crafting visual prompts..." : "AI is painting your vision..."}
                        />
                    </div>
                ) : generatedImage ? (
                    /* State: Result Display */
                    <div className="space-y-6 animate-fade-in">
                        <VisionCard
                            image={generatedImage}
                            analysisResults={analysisResults}
                            ventureName={validationData.ventureName}
                            onRegenerate={() => setGeneratedImage(null)}
                        />
                    </div>
                ) : (
                    /* State: Configuration (Initial) */
                    <div className="space-y-8">

                        {/* Style Selector */}
                        <div>
                            <label className="block text-sm font-medium text-slate-300 mb-4">Choose a Visual Style</label>
                            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                                {STYLES.map((style) => (
                                    <button
                                        key={style.id}
                                        onClick={() => setSelectedStyle(style.id)}
                                        className={`
                      relative p-4 rounded-xl border-2 text-left transition-all duration-200 group
                      ${selectedStyle === style.id
                                                ? 'border-blue-500 bg-blue-900/20'
                                                : 'border-slate-700 bg-slate-800/50 hover:border-slate-600 hover:bg-slate-800'
                                            }
                    `}
                                    >
                                        <div className="text-2xl mb-2">{style.icon}</div>
                                        <div className={`font-semibold mb-1 ${selectedStyle === style.id ? 'text-white' : 'text-slate-200'}`}>
                                            {style.label}
                                        </div>
                                        <div className="text-xs text-slate-400 group-hover:text-slate-300">
                                            {style.description}
                                        </div>

                                        {selectedStyle === style.id && (
                                            <div className="absolute top-3 right-3 w-4 h-4 bg-blue-500 rounded-full shadow-lg shadow-blue-500/50 animate-pulse"></div>
                                        )}
                                    </button>
                                ))}
                            </div>
                        </div>

                        {/* Prompt Preview (Optional/Advanced) */}
                        <div className="p-4 bg-slate-950 rounded-lg border border-slate-800">
                            <div className="flex items-center gap-2 mb-2 text-xs text-slate-500 uppercase tracking-wider font-semibold">
                                <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                                AI Context Info
                            </div>
                            <p className="text-sm text-slate-400 italic">
                                Generating based on <span className="text-blue-400 font-medium">{analysisResults.strengths?.[0] || 'your core strengths'}</span> and a score of <span className="text-emerald-400 font-medium">{analysisResults.overallScore}</span>.
                            </p>
                        </div>

                        {/* Action Button */}
                        <button
                            onClick={handleGenerate}
                            className="w-full py-4 bg-gradient-to-r from-blue-600 to-emerald-600 hover:from-blue-500 hover:to-emerald-500 text-white font-bold rounded-xl shadow-lg shadow-blue-900/20 transition-all transform active:scale-[0.98] flex items-center justify-center gap-3 text-lg"
                        >
                            <span className="text-xl">✨</span>
                            Generate Vision Asset
                        </button>
                    </div>
                )}
            </div>
        </div>
    );
};

export default VisionGenerator;
