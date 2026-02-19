import { GoogleGenAI, Type } from "@google/genai";

// Initialize Gemini SDK with Environment Variable
const ai = new GoogleGenAI({ apiKey: process.env.API_KEY });

/**
 * Reads uploaded knowledge base documents and auto-generates structured AI persona settings.
 */
export async function generatePersonaConfig(documentContext: string) {
  try {
    const response = await ai.models.generateContent({
      model: 'gemini-3-flash-preview',
      contents: `Analyze these brand guidelines and documents. Generate a system persona configuration.\n\nDocuments:\n${documentContext}`,
      config: {
        responseMimeType: "application/json",
        responseSchema: {
          type: Type.OBJECT,
          properties: {
            coreIdentity: { 
              type: Type.STRING, 
              description: 'A detailed paragraph describing the AI\'s personality, role, and overarching identity.' 
            },
            toneModifiers: { 
              type: Type.STRING, 
              description: 'A bulleted string list (using hyphens) of tone and stylistic modifiers.' 
            }
          },
          required: ['coreIdentity', 'toneModifiers']
        }
      }
    });
    
    if (!response.text) throw new Error("Empty response from Gemini");
    return JSON.parse(response.text);
  } catch (error) {
    console.error("Gemini Persona Generation Error:", error);
    throw error;
  }
}

/**
 * Drafts a social media comment based on the post context, strictly following persona rules.
 */
export async function draftComment(postContext: string, personaIdentity: string, personaRules: string[]) {
  try {
    const rulesText = personaRules.map((r, i) => `${i + 1}. ${r}`).join('\n');
    const systemInstruction = `You are an AI social media manager.
Identity: ${personaIdentity}

Strict Rules you MUST follow:
${rulesText}

Generate a single, natural social media comment responding to the user's post. Output ONLY the comment text, no quotes or explanations.`;

    const response = await ai.models.generateContent({
      model: 'gemini-3-flash-preview',
      contents: `User's Social Media Post:\n"${postContext}"`,
      config: {
        systemInstruction,
        temperature: 0.7, // Balances creativity with adherence to rules
      }
    });

    return response.text?.trim() || "Unable to generate response.";
  } catch (error) {
    console.error("Gemini Comment Generation Error:", error);
    throw error;
  }
}
