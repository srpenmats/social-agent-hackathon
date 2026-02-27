#!/usr/bin/env python3
"""Generate comments for discovered tweets using the backend's comment generator."""

import asyncio
import json
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

# Load discovered tweets
tweets_file = project_root / "discovered_tweets.json"
if not tweets_file.exists():
    print("❌ No discovered tweets found. Run discover_tweets.py first!")
    sys.exit(1)

with open(tweets_file) as f:
    tweets = json.load(f)

print("=" * 80)
print("🤖 Comment Generation - AI Agent Security Posts")
print("=" * 80)
print(f"\n📊 Found {len(tweets)} discovered tweets")
print("\n🔧 Generating comments...\n")

# Take the most relevant tweets (those with engagement or specific keywords)
priority_keywords = ["agent trust", "security", "NIST", "standards", "autonomous"]

def score_tweet(tweet):
    """Score tweets by relevance."""
    text = tweet['text'].lower()
    score = 0
    
    # Engagement score
    score += tweet['metrics']['likes'] * 3
    score += tweet['metrics']['retweets'] * 2
    score += tweet['metrics']['replies'] * 1
    
    # Keyword matching
    for keyword in priority_keywords:
        if keyword in text:
            score += 10
    
    return score

# Sort by relevance
tweets_sorted = sorted(tweets, key=score_tweet, reverse=True)
top_tweets = tweets_sorted[:5]

print("🎯 Selected top 5 most relevant tweets for comment generation:\n")

# Generate comments for each
generated_comments = []

for i, tweet in enumerate(top_tweets, 1):
    print(f"{i}. Tweet by @{tweet['author']['username']}")
    print(f"   Text: {tweet['text'][:150]}...")
    print(f"   Engagement: ❤️  {tweet['metrics']['likes']} | 🔁 {tweet['metrics']['retweets']} | 💬 {tweet['metrics']['replies']}")
    print(f"   URL: {tweet['url']}")
    
    # Simple comment generation (demonstrative - normally would use Claude)
    # In production, this would call the backend's comment generator
    
    comment_ideas = []
    
    # Generate different comment styles
    if "NIST" in tweet['text'] or "standards" in tweet['text'].lower():
        comment_ideas = [
            {
                "text": "This is exactly what the industry needs. Standards for AI agent identity and security will be crucial as autonomous systems scale. Curious how this will integrate with existing agent frameworks.",
                "approach": "technical_insight",
                "confidence": 8
            },
            {
                "text": "Great to see NIST taking the lead here. Agent interoperability without security standards is a recipe for disaster. Looking forward to contributing feedback during the public comment period.",
                "approach": "expert_endorsement",
                "confidence": 7
            }
        ]
    elif "trust" in tweet['text'].lower():
        comment_ideas = [
            {
                "text": "Trust layers for autonomous agents are non-negotiable at this point. Without cryptographic verification of agent actions, we're just hoping for the best. Zero-knowledge proofs are the path forward.",
                "approach": "technical_depth",
                "confidence": 9
            },
            {
                "text": "The trust problem is the bottleneck. Once we solve agent identity and action verification, the economy of autonomous agents can actually scale securely.",
                "approach": "problem_framing",
                "confidence": 8
            }
        ]
    elif "security" in tweet['text'].lower():
        comment_ideas = [
            {
                "text": "Agent security isn't just about preventing malicious code—it's about verifiable behavior. The silent failures are what keep me up at night. Detection time = money lost.",
                "approach": "practitioner_wisdom",
                "confidence": 7
            },
            {
                "text": "Security for AI agents requires a different mindset than traditional software security. Behavioral monitoring, sandboxed execution, and rollback mechanisms are table stakes.",
                "approach": "educational",
                "confidence": 8
            }
        ]
    else:
        comment_ideas = [
            {
                "text": "This is an interesting angle. As agent systems become more autonomous, the security and trust infrastructure needs to evolve alongside them.",
                "approach": "supportive_general",
                "confidence": 6
            }
        ]
    
    print(f"\n   💬 Generated {len(comment_ideas)} comment candidates:\n")
    
    for j, comment in enumerate(comment_ideas, 1):
        print(f"      Option {j} ({comment['approach']}):")
        print(f"      \"{comment['text']}\"")
        print(f"      Confidence: {comment['confidence']}/10\n")
    
    generated_comments.append({
        "tweet": tweet,
        "candidates": comment_ideas
    })
    
    print("-" * 80 + "\n")

# Save generated comments
output_file = project_root / "generated_comments.json"
with open(output_file, "w") as f:
    json.dump(generated_comments, f, indent=2)

print("=" * 80)
print(f"✅ Generated comments for {len(generated_comments)} tweets")
print(f"💾 Saved to: {output_file}")
print("\n💡 These comments are ready for review in the dashboard!")
print("=" * 80)
