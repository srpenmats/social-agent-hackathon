import React, { useState, useEffect } from 'react';
import { AreaChart, Area, XAxis, Tooltip, ResponsiveContainer } from 'recharts';
import { RoutePath } from '../App';
import { DashboardAPI, ExecutionAPI, ConnectionsAPI, ApiError } from '../services/api';

type Timeframe = '24h' | '7d' | '30d';

interface OverviewProps {
  onNavigate: (route: RoutePath) => void;
}

export default function Overview({ onNavigate }: OverviewProps) {
  const [killSwitch, setKillSwitch] = useState(false);
  const [timeframe, setTimeframe] = useState<Timeframe>('24h');
  const [data, setData] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [systemStatus, setSystemStatus] = useState<any>(null);
  const [connections, setConnections] = useState<any[]>([]);
  const [togglingKill, setTogglingKill] = useState(false);

  useEffect(() => {
    setData(null);
    setError(null);
    DashboardAPI.getOverview(timeframe)
      .then(setData)
      .catch((err) => {
        setError(err instanceof ApiError ? err.detail : 'Unable to reach backend. Check your connection.');
      });
  }, [timeframe]);

  useEffect(() => {
    ExecutionAPI.getStatus()
      .then((status) => {
        setSystemStatus(status);
        setKillSwitch(status.kill_switch_enabled ?? false);
      })
      .catch(() => {});

    ConnectionsAPI.getConnections()
      .then(setConnections)
      .catch(() => {});
  }, []);

  const handleKillSwitch = async () => {
    setTogglingKill(true);
    try {
      await ExecutionAPI.setKillSwitch(!killSwitch);
      setKillSwitch(!killSwitch);
    } catch {
      // Revert on failure
    } finally {
      setTogglingKill(false);
    }
  };

  const connectedCount = connections.filter((c: any) => c.connected).length;
  const totalPlatforms = connections.length || 3;

  if (error) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center bg-[#0B0F1A]">
        <span className="material-symbols-outlined text-5xl text-red-400 mb-4">cloud_off</span>
        <h2 className="text-xl font-bold text-white mb-2">Connection Error</h2>
        <p className="text-gray-400 text-sm mb-6 max-w-md text-center">{error}</p>
        <button onClick={() => { setError(null); setData(null); DashboardAPI.getOverview(timeframe).then(setData).catch((e) => setError(e instanceof ApiError ? e.detail : 'Unable to reach backend.')); }} className="px-6 py-2 bg-[#1E2538] text-white rounded hover:bg-[#2D3748] transition-colors">Retry</button>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center bg-[#0B0F1A]">
        <div className="w-10 h-10 border-4 border-[#10B981] border-t-transparent rounded-full animate-spin"></div>
        <span className="text-[#10B981] mt-4 font-medium tracking-widest uppercase text-sm animate-pulse">Loading Dashboard...</span>
      </div>
    );
  }

  return (
    <div className="flex-1 flex flex-col h-full bg-[#0B0F1A]">
      <header className="h-16 flex items-center justify-between px-8 border-b border-[#1F2937] bg-[#0B0F1A] flex-shrink-0">
        <nav aria-label="Breadcrumb" className="flex">
          <ol className="flex items-center space-x-2">
            <li>
              <span className="text-gray-400 hover:text-white cursor-pointer flex items-center">
                <span className="material-symbols-outlined text-[20px]">home</span>
              </span>
            </li>
            <li><span className="text-gray-600">/</span></li>
            <li><span className="text-sm font-medium text-white">Overview Dashboard</span></li>
          </ol>
        </nav>
        <div className="flex items-center gap-4">
          <div className="flex bg-[#131828] rounded-lg p-1 border border-[#1F2937]">
            <button
              onClick={() => setTimeframe('24h')}
              className={`px-3 py-1 text-xs font-medium rounded transition-colors ${timeframe === '24h' ? 'bg-[#1F2937] text-white shadow-sm' : 'text-gray-400 hover:text-white'}`}
            >24h</button>
            <button
              onClick={() => setTimeframe('7d')}
              className={`px-3 py-1 text-xs font-medium rounded transition-colors ${timeframe === '7d' ? 'bg-[#1F2937] text-white shadow-sm' : 'text-gray-400 hover:text-white'}`}
            >7d</button>
            <button
              onClick={() => setTimeframe('30d')}
              className={`px-3 py-1 text-xs font-medium rounded transition-colors ${timeframe === '30d' ? 'bg-[#1F2937] text-white shadow-sm' : 'text-gray-400 hover:text-white'}`}
            >30d</button>
          </div>
          <button className="p-2 text-gray-400 hover:text-white transition-colors relative">
            <span className="material-symbols-outlined text-[20px]">notifications</span>
            <span className="absolute top-2 right-2 w-2 h-2 bg-red-500 rounded-full border border-[#0B0F1A]"></span>
          </button>
        </div>
      </header>

      <div className="flex-1 overflow-y-auto p-8 scroller">
        {/* Metrics Row */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          {data.stats.map((stat: any, i: number) => (
            <div key={i} className="bg-[#131828] border border-[#1F2937] rounded-xl p-5 shadow-sm">
              <div className="flex justify-between items-start mb-2">
                <span className="text-sm text-gray-400 font-medium">{stat.title}</span>
                <span className="material-symbols-outlined text-gray-500 text-[20px]">{stat.icon}</span>
              </div>
              <div className="flex items-baseline gap-2">
                <span className="text-2xl font-bold text-white">{stat.value}</span>
                <span className={`text-xs font-medium flex items-center ${stat.trendUp ? 'text-[#10B981]' : 'text-[#EF4444]'}`}>
                  <span className="material-symbols-outlined text-[14px]">
                    {stat.trendUp ? 'arrow_upward' : 'arrow_downward'}
                  </span> {stat.trend}
                </span>
              </div>
              <div className="h-1 w-full bg-[#1F2937] mt-4 rounded-full overflow-hidden">
                <div className={`h-full ${stat.color}`} style={{ width: `${stat.progress}%` }}></div>
              </div>
            </div>
          ))}

          <div className="bg-[#131828] border border-[#1F2937] rounded-xl p-5 shadow-sm">
            <div className="flex justify-between items-start mb-2">
              <span className="text-sm text-gray-400 font-medium">Active Platforms</span>
              <span className="material-symbols-outlined text-gray-500 text-[20px]">layers</span>
            </div>
            <div className="flex items-baseline gap-2">
              <span className="text-2xl font-bold text-white">{connectedCount}/{totalPlatforms}</span>
              <span className="text-xs text-gray-500">{connectedCount === totalPlatforms ? 'All Systems Go' : 'Some Disconnected'}</span>
            </div>
            <div className="flex gap-2 mt-4">
              <div className="w-2 h-2 rounded-full bg-[#EE1D52]"></div>
              <div className="w-2 h-2 rounded-full bg-[#E1306C]"></div>
              <div className="w-2 h-2 rounded-full bg-[#1DA1F2]"></div>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-8">
          <div className="lg:col-span-2 space-y-8">
            {/* Platform Health */}
            <div>
              <h3 className="text-sm font-semibold text-gray-400 mb-4 uppercase tracking-wider">Platform Health</h3>
              <div className="grid grid-cols-3 gap-4">
                {data.platformHealth.map((plat: any, i: number) => (
                  <div
                    key={i}
                    onClick={() => onNavigate(plat.route as RoutePath)}
                    className={`bg-[#131828] border border-[#1F2937] rounded-lg p-4 flex flex-col gap-3 transition-colors cursor-pointer group ${plat.hoverBorder}`}
                  >
                    <div className="flex justify-between items-center">
                      <div className="flex items-center gap-2">
                        <div className={`w-6 h-6 rounded bg-[#1F2937] flex items-center justify-center ${plat.color}`}>
                          <span className="material-symbols-outlined text-[16px] overflow-hidden whitespace-nowrap">{plat.icon}</span>
                        </div>
                        <span className={`text-sm font-medium text-white group-hover:${plat.color}`}>{plat.name}</span>
                      </div>
                      <span className={`w-2 h-2 rounded-full ${plat.statusColor || 'bg-[#10B981]'}`}></span>
                    </div>
                    <div className="grid grid-cols-2 gap-2 mt-1">
                      <div>
                        <div className="text-[10px] text-gray-500 uppercase">{plat.stat1Lbl}</div>
                        <div className="text-lg font-bold text-white">{plat.stat1Val}</div>
                      </div>
                      <div>
                        <div className="text-[10px] text-gray-500 uppercase">{plat.stat2Lbl}</div>
                        <div className="text-lg font-bold text-white">{plat.stat2Val}</div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Engagement Activity Chart */}
            <div className="bg-[#131828] rounded-xl p-6 border border-[#1F2937]">
              <div className="flex justify-between items-center mb-6">
                <div>
                  <h3 className="text-lg font-semibold text-white">Engagement Activity</h3>
                  <p className="text-xs text-gray-500">Comments posted over the selected timeframe</p>
                </div>
                <div className="flex gap-4 text-xs">
                  <div className="flex items-center gap-2"><span className="w-2 h-2 rounded-full bg-[#EE1D52]"></span><span className="text-gray-400">TikTok</span></div>
                  <div className="flex items-center gap-2"><span className="w-2 h-2 rounded-full bg-[#E1306C]"></span><span className="text-gray-400">Instagram</span></div>
                  <div className="flex items-center gap-2"><span className="w-2 h-2 rounded-full bg-[#1DA1F2]"></span><span className="text-gray-400">X</span></div>
                </div>
              </div>
              <div className="h-64 w-full relative">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={data.chart} margin={{ top: 10, right: 0, left: -20, bottom: 0 }}>
                    <defs>
                      <linearGradient id="colorTiktok" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#EE1D52" stopOpacity={0.3}/>
                        <stop offset="95%" stopColor="#EE1D52" stopOpacity={0}/>
                      </linearGradient>
                      <linearGradient id="colorIg" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#E1306C" stopOpacity={0.3}/>
                        <stop offset="95%" stopColor="#E1306C" stopOpacity={0}/>
                      </linearGradient>
                      <linearGradient id="colorX" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#1DA1F2" stopOpacity={0.3}/>
                        <stop offset="95%" stopColor="#1DA1F2" stopOpacity={0}/>
                      </linearGradient>
                    </defs>
                    <XAxis dataKey="time" stroke="#4B5563" fontSize={10} tickLine={false} axisLine={false} />
                    <Tooltip
                      contentStyle={{ backgroundColor: '#1F2937', border: '1px solid #374151', borderRadius: '8px', fontSize: '12px' }}
                      itemStyle={{ color: '#fff' }}
                    />
                    <Area type="monotone" dataKey="tiktok" stroke="#EE1D52" strokeWidth={2} fillOpacity={1} fill="url(#colorTiktok)" />
                    <Area type="monotone" dataKey="instagram" stroke="#E1306C" strokeWidth={2} fillOpacity={1} fill="url(#colorIg)" />
                    <Area type="monotone" dataKey="x" stroke="#1DA1F2" strokeWidth={2} fillOpacity={1} fill="url(#colorX)" />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>

          <div className="space-y-8">
            {/* System Status */}
            <div className="bg-[#131828] rounded-xl p-6 border border-[#1F2937]">
              <h3 className="text-sm font-semibold text-gray-400 mb-4 uppercase tracking-wider">System Status</h3>
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center gap-3">
                  <div className="relative flex h-3 w-3">
                    {!killSwitch && <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>}
                    <span className={`relative inline-flex rounded-full h-3 w-3 ${killSwitch ? 'bg-red-500' : 'bg-emerald-500'}`}></span>
                  </div>
                  <div>
                    <div className="text-white font-medium text-sm">{killSwitch ? 'Agent Halted' : 'Agent Running'}</div>
                    <div className="text-gray-500 text-xs">Uptime: {systemStatus?.uptime ?? '--'}</div>
                  </div>
                </div>
              </div>

              <div className="space-y-4 mb-6">
                <div className="flex justify-between text-xs">
                  <span className="text-gray-400">Discovery Latency</span>
                  <span className="text-white font-mono">{systemStatus?.discovery_latency_ms != null ? `${systemStatus.discovery_latency_ms}ms` : '--'}</span>
                </div>
                <div className="flex justify-between text-xs">
                  <span className="text-gray-400">Queue Depth</span>
                  <span className="text-white font-mono">{systemStatus?.queue_depth ?? '--'} items</span>
                </div>
                <div className="flex justify-between text-xs">
                  <span className="text-gray-400">API Health</span>
                  <span className={`${killSwitch ? 'text-red-500' : 'text-[#10B981]'} font-mono`}>{killSwitch ? '0%' : (systemStatus?.api_health ?? '--')}</span>
                </div>
              </div>

              <div className={`rounded-lg p-4 border transition-colors ${killSwitch ? 'bg-red-900/20 border-red-500/50' : 'bg-[#1F2937]/50 border-[#EF4444]/20'}`}>
                <div className="flex justify-between items-center">
                  <div>
                    <div className="text-white font-semibold text-sm">Kill Switch</div>
                    <div className="text-gray-500 text-[10px]">Stop all posting immediately</div>
                  </div>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input type="checkbox" className="sr-only peer" checked={killSwitch} disabled={togglingKill} onChange={handleKillSwitch} />
                    <div className="w-11 h-6 bg-gray-600 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-[#EF4444]"></div>
                  </label>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
