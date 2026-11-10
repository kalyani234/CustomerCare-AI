from chatbot.llm import generate_response


def start_chatbot():

    print("Welcome to CustomerCare AI!")
    print("Type 'exit' to end the conversation.")

    while True:

        question = input("\nCustomer: ")

        if question.lower() == "exit":
            print("CustomerCare AI: Thank you for contacting us. Goodbye!")
            break

        try:
            answer = generate_response(question)
            print("\nCustomerCare AI:", answer)

        except Exception as error:
            print("\nCustomerCare AI: Sorry, something went wrong.")
            print("Error details:", error)


if __name__ == "__main__":
    start_chatbot()