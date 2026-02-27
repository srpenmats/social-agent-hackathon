import React, { useState, useEffect } from 'react';
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
import { apiFetch, ApiError } from '../services/api';

interface FeedbackStats {
  total_decisions: number;
  approved_count: number;
  denied_count: number;
  approval_rate: number;
  recent_approval_rate: number;
  improvement: number;
  active_approved_examples: number;
  active_denied_examples: number;
}

interface TrendPoint {
  date: string;
  approval_rate: number;
  total: number;
  approved: number;
  denied: number;
}

interface FeedbackExample {
  id: number;
  comment_text: string;
  original_post_text: string;
  original_post_author?: string;
  platform: string;
  approach?: string;
  risk_score: number;
  decision_reason?: string;
  decided_at: string;
}

export default function AILearning() {
  const [stats, setStats] = useState<FeedbackStats | null>(null);
  const [trend, setTrend] = useState<TrendPoint[]>([]);
  const [examples, setExamples] = useState<{ approved: FeedbackExample[]; denied: FeedbackExample[] }>({ approved: [], denied: [] });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([
      apiFetch<FeedbackStats>('/feedback/stats'),
      apiFetch<{ trend: TrendPoint[] }>('/feedback/accuracy-trend'),
      apiFetch<{ approved: FeedbackExample[]; denied: FeedbackExample[] }>('/feedback/examples'),
    ])
      .then(([statsData, trendData, examplesData]) => {
        setStats(statsData);
        setTrend(trendData.trend || []);
        setExamples(examplesData);
        setLoading(false);
      })
      .catch((err) => {
        setError(err instanceof ApiError ? err.detail : 'Unable to load AI Learning data.');
        setLoading(false);
      });
  }, []);

  if (error) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center bg-[#0B0F1A]">
        <span className="material-symbols-outlined text-5xl text-red-400 mb-4">cloud_off</span>
        <h2 className="text-xl font-bold text-white mb-2">Connection Error</h2>
        <p className="text-gray-400 text-sm mb-6 max-w-md text-center">{error}</p>
        <button onClick={() => window.location.reload()} className="px-6 py-2 bg-[#1E2538] text-white rounded hover:bg-[#2D3748] transition-colors">Retry</button>
      </div>
    );
  }

  if (loading || !stats) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center bg-[#0B0F1A]">
        <div className="w-10 h-10 border-4 border-[#10B981] border-t-transparent rounded-full animate-spin"></div>
        <span className="text-[#10B981] mt-4 font-medium tracking-widest uppercase text-sm animate-pulse">Loading AI Learning...</span>
      </div>
    );
  }

  const approvalPct = Math.round(stats.approval_rate);
  const recentPct = Math.round(stats.recent_approval_rate);
  const improvementDelta = Math.round(stats.improvement);

  return (
    <div className="flex-1 flex flex-col h-full bg-[#0B0F1A]">
      {/* Header */}
      <header className="h-16 flex items-center justify-between px-8 border-b border-[#1F2937] bg-[#0B0F1A] flex-shrink-0">
        <nav aria-label="Breadcrumb" className="flex">
          <ol className="flex items-center space-x-2">
            <li>
              <span className="text-gray-400 hover:text-white cursor-pointer flex items-center">
                <span className="material-symbols-outlined text-[20px]">home</span>
              </span>
            </li>
            <li><span className="text-gray-600">/</span></li>
            <li><span className="text-sm font-medium text-white">AI Learning Loop</span></li>
          </ol>
        </nav>
        <div className="flex items-center gap-3">
          <span className="px-3 py-1 rounded-full text-[10px] font-bold bg-[#10B981]/20 text-[#10B981] border border-[#10B981]/30 uppercase tracking-wider flex items-center gap-1.5">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-[#10B981] opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-[#10B981]"></span>
            </span>
            Learning Active
          </span>
        </div>
      </header>

      <div className="flex-1 overflow-y-auto p-8 scroller">
        {/* Stats Cards Row */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          {/* Approval Rate */}
          <div className="bg-[#131828] border border-[#1F2937] rounded-xl p-5 shadow-sm">
            <div className="flex justify-between items-start mb-2">
              <span className="text-sm text-gray-400 font-medium">Approval Rate</span>
              <span className="material-symbols-outlined text-gray-500 text-[20px]">verified</span>
            </div>
            <div className="flex items-baseline gap-2">
              <span className="text-2xl font-bold text-white">{approvalPct}%</span>
              <span className={`text-xs font-medium flex items-center ${improvementDelta >= 0 ? 'text-[#10B981]' : 'text-[#EF4444]'}`}>
                <span className="material-symbols-outlined text-[14px]">
                  {improvementDelta >= 0 ? 'arrow_upward' : 'arrow_downward'}
                </span> {Math.abs(improvementDelta)}%
              </span>
            </div>
            <div className="h-1 w-full bg-[#1F2937] mt-4 rounded-full overflow-hidden">
              <div className="h-full bg-[#10B981] rounded-full transition-all duration-500" style={{ width: `${approvalPct}%` }}></div>
            </div>
          </div>

          {/* Total Feedback */}
          <div className="bg-[#131828] border border-[#1F2937] rounded-xl p-5 shadow-sm">
            <div className="flex justify-between items-start mb-2">
              <span className="text-sm text-gray-400 font-medium">Total Feedback</span>
              <span className="material-symbols-outlined text-gray-500 text-[20px]">forum</span>
            </div>
            <div className="flex items-baseline gap-2">
              <span className="text-2xl font-bold text-white">{stats.total_decisions}</span>
            </div>
            <p className="text-xs text-gray-500 mt-3">{stats.approved_count} approved / {stats.denied_count} denied</p>
          </div>

          {/* Learning Improvement */}
          <div className="bg-[#131828] border border-[#1F2937] rounded-xl p-5 shadow-sm">
            <div className="flex justify-between items-start mb-2">
              <span className="text-sm text-gray-400 font-medium">Learning Improvement</span>
              <span className="material-symbols-outlined text-gray-500 text-[20px]">trending_up</span>
            </div>
            <div className="flex items-baseline gap-2">
              <span className={`text-2xl font-bold ${improvementDelta >= 0 ? 'text-[#10B981]' : 'text-[#EF4444]'}`}>
                {improvementDelta >= 0 ? '+' : ''}{improvementDelta}%
              </span>
            </div>
            <p className="text-xs text-gray-500 mt-3">Recent {recentPct}% vs overall {approvalPct}%</p>
          </div>

          {/* Context Window */}
          <div className="bg-[#131828] border border-[#1F2937] rounded-xl p-5 shadow-sm">
            <div className="flex justify-between items-start mb-2">
              <span className="text-sm text-gray-400 font-medium">Context Window</span>
              <div className="flex items-center gap-1">
                <span className="material-symbols-outlined text-gray-500 text-[20px]">memory</span>
                <span className="material-symbols-outlined text-gray-600 text-[16px] cursor-help" title="Number of examples actively fed into the AI's system prompt for learning">info</span>
              </div>
            </div>
            <div className="flex items-baseline gap-2">
              <span className="text-2xl font-bold text-white">{stats.active_approved_examples + stats.active_denied_examples}</span>
              <span className="text-xs text-gray-500">examples</span>
            </div>
            <p className="text-xs text-gray-500 mt-3">{stats.active_approved_examples} approved, {stats.active_denied_examples} denied</p>
          </div>
        </div>

        {/* Accuracy Over Time Chart */}
        <div className="bg-[#131828] rounded-xl p-6 border border-[#1F2937] mb-8">
          <div className="flex justify-between items-center mb-6">
            <div>
              <h3 className="text-lg font-semibold text-white">Approval Rate Over Time</h3>
              <p className="text-xs text-gray-500">Model learning from human feedback</p>
            </div>
            <div className="flex items-center gap-2 text-xs">
              <span className="w-2 h-2 rounded-full bg-[#10B981]"></span>
              <span className="text-gray-400">Approval Rate</span>
            </div>
          </div>
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={trend} margin={{ top: 10, right: 0, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="colorApproval" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#10B981" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#10B981" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <XAxis dataKey="date" stroke="#4B5563" fontSize={10} tickLine={false} axisLine={false} />
                <YAxis stroke="#4B5563" fontSize={10} tickLine={false} axisLine={false} tickFormatter={(v: number) => `${Math.round(v)}%`} domain={[0, 100]} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#1F2937', border: '1px solid #374151', borderRadius: '8px', fontSize: '12px' }}
                  itemStyle={{ color: '#fff' }}
                  formatter={(value: number) => [`${Math.round(value)}%`, 'Approval Rate']}
                  labelStyle={{ color: '#9CA3AF' }}
                />
                <Area type="monotone" dataKey="approval_rate" stroke="#10B981" strokeWidth={2} fillOpacity={1} fill="url(#colorApproval)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Examples Row */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          {/* Approved Examples */}
          <div className="bg-[#131828] border border-[#1F2937] rounded-xl flex flex-col overflow-hidden">
            <div className="p-4 border-b border-[#1F2937] bg-[#1E2538]/50">
              <div className="flex items-center gap-2">
                <span className="material-symbols-outlined text-[#10B981] text-[18px]">check_circle</span>
                <h3 className="font-semibold text-white">Teaching the AI: Do This</h3>
              </div>
              <p className="text-xs text-gray-500 mt-1">These approved comments are fed as positive examples</p>
            </div>
            <div className="flex-1 p-4 overflow-y-auto scroller space-y-3 max-h-[400px]">
              {examples.approved.length > 0 ? examples.approved.map((ex) => (
                <div key={ex.id} className="border-l-2 border-[#10B981] bg-[#0B0F1A] rounded-r-lg p-4">
                  <p className="text-xs text-gray-500 italic mb-2 line-clamp-2">"{ex.original_post_text}"</p>
                  <p className="text-sm text-white mb-3">"{ex.comment_text}"</p>
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-[#10B981]/20 text-[#10B981] border border-[#10B981]/30">
                      Risk: {ex.risk_score != null ? ex.risk_score.toFixed(1) : 'N/A'}
                    </span>
                    {ex.approach && (
                      <span className="px-2 py-0.5 rounded text-[10px] font-medium bg-[#1DA1F2]/10 text-[#1DA1F2] border border-[#1DA1F2]/20">
                        {ex.approach}
                      </span>
                    )}
                    {ex.platform && (
                      <span className="px-2 py-0.5 rounded text-[10px] font-medium bg-[#F59E0B]/10 text-[#F59E0B] border border-[#F59E0B]/20">
                        {ex.platform}
                      </span>
                    )}
                  </div>
                </div>
              )) : (
                <div className="flex flex-col items-center justify-center py-12 text-gray-500">
                  <span className="material-symbols-outlined text-3xl mb-2">school</span>
                  <p className="text-sm">No approved examples yet.</p>
                  <p className="text-xs text-gray-600 mt-1">Approve comments in the Review Queue to start teaching.</p>
                </div>
              )}
            </div>
          </div>

          {/* Denied Examples */}
          <div className="bg-[#131828] border border-[#1F2937] rounded-xl flex flex-col overflow-hidden">
            <div className="p-4 border-b border-[#1F2937] bg-[#1E2538]/50">
              <div className="flex items-center gap-2">
                <span className="material-symbols-outlined text-[#EF4444] text-[18px]">cancel</span>
                <h3 className="font-semibold text-white">Teaching the AI: Avoid This</h3>
              </div>
              <p className="text-xs text-gray-500 mt-1">These denied comments are fed as negative examples</p>
            </div>
            <div className="flex-1 p-4 overflow-y-auto scroller space-y-3 max-h-[400px]">
              {examples.denied.length > 0 ? examples.denied.map((ex) => (
                <div key={ex.id} className="border-l-2 border-[#EF4444] bg-[#0B0F1A] rounded-r-lg p-4">
                  <p className="text-xs text-gray-500 italic mb-2 line-clamp-2">"{ex.original_post_text}"</p>
                  <p className="text-sm text-white mb-3">"{ex.comment_text}"</p>
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-[#EF4444]/20 text-[#EF4444] border border-[#EF4444]/30">
                      Risk: {ex.risk_score != null ? ex.risk_score.toFixed(1) : 'N/A'}
                    </span>
                    {ex.decision_reason && (
                      <span className="px-2 py-0.5 rounded text-[10px] font-medium bg-[#EF4444]/10 text-[#EF4444] border border-[#EF4444]/20">
                        {ex.decision_reason}
                      </span>
                    )}
                  </div>
                </div>
              )) : (
                <div className="flex flex-col items-center justify-center py-12 text-gray-500">
                  <span className="material-symbols-outlined text-3xl mb-2">block</span>
                  <p className="text-sm">No denied examples yet.</p>
                  <p className="text-xs text-gray-600 mt-1">Deny comments in the Review Queue to teach the AI what to avoid.</p>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* How It Works Pipeline */}
        <div className="bg-[#131828] rounded-xl p-6 border border-[#1F2937]">
          <h3 className="text-lg font-semibold text-white mb-2">How It Works</h3>
          <p className="text-xs text-gray-500 mb-6">The AI Learning Loop continuously improves comment quality based on your feedback</p>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-0 items-stretch">
            {[
              { icon: 'person', title: 'Human Reviews', desc: 'Approve or deny AI-generated comments', color: '#1DA1F2' },
              { icon: 'save', title: 'Feedback Stored', desc: 'Decisions saved to learning database', color: '#F59E0B' },
              { icon: 'psychology', title: 'Context Injection', desc: 'Examples fed into LLM system prompt', color: '#a855f7' },
              { icon: 'trending_up', title: 'Better Output', desc: 'AI generates more on-brand comments', color: '#10B981' },
            ].map((step, i) => (
              <div key={i} className="flex items-center">
                <div className="flex-1 flex flex-col items-center text-center px-2">
                  <div
                    className="w-12 h-12 rounded-xl flex items-center justify-center mb-3"
                    style={{ backgroundColor: `${step.color}20`, border: `1px solid ${step.color}30` }}
                  >
                    <span className="material-symbols-outlined text-[24px]" style={{ color: step.color }}>{step.icon}</span>
                  </div>
                  <h4 className="text-sm font-semibold text-white mb-1">{step.title}</h4>
                  <p className="text-[11px] text-gray-500 leading-relaxed">{step.desc}</p>
                </div>
                {i < 3 && (
                  <div className="hidden md:flex items-center text-gray-600 flex-shrink-0 px-1">
                    <span className="material-symbols-outlined text-[20px]">chevron_right</span>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
