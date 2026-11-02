"""LLM client with mock and openai_compat modes."""
from typing import Optional, Literal
import httpx


class LLMClient:
    """LLM client interface."""
    
    def __init__(
        self,
        mode: Literal["mock", "openai_compat"] = "mock",
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        seed: int = 1337,
    ):
        """Initialize LLM client.
        
        Args:
            mode: Client mode
            base_url: API base URL for openai_compat mode
            api_key: API key for openai_compat mode
            model: Model name for openai_compat mode
            seed: Random seed for determinism
        """
        self.mode = mode
        self.base_url = base_url
        self.api_key = api_key
        self.model = model
        self.seed = seed
        self._counter = 0
    
    async def complete(
        self,
        prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.0,
        stop: Optional[list[str]] = None,
    ) -> str:
        """Generate completion.
        
        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            stop: Stop sequences
            
        Returns:
            Generated text
        """
        if self.mode == "mock":
            return self._mock_complete(prompt)
        elif self.mode == "openai_compat":
            return await self._openai_complete(
                prompt, max_tokens, temperature, stop
            )
        else:
            raise ValueError(f"Unknown mode: {self.mode}")
    
    def _mock_complete(self, prompt: str) -> str:
        """Deterministic mock completion.
        
        Args:
            prompt: Input prompt
            
        Returns:
            Mock response
        """
        self._counter += 1
        
        # Simple keyword-based responses
        if "search" in prompt.lower():
            return '{"action": "search_view", "query": "usb-c charger"}'
        elif "order" in prompt.lower() or "purchase" in prompt.lower():
            return '{"action": "propose_order", "sku": "USBC-FAST-001", "qty": 1}'
        elif "attack" in prompt.lower() or "injection" in prompt.lower():
            return "attack"
        elif "benign" in prompt.lower() or "safe" in prompt.lower():
            return "benign"
        else:
            return "unsure"
    
    async def _openai_complete(
        self,
        prompt: str,
        max_tokens: int,
        temperature: float,
        stop: Optional[list[str]],
    ) -> str:
        """OpenAI-compatible completion.
        
        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens
            temperature: Sampling temperature
            stop: Stop sequences
            
        Returns:
            Generated text
        """
        if not self.base_url or not self.model:
            raise ValueError("base_url and model required for openai_compat mode")
        
        async with httpx.AsyncClient() as client:
            headers = {"Content-Type": "application/json"}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
            
            body = {
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": max_tokens,
                "temperature": temperature,
                "seed": self.seed,
            }
            
            if stop:
                body["stop"] = stop
            
            response = await client.post(
                f"{self.base_url}/v1/chat/completions",
                headers=headers,
                json=body,
                timeout=30.0,
            )
            
            response.raise_for_status()
            data = response.json()
            
            return data["choices"][0]["message"]["content"]
