from rag import search_policies


query = "Does the policy cover maternity?"


results = search_policies(
    query,
    n_results=3
)


print("\nSearch results:\n")


for i, document in enumerate(
    results["documents"][0]
):

    print("=" * 60)

    print(
        f"Result {i + 1}"
    )

    print(
        f"Source: {results['metadatas'][0][i]['source']}"
    )

    print("\nDocument:")

    print(document)