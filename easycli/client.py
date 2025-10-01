"""
AI Client module for interacting with Anthropic's LLM API.
"""

from typing import AsyncIterator, Optional, Dict, List
import anthropic
import time

from .logger import ModernLogger


class AIClient:
    """
    A wrapper around Anthropic's LLM API with streaming support.
    
    Example:
        >>> client = AIClient(api_key="your-key")
        >>> async for chunk in client.chat_stream("Hello!"):
        >>>     print(chunk, end="", flush=True)
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "claude-sonnet-4-20250514",
        max_tokens: int = 4096,
        logger: Optional[ModernLogger] = None,
    ):
        """
        Initialize the AI client.
        
        Args:
            api_key: Anthropic API key (or set LLM_API_KEY env var)
            model: LLM model to use
            max_tokens: Maximum tokens in response
            logger: Optional ModernLogger instance
        """
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model
        self.max_tokens = max_tokens
        self.logger = logger or ModernLogger(name="ai-client", level="info")
        
    def chat(
        self,
        message: str,
        system: Optional[str] = None,
        conversation_history: Optional[List[Dict]] = None,
    ) -> str:
        """
        Send a message and get a complete response.
        
        Args:
            message: User message
            system: Optional system prompt
            conversation_history: Optional list of previous messages
            
        Returns:
            Complete response text
        """
        messages = conversation_history or []
        messages.append({"role": "user", "content": message})
        
        try:
            kwargs = {
                "model": self.model,
                "max_tokens": self.max_tokens,
                "messages": messages,
            }
            if system:
                kwargs["system"] = system
                
            response = self.client.messages.create(**kwargs)
            return response.content[0].text
            
        except Exception as e:
            self.logger.error(f"API request failed: {e}")
            raise
    
    async def chat_stream(
        self,
        message: str,
        system: Optional[str] = None,
        conversation_history: Optional[List[Dict]] = None,
    ) -> AsyncIterator[str]:
        """
        Send a message and stream the response.
        
        Args:
            message: User message
            system: Optional system prompt
            conversation_history: Optional list of previous messages
            
        Yields:
            Text chunks as they arrive
        """
        messages = conversation_history or []
        messages.append({"role": "user", "content": message})
        
        try:
            kwargs = {
                "model": self.model,
                "max_tokens": self.max_tokens,
                "messages": messages,
            }
            if system:
                kwargs["system"] = system
            
            with self.client.messages.stream(**kwargs) as stream:
                for text in stream.text_stream:
                    yield text
                    
        except Exception as e:
            self.logger.error(f"Streaming request failed: {e}")
            raise
    
    def chat_stream_with_logger(
        self,
        message: str,
        system: Optional[str] = None,
        conversation_history: Optional[List[Dict]] = None,
        stream_title: Optional[str] = "LLM Response",
        render_markdown: bool = False,
    ) -> str:
        """
        Send a message and display streaming response with ModernLogger.
        
        Args:
            message: User message
            system: Optional system prompt
            conversation_history: Optional list of previous messages
            stream_title: Title for the stream display (None to disable)
            render_markdown: Whether to render final response as Markdown
            
        Returns:
            Complete response text
        """
        messages = conversation_history or []
        messages.append({"role": "user", "content": message})
        
        try:
            kwargs = {
                "model": self.model,
                "max_tokens": self.max_tokens,
                "messages": messages,
            }
            if system:
                kwargs["system"] = system
            
            full_response = ""
            start_time = time.time()
            
            if stream_title:
                # 使用 ModernLogger 的流式显示
                with self.logger.stream(title=stream_title) as s:
                    with self.client.messages.stream(**kwargs) as stream:
                        for text in stream.text_stream:
                            full_response += text
                            elapsed = time.time() - start_time
                            s.update_text(full_response, elapsed_s=elapsed)
            else:
                # 不使用标题，直接输出
                with self.client.messages.stream(**kwargs) as stream:
                    for text in stream.text_stream:
                        full_response += text
                        self.logger.console.print(text, end="")
            
            # 如果启用 Markdown 渲染，显示最终结果
            if render_markdown and full_response:
                from rich.markdown import Markdown
                self.logger.console.print()
                self.logger.console.print()
                try:
                    md = Markdown(full_response)
                    self.logger.console.print(md)
                except Exception:
                    # Markdown 解析失败，使用纯文本
                    self.logger.console.print(full_response)
            
            return full_response
            
        except Exception as e:
            self.logger.error(f"Streaming request failed: {e}")
            raise
