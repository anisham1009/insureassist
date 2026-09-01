from conversation import ConversationManager


conversation = ConversationManager()


messages = [
    "Does HealthSecure Plus cover maternity?",
    "What is the waiting period?",
    "What is the premium?",
    "How much coverage does it provide?",
    "What about the deductible?",
]


for message in messages:

    print("=" * 70)
    print("CUSTOMER:")
    print(message)

    answer = conversation.process_message(message)

    print("\nINSUREASSIST:")
    print(answer)
    print()