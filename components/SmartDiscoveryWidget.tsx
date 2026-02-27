import React, { useState } from 'react';

interface PostAnalysis {
  post_id: string;
  author: string;
  text: string;
  url: string;
  likes: number;
  retweets: number;
  replies: number;
  relevance_score: number;
  engagement_potential: number;
  persona_recommendation: string;
  risk_level: string;
  angle_summary: string;
  recommendation_score: number;
  reasoning: string;
}

interface SmartDiscoveryResponse {
  query: string;
  found_posts: number;
  analyzed_posts: number;
  recommendations: PostAnalysis[];
  top_post: PostAnalysis | null;
}

const API_BASE = process.env.REACT_APP_API_BASE || 'http://localhost:8000/api/v1';

export default function SmartDiscoveryWidget() {
  const [query, setQuery] = useState('');
  const [minEngagement, setMinEngagement] = useState(100);
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<SmartDiscoveryResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleDiscover = async () => {
    if (!query.trim()) {
      setError('Please enter search keywords');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE}/hubs/x/smart-discovery`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: query.trim(),
          min_engagement: minEngagement,
          max_results: 10,
        }),
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.statusText}`);
      }

      const data: SmartDiscoveryResponse = await response.json();
      setResults(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to discover posts');
      setResults(null);
    } finally {
      setLoading(false);
    }
  };

  const getRiskColor = (risk: string) => {
    switch (risk.toLowerCase()) {
      case 'green': return 'text-green-500 bg-green-500/10 border-green-500/30';
      case 'yellow': return 'text-yellow-500 bg-yellow-500/10 border-yellow-500/30';
      case 'red': return 'text-red-500 bg-red-500/10 border-red-500/30';
      default: return 'text-gray-500 bg-gray-500/10 border-gray-500/30';
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 8) return 'text-green-500';
    if (score >= 6) return 'text-yellow-500';
    return 'text-gray-500';
  };

  const handleViewPost = (url: string) => {
    window.open(url, '_blank', 'noopener,noreferrer');
  };

  const handleAddToQueue = async (post: PostAnalysis) => {
    // TODO: Implement add to review queue
    console.log('Add to queue:', post.post_id);
    alert(`Adding post by @${post.author} to review queue (not implemented yet)`);
  };

  return (
    <div className="bg-[#131828] border border-[#1F2937] rounded-xl flex flex-col overflow-hidden">
      {/* Header */}
      <div className="p-4 border-b border-[#1F2937] flex justify-between items-center bg-[#1E2538]/50">
        <h3 className="font-semibold text-white flex items-center gap-2">
          <span className="material-symbols-outlined text-[#1DA1F2] text-[18px]">search</span>
          Smart Discovery
        </h3>
        <span className="text-[10px] uppercase bg-[#1DA1F2]/20 text-[#1DA1F2] px-2 py-0.5 rounded border border-[#1DA1F2]/30">
          AI-Powered
        </span>
      </div>

      {/* Input Form */}
      <div className="p-4 space-y-4 bg-[#0B0F1A]">
        <div>
          <label className="block text-xs text-gray-400 mb-2 uppercase tracking-wider">
            Search Keywords
          </label>
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="e.g., OpenClaw security, AI agent vulnerabilities..."
            className="w-full px-4 py-2.5 bg-[#131828] border border-[#2D3748] rounded-lg text-white text-sm placeholder-gray-600 focus:outline-none focus:border-[#1DA1F2]/50 transition-colors"
            onKeyPress={(e) => e.key === 'Enter' && handleDiscover()}
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-xs text-gray-400 mb-2 uppercase tracking-wider">
              Min Engagement
            </label>
            <input
              type="number"
              value={minEngagement}
              onChange={(e) => setMinEngagement(parseInt(e.target.value) || 100)}
              min="10"
              step="10"
              className="w-full px-4 py-2.5 bg-[#131828] border border-[#2D3748] rounded-lg text-white text-sm focus:outline-none focus:border-[#1DA1F2]/50 transition-colors"
            />
          </div>
          <div className="flex items-end">
            <button
              onClick={handleDiscover}
              disabled={loading}
              className="w-full px-4 py-2.5 bg-[#1DA1F2] text-white rounded-lg text-sm font-medium hover:bg-[#1DA1F2]/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {loading ? (
                <>
                  <span className="material-symbols-outlined text-[18px] animate-spin">refresh</span>
                  Discovering...
                </>
              ) : (
                <>
                  <span className="material-symbols-outlined text-[18px]">search</span>
                  Discover & Analyze
                </>
              )}
            </button>
          </div>
        </div>

        {error && (
          <div className="p-3 bg-red-500/10 border border-red-500/30 rounded-lg text-red-500 text-sm flex items-center gap-2">
            <span className="material-symbols-outlined text-[18px]">error</span>
            {error}
          </div>
        )}
      </div>

      {/* Results */}
      <div className="flex-1 overflow-y-auto scroller">
        {results && (
          <div className="p-4 space-y-4">
            {/* Summary */}
            <div className="p-3 bg-[#1E2538]/50 border border-[#2D3748] rounded-lg">
              <div className="flex items-center justify-between text-xs">
                <span className="text-gray-400">
                  Found <span className="text-white font-bold">{results.found_posts}</span> posts,
                  analyzed <span className="text-white font-bold">{results.analyzed_posts}</span>
                </span>
                <span className="text-gray-500">Query: "{results.query}"</span>
              </div>
            </div>

            {/* Recommendations */}
            {results.recommendations.length > 0 ? (
              <div className="space-y-3">
                {results.recommendations.map((post, index) => (
                  <div
                    key={post.post_id}
                    className="p-4 border border-[#2D3748] rounded-lg bg-[#0B0F1A] hover:border-[#1DA1F2]/50 transition-colors"
                  >
                    {/* Score Badge */}
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex items-center gap-2">
                        <span className={`text-2xl font-bold ${getScoreColor(post.recommendation_score)}`}>
                          {post.recommendation_score.toFixed(1)}
                        </span>
                        <span className="text-xs text-gray-500">/10</span>
                        {index === 0 && (
                          <span className="ml-2 px-2 py-0.5 bg-yellow-500/20 text-yellow-500 text-[10px] font-bold rounded border border-yellow-500/30 uppercase">
                            Top Pick
                          </span>
                        )}
                      </div>
                      <span className={`px-2 py-0.5 text-[10px] font-bold rounded border uppercase ${getRiskColor(post.risk_level)}`}>
                        {post.risk_level}
                      </span>
                    </div>

                    {/* Author & Engagement */}
                    <div className="flex items-center gap-4 mb-2 text-xs text-gray-400">
                      <span className="text-[#1DA1F2]">@{post.author}</span>
                      <span>🔥 {post.likes} likes</span>
                      <span>🔁 {post.retweets} RT</span>
                      <span>💬 {post.replies} replies</span>
                    </div>

                    {/* Post Text */}
                    <p className="text-sm text-white mb-3 line-clamp-3 leading-relaxed">
                      {post.text}
                    </p>

                    {/* Analysis */}
                    <div className="space-y-2 mb-3 p-3 bg-[#131828] rounded border border-[#2D3748]">
                      <div className="grid grid-cols-2 gap-2 text-xs">
                        <div>
                          <span className="text-gray-500">Relevance:</span>
                          <span className="text-white font-bold ml-2">{post.relevance_score.toFixed(1)}/10</span>
                        </div>
                        <div>
                          <span className="text-gray-500">Engagement:</span>
                          <span className="text-white font-bold ml-2">{post.engagement_potential.toFixed(1)}/10</span>
                        </div>
                      </div>
                      <div className="text-xs">
                        <span className="text-gray-500">Persona:</span>
                        <span className="text-[#1DA1F2] font-medium ml-2">{post.persona_recommendation}</span>
                      </div>
                      <div className="text-xs text-gray-400 italic">
                        💡 {post.angle_summary}
                      </div>
                      <div className="text-[10px] text-gray-500 pt-2 border-t border-[#2D3748]">
                        {post.reasoning}
                      </div>
                    </div>

                    {/* Actions */}
                    <div className="flex gap-2">
                      <button
                        onClick={() => handleViewPost(post.url)}
                        className="flex-1 px-3 py-2 bg-[#1E2538] text-[#1DA1F2] border border-[#1DA1F2]/30 rounded text-xs font-medium hover:bg-[#1DA1F2]/10 transition-colors flex items-center justify-center gap-1"
                      >
                        <span className="material-symbols-outlined text-[14px]">open_in_new</span>
                        View Post
                      </button>
                      <button
                        onClick={() => handleAddToQueue(post)}
                        className="flex-1 px-3 py-2 bg-[#1DA1F2]/10 text-[#1DA1F2] border border-[#1DA1F2]/30 rounded text-xs font-medium hover:bg-[#1DA1F2]/20 transition-colors flex items-center justify-center gap-1"
                      >
                        <span className="material-symbols-outlined text-[14px]">add_circle</span>
                        Add to Queue
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="flex flex-col items-center justify-center py-16 text-gray-500">
                <span className="material-symbols-outlined text-4xl mb-2">search_off</span>
                <p className="text-sm">No relevant posts found. Try different keywords.</p>
              </div>
            )}
          </div>
        )}

        {!results && !loading && (
          <div className="flex flex-col items-center justify-center py-16 px-6 text-center">
            <span className="material-symbols-outlined text-5xl mb-4 text-[#1DA1F2]/30">psychology</span>
            <h4 className="text-white font-semibold mb-2">AI-Powered Post Discovery</h4>
            <p className="text-sm text-gray-500 max-w-md">
              Enter keywords to discover high-engagement posts. GenClaw will analyze relevance, 
              recommend personas, assess risk, and score engagement potential.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
