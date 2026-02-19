import React, { useState, useEffect } from 'react';
import { HubAPI } from '../services/api';

export default function XHub() {
  const [data, setData] = useState<any>(null);

  useEffect(() => {
    HubAPI.getStats('x').then(setData).catch(console.error);
  }, []);

  if (!data) {
    return (
      <div className="flex-1 bg-[#0B0F1A] flex flex-col items-center justify-center">
        <div className="w-10 h-10 border-4 border-[#1DA1F2] border-t-transparent rounded-full animate-spin"></div>
        <span className="text-[#1DA1F2] mt-4 font-medium tracking-widest uppercase text-sm animate-pulse">Loading X Data...</span>
      </div>
    );
  }

  return (
    <div className="flex-1 flex flex-col h-full bg-[#0B0F1A] overflow-hidden">
      <header className="h-20 px-8 border-b border-[#1F2937] bg-gradient-to-r from-[#131828] to-[#0B0F1A] flex items-center justify-between shrink-0 relative overflow-hidden">
        <div className="absolute top-0 right-0 w-64 h-full bg-gradient-to-l from-[#1DA1F2]/10 to-transparent pointer-events-none"></div>
        <div className="absolute bottom-0 left-0 w-full h-[1px] bg-gradient-to-r from-[#1DA1F2]/50 to-transparent"></div>
        
        <div className="flex items-center gap-4 z-10">
          <div className="w-12 h-12 rounded-xl bg-black border border-[#1F2937] flex items-center justify-center shadow-[0_0_15px_rgba(29,161,242,0.2)]">
            <span className="text-white text-3xl font-bold font-sans">X</span>
          </div>
          <div>
            <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2">
              X Command Hub
              <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-[#10B981]/20 text-[#10B981] border border-[#10B981]/30 uppercase tracking-wider">Active</span>
            </h1>
            <p className="text-sm text-gray-400">Monitoring mentions, industry keywords, and thread engagements.</p>
          </div>
        </div>
      </header>

      <div className="flex-1 overflow-y-auto p-8 scroller flex flex-col gap-8">
        {/* Stats Row */}
        <div className="grid grid-cols-4 gap-4">
          {[
            { label: 'Mentions Replied', value: data.stats.replies, trend: '+5%', color: 'text-[#1DA1F2]' },
            { label: 'Keywords Triggered', value: data.stats.keywords, trend: '-2%', color: 'text-gray-300' },
            { label: 'Avg Sentiment', value: data.stats.sentiment, trend: '78%', color: 'text-[#10B981]' },
            { label: 'API Quota', value: data.stats.quota, trend: 'Reset 4h', color: 'text-yellow-400' },
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
           {/* Keyword Streams */}
           <div className="bg-[#131828] border border-[#1F2937] rounded-xl flex flex-col overflow-hidden">
             <div className="p-4 border-b border-[#1F2937] flex justify-between items-center bg-[#1E2538]/50">
              <h3 className="font-semibold text-white">Keyword Streams</h3>
              <span className="material-symbols-outlined text-gray-400">filter_list</span>
            </div>
            <div className="flex-1 p-4 overflow-y-auto scroller space-y-4">
              {data.keywords.map((stream: any, i: number) => (
                <div key={i} className="p-4 border border-[#2D3748] rounded-lg bg-[#0B0F1A] hover:border-[#1DA1F2]/50 transition-colors cursor-pointer">
                  <div className="flex justify-between items-start mb-2">
                    <span className="font-mono text-sm text-[#1DA1F2]">{stream.term}</span>
                    <span className="text-[10px] uppercase bg-[#1E2538] text-gray-400 px-2 py-0.5 rounded border border-[#2D3748]">{stream.action}</span>
                  </div>
                  <p className="text-xs text-gray-400 italic mb-2 line-clamp-2">Match: "{stream.match}"</p>
                  <div className="flex items-center gap-2 text-[10px] text-gray-500">
                    <span className="w-1.5 h-1.5 rounded-full bg-green-500"></span> Active Stream • Volume: {stream.volume}
                  </div>
                </div>
              ))}
            </div>
           </div>

           {/* Drafts / Pending Review */}
           <div className="bg-[#131828] border border-[#1F2937] rounded-xl flex flex-col overflow-hidden">
             <div className="p-4 border-b border-[#1F2937] flex justify-between items-center bg-[#1E2538]/50">
              <h3 className="font-semibold text-white flex items-center gap-2">
                 <span className="material-symbols-outlined text-yellow-500 text-[18px]">warning</span>
                 High-Risk Drafts
              </h3>
              <button className="text-xs bg-[#1DA1F2]/20 text-[#1DA1F2] px-2 py-1 rounded font-medium">Review All ({data.drafts.length})</button>
            </div>
            <div className="flex-1 p-0 overflow-y-auto scroller divide-y divide-[#2D3748]">
              {data.drafts.map((item: any, i: number) => (
                <div key={i} className="p-5 bg-[#0B0F1A] hover:bg-[#131828] transition-colors">
                  <div className="text-xs text-gray-500 mb-2">Replying to <span className="text-[#1DA1F2]">{item.user}</span></div>
                  <p className="text-sm text-gray-300 mb-3">"{item.msg}"</p>
                  
                  <div className="relative">
                    <div className="absolute left-0 top-0 bottom-0 w-1 bg-yellow-500 rounded-l"></div>
                    <div className="bg-[#1E2538] p-3 pl-4 rounded rounded-l-none border border-[#2D3748] border-l-0">
                      <div className="text-[10px] font-bold text-yellow-500 mb-1 uppercase">Draft Response (Needs Approval)</div>
                      <p className="text-sm text-white">"{item.draft}"</p>
                    </div>
                  </div>
                  
                  <div className="mt-3 flex gap-2">
                    <button className="flex-1 py-1.5 bg-[#10B981]/10 text-[#10B981] border border-[#10B981]/30 rounded text-xs font-medium hover:bg-[#10B981]/20">Approve</button>
                    <button className="flex-1 py-1.5 bg-[#EF4444]/10 text-[#EF4444] border border-[#EF4444]/30 rounded text-xs font-medium hover:bg-[#EF4444]/20">Reject</button>
                    <button className="px-3 py-1.5 bg-[#2D3748] text-white rounded text-xs font-medium hover:bg-[#394559] material-symbols-outlined text-[14px]">edit</button>
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