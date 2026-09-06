import openai
from openai import AsyncOpenAI
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential_jitter
from rag_bot.config import settings

client = AsyncOpenAI(
    api_key=settings.deepseek_api_key,
    base_url="https://api.deepseek.com"
)

@retry(
    retry=retry_if_exception_type(openai.RateLimitError),
    wait=wait_exponential_jitter(initial=1, max=60, exp_base=2, jitter=1),
    stop=stop_after_attempt(5)
)
async def generate_answer(query: str, context: str) -> str:
    system_prompt = (
        "You are an AI assistant. Answer the user's question based ONLY on the following context. "
        "If the context doesn't contain the answer, say you don't know.\n\n"
        f"Context:\n{context}"
    )

    response = await client.chat.completions.create(
        model="deepseek-v4-flash",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query}
        ],
        temperature=0.0
    )

    return response.choices[0].message.content
