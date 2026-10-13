const STYLE_PRESETS = {
    cinematic: {
        style: "Cinematic editorial photography meets concept art, 8k resolution, highly detailed",
        lighting: "Golden hour, dramatic shadows with rim lighting, volumetric fog",
        mood: "Aspirational, powerful, transformative, blockbuster movie feel",
        colorPalette: "Deep navy blues, warm golds, clean whites, high contrast"
    },
    minimal: {
        style: "Clean Apple-style product photography, macro details, minimalist composition",
        lighting: "Soft, diffused studio lighting, soft shadows",
        mood: "Elegant, simple, focused, premium",
        colorPalette: "Monochromatic whites and grays with single accent color, matte finish"
    },
    tech: {
        style: "Futuristic tech visualization with data elements, cyberpunk influence, 3D render",
        lighting: "Cool blue ambient with neon accents, glow effects",
        mood: "Innovative, cutting-edge, intelligent, data-driven",
        colorPalette: "Electric blues, cyan accents, dark backgrounds, glass textures"
    },
    illustrated: {
        style: "Modern editorial illustration, Behance-featured style, vector art aesthetic",
        lighting: "Flat with subtle gradients, soft ambient occlusion",
        mood: "Friendly, approachable, creative, startup vibes",
        colorPalette: "Vibrant but harmonious, modern startup aesthetic, pastel accents"
    }
};

const SECTOR_VISUAL_CUES = {
    fintech: "digital interfaces, flowing data streams, secure vault imagery, financial graphs",
    healthtech: "medical innovation, human wellness, DNA strands, caring technology, clean clinical environments",
    edtech: "learning environments, floating books, growth metaphors, neural connections, knowledge sharing",
    construction: "infrastructure, blueprints coming to life, precision engineering, urban development, safety gear",
    ecommerce: "seamless transactions, connected marketplaces, delivery drones, happy customers, packaging",
    saas: "dashboard interfaces, floating UI elements, productivity, connected workflows, cloud computing",
    ai_ml: "neural networks, brain circuitry, intelligent automation, data transformation, robots",
    sustainability: "green technology, solar panels, environmental harmony, leaves merging with tech, clean energy",
    logistics: "global networks, shipping containers, world map connections, efficient movement, supply chain optimization",
    default: "innovation, technology, lightbulbs, rocket ships, upward graphs, progress"
};

const SCORE_TO_VISUAL_EMPHASIS = {
    problem: {
        high: "dramatic before/after transformation showing problem elimination",
        low: "subtle problem acknowledgment with focus on solution potential"
    },
    market: {
        high: "vast scale visualization, global reach, massive adoption imagery, crowd of people",
        low: "focused niche, specialized excellence, boutique quality, single user focus"
    },
    solution: {
        high: "elegant technology in action, seamless user experience showcase, magic happening",
        low: "potential and promise, early-stage innovation aesthetics, blueprints"
    },
    moat: {
        high: "unique, fortress-like defensibility, protected asset, castle metaphor",
        low: "speed and agility, running shoes, first-mover energy, blurred motion"
    },
    velocity: {
        high: "rapid growth trajectory, rocket launch, momentum and acceleration, speed lines",
        low: "steady, sustainable, deliberate progress, planting seeds"
    }
};

export const buildVisionPrompt = ({
    validationData,
    analysisResults,
    style = 'cinematic',
}) => {
    const {
        ventureName,
        painPoint,
        solution,
        sector
    } = validationData;

    const {
        strengths = [],
        scores
    } = analysisResults;

    // Get style preset
    const stylePreset = STYLE_PRESETS[style];

    // Get sector-specific visual cues
    const sectorKey = sector?.toLowerCase().replace(/[^a-z_]/g, '') || 'default';
    const sectorCues = SECTOR_VISUAL_CUES[sectorKey] || SECTOR_VISUAL_CUES.default;

    // Determine dominant strength from scores
    const entries = Object.entries(scores);
    const dominantDimension = entries.sort((a, b) => b[1] - a[1])[0];

    const dominantKey = dominantDimension ? dominantDimension[0] : 'solution';
    const dominantScore = dominantDimension ? dominantDimension[1] : 70;

    // Get visual emphasis based on score
    const scoreLevel = dominantScore >= 70 ? 'high' : 'low';
    const visualEmphasis = SCORE_TO_VISUAL_EMPHASIS[dominantKey]?.[scoreLevel] ||
        SCORE_TO_VISUAL_EMPHASIS.solution.high;

    const keyStrength = strengths[0] || 'innovative solution';

    return `Create a cinematic, aspirational hero image for a startup pitch deck.
  
  STARTUP CONTEXT:
  - Name: ${ventureName}
  - Problem solved: ${painPoint}
  - Solution: ${solution}
  - Visual domain: ${sectorCues}
  
  VISUAL DIRECTION:
  - Primary emphasis: ${visualEmphasis}
  - Key strength to subtly visualize: "${keyStrength}"
  - Style: ${stylePreset.style}
  - Lighting: ${stylePreset.lighting}
  - Mood: ${stylePreset.mood}
  - Color palette: ${stylePreset.colorPalette}
  
  COMPOSITION REQUIREMENTS:
  - Aspect ratio: 16:9 (Landscape)
  - No text, logos, or watermarks in the image itself.
  - Leave breathing room/negative space in lower-third or left side for potential text overlay.
  - Photorealistic with subtle conceptual/futuristic elements (unless style is Illustrated).
  - Show the TRANSFORMATION - the world AFTER this solution exists.
  - Evoke emotion: "This is the future I want to build".
  
  AVOID:
  - Generic stock photo aesthetics.
  - Cluttered compositions.
  - Text, words, or typography inside the artwork.
  - Distorted faces or hands.`;
};
