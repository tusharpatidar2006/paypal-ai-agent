# Progress

## Phase 0: Bootstrap
- [x] T0.1 Create PROGRESS.md and HUMAN_TODO.md
- [x] T0.2 Create .gitignore, LICENSE (Apache-2.0), pyproject.toml skeleton
- [x] T0.3 Create directory tree
- [x] T0.4 Create .env.example
- [x] T0.5 Create Makefile with all targets
- [x] T0.6 Initial commit (git operations timeout, manual step needed)

## Phase 1: Core contracts and crypto
- [ ] T1.1 Implement Money, Address, Intent, Mandate in contracts.py
- [ ] T1.2 Implement canonical.py (deterministic JSON)
- [ ] T1.3 Implement signing.py (Ed25519) and keys.py
- [ ] T1.4 Write tests for signing and mandate creation
- [ ] T1.5 Implement nonce_store.py

## Phase 2: PayPal clients
- [ ] T2.1 Implement base.py (PayPalClient interface)
- [ ] T2.2 Implement fake.py (in-memory orders)
- [ ] T2.3 Implement mapping.py (mandate→PayPal Orders v2)
- [ ] T2.4 Write tests for fake mode
- [ ] T2.5 Implement real.py (sandbox REST)
- [ ] T2.6 Implement approval.py (simulated, manual link, playwright)
- [ ] T2.7 scripts/paypal_smoke.py

## Phase 3: Policy engine
- [ ] T3.1 Implement checks.py (payee, currency, amounts, etc.)
- [ ] T3.2 Implement reasons.py (codes and merchant mapping)
- [ ] T3.3 Implement engine.py (ALLOW/CHALLENGE/BLOCK + ratchet)
- [ ] T3.4 Write property tests for the ratchet
- [ ] T3.5 Implement PinnedSnapshot HMAC

## Phase 4: Marketplace simulator
- [ ] T4.1 Create fixtures/catalog.json (20+ SKUs, 5 categories, multi-merchant)
- [ ] T4.2 Implement catalog.py and pages.py (HTML with hooks)
- [ ] T4.3 Implement images.py (placeholder images with optional text)
- [ ] T4.4 Implement server.py (marketplace Flask-like routes)
- [ ] T4.5 Write tests for catalog parsing

## Phase 5: Ingestion and detection (lite profile)
- [ ] T5.1 Implement static_dom.py (lxml + beautifulsoup)
- [ ] T5.2 Implement visibility.py (CSS computed visibility)
- [ ] T5.3 Implement normalize.py (Unicode, ZWJ, homoglyphs)
- [ ] T5.4 Implement decode.py (base64, URL, HTML entity)
- [ ] T5.5 Implement segments.py (extraction)
- [ ] T5.6 Implement rules.py (pattern detectors)
- [ ] T5.7 Implement classifier.py (TF-IDF logistic, ONNX optional)
- [ ] T5.8 Implement embed.py (HashingVectorizer fallback)
- [ ] T5.9 Implement knn.py (L2 distance)
- [ ] T5.10 Implement stack.py (calibration)
- [ ] T5.11 Implement cascade.py (band assignment)
- [ ] T5.12 Write tests for detector cascade

## Phase 6: Sanitization and isolation
- [ ] T6.1 Implement neutralize.py (remove flagged spans, charset filter)
- [ ] T6.2 Implement extract.py (typed StructuredView)
- [ ] T6.3 Implement provenance.py (HMAC snapshot)
- [ ] T6.4 Implement canary.py (honeypot skus)
- [ ] T6.5 Write tests for sanitization

## Phase 7: LLM client and agents
- [ ] T7.1 Implement llm/client.py (mock and openai_compat)
- [ ] T7.2 Implement llm/protocol.py (JSON action loop)
- [ ] T7.3 Implement agents/naive.py (ScriptedNaiveAgent baseline)
- [ ] T7.4 Implement agents/prompts.py
- [ ] T7.5 Implement agents/protected.py (ProtectedAgent)
- [ ] T7.6 Implement agents/loop.py
- [ ] T7.7 Write tests for agent action parsing

## Phase 8: Gateway orchestrator
- [ ] T8.1 Implement sessions.py (session state)
- [ ] T8.2 Implement orchestrator.py (purchase flow)
- [ ] T8.3 Implement challenges.py (user approval)
- [ ] T8.4 Implement events.py (SSE)
- [ ] T8.5 Write integration tests for purchase flows

## Phase 9: Telemetry and audit
- [ ] T9.1 Implement audit.py (hash-chained log)
- [ ] T9.2 Implement minhash.py
- [ ] T9.3 Implement signatures.py (store + lookup)
- [ ] T9.4 Implement merchants.py (salted hashes)
- [ ] T9.5 Implement appeals.py (state machine)
- [ ] T9.6 Implement attestation.py (signature verification)
- [ ] T9.7 Write tests for hash chain integrity

## Phase 10: Red-team harness
- [ ] T10.1 Implement families.py (attack goals and families)
- [ ] T10.2 Implement seeds.py (base payloads)
- [ ] T10.3 Implement transforms.py (mutation operators)
- [ ] T10.4 Implement bandit.py (UCB1 operator selection)
- [ ] T10.5 Implement generator.py
- [ ] T10.6 Implement evolve.py (generation loop)
- [ ] T10.7 Implement oracle.py (ground-truth diff checker)
- [ ] T10.8 scripts/build_corpora.py

## Phase 11: Evaluation
- [ ] T11.1 Implement harness.py (run all tests)
- [ ] T11.2 Implement metrics.py (precision, recall, F1, FPR, bypass rate)
- [ ] T11.3 Implement latency.py (P50, P95, P99)
- [ ] T11.4 Implement ablation.py (disable cascade stages)
- [ ] T11.5 Implement report.py (generate reports/)
- [ ] T11.6 Makefile target: make eval
- [ ] T11.7 scripts/calibrate.py (threshold tuning on train only)

## Phase 12: Quarantined judge
- [ ] T12.1 Implement judge.py (LLM spotlight, enum output, timeout)
- [ ] T12.2 Implement spotlight.py (context building)
- [ ] T12.3 Write tests for judge isolation

## Phase 13: Web UI
- [ ] T13.1 Vite + React + TS skeleton
- [ ] T13.2 Mandate Studio component (form + signature display)
- [ ] T13.3 Purchase component (mode toggle, session)
- [ ] T13.4 Event stream display (SSE)
- [ ] T13.5 Audit log grid (AG Grid)
- [ ] T13.6 Telemetry charts (Recharts)
- [ ] T13.7 FastAPI static serving of /web/dist

## Phase 14: Invariant tests
- [ ] T14.1 I-1: No order without ALLOW or approved CHALLENGE
- [ ] T14.2 I-2: All order fields match mandate
- [ ] T14.3 I-3: Detector can only tighten verdict
- [ ] T14.4 I-4: No UNTRUSTED_MERCHANT text to agent
- [ ] T14.5 I-5: Signing key unreachable from gateway/ingest/detect
- [ ] T14.6 I-6: Fail closed on exceptions
- [ ] T14.7 I-7: Hash chain verifies
- [ ] T14.8 I-8: No scores/rules in merchant responses
- [ ] T14.9 I-9: No PII in telemetry

## Phase 15: Full detector profile
- [ ] T15.1 Implement render.py (Playwright)
- [ ] T15.2 Implement ocr.py (pytesseract)
- [ ] T15.3 scripts/fetch_models.py (DeBERTa ONNX, fastembed)
- [ ] T15.4 Update classifier.py for ONNX
- [ ] T15.5 Update embed.py for fastembed
- [ ] T15.6 Write tests gated by model availability

## Phase 16: Optional MCP adapter
- [ ] T16.1 Implement paypal/mcp_adapter.py
- [ ] T16.2 scripts/mcp_smoke.py
- [ ] T16.3 Document MCP server location/version

## Phase 17: Packaging
- [ ] T17.1 Dockerfile (multi-stage)
- [ ] T17.2 docker-compose.yml
- [ ] T17.3 render.yaml
- [ ] T17.4 Test docker build

## Phase 18: Scenarios and demo
- [ ] T18.1 fixtures/scenarios.json (5+ demo flows)
- [ ] T18.2 Makefile target: make demo
- [ ] T18.3 docs/VIDEO_SCRIPT.md
- [ ] T18.4 scripts/publish_checklist.md

## Phase 19: Documentation
- [ ] T19.1 README.md (generated by agent)
- [ ] T19.2 docs/ARCHITECTURE.md
- [ ] T19.3 docs/DEVPOST_DRAFT.md
- [ ] T19.4 THIRD_PARTY.md

## Phase 20: Final checks
- [ ] T20.1 Run make eval, commit reports/
- [ ] T20.2 Run make verify-invariants
- [ ] T20.3 Run make lint
- [ ] T20.4 Verify all numbers in README come from reports/
- [ ] T20.5 Review THIRD_PARTY.md licenses
- [ ] T20.6 Verify .env.example is complete

## BLOCKED
(none)

## Decisions
- Starting with Phase 0 bootstrap
