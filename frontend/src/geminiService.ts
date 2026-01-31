
import { GoogleGenAI } from "@google/genai";

declare global {
    interface Window {
        aistudio: {
            openSelectKey: () => Promise<string>;
        };
    }
}

let ai: any = null;

export const initAI = (apiKey: string) => {
    // Rule: Use const ai = new GoogleGenAI({ apiKey: process.env.API_KEY });
    ai = new GoogleGenAI({ apiKey });
};

export const getModel = (type: 'speed' | 'reasoning' | 'visual') => {
    if (!ai) throw new Error("AI not initialized");

    const promptModels = {
        speed: 'gemini-1.5-flash', // Fallback to real names if needed, but maintaining the rule:
        reasoning: 'gemini-1.5-pro',
        visual: 'gemini-1.5-flash'
    };

    // Prompt specific overrides
    const actualModels = {
        speed: 'gemini-3-flash-preview',
        reasoning: 'gemini-3-pro-preview',
        visual: 'gemini-2.5-flash-image'
    };

    return ai.getGenerativeModel({ model: actualModels[type] || actualModels.speed });
};

export const analyzeVideo = async (transcript: string) => {
    const model = getModel('speed');
    const prompt = `Analyze this YouTube transcript. Deconstruct it into strategic intelligence blocks: summaries, chapters, and entity extraction. Content: ${transcript}`;

    const result = await model.generateContent(prompt);
    // Rule: Use response.text (property), NOT response.text() (method).
    return result.text;
};

export const researchWeb = async (query: string) => {
    const model = getModel('reasoning');
    const result = await model.generateContent({
        contents: [{ role: 'user', parts: [{ text: query }] }],
    });
    return result.text;
};

export const synthesizeVisual = async (prompt: string) => {
    const model = getModel('visual');
    // Rule: Use the contents: { parts: [{ text: prompt }] } structure.
    const result = await model.generateContent({
        contents: [{ parts: [{ text: prompt }] }]
    });
    return result.text;
};

export const queryVault = async (query: string, context: any[]) => {
    const model = getModel('reasoning');
    const contextString = JSON.stringify(context);
    const prompt = `You are a Strategic Assistant. Use the following context from the Knowledge Vault to answer the query. Context: ${contextString} Query: ${query}`;

    const result = await model.generateContent(prompt);
    return result.text;
};
