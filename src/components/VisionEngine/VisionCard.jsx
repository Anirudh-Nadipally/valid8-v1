import React, { useState } from 'react';
import { generateSocialCard } from '../../utils/socialCardGenerator';

const VisionCard = ({
    image,
    analysisResults,
    ventureName,
    onRegenerate
}) => {
    const [isDownloading, setIsDownloading] = useState(false);
    const [isCreatingCard, setIsCreatingCard] = useState(false);

    const handleDownloadHero = () => {
        setIsDownloading(true);
        const link = document.createElement('a');
        link.href = image.url;
        link.download = `${ventureName.replace(/\s+/g, '_')}_Vision_Hero.png`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        setIsDownloading(false);
    };

    const handleDownloadSocial = async () => {
        try {
            setIsCreatingCard(true);
            const dataUrl = await generateSocialCard({
                heroImageUrl: image.url,
                ventureName,
                analysisResults
            });

            const link = document.createElement('a');
            link.href = dataUrl;
            link.download = `${ventureName.replace(/\s+/g, '_')}_Social_Card.png`;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        } catch (e) {
            console.error("Failed to generate social card", e);
            alert("Could not generate social card.");
        } finally {
            setIsCreatingCard(false);
        }
    };

    return (
        <div className="w-full bg-slate-800 rounded-xl overflow-hidden border border-slate-700 shadow-2xl transition-all hover:border-slate-600">
            {/* Image Container */}
            <div className="relative group aspect-video w-full bg-slate-900 overflow-hidden">
                <img
                    src={image.url}
                    alt={`AI Vision for ${ventureName}`}
                    className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-105"
                />

                {/* Hover Overlay - Clean design without branding */}
                <div className="absolute inset-0 bg-gradient-to-t from-slate-900/80 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex flex-col justify-end p-6">
                    <p className="text-white font-medium mb-1 drop-shadow-md">{ventureName}</p>
                    <p className="text-slate-300 text-xs drop-shadow-md opacity-80">Vision {image.style} Asset</p>
                </div>
            </div>

            {/* Action Bar */}
            <div className="p-6 flex flex-col md:flex-row items-center justify-between gap-4">
                <div className="flex items-center gap-3">
                    <div className={`
            flex items-center justify-center w-12 h-12 rounded-full font-bold text-white text-lg shadow-lg
            ${analysisResults.overallScore >= 80 ? 'bg-emerald-500' : analysisResults.overallScore >= 60 ? 'bg-amber-500' : 'bg-red-500'}
          `}>
                        {analysisResults.overallScore}
                    </div>
                    <div>
                        <h3 className="text-white font-semibold">{ventureName}</h3>
                        <p className="text-slate-400 text-sm">Vision {image.style} • {new Date(image.generatedAt).toLocaleTimeString()}</p>
                    </div>
                </div>

                <div className="flex flex-wrap gap-3">
                    {/* Primary Download Button */}
                    <button
                        onClick={handleDownloadHero}
                        disabled={isDownloading}
                        className="px-5 py-2.5 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white rounded-xl text-sm font-bold transition-all shadow-lg shadow-emerald-900/30 flex items-center gap-2"
                    >
                        {isDownloading ? 'Downloading...' : (
                            <>
                                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" /></svg>
                                Download Image
                            </>
                        )}
                    </button>

                    {/* Social Card Button */}
                    <button
                        onClick={handleDownloadSocial}
                        disabled={isCreatingCard}
                        className="px-5 py-2.5 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white rounded-xl text-sm font-bold transition-all shadow-lg shadow-blue-900/30 flex items-center gap-2"
                    >
                        {isCreatingCard ? 'Creating...' : (
                            <>
                                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z" /></svg>
                                Share Card
                            </>
                        )}
                    </button>

                    {/* Regenerate Button */}
                    <button
                        onClick={onRegenerate}
                        className="px-4 py-2.5 bg-slate-700 hover:bg-slate-600 text-white rounded-xl text-sm font-medium transition-all flex items-center gap-2"
                        title="Generate New Vision"
                    >
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" /></svg>
                        New Style
                    </button>
                </div>
            </div>
        </div>
    );
};

export default VisionCard;
