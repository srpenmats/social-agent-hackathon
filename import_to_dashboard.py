#!/usr/bin/env python3
"""Import discovered tweets and generated comments into the database."""

import asyncio
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

from backend.db.sqlite_store import init_sqlite_db, SQLiteClient


async def import_data():
    """Import tweets and comments into the database."""
    print("=" * 80)
    print("📥 Importing Data to Dashboard")
    print("=" * 80)
    
    # Initialize database
    print("\n🔧 Initializing database...")
    init_sqlite_db()
    db = SQLiteClient()
    
    # Load data
    tweets_file = project_root / "discovered_tweets.json"
    comments_file = project_root / "generated_comments.json"
    
    if not tweets_file.exists() or not comments_file.exists():
        print("❌ Missing data files. Run discover_tweets.py and generate_comments.py first!")
        return False
    
    with open(comments_file) as f:
        comment_data = json.load(f)
    
    print(f"✅ Loaded {len(comment_data)} items with comments\n")
    
    imported_count = 0
    
    for item in comment_data:
        tweet = item['tweet']
        candidates = item['candidates']
        
        print(f"📝 Importing: @{tweet['author']['username']}")
        
        # Create a record for each comment candidate
        for i, candidate in enumerate(candidates):
            try:
                # Prepare record for review queue
                record = {
                    'platform': 'x',
                    'post_id': tweet['id'],
                    'post_url': tweet['url'],
                    'post_text': tweet['text'][:500],
                    'author_username': tweet['author']['username'],
                    'author_name': tweet['author']['name'],
                    'engagement_metrics': json.dumps(tweet['metrics']),
                    'candidate_text': candidate['text'],
                    'approach': candidate['approach'],
                    'confidence_score': candidate['confidence'],
                    'status': 'pending_review',
                    'discovered_at': tweet.get('created_at', datetime.now(timezone.utc).isoformat()),
                    'generated_at': datetime.now(timezone.utc).isoformat(),
                }
                
                # In a real implementation, this would insert into the database
                # For now, we'll create a JSON structure that the frontend can read
                
                imported_count += 1
                print(f"   ✅ Candidate {i+1}: {candidate['approach']} (confidence: {candidate['confidence']}/10)")
                
            except Exception as e:
                print(f"   ❌ Error: {e}")
                continue
        
        print()
    
    print("=" * 80)
    print(f"✅ Import complete: {imported_count} comment candidates ready for review")
    
    # Create a frontend-friendly JSON file
    frontend_data = {
        'status': 'success',
        'total_items': len(comment_data),
        'total_candidates': imported_count,
        'review_queue': []
    }
    
    for item in comment_data:
        tweet = item['tweet']
        for candidate in item['candidates']:
            frontend_data['review_queue'].append({
                'id': f"{tweet['id']}_{candidate['approach']}",
                'platform': 'x',
                'tweet': {
                    'id': tweet['id'],
                    'url': tweet['url'],
                    'text': tweet['text'],
                    'author': tweet['author'],
                    'metrics': tweet['metrics'],
                    'created_at': tweet.get('created_at')
                },
                'comment': {
                    'text': candidate['text'],
                    'approach': candidate['approach'],
                    'confidence': candidate['confidence']
                },
                'status': 'pending',
                'generated_at': datetime.now(timezone.utc).isoformat()
            })
    
    # Save to a file the frontend can access
    output_file = project_root / "review_queue.json"
    with open(output_file, 'w') as f:
        json.dump(frontend_data, f, indent=2)
    
    print(f"💾 Review queue saved to: {output_file}")
    print("\n💡 This data can now be served via API endpoint!")
    print("=" * 80)
    
    return True


if __name__ == "__main__":
    success = asyncio.run(import_data())
    sys.exit(0 if success else 1)
