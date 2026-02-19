import React, { useState } from 'react';
import { AuthAPI } from '../services/api';

export default function SettingsConnections() {
  const [connecting, setConnecting] = useState<string | null>(null);

  const handleConnect = async (platform: string) => {
    setConnecting(platform);
    // Simulate redirection to backend OAuth endpoint
    const authUrl = AuthAPI.getAuthUrl(platform);
    setTimeout(() => {
      // In a real app: window.location.href = authUrl;
      alert(`Redirecting to backend OAuth path: ${authUrl}`);
      setConnecting(null);
    }, 1000);
  };

  return (
    <div className="max-w-6xl mx-auto space-y-8">
      <div className="flex justify-between items-end mb-6">
        <div>
          <h3 className="text-xl font-semibold text-white">Platform Connections</h3>
          <p className="text-sm text-gray-400 mt-1">Manage authentication via backend OAuth paths. Connected accounts automatically start API workers.</p>
        </div>
      </div>

      {/* Instagram Connection (Disconnected Example) */}
      <div className="glass-card rounded-xl p-6 relative overflow-hidden">
        <div className="flex flex-col md:flex-row gap-6 relative z-10">
          <div className="w-16 h-16 bg-gradient-to-tr from-[#f09433] via-[#dc2743] to-[#bc1888] rounded-xl flex items-center justify-center">
            <span className="material-symbols-outlined text-white text-3xl">photo_camera</span>
          </div>
          <div className="flex-1 space-y-4">
            <h4 className="text-lg font-bold text-white flex items-center gap-2">
              Instagram
              <span className="px-2 py-0.5 rounded-full bg-red-900/30 text-red-400 border border-red-500/30 text-xs font-medium flex items-center gap-1.5">
                <span className="status-dot bg-red-500"></span> Disconnected
              </span>
            </h4>
            <p className="text-sm text-gray-400">Connect your Instagram Professional account to enable feed monitoring via Graph API.</p>
          </div>
          <div className="flex flex-col justify-center gap-3 pl-6 border-l border-gray-800">
            <button 
              onClick={() => handleConnect('instagram')}
              disabled={connecting === 'instagram'}
              className="w-full flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors"
            >
              {connecting === 'instagram' ? <span className="material-symbols-outlined animate-spin text-base">autorenew</span> : <span className="material-symbols-outlined text-base">login</span>}
              Connect via OAuth
            </button>
          </div>
        </div>
      </div>

      {/* X Connection (Connected Example) */}
      <div className="glass-card rounded-xl p-6 relative overflow-hidden">
        <div className="flex flex-col md:flex-row gap-6 relative z-10">
          <div className="w-16 h-16 bg-black rounded-xl border border-gray-700 flex items-center justify-center">
            <span className="text-white text-3xl font-bold font-sans">X</span>
          </div>
          <div className="flex-1 space-y-4">
            <div className="flex justify-between">
              <h4 className="text-lg font-bold text-white flex items-center gap-2">
                X (Twitter)
                <span className="px-2 py-0.5 rounded-full bg-green-900/30 text-green-400 border border-green-500/30 text-xs font-medium flex items-center gap-1.5">
                  <span className="status-dot bg-green-500"></span> Connected
                </span>
              </h4>
              <p className="text-sm text-green-400 font-medium">Valid Token</p>
            </div>
            <div className="flex gap-4 pt-2">
              <div className="bg-gray-900/50 p-3 rounded-lg border border-gray-800">
                <p className="text-xs text-gray-500 uppercase">Auth Method</p>
                <p className="text-sm text-gray-200">OAuth 2.0 PKCE</p>
              </div>
            </div>
          </div>
          <div className="flex flex-col justify-center gap-3 pl-6 border-l border-gray-800">
            <button className="text-red-400 hover:text-red-300 text-sm font-medium text-center">Disconnect</button>
          </div>
        </div>
      </div>
    </div>
  );
}