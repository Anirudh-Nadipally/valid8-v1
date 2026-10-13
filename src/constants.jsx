import React from 'react';
import { Briefcase, Cpu, Search, Flame, Scale } from 'lucide-react';

export const PERSONAS = {
    vc: {
        id: 'vc',
        name: 'The Ruthless VC',
        role: 'Partner at YC',
        icon: <Briefcase className="w-5 h-5" />,
        color: 'text-rose-600',
        bgColor: 'bg-rose-100',
        gradient: 'from-rose-500 to-red-600',
        description: " cares only about 100x returns, moats, and exit strategy.",
        promptContext: "You are a 'Ruthless VC' persona, a Partner at YC. You only care about 100x returns, massive market size, and unassailable moats. Be harsh, direct, and slightly arrogant. Focus on scalability and exit strategy."
    },
    bootstrapper: {
        id: 'bootstrapper',
        name: 'The Indie Hacker',
        role: '$10M ARR Bootstrapper',
        icon: <Cpu className="w-5 h-5" />,
        color: 'text-emerald-600',
        bgColor: 'bg-emerald-100',
        gradient: 'from-emerald-500 to-teal-600',
        description: "focuses on day-one revenue, margins, and simplicity.",
        promptContext: "You are a 'Pragmatic Bootstrapper' persona. You care about profitability, unit economics, and getting the first paying customer NOW. Be skeptical of 'big visions' and focus on day 1 revenue, margins, and simple execution."
    },
    researcher: {
        id: 'researcher',
        name: 'The Mom Test',
        role: 'User Research Expert',
        icon: <Search className="w-5 h-5" />,
        color: 'text-amber-600',
        bgColor: 'bg-amber-100',
        gradient: 'from-amber-500 to-orange-600',
        description: "ignores the solution to obsess over the actual user problem.",
        promptContext: "You are a 'User Research Expert' persona using 'The Mom Test'. You don't care about the solution; you care about the PROBLEM. Be inquisitive, skeptical of assumptions, and relentlessly focus on whether the user's pain is real, validated, and frequent."
    },
    roaster: {
        id: 'roaster',
        name: 'Silicon Valley Satirist',
        role: 'Chief Hater',
        icon: <Flame className="w-5 h-5" />,
        color: 'text-purple-600',
        bgColor: 'bg-purple-100',
        gradient: 'from-purple-500 to-indigo-600',
        description: "will destroy your ego for viral engagement.",
        promptContext: "You are a 'Silicon Valley Satirist' persona. Roast this idea mercilessly. Use tech slang (skibidi, rizz, pivot hell, vaporware). Be funny, over-the-top, but secretly hide some brutal truth in your roast."
    },
    legal: {
        id: 'legal',
        name: 'The Legal Eagle',
        role: 'IP & Startup Counsel',
        icon: <Scale className="w-5 h-5" />,
        color: 'text-slate-700',
        bgColor: 'bg-slate-200',
        gradient: 'from-slate-600 to-slate-800',
        description: "identifies regulatory risks, IP issues, and compliance pitfalls.",
        promptContext: "You are a 'Startup Lawyer' persona. You are risk-averse, detail-oriented, and focused on compliance. Look for IP infringement potential, GDPR/Data privacy issues, co-founder equity traps, and highly regulated industry red flags (Fintech/Medtech/AI)."
    }
};

export const DEMO_ANALYSIS = {
    // Scores and trace below are real output of the rules engine on the demo idea (vc_focused weights)
    scores: {"problem": 95, "solution": 85, "market": 100, "moat": 85, "feasibility": 58},
    overallScore: 84,
    scoreTrace: {"finalScore": 84.2, "grade": "Strong", "rulesVersion": "1.0.0", "weightProfile": "vc_focused", "validation": "passed", "dimensions": [{"key": "problem_clarity", "label": "Problem Clarity", "score": 95, "weight": 0.1, "weighted": 9.5, "rules": [{"id": "PC-003", "points": 20, "reason": "Contains pain keyword: lose"}, {"id": "PC-004", "points": 15, "reason": "Competitive awareness shown"}, {"id": "PC-005", "points": 10, "reason": "Problem directly extracted"}]}, {"key": "solution_feasibility", "label": "Solution Feasibility", "score": 85, "weight": 0.1, "weighted": 8.5, "rules": [{"id": "SF-004", "points": 15, "reason": "At prototype stage"}, {"id": "SF-006", "points": 20, "reason": "Has actual users"}]}, {"key": "market_size_potential", "label": "Market Size Potential", "score": 100, "weight": 0.3, "weighted": 30.0, "rules": [{"id": "MS-001", "points": 30, "reason": "Global market target"}]}, {"key": "competitive_landscape", "label": "Competitive Landscape", "score": 85, "weight": 0.2, "weighted": 17.0, "rules": [{"id": "CL-001", "points": 20, "reason": "Competitors identified: Notion, ChatGPT"}, {"id": "CL-003", "points": 15, "reason": "Emerging industry: ai_ml"}]}, {"key": "business_model_viability", "label": "Business Model Viability", "score": 58, "weight": 0.15, "weighted": 8.7, "rules": [{"id": "BM-006", "points": 8, "reason": "Freemium consumer model"}]}, {"key": "team_readiness", "label": "Team Readiness", "score": 55, "weight": 0.1, "weighted": 5.5, "rules": [{"id": "TR-003", "points": 5, "reason": "Solo founder"}]}, {"key": "data_completeness", "label": "Data Completeness", "score": 100, "weight": 0.05, "weighted": 5.0, "rules": [{"id": "DC-001", "points": 30, "reason": "All required fields populated"}, {"id": "DC-002", "points": 25, "reason": "High extraction confidence"}, {"id": "DC-006", "points": 8, "reason": "Form-based input"}, {"id": "DC-008", "points": 15, "reason": "No fields inferred"}, {"id": "DC-009", "points": 10, "reason": "Optional context provided (4/4)"}]}]},
    verdict: "Strong on paper. Now prove someone pays before you build more.",
    strengths: ["Great UX potential", "Low initial cost", "Viral loop possibility"],
    weaknesses: ["Google can build this in a weekend", "No clear monetization", "Market is fragmented"],
    competitors: [
        { name: "Google", type: "Direct", reason: "They own the data" },
        { name: "Notion", type: "Indirect", reason: "Solves the workflow differently" }
    ],
    leanCanvas: {
        problemSummary: "People forget their startup ideas.",
        solutionSummary: "A centralized validation dashboard.",
        metrics: "Weekly Active Users, Ideas Validated",
        channels: "Twitter, Product Hunt",
        revenue: "Freemium SaaS",
        costs: "Hosting, API Credits"
    },
    goToMarket: {
        firstCustomers: [
            { persona: "Indie Hackers on Twitter", details: "Specifically, those who publicly share their 'build in public' journey and are looking for new-fast tools." },
            { persona: "Product Managers at Startups", details: "PMs at 10-50 person companies who are frustrated with bloated 'innovation' software." },
            { persona: "CS Students in Hackathons", details: "Students who need to quickly validate an idea over a weekend to win a prize." }
        ],
        marketingHooks: [
            { hook: "Stop building. Start validating.", details: "Your next idea, roasted by a VC in 30 seconds." },
            { hook: "Is your idea brilliant... or just a fever dream?", details: "Upload your pitch deck and find out before you write a line of code." },
            { hook: "Turn your 'what if' into a 'what's next'.", details: "Go from idea to go-to-market plan instantly." }
        ],
        experiments: [
            { title: "Landing Page Test", action: "Create a waitlist explaining the value prop.", metric: "20% conversion rate" },
            { title: "Concierge MVP", action: "Manually validate 10 ideas for friends.", metric: "NPS > 50" },
            { title: "Cold Outreach", action: "DM 50 founders on Twitter.", metric: "5 demos booked" }
        ]
    },
    pivotSuggestion: "Pivot to a B2B enterprise innovation management platform."
};
