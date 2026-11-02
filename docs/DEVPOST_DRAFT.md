# Clean Room - DevPost Submission

## Project Title
**Clean Room: Trust Layer for AI Shopping Agents**

## Tagline (80 chars max)
Cryptographic mandates + ML detection stop merchant prompt injection attacks

## Inspiration
AI shopping agents are emerging as a convenient way for users to browse and buy products. However, they face a critical security threat: malicious merchants can embed prompt injections in product listings to hijack the agent's behavior—changing shipping addresses, swapping payees, inflating prices, or exfiltrating data.

Traditional content filtering isn't enough because:
- LLMs are vulnerable to sophisticated prompt injections
- New attack vectors emerge constantly (zero-width characters, homoglyphs, CSS tricks)
- False positives block legitimate content
- Attackers adapt faster than manual rule updates

We needed a solution that protects users even when detection fails.

## What It Does
Clean Room implements **defense-in-depth** for AI shopping agents through four security layers:

### 1. Signed Mandates (Cryptographic Enforcement)
Users create Ed25519-signed purchase mandates that specify:
- Maximum total amount
- Allowed merchants (payee allowlist)
- Exact shipping address
- Item quantity and line item limits
- Single-use nonce to prevent replay attacks

**Invariant:** Money cannot leave these constraints, even if all other layers fail.

### 2. Detection Cascade (Multi-Stage Analysis)
Suspicious content goes through:
- **Rules:** Fast pattern matching for known attacks
- **ML Classifier:** TF-IDF logistic regression (lite) or ONNX DeBERTa (full)
- **kNN Similarity:** Compare against known attack signatures using MinHash
- **Stacking:** Calibrated ensemble with band assignment (clear/gray/flagged)
- **Quarantined Judge:** Isolated LLM with no tools, enum-only output for gray band

### 3. Sanitization (Structured Views)
Protected agents never see raw merchant HTML. They receive:
- Typed, schema-validated fields only
- Character-set restricted text (titles ≤80 chars)
- Fixed vocabulary features from allowlist
- Flagged spans removed completely
- Generic notices instead of raw detection results

### 4. Policy Ratchet (Verdict Hardening)
Detection results can only **tighten** the verdict:
- Clear content → ALLOW
- Flagged content → CHALLENGE (user confirms) or notify
- Gray (unresolved) → CHALLENGE
- Hard constraint violations → BLOCK

Soft deviations (price drift, quantity over limit, SKU not viewed) also trigger CHALLENGE.

## How We Built It

### Stack
- **Backend:** Python 3.11+, FastAPI, Pydantic v2
- **Crypto:** Ed25519 signing (cryptography library), canonical JSON
- **PayPal:** Orders API v2 (sandbox mode), in-memory fake client for testing
- **Detection:** scikit-learn (TF-IDF, kNN), optional ONNX Runtime (DeBERTa)
- **Storage:** SQLite (nonces, audit log, signatures)
- **Frontend:** React + TypeScript, Vite, AG Grid Community, Recharts
- **Deployment:** Docker, docker-compose, Render-compatible

### Architecture
Four trust zones with boundary enforcement:
1. **Untrusted Zone** (red): Raw merchant content
2. **Screening Zone** (orange): Ingestion, detection, sanitization
3. **Agent Zone** (blue): Protected agents with structured views only
4. **Trusted Zone** (green): Policy engine, mandate validation, PayPal API

### Key Implementation Details

**Determinism:**
- All randomness uses configurable seed
- Canonical JSON serialization for signing
- Reproducible test results

**Fail Closed:**
- Any exception, timeout, or unscanned content → no view, no order
- Security invariants enforced with automated tests

**Cross-Merchant Immunization:**
- Attack signatures shared via MinHash
- Provisional → global promotion after K merchants see same pattern
- New variants caught by similarity before any agent interaction

**Red Team Harness:**
- Evolutionary attack generation
- UCB1 bandit selects mutation operators
- Fitness: bypass detector AND hijack naive agent (oracle check)
- Retrain on discoveries, re-evaluate on held-out families

**Audit Trail:**
- Hash-chained log (tamper-evident)
- Every decision recorded with timestamp
- Verification detects modifications

## Challenges We Ran Into

### 1. Balancing Security and Usability
Too strict detection → false positives block legitimate content  
Too loose → attacks slip through

**Solution:** Multi-stage cascade with calibrated thresholds and user challenges for gray band

### 2. Adversarial Robustness
Attackers can obfuscate prompts with zero-width characters, homoglyphs, base64, CSS tricks

**Solution:** Normalization pipeline + decode depth tracking + multiple detection stages

### 3. Performance vs. Accuracy
Deep models (DeBERTa) are slow; simple rules miss novel attacks

**Solution:** Tiered profiles (lite/full) and stacking ensemble for best of both

### 4. Zero External Dependencies
System must work for judges without PayPal/LLM credentials

**Solution:** Fake/mock mode as default (in-memory PayPal, deterministic LLM responses)

### 5. Autonomous Build
Entire project built by AI agent following specification

**Solution:** Detailed build spec with acceptance criteria, fallbacks, and honesty rules

## Accomplishments That We're Proud Of

✅ **Works offline by default** - Zero external services required for testing  
✅ **Cryptographic guarantees** - Signed mandates enforce hard constraints  
✅ **Defense-in-depth** - Multiple independent security layers  
✅ **Deterministic testing** - Reproducible results with seeded randomness  
✅ **Security invariants** - Automated tests verify 9 core security properties  
✅ **Red team validated** - Evolutionary attack generation hardens detection  
✅ **Production-ready architecture** - Audit logs, signature sharing, appeal system  
✅ **Open source** - Apache 2.0 licensed, well-documented  
✅ **PayPal integration** - Real sandbox API plus fake mode for testing  

## What We Learned

### Technical Insights
- **Prompt injection is harder to detect than expected** - Simple patterns catch obvious attempts, but adversarial obfuscation requires multiple detection stages
- **Cryptographic enforcement is essential** - ML detection will always have false negatives; mandates provide a security backstop
- **Fail-closed design is critical** - Any uncertainty must default to blocking or challenging, never silent allowance
- **Cross-merchant signatures work** - Attack variants seen on one merchant get blocked on others before agent interaction

### AI Safety Principles
- **Never trust external content** - Treat all merchant input as adversarial
- **Isolate privileged operations** - Agent tools must be narrow and validated
- **Make security visible** - Users should understand when challenges occur and why
- **Design for auditability** - Hash-chained logs enable forensic analysis

## What's Next for Clean Room

### Short-Term Enhancements
- **Multilingual support** - Detection models beyond English
- **Image-based injection** - Detect prompts embedded in product images via OCR + analysis
- **Real-time collaboration** - Signature sharing across user community
- **Mobile app** - iOS/Android clients for on-the-go shopping

### Long-Term Vision
- **Multi-marketplace support** - Extend to eBay, Amazon, Etsy, etc.
- **Federated learning** - Train detection models across merchants without sharing raw data
- **Hardware wallet integration** - Cold storage for signing keys
- **Regulatory compliance** - GDPR, CCPA, PSD2 alignment
- **Enterprise deployment** - Corporate purchasing agents with company mandates

### Research Directions
- **Adversarial robustness** - Certified defenses against prompt injection
- **Interpretability** - Explainable detection for user trust
- **Privacy-preserving telemetry** - Zero-knowledge proofs for attack signatures
- **Formal verification** - Machine-checked security properties

## Built With
- Python
- FastAPI
- React
- TypeScript
- PayPal API
- Ed25519 Cryptography
- ONNX Runtime
- scikit-learn
- Docker
- SQLite

## Try It Out

### GitHub Repository
[Insert your GitHub URL here]

### Live Demo (Optional)
[Insert Render deployment URL if available]

### Quick Start
```bash
git clone <your-repo-url>
cd clean-room
make setup
make web
make dev
# Visit http://localhost:8000
```

### Demo Video
[Insert YouTube URL here - under 3:00]

## Team
[Insert team member names/roles if applicable]

Built for the **PayPal AI Hackathon 2026**

---

## Additional Information

### Licensing
Apache License 2.0 - See LICENSE and THIRD_PARTY.md

### Documentation
- Architecture: docs/ARCHITECTURE.md
- Build Spec: CLEAN_ROOM_BUILD_SPEC.md
- API Docs: Available at /docs endpoint when running

### Security Invariants Tested
1. No order without ALLOW or approved CHALLENGE
2. All order fields match mandate
3. Detection can only tighten verdict (ratchet)
4. Protected agent receives no raw untrusted text
5. Signing key unreachable from processing code
6. Fail closed on exceptions/timeouts
7. Hash chain verifies and detects tampering
8. Merchants never see scores/rules/model names
9. Telemetry contains no buyer PII

### Performance Metrics
(Generated by `make eval` - see reports/ directory)
- Detection accuracy: [Insert from reports/]
- Scan latency P95: [Insert from reports/]
- Red team bypass rate: [Insert from reports/]
- Test coverage: [Insert from reports/]

---

## Judging Criteria Alignment

### Technological Implementation (20%)
- Multi-stage ML pipeline with ensemble stacking
- Cryptographic signing and verification
- Real PayPal sandbox integration
- Production-grade architecture (audit logs, docker, tests)

### Design (20%)
- Clean separation of trust zones
- Intuitive UI (React + TypeScript)
- Fail-closed security by default
- Graceful degradation (fake/lite modes)

### Potential Impact (20%)
- Solves critical security problem for emerging AI agents
- Applicable to any e-commerce platform
- Protects vulnerable users from financial fraud
- Enables safe AI-assisted shopping at scale

### Innovation (20%)
- Novel combination of cryptographic mandates + ML detection
- Cross-merchant attack signature sharing
- Red team evolutionary harness
- Defense-in-depth with ratchet logic

### Presentation (20%)
- Comprehensive documentation
- Clear architecture diagrams
- Demo video showing attack scenarios
- Open source with Apache 2.0 license

---

**Submission Date:** [Insert date]  
**Last Updated:** November 2, 2026
