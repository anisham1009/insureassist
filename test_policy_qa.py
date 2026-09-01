from policy_qa import answer_policy_question


questions = [
    "Does HealthSecure Plus cover maternity?",
    "What is the premium of HealthSecure Plus?",
    "How much coverage does HealthSecure Plus provide?",
    "What is the waiting period?",
]


for question in questions:

    print("=" * 70)
    print("CUSTOMER:")
    print(question)

    print("\nINSUREASSIST:")

    answer = answer_policy_question(question)

    print(answer)

    print()