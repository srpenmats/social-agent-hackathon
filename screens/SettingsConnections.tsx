import React, { useState, useEffect } from 'react';
import { ConnectionsAPI, ApiError } from '../services/api';

const platformConfig: Record<string, { name: string; icon: string; iconBg: string; iconContent?: string }> = {
  tiktok: {
    name: 'TikTok',
    icon: 'music_note',
    iconBg: 'bg-black border border-[#1F2937]',
  },
  instagram: {
    name: 'Instagram',
    icon: 'photo_camera',
    iconBg: 'bg-gradient-to-tr from-[#f09433] via-[#dc2743] to-[#bc1888]',
  },
  x: {
    name: 'X (Twitter)',
    icon: '',
    iconBg: 'bg-black border border-gray-700',
    iconContent: 'X',
  },
};

export default function SettingsConnections() {
  const [connections, setConnections] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [connecting, setConnecting] = useState<string | null>(null);
  const [disconnecting, setDisconnecting] = useState<string | null>(null);
  const [testing, setTesting] = useState<string | null>(null);

  useEffect(() => {
    loadConnections();

    // Handle OAuth callback
    const params = new URLSearchParams(window.location.search);
    const code = params.get('code');
    const state = params.get('state');
    const platform = params.get('platform');
    if (code && state && platform) {
      ConnectionsAPI.handleCallback(platform, code, state)
        .then(() => {
          // Clear URL params and reload connections
          window.history.replaceState({}, '', window.location.pathname);
          loadConnections();
        })
        .catch((err) => console.error('OAuth callback failed:', err));
    }
  }, []);

  const loadConnections = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await ConnectionsAPI.getConnections();
      setConnections(data);
    } catch (e) {
      setError(e instanceof ApiError ? e.detail : 'Failed to load connections.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleConnect = async (platform: string) => {
    setConnecting(platform);
    try {
      const result = await ConnectionsAPI.connect(platform);
      if (result.auth_url) {
        window.location.href = result.auth_url;
      }
    } catch (e) {
      console.error('Connect failed:', e);
      setConnecting(null);
    }
  };

  const handleDisconnect = async (platform: string) => {
    if (!confirm(`Are you sure you want to disconnect ${platformConfig[platform]?.name || platform}? This will stop all workers for this platform.`)) return;
    setDisconnecting(platform);
    try {
      await ConnectionsAPI.disconnect(platform);
      setConnections(prev => prev.map(c => c.platform === platform ? { ...c, connected: false } : c));
    } catch (e) {
      console.error('Disconnect failed:', e);
    } finally {
      setDisconnecting(null);
    }
  };

  const handleTest = async (platform: string) => {
    setTesting(platform);
    try {
      const result = await ConnectionsAPI.testConnection(platform);
      alert(result.healthy ? `${platformConfig[platform]?.name}: Connection healthy!` : `${platformConfig[platform]?.name}: ${result.message}`);
    } catch (e) {
      alert(`Test failed for ${platformConfig[platform]?.name}`);
    } finally {
      setTesting(null);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-16">
        <div className="w-8 h-8 border-4 border-blue-400 border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center py-16">
        <span className="material-symbols-outlined text-4xl text-red-400 mb-4">error_outline</span>
        <p className="text-gray-400 text-sm mb-4">{error}</p>
        <button onClick={loadConnections} className="px-4 py-2 bg-[#1E2538] text-white rounded hover:bg-[#2D3748] transition-colors text-sm">Retry</button>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto space-y-8">
      <div className="flex justify-between items-end mb-6">
        <div>
          <h3 className="text-xl font-semibold text-white">Platform Connections</h3>
          <p className="text-sm text-gray-400 mt-1">Manage authentication via backend OAuth paths. Connected accounts automatically start API workers.</p>
        </div>
      </div>

      {connections.length === 0 ? (
        <div className="text-center py-12 text-gray-500">
          <span className="material-symbols-outlined text-4xl mb-2">link_off</span>
          <p className="text-sm">No platforms available. Check backend configuration.</p>
        </div>
      ) : connections.map((conn: any) => {
        const config = platformConfig[conn.platform] || { name: conn.platform, icon: 'link', iconBg: 'bg-gray-800' };

        return (
          <div key={conn.platform} className="glass-card rounded-xl p-6 relative overflow-hidden bg-[#131828] border border-[#2D3748]">
            <div className="flex flex-col md:flex-row gap-6 relative z-10">
              <div className={`w-16 h-16 ${config.iconBg} rounded-xl flex items-center justify-center`}>
                {config.iconContent ? (
                  <span className="text-white text-3xl font-bold font-sans">{config.iconContent}</span>
                ) : (
                  <span className="material-symbols-outlined text-white text-3xl">{config.icon}</span>
                )}
              </div>
              <div className="flex-1 space-y-4">
                <div className="flex justify-between">
                  <h4 className="text-lg font-bold text-white flex items-center gap-2">
                    {config.name}
                    <span className={`px-2 py-0.5 rounded-full text-xs font-medium flex items-center gap-1.5 ${
                      conn.connected
                        ? 'bg-green-900/30 text-green-400 border border-green-500/30'
                        : 'bg-red-900/30 text-red-400 border border-red-500/30'
                    }`}>
                      <span className={`w-1.5 h-1.5 rounded-full ${conn.connected ? 'bg-green-500' : 'bg-red-500'}`}></span>
                      {conn.connected ? 'Connected' : 'Disconnected'}
                    </span>
                  </h4>
                  {conn.connected && conn.token_status && (
                    <p className={`text-sm font-medium ${conn.token_status === 'valid' ? 'text-green-400' : 'text-yellow-400'}`}>
                      {conn.token_status === 'valid' ? 'Valid Token' : 'Token Expiring'}
                    </p>
                  )}
                </div>
                {conn.connected && (
                  <div className="flex gap-4 pt-2">
                    {conn.auth_method && (
                      <div className="bg-gray-900/50 p-3 rounded-lg border border-gray-800">
                        <p className="text-xs text-gray-500 uppercase">Auth Method</p>
                        <p className="text-sm text-gray-200">{conn.auth_method}</p>
                      </div>
                    )}
                    {conn.workers && (
                      <div className="bg-gray-900/50 p-3 rounded-lg border border-gray-800">
                        <p className="text-xs text-gray-500 uppercase">Active Workers</p>
                        <p className="text-sm text-gray-200">{conn.workers}</p>
                      </div>
                    )}
                    {conn.last_sync && (
                      <div className="bg-gray-900/50 p-3 rounded-lg border border-gray-800">
                        <p className="text-xs text-gray-500 uppercase">Last Sync</p>
                        <p className="text-sm text-gray-200">{conn.last_sync}</p>
                      </div>
                    )}
                  </div>
                )}
                {!conn.connected && (
                  <p className="text-sm text-gray-400">Connect your {config.name} account to enable monitoring and engagement.</p>
                )}
              </div>
              <div className="flex flex-col justify-center gap-3 pl-6 border-l border-gray-800">
                {conn.connected ? (
                  <>
                    <button
                      onClick={() => handleTest(conn.platform)}
                      disabled={testing === conn.platform}
                      className="flex items-center justify-center gap-2 bg-[#1E2538] hover:bg-[#2D3748] text-white px-4 py-2 rounded-md text-sm font-medium transition-colors disabled:opacity-50"
                    >
                      {testing === conn.platform ? (
                        <span className="material-symbols-outlined animate-spin text-base">autorenew</span>
                      ) : (
                        <span className="material-symbols-outlined text-base">speed</span>
                      )}
                      Test Connection
                    </button>
                    <button
                      onClick={() => handleDisconnect(conn.platform)}
                      disabled={disconnecting === conn.platform}
                      className="text-red-400 hover:text-red-300 text-sm font-medium text-center disabled:opacity-50"
                    >
                      {disconnecting === conn.platform ? 'Disconnecting...' : 'Disconnect'}
                    </button>
                  </>
                ) : (
                  <button
                    onClick={() => handleConnect(conn.platform)}
                    disabled={connecting === conn.platform}
                    className="w-full flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors"
                  >
                    {connecting === conn.platform ? (
                      <span className="material-symbols-outlined animate-spin text-base">autorenew</span>
                    ) : (
                      <span className="material-symbols-outlined text-base">login</span>
                    )}
                    Connect via OAuth
                  </button>
                )}
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}
