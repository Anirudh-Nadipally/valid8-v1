import { GoogleGenAI } from "@google/genai";

// Use gemini-2.5-flash-image for standard generation
const MODEL_NAME = 'gemini-2.5-flash-002'; // Updated to valid model if needed, but keeping original or close equivalent if available. 
// "gemini-2.5-flash-image" might be a custom or preview model. 
// I will stick to what the reference code had: 'gemini-2.5-flash-image'. 
// If that fails, I'll advise user. Actually the reference said: gemini-2.5-flash-image
// I will use that.

const TARGET_MODEL = 'gemini-2.0-flash-exp'; // Using a known working model for image generation if 2.5 isn't public yet, or strictly following text.
// Actually, for image generation via GenAI SDK, it usually uses the 'imagen-3.0-generate-001' or similar, OR multimodal models.
// But the reference code uses: 'gemini-2.5-flash-image' and `imageConfig`.
// I will trust the reference code provided by the user implicitly.

const REFERENCE_MODEL = 'gemini-2.5-flash-image';

export const generateImageWithGemini = async (prompt) => {
    const apiKey = import.meta.env.VITE_GOOGLE_API_KEY;
    if (!apiKey) {
        throw new Error("API Key is missing. Please set VITE_GOOGLE_API_KEY in .env.");
    }

    const ai = new GoogleGenAI({ apiKey });

    try {
        const response = await ai.models.generateContent({
            model: REFERENCE_MODEL,
            contents: prompt,
            config: {
                imageConfig: {
                    aspectRatio: "16:9"
                }
            }
        });

        if (!response.candidates || response.candidates.length === 0) {
            throw new Error("No candidates returned from Gemini.");
        }

        const candidate = response.candidates[0];
        const parts = candidate.content?.parts;

        if (!parts) {
            throw new Error("No content parts in response.");
        }

        // Iterate to find the image part
        for (const part of parts) {
            if (part.inlineData && part.inlineData.data) {
                const mimeType = part.inlineData.mimeType || 'image/png';
                const base64Data = part.inlineData.data;
                return `data:${mimeType};base64,${base64Data}`;
            }
        }

        throw new Error("No image data found in response parts.");

    } catch (error) {
        console.error("Gemini Image Generation Error:", error);
        throw error;
    }
};
