import React, { useState, useEffect, useCallback } from 'react';
import { HubAPI, ApiError } from '../services/api';

const API_BASE = 'http://localhost:8000/api/v1';

const decideDraft = async (reviewId: number, decision: 'approve' | 'reject', editedText?: string) => {
  const token = localStorage.getItem('auth_token');
  const headers: Record<string, string> = { 'Content-Type': 'application/json' };
  if (token) headers['Authorization'] = `Bearer ${token}`;

  const body: Record<string, string> = { decision };
  if (editedText !== undefined) body.edited_text = editedText;

  const resp = await fetch(`${API_BASE}/review/${reviewId}/decide`, {
    method: 'POST',
    headers,
    body: JSON.stringify(body),
  });
  if (!resp.ok) {
    const detail = await resp.text().catch(() => 'Unknown error');
    throw new Error(`Failed to decide: ${detail}`);
  }
  return resp.json();
};

export default function InstagramHub() {
  const [data, setData] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [refreshing, setRefreshing] = useState(false);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [editText, setEditText] = useState('');

  const fetchData = useCallback(async () => {
    try {
      const result = await HubAPI.getStats('instagram');
      setData(result);
      setError(null);
    } catch (err) {
      setError(err instanceof ApiError ? err.detail : 'Failed to load Instagram data.');
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const handleRefresh = async () => {
    setRefreshing(true);
    try {
      await fetch(`${API_BASE}/hubs/instagram/sync`, { method: 'POST' });
    } catch (e) {
      console.warn('Sync request failed, reloading cached data:', e);
    }
    await fetchData();
    setRefreshing(false);
  };

  const handleApprove = async (item: any) => {
    try {
      await decideDraft(item.id, 'approve');
      setData((prev: any) => ({
        ...prev,
        drafts: prev.drafts.filter((d: any) => d.id !== item.id),
      }));
    } catch (e) {
      console.error('Failed to approve draft:', e);
    }
  };

  const handleReject = async (item: any) => {
    try {
      await decideDraft(item.id, 'reject');
      setData((prev: any) => ({
        ...prev,
        drafts: prev.drafts.filter((d: any) => d.id !== item.id),
      }));
    } catch (e) {
      console.error('Failed to reject draft:', e);
    }
  };

  const handleEdit = (item: any) => {
    setEditingId(item.id);
    setEditText(item.draft);
  };

  const handleSaveEdit = async (item: any) => {
    try {
      await decideDraft(item.id, 'approve', editText);
      setData((prev: any) => ({
        ...prev,
        drafts: prev.drafts.filter((d: any) => d.id !== item.id),
      }));
      setEditingId(null);
      setEditText('');
    } catch (e) {
      console.error('Failed to save edited draft:', e);
    }
  };

  const handleCancelEdit = () => {
    setEditingId(null);
    setEditText('');
  };

  if (error) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center bg-[#0B0F1A]">
        <span className="material-symbols-outlined text-5xl text-[#E1306C] mb-4">no_photography</span>
        <h2 className="text-xl font-bold text-white mb-2">Instagram Data Unavailable</h2>
        <p className="text-gray-400 text-sm mb-6 max-w-md text-center">{error}</p>
        <p className="text-gray-500 text-xs">Connect Instagram in Settings to see data.</p>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="flex-1 bg-[#0B0F1A] flex flex-col items-center justify-center">
        <div className="w-10 h-10 border-4 border-[#E1306C] border-t-transparent rounded-full animate-spin"></div>
        <span className="text-[#E1306C] mt-4 font-medium tracking-widest uppercase text-sm animate-pulse">Loading Instagram Data...</span>
      </div>
    );
  }

  return (
    <div className="flex-1 flex flex-col h-full bg-[#0B0F1A] overflow-hidden">
      <header className="h-20 px-8 border-b border-[#1F2937] bg-gradient-to-r from-[#131828] to-[#0B0F1A] flex items-center justify-between shrink-0 relative overflow-hidden">
        <div className="absolute top-0 right-0 w-64 h-full bg-gradient-to-l from-[#E1306C]/10 to-transparent pointer-events-none"></div>
        <div className="absolute bottom-0 left-0 w-full h-[1px] bg-gradient-to-r from-[#f09433]/50 via-[#E1306C]/50 to-[#bc1888]/50"></div>

        <div className="flex items-center gap-4 z-10">
          <div className="w-12 h-12 rounded-xl bg-gradient-to-tr from-[#f09433] via-[#dc2743] to-[#bc1888] flex items-center justify-center shadow-[0_0_15px_rgba(225,48,108,0.3)]">
            <span className="material-symbols-outlined text-3xl text-white">photo_camera</span>
          </div>
          <div>
            <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2">
              Instagram Command Hub
              <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-[#10B981]/20 text-[#10B981] border border-[#10B981]/30 uppercase tracking-wider">Active</span>
            </h1>
            <p className="text-sm text-gray-400">Discovering finance Reels and engaging with creators</p>
          </div>
        </div>

        <button
          onClick={handleRefresh}
          disabled={refreshing}
          className="z-10 flex items-center gap-2 px-4 py-2 bg-[#E1306C]/10 text-[#E1306C] border border-[#E1306C]/30 rounded-lg text-sm font-medium hover:bg-[#E1306C]/20 transition-colors disabled:opacity-50"
        >
          <span className={`material-symbols-outlined text-[18px] ${refreshing ? 'animate-spin' : ''}`}>refresh</span>
          {refreshing ? 'Syncing...' : 'Discover Reels'}
        </button>
      </header>

      <div className="flex-1 overflow-y-auto p-8 scroller flex flex-col gap-8">
        {/* Stats Row */}
        <div className="grid grid-cols-4 gap-4">
          {[
            { label: 'Reels Discovered', value: data.reels?.length || 0, trend: '+24%', color: 'text-[#E1306C]' },
            { label: 'Comments Drafted', value: data.drafts?.length || 0, trend: 'Pending', color: 'text-[#f09433]' },
            { label: 'Avg Sentiment', value: data.stats.sentiment, trend: '86%', color: 'text-[#10B981]' },
            { label: 'Engagement Rate', value: data.stats.quota, trend: '+12%', color: 'text-[#bc1888]' },
          ].map((stat, i) => (
            <div key={i} className="bg-[#131828] border border-[#1F2937] rounded-xl p-5 shadow-sm">
              <div className="text-xs text-gray-500 uppercase tracking-wider mb-2">{stat.label}</div>
              <div className="flex items-end justify-between">
                <div className="text-2xl font-bold text-white">{stat.value}</div>
                <div className={`text-xs font-bold ${stat.color} bg-[#1E2538] px-2 py-1 rounded`}>{stat.trend}</div>
              </div>
            </div>
          ))}
        </div>

        <div className="flex-1 grid grid-cols-2 gap-8 min-h-[400px]">
          {/* Discovered Reels Feed */}
          <div className="bg-[#131828] border border-[#1F2937] rounded-xl flex flex-col overflow-hidden">
            <div className="p-4 border-b border-[#1F2937] flex justify-between items-center bg-[#1E2538]/50">
              <div className="flex items-center gap-2">
                <span className="material-symbols-outlined text-[#E1306C] text-[18px]">slow_motion_video</span>
                <h3 className="font-semibold text-white">Discovered Finance Reels</h3>
              </div>
              <span className="text-xs text-gray-500 bg-[#1E2538] px-2 py-1 rounded border border-[#2D3748]">{data.reels?.length || 0} reels</span>
            </div>
            <div className="flex-1 p-4 overflow-y-auto scroller space-y-4">
              {data.reels && data.reels.length > 0 ? data.reels.map((reel: any, i: number) => (
                <div key={i} className="p-4 border border-[#2D3748] rounded-lg bg-[#0B0F1A] hover:border-[#E1306C]/50 transition-colors cursor-pointer group">
                  <div className="flex justify-between items-start mb-2">
                    <div className="flex items-center gap-2">
                      <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-[#f09433] to-[#E1306C] p-[2px] shrink-0">
                        <div className="w-full h-full bg-[#0B0F1A] rounded-full flex items-center justify-center">
                          <span className="material-symbols-outlined text-[14px] text-[#E1306C]">person</span>
                        </div>
                      </div>
                      <span className="font-mono text-sm text-[#E1306C]">{reel.creator}</span>
                    </div>
                    <span className="text-[10px] uppercase bg-[#E1306C]/10 text-[#E1306C] px-2 py-0.5 rounded border border-[#E1306C]/20 font-medium">Reel</span>
                  </div>
                  <p className="text-xs text-gray-300 mb-3 line-clamp-2 leading-relaxed">{reel.description}</p>
                  <div className="flex items-center gap-3 text-[10px] text-gray-500 flex-wrap">
                    <span className="flex items-center gap-1">
                      <span className="material-symbols-outlined text-[12px] text-[#E1306C]">favorite</span>
                      {reel.likes >= 1000 ? `${(reel.likes / 1000).toFixed(1)}k` : reel.likes}
                    </span>
                    {reel.hashtags?.slice(0, 3).map((tag: string, j: number) => (
                      <span key={j} className="text-[#bc1888] bg-[#bc1888]/10 px-1.5 py-0.5 rounded">{tag}</span>
                    ))}
                    <span className="ml-auto opacity-0 group-hover:opacity-100 transition-opacity text-[#E1306C] font-medium">View Reel →</span>
                  </div>
                </div>
              )) : (
                <div className="flex flex-col items-center justify-center py-16 text-gray-500">
                  <span className="material-symbols-outlined text-4xl mb-2">search_off</span>
                  <p className="text-sm">No finance Reels discovered yet.</p>
                  <p className="text-xs mt-1 text-gray-600">Click "Discover Reels" to find content.</p>
                </div>
              )}
            </div>
          </div>

          {/* Draft Comments / Pending Review */}
          <div className="bg-[#131828] border border-[#1F2937] rounded-xl flex flex-col overflow-hidden">
            <div className="p-4 border-b border-[#1F2937] flex justify-between items-center bg-[#1E2538]/50">
              <h3 className="font-semibold text-white flex items-center gap-2">
                <span className="material-symbols-outlined text-[#f09433] text-[18px]">rate_review</span>
                Draft Comments
              </h3>
              {data.drafts && data.drafts.length > 0 && (
                <button className="text-xs bg-[#E1306C]/20 text-[#E1306C] px-2 py-1 rounded font-medium">Review All ({data.drafts.length})</button>
              )}
            </div>
            <div className="flex-1 p-0 overflow-y-auto scroller divide-y divide-[#2D3748]">
              {data.drafts && data.drafts.length > 0 ? data.drafts.map((item: any, i: number) => (
                <div key={item.id ?? i} className="p-5 bg-[#0B0F1A] hover:bg-[#131828] transition-colors">
                  <div className="text-xs text-gray-500 mb-2 flex items-center gap-1 flex-wrap">
                    <span>Replying to</span>
                    {item.tweet_url ? (
                      <a href={item.tweet_url} target="_blank" rel="noopener noreferrer" className="text-[#E1306C] hover:underline inline-flex items-center gap-1">
                        {item.user}
                        <span className="material-symbols-outlined text-[12px]">open_in_new</span>
                      </a>
                    ) : (
                      <span className="text-[#E1306C]">{item.user}</span>
                    )}
                    {item.risk_score != null && (
                      <span className={`ml-1 px-1.5 py-0.5 rounded text-[10px] font-bold ${
                        item.risk_score > 25 ? 'bg-yellow-500/20 text-yellow-400 border border-yellow-500/30' : 'bg-green-500/20 text-green-400 border border-green-500/30'
                      }`}>
                        Risk: {item.risk_score}
                      </span>
                    )}
                  </div>
                  <p className="text-sm text-gray-300 mb-3 line-clamp-2">"{item.msg}"</p>

                  {editingId === item.id ? (
                    <div className="space-y-2">
                      <div className="relative">
                        <div className="absolute left-0 top-0 bottom-0 w-1 bg-[#E1306C] rounded-l"></div>
                        <textarea
                          value={editText}
                          onChange={(e) => setEditText(e.target.value)}
                          className="w-full bg-[#1E2538] text-white text-sm p-3 pl-4 rounded rounded-l-none border border-[#2D3748] border-l-0 resize-none focus:outline-none focus:border-[#E1306C]/50"
                          rows={3}
                        />
                      </div>
                      <div className="flex gap-2">
                        <button
                          onClick={() => handleSaveEdit(item)}
                          className="flex-1 py-1.5 bg-[#E1306C]/10 text-[#E1306C] border border-[#E1306C]/30 rounded text-xs font-medium hover:bg-[#E1306C]/20"
                        >
                          Save & Approve
                        </button>
                        <button
                          onClick={handleCancelEdit}
                          className="px-3 py-1.5 bg-[#2D3748] text-gray-400 rounded text-xs font-medium hover:bg-[#394559]"
                        >
                          Cancel
                        </button>
                      </div>
                    </div>
                  ) : (
                    <>
                      <div className="relative">
                        <div className="absolute left-0 top-0 bottom-0 w-1 bg-gradient-to-b from-[#f09433] to-[#E1306C] rounded-l"></div>
                        <div className="bg-[#1E2538] p-3 pl-4 rounded rounded-l-none border border-[#2D3748] border-l-0">
                          <div className="text-[10px] font-bold text-[#f09433] mb-1 uppercase">Draft Comment (Needs Approval)</div>
                          <p className="text-sm text-white">"{item.draft}"</p>
                        </div>
                      </div>

                      <div className="mt-3 flex gap-2">
                        <button
                          onClick={() => handleApprove(item)}
                          className="flex-1 py-1.5 bg-[#10B981]/10 text-[#10B981] border border-[#10B981]/30 rounded text-xs font-medium hover:bg-[#10B981]/20"
                        >
                          Approve
                        </button>
                        <button
                          onClick={() => handleReject(item)}
                          className="flex-1 py-1.5 bg-[#EF4444]/10 text-[#EF4444] border border-[#EF4444]/30 rounded text-xs font-medium hover:bg-[#EF4444]/20"
                        >
                          Reject
                        </button>
                        <button
                          onClick={() => handleEdit(item)}
                          className="px-3 py-1.5 bg-[#2D3748] text-white rounded text-xs font-medium hover:bg-[#394559] material-symbols-outlined text-[14px]"
                        >
                          edit
                        </button>
                      </div>
                    </>
                  )}
                </div>
              )) : (
                <div className="flex flex-col items-center justify-center py-16 text-gray-500">
                  <span className="material-symbols-outlined text-4xl mb-2">drafts</span>
                  <p className="text-sm">No drafts pending review.</p>
                  <p className="text-xs mt-1 text-gray-600">The agent will generate comments on discovered Reels.</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
