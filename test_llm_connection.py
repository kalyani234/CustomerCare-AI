
from chatbot.llm import generate_response

question = "1. What is software testing? 2. What is automation testing?"

answer = generate_response(question)

print("\nCustomer:", question)
print("\nCustomerCare AI:", answer)
