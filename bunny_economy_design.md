# The_Remeris_Archive Companion Economy -  Design Doc v1

Core principle, above all else: **XP requires net creative output, not presence.**
Every formula, price, and bonus below is checked against this rule. If a future addition can be gamed by sitting idle, deleting-and-retyping the same words, or just "showing up," it doesn't belong in this system.

---

## 1. The Two Currencies

| | Ink Quill (IQ) | Wisdom Fragments (WF) |
|---|---|---|
| **What it is** | Permanent XP - never decreases | Spendable currency |
| **Drives** | Bunny's level, voicelines, lore | Themes, sounds, lofi, bunny cosmetics |
| **Feels like** | Your lifetime writing journey | Your spending money |

**Important design change: I earlier proposed *converting* IQ into WF manually. Eventually I recommended myself against that - spending down a stockpile of IQ to buy a theme would mean *watching your bunny's level requirement effectively get harder to justify*, which feels bad even if the level itself doesn't drop. 

Instead: **both currencies are earned simultaneously from the same net words**, at different rates. IQ is the "big permanent number," WF is the "smaller spendable number." You never trade one for the other - you just earn both every time you write. This keeps the "Ink Quill turns into Wisdom Fragments" *flavor* (WF literally only exists because you wrote) without ever making spending feel like a downgrade.

If I still want a manual conversion feature later for thematic reasons ("the bunny transmutes old memories into wisdom"), it's easy to add on top of this foundation - but it seems easier to ship without it first and see if it's even missed.

---

## 2. The Core Formula (per writing session)

```
net_words = max(0, words_at_session_end − words_at_session_start)

IQ_earned = net_words × 1                    (1 word = 1 Ink Quill, flat and transparent)
WF_earned = floor(net_words ÷ 10)             (1 Wisdom Fragment per 10 words)

+ return_bonus   (see below)
+ milestone_bonus (see below, one-time per threshold, lifetime)
```

**Why net, not gross:** deleting 500 words and typing 500 different ones nets 0 IQ. This alone kills almost every way someone could try to game it - heavy rewriting isn't punished, but it also isn't free XP.

**Why 1:1 for IQ:** total transparency. "1000 words = 1000 Ink Quill" is something a user can say out loud and be right. All the actual *pacing* of progression happens in the level curve (below), not by hiding a multiplier in the word-to-XP conversion.

### Return bonus
```
if hours_since_last_session > 18:
    IQ_earned += 25
```
Flat, one-time per return, not stackable within the same day. Rewards *coming back*, not *coming back every single day without fail* - exactly matching the no-streak-punishment stance.

### First session of the day
**0 XP.** Just a unique bunny greeting line. The moment this gives even +5 XP, it quietly becomes a daily check-in app, which is the opposite of what I want. Keep it purely narrative.

### Idle time
Not tracked as a penalty - it's just naturally worth 0 IQ, because idle time produces 0 net words. No extra logic needed; the net-words rule already handles it for free.

---

## 3. Bunny Level Curve (driven by lifetime IQ)

```
IQ_needed_to_reach_level(L) = round(200 × L^1.5)     (this is the increment from L-1 to L)
```

| Level | IQ needed (this level) | Cumulative lifetime IQ | ≈ words written |
|---|---|---|---|
| 2 | 200 | 200 | 200 |
| 3 | 566 | 766 | 766 |
| 4 | 1,039 | 1,805 | ~1,800 |
| 5 | 1,600 | 3,405 | ~3,400 |
| 6 | 2,236 | 5,641 | ~5,600 |
| 7 | 2,939 | 8,580 | ~8,600 |
| 8 | 3,704 | 12,284 | ~12,300 |
| 9 | 4,525 | 16,809 | ~16,800 |
| 10 | 5,400 | 22,209 | ~22,200 |

Since IQ is 1:1 with words, this table doubles as "how many lifetime words until level N" - easy to reason about, easy to tune later (just change the exponent).

Levels feel meaningfully separate from **Environments** (below), which unlock on their own coarser lifetime-word ladder. That's intentional: two tracks, occasionally lining up (nice "double win" days), but neither dependent on the other. Voicelines and lore unlock off the **level** track, not the environment track.

**Suggested unlock cadence:**
- Every level → small bunny reaction/animation
- Every 3 levels → new voiceline pool unlocks
- Every 5 levels → a lore fragment unlocks (little bit of bunny backstory, unlocked not bought)

---

## 4. Wisdom Fragments - Shop Pricing

Guardrail: **the first purchase should be affordable within the first sitting.** At 1 WF per 10 words, someone writing 500 words in a first session has 50 WF - that needs to be enough for *something*, or the loop never proves itself.

| Item | Category | Price (WF) | Notes |
|---|---|---|---|
| Default theme | Theme | Free | Already unlocked |
| Blue / Mint / Lavender / Pink theme | Theme | 50 WF each | Cheap, fast first win |
| Dark theme | Theme | 50 WF | Same tier |
| Future "premium" themes (animated accents, seasonal) | Theme | 150–250 WF | Later addition |
| Typing sound pack (keyboard clack styles, page-turn) | Sound | 75–150 WF | |
| Lofi music pack (~5 tracks) | Music | 200 WF | |
| Additional lofi packs | Music | 200–300 WF | Slightly pricier over time |
| Bunny accessory (hat, scarf) | Cosmetic | 100 WF | |
| Bunny full outfit (robe recolor, seasonal costume) | Cosmetic | 300 WF | |
| Rare animated accessory (sparkle trail, glowing item) | Cosmetic | 500 WF | Aspirational, later-game |

**Not for sale, ever:**
- **Voicelines & lore** - unlock from bunny *level* (IQ), free. These are earned narrative payoff, not shop items - pricing them would make them feel transactional instead of like growth.
- **Environments** - unlock from lifetime *word count*, free. To me instinctually these should feel like an accomplishment, not a purchase. Full agreement on this one - don't relitigate it later even if it's tempting to monetize-adjacent it.

---

## 5. Environments (confirmed ladder from my brainstorm)

Purely lifetime-word-count gated. No WF cost, ever.

| Lifetime words | Environment | Ambience included (auto, muteable) |
|---|---|---|
| 0 | Default Desk | none |
| 1,000 | Park | birdsong, light wind |
| 5,000 | Café | café chatter, cup clinks |
| 10,000 | Library | page turns, quiet murmur |
| 25,000 | Rain Window | rain, distant thunder |
| 50,000 | Night Archive | fireplace crackle, night wind |

Two separate mute toggles as I specified: one for **ambience** (rain/café/etc.), one for **music** (lofi). Both default ON but instantly killable.

Room to extend later: a 100,000-word "prestige" environment slot is easy to bolt on without touching this table's logic - just add a row.

---

## 6. Guardrails Recap (the "doesn't feel bad" checklist)

- Net words only - editing/rewriting is never penalized, never double-rewarded
- No streaks, no daily punishment - flat return bonus instead
- First purchase reachable in one sitting
- Nothing gameplay-mandatory is ever locked behind payment - it's all atmosphere, so nothing here creates a "pay to compete" feeling
- Two currencies, but never a demoralizing trade-off between them
- Environments and lore feel *earned*, not purchased - preserves the "accomplishment" feeling I specifically wanted

---

## 7. Building This So I Can Extend It Later

When it's time to code this up, structure it so **adding a new item never requires touching the core logic**:

- **Shop items as data, not code** - a list of `{id, name, category, price_wf, unlock_type}` entries (similar to how `themes.py` is already just a dictionary). Adding a new theme or sound pack later = one new entry, zero logic changes.
- **One constants file** holding every tunable number (`WORDS_TO_IQ_RATIO`, `RETURN_BONUS_IQ`, the level-curve exponent, the environment word-thresholds) - so rebalancing later means editing one file, not hunting through the codebase.
- **An append-only session log**, not just a running total - store `{timestamp, net_words, iq_earned, wf_earned}` per session. This costs almost nothing to build now, and later shows the user graphs ("words per day this month"), recompute past sessions if I ever tweak the formula, and debug any "why did I get this much XP" questions.

This mirrors the same pattern I've already got in the app (theme dictionary, settings module) - so it'll feel like a natural extension of the existing codebase rather than a new architecture to learn.
