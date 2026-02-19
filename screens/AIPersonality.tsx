import React, { useState, useEffect } from 'react';
import { PersonaAPI } from '../services/api';
import { generatePersonaConfig } from '../services/ai';

export default function AIPersonality() {
  const [personas, setPersonas] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  
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
    try {
      const data = await PersonaAPI.getPersonas();
      setPersonas(data);
    } catch (e) {
      console.error(e);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDragOver = (e: React.DragEvent) => e.preventDefault();
  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsUploading(true);
    setTimeout(() => {
      setIsUploading(false);
      setTempFiles([...tempFiles, {
        name: 'new_brand_guidelines_2024.pdf',
        modified: 'Just now', size: '2.4 MB', type: 'pdf',
        content: "Our brand voice is extremely professional, highly educational, and focuses on long-term wealth building without giving specific financial advice. We use data to back up our claims."
      }]);
    }, 1000);
  };

  const handleGenerate = async () => {
    setIsGenerating(true);
    try {
      // Aggregate text from uploaded files
      const documentContext = tempFiles.map(f => f.content).join('\n\n');
      
      // Call Gemini SDK to parse documents and return structured JSON
      const config = await generatePersonaConfig(documentContext);
      
      setGeneratedIdentity(config.coreIdentity || '');
      setGeneratedModifiers(config.toneModifiers || '');
    } catch (error) {
      console.error("Failed to generate config", error);
      setGeneratedIdentity("Fallback: Professional educator.");
      setGeneratedModifiers("- Approachable\n- Professional");
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
      
      const saved = await PersonaAPI.savePersona(newPersona);
      setPersonas([saved, ...personas]);
      setIsCreating(false);
      setActivePersonaId(saved.id);
    } catch (e) {
      console.error(e);
    }
  };

  if (isLoading) return <div className="flex-1 bg-[#0B0F1A] flex items-center justify-center"><div className="w-8 h-8 border-4 border-[#F59E0B] border-t-transparent rounded-full animate-spin"></div></div>;

  return (
    <div className="flex-1 flex flex-col h-full bg-[#0B0F1A] overflow-hidden">
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
            {personas.map((p) => (
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
                      Generate Config via Gemini
                    </button>
                  )}
                </div>

                {/* Gemini Output */}
                {generatedIdentity && (
                  <div className="bg-[#131828] border border-[#F59E0B]/50 rounded-xl overflow-hidden animate-in slide-in-from-bottom-4">
                     <div className="px-6 py-4 bg-[#F59E0B]/10 border-b border-[#F59E0B]/20 flex items-center gap-2">
                       <span className="material-symbols-outlined text-[#F59E0B]">auto_awesome</span>
                       <h3 className="font-semibold text-[#F59E0B]">Gemini Generated Configuration</h3>
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
            <div className="max-w-5xl mx-auto p-8">
               <h2 className="text-2xl font-bold text-white mb-6">{activePersona.name}</h2>
               <div className="bg-[#131828] p-6 rounded-xl border border-[#2D3748] mb-6">
                 <h3 className="text-sm font-semibold text-gray-400 uppercase mb-2">Core Identity</h3>
                 <p className="text-gray-200 text-sm font-mono leading-relaxed">{activePersona.coreIdentity}</p>
               </div>
               <div className="bg-[#131828] p-6 rounded-xl border border-[#2D3748]">
                 <h3 className="text-sm font-semibold text-gray-400 uppercase mb-2">Tone Modifiers</h3>
                 <pre className="text-gray-200 text-sm font-mono whitespace-pre-wrap font-sans">{activePersona.toneModifiers}</pre>
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