import React, { useState, useEffect } from 'react';
import { SettingsAPI, ApiError } from '../services/api';

export default function SettingsBrandVoice() {
  const [voiceConfig, setVoiceConfig] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isSaving, setIsSaving] = useState(false);

  // Editable fields
  const [coreIdentity, setCoreIdentity] = useState('');
  const [toneModifiers, setToneModifiers] = useState('');
  const [rules, setRules] = useState<{ id: string; text: string }[]>([]);
  const [noGoZones, setNoGoZones] = useState('');
  const [positiveExamples, setPositiveExamples] = useState<{ context: string; msg: string }[]>([]);
  const [negativeExamples, setNegativeExamples] = useState<{ context: string; msg: string; reason: string }[]>([]);

  // Tester state
  const [testContext, setTestContext] = useState('');
  const [testResults, setTestResults] = useState<any[]>([]);
  const [isTesting, setIsTesting] = useState(false);

  useEffect(() => {
    SettingsAPI.getVoiceConfig()
      .then((config) => {
        setVoiceConfig(config);
        setCoreIdentity(config.core_identity || '');
        setToneModifiers(config.tone_modifiers || '');
        setRules((config.rules || []).map((r: string, i: number) => ({ id: String(i + 1).padStart(2, '0'), text: r })));
        setNoGoZones(config.no_go_zones || '');
        setPositiveExamples(config.positive_examples || []);
        setNegativeExamples(config.negative_examples || []);
      })
      .catch((e) => {
        setError(e instanceof ApiError ? e.detail : 'Failed to load voice configuration.');
      })
      .finally(() => setIsLoading(false));
  }, []);

  const handleSave = async () => {
    setIsSaving(true);
    try {
      await SettingsAPI.updateVoiceConfig({
        core_identity: coreIdentity,
        tone_modifiers: toneModifiers,
        rules: rules.map(r => r.text),
        no_go_zones: noGoZones,
        positive_examples: positiveExamples,
        negative_examples: negativeExamples,
      });
    } catch (e) {
      console.error('Save failed:', e);
    } finally {
      setIsSaving(false);
    }
  };

  const handleTest = async () => {
    if (!testContext.trim()) return;
    setIsTesting(true);
    setTestResults([]);
    try {
      const response = await SettingsAPI.testVoice(testContext);
      setTestResults(response.results || []);
    } catch (e) {
      setTestResults([{ approach: 'Error', score: '0/100', text: 'Failed to generate test comment. Check backend connection.' }]);
    } finally {
      setIsTesting(false);
    }
  };

  const addRule = () => {
    const nextId = String(rules.length + 1).padStart(2, '0');
    setRules([...rules, { id: nextId, text: '' }]);
  };

  const removeRule = (idx: number) => {
    setRules(rules.filter((_, i) => i !== idx));
  };

  const updateRule = (idx: number, text: string) => {
    setRules(rules.map((r, i) => i === idx ? { ...r, text } : r));
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-16">
        <div className="w-8 h-8 border-4 border-[#00B894] border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center py-16">
        <span className="material-symbols-outlined text-4xl text-red-400 mb-4">error_outline</span>
        <p className="text-gray-400 text-sm mb-4">{error}</p>
      </div>
    );
  }

  return (
    <div className="max-w-[1600px] mx-auto grid grid-cols-12 gap-8">
      {/* Left Column - Configurations */}
      <div className="col-span-12 lg:col-span-8 space-y-6">
        <div className="flex items-start justify-between">
          <div>
            <h2 className="text-lg font-semibold text-white">Voice Configuration</h2>
            <p className="text-sm text-gray-400 mt-1">Define the core personality and rules for the AI Agent. These settings directly influence the <span className="mono-text text-[#00B894] bg-[#00B894]/10 px-1 rounded text-xs">system_prompt</span>.</p>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={handleSave}
              disabled={isSaving}
              className="px-4 py-2 bg-[#00B894] hover:bg-[#00a383] text-white rounded-lg text-sm font-medium transition-colors disabled:opacity-50"
            >
              {isSaving ? 'Saving...' : 'Save Changes'}
            </button>
          </div>
        </div>

        {/* Persona Traits */}
        <div className="bg-[#131828] border border-[#2D3748] rounded-lg overflow-hidden">
          <div className="px-4 py-3 bg-[#1E2538] border-b border-[#2D3748] flex justify-between items-center">
            <div className="flex items-center gap-2">
              <span className="material-symbols-outlined text-[#00B894] text-sm">face</span>
              <h3 className="text-sm font-semibold text-white uppercase tracking-wider">Persona Traits</h3>
            </div>
          </div>
          <div className="p-4 grid grid-cols-2 gap-4">
            <div className="space-y-1">
              <label className="text-xs text-gray-400 font-medium uppercase">Core Identity</label>
              <textarea
                className="w-full bg-[#0B0F1A] border border-[#2D3748] rounded text-sm text-gray-100 p-3 focus:ring-1 focus:ring-[#00B894] focus:border-[#00B894] mono-text resize-none h-24 outline-none"
                value={coreIdentity}
                onChange={(e) => setCoreIdentity(e.target.value)}
              />
            </div>
            <div className="space-y-1">
              <label className="text-xs text-gray-400 font-medium uppercase">Tone Modifiers</label>
              <textarea
                className="w-full bg-[#0B0F1A] border border-[#2D3748] rounded text-sm text-gray-100 p-3 focus:ring-1 focus:ring-[#00B894] focus:border-[#00B894] mono-text resize-none h-24 outline-none"
                value={toneModifiers}
                onChange={(e) => setToneModifiers(e.target.value)}
              />
            </div>
          </div>
        </div>

        {/* Comment Rules */}
        <div className="bg-[#131828] border border-[#2D3748] rounded-lg overflow-hidden">
          <div className="px-4 py-3 bg-[#1E2538] border-b border-[#2D3748] flex justify-between items-center">
            <div className="flex items-center gap-2">
              <span className="material-symbols-outlined text-blue-400 text-sm">gavel</span>
              <h3 className="text-sm font-semibold text-white uppercase tracking-wider">Comment Rules</h3>
            </div>
            <span className="text-xs text-gray-400 mono-text">active_rules: {rules.length}</span>
          </div>
          <div className="p-4 space-y-3">
            {rules.map((rule, idx) => (
              <div key={idx} className="flex items-center gap-3 p-3 bg-[#0B0F1A] rounded border border-[#2D3748]">
                <span className="text-[#00B894] mono-text text-xs">{rule.id}</span>
                <input
                  className="flex-1 bg-transparent border-none text-sm text-white focus:ring-0 px-0 outline-none"
                  type="text"
                  value={rule.text}
                  onChange={(e) => updateRule(idx, e.target.value)}
                />
                <button onClick={() => removeRule(idx)} className="text-gray-400 hover:text-[#E17055]">
                  <span className="material-symbols-outlined text-sm">close</span>
                </button>
              </div>
            ))}
            <button onClick={addRule} className="w-full py-2 border border-dashed border-[#2D3748] text-gray-400 text-xs uppercase font-medium hover:border-[#00B894] hover:text-[#00B894] transition-colors rounded">
              + Add Rule
            </button>
          </div>
        </div>

        {/* No-Go Zones */}
        <div className="bg-[#131828] border border-[#2D3748] rounded-lg overflow-hidden">
          <div className="px-4 py-3 bg-[#1E2538] border-b border-[#2D3748] flex justify-between items-center">
            <div className="flex items-center gap-2">
              <span className="material-symbols-outlined text-[#E17055] text-sm">do_not_disturb_on</span>
              <h3 className="text-sm font-semibold text-white uppercase tracking-wider">No-Go Zones</h3>
            </div>
          </div>
          <div className="p-4">
            <textarea
              className="w-full bg-[#0B0F1A] border border-[#E17055]/30 rounded text-sm text-gray-100 p-3 focus:ring-1 focus:ring-[#E17055] focus:border-[#E17055] mono-text resize-none h-24 placeholder-gray-600 outline-none"
              placeholder="Enter topics to avoid completely..."
              value={noGoZones}
              onChange={(e) => setNoGoZones(e.target.value)}
            />
          </div>
        </div>

        {/* Examples Grid */}
        <div className="grid grid-cols-2 gap-6 pb-8">
          {/* Positive Examples */}
          <div className="bg-[#131828] border border-[#2D3748] rounded-lg overflow-hidden flex flex-col">
            <div className="px-4 py-3 bg-[#1E2538] border-b border-[#2D3748] flex justify-between items-center border-l-4 border-l-[#00B894]">
              <h3 className="text-sm font-semibold text-white uppercase tracking-wider">Positive Examples</h3>
              <span className="bg-[#00B894]/20 text-[#00B894] text-[10px] px-2 py-0.5 rounded font-mono">DO THIS</span>
            </div>
            <div className="p-4 space-y-4 flex-1">
              {positiveExamples.map((ex, i) => (
                <div key={i} className="p-3 bg-[rgba(0,184,148,0.1)] rounded border border-[#00B894]/30 relative group">
                  <div className="text-[10px] text-[#00B894] font-bold mb-1 uppercase tracking-wide">Context: {ex.context}</div>
                  <p className="text-sm text-gray-200 italic">{ex.msg}</p>
                  <div className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity flex gap-1">
                    <button className="bg-[#E17055] text-white p-1 rounded hover:bg-[#c05a42]"><span className="material-symbols-outlined text-[14px]">delete</span></button>
                  </div>
                </div>
              ))}
              <button className="w-full py-2 border border-dashed border-[#2D3748] text-gray-400 text-xs font-medium hover:border-[#00B894] hover:text-[#00B894] transition-colors rounded">
                + Add Positive Example
              </button>
            </div>
          </div>

          {/* Negative Examples */}
          <div className="bg-[#131828] border border-[#2D3748] rounded-lg overflow-hidden flex flex-col">
            <div className="px-4 py-3 bg-[#1E2538] border-b border-[#2D3748] flex justify-between items-center border-l-4 border-l-[#E17055]">
              <h3 className="text-sm font-semibold text-white uppercase tracking-wider">Negative Examples</h3>
              <span className="bg-[#E17055]/20 text-[#E17055] text-[10px] px-2 py-0.5 rounded font-mono">AVOID THIS</span>
            </div>
            <div className="p-4 space-y-4 flex-1">
              {negativeExamples.map((ex, i) => (
                <div key={i} className="p-3 bg-[rgba(225,112,85,0.1)] rounded border border-[#E17055]/30 relative group">
                  <div className="text-[10px] text-[#E17055] font-bold mb-1 uppercase tracking-wide">Context: {ex.context}</div>
                  <p className="text-sm text-gray-200 italic">{ex.msg}</p>
                  {ex.reason && <div className="mt-2 text-[10px] text-[#E17055] border-t border-[#E17055]/20 pt-1">Reason: {ex.reason}</div>}
                  <div className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity flex gap-1">
                    <button className="bg-[#E17055] text-white p-1 rounded hover:bg-[#c05a42]"><span className="material-symbols-outlined text-[14px]">delete</span></button>
                  </div>
                </div>
              ))}
              <button className="w-full py-2 border border-dashed border-[#2D3748] text-gray-400 text-xs font-medium hover:border-[#E17055] hover:text-[#E17055] transition-colors rounded">
                + Add Negative Example
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Right Column - Live Tester */}
      <div className="col-span-12 lg:col-span-4 space-y-6">
        <div className="bg-[#131828] border border-[#2D3748] rounded-lg shadow-2xl overflow-hidden sticky top-0">
          <div className="px-4 py-3 bg-[#1E2538] border-b border-[#2D3748] flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="material-symbols-outlined text-[#00B894] animate-pulse">science</span>
              <h3 className="text-sm font-semibold text-white uppercase tracking-wider">Live Voice Tester</h3>
            </div>
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-[#00B894]"></span>
              <span className="text-[10px] text-gray-400 uppercase">Ready</span>
            </div>
          </div>

          <div className="p-5 space-y-6">
            <div className="space-y-2">
              <label className="text-xs font-medium text-gray-400 uppercase flex justify-between">
                Video Context / Transcript
                <span className="text-[10px] text-gray-500">Max 500 chars</span>
              </label>
              <textarea
                className="w-full bg-[#0B0F1A] border border-[#2D3748] rounded text-sm text-gray-100 p-3 focus:ring-1 focus:ring-[#00B894] focus:border-[#00B894] mono-text h-32 resize-none outline-none placeholder-gray-600"
                placeholder="Paste video description or transcript here... e.g., 'A creator explains why they stopped buying coffee to save for a house deposit.'"
                value={testContext}
                onChange={(e) => setTestContext(e.target.value)}
                maxLength={500}
              ></textarea>
              <div className="flex justify-end pt-1">
                <button
                  onClick={handleTest}
                  disabled={isTesting || !testContext.trim()}
                  className="w-full py-2.5 bg-[#00B894] hover:bg-[#00a383] text-white rounded font-medium text-sm flex items-center justify-center gap-2 transition-colors shadow-lg shadow-[#00B894]/20 disabled:opacity-50"
                >
                  {isTesting ? (
                    <span className="material-symbols-outlined text-[18px] animate-spin">autorenew</span>
                  ) : (
                    <span className="material-symbols-outlined text-[18px]">psychology</span>
                  )}
                  {isTesting ? 'Generating...' : 'Generate Test Comment'}
                </button>
              </div>
            </div>

            <div className="relative flex items-center py-2">
              <div className="flex-grow border-t border-[#2D3748]"></div>
              <span className="flex-shrink-0 mx-4 text-gray-500 text-[10px] uppercase font-bold">Preview Output</span>
              <div className="flex-grow border-t border-[#2D3748]"></div>
            </div>

            <div className="space-y-3">
              {testResults.length === 0 ? (
                <div className="text-center py-6 text-gray-500 text-xs">
                  Enter context above and click "Generate" to see AI responses.
                </div>
              ) : testResults.map((res: any, i: number) => (
                <div key={i} className="bg-[#0B0F1A] border border-[#2D3748] rounded p-3 relative group hover:border-[#00B894]/50 transition-colors">
                  <div className="flex justify-between items-start mb-2">
                    <span className="text-[10px] bg-[#1E2538] text-gray-400 px-1.5 py-0.5 rounded border border-[#2D3748] mono-text">Approach: {res.approach || 'Default'}</span>
                    <span className={`text-[10px] ${(res.score || 0) >= 80 ? 'text-[#00B894]' : 'text-[#FDCB6E]'}`}>Score: {res.score || '--'}</span>
                  </div>
                  <p className="text-sm text-gray-100">{res.text || res.msg || 'No output'}</p>
                  <div className="mt-3 pt-2 border-t border-[#2D3748] flex justify-end opacity-50 group-hover:opacity-100 transition-opacity">
                    <button
                      onClick={() => navigator.clipboard.writeText(res.text || '')}
                      className="text-gray-400 hover:text-[#00B894] text-[10px] flex items-center gap-1"
                    >
                      <span className="material-symbols-outlined text-[12px]">content_copy</span> Copy
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
