from rag_llm import answer_with_rag


question = "Does HealthSecure Plus cover maternity?"


print("\nCustomer:")
print(question)


answer = answer_with_rag(question)


print("\nInsureAssist:")
print(answer)