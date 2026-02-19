import React, { useState } from 'react';
import SettingsConnections from './SettingsConnections';

type SettingsTab = 'connections' | 'keys' | 'voice' | 'risk' | 'discovery' | 'execution';

interface AttachedFile {
  id: string;
  name: string;
  modified: string;
  size: string;
  type: 'code' | 'doc' | 'pdf' | 'json';
}

const initialFiles: Record<string, AttachedFile[]> = {
  voice: [
    { id: '1', name: 'brand_voice_guidelines_v2.pdf', modified: '2 days ago', size: '2.4 MB', type: 'pdf' },
    { id: '2', name: 'tone_modifiers.json', modified: '5 hours ago', size: '12 KB', type: 'json' },
  ],
  risk: [
    { id: '3', name: 'compliance_rules_2024.docx', modified: '1 week ago', size: '1.1 MB', type: 'doc' },
    { id: '4', name: 'forbidden_topics_list.md', modified: '3 days ago', size: '45 KB', type: 'code' },
  ],
  discovery: [
    { id: '5', name: 'target_audience_personas.pdf', modified: '1 month ago', size: '3.2 MB', type: 'pdf' },
    { id: '6', name: 'keyword_tracking_config.json', modified: 'Just now', size: '8 KB', type: 'json' },
  ],
  execution: [
    { id: '7', name: 'posting_schedule_limits.md', modified: '2 weeks ago', size: '15 KB', type: 'code' },
  ]
};

const tabInfo: Record<SettingsTab, { label: string, desc: string, icon: string, color: string, isKB?: boolean }> = {
  connections: { label: 'Connections', desc: 'Social platform authentications.', icon: 'hub', color: 'text-blue-400' },
  keys: { label: 'API Keys', desc: 'LLM and third-party API keys.', icon: 'key', color: 'text-yellow-400' },
  voice: { label: 'Brand Voice', desc: 'Upload brand guidelines, tone-of-voice documents, and persona traits.', icon: 'record_voice_over', color: 'text-[#00B894]', isKB: true },
  risk: { label: 'Risk & Compliance', desc: 'Upload compliance rules, forbidden topics (no-go zones), and legal constraints.', icon: 'gavel', color: 'text-blue-400', isKB: true },
  discovery: { label: 'Discovery', desc: 'Upload target keywords, audience definitions, and platform monitoring strategies.', icon: 'radar', color: 'text-purple-400', isKB: true },
  execution: { label: 'Execution', desc: 'Upload posting schedules, approval workflows, and engagement limits.', icon: 'rocket_launch', color: 'text-[#F59E0B]', isKB: true }
};

export default function Settings() {
  const [activeTab, setActiveTab] = useState<SettingsTab>('connections');
  const [filesByTab, setFilesByTab] = useState<Record<string, AttachedFile[]>>(initialFiles);
  const [isUploading, setIsUploading] = useState(false);

  const activeInfo = tabInfo[activeTab];
  const activeFiles = activeInfo.isKB ? filesByTab[activeTab] || [] : [];

  const handleDragOver = (e: React.DragEvent) => e.preventDefault();
  
  const handleDrop = (e: React.DragEvent) => {
    if (!activeInfo.isKB) return;
    e.preventDefault();
    setIsUploading(true);
    
    setTimeout(() => {
      setIsUploading(false);
      const newFile: AttachedFile = {
        id: Math.random().toString(36).substr(2, 9),
        name: `new_${activeTab}_document.pdf`,
        modified: 'Just now',
        size: '1.8 MB',
        type: 'pdf'
      };
      
      setFilesByTab(prev => ({
        ...prev,
        [activeTab]: [newFile, ...(prev[activeTab] || [])]
      }));
    }, 1500);
  };

  const handleDelete = (fileId: string) => {
    if (!activeInfo.isKB) return;
    setFilesByTab(prev => ({
      ...prev,
      [activeTab]: prev[activeTab].filter(f => f.id !== fileId)
    }));
  };

  const renderAPIKeys = () => (
    <div className="max-w-5xl mx-auto space-y-6">
      <div className="flex justify-between items-end mb-6">
        <div>
          <h3 className="text-xl font-semibold text-white">API Keys & Integrations</h3>
          <p className="text-sm text-gray-400 mt-1">Manage external provider keys for LLMs, analytics, and other services.</p>
        </div>
      </div>
      <div className="space-y-4">
        {/* Anthropic */}
        <div className="bg-[#131828] border border-[#2D3748] rounded-xl p-6 flex items-center justify-between group hover:border-gray-500 transition-colors">
          <div className="flex gap-4 items-center">
            <div className="w-12 h-12 bg-gray-800 rounded-lg flex items-center justify-center border border-gray-700">
              <span className="material-symbols-outlined text-purple-400 text-2xl">psychology</span>
            </div>
            <div>
              <h4 className="text-white font-medium">Anthropic (Claude 3.5 Sonnet)</h4>
              <div className="flex items-center gap-2 mt-1">
                <span className="text-xs bg-green-500/10 text-green-400 px-2 py-0.5 rounded border border-green-500/20">Connected</span>
                <span className="text-xs text-gray-500 font-mono">sk-ant-api03-••••••••••••</span>
              </div>
            </div>
          </div>
          <button className="px-4 py-2 border border-[#2D3748] hover:bg-[#1E2538] text-white rounded-lg text-sm transition-colors">Edit Key</button>
        </div>
        
        {/* OpenAI */}
        <div className="bg-[#131828] border border-[#2D3748] rounded-xl p-6 flex items-center justify-between group hover:border-gray-500 transition-colors">
          <div className="flex gap-4 items-center">
            <div className="w-12 h-12 bg-gray-800 rounded-lg flex items-center justify-center border border-gray-700">
              <span className="material-symbols-outlined text-green-400 text-2xl">memory</span>
            </div>
            <div>
              <h4 className="text-white font-medium">OpenAI</h4>
              <div className="flex items-center gap-2 mt-1">
                <span className="text-xs bg-gray-500/10 text-gray-400 px-2 py-0.5 rounded border border-gray-500/20">Not Configured</span>
              </div>
            </div>
          </div>
          <button className="px-4 py-2 bg-[#00B894] hover:bg-[#00a383] text-white rounded-lg text-sm transition-colors font-medium">Add Key</button>
        </div>

        {/* Google Gemini */}
        <div className="bg-[#131828] border border-[#2D3748] rounded-xl p-6 flex items-center justify-between group hover:border-gray-500 transition-colors">
          <div className="flex gap-4 items-center">
            <div className="w-12 h-12 bg-gray-800 rounded-lg flex items-center justify-center border border-gray-700">
              <span className="material-symbols-outlined text-blue-400 text-2xl">model_training</span>
            </div>
            <div>
              <h4 className="text-white font-medium">Google Gemini</h4>
              <div className="flex items-center gap-2 mt-1">
                <span className="text-xs bg-green-500/10 text-green-400 px-2 py-0.5 rounded border border-green-500/20">Connected</span>
                <span className="text-xs text-gray-500 font-mono">AIzaSy••••••••••••</span>
              </div>
            </div>
          </div>
          <button className="px-4 py-2 border border-[#2D3748] hover:bg-[#1E2538] text-white rounded-lg text-sm transition-colors">Edit Key</button>
        </div>
      </div>
    </div>
  );

  const renderKnowledgeBase = () => (
    <div className="max-w-5xl mx-auto space-y-6">
      <div className="flex justify-between items-end mb-2">
        <div>
          <h3 className="text-lg font-semibold text-white flex items-center gap-2">
            {activeInfo.label} Files
          </h3>
          <p className="text-sm text-gray-400 mt-1">{activeInfo.desc}</p>
        </div>
        <span className="text-xs font-mono text-gray-500 bg-[#131828] border border-[#2D3748] px-2 py-1 rounded">
          {activeFiles.length} file(s) indexed
        </span>
      </div>

      <div 
        onDragOver={handleDragOver}
        onDrop={handleDrop}
        className={`border-2 border-dashed rounded-2xl p-10 flex flex-col items-center justify-center transition-all cursor-pointer group relative overflow-hidden
          ${isUploading ? 'border-[#00B894] bg-[#00B894]/5' : 'border-[#2D3748] hover:border-[#00B894] bg-[#131828]/50 hover:bg-[#131828]'}
        `}
      >
        {isUploading && (
          <div className="absolute inset-0 bg-[#0B0F1A]/60 backdrop-blur-sm flex items-center justify-center z-10">
            <div className="flex flex-col items-center gap-3">
              <div className="w-8 h-8 border-4 border-[#00B894] border-t-transparent rounded-full animate-spin"></div>
              <span className="text-sm font-medium text-[#00B894] animate-pulse">Processing file...</span>
            </div>
          </div>
        )}
        <div className={`w-16 h-16 rounded-full flex items-center justify-center mb-4 transition-colors ${isUploading ? 'bg-[#00B894]/20' : 'bg-[#1E2538] group-hover:bg-[#00B894]/20'}`}>
          <span className={`material-symbols-outlined text-3xl transition-colors ${isUploading ? 'text-[#00B894]' : 'text-gray-400 group-hover:text-[#00B894]'}`}>
            cloud_upload
          </span>
        </div>
        <p className="text-base font-medium text-white mb-2">Drag and drop documents here</p>
        <p className="text-sm text-gray-500 mb-4">or click to browse your files</p>
        <div className="flex gap-2">
          <span className="text-[10px] uppercase font-bold text-gray-400 bg-[#0B0F1A] border border-[#2D3748] px-2 py-1 rounded">PDF</span>
          <span className="text-[10px] uppercase font-bold text-gray-400 bg-[#0B0F1A] border border-[#2D3748] px-2 py-1 rounded">DOCX</span>
          <span className="text-[10px] uppercase font-bold text-gray-400 bg-[#0B0F1A] border border-[#2D3748] px-2 py-1 rounded">JSON</span>
          <span className="text-[10px] uppercase font-bold text-gray-400 bg-[#0B0F1A] border border-[#2D3748] px-2 py-1 rounded">MD</span>
        </div>
      </div>

      <div className="bg-[#131828] border border-[#2D3748] rounded-xl overflow-hidden shadow-sm">
        <div className="grid grid-cols-12 gap-4 px-6 py-4 bg-[#1E2538] border-b border-[#2D3748] text-xs font-semibold text-gray-400 uppercase tracking-wider">
          <div className="col-span-6">File Name</div>
          <div className="col-span-3">Last Modified</div>
          <div className="col-span-2">Size</div>
          <div className="col-span-1 text-center">Actions</div>
        </div>
        <div className="divide-y divide-[#2D3748]">
          {activeFiles.length === 0 ? (
            <div className="p-10 text-center text-gray-500 text-sm flex flex-col items-center gap-2">
              <span className="material-symbols-outlined text-4xl opacity-50">description</span>
              No files uploaded for {activeInfo.label} yet.
            </div>
          ) : (
            activeFiles.map((file) => (
              <div key={file.id} className="grid grid-cols-12 gap-4 px-6 py-4 items-center hover:bg-[#1E2538]/50 transition-colors group">
                <div className="col-span-6 flex items-center gap-3 overflow-hidden">
                  <div className={`w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 ${
                    file.type === 'pdf' ? 'bg-red-500/10 text-red-400' :
                    file.type === 'json' ? 'bg-yellow-500/10 text-yellow-400' :
                    file.type === 'doc' ? 'bg-blue-500/10 text-blue-400' :
                    'bg-purple-500/10 text-purple-400'
                  }`}>
                    <span className="material-symbols-outlined text-[18px]">
                      {file.type === 'code' ? 'data_object' : file.type === 'json' ? 'settings_ethernet' : 'description'}
                    </span>
                  </div>
                  <span className="text-sm text-gray-200 truncate font-mono text-[13px] group-hover:text-[#00B894] transition-colors cursor-pointer">
                    {file.name}
                  </span>
                </div>
                <div className="col-span-3 text-sm text-gray-500">{file.modified}</div>
                <div className="col-span-2 text-sm text-gray-500">{file.size}</div>
                <div className="col-span-1 flex justify-center opacity-0 group-hover:opacity-100 transition-opacity">
                  <button 
                    onClick={() => handleDelete(file.id)}
                    className="text-gray-500 hover:text-red-400 transition-colors p-1"
                    title="Delete File"
                  >
                    <span className="material-symbols-outlined text-[20px]">delete</span>
                  </button>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );

  return (
    <div className="flex-1 flex flex-col h-full bg-[#0B0F1A] overflow-hidden">
      <header className="bg-[#131828] border-b border-[#1F2937] px-8 py-5 flex justify-between items-center shrink-0">
        <div className="flex items-center gap-4">
          <div>
            <h2 className="text-2xl font-bold text-white flex items-center gap-3">
              <span className="material-symbols-outlined text-[#00B894] text-3xl">settings</span>
              Settings & Configuration
            </h2>
            <p className="text-sm text-gray-400 mt-1">Manage system integrations, platform authentications, and AI Knowledge Base documents.</p>
          </div>
        </div>
        
        {activeInfo.isKB && (
          <div className="flex items-center gap-4">
            <button className="px-4 py-2 rounded-md text-sm font-medium transition-colors flex items-center gap-2 shadow-lg bg-[#00B894] hover:bg-[#00a383] shadow-[#00B894]/20 text-white">
              <span className="material-symbols-outlined text-[18px]">sync</span>
              Sync Knowledge Base
            </button>
          </div>
        )}
      </header>

      <div className="px-8 border-b border-[#1F2937] shrink-0 bg-[#0B0F1A] overflow-x-auto scroller">
        <div className="flex items-center">
          {/* System Settings */}
          <div className="flex space-x-6 pr-6">
            {(['connections', 'keys'] as SettingsTab[]).map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`py-4 text-sm font-medium transition-colors flex items-center gap-2 whitespace-nowrap ${
                  activeTab === tab 
                    ? `border-b-2 border-white text-white` 
                    : 'text-gray-400 hover:text-gray-200'
                }`}
              >
                <span className={`material-symbols-outlined text-[18px] ${activeTab === tab ? tabInfo[tab].color : ''}`}>
                  {tabInfo[tab].icon}
                </span>
                {tabInfo[tab].label}
              </button>
            ))}
          </div>

          <div className="w-px h-6 bg-[#2D3748] flex-shrink-0"></div>
          
          <div className="flex items-center pl-6">
            <span className="text-[10px] font-bold text-gray-500 uppercase tracking-wider mr-4">Knowledge Base:</span>
            <div className="flex space-x-6">
              {(['voice', 'risk', 'discovery', 'execution'] as SettingsTab[]).map((tab) => (
                <button
                  key={tab}
                  onClick={() => setActiveTab(tab)}
                  className={`py-4 text-sm font-medium transition-colors flex items-center gap-2 whitespace-nowrap ${
                    activeTab === tab 
                      ? `border-b-2 border-white text-white` 
                      : 'text-gray-400 hover:text-gray-200'
                  }`}
                >
                  <span className={`material-symbols-outlined text-[18px] ${activeTab === tab ? tabInfo[tab].color : ''}`}>
                    {tabInfo[tab].icon}
                  </span>
                  {tabInfo[tab].label}
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-8 scroller relative">
        {activeTab === 'connections' && <SettingsConnections />}
        {activeTab === 'keys' && renderAPIKeys()}
        {activeInfo.isKB && renderKnowledgeBase()}
      </div>
    </div>
  );
}