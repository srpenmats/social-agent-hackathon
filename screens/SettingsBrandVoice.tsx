import React from 'react';

export default function SettingsBrandVoice() {
  return (
    <div className="max-w-[1600px] mx-auto grid grid-cols-12 gap-8">
      {/* Left Column - Configurations */}
      <div className="col-span-12 lg:col-span-8 space-y-6">
        <div className="flex items-start justify-between">
          <div>
            <h2 className="text-lg font-semibold text-white">Voice Configuration</h2>
            <p className="text-sm text-gray-400 mt-1">Define the core personality and rules for the AI Agent. These settings directly influence the <span className="mono-text text-[#00B894] bg-[#00B894]/10 px-1 rounded text-xs">system_prompt</span>.</p>
          </div>
          <div className="flex items-center gap-2">
            <span className="px-2 py-1 rounded bg-[#1E2538] border border-[#2D3748] text-xs font-mono text-gray-400">model: claude-3.5-sonnet</span>
          </div>
        </div>

        {/* Persona Traits */}
        <div className="bg-[#131828] border border-[#2D3748] rounded-lg overflow-hidden">
          <div className="px-4 py-3 bg-[#1E2538] border-b border-[#2D3748] flex justify-between items-center">
            <div className="flex items-center gap-2">
              <span className="material-symbols-outlined text-[#00B894] text-sm">face</span>
              <h3 className="text-sm font-semibold text-white uppercase tracking-wider">Persona Traits</h3>
            </div>
            <button className="text-gray-400 hover:text-white"><span className="material-symbols-outlined text-sm">edit</span></button>
          </div>
          <div className="p-4 grid grid-cols-2 gap-4">
            <div className="space-y-1">
              <label className="text-xs text-gray-400 font-medium uppercase">Core Identity</label>
              <textarea 
                className="w-full bg-[#0B0F1A] border border-[#2D3748] rounded text-sm text-gray-100 p-3 focus:ring-1 focus:ring-[#00B894] focus:border-[#00B894] mono-text resize-none h-24"
                defaultValue={`Financial guru meets supportive older sibling. Knowledgeable but never condescending. Uses "we" language to build community.`}
              />
            </div>
            <div className="space-y-1">
              <label className="text-xs text-gray-400 font-medium uppercase">Tone Modifiers</label>
              <textarea 
                className="w-full bg-[#0B0F1A] border border-[#2D3748] rounded text-sm text-gray-100 p-3 focus:ring-1 focus:ring-[#00B894] focus:border-[#00B894] mono-text resize-none h-24"
                defaultValue={`- Empathetic\n- Witty (but not cheesy)\n- Direct\n- Optimistic regarding financial futures`}
              />
            </div>
          </div>
        </div>

        {/* Comment Rules */}
        <div className="bg-[#131828] border border-[#2D3748] rounded-lg overflow-hidden">
          <div className="px-4 py-3 bg-[#1E2538] border-b border-[#2D3748] flex justify-between items-center">
            <div className="flex items-center gap-2">
              <span className="material-symbols-outlined text-blue-400 text-sm">gavel</span>
              <h3 className="text-sm font-semibold text-white uppercase tracking-wider">Comment Rules</h3>
            </div>
            <span className="text-xs text-gray-400 mono-text">active_rules: 5</span>
          </div>
          <div className="p-4 space-y-3">
            {[
              { id: '01', text: "Always keep comments under 280 characters unless it's a deep educational dive." },
              { id: '02', text: "Use max 1 emoji per comment. Prefer: 🚀, 🦁, 💸, 📈." },
              { id: '03', text: "Never offer specific investment advice (buy/sell). Stick to education." }
            ].map(rule => (
              <div key={rule.id} className="flex items-center gap-3 p-3 bg-[#0B0F1A] rounded border border-[#2D3748]">
                <span className="text-[#00B894] mono-text text-xs">{rule.id}</span>
                <input className="flex-1 bg-transparent border-none text-sm text-white focus:ring-0 px-0 outline-none" type="text" defaultValue={rule.text} />
                <button className="text-gray-400 hover:text-[#E17055]"><span className="material-symbols-outlined text-sm">close</span></button>
              </div>
            ))}
            <button className="w-full py-2 border border-dashed border-[#2D3748] text-gray-400 text-xs uppercase font-medium hover:border-[#00B894] hover:text-[#00B894] transition-colors rounded">
              + Add Rule
            </button>
          </div>
        </div>

        {/* No-Go Zones */}
        <div className="bg-[#131828] border border-[#2D3748] rounded-lg overflow-hidden">
          <div className="px-4 py-3 bg-[#1E2538] border-b border-[#2D3748] flex justify-between items-center">
            <div className="flex items-center gap-2">
              <span className="material-symbols-outlined text-[#E17055] text-sm">do_not_disturb_on</span>
              <h3 className="text-sm font-semibold text-white uppercase tracking-wider">No-Go Zones</h3>
            </div>
          </div>
          <div className="p-4">
            <textarea 
              className="w-full bg-[#0B0F1A] border border-[#E17055]/30 rounded text-sm text-gray-100 p-3 focus:ring-1 focus:ring-[#E17055] focus:border-[#E17055] mono-text resize-none h-24 placeholder-gray-600 outline-none" 
              placeholder="Enter topics to avoid completely..."
              defaultValue={`Politics, Religion, Competitor bashing, specific stock price predictions, crypto speculation pumps.`}
            />
          </div>
        </div>

        {/* Examples Grid */}
        <div className="grid grid-cols-2 gap-6 pb-8">
          {/* Positive Examples */}
          <div className="bg-[#131828] border border-[#2D3748] rounded-lg overflow-hidden flex flex-col">
            <div className="px-4 py-3 bg-[#1E2538] border-b border-[#2D3748] flex justify-between items-center border-l-4 border-l-[#00B894]">
              <h3 className="text-sm font-semibold text-white uppercase tracking-wider">Positive Examples</h3>
              <span className="bg-[#00B894]/20 text-[#00B894] text-[10px] px-2 py-0.5 rounded font-mono">DO THIS</span>
            </div>
            <div className="p-4 space-y-4 flex-1">
              {[
                { context: 'Budgeting Tips Video', msg: '"This is actually a solid hack! The 50/30/20 rule changed the game for us. Have you tried automating the savings part? 🦁"' },
                { context: 'User complaining about debt', msg: '"Debt fatigue is real. Don\'t be too hard on yourself. Small steps compound faster than you think. We\'re rooting for you! 📈"' }
              ].map((ex, i) => (
                <div key={i} className="p-3 bg-[rgba(0,184,148,0.1)] rounded border border-[#00B894]/30 relative group">
                  <div className="text-[10px] text-[#00B894] font-bold mb-1 uppercase tracking-wide">Context: {ex.context}</div>
                  <p className="text-sm text-gray-200 italic">{ex.msg}</p>
                  <div className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity flex gap-1">
                    <button className="bg-[#00B894] text-white p-1 rounded hover:bg-[#008f72]"><span className="material-symbols-outlined text-[14px]">edit</span></button>
                    <button className="bg-[#E17055] text-white p-1 rounded hover:bg-[#c05a42]"><span className="material-symbols-outlined text-[14px]">delete</span></button>
                  </div>
                </div>
              ))}
              <button className="w-full py-2 border border-dashed border-[#2D3748] text-gray-400 text-xs font-medium hover:border-[#00B894] hover:text-[#00B894] transition-colors rounded">
                + Add Positive Example
              </button>
            </div>
          </div>

          {/* Negative Examples */}
          <div className="bg-[#131828] border border-[#2D3748] rounded-lg overflow-hidden flex flex-col">
            <div className="px-4 py-3 bg-[#1E2538] border-b border-[#2D3748] flex justify-between items-center border-l-4 border-l-[#E17055]">
              <h3 className="text-sm font-semibold text-white uppercase tracking-wider">Negative Examples</h3>
              <span className="bg-[#E17055]/20 text-[#E17055] text-[10px] px-2 py-0.5 rounded font-mono">AVOID THIS</span>
            </div>
            <div className="p-4 space-y-4 flex-1">
              {[
                { context: 'Crypto Crash Video', msg: '"Buy the dip! It\'s going to the moon soon 🚀🚀🚀 #crypto"', reason: 'Financial advice, speculative, too many emojis.' },
                { context: 'Competitor Feature Launch', msg: '"Their app is terrible compared to ours. Switch to MoneyLion."', reason: 'Aggressive competitor bashing, bad sportsmanship.' }
              ].map((ex, i) => (
                <div key={i} className="p-3 bg-[rgba(225,112,85,0.1)] rounded border border-[#E17055]/30 relative group">
                  <div className="text-[10px] text-[#E17055] font-bold mb-1 uppercase tracking-wide">Context: {ex.context}</div>
                  <p className="text-sm text-gray-200 italic">{ex.msg}</p>
                  <div className="mt-2 text-[10px] text-[#E17055] border-t border-[#E17055]/20 pt-1">Reason: {ex.reason}</div>
                  <div className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity flex gap-1">
                    <button className="bg-[#00B894] text-white p-1 rounded hover:bg-[#008f72]"><span className="material-symbols-outlined text-[14px]">edit</span></button>
                    <button className="bg-[#E17055] text-white p-1 rounded hover:bg-[#c05a42]"><span className="material-symbols-outlined text-[14px]">delete</span></button>
                  </div>
                </div>
              ))}
              <button className="w-full py-2 border border-dashed border-[#2D3748] text-gray-400 text-xs font-medium hover:border-[#E17055] hover:text-[#E17055] transition-colors rounded">
                + Add Negative Example
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Right Column - Live Tester */}
      <div className="col-span-12 lg:col-span-4 space-y-6">
        <div className="bg-[#131828] border border-[#2D3748] rounded-lg shadow-2xl overflow-hidden sticky top-0">
          <div className="px-4 py-3 bg-[#1E2538] border-b border-[#2D3748] flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="material-symbols-outlined text-[#00B894] animate-pulse">science</span>
              <h3 className="text-sm font-semibold text-white uppercase tracking-wider">Live Voice Tester</h3>
            </div>
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-[#00B894]"></span>
              <span className="text-[10px] text-gray-400 uppercase">Ready</span>
            </div>
          </div>
          
          <div className="p-5 space-y-6">
            <div className="space-y-2">
              <label className="text-xs font-medium text-gray-400 uppercase flex justify-between">
                Video Context / Transcript
                <span className="text-[10px] text-gray-500">Max 500 chars</span>
              </label>
              <textarea 
                className="w-full bg-[#0B0F1A] border border-[#2D3748] rounded text-sm text-gray-100 p-3 focus:ring-1 focus:ring-[#00B894] focus:border-[#00B894] mono-text h-32 resize-none outline-none placeholder-gray-600" 
                placeholder="Paste video description or transcript here... e.g., 'A creator explains why they stopped buying coffee to save for a house deposit.'"
              ></textarea>
              <div className="flex justify-end pt-1">
                <button className="w-full py-2.5 bg-[#00B894] hover:bg-[#00a383] text-white rounded font-medium text-sm flex items-center justify-center gap-2 transition-colors shadow-lg shadow-[#00B894]/20">
                  <span className="material-symbols-outlined text-[18px]">psychology</span>
                  Generate Test Comment
                </button>
              </div>
            </div>

            <div className="relative flex items-center py-2">
              <div className="flex-grow border-t border-[#2D3748]"></div>
              <span className="flex-shrink-0 mx-4 text-gray-500 text-[10px] uppercase font-bold">Preview Output</span>
              <div className="flex-grow border-t border-[#2D3748]"></div>
            </div>

            <div className="space-y-3">
              {[
                { approach: 'Supportive', score: '92/100', color: 'text-[#00B894]', dots: ['bg-green-500', 'bg-green-500', 'bg-green-500'], msg: '"Small sacrifices add up! ☕️🏠 It\'s not about deprivation, it\'s about prioritization. Love seeing goals turn into reality!"' },
                { approach: 'Witty', score: '78/100', color: 'text-[#FDCB6E]', dots: ['bg-green-500', 'bg-yellow-500', 'bg-green-500'], msg: '"The latte factor strikes again! 😂 Seriously though, house > caffeine. Keep crushing it!"' }
              ].map((res, i) => (
                <div key={i} className="bg-[#0B0F1A] border border-[#2D3748] rounded p-3 relative group hover:border-[#00B894]/50 transition-colors">
                  <div className="flex justify-between items-start mb-2">
                    <span className="text-[10px] bg-[#1E2538] text-gray-400 px-1.5 py-0.5 rounded border border-[#2D3748] mono-text">Approach: {res.approach}</span>
                    <span className={`text-[10px] ${res.color}`}>Score: {res.score}</span>
                  </div>
                  <p className="text-sm text-gray-100">{res.msg}</p>
                  <div className="mt-3 pt-2 border-t border-[#2D3748] flex justify-between items-center opacity-50 group-hover:opacity-100 transition-opacity">
                    <div className="flex gap-1">
                      {res.dots.map((dColor, j) => <span key={j} className={`w-2 h-2 rounded-full ${dColor}`}></span>)}
                    </div>
                    <button className="text-gray-400 hover:text-[#00B894] text-[10px] flex items-center gap-1">
                      <span className="material-symbols-outlined text-[12px]">content_copy</span> Copy
                    </button>
                  </div>
                </div>
              ))}
            </div>

            {/* Drift chart mockup */}
            <div className="bg-[#0B0F1A] rounded p-3 mt-4">
              <h4 className="text-[10px] text-gray-400 uppercase font-bold mb-2">Voice Consistency Drift</h4>
              <div className="flex items-end gap-1 h-16">
                {[40, 60, 80, 90, 95].map((h, i) => (
                   <div key={i} className={`bg-[#00B894] w-1/6 rounded-t opacity-${h === 100 ? '100' : h}`}></div>
                ))}
                <div className="bg-[#1E2538] w-1/6 h-[100%] rounded-t flex items-center justify-center border border-[#00B894] border-dashed">
                  <span className="text-[8px] text-[#00B894]">NOW</span>
                </div>
              </div>
            </div>

          </div>
        </div>
      </div>
    </div>
  );
}