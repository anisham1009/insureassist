from rag import get_relevant_context
from llm import ask_llm


def answer_with_rag(question: str) -> str:

    # Retrieve relevant policy information
    context = get_relevant_context(
        question,
        n_results=3,
    )

    # Build grounded prompt
    prompt = f"""
You are InsureAssist, an AI assistant that helps
customers understand insurance policies.

Answer the customer's question using ONLY the
policy information provided below.

IMPORTANT RULES:

1. Do not invent policy features.
2. Do not assume information that is not provided.
3. If the answer is not available in the provided
   policy information, clearly say that you don't
   have enough information.
4. Clearly mention the relevant policy name when
   appropriate.
5. Do not make a final purchase decision for the
   customer.
6. Explain the information in simple language.

POLICY INFORMATION:

{context}


CUSTOMER QUESTION:

{question}


Provide a concise and helpful answer.
"""

    # Ask Gemini to generate the final answer
    answer = ask_llm(prompt)

    return answer