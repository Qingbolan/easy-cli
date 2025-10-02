from typing import Optional, List, Dict, Iterator
from openai import OpenAI


class AIClient:
    """
    Universal AI Client - Uses OpenAI SDK, supports any compatible API

    Supports:
        - OpenAI API
        - Azure OpenAI
        - Local models (e.g. Ollama, LM Studio)
        - Any OpenAI-compatible API

    Example:
        >>> # OpenAI
        >>> client = UniversalAIClient(api_key="sk-xxx")
        >>>
        >>> # Local Ollama
        >>> client = UniversalAIClient(
        >>>     base_url="http://localhost:11434/v1",
        >>>     api_key="ollama"
        >>> )
        >>>
        >>> # Azure OpenAI
        >>> client = UniversalAIClient(
        >>>     base_url="https://xxx.openai.azure.com/openai/deployments/xxx",
        >>>     api_key="your-key"
        >>> )
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: str = "gpt-3.5-turbo",
        max_tokens: int = 4096,
        timeout: float = 60.0,
    ):
        """
        Initialize client

        Args:
            api_key: API key (can be any value for some local APIs)
            base_url: API base URL (None uses official OpenAI)
            model: Model name
            max_tokens: Maximum token count
            timeout: Request timeout
        """
        self.model = model
        self.max_tokens = max_tokens

        # Create OpenAI client
        client_kwargs = {
            "api_key": api_key or "dummy-key",
            "timeout": timeout,
        }
        
        if base_url:
            client_kwargs["base_url"] = base_url
        
        self.client = OpenAI(**client_kwargs)
    
    def chat(
        self,
        message: str,
        system: Optional[str] = None,
        conversation_history: Optional[List[Dict]] = None,
        temperature: float = 0.7,
    ) -> str:
        """
        Send message and get complete response

        Args:
            message: User message
            system: System prompt
            conversation_history: Conversation history
            temperature: Temperature parameter

        Returns:
            Complete response text
        """
        messages = []

        # Add system message
        if system:
            messages.append({"role": "system", "content": system})

        # Add history messages
        if conversation_history:
            messages.extend(conversation_history)

        # Add current message
        messages.append({"role": "user", "content": message})
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=self.max_tokens,
                temperature=temperature,
            )
            return response.choices[0].message.content
        
        except Exception as e:
            raise RuntimeError(f"Chat request failed: {e}")
    
    def chat_stream(
        self,
        message: str,
        system: Optional[str] = None,
        conversation_history: Optional[List[Dict]] = None,
        temperature: float = 0.7,
    ) -> Iterator[str]:
        """
        Stream message sending

        Args:
            message: User message
            system: System prompt
            conversation_history: Conversation history
            temperature: Temperature parameter

        Yields:
            Text chunks
        """
        messages = []
        
        if system:
            messages.append({"role": "system", "content": system})
        
        if conversation_history:
            messages.extend(conversation_history)
        
        messages.append({"role": "user", "content": message})
        
        try:
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=self.max_tokens,
                temperature=temperature,
                stream=True,
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content
        
        except Exception as e:
            raise RuntimeError(f"Streaming request failed: {e}")
    
    @classmethod
    def from_config(cls, config: Dict) -> 'AIClient':
        """
        Create client from configuration dictionary

        Example:
            >>> config = {
            >>>     "api_key": "sk-xxx",
            >>>     "base_url": "http://localhost:11434/v1",
            >>>     "model": "llama2",
            >>> }
            >>> client = UniversalAIClient.from_config(config)
        """
        return cls(
            api_key=config.get("api_key"),
            base_url=config.get("base_url"),
            model=config.get("model", "gpt-3.5-turbo"),
            max_tokens=config.get("max_tokens", 4096),
            timeout=config.get("timeout", 60.0),
        )


# Preset configurations
PRESET_CONFIGS = {
    "openai": {
        "name": "OpenAI",
        "base_url": None,
        "models": ["gpt-4", "gpt-4o", "gpt-5"],
    },
    "ollama": {
        "name": "Ollama (Local)",
        "base_url": "http://localhost:11434/v1",
        "api_key": "ollama",
        "models": ["llama2", "mistral", "codellama"],
    },
    "lm-studio": {
        "name": "LM Studio (Local)",
        "base_url": "http://localhost:1234/v1",
        "api_key": "lm-studio",
        "models": ["local-model"],
    },
    "azure": {
        "name": "Azure OpenAI",
        "base_url": "https://YOUR_RESOURCE.openai.azure.com/openai/deployments/YOUR_DEPLOYMENT",
        "models": ["gpt-4", "gpt-35-turbo"],
    },
}


def get_preset_config(preset: str) -> Dict:
    """
    Get preset configuration

    Args:
        preset: Preset name (openai, ollama, lm-studio, azure)

    Returns:
        Configuration dictionary
    """
    if preset not in PRESET_CONFIGS:
        available = ", ".join(PRESET_CONFIGS.keys())
        raise ValueError(f"Unknown preset: {preset}. Available: {available}")
    
    return PRESET_CONFIGS[preset].copy()


__all__ = [
    'AIClient',
    'PRESET_CONFIGS',
    'get_preset_config',
]
