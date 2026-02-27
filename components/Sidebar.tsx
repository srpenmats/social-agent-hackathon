import React, { useState, useEffect } from 'react';
import { RoutePath } from '../App';
import { ReviewAPI } from '../services/api';

interface SidebarProps {
  currentRoute: RoutePath;
  onNavigate: (route: RoutePath) => void;
}

export default function Sidebar({ currentRoute, onNavigate }: SidebarProps) {
  const [pendingCount, setPendingCount] = useState(0);

  useEffect(() => {
    ReviewAPI.getQueue()
      .then((data: any) => setPendingCount(data.pending_count ?? data.items?.length ?? 0))
      .catch(() => {});
  }, [currentRoute]);
  const navItemClass = (path: RoutePath) => `
    flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-md transition-colors group cursor-pointer
    ${currentRoute === path 
      ? 'bg-[#1F2937]/50 text-white border border-[#1F2937] border-l-2 border-l-[#10B981]' 
      : 'text-gray-400 hover:text-white hover:bg-[#1F2937]/30'
    }
  `;

  return (
    <aside className="w-64 flex-shrink-0 border-r border-[#1F2937] bg-[#0B0F1A] flex flex-col justify-between z-20">
      <div>
        <div className="h-16 flex items-center px-6 border-b border-[#1F2937]">
          <div className="flex items-center gap-2 font-bold text-lg tracking-tight text-white">
            <span className="material-symbols-outlined text-[#10B981]">smart_toy</span>
            <span>SocialAgent<span className="text-[#10B981] text-xs align-top ml-0.5">PRO</span></span>
          </div>
        </div>
        
        <nav className="p-4 space-y-1">
          <div onClick={() => onNavigate('/overview')} className={navItemClass('/overview')}>
            <span className="material-symbols-outlined text-[20px] overflow-hidden whitespace-nowrap">dashboard</span>
            Overview
          </div>

          <div className="pt-4 pb-2 px-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">Hubs</div>
          <div onClick={() => onNavigate('/hub/tiktok')} className={navItemClass('/hub/tiktok')}>
            <span className="material-symbols-outlined text-[20px] overflow-hidden whitespace-nowrap text-[#EE1D52]">music_note</span>
            TikTok Hub
          </div>
          <div onClick={() => onNavigate('/hub/instagram')} className={navItemClass('/hub/instagram')}>
            <span className="material-symbols-outlined text-[20px] overflow-hidden whitespace-nowrap text-[#E1306C]">photo_camera</span>
            Instagram Hub
          </div>
          <div onClick={() => onNavigate('/hub/x')} className={navItemClass('/hub/x')}>
            <span className="text-lg font-bold w-[20px] text-center leading-none text-[#1DA1F2]">X</span>
            X / Twitter Hub
          </div>

          <div className="pt-4 pb-2 px-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">Management</div>
          <div onClick={() => onNavigate('/personas')} className={navItemClass('/personas')}>
            <span className="material-symbols-outlined text-[20px] overflow-hidden whitespace-nowrap text-[#F59E0B]">psychology</span>
            AI Personas
          </div>
          <div onClick={() => onNavigate('/library')} className={navItemClass('/library')}>
            <span className="material-symbols-outlined text-[20px] overflow-hidden whitespace-nowrap text-[#a855f7]">library_books</span>
            Comment Library
          </div>
          <div onClick={() => onNavigate('/learning')} className={navItemClass('/learning')}>
            <span className="material-symbols-outlined text-[20px] text-[#10B981]">model_training</span>
            AI Learning
          </div>
          <div onClick={() => onNavigate('/review')} className={`${navItemClass('/review')} flex justify-between`}>
            <div className="flex items-center gap-3">
              <span className="material-symbols-outlined text-[20px] overflow-hidden whitespace-nowrap">rate_review</span>
              Review Queue
            </div>
            {pendingCount > 0 && <span className="bg-[#EF4444] text-white text-[10px] font-bold px-1.5 py-0.5 rounded-full">{pendingCount}</span>}
          </div>
        </nav>
      </div>

      <div className="p-4 border-t border-[#1F2937]">
        <div onClick={() => onNavigate('/settings')} className={navItemClass('/settings')}>
          <span className="material-symbols-outlined text-[20px] overflow-hidden whitespace-nowrap">settings</span>
          Settings
        </div>
        
        <div className="mt-4 flex items-center gap-3 px-3">
          <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-purple-500 to-blue-500 flex items-center justify-center text-xs font-bold text-white shadow-lg">
            JD
          </div>
          <div className="flex flex-col">
            <span className="text-xs font-medium text-white">Jane Doe</span>
            <span className="text-[10px] text-gray-500">Admin</span>
          </div>
        </div>
      </div>
    </aside>
  );
}