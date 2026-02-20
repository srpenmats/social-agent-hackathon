// AI Service - thin wrapper around backend AI endpoints
// Client-side Gemini SDK has been removed; all AI runs server-side.

import { PersonaAPI, SettingsAPI } from './api';

/**
 * Reads uploaded knowledge base documents and auto-generates structured AI persona settings.
 * Proxied through backend POST /api/v1/personas/generate
 */
export async function generatePersonaConfig(documentContext: string) {
  return PersonaAPI.generatePersona(documentContext);
}

/**
 * Drafts a social media comment based on the post context, strictly following persona rules.
 * Proxied through backend POST /api/v1/settings/voice/test
 */
export async function draftComment(postContext: string, personaIdentity: string, personaRules: string[]) {
  const response = await SettingsAPI.testVoice(postContext);
  // Backend returns { results: [{ text, approach, score }] }
  // Return the first result's text for backward compat with ReviewQueue
  if (response.results && response.results.length > 0) {
    return response.results[0].text;
  }
  return "Unable to generate response.";
}
