# Hobim Trades Website — Planning Summary

## Business Scope
Three products, one platform:
1. **Mentorship** — recurring paid, hands-on
2. **Courses** — one-time purchase, gated streaming (not downloadable)
3. **Trading bots/systems** (MQL/MetaTrader EAs) — hybrid pricing, subscription-focused

No signals product for now.

---

## Product Details

### Courses
- Delivery model: gated streaming only, like Whop — never downloadable files
- Bundled with 1 month of free mentorship access after purchase, as a conversion funnel (newbies who like the community convert into paying mentorship customers)

### Mentorship
- Format: hands-on — shows his own trading setup, weekend live group calls, answers both technical and psychological questions
- Must be recurring revenue, not lifetime or free
- Positioning note: not contradictory to sell automation (bots) alongside manual mentorship — mentorship serves people who want to *become* traders, bots serve people who want the *results* without doing the work; the manual trading expertise is what makes the bots credible
- Scaling problem identified: can't personally answer every question at scale
- Solution: an AI assistant (LangGraph-based), clearly labeled as AI, trained on his trading material/FAQ, handles common/repeated technical and definitional questions instantly. Escalates anything psychological/emotional, account-specific, or where it's not confident, to him personally on the weekend calls. Must never pretend to be him — always labeled.
- Additional scaling support: structured Q&A windows (not "ask anytime"), a searchable FAQ built from repeated questions, and a peer-support tier (experienced members get a recognized role for helping newer ones)

### Bots (MQL/MetaTrader EAs)
- Pricing tiers per bot: **free tier**, **1-month**, **6-month**, **12-month** subscriptions, and a **one-off (lifetime) purchase**
- Lifetime buyers still pay a smaller recurring fee — separates the one-time license (the algorithm itself, owned forever) from the ongoing cost of infra/hosting/data that keeps it running
- Default: lifetime license includes hosted infra + the recurring hosting fee (for non-technical users who don't want to manage a VPS)
- Opt-out: technical users can self-host (their own VPS) and skip the recurring fee entirely
- Delivery reality: MQL bots run inside MetaTrader 4/5, which must run continuously — this requires a VPS (the user's own, or Hobim Trades' managed one) since a personal laptop being on/off would stop the bot
- Licensing/entitlement flow (standard EA-seller pattern):
  1. User subscribes → payment processed → backend creates/updates an entitlement record tied to the user's account + their broker account number (prevents license sharing across accounts)
  2. Backend issues a license key
  3. The EA calls the backend's API periodically via MQL5's `WebRequest()` function, sending account number + license key
  4. Backend checks the entitlements table and returns valid/invalid
  5. EA enables/disables trading based on the response — subscription lapse = bot stops automatically, no manual step needed
  - Note: `WebRequest()` requires the API URL to be whitelisted in MetaTrader's settings — a one-time setup step (invisible to the user on hosted/managed accounts, a documented step for self-hosted users)
- Broker/prop firm affiliate angle: recommend brokers/prop firms based on whether they allow EA/bot trading (many prop firms restrict or ban bots outright), using affiliate (Introducing Broker) links for commission when users fund/trade through them
  - Researching prop firm compatibility via propfirmatch.com
  - Plan: maintain a broker/prop-firm compatibility table (allowed/restricted/conditional, commission structure, affiliate link) and surface relevant recommendations at the point a user is setting up a bot subscription (personal funds vs. prop firm account as a filter)
  - Note: commission tracking is controlled by the broker's own system, not verifiable independently — pick reputable brokers for reliable affiliate payouts

---

## Shared Backend Model (covers all three products with one system)
- **Users** — auth, profile, role
- **Products** — generic table for courses, bots, mentorship, each with a `type` field and pricing tiers
- **Pricing tiers** — per product: free, 1/6/12-month, lifetime, with price and billing interval
- **Subscriptions** — user + product + tier, with status (active/cancelled/expired) and current period end
- **Entitlements** — the access-control table every part of the system checks ("does user X have valid access to product Y right now") — derived from subscriptions but kept separate for fast checks
- **Payments/transactions** — record of charges, gateway used, for audit/reconciliation

## Service Breakdown (all FastAPI, can start as one app)
- Auth service
- Catalog/product service
- Billing service — Paystack/Flutterwave (Stripe later if going international), handles webhooks for payment success/renewal/failure, updates subscriptions/entitlements (needs webhook retry/idempotency built in from day one)
- Content delivery service — gated/streamed course video, never a raw downloadable link
- Bot delivery/licensing service — issues license keys/tokens tied to entitlements, handles the EA-facing validation endpoint
- AI assistant service — LangGraph-based, scoped to FAQ/course content, with escalation rules

## Suggested Build Order
1. Auth + Users + Products + basic marketing pages (no payment yet)
2. Billing integration + Subscriptions + Entitlements (the core, hardest part)
3. Course content delivery (gated streaming)
4. Bot licensing/entitlement checks
5. Mentorship community wiring (e.g. Discord role sync tied to entitlements)
6. AI assistant layered in last, once there's real FAQ data from actual users

---

## Website Architecture Decisions
- **Frontend**: Next.js, hosted on Vercel — main domain (e.g. `hobimtrades.com`)
  - Subtle animation only (Framer Motion) — hero entrance, pricing card hover/lift, scroll-triggered fade-ins, smooth dashboard state transitions
  - No animation on functional flows: course video player, checkout/payment, in-dashboard actions — keep those fast and friction-free
- **Backend**: FastAPI, hosted on Railway or Render — subdomain (e.g. `api.hobimtrades.com`)
- **Database**: Postgres, managed (via the backend hosting platform)
- **Redis**: added later once there's an actual speed need (session/cache, fast entitlement checks) — not needed day one
- **Decision**: keep frontend and backend on separate servers (not combined in one Next.js project) — chosen specifically because the backend logic here (entitlements, licensing, billing webhooks, AI assistant) is substantial and better done in Python/FastAPI than crammed into JS-based API routes. Requires CORS configuration on the FastAPI side to allow the frontend domain.
- **Domain**: bought from a registrar (e.g. Namecheap), DNS configured to point the main domain at Vercel and the `api.` subdomain at Railway/Render
- **HTTPS/SSL**: handled automatically by Vercel/Railway/Render once the domain is connected

### How a page load actually flows
User types `hobimtrades.com` → DNS routes to Vercel (frontend) → frontend loads and its JS calls `api.hobimtrades.com` → DNS routes that to Railway/Render (backend) → FastAPI processes the request (checks entitlements, DB, etc.) and returns data → frontend displays it.

---

## Infrastructure Cost Picture

**Fixed cost (backend + DB + frontend hosting, doesn't scale per user):**
- Roughly $10–40/month to start on Railway/Render for the backend + Postgres; Vercel free tier is enough for the frontend initially

**Variable cost (per hosted bot subscriber — each needs their own isolated VPS running MetaTrader):**
- Budget forex VPS: ~$8–15/month per instance
- Mid-range (better latency/uptime, more appropriate for running client money): ~$20–40/month per instance
- Annual commitments lower the per-month rate

**Pricing implication:** the recurring hosting fee charged to hosted users (including lifetime buyers who opt for hosting) needs to sit above the real per-user VPS cost with margin — not just break-even — to account for churn, provider price changes, and time spent managing instances.

**Other variable costs:**
- Payment gateway fees (Paystack/Flutterwave typically ~1.5–3.5% per transaction)
- LLM API costs for the AI assistant — usage-based, small per query relative to VPS costs

**Not a cost to worry about:** real-time market data — MT4/MT5 gets live prices directly from the user's broker connection, no separate data feed subscription needed.

---

## Open / Not Yet Decided
- Exact pricing numbers for each tier (courses, mentorship, bot subscriptions, hosting fee) — cost picture is now known, numbers not yet set
- Actual Postgres schema (tables, columns, relationships) — not yet built
- Billing/webhook flow details — not yet worked through
- Site/page structure (what's public vs. gated) — not yet mapped
- Specific brokers/prop firms to feature — research in progress via propfirmatch.com