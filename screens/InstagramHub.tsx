import React, { useState, useEffect } from 'react';
import { HubAPI } from '../services/api';

export default function InstagramHub() {
  const [data, setData] = useState<any>(null);

  useEffect(() => {
    HubAPI.getStats('instagram').then(setData).catch(console.error);
  }, []);

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
            <p className="text-sm text-gray-400">Managing Reel comments, Story replies, and DM automations.</p>
          </div>
        </div>
      </header>

      <div className="flex-1 overflow-y-auto p-8 scroller">
        {/* Stats Row */}
        <div className="grid grid-cols-4 gap-4 mb-8">
          {[
            { label: 'Reel Comments', value: data.stats.comments, trend: '+12%', color: 'text-[#E1306C]' },
            { label: 'Story Replies', value: data.stats.storyReplies, trend: '+45%', color: 'text-[#f09433]' },
            { label: 'DMs Handled', value: data.stats.dms, trend: '-2%', color: 'text-[#bc1888]' },
            { label: 'Profile Clicks', value: data.stats.clicks, trend: '+18%', color: 'text-white' },
          ].map((stat, i) => (
            <div key={i} className="bg-[#131828] border border-[#1F2937] rounded-xl p-5 shadow-sm">
              <div className="text-xs text-gray-500 uppercase tracking-wider mb-2">{stat.label}</div>
              <div className="flex items-end justify-between">
                <div className="text-3xl font-bold text-white">{stat.value}</div>
                <div className={`text-xs font-bold ${stat.color} bg-black/20 px-2 py-1 rounded`}>{stat.trend}</div>
              </div>
            </div>
          ))}
        </div>

        <div className="grid grid-cols-12 gap-8 h-[calc(100%-120px)] min-h-[500px]">
          {/* Top Performing Content */}
          <div className="col-span-4 bg-[#131828] border border-[#1F2937] rounded-xl flex flex-col overflow-hidden">
             <div className="p-4 border-b border-[#1F2937] flex justify-between items-center bg-[#1E2538]/50">
              <h3 className="font-semibold text-white">Top Performing Content</h3>
            </div>
            <div className="p-4 grid grid-cols-2 gap-4 flex-1 overflow-y-auto scroller">
              {data.topContent.map((item: any, i: number) => (
                <div key={i} className="relative group cursor-pointer">
                  <div className="aspect-[4/5] rounded-lg bg-gray-800 overflow-hidden border border-[#2D3748] group-hover:border-[#E1306C] transition-colors relative">
                    <img src={item.img} alt="post" className="w-full h-full object-cover opacity-80 group-hover:opacity-100 transition-opacity" />
                    <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent"></div>
                  </div>
                  <div className="absolute bottom-2 left-2 right-2 flex justify-between items-end">
                    <span className="text-[10px] text-white flex items-center gap-1 font-medium drop-shadow-md">
                      <span className="material-symbols-outlined text-[12px]">favorite</span> {item.likes}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Live Activity Feed */}
          <div className="col-span-8 bg-[#131828] border border-[#1F2937] rounded-xl flex flex-col overflow-hidden">
            <div className="p-4 border-b border-[#1F2937] flex justify-between items-center bg-[#1E2538]/50">
              <div className="flex items-center gap-2">
                <span className="w-2 h-2 bg-[#E1306C] rounded-full animate-pulse"></span>
                <h3 className="font-semibold text-white">Live Activity Feed</h3>
              </div>
              <div className="flex gap-2">
                <button className="text-xs text-gray-400 hover:text-white px-2 py-1 rounded border border-[#2D3748]">Filter</button>
              </div>
            </div>
            <div className="p-4 space-y-4 overflow-y-auto scroller flex-1 bg-[#0B0F1A]/50">
               {data.feed.map((interaction: any, i: number) => (
                <div key={i} className="p-4 bg-[#1E2538]/50 rounded-xl border border-[#2D3748]">
                  <div className="flex items-center gap-3 mb-3 pb-3 border-b border-[#2D3748]">
                    <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-[#f09433] to-[#E1306C] p-[2px]">
                      <div className="w-full h-full bg-black rounded-full overflow-hidden">
                        <img src={`https://picsum.photos/50/50?random=${i+30}`} alt="avatar" />
                      </div>
                    </div>
                    <div>
                      <div className="text-sm font-semibold text-white">{interaction.user}</div>
                      <div className="text-[10px] text-gray-400">{interaction.type} • {interaction.source}</div>
                    </div>
                  </div>
                  <div className="pl-11 space-y-3">
                    <div className="text-sm text-gray-300">"{interaction.msg}"</div>
                    <div className="bg-[#0B0F1A] p-3 rounded-lg border border-[#2D3748]">
                      <div className="text-[10px] font-bold text-[#E1306C] mb-1 uppercase tracking-wider">Agent Reply</div>
                      <div className="text-sm text-white">{interaction.reply}</div>
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