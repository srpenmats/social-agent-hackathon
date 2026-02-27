#!/usr/bin/env node

const { program } = require('commander');
const axios = require('axios');

const BEARER_TOKEN = process.env.TWITTER_BEARER_TOKEN;
const BASE_URL = 'https://api.twitter.com/2';

if (!BEARER_TOKEN) {
  console.error('Error: TWITTER_BEARER_TOKEN environment variable not set');
  process.exit(1);
}

const client = axios.create({
  baseURL: BASE_URL,
  headers: {
    'Authorization': `Bearer ${BEARER_TOKEN}`,
    'Content-Type': 'application/json'
  }
});

// Helper: Extract tweet ID from URL or return as-is
function getTweetId(input) {
  const match = input.match(/status\/(\d+)/);
  return match ? match[1] : input;
}

// Helper: Extract username from handle
function getUsername(handle) {
  return handle.replace('@', '');
}

// Command: search
program
  .command('search <query>')
  .option('-n, --count <number>', 'Number of results', '10')
  .option('--json', 'Output as JSON')
  .option('--recent', 'Recent tweets only')
  .option('--popular', 'Popular tweets only')
  .action(async (query, options) => {
    try {
      const params = {
        query: query + ' -is:retweet lang:en',
        max_results: Math.min(parseInt(options.count), 100),
        'tweet.fields': 'created_at,public_metrics,author_id,conversation_id,text',
        'expansions': 'author_id',
        'user.fields': 'username,name,public_metrics,verified'
      };

      const response = await client.get('/tweets/search/recent', { params });
      
      const tweets = response.data.data || [];
      const users = {};
      if (response.data.includes?.users) {
        response.data.includes.users.forEach(u => users[u.id] = u);
      }

      const results = tweets.map(tweet => {
        const author = users[tweet.author_id] || {};
        const metrics = tweet.public_metrics || {};
        return {
          id: tweet.id,
          text: tweet.text,
          author_username: author.username || 'unknown',
          author_name: author.name || 'Unknown',
          author_verified: author.verified || false,
          author_followers: author.public_metrics?.followers_count || 0,
          likes: metrics.like_count || 0,
          retweets: metrics.retweet_count || 0,
          replies: metrics.reply_count || 0,
          quotes: metrics.quote_count || 0,
          bookmarks: metrics.bookmark_count || 0,
          impressions: metrics.impression_count || 0,
          created_at: tweet.created_at,
          url: `https://twitter.com/${author.username}/status/${tweet.id}`
        };
      });

      if (options.json) {
        console.log(JSON.stringify(results, null, 2));
      } else {
        results.forEach(r => {
          console.log(`\n${r.author_name} (@${r.author_username})`);
          console.log(`${r.text}`);
          console.log(`💬 ${r.replies} 🔁 ${r.retweets} ❤️ ${r.likes} 📊 ${r.impressions}`);
          console.log(`🔗 ${r.url}`);
        });
      }
    } catch (error) {
      console.error('Error:', error.response?.data || error.message);
      process.exit(1);
    }
  });

// Command: read (get single tweet)
program
  .command('read <tweet>')
  .option('--json', 'Output as JSON')
  .action(async (tweet, options) => {
    try {
      const tweetId = getTweetId(tweet);
      const params = {
        'tweet.fields': 'created_at,public_metrics,author_id,conversation_id,text,referenced_tweets',
        'expansions': 'author_id',
        'user.fields': 'username,name,public_metrics,verified'
      };

      const response = await client.get(`/tweets/${tweetId}`, { params });
      
      const tweetData = response.data.data;
      const author = response.data.includes?.users?.[0] || {};
      const metrics = tweetData.public_metrics || {};

      const result = {
        id: tweetData.id,
        text: tweetData.text,
        author_username: author.username,
        author_name: author.name,
        author_verified: author.verified || false,
        likes: metrics.like_count || 0,
        retweets: metrics.retweet_count || 0,
        replies: metrics.reply_count || 0,
        quotes: metrics.quote_count || 0,
        bookmarks: metrics.bookmark_count || 0,
        impressions: metrics.impression_count || 0,
        created_at: tweetData.created_at,
        url: `https://twitter.com/${author.username}/status/${tweetData.id}`
      };

      if (options.json) {
        console.log(JSON.stringify(result, null, 2));
      } else {
        console.log(`\n${result.author_name} (@${result.author_username})`);
        console.log(`${result.text}`);
        console.log(`💬 ${result.replies} 🔁 ${result.retweets} ❤️ ${result.likes}`);
        console.log(`💾 ${result.bookmarks} 💬 ${result.quotes} 📊 ${result.impressions}`);
        console.log(`🔗 ${result.url}`);
      }
    } catch (error) {
      console.error('Error:', error.response?.data || error.message);
      process.exit(1);
    }
  });

// Command: reply (post reply - requires OAuth 1.0a)
program
  .command('reply <tweet> <text>')
  .option('--json', 'Output as JSON')
  .action(async (tweet, text, options) => {
    try {
      const tweetId = getTweetId(tweet);
      
      // Note: This requires OAuth 1.0a or OAuth 2.0 with write scope
      // Bearer token alone won't work for posting
      const response = await client.post('/tweets', {
        text: text,
        reply: {
          in_reply_to_tweet_id: tweetId
        }
      });

      const result = {
        id: response.data.data.id,
        text: response.data.data.text,
        url: `https://twitter.com/i/status/${response.data.data.id}`
      };

      if (options.json) {
        console.log(JSON.stringify(result, null, 2));
      } else {
        console.log('✅ Reply posted successfully!');
        console.log(`🔗 ${result.url}`);
      }
    } catch (error) {
      console.error('Error:', error.response?.data || error.message);
      console.error('\nNote: Posting requires OAuth 2.0 with write scope, not just bearer token.');
      process.exit(1);
    }
  });

// Command: tweet (post new tweet)
program
  .command('tweet <text>')
  .option('--json', 'Output as JSON')
  .action(async (text, options) => {
    try {
      const response = await client.post('/tweets', {
        text: text
      });

      const result = {
        id: response.data.data.id,
        text: response.data.data.text,
        url: `https://twitter.com/i/status/${response.data.data.id}`
      };

      if (options.json) {
        console.log(JSON.stringify(result, null, 2));
      } else {
        console.log('✅ Tweet posted successfully!');
        console.log(`🔗 ${result.url}`);
      }
    } catch (error) {
      console.error('Error:', error.response?.data || error.message);
      console.error('\nNote: Posting requires OAuth 2.0 with write scope, not just bearer token.');
      process.exit(1);
    }
  });

// Command: auth-check
program
  .command('auth-check')
  .action(async () => {
    try {
      // Try to get user info to verify token
      const response = await client.get('/users/me');
      console.log('✅ Authentication successful!');
      console.log(`Authenticated as: @${response.data.data.username}`);
    } catch (error) {
      console.error('❌ Authentication failed');
      console.error('Error:', error.response?.data || error.message);
      process.exit(1);
    }
  });

program.parse(process.argv);
