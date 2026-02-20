import React, { useState, useEffect, useRef } from 'react';
import { CommentsAPI, ApiError } from '../services/api';

export default function CommentLibrary() {
  const [activeTab, setActiveTab] = useState('All');
  const [snippets, setSnippets] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const categories = ['All', 'Support', 'Engagement', 'Education', 'Lead Gen', 'Crisis'];

  const fetchComments = async (category: string, search: string) => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await CommentsAPI.getComments({
        category: category !== 'All' ? category : undefined,
        search: search || undefined,
      });
      setSnippets(data);
    } catch (e) {
      setError(e instanceof ApiError ? e.detail : 'Failed to load comment library.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchComments(activeTab, searchQuery);
  }, [activeTab]);

  const handleSearchChange = (value: string) => {
    setSearchQuery(value);
    if (debounceRef.current) clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(() => {
      fetchComments(activeTab, value);
    }, 400);
  };

  if (error && snippets.length === 0) {
    return (
      <div className="flex-1 bg-[#0B0F1A] flex flex-col items-center justify-center">
        <span className="material-symbols-outlined text-5xl text-red-400 mb-4">error_outline</span>
        <h2 className="text-xl font-bold text-white mb-2">Library Unavailable</h2>
        <p className="text-gray-400 text-sm mb-6 max-w-md text-center">{error}</p>
        <button onClick={() => fetchComments(activeTab, searchQuery)} className="px-6 py-2 bg-[#1E2538] text-white rounded hover:bg-[#2D3748] transition-colors">Retry</button>
      </div>
    );
  }

  if (isLoading && snippets.length === 0) {
    return (
      <div className="flex-1 bg-[#0B0F1A] flex flex-col items-center justify-center">
        <div className="w-10 h-10 border-4 border-[#a855f7] border-t-transparent rounded-full animate-spin"></div>
        <span className="text-[#a855f7] mt-4 font-medium tracking-widest uppercase text-sm animate-pulse">Loading Library...</span>
      </div>
    );
  }

  return (
    <div className="flex-1 flex flex-col h-full bg-[#0B0F1A] overflow-hidden">
      <header className="h-20 px-8 border-b border-[#1F2937] bg-[#131828] flex items-center justify-between shrink-0">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2">
            <span className="material-symbols-outlined text-[#a855f7] text-3xl">library_books</span>
            Comment Library
          </h1>
          <p className="text-sm text-gray-400">Manage pre-approved snippets, templates, and high-performing historical responses.</p>
        </div>
        <div className="flex gap-3">
          <button className="px-4 py-2 bg-[#1E2538] hover:bg-[#2D3748] border border-[#2D3748] rounded-lg text-sm font-medium transition-colors text-white flex items-center gap-2">
            <span className="material-symbols-outlined text-[18px]">file_download</span> Export CSV
          </button>
          <button className="px-4 py-2 bg-[#a855f7] hover:bg-[#9333ea] text-white rounded-lg text-sm font-bold transition-colors shadow-lg shadow-[#a855f7]/20 flex items-center gap-2">
            <span className="material-symbols-outlined text-[18px]">add</span> Add Snippet
          </button>
        </div>
      </header>

      <div className="flex-1 flex flex-col overflow-hidden p-8">
        {/* Controls Bar */}
        <div className="flex justify-between items-center mb-6 shrink-0">
          <div className="flex space-x-2 overflow-x-auto scroller pb-2">
            {categories.map(cat => (
              <button
                key={cat}
                onClick={() => setActiveTab(cat)}
                className={`px-4 py-1.5 rounded-full text-sm font-medium whitespace-nowrap transition-colors ${
                  activeTab === cat
                    ? 'bg-[#a855f7] text-white shadow-md shadow-[#a855f7]/20'
                    : 'bg-[#131828] text-gray-400 hover:text-white border border-[#2D3748]'
                }`}
              >
                {cat}
              </button>
            ))}
          </div>

          <div className="relative w-72">
            <span className="material-symbols-outlined absolute left-3 top-2 text-gray-500 text-[20px]">search</span>
            <input
              type="text"
              placeholder="Search snippets or tags..."
              value={searchQuery}
              onChange={(e) => handleSearchChange(e.target.value)}
              className="w-full bg-[#131828] border border-[#2D3748] rounded-full py-2 pl-10 pr-4 text-sm text-white focus:outline-none focus:border-[#a855f7]"
            />
          </div>
        </div>

        {/* Library Grid */}
        <div className="flex-1 overflow-y-auto scroller">
          {snippets.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-20 text-gray-500">
              <span className="material-symbols-outlined text-5xl mb-4">chat_bubble_outline</span>
              <h3 className="text-lg font-semibold text-white mb-2">No Comments Found</h3>
              <p className="text-sm text-gray-400">Comments will appear here as the agent operates.</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6 pb-8">
              {snippets.map(snippet => (
                <div key={snippet.id} className="bg-[#131828] border border-[#1F2937] hover:border-[#a855f7]/50 rounded-xl flex flex-col transition-colors group">
                  <div className="p-4 border-b border-[#1F2937] flex justify-between items-center bg-[#1E2538]/30 rounded-t-xl">
                    <div className="flex items-center gap-2">
                      <span className={`w-2 h-2 rounded-full ${
                        snippet.category === 'Support' ? 'bg-blue-400' :
                        snippet.category === 'Education' ? 'bg-[#00B894]' :
                        snippet.category === 'Lead Gen' ? 'bg-yellow-400' :
                        snippet.category === 'Crisis' ? 'bg-red-500' : 'bg-purple-400'
                      }`}></span>
                      <span className="text-xs font-semibold text-gray-300 uppercase tracking-wider">{snippet.category}</span>
                    </div>
                    <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                      <button className="p-1 text-gray-400 hover:text-white rounded"><span className="material-symbols-outlined text-[16px]">edit</span></button>
                      <button className="p-1 text-gray-400 hover:text-[#a855f7] rounded"><span className="material-symbols-outlined text-[16px]">content_copy</span></button>
                    </div>
                  </div>

                  <div className="p-5 flex-1 flex flex-col">
                    <p className="text-sm text-gray-200 leading-relaxed mb-4 flex-1">"{snippet.text}"</p>

                    <div className="flex flex-wrap gap-2 mb-4">
                      {(snippet.tags || []).map((tag: string) => (
                        <span key={tag} className="px-2 py-0.5 bg-[#0B0F1A] border border-[#2D3748] text-gray-400 rounded text-[10px] font-mono">#{tag}</span>
                      ))}
                    </div>

                    <div className="pt-3 border-t border-[#1F2937] flex justify-between items-center">
                      <div className="flex gap-4">
                        <div className="flex flex-col">
                          <span className="text-[10px] text-gray-500 uppercase font-bold">Times Used</span>
                          <span className="text-xs text-white font-mono">{(snippet.uses || 0).toLocaleString()}</span>
                        </div>
                        <div className="flex flex-col">
                          <span className="text-[10px] text-gray-500 uppercase font-bold">Avg Likes</span>
                          <span className="text-xs text-[#00B894] font-mono flex items-center gap-0.5">
                            <span className="material-symbols-outlined text-[12px]">favorite</span> {snippet.avgLikes || 0}
                          </span>
                        </div>
                      </div>

                      <button className="text-xs font-medium text-[#a855f7] hover:text-[#9333ea] flex items-center gap-1 bg-[#a855f7]/10 px-2 py-1 rounded">
                         AI Template <span className="material-symbols-outlined text-[14px]">auto_awesome</span>
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
