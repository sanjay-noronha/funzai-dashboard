# Funza Academy — Weekly Shorts Insights Protocol

## When to run this
Every time Sanjay downloads a fresh Shorts Analytics Excel from YouTube Studio.
Ask him: "Which Excel file should I use?" — it lives in YouTubeAnalytics/shorts/.

## Step 1 — Read before touching data
Before loading the Excel, read:
1. `content_pipeline.md` — official category codes per video (S-numbers)
2. `script_performance_log.md` — known patterns already identified

## Step 2 — Load and classify the Excel
File path pattern: `YouTubeAnalytics/shorts/YouTube_Shorts_Analytics_<date>.xlsx`
Sheet: `Table data`. Filter out rows where `Content == "Total"`.

### Category system
Every video gets a parent category (A/B/C) and sub-category:

| Code | Name | What it is |
|---|---|---|
| A | News | Current events with AI angle |
| A1 | Governance & Safety | Regulation, safety, data privacy, AI ethics |
| A2 | Jobs & Economy | Employment, wages, productivity, costs |
| A3 | Indirect Trend | Non-AI topic trending + genuine AI connection (≤20% cap) |
| B | Vocab | AI vocabulary explained for non-technical professionals |
| B1 | Meeting-survival terms | Terms Marisa hears in meetings (RAG, LLM, hallucination, guardrails) |
| B2 | Manager-decision terms | Terms needed to make decisions (tokens, build-vs-buy, red teaming) |
| B3 | Tool explainers | Specific tool walkthroughs |
| C | Someone Did This | Aspiration/social proof engine |
| C1 | Peer stories | Real named person who did something with AI |
| C2 | Resource recommendations | Course/tool Sanjay recommends (Andrew Ng, Google, etc.) |

### Classification priority
1. Check `content_pipeline.md` for the video's S-number and its declared category code
2. If not in pipeline, classify from the title using the category definitions above
3. Default fallback: A1 (most common category)

### Legacy type codes (pre-July 2026 back catalogue)
T/SF → A, IT → A3, V/P → B, L → C (linked/trailer)

## Step 3 — Key columns to extract
From the Excel:
- `Video title`
- `Video publish time` (parse with formats: `%b %d, %Y` / `%B %d, %Y` / `%Y-%m-%d`)
- `Stayed to watch (%)` — Shorts-exclusive hook signal
- `Average percentage viewed (%)` — full-video retention signal
- `Engaged views`
- `Impressions click-through rate (%)`
- `Subscribers gained`, `Subscribers lost`

## Step 4 — Compute OKR metrics

### Windows
- **Recent:** last 12 published shorts (sort by publish_date descending, head(12))
- **All-time:** all rows in the file (all AI videos since relaunch)

### OKR targets and thresholds (set Dec 2026)
| Metric | Target | Green ≥ | Amber ≥ | Red |
|---|---|---|---|---|
| Stayed to Watch (%) | 62% | 58% | 45% | <45% |
| Avg % Viewed (%) | 68% | 62% | 50% | <50% |
| Engaged Views | 600 | 600 | 0 | <0 |
| CTR non-feed (%) | 4.0% | 4.0% | 2.0% | <2.0% |

RAG status: green/amber/red — applied to the RECENT value.

## Step 5 — Compute sub-category averages
For each sub-category (A1/A2/A3/B1/B2/B3/C1/C2) that has at least 1 video:
- count, avg_stayed, avg_pct_viewed, avg_engaged_views, avg_ctr

## Step 6 — Top and bottom performers (composite OKR score)

Rank videos by a **weighted composite score** across all 4 OKR metrics:

```
score = 0.40 × (stayed_to_watch / 70)
      + 0.25 × (avg_pct_viewed  / 80)
      + 0.25 × (engaged_views   / 600)
      + 0.10 × (ctr             / 4.0)
```

Score of 1.0 = hitting every OKR target exactly. Cap each ratio at 1.5 so no single metric dominates.

**Weights rationale:**
- Stayed to Watch 40% — YouTube's #1 Shorts signal; binary decision in 1–3 seconds
- Avg % Viewed 25% — full-video quality; hook + content + payoff + exit
- Engaged Views 25% — subscriber conversion signal (6x vs News confirmed on channel)
- CTR 10% — packaging signal, but non-feed is a small fraction of Shorts traffic

**Top 3:** videos published >21 days ago (data has stabilised), highest composite score
**Bottom 3:** videos published >7 days ago (enough signal), lowest composite score

Include `composite_score` on every video in the videos list.
Include `scoring_note` in meta explaining the weights used.

## Step 6b — Outliers (single-metric extremes)

Always compute and include in `"outliers"` key:

| Key | Definition | Pool |
|---|---|---|
| `best_ctr` | Highest CTR % | All videos |
| `best_stayed` | Highest Stayed to Watch % | All videos |
| `best_pct_viewed` | Highest Avg % Viewed | All videos |
| `best_subs` | Most Subscribers gained | All videos |
| `worst_ctr_recent` | Lowest CTR % | Last 12 only |
| `worst_stayed_recent` | Lowest Stayed to Watch % | Last 12 only |

Each outlier entry: `{ title, value, unit, sub_category, publish_date, note }`
Note = one sentence explaining why this outlier matters or what to do about it.

## Step 7 — Patterns (mandatory checks)
Always compute and include:
1. Category mix (A/B/C counts and %) — flag if Vocab <25% of total
2. Subs/video by category (Subscribers gained ÷ video count) — Vocab should run higher
3. Best sub-category on each metric (engaged views, stayed, CTR)
4. Recent trend: first 6 of recent window vs next 6 — is stayed_to_watch improving?
5. Gap between Avg % Viewed and Stayed to Watch — if gap <5pp, the decision is binary (hook or swipe)
6. C category count — flag if <5 videos total

## Step 8 — Recommendations (max 3, actionable only)
Base on actual gaps vs targets. Standard triggers:
- Stayed to Watch <58% → hook rubric enforcement recommendation
- CTR <4% → title/thumbnail review + cite channel's own top CTR benchmarks
- Vocab (B) <25% of total → increase B cadence to 2/week
- C <5 videos → start C1 peer story series

## Step 9 — Output JSON schema
Save to: `dashboard/weekly_insights/YYYY-MM-DD_shorts.json`

```json
{
  "meta": {
    "generated_date": "YYYY-MM-DD",
    "data_range": "DD Mon YYYY – DD Mon YYYY",
    "total_videos_analyzed": 63,
    "recent_window": "last 12 (published DD Mon – DD Mon YYYY)",
    "source_file": "YouTube_Shorts_Analytics_2_Aug_2026.xlsx"
  },
  "okr_snapshot": {
    "stayed_to_watch":  { "recent": 53.8, "alltime": 44.7, "target": 70.0, "status": "amber" },
    "avg_pct_viewed":   { "recent": 55.5, "alltime": 55.0, "target": 80.0, "status": "amber" },
    "engaged_views":    { "recent": 393,  "alltime": 325,  "target": 600,  "status": "amber" },
    "ctr":              { "recent": 2.53, "alltime": 1.81, "target": 4.0,  "status": "amber" }
  },
  "sub_category_performance": {
    "A1": {
      "label": "A1 Governance & Safety",
      "count": 23,
      "avg_stayed": 49.5,
      "avg_pct_viewed": 57.7,
      "avg_engaged_views": 419,
      "avg_ctr": 1.84
    }
  },
  "videos": [
    {
      "title": "...",
      "publish_date": "YYYY-MM-DD",
      "category": "A",
      "sub_category": "A1",
      "stayed_to_watch": 54.2,
      "avg_pct_viewed": 56.7,
      "engaged_views": 630,
      "ctr": 0.21
    }
  ],
  "top_performers": [
    { "rank": 1, "title": "...", "category": "A", "sub_category": "A1", "reason": "Engaged views: 630 | Stayed: 54.2% | CTR: 0.21%" }
  ],
  "bottom_performers": [
    { "rank": 1, "title": "...", "category": "B", "sub_category": "B1", "reason": "Stayed: 12.5% (hook failed) | Engaged views: 37 | CTR: 0.63%" }
  ],
  "patterns": [ "string", "string" ],
  "recommendations": [ "string", "string" ]
}
```

## Step 10 — Tell Sanjay
After saving, say:
1. Report saved to `dashboard/weekly_insights/YYYY-MM-DD_shorts.json`
2. Refresh the dashboard → Weekly Insights tab → select the report from the dropdown
3. Give a 5-bullet plain-English summary of the key findings
