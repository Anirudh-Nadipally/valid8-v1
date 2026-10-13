import React from 'react';

const GenerationProgress = ({ progress, message }) => {
    return (
        <div className="w-full max-w-lg mx-auto p-8 text-center bg-slate-800 rounded-xl border border-slate-700 shadow-xl">
            <div className="mb-6 relative">
                <div className="w-16 h-16 mx-auto border-4 border-blue-500/30 border-t-blue-500 rounded-full animate-spin"></div>
                <div className="absolute inset-0 flex items-center justify-center text-xs font-bold text-blue-400">
                    {Math.round(progress)}%
                </div>
            </div>
            <h3 className="text-xl font-semibold text-white mb-2 animate-pulse">
                {message}
            </h3>
            <p className="text-slate-400 text-sm mb-4">
                Valid8 AI is visualizing your venture data...
            </p>

            {/* Progress Bar */}
            <div className="w-full bg-slate-700 rounded-full h-2.5 mb-2 overflow-hidden">
                <div
                    className="bg-gradient-to-r from-blue-600 to-emerald-500 h-2.5 rounded-full transition-all duration-500 ease-out"
                    style={{ width: `${progress}%` }}
                ></div>
            </div>

            <div className="flex justify-between text-xs text-slate-500 mt-2">
                <span>Analysis</span>
                <span>Prompting</span>
                <span>Generation</span>
                <span>Finalizing</span>
            </div>
        </div>
    );
};

export default GenerationProgress;
