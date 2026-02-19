// API Client for SocialAgent Pro Backend

const BASE_URL = '/api/v1';

// Helper to handle API responses and gracefully fallback to mock data if backend is missing
async function apiFetch<T>(endpoint: string, options?: RequestInit, mockFallback?: T): Promise<T> {
  try {
    const token = localStorage.getItem('auth_token');
    const headers = {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...(options?.headers || {})
    };

    const response = await fetch(`${BASE_URL}${endpoint}`, { ...options, headers });
    
    if (!response.ok) {
      throw new Error(`API Error: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.warn(`[API Stub] Backend unreachable for ${endpoint}, returning fallback data.`);
    if (mockFallback !== undefined) {
      // Simulate network delay to test async loading states in UI
      await new Promise(resolve => setTimeout(resolve, 600));
      return mockFallback;
    }
    throw error;
  }
}

// --- Endpoints ---

export const AuthAPI = {
  getAuthUrl: (platform: string) => `${BASE_URL}/auth/${platform}/authorize`,
  disconnect: (platform: string) => apiFetch(`/auth/${platform}/disconnect`, { method: 'POST' }, { success: true })
};

export const DashboardAPI = {
  getOverview: (timeframe: '24h' | '7d' | '30d') => {
    const fallbacks = {
      '24h': {
        chart: [
          { time: '00:00', tiktok: 10, instagram: 5, x: 2 },
          { time: '04:00', tiktok: 20, instagram: 12, x: 3 },
          { time: '08:00', tiktok: 15, instagram: 25, x: 2 },
          { time: '12:00', tiktok: 35, instagram: 40, x: 1 },
          { time: '16:00', tiktok: 45, instagram: 50, x: 3 },
          { time: '20:00', tiktok: 75, instagram: 40, x: 10 },
          { time: '23:59', tiktok: 50, instagram: 15, x: 22 },
        ],
        stats: [
          { title: 'Total Engagements', value: '1,284', trend: '+12%', trendUp: true, icon: 'chat_bubble_outline', progress: 75, color: 'bg-[#10B981]' },
          { title: 'Avg Engagement Rate', value: '4.8%', trend: '+0.4%', trendUp: true, icon: 'ssid_chart', progress: 60, color: 'bg-blue-500' },
          { title: 'Approval Rate', value: '94.2%', trend: '-1.2%', trendUp: false, icon: 'check_circle', progress: 94, color: 'bg-purple-500' },
        ],
        platformHealth: [
          { name: 'TikTok', route: '/hub/tiktok', icon: 'music_note', color: 'text-[#EE1D52]', hoverBorder: 'hover:border-[#EE1D52]', stat1Lbl: 'Comments', stat1Val: '482', stat2Lbl: 'Avg Likes', stat2Val: '2.1k' },
          { name: 'Instagram', route: '/hub/instagram', icon: 'photo_camera', color: 'text-[#E1306C]', hoverBorder: 'hover:border-[#E1306C]', stat1Lbl: 'Comments', stat1Val: '315', stat2Lbl: 'Avg Likes', stat2Val: '856' },
          { name: 'X / Twitter', route: '/hub/x', icon: 'close', color: 'text-[#1DA1F2]', hoverBorder: 'hover:border-[#1DA1F2]', statusColor: 'bg-[#F59E0B]', stat1Lbl: 'Replies', stat1Val: '156', stat2Lbl: 'Impressions', stat2Val: '12k' },
        ]
      },
      '7d': {
        chart: [
          { time: 'Mon', tiktok: 150, instagram: 80, x: 40 },
          { time: 'Tue', tiktok: 230, instagram: 120, x: 60 },
          { time: 'Wed', tiktok: 180, instagram: 250, x: 45 },
          { time: 'Thu', tiktok: 350, instagram: 400, x: 50 },
          { time: 'Fri', tiktok: 450, instagram: 300, x: 80 },
          { time: 'Sat', tiktok: 600, instagram: 450, x: 120 },
          { time: 'Sun', tiktok: 500, instagram: 200, x: 90 },
        ],
        stats: [
          { title: 'Total Engagements', value: '9,452', trend: '+18%', trendUp: true, icon: 'chat_bubble_outline', progress: 82, color: 'bg-[#10B981]' },
          { title: 'Avg Engagement Rate', value: '5.1%', trend: '+0.7%', trendUp: true, icon: 'ssid_chart', progress: 65, color: 'bg-blue-500' },
          { title: 'Approval Rate', value: '95.1%', trend: '+0.5%', trendUp: true, icon: 'check_circle', progress: 95, color: 'bg-purple-500' },
        ],
        platformHealth: [
          { name: 'TikTok', route: '/hub/tiktok', icon: 'music_note', color: 'text-[#EE1D52]', hoverBorder: 'hover:border-[#EE1D52]', stat1Lbl: 'Comments', stat1Val: '3.2k', stat2Lbl: 'Avg Likes', stat2Val: '14.5k' },
          { name: 'Instagram', route: '/hub/instagram', icon: 'photo_camera', color: 'text-[#E1306C]', hoverBorder: 'hover:border-[#E1306C]', stat1Lbl: 'Comments', stat1Val: '2.1k', stat2Lbl: 'Avg Likes', stat2Val: '6.2k' },
          { name: 'X / Twitter', route: '/hub/x', icon: 'close', color: 'text-[#1DA1F2]', hoverBorder: 'hover:border-[#1DA1F2]', statusColor: 'bg-[#F59E0B]', stat1Lbl: 'Replies', stat1Val: '942', stat2Lbl: 'Impressions', stat2Val: '85k' },
        ]
      },
      '30d': {
        chart: [
          { time: 'Week 1', tiktok: 1200, instagram: 800, x: 300 },
          { time: 'Week 2', tiktok: 1800, instagram: 1200, x: 450 },
          { time: 'Week 3', tiktok: 2500, instagram: 1500, x: 600 },
          { time: 'Week 4', tiktok: 2200, instagram: 1800, x: 550 },
        ],
        stats: [
          { title: 'Total Engagements', value: '42,891', trend: '+24%', trendUp: true, icon: 'chat_bubble_outline', progress: 88, color: 'bg-[#10B981]' },
          { title: 'Avg Engagement Rate', value: '4.9%', trend: '+0.2%', trendUp: true, icon: 'ssid_chart', progress: 62, color: 'bg-blue-500' },
          { title: 'Approval Rate', value: '93.8%', trend: '-0.4%', trendUp: false, icon: 'check_circle', progress: 93, color: 'bg-purple-500' },
        ],
        platformHealth: [
          { name: 'TikTok', route: '/hub/tiktok', icon: 'music_note', color: 'text-[#EE1D52]', hoverBorder: 'hover:border-[#EE1D52]', stat1Lbl: 'Comments', stat1Val: '14.5k', stat2Lbl: 'Avg Likes', stat2Val: '68.2k' },
          { name: 'Instagram', route: '/hub/instagram', icon: 'photo_camera', color: 'text-[#E1306C]', hoverBorder: 'hover:border-[#E1306C]', stat1Lbl: 'Comments', stat1Val: '8.4k', stat2Lbl: 'Avg Likes', stat2Val: '24.1k' },
          { name: 'X / Twitter', route: '/hub/x', icon: 'close', color: 'text-[#1DA1F2]', hoverBorder: 'hover:border-[#1DA1F2]', statusColor: 'bg-[#F59E0B]', stat1Lbl: 'Replies', stat1Val: '3.8k', stat2Lbl: 'Impressions', stat2Val: '420k' },
        ]
      }
    };
    return apiFetch(`/dashboard/overview?timeframe=${timeframe}`, {}, fallbacks[timeframe]);
  }
};

export const QueueAPI = {
  getPendingItems: () => apiFetch('/queue/pending', {}, [
    { 
      id: 'q1', platform: 'TikTok', user: '@finance_guru_99', avatar: 'https://picsum.photos/50/50?random=5',
      postContext: "Why 401ks are basically a scam... or are they? Let's break down the math! 📉📈 #finance #investing",
      thumbnail: 'https://picsum.photos/400/600?random=4', riskScore: 15, riskLabel: 'Low Risk'
    },
    { 
      id: 'q2', platform: 'Instagram', user: '@sarah_styles', avatar: 'https://picsum.photos/50/50?random=6',
      postContext: "Just got my first credit card, any tips to not ruin my life? 😅",
      thumbnail: 'https://picsum.photos/400/600?random=7', riskScore: 8, riskLabel: 'Low Risk'
    }
  ]),
  resolveItem: (id: string, action: 'approve' | 'reject' | 'edit', finalComment?: string) => 
    apiFetch(`/queue/${id}/resolve`, {
      method: 'POST',
      body: JSON.stringify({ action, finalComment })
    }, { success: true })
};

export const PersonaAPI = {
  getPersonas: () => apiFetch('/personas', {}, [
    { 
      id: 'p1', name: 'Financial Guru', type: 'Educator', active: true, color: 'text-blue-400', bg: 'bg-blue-400/10',
      coreIdentity: 'You are a high-energy, highly knowledgeable financial educator.',
      toneModifiers: '- Authoritative but approachable\n- Uses concrete data',
      rules: ['Always summarize the core concept.', 'Never give explicit "buy" advice.'],
      temperature: 0.7, files: []
    }
  ]),
  savePersona: (persona: any) => apiFetch(`/personas/${persona.id || 'new'}`, {
    method: persona.id ? 'PUT' : 'POST',
    body: JSON.stringify(persona)
  }, { ...persona, id: persona.id || 'p_new' })
};

export const HubAPI = {
  getStats: (platform: string) => {
    let fallbackData: any = {};
    
    if (platform === 'tiktok') {
      fallbackData = {
        stats: { monitored: '14.2k', posted: '3,842', avgLike: '45.2', conversion: '2.4%' },
        feed: [
          { user: '@user1023', matchedRule: 'FinTok Trend Hijack', time: '12m ago', post: "I literally have $12 to my name until Friday...", reply: "Felt that! 😅 Check out our cash advance feature!" },
          { user: '@crypto_bro', matchedRule: 'Debt Management', time: '45m ago', post: "Just maxed out my 3rd credit card lol", reply: "The debt fatigue is real! Small steps compound faster than you think. 📉" }
        ]
      };
    } else if (platform === 'instagram') {
      fallbackData = {
        stats: { comments: '5.2k', storyReplies: '842', dms: '1.1k', clicks: '8.4k' },
        topContent: [
          { id: 1, img: 'https://picsum.photos/200/250?random=20', likes: '120k' },
          { id: 2, img: 'https://picsum.photos/200/250?random=21', likes: '100k' },
          { id: 3, img: 'https://picsum.photos/200/250?random=22', likes: '80k' },
          { id: 4, img: 'https://picsum.photos/200/250?random=23', likes: '60k' }
        ],
        feed: [
          { user: 'invest_bro', type: 'Comment on Reel', source: 'How to save $10k', msg: 'Is this possible with a 50k salary?', reply: 'Absolutely! It takes discipline but starting with 10% auto-transfers makes it painless.' },
          { user: 'sarah_styles', type: 'Story Reply', source: 'Q&A Tuesday', msg: '🔥 Love this advice', reply: 'Thanks Sarah! Keep crushing your goals! 🚀' }
        ]
      };
    } else if (platform === 'x') {
      fallbackData = {
        stats: { replies: '1,204', keywords: '8.4k', sentiment: 'Positive', quota: '42%' },
        keywords: [
          { term: '"need a loan"', volume: 'High', action: 'Auto-Reply', match: 'I need a small loan to cover rent until my next paycheck drops...' },
          { term: '@MoneyLion support', volume: 'Medium', action: 'Queue Review', match: 'Hey @MoneyLion my card was declined but I have funds??' }
        ],
        drafts: [
          { id: 1, user: '@angry_user_99', msg: "This app is literally stealing my money with these hidden subscription fees.", draft: "We hear your frustration. We aim for 100% transparency. Please DM us your account email so our escalation team can review those charges immediately." },
          { id: 2, user: '@lost_student', msg: "I don't even know how APR works, they didn't teach this in school.", draft: "We got you! APR is basically the total cost of borrowing money over a year, including interest and fees. Check out our latest blog for a simple breakdown." }
        ]
      };
    }

    return apiFetch(`/hubs/${platform}/stats`, {}, fallbackData);
  }
};

export const LibraryAPI = {
  getSnippets: () => apiFetch('/library/snippets', {}, [
    { id: 1, text: "Thanks for reaching out! Please send us a DM with your account email and our support team will investigate this immediately. 🔒", category: 'Support', uses: 1243, avgLikes: 2, tags: ['routing', 'safe'] },
    { id: 2, text: "The 50/30/20 rule is a great starting point: 50% needs, 30% wants, 20% savings. Small steps lead to big wins! 📈", category: 'Education', uses: 890, avgLikes: 45, tags: ['budgeting', 'tips'] },
    { id: 3, text: "Love this! Consistency is key when it comes to building wealth. Keep crushing it 💪", category: 'Engagement', uses: 2105, avgLikes: 12, tags: ['hype', 'general'] },
    { id: 4, text: "Great question! Check out the link in our bio for a full breakdown of how our cash advance feature works with zero hidden fees. 💸", category: 'Lead Gen', uses: 450, avgLikes: 8, tags: ['product', 'link-in-bio'] },
    { id: 5, text: "We apologize for the inconvenience. Our systems are currently undergoing maintenance but should be fully restored shortly. Thank you for your patience! 🙏", category: 'Crisis', uses: 32, avgLikes: 1, tags: ['downtime', 'apology'] }
  ])
};
