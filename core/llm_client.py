"""Thin LLM wrapper so agents don't care which provider is configured."""
from __future__ import annotations
from functools import lru_cache

from config.settings import get_settings


class LLMClient:
    def __init__(self) -> None:
        s = get_settings()
        self._model = s.llm_model
        if s.anthropic_api_key:
            from langchain_anthropic import ChatAnthropic
            self._client = ChatAnthropic(
                model=s.llm_model,
                api_key=s.anthropic_api_key,
                temperature=0,
            )
        elif s.openai_api_key:
            from langchain_openai import ChatOpenAI
            self._client = ChatOpenAI(
                model="gpt-4o",
                api_key=s.openai_api_key,
                temperature=0,
            )
        else:
            raise RuntimeError("No LLM API key configured (ANTHROPIC or OPENAI).")

    def complete(self, system: str, user: str) -> str:
        from langchain_core.messages import SystemMessage, HumanMessage
        resp = self._client.invoke(
            [SystemMessage(content=system), HumanMessage(content=user)]
        )
        return resp.content if isinstance(resp.content, str) else str(resp.content)


@lru_cache
def get_llm() -> LLMClient:
    return LLMClient()
