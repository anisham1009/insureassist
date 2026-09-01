
from pathlib import Path
import re

import pandas as pd


# =========================================================
# Project paths
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent

PRODUCT_FILE = BASE_DIR / "data" / "insurance_products.csv"


# =========================================================
# Load insurance products
# =========================================================

def load_products():

    if not PRODUCT_FILE.exists():
        raise FileNotFoundError(
            f"Insurance product file not found: {PRODUCT_FILE}"
        )

    products = pd.read_csv(PRODUCT_FILE)

    return products


# =========================================================
# Convert deductible to numeric value
# =========================================================

def parse_deductible(value):

    text = str(value).strip().lower()

    if text in [
        "no deductible",
        "none",
        "zero",
        "0"
    ]:
        return 0.0

    # Remove currency symbols and commas
    text = text.replace("₹", "")
    text = text.replace(",", "")

    match = re.search(
        r"\d+(?:\.\d+)?",
        text
    )

    if match:
        return float(match.group())

    # Unknown deductible
    return 999999999.0


# =========================================================
# Convert waiting period to years
# =========================================================

def parse_waiting_period(value):

    text = str(value).strip().lower()

    match = re.search(
        r"(\d+(?:\.\d+)?)\s*"
        r"(day|days|month|months|year|years)",
        text
    )

    if not match:
        return None

    number = float(match.group(1))
    unit = match.group(2)

    if unit in ["day", "days"]:

        return number / 365

    elif unit in ["month", "months"]:

        return number / 12

    elif unit in ["year", "years"]:

        return number

    return None


# =========================================================
# Calculate policy score
# =========================================================

def calculate_policy_score(
    policy,
    customer
):

    score = 0

    reasons = []


    # -----------------------------------------------------
    # 1. Budget
    # -----------------------------------------------------

    annual_premium = float(
        policy["annual_premium"]
    )

    budget = float(
        customer["budget"]
    )

    if annual_premium <= budget:

        score += 25

        reasons.append(
            "The annual premium is within "
            "the customer's budget."
        )

    else:

        score -= 20

        reasons.append(
            "The annual premium exceeds "
            "the customer's budget."
        )


    # -----------------------------------------------------
    # 2. Coverage requirement
    # -----------------------------------------------------

    coverage = float(
        policy["coverage_amount"]
    )

    required_coverage = float(
        customer["required_coverage"]
    )

    if coverage >= required_coverage:

        score += 25

        reasons.append(
            "The policy meets or exceeds "
            "the required coverage."
        )

    else:

        score -= 15

        reasons.append(
            "The policy provides less coverage "
            "than requested."
        )


    # -----------------------------------------------------
    # 3. Age eligibility
    # -----------------------------------------------------

    age = int(
        customer["age"]
    )

    age_min = int(
        policy["age_min"]
    )

    age_max = int(
        policy["age_max"]
    )

    if age_min <= age <= age_max:

        score += 20

        reasons.append(
            "The customer is within the "
            "policy's eligibility age range."
        )

    else:

        score -= 100

        reasons.append(
            "The customer is outside the "
            "policy's eligibility age range."
        )


    # -----------------------------------------------------
    # 4. Maternity requirement
    # -----------------------------------------------------

    maternity_required = customer.get(
        "maternity_required",
        False
    )

    maternity_available = str(
        policy["maternity"]
    ).strip().lower()

    maternity_yes = maternity_available in [
        "yes",
        "available",
        "included",
        "true"
    ]

    if maternity_required:

        if maternity_yes:

            score += 20

            reasons.append(
                "Maternity coverage is available."
            )

        else:

            score -= 30

            reasons.append(
                "Maternity coverage is not available."
            )

    else:

        score += 5

        reasons.append(
            "Maternity coverage is not required."
        )


    # -----------------------------------------------------
    # 5. Deductible preference
    # -----------------------------------------------------

    max_deductible = float(
        customer.get(
            "max_deductible",
            999999999
        )
    )

    deductible = parse_deductible(
        policy["deductible"]
    )

    if deductible <= max_deductible:

        score += 10

        reasons.append(
            "The deductible is within "
            "the customer's preferred limit."
        )

    else:

        score -= 10

        reasons.append(
            "The deductible is higher than "
            "the customer's preferred limit."
        )


    # -----------------------------------------------------
    # 6. Pre-existing disease requirement
    # -----------------------------------------------------

    pre_existing_required = customer.get(
        "pre_existing_disease",
        False
    )

    if pre_existing_required:

        pre_existing_info = str(
            policy["pre_existing_disease"]
        ).strip().lower()

        if pre_existing_info not in [
            "no",
            "not covered",
            "excluded"
        ]:

            score += 10

            reasons.append(
                "The policy provides coverage "
                "information for pre-existing diseases."
            )

        else:

            score -= 20

            reasons.append(
                "Pre-existing diseases "
                "are not covered."
            )


    # -----------------------------------------------------
    # 7. Waiting period preference
    # -----------------------------------------------------

    max_waiting_period_years = customer.get(
        "max_waiting_period_years",
        None
    )

    if max_waiting_period_years is not None:

        waiting_period_years = parse_waiting_period(
            policy["waiting_period"]
        )

        if waiting_period_years is not None:

            if (
                waiting_period_years
                <= max_waiting_period_years
            ):

                score += 10

                reasons.append(
                    "The waiting period is within "
                    "the customer's preference."
                )

            else:

                score -= 10

                reasons.append(
                    "The waiting period is longer "
                    "than the customer's preference."
                )


    # -----------------------------------------------------
    # Return result
    # -----------------------------------------------------

    return score, reasons


# =========================================================
# Recommend policies
# =========================================================

def recommend_policies(
    customer,
    top_n=3
):

    products = load_products()

    recommendations = []


    for _, policy in products.iterrows():

        score, reasons = calculate_policy_score(
            policy,
            customer
        )

        recommendations.append(
            {
                "policy_id": policy["policy_id"],
                "policy_name": policy["policy_name"],
                "policy_type": policy["policy_type"],
                "annual_premium": policy["annual_premium"],
                "coverage_amount": policy["coverage_amount"],
                "deductible": policy["deductible"],
                "waiting_period": policy["waiting_period"],
                "score": score,
                "reasons": reasons,
            }
        )


    # -----------------------------------------------------
    # Sort highest score first
    # -----------------------------------------------------

    recommendations.sort(
        key=lambda x: x["score"],
        reverse=True
    )


    return recommendations[:top_n]


# =========================================================
# Format recommendations
# =========================================================

def format_recommendations(
    recommendations
):

    output = []


    for index, policy in enumerate(
        recommendations,
        start=1
    ):

        text = (
            f"{index}. "
            f"{policy['policy_name']} "
            f"({policy['policy_id']})\n"
        )

        text += (
            f"   Annual Premium: "
            f"₹{float(policy['annual_premium']):,.0f}\n"
        )

        text += (
            f"   Coverage: "
            f"₹{float(policy['coverage_amount']):,.0f}\n"
        )

        text += (
            f"   Deductible: "
            f"{policy['deductible']}\n"
        )

        text += (
            f"   Waiting Period: "
            f"{policy['waiting_period']}\n"
        )

        text += (
            f"   Recommendation Score: "
            f"{policy['score']}\n"
        )

        text += "   Reasons:\n"


        for reason in policy["reasons"]:

            text += (
                f"   - {reason}\n"
            )


        output.append(text)


    return "\n".join(output)


# =========================================================
# Generate personalized summary
# =========================================================

def generate_recommendation_summary(
    recommendations,
    customer
):

    if not recommendations:

        return (
            "No suitable policies were found "
            "based on the provided requirements."
        )


    best = recommendations[0]


    summary = (
        f"Based on the customer's stated requirements, "
        f"{best['policy_name']} appears to be the "
        f"closest match."
    )


    summary += "\n\nWhy it matches:"


    for reason in best["reasons"]:

        summary += (
            f"\n- {reason}"
        )


    if len(recommendations) > 1:

        summary += (
            "\n\nOther policies considered:"
        )


        for policy in recommendations[1:]:

            summary += (
                f"\n- {policy['policy_name']} "
                f"(score: {policy['score']})"
            )


    summary += (
        "\n\nNote: This is a prototype recommendation "
        "based on the information provided and should "
        "not be treated as an insurance underwriting "
        "or approval decision."
    )


    return summary

