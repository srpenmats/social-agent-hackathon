import React, { useState, useEffect } from 'react';
import { ReviewAPI, PersonaAPI, ApiError } from '../services/api';
import { draftComment } from '../services/ai';

export default function ReviewQueue() {
  const [queue, setQueue] = useState<any[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Gemini State
  const [draftedText, setDraftedText] = useState('');
  const [isDrafting, setIsDrafting] = useState(false);
  const [isResolving, setIsResolving] = useState(false);

  // Active persona (fetched from backend)
  const [personaIdentity, setPersonaIdentity] = useState('');
  const [personaRules, setPersonaRules] = useState<string[]>([]);

  useEffect(() => {
    // Fetch the active persona for drafting context
    PersonaAPI.getPersonas()
      .then((personas) => {
        const active = personas.find((p: any) => p.active) || personas[0];
        if (active) {
          setPersonaIdentity(active.coreIdentity || '');
          setPersonaRules(active.rules || []);
        }
      })
      .catch(() => {});

    loadQueue();
  }, []);

  const loadQueue = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const items = await ReviewAPI.getQueue();
      setQueue(items);
      setCurrentIndex(0);
      if (items.length > 0) {
        generateDraft(items[0].postContext);
      }
    } catch (e) {
      setError(e instanceof ApiError ? e.detail : 'Failed to load review queue.');
    } finally {
      setIsLoading(false);
    }
  };

  const generateDraft = async (postContext: string) => {
    setIsDrafting(true);
    setDraftedText('');
    try {
      const draft = await draftComment(postContext, personaIdentity, personaRules);
      setDraftedText(draft);
    } catch (e) {
      setDraftedText("Error generating draft. Please write manually.");
    } finally {
      setIsDrafting(false);
    }
  };

  const handleResolve = async (action: 'approve' | 'reject' | 'edit') => {
    if (!currentItem || isResolving) return;
    setIsResolving(true);

    try {
      await ReviewAPI.decide(currentItem.id, action, draftedText);
      // Move to next item
      if (currentIndex < queue.length - 1) {
        const nextIdx = currentIndex + 1;
        setCurrentIndex(nextIdx);
        generateDraft(queue[nextIdx].postContext);
      } else {
        setQueue([]); // Queue empty
      }
    } catch (e) {
      console.error("Failed to resolve item", e);
    } finally {
      setIsResolving(false);
    }
  };

  if (error) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center bg-[#0B0F1A]">
        <span className="material-symbols-outlined text-5xl text-red-400 mb-4">error_outline</span>
        <h2 className="text-xl font-bold text-white mb-2">Queue Unavailable</h2>
        <p className="text-gray-400 text-sm mb-6 max-w-md text-center">{error}</p>
        <button onClick={loadQueue} className="px-6 py-2 bg-[#1E2538] text-white rounded hover:bg-[#2D3748] transition-colors">Retry</button>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="flex-1 flex items-center justify-center bg-[#0B0F1A]">
        <div className="flex flex-col items-center gap-4">
          <div className="w-10 h-10 border-4 border-teal-500 border-t-transparent rounded-full animate-spin"></div>
          <span className="text-teal-400 font-medium tracking-widest uppercase text-sm animate-pulse">Fetching Queue...</span>
        </div>
      </div>
    );
  }

  const currentItem = queue[currentIndex];

  if (!currentItem) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center bg-[#0B0F1A]">
        <span className="material-symbols-outlined text-6xl text-teal-500 mb-4">task_alt</span>
        <h2 className="text-2xl font-bold text-white mb-2">Queue is Empty</h2>
        <p className="text-gray-400">All caught up! Great job.</p>
        <button onClick={loadQueue} className="mt-6 px-6 py-2 bg-[#1E2538] text-white rounded hover:bg-[#2D3748] transition-colors">Refresh</button>
      </div>
    );
  }

  return (
    <div className="flex-1 flex flex-col h-full relative overflow-hidden bg-gradient-to-br from-[#0B0F1A] via-[#0f1524] to-[#0B0F1A]">
      <header className="h-16 border-b border-[#2D3748] flex items-center justify-between px-8 bg-[#0B0F1A]/80 backdrop-blur-md z-10 flex-shrink-0">
        <div className="flex items-center gap-4">
          <h1 className="text-xl font-semibold text-white tracking-tight">Review Queue</h1>
          <div className="bg-teal-500/10 border border-teal-500/30 text-teal-400 px-3 py-1 rounded-full text-xs font-medium flex items-center gap-2">
            <span className="w-1.5 h-1.5 bg-teal-400 rounded-full animate-pulse"></span>
            {queue.length - currentIndex} Pending Items
          </div>
        </div>
      </header>

      <div className="flex-1 grid grid-cols-12 gap-0 overflow-hidden">
        <div className="col-span-9 p-8 flex flex-col h-full overflow-y-auto scroller relative">
          <div className="absolute inset-0 opacity-[0.03] pointer-events-none" style={{ backgroundImage: 'radial-gradient(#4fd1c5 1px, transparent 1px)', backgroundSize: '24px 24px' }}></div>

          <div className="w-full max-w-5xl mx-auto flex-1 flex flex-col justify-center z-10">
            <div className="bg-[#131828]/95 backdrop-blur-md border border-[#2D3748] rounded-2xl shadow-2xl flex flex-col md:flex-row overflow-hidden min-h-[500px]">

              {/* Media Preview */}
              <div className="w-full md:w-[380px] bg-black relative flex flex-col border-r border-[#2D3748]">
                <div className="absolute top-4 left-4 z-10 bg-black/60 backdrop-blur-sm border border-white/10 px-3 py-1 rounded-full flex items-center gap-2">
                  <span className="material-symbols-outlined text-xs text-white">public</span>
                  <span className="text-xs font-semibold text-white">{currentItem.platform}</span>
                </div>

                <div className="flex-1 bg-gray-900 relative overflow-hidden flex flex-col">
                  <img alt="Content thumbnail" className="w-full h-full object-cover opacity-80" src={currentItem.thumbnail}/>
                  <div className="absolute bottom-0 left-0 right-0 p-4 bg-gradient-to-t from-black/90 to-transparent">
                    <div className="flex items-center gap-2 mb-2">
                      <img className="w-6 h-6 rounded-full border border-white/20" src={currentItem.avatar} alt="Avatar"/>
                      <span className="text-xs text-gray-300 font-medium">{currentItem.user}</span>
                    </div>
                    <p className="text-sm text-white line-clamp-3">{currentItem.postContext}</p>
                  </div>
                </div>
              </div>

              {/* Review Content */}
              <div className="flex-1 flex flex-col p-8 bg-[#131828]">
                <div className="flex justify-between items-start mb-6">
                  <div>
                    <h2 className="text-lg font-semibold text-white mb-1">Review Generated Comment</h2>
                    <div className="flex items-center gap-2">
                      <span className="text-xs text-gray-400">Generated by</span>
                      <span className="text-xs bg-purple-500/10 text-purple-400 px-2 py-0.5 rounded border border-purple-500/20">AI Backend</span>
                    </div>
                  </div>

                  <div className="flex items-center gap-3 bg-[#0B0F1A] border border-[#00B894] rounded-lg p-2 pr-4 shadow-sm">
                    <div className="w-10 h-10 rounded-full border-4 border-[#00B894] flex items-center justify-center text-[#00B894] font-bold text-sm">
                      {currentItem.riskScore}
                    </div>
                    <div className="flex flex-col">
                      <span className="text-[#00B894] text-xs font-bold uppercase tracking-wider">{currentItem.riskLabel}</span>
                      <span className="text-[10px] text-gray-400">Score: {currentItem.riskScore}/100</span>
                    </div>
                  </div>
                </div>

                <div className="flex-1 mb-8 flex flex-col relative">
                  <label className="block text-xs font-medium text-gray-400 mb-2 uppercase tracking-wide">Proposed Response</label>

                  {isDrafting ? (
                    <div className="flex-1 bg-[#0B0F1A] border border-[#2D3748] rounded-xl flex items-center justify-center p-4">
                      <div className="flex items-center gap-3 text-gray-400">
                        <span className="material-symbols-outlined animate-spin text-teal-500">autorenew</span>
                        <span className="text-sm">AI is drafting a response...</span>
                      </div>
                    </div>
                  ) : (
                    <div className="relative flex-1">
                      <textarea
                        className="w-full h-full min-h-[140px] bg-[#0B0F1A] border border-[#2D3748] rounded-xl p-4 text-gray-100 text-lg leading-relaxed focus:ring-2 focus:ring-teal-500/50 focus:border-teal-500 outline-none resize-none transition-all shadow-inner"
                        spellCheck="false"
                        value={draftedText}
                        onChange={(e) => setDraftedText(e.target.value)}
                      />
                      <div className="absolute bottom-4 right-4 text-xs text-gray-500 font-mono">{draftedText.length} chars</div>
                    </div>
                  )}
                </div>

                <div className="flex items-center gap-4 mt-auto">
                  <button
                    disabled={isResolving || isDrafting}
                    onClick={() => handleResolve('reject')}
                    className="flex-1 h-12 bg-red-500/10 hover:bg-red-500/20 disabled:opacity-50 text-red-400 border border-red-500/30 rounded-lg flex items-center justify-center gap-2 transition-colors font-medium">
                    Reject
                  </button>
                  <button
                    disabled={isResolving || isDrafting}
                    onClick={() => handleResolve('edit')}
                    className="flex-1 h-12 bg-[#1E2538] hover:bg-[#2D3748] disabled:opacity-50 text-white border border-[#2D3748] rounded-lg flex items-center justify-center gap-2 transition-colors font-medium">
                    Edit
                  </button>
                  <button
                    disabled={isResolving || isDrafting}
                    onClick={() => handleResolve('approve')}
                    className="flex-1 h-12 bg-teal-500 hover:bg-teal-600 disabled:opacity-50 text-white rounded-lg flex items-center justify-center gap-2 transition-colors font-medium shadow-lg shadow-teal-500/20">
                    Approve
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Sidebar placeholder for Recent Decisions */}
        <div className="col-span-3 border-l border-[#2D3748] bg-[#0f1420] p-6 hidden lg:flex flex-col">
          <h3 className="text-sm font-semibold text-gray-300 mb-6 uppercase tracking-wider">Queue Progress</h3>
          <div className="text-gray-500 text-sm">
            Completed: {currentIndex} / {queue.length}
          </div>
        </div>
      </div>
    </div>
  );
}
