
from recommendation import (
    recommend_policies,
    format_recommendations,
)


# ---------------------------------------------------------
# Synthetic customer profile
# ---------------------------------------------------------

customer = {

    "age": 35,

    "budget": 15000,

    "required_coverage": 1000000,

    "maternity_required": True,

    "max_deductible": 5000,

    "pre_existing_disease": False,

    "max_waiting_period_years": 3,
}


# ---------------------------------------------------------
# Generate recommendations
# ---------------------------------------------------------

recommendations = recommend_policies(
    customer,
    top_n=3
)


# ---------------------------------------------------------
# Display results
# ---------------------------------------------------------

print("\n")
print("=" * 70)
print("INSUREASSIST POLICY RECOMMENDATIONS")
print("=" * 70)


print("\nCustomer Profile:")
print(customer)


print("\nRecommended Policies:")
print("-" * 70)


print(
    format_recommendations(
        recommendations
    )
)


print("\n")
print("=" * 70)
