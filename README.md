# Clean Room

**A trust layer for AI shopping agents that stops hostile merchant content from hijacking transactions.**

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

## Overview

Clean Room protects AI shopping agents from prompt injection attacks embedded in merchant content (product listings, reviews, images, invoices). Even when detection fails, signed mandates ensure money cannot leave the user's approved limits.

**Built for:** PayPal AI Hackathon 2026  
**Demo Video:** [Coming soon - See HUMAN_TODO.md]  
**Live Demo:** [Coming soon - See HUMAN_TODO.md]

## The Problem

AI shopping agents read merchant content to help users buy products. Malicious merchants can inject prompts into their listings to:
- Change shipping addresses
- Swap to different merchants (payee swap)
- Add extra items
- Inflate prices
- Exfiltrate user data

Traditional content filtering isn't enough because:
1. LLMs are vulnerable to sophisticated prompt injections
2. New attack vectors emerge constantly
3. False positives block legitimate content
4. Merchants can obfuscate attacks

## The Solution: Defense in Depth

Clean Room implements **four security layers**:

### 1. Signed Mandates (Cryptographic Enforcement)
Users create Ed25519-signed mandates that specify:
- Maximum total amount
- Allowed merchants
- Exact shipping address
- Item quantity limits
- Single-use nonce

**Invariant:** Money cannot leave these constraints, even if all other layers fail.

### 2. Detection Cascade (Multi-Stage Analysis)
```
Raw Content → Rules → ML Classifier → kNN Signatures → Stacking → Band
                                                                    ↓
                            Gray Band → Quarantined LLM Judge → Final Band
```

- **Rules:** Fast pattern matching for known attacks
- **Classifier:** ONNX DeBERTa model (Apache-2.0)
- **kNN:** Similarity search against known attack signatures
- **Stacking:** Calibrated ensemble
- **Judge:** Isolated LLM with no tools, enum-only output

### 3. Sanitization (Structured Views)
Protected agents never see raw merchant content. They receive:
- Typed, schema-validated fields only
- Character-set restricted text (80 chars max)
- Fixed vocabulary features
- Flagged spans removed
- Generic notices instead of raw detections

### 4. Policy Ratchet (Verdict Hardening)
Detection results can only **tighten** the verdict:
- Clear → ALLOW
- Flagged → CHALLENGE or notify
- Gray (unresolved) → CHALLENGE

Soft deviations (price drift, quantity over limit) also trigger CHALLENGE.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│  UNTRUSTED ZONE: Merchant Content (HTML, reviews, images, JSON) │
└────────────────────┬────────────────────────────────────────────┘
                     ↓
           ┌─────────────────────┐
           │  SCREENING ZONE     │
           │  • Ingest & render  │
           │  • Normalize        │
           │  • Detect cascade   │
           │  • Sanitize         │
           └─────────┬───────────┘
                     ↓
            ┌────────────────┐
            │  AGENT ZONE    │
            │  StructuredView│
            └────────┬───────┘
                     ↓
         ┌──────────────────────┐
         │  TRUSTED ZONE        │
         │  • Policy engine     │
         │  • Mandate check     │
         │  • PayPal API call   │
         └──────────────────────┘
```

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for detailed diagrams.

## Key Features

- ✅ **Works offline by default** (fake PayPal, mock LLM, lite detector)
- ✅ **Deterministic testing** (seeded randomness, reproducible)
- ✅ **Zero external dependencies required** (optional upgrades available)
- ✅ **Security invariants with tests** (see tests/invariants/)
- ✅ **Hash-chained audit log** (tamper-evident)
- ✅ **Cross-merchant immunization** (signature sharing)
- ✅ **Red team hardening loop** (evolutionary attack generation)
- ✅ **Merchant appeal system** (state machine for false positives)

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+ (for web UI)
- Optional: PayPal sandbox account, LLM API, Tesseract OCR

### Installation

```bash
# Clone repository
git clone <your-repo-url>
cd clean-room

# Install Python dependencies (base mode)
make setup

# Optional: Install full detector profile
pip install -e '.[full]'

# Build web UI
make web

# Copy environment template
cp .env.example .env
# Edit .env if you have PayPal/LLM credentials (optional)
```

### Run

```bash
# Start backend (fake mode, works immediately)
make dev

# In another terminal: Run demo scenario
make demo

# Run tests
make test
```

The system runs in **fallback mode** by default:
- `PAYPAL_MODE=fake` (in-memory orders)
- `LLM_MODE=mock` (deterministic responses)
- `DETECTOR_PROFILE=lite` (rules + TF-IDF + hashing kNN)

This requires **zero external services** and all tests pass.

### Optional: Real Sandbox Mode

See [HUMAN_TODO.md](HUMAN_TODO.md) for step-by-step instructions to enable:
- Real PayPal sandbox integration (H1, H2, H3)
- Real LLM endpoints (H4)
- Full ML models (H6)
- OCR with Tesseract (H7)

## Project Structure

```
clean-room/
├── src/cleanroom/          # Main package
│   ├── models/            # Data contracts (Money, Mandate, Orders)
│   ├── crypto/            # Ed25519 signing, canonical JSON
│   ├── paypal/            # PayPal client (fake, real, MCP)
│   ├── policy/            # Policy engine, mandate checks
│   ├── marketplace/       # Simulated marketplace
│   ├── ingest/            # Content ingestion, normalization
│   ├── detect/            # Detection cascade
│   ├── sanitize/          # View construction
│   ├── isolation/         # Honeypots, canaries, provenance
│   ├── llm/               # LLM client (mock, openai_compat)
│   ├── agents/            # Naive and protected agents
│   ├── gateway/           # Orchestrator, sessions, challenges
│   ├── telemetry/         # Audit log, signatures, appeals
│   ├── redteam/           # Attack generation
│   ├── eval/              # Evaluation harness, metrics
│   └── api/               # FastAPI application
├── web/                   # React TypeScript UI
├── tests/                 # Test suite
│   ├── unit/             # Unit tests
│   ├── property/         # Property-based tests
│   ├── invariants/       # Security invariant tests
│   ├── integration/      # Integration tests
│   └── e2e/              # End-to-end tests
├── fixtures/             # Test data (catalog, scenarios)
├── scripts/              # Utility scripts
├── docs/                 # Documentation
└── reports/              # Generated metrics (committed)
```

## Testing

```bash
# All tests
make test

# Fast tests only (no e2e)
make test-fast

# Security invariants
make verify-invariants

# Lint
make lint
```

## Development

```bash
# Run backend with auto-reload
make dev

# Run frontend dev server
cd web && npm run dev

# Run red team generation
make redteam

# Run full evaluation
make eval

# Generate reports
make report
```

## Deployment

### Docker

```bash
# Build image
make docker

# Or use docker-compose
make docker-compose
```

### Render (Free Tier)

See [HUMAN_TODO.md](HUMAN_TODO.md) H9 for deployment instructions.  
**Note:** Use `DETECTOR_PROFILE=lite` on free tier (memory limits).

## Evaluation Results

*Generated by make eval - reports/ directory*

(Reports will be generated during evaluation phase)

## Security Invariants

All invariants are tested in `tests/invariants/`:

1. **I-1:** No PayPal order created unless verdict is ALLOW or approved CHALLENGE
2. **I-2:** All order fields match mandate constraints
3. **I-3:** Detection can only tighten verdict (ratchet)
4. **I-4:** Protected agent receives no raw UNTRUSTED_MERCHANT text
5. **I-5:** Signing key unreachable from gateway/ingest/detect code
6. **I-6:** Fail closed on exceptions/timeouts
7. **I-7:** Hash chain verifies and detects tampering
8. **I-8:** Merchants never see scores, rules, or model names
9. **I-9:** Telemetry contains no buyer PII (salted hashes only)

## License

This project is licensed under the Apache License 2.0 - see [LICENSE](LICENSE) for details.

Third-party dependencies and models are listed in [THIRD_PARTY.md](THIRD_PARTY.md).

## Contributing

This project was built for the PayPal AI Hackathon 2026. For issues or questions, please open a GitHub issue.

## Acknowledgments

- PayPal Developer Platform (sandbox)
- ProtectAI DeBERTa Prompt Injection Model (Apache-2.0)
- FastAPI, Pydantic, ONNX Runtime
- React, TypeScript, AG Grid Community, Recharts

## Citation

```bibtex
@software{cleanroom2026,
  title = {Clean Room: Trust Layer for AI Shopping Agents},
  author = {Clean Room Contributors},
  year = {2026},
  license = {Apache-2.0},
  url = {<your-repo-url>}
}
```

---

**Status:** 🚧 Built by autonomous agent per CLEAN_ROOM_BUILD_SPEC.md  
**Last Updated:** November 2, 2026  
**Submission Deadline:** November 12, 2026, 12:00 PM Pacific
