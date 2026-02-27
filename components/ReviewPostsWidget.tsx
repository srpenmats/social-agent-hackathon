import React, { useState, useEffect } from 'react';

interface ReviewPost {
  id: string;
  post_id: string;
  author: string;
  text: string;
  url: string;
  likes: number;
  retweets: number;
  replies: number;
  quotes?: number;
  bookmarks?: number;
  impressions?: number;
  relevance_score: number;
  engagement_potential: number;
  persona_recommendation: string;
  risk_level: string;
  angle_summary: string;
  recommendation_score: number;
  status: 'pending' | 'draft' | 'approved';
  draft_comment?: string;
  created_at: string;
}

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || process.env.REACT_APP_API_BASE || 'https://social-agent-hackathon-production.up.railway.app/api/v1';

export default function ReviewPostsWidget() {
  const [posts, setPosts] = useState<ReviewPost[]>([]);
  const [loading, setLoading] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editComment, setEditComment] = useState('');
  const [filter, setFilter] = useState<'all' | 'pending' | 'draft' | 'approved'>('pending');

  useEffect(() => {
    loadReviewPosts();
  }, [filter]);

  const loadReviewPosts = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/jen/review-posts?status=${filter}`);
      const data = await response.json();
      setPosts(data.posts || []);
    } catch (error) {
      console.error('Failed to load review posts:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleEdit = (post: ReviewPost) => {
    setEditingId(post.id);
    setEditComment(post.draft_comment || '');
  };

  const handleSaveDraft = async (postId: string) => {
    try {
      await fetch(`${API_BASE}/jen/review-posts/${postId}/draft`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ comment: editComment })
      });
      setEditingId(null);
      loadReviewPosts();
    } catch (error) {
      console.error('Failed to save draft:', error);
    }
  };

  const handleApprove = async (postId: string, comment: string) => {
    if (!confirm('Approve this comment for posting?')) return;
    
    try {
      await fetch(`${API_BASE}/jen/review-posts/${postId}/approve`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ comment })
      });
      loadReviewPosts();
    } catch (error) {
      console.error('Failed to approve:', error);
    }
  };

  const handleRemove = async (postId: string) => {
    if (!confirm('Remove this post from review queue?')) return;
    
    try {
      await fetch(`${API_BASE}/jen/review-posts/${postId}`, {
        method: 'DELETE'
      });
      loadReviewPosts();
    } catch (error) {
      console.error('Failed to remove:', error);
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

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pending': return 'text-blue-500 bg-blue-500/10 border-blue-500/30';
      case 'draft': return 'text-yellow-500 bg-yellow-500/10 border-yellow-500/30';
      case 'approved': return 'text-green-500 bg-green-500/10 border-green-500/30';
      default: return 'text-gray-500 bg-gray-500/10 border-gray-500/30';
    }
  };

  return (
    <div className="bg-[#131828] border border-[#1F2937] rounded-xl flex flex-col overflow-hidden">
      {/* Header */}
      <div className="p-4 border-b border-[#1F2937] flex justify-between items-center bg-[#1E2538]/50">
        <h3 className="font-semibold text-white flex items-center gap-2">
          <span className="material-symbols-outlined text-[20px]">rate_review</span>
          Review Posts
        </h3>
        
        {/* Status Filter */}
        <div className="flex gap-2">
          {(['all', 'pending', 'draft', 'approved'] as const).map(status => (
            <button
              key={status}
              onClick={() => setFilter(status)}
              className={`px-3 py-1 text-xs font-medium rounded transition-colors ${
                filter === status
                  ? 'bg-[#1DA1F2] text-white'
                  : 'bg-[#1E2538] text-gray-400 hover:bg-[#1DA1F2]/20'
              }`}
            >
              {status.charAt(0).toUpperCase() + status.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {/* Posts List */}
      <div className="flex-1 overflow-y-auto scroller p-4 space-y-4">
        {loading ? (
          <div className="text-center py-8 text-gray-400">
            <span className="material-symbols-outlined text-[32px] animate-spin">refresh</span>
            <p className="mt-2">Loading...</p>
          </div>
        ) : posts.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <span className="material-symbols-outlined text-[32px]">inbox</span>
            <p className="mt-2">No posts in review queue</p>
            <p className="text-xs mt-1">Add posts from Smart Discovery</p>
          </div>
        ) : (
          posts.map(post => (
            <div
              key={post.id}
              className="bg-[#0B0F1A] border border-[#2D3748] rounded-lg p-4 hover:border-[#1DA1F2]/30 transition-colors"
            >
              {/* Header */}
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center gap-2">
                  <span className={`px-2 py-0.5 text-[10px] font-bold rounded border uppercase ${getStatusColor(post.status)}`}>
                    {post.status}
                  </span>
                  <span className={`px-2 py-0.5 text-[10px] font-bold rounded border uppercase ${getRiskColor(post.risk_level)}`}>
                    {post.risk_level}
                  </span>
                  <span className="text-xs text-gray-500">
                    Score: <span className="text-[#1DA1F2] font-bold">{post.recommendation_score.toFixed(1)}</span>/10
                  </span>
                </div>
                
                <button
                  onClick={() => handleRemove(post.id)}
                  className="text-gray-500 hover:text-red-500 transition-colors"
                  title="Remove from queue"
                >
                  <span className="material-symbols-outlined text-[18px]">close</span>
                </button>
              </div>

              {/* Original Post */}
              <div className="mb-3 p-3 bg-[#131828] rounded border border-[#2D3748]">
                <div className="flex items-center gap-3 mb-2 text-xs text-gray-400">
                  <span className="text-[#1DA1F2]">@{post.author}</span>
                  <span>❤️ {post.likes.toLocaleString()}</span>
                  <span>🔁 {post.retweets.toLocaleString()}</span>
                  <span>💬 {post.replies.toLocaleString()}</span>
                </div>
                <p className="text-sm text-white mb-2 line-clamp-3">{post.text}</p>
                <a
                  href={post.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-xs text-[#1DA1F2] hover:underline flex items-center gap-1"
                >
                  <span className="material-symbols-outlined text-[12px]">open_in_new</span>
                  View on Twitter
                </a>
              </div>

              {/* Jen Analysis */}
              <div className="mb-3 p-3 bg-[#131828] rounded border border-[#2D3748]">
                <div className="text-xs font-semibold text-[#10B981] mb-1">
                  ✅ Jen's Recommendation:
                </div>
                <div className="text-xs text-gray-400 mb-2">
                  <span className="text-gray-500">Persona:</span>
                  <span className="text-[#1DA1F2] font-medium ml-2">{post.persona_recommendation}</span>
                </div>
                <div className="text-xs text-gray-400 italic">
                  💡 {post.angle_summary}
                </div>
              </div>

              {/* Comment Editor */}
              {editingId === post.id ? (
                <div className="space-y-2">
                  <textarea
                    value={editComment}
                    onChange={(e) => setEditComment(e.target.value)}
                    placeholder="Write your comment..."
                    className="w-full px-3 py-2 bg-[#131828] border border-[#2D3748] rounded text-white text-sm resize-none focus:outline-none focus:border-[#1DA1F2]/50"
                    rows={4}
                  />
                  <div className="flex gap-2">
                    <button
                      onClick={() => handleSaveDraft(post.id)}
                      className="flex-1 px-3 py-2 bg-yellow-500/10 text-yellow-500 border border-yellow-500/30 rounded text-xs font-medium hover:bg-yellow-500/20 transition-colors"
                    >
                      💾 Save Draft
                    </button>
                    <button
                      onClick={() => handleApprove(post.id, editComment)}
                      className="flex-1 px-3 py-2 bg-green-500/10 text-green-500 border border-green-500/30 rounded text-xs font-medium hover:bg-green-500/20 transition-colors"
                    >
                      ✅ Approve & Post
                    </button>
                    <button
                      onClick={() => setEditingId(null)}
                      className="px-3 py-2 bg-[#1E2538] text-gray-400 rounded text-xs font-medium hover:bg-[#2D3748] transition-colors"
                    >
                      Cancel
                    </button>
                  </div>
                </div>
              ) : post.draft_comment ? (
                <div className="space-y-2">
                  <div className="p-3 bg-[#131828] rounded border border-[#2D3748]">
                    <div className="text-xs text-gray-500 mb-1">Draft Comment:</div>
                    <p className="text-sm text-white">{post.draft_comment}</p>
                  </div>
                  <div className="flex gap-2">
                    <button
                      onClick={() => handleEdit(post)}
                      className="flex-1 px-3 py-2 bg-[#1DA1F2]/10 text-[#1DA1F2] border border-[#1DA1F2]/30 rounded text-xs font-medium hover:bg-[#1DA1F2]/20 transition-colors"
                    >
                      ✏️ Edit
                    </button>
                    <button
                      onClick={() => handleApprove(post.id, post.draft_comment)}
                      className="flex-1 px-3 py-2 bg-green-500/10 text-green-500 border border-green-500/30 rounded text-xs font-medium hover:bg-green-500/20 transition-colors"
                    >
                      ✅ Approve & Post
                    </button>
                  </div>
                </div>
              ) : (
                <button
                  onClick={() => handleEdit(post)}
                  className="w-full px-3 py-2 bg-[#1DA1F2]/10 text-[#1DA1F2] border border-[#1DA1F2]/30 rounded text-xs font-medium hover:bg-[#1DA1F2]/20 transition-colors"
                >
                  ✏️ Write Comment
                </button>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
}
