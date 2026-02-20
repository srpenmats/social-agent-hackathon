import React, { useState, useEffect } from 'react';
import { PersonaAPI, ApiError } from '../services/api';
import { generatePersonaConfig } from '../services/ai';

export default function AIPersonality() {
  const [personas, setPersonas] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [isCreating, setIsCreating] = useState(false);
  const [activePersonaId, setActivePersonaId] = useState<string | null>(null);

  // Creation States
  const [isUploading, setIsUploading] = useState(false);
  const [tempFiles, setTempFiles] = useState<any[]>([]);
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedIdentity, setGeneratedIdentity] = useState('');
  const [generatedModifiers, setGeneratedModifiers] = useState('');

  const activePersona = personas.find(p => p.id === activePersonaId);

  useEffect(() => {
    fetchPersonas();
  }, []);

  const fetchPersonas = async () => {
    setError(null);
    try {
      const data = await PersonaAPI.getPersonas();
      setPersonas(data);
    } catch (e) {
      setError(e instanceof ApiError ? e.detail : 'Failed to load personas.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleDragOver = (e: React.DragEvent) => e.preventDefault();
  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsUploading(true);
    // Extract dropped files
    const files = Array.from(e.dataTransfer.files);
    setTimeout(() => {
      setIsUploading(false);
      const newFiles = files.map(f => ({
        name: f.name,
        modified: 'Just now',
        size: `${(f.size / 1024).toFixed(0)} KB`,
        type: f.name.split('.').pop() || 'pdf',
        content: '' // Content will be read by backend
      }));
      setTempFiles([...tempFiles, ...newFiles]);
    }, 500);
  };

  const handleGenerate = async () => {
    setIsGenerating(true);
    try {
      // Aggregate text from uploaded files (backend processes the actual files)
      const documentContext = tempFiles.map(f => f.content || f.name).join('\n\n');

      // Call backend via ai.ts wrapper
      const config = await generatePersonaConfig(documentContext);

      setGeneratedIdentity(config.coreIdentity || '');
      setGeneratedModifiers(config.toneModifiers || '');
    } catch (error) {
      console.error("Failed to generate config", error);
      setGeneratedIdentity("Generation failed. Please configure manually.");
      setGeneratedModifiers("- Configure tone modifiers manually");
    } finally {
      setIsGenerating(false);
    }
  };

  const startCreate = () => {
    setActivePersonaId(null);
    setIsCreating(true);
    setTempFiles([]);
    setGeneratedIdentity('');
    setGeneratedModifiers('');
  };

  const handleSave = async () => {
    try {
      const newPersona = {
        name: 'New AI Persona',
        type: 'Custom',
        active: true,
        color: 'text-purple-400',
        bg: 'bg-purple-400/10',
        coreIdentity: generatedIdentity,
        toneModifiers: generatedModifiers,
        rules: [],
        temperature: 0.5,
        files: tempFiles
      };

      const saved = await PersonaAPI.createPersona(newPersona);
      setPersonas([saved, ...personas]);
      setIsCreating(false);
      setActivePersonaId(saved.id);
    } catch (e) {
      console.error(e);
    }
  };

  if (error && personas.length === 0) {
    return (
      <div className="flex-1 bg-[#0B0F1A] flex flex-col items-center justify-center">
        <span className="material-symbols-outlined text-5xl text-red-400 mb-4">error_outline</span>
        <h2 className="text-xl font-bold text-white mb-2">Personas Unavailable</h2>
        <p className="text-gray-400 text-sm mb-6 max-w-md text-center">{error}</p>
        <button onClick={fetchPersonas} className="px-6 py-2 bg-[#1E2538] text-white rounded hover:bg-[#2D3748] transition-colors">Retry</button>
      </div>
    );
  }

  if (isLoading) return <div className="flex-1 bg-[#0B0F1A] flex items-center justify-center"><div className="w-8 h-8 border-4 border-[#F59E0B] border-t-transparent rounded-full animate-spin"></div></div>;

  return (
    <div className="flex-1 flex flex-col h-full bg-[#0B0F1A] overflow-hidden">
      <style>{`
        input[type="range"].temp-slider::-webkit-slider-thumb {
          -webkit-appearance: none;
          appearance: none;
          width: 20px;
          height: 20px;
          border-radius: 50%;
          background: white;
          border: 3px solid #F59E0B;
          cursor: pointer;
          box-shadow: 0 0 8px rgba(245, 158, 11, 0.4);
          margin-top: 0;
        }
        input[type="range"].temp-slider::-moz-range-thumb {
          width: 20px;
          height: 20px;
          border-radius: 50%;
          background: white;
          border: 3px solid #F59E0B;
          cursor: pointer;
          box-shadow: 0 0 8px rgba(245, 158, 11, 0.4);
        }
      `}</style>
      <header className="h-20 px-8 border-b border-[#1F2937] bg-[#131828] flex items-center justify-between shrink-0">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2">
            <span className="material-symbols-outlined text-[#F59E0B] text-3xl">psychology</span>
            AI Personas
          </h1>
          <p className="text-sm text-gray-400">Manage the personalities, guardrails, and knowledge bases driving your agents.</p>
        </div>
        <button
          onClick={startCreate}
          className="px-4 py-2 bg-[#F59E0B] hover:bg-[#d98b09] text-black rounded-lg text-sm font-bold transition-colors shadow-lg shadow-[#F59E0B]/20 flex items-center gap-2"
        >
          <span className="material-symbols-outlined text-[18px]">add</span> Create Persona
        </button>
      </header>

      <div className="flex-1 flex overflow-hidden">
        {/* Left Sidebar */}
        <div className="w-80 border-r border-[#1F2937] bg-[#0B0F1A] flex flex-col z-10">
          <div className="flex-1 overflow-y-auto scroller p-3 space-y-2">
            {personas.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-12 text-gray-500">
                <span className="material-symbols-outlined text-3xl mb-2">person_off</span>
                <p className="text-xs text-center">No personas yet. Create one to get started.</p>
              </div>
            ) : personas.map((p) => (
              <div
                key={p.id}
                onClick={() => { setIsCreating(false); setActivePersonaId(p.id); }}
                className={`p-3 border rounded-lg cursor-pointer transition-colors relative ${activePersonaId === p.id ? 'bg-[#1E2538] border-[#F59E0B]' : 'bg-[#131828] border-[#2D3748] hover:border-gray-500'}`}
              >
                {p.active && <span className="absolute top-3 right-3 w-2 h-2 rounded-full bg-[#10B981]"></span>}
                <div className="font-semibold text-white mb-1">{p.name}</div>
                <div className={`inline-block px-2 py-0.5 rounded text-[10px] font-medium ${p.color} ${p.bg}`}>{p.type}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Right Area */}
        <div className="flex-1 bg-[#0B0F1A] overflow-y-auto scroller relative">
          {isCreating ? (
            <div className="max-w-5xl mx-auto p-8 animate-in fade-in duration-300">
              <h2 className="text-xl font-bold text-white mb-8">Create New Persona</h2>
              <div className="space-y-8">
                {/* File Upload Zone */}
                <div className="bg-[#131828] p-6 rounded-xl border border-[#2D3748]">
                  <h3 className="text-sm font-semibold text-white mb-4">Upload Context Files</h3>
                  <div
                    onDragOver={handleDragOver}
                    onDrop={handleDrop}
                    className="border-2 border-dashed border-[#2D3748] hover:border-[#F59E0B] bg-[#0B0F1A] rounded-xl p-8 flex flex-col items-center justify-center transition-colors cursor-pointer group"
                  >
                    {isUploading ? <div className="w-8 h-8 border-4 border-[#F59E0B] border-t-transparent rounded-full animate-spin"></div> :
                    <>
                      <span className="material-symbols-outlined text-3xl text-gray-500 group-hover:text-[#F59E0B] mb-2">upload_file</span>
                      <p className="text-sm font-medium text-white">Drag and drop files here</p>
                    </>}
                  </div>

                  <div className="mt-4 space-y-2">
                    {tempFiles.map((f, i) => (
                      <div key={i} className="text-sm text-gray-400 bg-[#0B0F1A] p-2 rounded border border-[#2D3748] flex items-center gap-2">
                        <span className="material-symbols-outlined text-red-400">description</span> {f.name}
                      </div>
                    ))}
                  </div>

                  {tempFiles.length > 0 && !generatedIdentity && (
                    <button onClick={handleGenerate} disabled={isGenerating} className="mt-6 px-6 py-3 bg-[#F59E0B] text-black rounded-lg font-bold w-full flex items-center justify-center gap-2">
                      {isGenerating ? <span className="material-symbols-outlined animate-spin">autorenew</span> : <span className="material-symbols-outlined">auto_awesome</span>}
                      Generate Config via AI
                    </button>
                  )}
                </div>

                {/* AI Output */}
                {generatedIdentity && (
                  <div className="bg-[#131828] border border-[#F59E0B]/50 rounded-xl overflow-hidden animate-in slide-in-from-bottom-4">
                     <div className="px-6 py-4 bg-[#F59E0B]/10 border-b border-[#F59E0B]/20 flex items-center gap-2">
                       <span className="material-symbols-outlined text-[#F59E0B]">auto_awesome</span>
                       <h3 className="font-semibold text-[#F59E0B]">AI Generated Configuration</h3>
                     </div>
                     <div className="p-6 grid grid-cols-2 gap-6">
                        <div>
                          <label className="block text-xs font-bold text-gray-400 uppercase mb-2">Core Identity</label>
                          <textarea className="w-full bg-[#0B0F1A] border border-[#2D3748] rounded-lg p-3 text-sm text-[#F3F4F6] font-mono h-32 outline-none" value={generatedIdentity} onChange={(e) => setGeneratedIdentity(e.target.value)} />
                        </div>
                        <div>
                          <label className="block text-xs font-bold text-gray-400 uppercase mb-2">Tone Modifiers</label>
                          <textarea className="w-full bg-[#0B0F1A] border border-[#2D3748] rounded-lg p-3 text-sm text-[#F3F4F6] font-mono h-32 outline-none" value={generatedModifiers} onChange={(e) => setGeneratedModifiers(e.target.value)} />
                        </div>
                     </div>
                     <div className="p-6 pt-0 flex justify-end">
                        <button onClick={handleSave} className="px-6 py-2 bg-[#F59E0B] text-black rounded text-sm font-bold shadow-md">Save Persona</button>
                     </div>
                  </div>
                )}
              </div>
            </div>
          ) : activePersona ? (
            <div className="max-w-5xl mx-auto p-8 space-y-6">
               <div className="flex items-center gap-4 mb-2">
                 <h2 className="text-2xl font-bold text-white">{activePersona.name}</h2>
                 <span className={`px-3 py-1 rounded-full text-xs font-bold ${activePersona.color} ${activePersona.bg}`}>{activePersona.type}</span>
                 {activePersona.active && <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-[#10B981]/20 text-[#10B981] border border-[#10B981]/30 uppercase tracking-wider">Active</span>}
               </div>

               <div className="bg-[#131828] p-6 rounded-xl border border-[#2D3748]">
                 <h3 className="text-sm font-semibold text-gray-400 uppercase mb-3">Core Identity</h3>
                 <p className="text-gray-200 text-sm leading-relaxed whitespace-pre-line">{activePersona.coreIdentity}</p>
               </div>

               <div className="bg-[#131828] p-6 rounded-xl border border-[#2D3748]">
                 <h3 className="text-sm font-semibold text-gray-400 uppercase mb-3">Tone & Voice Calibration</h3>
                 <pre className="text-gray-200 text-sm whitespace-pre-wrap font-sans leading-relaxed">{activePersona.toneModifiers}</pre>
               </div>

               {activePersona.voicePillars && (
                 <div className="bg-[#131828] p-6 rounded-xl border border-[#2D3748]">
                   <h3 className="text-sm font-semibold text-gray-400 uppercase mb-4">Voice Pillars</h3>
                   <div className="grid grid-cols-2 gap-3">
                     {activePersona.voicePillars.map((pillar: any, i: number) => (
                       <div key={i} className="bg-[#0B0F1A] border border-[#2D3748] rounded-lg p-4">
                         <div className="text-sm font-bold text-white mb-1">{pillar.name}</div>
                         <p className="text-xs text-gray-400 italic">{pillar.cat || pillar.desc}</p>
                       </div>
                     ))}
                   </div>
                 </div>
               )}

               {activePersona.contentTemplates && (
                 <div className="bg-[#131828] p-6 rounded-xl border border-[#2D3748]">
                   <h3 className="text-sm font-semibold text-gray-400 uppercase mb-3">Content Templates</h3>
                   <div className="space-y-2">
                     {activePersona.contentTemplates.map((t: string, i: number) => (
                       <div key={i} className="flex items-start gap-2 text-sm text-gray-300">
                         <span className="text-[#F59E0B] mt-0.5">&#9679;</span>
                         <span>{t}</span>
                       </div>
                     ))}
                   </div>
                 </div>
               )}

               <div className="bg-[#131828] p-6 rounded-xl border border-red-500/20">
                 <h3 className="text-sm font-semibold text-red-400 uppercase mb-3 flex items-center gap-2">
                   <span className="material-symbols-outlined text-[16px]">shield</span>
                   Guardrails & Rules
                 </h3>
                 <div className="space-y-2">
                   {(activePersona.rules || []).map((rule: string, i: number) => (
                     <div key={i} className="flex items-start gap-2 text-sm text-gray-300">
                       <span className="text-red-400 mt-0.5 text-xs">&#10005;</span>
                       <span>{rule}</span>
                     </div>
                   ))}
                 </div>
               </div>

               <div className="bg-[#131828] p-5 rounded-xl border border-[#2D3748]">
                 <div className="flex items-center justify-between mb-3">
                   <span className="text-sm font-semibold text-gray-400 uppercase">Temperature</span>
                   <span className="text-lg font-mono font-bold text-white">{(activePersona.temperature || 0.5).toFixed(2)}</span>
                 </div>
                 <div className="relative">
                   <input
                     type="range"
                     min="0"
                     max="1"
                     step="0.01"
                     value={activePersona.temperature || 0.5}
                     onChange={(e) => {
                       const newTemp = parseFloat(e.target.value);
                       setPersonas(prev => prev.map(p => p.id === activePersona.id ? { ...p, temperature: newTemp } : p));
                     }}
                     className="w-full h-2 rounded-full appearance-none cursor-pointer temp-slider"
                     style={{
                       background: `linear-gradient(to right, #3B82F6 0%, #F59E0B ${(activePersona.temperature || 0.5) * 100}%, #1E2538 ${(activePersona.temperature || 0.5) * 100}%)`,
                     }}
                   />
                 </div>
                 <div className="flex justify-between mt-2 text-[10px] text-gray-500 uppercase tracking-wider">
                   <span>Precise</span>
                   <span>Balanced</span>
                   <span>Creative</span>
                 </div>
               </div>
            </div>
          ) : (
             <div className="flex h-full items-center justify-center text-gray-500">Select or create a persona.</div>
          )}
        </div>
      </div>
    </div>
  );
}
