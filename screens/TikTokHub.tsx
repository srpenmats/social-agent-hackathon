import React, { useState, useEffect } from 'react';
import { HubAPI } from '../services/api';

export default function TikTokHub() {
  const [data, setData] = useState<any>(null);

  useEffect(() => {
    HubAPI.getStats('tiktok').then(setData).catch(console.error);
  }, []);

  if (!data) {
    return (
      <div className="flex-1 bg-[#0B0F1A] flex flex-col items-center justify-center">
        <div className="w-10 h-10 border-4 border-[#EE1D52] border-t-transparent rounded-full animate-spin"></div>
        <span className="text-[#EE1D52] mt-4 font-medium tracking-widest uppercase text-sm animate-pulse">Loading TikTok Data...</span>
      </div>
    );
  }

  return (
    <div className="flex-1 flex flex-col h-full bg-[#0B0F1A] overflow-hidden">
      <header className="h-20 px-8 border-b border-[#1F2937] bg-gradient-to-r from-[#131828] to-[#0B0F1A] flex items-center justify-between shrink-0 relative overflow-hidden">
        <div className="absolute top-0 right-0 w-64 h-full bg-gradient-to-l from-[#EE1D52]/10 to-transparent pointer-events-none"></div>
        <div className="flex items-center gap-4 z-10">
          <div className="w-12 h-12 rounded-xl bg-black border border-[#1F2937] flex items-center justify-center shadow-[0_0_15px_rgba(238,29,82,0.2)]">
            <span className="material-symbols-outlined text-3xl text-white">music_note</span>
          </div>
          <div>
            <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2">
              TikTok Command Hub
              <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-[#10B981]/20 text-[#10B981] border border-[#10B981]/30 uppercase tracking-wider">Active</span>
            </h1>
          </div>
        </div>
      </header>

      <div className="flex-1 overflow-y-auto p-8 scroller">
        {/* Stats Row */}
        <div className="grid grid-cols-4 gap-4 mb-8">
          {[
            { label: 'Videos Monitored', value: data.stats.monitored, color: 'text-blue-400' },
            { label: 'Comments Posted', value: data.stats.posted, color: 'text-[#EE1D52]' },
            { label: 'Avg Like/Comment', value: data.stats.avgLike, color: 'text-[#69C9D0]' },
            { label: 'Conversion Rate', value: data.stats.conversion, color: 'text-yellow-400' },
          ].map((stat, i) => (
            <div key={i} className="bg-[#131828] border border-[#1F2937] rounded-xl p-5 shadow-sm">
              <div className="text-xs text-gray-500 uppercase tracking-wider mb-2">{stat.label}</div>
              <div className="text-3xl font-bold text-white">{stat.value}</div>
            </div>
          ))}
        </div>

        <div className="grid grid-cols-12 gap-8 min-h-[500px]">
          {/* Live Feed via API */}
          <div className="col-span-12 bg-[#131828] border border-[#1F2937] rounded-xl flex flex-col overflow-hidden">
            <div className="p-4 border-b border-[#1F2937] flex justify-between items-center bg-[#1E2538]/50">
              <div className="flex items-center gap-2">
                <span className="w-2 h-2 bg-[#EE1D52] rounded-full animate-pulse"></span>
                <h3 className="font-semibold text-white">Live Activity Feed (API Driven)</h3>
              </div>
            </div>
            <div className="p-4 space-y-4 overflow-y-auto scroller flex-1 bg-[#0B0F1A]/50">
              {data.feed.map((item: any, i: number) => (
                <div key={i} className="p-4 bg-[#131828] rounded-xl border border-[#2D3748] flex gap-4">
                  <div className="flex-1">
                    <div className="flex justify-between items-start mb-1">
                      <div className="text-xs text-gray-400 font-mono">Matched Rule: {item.matchedRule}</div>
                      <div className="text-xs text-gray-500">{item.time}</div>
                    </div>
                    <div className="text-sm text-gray-300 mb-2">
                      <span className="font-semibold text-white">{item.user}:</span> "{item.post}"
                    </div>
                    <div className="bg-[#1E2538] p-3 rounded-lg border border-[#2D3748] relative">
                      <p className="text-sm text-white"><span className="text-[#EE1D52] font-semibold">Agent Reply:</span> "{item.reply}"</p>
                    </div>
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