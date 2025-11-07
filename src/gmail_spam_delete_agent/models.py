from typing import Optional

from langchain_google_genai import ChatGoogleGenerativeAI


def get_gemini_chat(model: str = "gemini-2.5-flash", temperature: float = 1) -> ChatGoogleGenerativeAI:
	"""Return a configured ChatGoogleGenerativeAI model.

	Requires environment variable GOOGLE_API_KEY to be set.
	"""
	return ChatGoogleGenerativeAI(model=model, temperature=temperature)


def quick_sanity_prompt(prompt: str = "Say hello") -> str:
	"""Run a minimal sanity prompt against Gemini and return the text output."""
	llm = get_gemini_chat()
	resp = llm.invoke(prompt)
	return resp.content if hasattr(resp, "content") else str(resp)


