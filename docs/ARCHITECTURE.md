# Clean Room Architecture

## System Overview

Clean Room implements defense-in-depth for AI shopping agents through four trust zones and cryptographic mandate enforcement.

## Trust Zones

### 1. Untrusted Zone (Red)
**Content:** Raw merchant data
- HTML product listings
- Reviews and Q&A
- Seller messages
- Images with embedded text
- JSON-LD metadata

**Threat Model:** Adversarial content designed to manipulate AI agents through:
- Prompt injection
- Hidden instructions (CSS, zero-width chars)
- Homoglyphs and obfuscation
- Address/payee manipulation
- Data exfiltration

### 2. Screening Zone (Orange)
**Purpose:** Content analysis and sanitization

**Pipeline:**
1. **Ingest** (`ingest/`)
   - Render mode: static DOM or Playwright
   - Visibility analysis (CSS computed styles)
   - OCR for images (optional Tesseract)
   - Extract segments with provenance

2. **Normalize** (`ingest/normalize.py`)
   - Unicode NFC normalization
   - Zero-width character removal
   - Homoglyph replacement
   - Whitespace normalization

3. **Decode** (`ingest/decode.py`)
   - Base64 detection and decode
   - URL encoding
   - HTML entities
   - Track decode depth (limit cascades)

4. **Detect** (`detect/`)
   - Stage 1: Rule patterns (rules.py)
   - Stage 2a: ML classifier (TF-IDF or ONNX DeBERTa)
   - Stage 2b: kNN similarity vs signatures
   - Stage 2c: Stacking + calibration
   - Band assignment: clear / gray / flagged

5. **Judge** (quarantined, `detect/judge.py`)
   - Only for gray band
   - No tools, no internet
   - Enum output only: attack / benign / unsure
   - Timeout enforced

6. **Sanitize** (`sanitize/`)
   - Remove flagged spans
   - Extract typed fields only
   - Character-set restrictions
   - Length limits (80 chars titles)
   - Fixed vocabulary features

### 3. Agent Zone (Blue)
**Content:** StructuredView only

**Protected Agent:**
- Sees only sanitized, typed data
- Tools: `search_view(query)`, `propose_order(sku, qty)`
- Cannot access raw HTML/images
- Cannot set shipping address or payee

**Naive Agent (Baseline):**
- Sees raw HTML (for comparison)
- Free-form order construction
- No mandate enforcement
- Used to detect bypasses (oracle)

### 4. Trusted Zone (Green)
**Components:**

**Mandate Studio:**
- Creates signed mandates (Ed25519)
- User specifies limits
- Single-use nonce generation

**Gateway Orchestrator:**
- Receives ProposedOrder from agent
- Builds OrderDraft from mandate + pinned snapshot
- Validates all fields server-side

**Policy Engine:**
- Deterministic verdict logic
- Hard checks → BLOCK
- Soft checks → CHALLENGE
- Detection ratchet (tightening only)

**PayPal Client:**
- Creates orders only on ALLOW or approved CHALLENGE
- Fake (in-memory) / Real (sandbox REST) / MCP adapter

## Data Flow

### Purchase Flow

```
1. User creates mandate in Mandate Studio
   → Ed25519 signature over canonical JSON

2. User submits mandate + intent to Gateway
   → Gateway spawns protected agent session

3. Agent calls search_view("usb-c charger")
   → Gateway fetches listings
   → Screening pipeline processes content
   → Returns StructuredView to agent

4. Agent calls propose_order(sku="USBC-FAST-001", qty=1)
   → Gateway builds OrderDraft
   → Validates against mandate
   → Checks pinned snapshot (HMAC)

5. Policy Engine evaluates
   → Checks: signature, expiry, nonce, payee, currency, address, total
   → Detection band: clear / gray / flagged
   → Verdict: ALLOW / CHALLENGE / BLOCK

6. ALLOW → Create PayPal order
   CHALLENGE → Ask user for confirmation
   BLOCK → Reject with generic reason to merchant

7. Audit log records decision (hash-chained)
```

## Security Mechanisms

### 1. Cryptographic Mandate
**Ed25519 Signature:**
- Canonical JSON (deterministic serialization)
- Signature over mandate without signature field
- Public key verification in policy engine

**Fields:**
- `allowed_payees`: Merchant allowlist
- `max_total`: Hard cap
- `ship_to`: Frozen address
- `step_up_over`: Challenge threshold
- `nonce`: Single-use token

### 2. Detection Cascade

**Stage 1: Rules**
- Fast regex patterns
- Known attack signatures
- Obfuscation indicators
- Score: 0.0-1.0

**Stage 2a: Classifier**
- Lite: TF-IDF + logistic regression
- Full: ONNX DeBERTa (184M params)
- Probability: 0.0-1.0

**Stage 2b: kNN**
- MinHash (64 perms, salted word 3-grams)
- Optional: Embedding vectors (fastembed)
- Fallback: HashingVectorizer
- Similarity: 0.0-1.0

**Stage 2c: Stacking**
- Weighted ensemble
- Calibration (isotonic regression)
- Final probability: 0.0-1.0

**Stage 3: Judge**
- Quarantined LLM (no tools)
- Spotlight: Segment + surrounding context
- Enum output: attack / benign / unsure
- Only for gray band (t_low < p < t_high)

**Band Assignment:**
- `p < t_low` → **clear**
- `t_low ≤ p < t_high` → **gray** → judge
- `p ≥ t_high` → **flagged**

### 3. Policy Ratchet

```
Base verdict (from mandate checks):
  - Any hard failure → BLOCK
  - Soft deviations → CHALLENGE
  - All pass → ALLOW

Detection ratchet (tightening only):
  - ALLOW + flagged → CHALLENGE or notify
  - ALLOW + gray → CHALLENGE
  - CHALLENGE + anything → CHALLENGE
  - BLOCK + anything → BLOCK
```

### 4. Isolation Mechanisms

**Provenance Tracking:**
- Every segment tagged with source_ref
- DOM path + URL
- Visibility flag
- Decode history

**Honeypots:**
- Special SKUs (e.g., "HONEYPOT-999")
- Not in normal search results
- Touching them → BLOCK

**Canaries:**
- Secret tokens embedded in agent context
- If leaked to order note → BLOCK

**Pinned Snapshot:**
- Server captures prices at ingest time
- HMAC with gateway-only key
- TTL (default 15 min)
- Prevents TOCTOU price manipulation

### 5. Audit Log

**Hash Chain:**
```
Record_N = {
  seq: N,
  ts: timestamp,
  kind: "decision",
  payload: {...},
  prev_hash: hash(Record_{N-1}),
  hash: sha256(prev_hash || canonical_json(seq, ts, kind, payload))
}
```

**Tamper Detection:**
- Recompute hash chain from genesis
- Verify each link
- Detect modifications, insertions, deletions

### 6. Cross-Merchant Immunization

**Signature Store:**
- MinHash + optional embedding
- Salted merchant ID (no PII)
- Status: provisional / global / revoked
- Promote to global after K merchants or canary hit

**Similarity Lookup:**
- New content → compute signature
- Search existing signatures (Jaccard, L2)
- Match → flag before any agent sees it

## Red Team Harness

### Attack Generation

**Goals:**
- address_swap, payee_swap, extra_items, amount_inflation
- exfiltration, choice_manipulation, override_noop

**Surfaces:**
- title, description, review, seller_message, invoice
- image_text, jsonld, meta_attr, comment, checkout_page

**Obfuscations:**
- Homoglyphs, zero-width, base64, CSS hidden, HTML comments
- Unicode tricks, RTL override, zalgo text

**Evolution:**
- UCB1 bandit selects mutation operators
- Fitness: bypass detector AND hijack naive agent
- Oracle: diff between naive and protected outcomes
- Save successful bypasses → retrain → re-eval

**Data Splits:**
- train: Calibrate thresholds and train stack
- val: Tune hyperparameters
- test: Fixed evaluation set (never tuned on)
- heldout: Attack families never seen during training

## Performance Budgets

| Operation | Target | Notes |
|-----------|--------|-------|
| Scan (lite) | < 500ms P95 | Static DOM + rules + TF-IDF |
| Scan (full) | < 2s P95 | Playwright + ONNX + kNN |
| Judge call | < 6s (timeout) | LLM with enum output |
| Policy eval | < 10ms P95 | Deterministic checks |
| Mandate sign | < 5ms | Ed25519 |

## Deployment Modes

### 1. Fake Mode (Default)
- `PAYPAL_MODE=fake` (in-memory)
- `LLM_MODE=mock` (deterministic)
- `DETECTOR_PROFILE=lite` (no ML models)
- Zero external dependencies
- All tests pass

### 2. Sandbox Mode
- `PAYPAL_MODE=sandbox` (real REST API)
- `LLM_MODE=openai_compat` (real LLM)
- `DETECTOR_PROFILE=full` (ONNX + embeddings + OCR)
- Requires: H1, H4, H6, H7

### 3. Production (Out of Scope)
- Would require: production PayPal credentials, compliance review
- Not implemented (hackathon sandbox only)

## Testing Strategy

### Unit Tests
- Crypto: signing, verification, determinism
- Policy: mandate checks, nonce store, expiry
- Detection: rules, classifiers, kNN
- PayPal: fake client, mapping

### Property Tests (Hypothesis)
- Ratchet: detection never loosens verdict
- Canonical JSON: deterministic serialization
- Hash chain: tamper detection

### Invariant Tests
- I-1 to I-9 (see README)
- Mandatory for every commit

### Integration Tests
- End-to-end purchase flows
- Challenge approval
- Audit log verification

### E2E Tests (Optional)
- Playwright-driven UI tests
- Full stack scenarios

## Extension Points

### 1. Additional PayPal Features
- Subscriptions, invoicing, disputes
- Multi-currency support
- Tax calculation

### 2. Additional Detection Models
- Multilingual models (non-English)
- Image-based injection detection
- Audio analysis (voice shopping)

### 3. Additional Agent Types
- Multi-step planning agents
- Collaborative agents (multiple users)
- Federated agents (cross-platform)

### 4. Additional Marketplaces
- eBay, Amazon, Etsy adapters
- Physical retail (in-store agents)
- Service marketplaces (Upwork, Fiverr)

## References

- PayPal Orders API v2: https://developer.paypal.com/docs/api/orders/v2/
- ProtectAI DeBERTa: https://huggingface.co/protectai/deberta-v3-base-prompt-injection-v2
- Prompt Injection Taxonomy: https://github.com/jthack/PIPE
- Clean Room Spec: CLEAN_ROOM_BUILD_SPEC.md
