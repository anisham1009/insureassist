from rag import get_relevant_context


question = "Does HealthSecure Plus cover maternity?"


print("\nCustomer:")
print(question)

print("\nRetrieved policy context:")
print("=" * 60)

context = get_relevant_context(
    question,
    n_results=3,
)

print(context)

print("=" * 60)