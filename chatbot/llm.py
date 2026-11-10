
from groq import Groq

from chatbot.config import GROQ_API_KEY, GROQ_MODEL
from chatbot.prompts import SYSTEM_PROMPT
from chatbot.rag_pipeline import (
    load_documents,
    split_into_chunks,
    retrieve_relevant_chunks
)

MAX_QUESTION_LENGTH = 5000

def validate_api_key(api_key):
    if not api_key:
        raise ValueError(
            "Groq API key is missing. Check your .env file."
        )

validate_api_key(GROQ_API_KEY)

client = Groq(api_key=GROQ_API_KEY)



def generate_response(
    question: str,
    relevant_chunks=None
) -> str:
    """
    Generate a response using Groq.

    If relevant_chunks are supplied, use them directly.
    Otherwise, retrieve relevant company information.
    """
    if not isinstance(question, str):
        raise TypeError("Question must be a string")

    if not question or not question.strip():
        raise ValueError("Question cannot be empty")

    if len(question) > MAX_QUESTION_LENGTH:
        raise ValueError(
            f"Question must not exceed {MAX_QUESTION_LENGTH} characters"
        )

    # Step 1: Retrieve context only if it was not supplied
    if relevant_chunks is None:
        documents = load_documents()
        chunks = split_into_chunks(documents)

        relevant_chunks = retrieve_relevant_chunks(
            question,
            chunks,
            top_k=3
        )

    # Step 2: Combine retrieved information
    context = "\n\n".join(relevant_chunks)

    if not context:
        context = "No relevant company information was found."

    # Step 3: Add context to the system prompt
    system_message = SYSTEM_PROMPT.format(
        context=context
    )
    print("SYSTEM MESSAGE:", system_message)
    print("USER QUESTION:", question)
    
    # Step 4: Send context and question to Groq
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {
                "role": "system",
                "content": system_message
            },
            {
                "role": "user",
                "content": question
            }
        ],
        temperature=0.2
    )

    if not response.choices:
        raise ValueError("API returned no choices")

    answer = response.choices[0].message.content

    if answer is None or not answer.strip():
        raise ValueError("API returned empty content")

    return answer

