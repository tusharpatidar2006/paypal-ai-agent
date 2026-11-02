"""Configuration management with validation."""
import os
import sys
from typing import Literal
from pydantic_settings import BaseSettings
from pydantic import Field, field_validator


class Config(BaseSettings):
    """Application configuration with environment variable support."""

    # Modes
    paypal_mode: Literal["fake", "sandbox"] = "fake"
    llm_mode: Literal["mock", "openai_compat"] = "mock"
    detector_profile: Literal["lite", "full"] = "lite"
    render_mode: Literal["static", "playwright"] = "static"
    approval_mode: Literal["simulated", "manual", "playwright"] = "simulated"
    seed: int = 1337

    # PayPal sandbox
    paypal_client_id: str = ""
    paypal_client_secret: str = ""
    paypal_alt_client_id: str = ""
    paypal_alt_client_secret: str = ""
    paypal_base_url: str = "https://api-m.sandbox.paypal.com"
    paypal_return_url: str = "http://localhost:8000/paypal/return"
    paypal_cancel_url: str = "http://localhost:8000/paypal/cancel"

    # LLM
    llm_base_url: str = ""
    llm_api_key: str = ""
    llm_model: str = ""

    # Policy and detection
    flagged_action: Literal["notify", "challenge"] = "notify"
    snapshot_ttl_s: int = 900
    mandate_ttl_s: int = 900
    signature_promote_k: int = 2
    signature_provisional_ttl_s: int = 86400
    telemetry_salt: str = "change-me-locally"
    max_page_bytes: int = 1_500_000
    scan_timeout_s: int = 8
    judge_timeout_s: int = 6

    # Development
    allow_fallback: bool = True

    class Config:
        env_file = ".env"
        case_sensitive = False

    def validate_and_fallback(self) -> None:
        """Validate configuration and apply fallbacks if needed."""
        # PayPal validation
        if self.paypal_mode == "sandbox":
            if not self.paypal_client_id or not self.paypal_client_secret:
                self._handle_missing_creds("PayPal sandbox credentials")
            if "sandbox" not in self.paypal_base_url.lower():
                print(
                    "ERROR: PAYPAL_MODE=sandbox requires sandbox base URL. "
                    f"Got: {self.paypal_base_url}",
                    file=sys.stderr,
                )
                if self.allow_fallback:
                    print("Falling back to PAYPAL_MODE=fake", file=sys.stderr)
                    self.paypal_mode = "fake"
                else:
                    sys.exit(1)

        # LLM validation
        if self.llm_mode == "openai_compat":
            if not all([self.llm_base_url, self.llm_api_key, self.llm_model]):
                self._handle_missing_creds("LLM configuration")

        # Detector profile validation
        if self.detector_profile == "full":
            try:
                import onnxruntime  # noqa: F401
            except ImportError:
                print(
                    "WARNING: DETECTOR_PROFILE=full requires onnxruntime. "
                    "Install with: pip install -e '.[full]'",
                    file=sys.stderr,
                )
                if self.allow_fallback:
                    print("Falling back to DETECTOR_PROFILE=lite", file=sys.stderr)
                    self.detector_profile = "lite"
                else:
                    sys.exit(1)

    def _handle_missing_creds(self, what: str) -> None:
        """Handle missing credentials with fallback."""
        print(f"ERROR: {what} missing", file=sys.stderr)
        if self.allow_fallback:
            print("Falling back to mock/fake mode", file=sys.stderr)
            if "PayPal" in what:
                self.paypal_mode = "fake"
            elif "LLM" in what:
                self.llm_mode = "mock"
        else:
            sys.exit(1)


# Global config instance
config = Config()
config.validate_and_fallback()
