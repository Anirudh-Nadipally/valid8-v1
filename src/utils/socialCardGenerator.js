export const generateSocialCard = async ({
    heroImageUrl,
    ventureName,
    analysisResults,
}) => {
    const outputSize = { width: 1200, height: 630 };

    return new Promise((resolve, reject) => {
        const canvas = document.createElement('canvas');
        canvas.width = outputSize.width;
        canvas.height = outputSize.height;
        const ctx = canvas.getContext('2d');

        if (!ctx) {
            reject(new Error("Could not get canvas context"));
            return;
        }

        const heroImg = new Image();
        // Important for cross-origin if using remote URLs, but we are using base64 mostly
        heroImg.crossOrigin = 'anonymous';

        heroImg.onload = () => {
            // 1. Draw Hero Image (Cover Fit)
            drawImageCover(ctx, heroImg, outputSize.width, outputSize.height);

            // 2. Add Gradient Overlay (Bottom Up)
            const gradient = ctx.createLinearGradient(0, outputSize.height * 0.4, 0, outputSize.height);
            gradient.addColorStop(0, 'rgba(15, 23, 42, 0)'); // transparent slate-900
            gradient.addColorStop(0.6, 'rgba(15, 23, 42, 0.9)');
            gradient.addColorStop(1, 'rgba(15, 23, 42, 1)');
            ctx.fillStyle = gradient;
            ctx.fillRect(0, 0, outputSize.width, outputSize.height);

            // 3. Draw Score Badge
            drawScoreBadge(ctx, analysisResults.overallScore, {
                x: 80,
                y: outputSize.height - 150
            });

            // 4. Draw Venture Name
            ctx.font = 'bold 56px Inter, system-ui, sans-serif';
            ctx.fillStyle = '#FFFFFF';
            ctx.fillText(ventureName, 180, outputSize.height - 110);

            // 5. Draw Verdict Quote (Truncated)
            const verdict = analysisResults.verdictQuote || "Validated Idea";
            const truncatedQuote = verdict.length > 70
                ? verdict.substring(0, 67) + '...'
                : verdict;

            ctx.font = '30px Inter, system-ui, sans-serif';
            ctx.fillStyle = 'rgba(255, 255, 255, 0.9)';
            ctx.fillText(`"${truncatedQuote}"`, 180, outputSize.height - 60);

            // 6. Draw Valid8 Pro Attribution
            ctx.font = '20px Inter, system-ui, sans-serif';
            ctx.fillStyle = 'rgba(96, 165, 250, 0.8)'; // blue-400
            ctx.textAlign = 'right';
            ctx.fillText('Validated with Valid8 Pro', outputSize.width - 60, outputSize.height - 40);

            // Return Data URL
            resolve(canvas.toDataURL('image/png'));
        };

        heroImg.onerror = () => {
            reject(new Error('Failed to load hero image onto canvas'));
        };

        heroImg.src = heroImageUrl;
    });
};

const drawImageCover = (ctx, img, targetWidth, targetHeight) => {
    const imgRatio = img.width / img.height;
    const targetRatio = targetWidth / targetHeight;

    let drawWidth, drawHeight, offsetX, offsetY;

    if (imgRatio > targetRatio) {
        drawHeight = targetHeight;
        drawWidth = img.width * (targetHeight / img.height);
        offsetX = (targetWidth - drawWidth) / 2;
        offsetY = 0;
    } else {
        drawWidth = targetWidth;
        drawHeight = img.height * (targetWidth / img.width);
        offsetX = 0;
        offsetY = (targetHeight - drawHeight) / 2;
    }

    ctx.drawImage(img, offsetX, offsetY, drawWidth, drawHeight);
};

const drawScoreBadge = (ctx, score, position) => {
    const radius = 45;
    const { x, y } = position;

    // Background Circle
    ctx.beginPath();
    ctx.arc(x, y, radius, 0, Math.PI * 2);
    ctx.fillStyle = getScoreColor(score);
    ctx.fill();

    // Shadow
    ctx.shadowColor = 'rgba(0,0,0,0.5)';
    ctx.shadowBlur = 10;
    ctx.shadowOffsetX = 0;
    ctx.shadowOffsetY = 4;

    // Inner Ring
    ctx.beginPath();
    ctx.arc(x, y, radius - 4, 0, Math.PI * 2);
    ctx.lineWidth = 2;
    ctx.strokeStyle = 'rgba(255,255,255,0.3)';
    ctx.stroke();

    // Score Text
    ctx.shadowColor = 'transparent'; // Reset shadow
    ctx.font = 'bold 36px Inter, system-ui, sans-serif';
    ctx.fillStyle = '#FFFFFF';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(score.toString(), x, y + 2);

    // Reset alignment
    ctx.textAlign = 'left';
    ctx.textBaseline = 'alphabetic';
};

const getScoreColor = (score) => {
    if (score >= 80) return '#10B981'; // Green
    if (score >= 60) return '#F59E0B'; // Amber
    return '#EF4444'; // Red
};
