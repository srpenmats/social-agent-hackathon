"""AI Learning Loop — Feedback Loop Service.

Tracks approved/denied comment decisions over time so the AI can learn
from reviewer feedback. Provides stats, trend data, example retrieval,
and prompt-injection helpers for the comment generator.
"""

from __future__ import annotations

import logging
import random
from datetime import datetime, timedelta, timezone
from typing import Any

from db.connection import get_supabase_admin

logger = logging.getLogger(__name__)


class FeedbackLoopService:
    """Service layer for the comment_feedback table."""

    def __init__(self):
        self.db = get_supabase_admin()

    # ------------------------------------------------------------------
    # Stats
    # ------------------------------------------------------------------

    def get_stats(self) -> dict[str, Any]:
        all_rows = (
            self.db.table("comment_feedback")
            .select("id,decision,decided_at")
            .execute()
        )
        rows = all_rows.data or []
        total = len(rows)
        approved = sum(1 for r in rows if r["decision"] == "approved")
        denied = total - approved

        approval_rate = round((approved / total) * 100, 1) if total else 0.0

        # Recent = last 7 days
        cutoff = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
        recent = [r for r in rows if (r.get("decided_at") or "") >= cutoff]
        recent_total = len(recent)
        recent_approved = sum(1 for r in recent if r["decision"] == "approved")
        recent_rate = round((recent_approved / recent_total) * 100, 1) if recent_total else 0.0

        improvement = round(recent_rate - approval_rate, 1) if total else 0.0

        # Active example counts (latest N)
        approved_examples = (
            self.db.table("comment_feedback")
            .select("id")
            .eq("decision", "approved")
            .order("decided_at", desc=True)
            .limit(5)
            .execute()
        )
        denied_examples = (
            self.db.table("comment_feedback")
            .select("id")
            .eq("decision", "denied")
            .order("decided_at", desc=True)
            .limit(3)
            .execute()
        )

        return {
            "total_decisions": total,
            "approved_count": approved,
            "denied_count": denied,
            "approval_rate": approval_rate,
            "recent_approval_rate": recent_rate,
            "improvement": improvement,
            "active_approved_examples": len(approved_examples.data or []),
            "active_denied_examples": len(denied_examples.data or []),
        }

    # ------------------------------------------------------------------
    # Accuracy trend (daily buckets over last 14 days)
    # ------------------------------------------------------------------

    def get_accuracy_trend(self) -> dict[str, Any]:
        cutoff = (datetime.now(timezone.utc) - timedelta(days=14)).isoformat()
        result = (
            self.db.table("comment_feedback")
            .select("decision,decided_at")
            .gte("decided_at", cutoff)
            .order("decided_at")
            .execute()
        )
        rows = result.data or []

        # Bucket by date
        buckets: dict[str, dict[str, int]] = {}
        for r in rows:
            dt_str = r.get("decided_at", "")
            date_key = dt_str[:10] if dt_str else "unknown"
            if date_key == "unknown":
                continue
            if date_key not in buckets:
                buckets[date_key] = {"approved": 0, "denied": 0}
            if r["decision"] == "approved":
                buckets[date_key]["approved"] += 1
            else:
                buckets[date_key]["denied"] += 1

        trend = []
        for date_key in sorted(buckets.keys()):
            b = buckets[date_key]
            total = b["approved"] + b["denied"]
            rate = round((b["approved"] / total) * 100, 1) if total else 0.0
            trend.append({
                "date": date_key,
                "approval_rate": rate,
                "total": total,
                "approved": b["approved"],
                "denied": b["denied"],
            })

        return {"trend": trend}

    # ------------------------------------------------------------------
    # Examples
    # ------------------------------------------------------------------

    def get_examples(self, n_approved: int = 5, n_denied: int = 3) -> dict[str, Any]:
        approved = (
            self.db.table("comment_feedback")
            .select("id,comment_text,original_post_text,original_post_author,platform,approach,risk_score,decided_at")
            .eq("decision", "approved")
            .order("decided_at", desc=True)
            .limit(n_approved)
            .execute()
        )
        denied = (
            self.db.table("comment_feedback")
            .select("id,comment_text,original_post_text,original_post_author,platform,approach,risk_score,decision_reason,decided_at")
            .eq("decision", "denied")
            .order("decided_at", desc=True)
            .limit(n_denied)
            .execute()
        )
        return {
            "approved": approved.data or [],
            "denied": denied.data or [],
        }

    # ------------------------------------------------------------------
    # Prompt context builder (for LLM injection)
    # ------------------------------------------------------------------

    def get_feedback_context_for_prompt(
        self, n_approved: int = 5, n_denied: int = 3
    ) -> str:
        examples = self.get_examples(n_approved, n_denied)
        parts: list[str] = []

        if examples["approved"]:
            parts.append("## Approved Examples (Generate comments like these):")
            for ex in examples["approved"]:
                parts.append(
                    f"- [{ex.get('approach', 'general')}] \"{ex['comment_text']}\""
                )

        if examples["denied"]:
            parts.append("")
            parts.append("## Denied Examples (DO NOT generate comments like these):")
            for ex in examples["denied"]:
                reason = ex.get("decision_reason", "")
                parts.append(
                    f"- \"{ex['comment_text']}\" — Reason: {reason}"
                )

        return "\n".join(parts)

    # ------------------------------------------------------------------
    # Record a single feedback decision
    # ------------------------------------------------------------------

    def record_feedback(
        self,
        comment_text: str,
        decision: str,
        original_post_text: str | None = None,
        original_post_author: str | None = None,
        platform: str = "x",
        decision_reason: str | None = None,
        risk_score: float = 0,
        approach: str | None = None,
        persona: str | None = None,
        decided_by: str = "reviewer",
    ) -> dict[str, Any]:
        row = {
            "comment_text": comment_text,
            "decision": decision,
            "platform": platform,
            "risk_score": risk_score,
            "decided_by": decided_by,
        }
        if original_post_text is not None:
            row["original_post_text"] = original_post_text
        if original_post_author is not None:
            row["original_post_author"] = original_post_author
        if decision_reason is not None:
            row["decision_reason"] = decision_reason
        if approach is not None:
            row["approach"] = approach
        if persona is not None:
            row["persona"] = persona

        result = self.db.table("comment_feedback").insert(row).execute()
        return (result.data or [{}])[0]

    # ------------------------------------------------------------------
    # Seed demo data (~50 approved + ~20 denied over 14 days)
    # ------------------------------------------------------------------

    def seed_demo_data(self) -> dict[str, int]:
        # Clear existing feedback data first
        self.db.table("comment_feedback").delete().gte("id", 0).execute()

        now = datetime.now(timezone.utc)
        inserted_approved = 0
        inserted_denied = 0

        approved_comments = _APPROVED_COMMENTS
        denied_comments = _DENIED_COMMENTS

        # Distribute over 14 days with improving approval rate
        # Week 1 (days 14-8): ~60% approval
        # Week 2 (days 7-1): ~85% approval
        for day_offset in range(14, 0, -1):
            day_dt = now - timedelta(days=day_offset)
            is_week1 = day_offset > 7

            if is_week1:
                # ~60% approval: 3 approved, 2 denied per day
                n_approved = random.randint(2, 4)
                n_denied = random.randint(1, 3)
            else:
                # ~85% approval: 5 approved, 1 denied per day
                n_approved = random.randint(4, 6)
                n_denied = random.randint(0, 1)

            for _ in range(n_approved):
                if not approved_comments:
                    break
                entry = approved_comments.pop(0)
                hour = random.randint(9, 21)
                minute = random.randint(0, 59)
                decided_at = day_dt.replace(hour=hour, minute=minute, second=0).isoformat()
                self.db.table("comment_feedback").insert({
                    "comment_text": entry["comment"],
                    "original_post_text": entry["post"],
                    "original_post_author": entry["author"],
                    "platform": "x",
                    "decision": "approved",
                    "risk_score": entry["risk"],
                    "approach": entry["approach"],
                    "persona": "CashKitty",
                    "decided_at": decided_at,
                    "decided_by": "reviewer",
                }).execute()
                inserted_approved += 1

            for _ in range(n_denied):
                if not denied_comments:
                    break
                entry = denied_comments.pop(0)
                hour = random.randint(9, 21)
                minute = random.randint(0, 59)
                decided_at = day_dt.replace(hour=hour, minute=minute, second=0).isoformat()
                self.db.table("comment_feedback").insert({
                    "comment_text": entry["comment"],
                    "original_post_text": entry["post"],
                    "original_post_author": entry["author"],
                    "platform": "x",
                    "decision": "denied",
                    "decision_reason": entry["reason"],
                    "risk_score": entry["risk"],
                    "approach": entry["approach"],
                    "persona": "CashKitty",
                    "decided_at": decided_at,
                    "decided_by": "reviewer",
                }).execute()
                inserted_denied += 1

        return {"approved": inserted_approved, "denied": inserted_denied}


# ======================================================================
# Realistic seed data
# ======================================================================

_APPROVED_COMMENTS: list[dict[str, Any]] = [
    {"comment": "the way my savings account hits different after payday >> any retail therapy", "post": "Just got paid and already planning my next shopping spree", "author": "@savvyspender_", "approach": "witty", "risk": 8},
    {"comment": "credit score glow-ups are the best glow-ups. just saying.", "post": "6 month transformation update - feeling confident", "author": "@fitjourney22", "approach": "witty", "risk": 12},
    {"comment": "this is the energy i bring to checking my budget every Sunday night", "post": "Sunday reset routine that actually works", "author": "@productivityhub", "approach": "supportive", "risk": 5},
    {"comment": "normalize celebrating when your emergency fund hits 3 months", "post": "What milestone are you most proud of?", "author": "@growthmindset", "approach": "supportive", "risk": 10},
    {"comment": "me explaining compound interest to my friends at brunch", "post": "POV: you're the financial advisor of your friend group", "author": "@personalfinance101", "approach": "witty", "risk": 15},
    {"comment": "budgeting isn't boring, you're just not doing it right", "post": "Why does adulting have to be so boring", "author": "@twentysomething_", "approach": "witty", "risk": 11},
    {"comment": "setting up auto-save was the best decision i made this year", "post": "Best life hack you discovered this year?", "author": "@lifehacks_daily", "approach": "helpful", "risk": 7},
    {"comment": "your future self is gonna thank you for that budget spreadsheet", "post": "Things I wish I started earlier", "author": "@wisdomthread", "approach": "supportive", "risk": 6},
    {"comment": "the 50/30/20 rule changed my whole financial vibe", "post": "Drop a money tip that actually works", "author": "@moneymoves_", "approach": "helpful", "risk": 14},
    {"comment": "when your credit score goes up 50 points and nobody claps for you", "post": "Celebrate your small wins more", "author": "@motivationdaily", "approach": "witty", "risk": 9},
    {"comment": "imagine explaining to your past self that you'd enjoy reading about APY", "post": "Things that would shock your younger self", "author": "@nostalgia_hits", "approach": "witty", "risk": 13},
    {"comment": "tracking expenses is literally a superpower nobody talks about", "post": "Underrated life skills thread", "author": "@skillstack", "approach": "helpful", "risk": 8},
    {"comment": "this is the sign you needed to check your subscriptions today", "post": "Your wallet called, it wants to talk", "author": "@adulting101_", "approach": "helpful", "risk": 10},
    {"comment": "financial literacy should be mandatory in every school fr", "post": "What subject should be added to school curriculums?", "author": "@educationreform", "approach": "supportive", "risk": 16},
    {"comment": "me after canceling 3 subscriptions i forgot about: stonks", "post": "Just saved $200 this month without even trying", "author": "@frugalwins", "approach": "witty", "risk": 7},
    {"comment": "paying yourself first isn't selfish, it's smart", "post": "Self-care tips that actually matter", "author": "@wellnesscheck_", "approach": "supportive", "risk": 9},
    {"comment": "not me opening my banking app 12 times a day like it's instagram", "post": "What app do you check the most?", "author": "@techsurvey_", "approach": "witty", "risk": 11},
    {"comment": "side hustle + auto-savings = unstoppable combo", "post": "How I built multiple income streams", "author": "@hustleculture", "approach": "helpful", "risk": 14},
    {"comment": "round-ups are literally free money for your savings (well almost)", "post": "What's the easiest way to save without thinking?", "author": "@lazysaver", "approach": "helpful", "risk": 12},
    {"comment": "spending less doesn't mean living less, it means choosing better", "post": "Minimalism isn't about deprivation", "author": "@minimalfinance", "approach": "supportive", "risk": 8},
    {"comment": "cash back rewards are my love language", "post": "Drop your love language in the comments", "author": "@trendingtweets_", "approach": "witty", "risk": 10},
    {"comment": "my budget after meal prepping vs eating out every day is chef's kiss", "post": "Meal prep Sunday hits different", "author": "@mealprep_king", "approach": "witty", "risk": 6},
    {"comment": "starting an emergency fund feels impossible until you start. then it's addicting.", "post": "What financial advice would you give your 20-year-old self?", "author": "@retroadvice_", "approach": "supportive", "risk": 9},
    {"comment": "the glow-up nobody talks about: going from overdraft to positive balance", "post": "Underrated glow-ups", "author": "@glowupszn", "approach": "witty", "risk": 11},
    {"comment": "automatic savings transfers are basically paying your future self", "post": "Set it and forget it strategies", "author": "@passiveincome_", "approach": "helpful", "risk": 7},
    {"comment": "okay but can we normalize talking about money with friends?", "post": "Topics that are still taboo for no reason", "author": "@realtalk_thread", "approach": "supportive", "risk": 13},
    {"comment": "zero-based budgeting sounds intense but it literally just means giving every dollar a job", "post": "Financial terms that sound scarier than they are", "author": "@financejargon", "approach": "helpful", "risk": 15},
    {"comment": "my savings account watching me resist that impulse purchase: proud parent energy", "post": "The hardest part of adulting is...", "author": "@adultinghard", "approach": "witty", "risk": 8},
    {"comment": "if you're not automating your finances yet, this is your wake up call", "post": "Automation tips for busy people", "author": "@productivitypro_", "approach": "helpful", "risk": 12},
    {"comment": "credit cards aren't the enemy. not paying them off is.", "post": "Hot takes about personal finance", "author": "@hottakes_fin", "approach": "helpful", "risk": 18},
    {"comment": "just vibes and a fully-funded roth contribution", "post": "What does your ideal weekend look like?", "author": "@weekendvibes_", "approach": "witty", "risk": 10},
    {"comment": "shoutout to everyone who made a budget today. you're already ahead.", "post": "Monday motivation thread", "author": "@mondaymotivation", "approach": "supportive", "risk": 5},
    {"comment": "the best investment you can make is in your own financial education", "post": "Best investments in your 20s?", "author": "@youngmoney_", "approach": "supportive", "risk": 14},
    {"comment": "i used to think budgets were restrictive until i realized they're actually freeing", "post": "Perspectives that changed your life", "author": "@perspectiveshift", "approach": "supportive", "risk": 7},
    {"comment": "direct deposit day + auto-savings = my money never even touches my hands", "post": "The key to saving money is making it invisible", "author": "@invisiblesaver", "approach": "helpful", "risk": 9},
    {"comment": "being financially responsible is the ultimate flex", "post": "What's the biggest flex in 2026?", "author": "@culturewatch_", "approach": "witty", "risk": 11},
    {"comment": "when your net worth calculator finally shows green: main character moment", "post": "Main character energy", "author": "@maincharacter_", "approach": "witty", "risk": 10},
    {"comment": "pro tip: review your bank statements monthly. you'll be surprised what you find.", "post": "Pro tips that changed your finances", "author": "@protips_daily", "approach": "helpful", "risk": 8},
    {"comment": "latte factor is real but so is the joy factor, find your balance", "post": "The latte factor debate is tired", "author": "@coffeeandcash", "approach": "supportive", "risk": 12},
    {"comment": "new year resolution check: how's that savings goal going?", "post": "February check-in on your 2026 goals", "author": "@goalcheck_", "approach": "supportive", "risk": 6},
    {"comment": "building wealth is a marathon not a sprint and that's perfectly okay", "post": "Patience is underrated in personal finance", "author": "@slowwealth", "approach": "supportive", "risk": 7},
    {"comment": "high-yield savings accounts are the unsung heroes of personal finance", "post": "What financial product do you wish you knew about sooner?", "author": "@finproducttips", "approach": "helpful", "risk": 13},
    {"comment": "mood: checking my savings balance and actually smiling", "post": "Things that make you unexpectedly happy", "author": "@happymoments_", "approach": "witty", "risk": 5},
    {"comment": "the secret to financial wellness? consistency over intensity.", "post": "Wellness tips that apply to everything", "author": "@holisticwellness", "approach": "supportive", "risk": 9},
    {"comment": "nobody talks about how satisfying it is to hit your first $1k saved", "post": "Milestones worth celebrating", "author": "@milestonemoment", "approach": "supportive", "risk": 8},
    {"comment": "free resources for learning about money management exist and they're fire", "post": "Best free resources you've found online?", "author": "@freeresources_", "approach": "helpful", "risk": 10},
    {"comment": "the best budget is the one you'll actually stick to", "post": "Why do most budgets fail?", "author": "@budgetfails", "approach": "helpful", "risk": 7},
    {"comment": "watching my credit score climb every month is my new hobby", "post": "Pick up a new hobby they said", "author": "@hobbyhunter_", "approach": "witty", "risk": 11},
    {"comment": "money anxiety is real. starting small helps more than you think.", "post": "Let's talk about financial anxiety", "author": "@mentalhealth_fin", "approach": "supportive", "risk": 14},
    {"comment": "every payday is a chance to do better than last time", "post": "Payday rituals that work", "author": "@paydayroutine", "approach": "supportive", "risk": 6},
]

_DENIED_COMMENTS: list[dict[str, Any]] = [
    {"comment": "use MoneyLion and you're guaranteed to save at least $500 this month!", "post": "Best savings apps?", "author": "@appreviews_", "approach": "helpful", "risk": 82, "reason": "Financial guarantee claim — regulatory risk"},
    {"comment": "forget Chime and Dave, MoneyLion is the only app that actually works", "post": "Which fintech app should I use?", "author": "@fintechcompare", "approach": "witty", "risk": 75, "reason": "Competitor disparagement — names specific competitors"},
    {"comment": "invest in crypto NOW before it's too late, you won't regret it", "post": "Is crypto still worth it in 2026?", "author": "@cryptodaily_", "approach": "helpful", "risk": 90, "reason": "Investment advice with urgency — regulatory violation"},
    {"comment": "if you're not using MoneyLion's credit builder you're literally losing money every day", "post": "Credit building tips thread", "author": "@creditboost_", "approach": "helpful", "risk": 78, "reason": "Implied financial loss claim — misleading"},
    {"comment": "other banks are scamming you with hidden fees, switch to something better today", "post": "Why I left my traditional bank", "author": "@bankingrevolution", "approach": "witty", "risk": 85, "reason": "Defamatory claims about competitors — legal risk"},
    {"comment": "your credit score will jump 100 points if you follow this one trick", "post": "Credit score improvement hacks", "author": "@credithacks_", "approach": "helpful", "risk": 88, "reason": "Specific financial outcome guarantee — misleading"},
    {"comment": "DM me for a free financial plan that will change your life", "post": "Who needs a financial advisor?", "author": "@financialplanning_", "approach": "helpful", "risk": 92, "reason": "Unauthorized financial advisory solicitation"},
    {"comment": "lol imagine still being poor in 2026, couldn't be me", "post": "Hot takes for the new year", "author": "@hottakes2026", "approach": "witty", "risk": 80, "reason": "Insensitive/classist language — brand safety risk"},
    {"comment": "banks are the real criminals in this economy tbh", "post": "The economy is broken", "author": "@economywatcher", "approach": "witty", "risk": 72, "reason": "Anti-banking sentiment — conflicts with fintech brand"},
    {"comment": "the government doesn't want you to know this one savings hack", "post": "Financial secrets they don't teach you", "author": "@hiddenmoney_", "approach": "helpful", "risk": 76, "reason": "Conspiracy framing — erodes trust and credibility"},
    {"comment": "put all your money in one stock and watch it grow, trust me", "post": "How to start investing with $100", "author": "@investortips_", "approach": "helpful", "risk": 95, "reason": "Reckless investment advice — major regulatory risk"},
    {"comment": "traditional savings accounts are a complete scam, change my mind", "post": "Is saving even worth it anymore?", "author": "@financedebate", "approach": "witty", "risk": 70, "reason": "Product disparagement — undermines financial products"},
    {"comment": "MoneyLion will approve anyone for a loan, no questions asked", "post": "Where can I get a personal loan quickly?", "author": "@loanhelp_", "approach": "helpful", "risk": 91, "reason": "False lending claims — serious regulatory violation"},
    {"comment": "stop paying taxes legally with this one weird trick", "post": "Tax season tips and tricks", "author": "@taxseason2026", "approach": "helpful", "risk": 94, "reason": "Tax evasion implication — legal and regulatory risk"},
    {"comment": "your boss is exploiting you, quit your job and start trading", "post": "Is the 9-5 dead?", "author": "@workculture_", "approach": "witty", "risk": 79, "reason": "Irresponsible career/financial advice — brand risk"},
    {"comment": "i made $10k last month doing nothing, ask me how", "post": "Passive income ideas that work", "author": "@passiveincomeguru", "approach": "helpful", "risk": 88, "reason": "Unrealistic income claims — spam/scam pattern"},
    {"comment": "forget about retirement planning, YOLO your money while you're young", "post": "Do millennials need retirement plans?", "author": "@millennialmoney_", "approach": "witty", "risk": 74, "reason": "Anti-financial-planning message — contradicts brand mission"},
    {"comment": "MoneyLion's interest rates are way better than any bank, period", "post": "Best interest rates right now", "author": "@ratewatch_", "approach": "helpful", "risk": 77, "reason": "Unsubstantiated rate comparison — compliance risk"},
    {"comment": "boomers ruined the economy and now we have to fix it lmao", "post": "Generational wealth gap discussion", "author": "@genwealthgap", "approach": "witty", "risk": 71, "reason": "Generational divisiveness — brand safety risk"},
    {"comment": "this financial advisor is trash, don't listen to anything they say", "post": "Is hiring a financial advisor worth it?", "author": "@advisorreview_", "approach": "witty", "risk": 73, "reason": "Personal attack / defamatory — professional liability"},
]
