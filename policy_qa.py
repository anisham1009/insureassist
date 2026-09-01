# app/policy_qa.py

try:
    from .rag import search_policies
except ImportError:
    from rag import search_policies


# ============================================================
# Convert RAG results into a clean list of documents
# ============================================================

def extract_documents(results):

    if isinstance(results, dict):

        documents = results.get("documents", [])

        if documents and isinstance(documents[0], list):
            documents = documents[0]

        return [
            doc for doc in documents
            if isinstance(doc, str)
        ]

    if isinstance(results, list):

        if results and isinstance(results[0], list):
            results = results[0]

        return [
            doc for doc in results
            if isinstance(doc, str)
        ]

    return []


# ============================================================
# Extract a field from a policy document
# ============================================================

def get_field(document, field_name):
    """
    Extract a field value from policy documents.

    Supports both formats:

        Annual Premium: ₹12,500.

    and:

        Annual Premium:
        ₹12,500.
    """

    if not isinstance(document, str):
        return None

    lines = document.splitlines()

    for i, line in enumerate(lines):

        current = line.strip()

        # --------------------------------------------------------
        # Format 1:
        # Annual Premium: ₹12,500.
        # --------------------------------------------------------
        if current.startswith(field_name + ":"):

            value = current.split(":", 1)[1].strip()

            if value:
                return value

            # ----------------------------------------------------
            # Format 2:
            # Annual Premium:
            # ₹12,500.
            # ----------------------------------------------------
            for next_line in lines[i + 1:]:

                next_value = next_line.strip()

                if next_value:
                    return next_value

            return None

    return None
# ============================================================
# Extract policy name
# ============================================================

def get_policy_name(document):

    return (
        get_field(document, "Policy Name")
        or "Unknown Policy"
    )


# ============================================================
# Find policy mentioned in question
# ============================================================

def find_matching_policy(question, documents):

    question_lower = question.lower()

    # First try exact policy-name matching
    for document in documents:

        policy_name = get_policy_name(document)

        if (
            policy_name != "Unknown Policy"
            and policy_name.lower() in question_lower
        ):

            return document

    # If no policy name was explicitly mentioned,
    # use the first RAG result.
    return documents[0] if documents else None


# ============================================================
# Clean extracted value
# ============================================================

def clean_value(value):

    if value is None:
        return None

    return str(value).strip()


# ============================================================
# Detect what the customer is asking about
# ============================================================

def detect_question_type(question):

    q = question.lower()

    if (
        "premium" in q
        or "cost" in q
        or "price" in q
        or "pay" in q
    ):
        return "premium"

    if (
        "coverage" in q
        or "cover amount" in q
        or "sum insured" in q
        or "how much insurance" in q
        or "how much cover" in q
    ):
        return "coverage"

    if (
        "maternity" in q
        or "pregnancy" in q
    ):
        return "maternity"

    if (
        "waiting period" in q
        or "wait" in q
    ):
        return "waiting_period"

    if (
        "deductible" in q
    ):
        return "deductible"

    if (
        "pre-existing" in q
        or "pre existing" in q
        or "existing disease" in q
    ):
        return "pre_existing_disease"

    if (
        "hospital" in q
        or "hospitalization" in q
    ):
        return "hospitalization"

    if (
        "room rent" in q
        or "room-rent" in q
    ):
        return "room_rent"

    if (
        "claim" in q
    ):
        return "claim_process"

    if (
        "exclusion" in q
        or "excluded" in q
    ):
        return "exclusions"

    if (
        "eligible" in q
        or "eligibility" in q
        or "age" in q
    ):
        return "eligibility"

    return "general"


# ============================================================
# Build a concise answer
# ============================================================

def build_answer(question, results):

    question_type = detect_question_type(question)

    document = find_matching_policy(
        question,
        results
    )

    if not document:

        return (
            "I couldn't find a relevant insurance policy "
            "in the available policy documents."
        )

    policy_name = get_policy_name(document)

    # --------------------------------------------------------
    # PREMIUM
    # --------------------------------------------------------

    if question_type == "premium":

        premium = clean_value(
            get_field(
                document,
                "Annual Premium"
            )
        )

        if premium:

            return (
                f"The annual premium for "
                f"**{policy_name}** is **{premium}**."
            )

    # --------------------------------------------------------
    # COVERAGE
    # --------------------------------------------------------

    if question_type == "coverage":

        coverage = clean_value(
            get_field(
                document,
                "Coverage"
            )
        )

        if coverage:

            return (
                f"**{policy_name}** provides "
                f"**{coverage}**."
            )

    # --------------------------------------------------------
    # MATERNITY
    # --------------------------------------------------------

    if question_type == "maternity":

        maternity = clean_value(
            get_field(
                document,
                "Maternity"
            )
        )

        if maternity:

            return (
                f"**{policy_name}**: "
                f"{maternity}"
            )

    # --------------------------------------------------------
    # WAITING PERIOD
    # --------------------------------------------------------

    if question_type == "waiting_period":

        waiting = clean_value(
            get_field(
                document,
                "Waiting Period"
            )
        )

        if waiting:

            return (
                f"The initial waiting period for "
                f"**{policy_name}** is **{waiting}**."
            )

    # --------------------------------------------------------
    # DEDUCTIBLE
    # --------------------------------------------------------

    if question_type == "deductible":

        deductible = clean_value(
            get_field(
                document,
                "Deductible"
            )
        )

        if deductible:

            return (
                f"The deductible for "
                f"**{policy_name}** is **{deductible}**."
            )

    # --------------------------------------------------------
    # PRE-EXISTING DISEASE
    # --------------------------------------------------------

    if question_type == "pre_existing_disease":

        value = clean_value(
            get_field(
                document,
                "Pre-existing Diseases"
            )
        )

        if value:

            return (
                f"For **{policy_name}**, "
                f"{value}"
            )

    # --------------------------------------------------------
    # HOSPITALIZATION
    # --------------------------------------------------------

    if question_type == "hospitalization":

        value = clean_value(
            get_field(
                document,
                "Hospitalization"
            )
        )

        if value:

            return (
                f"For **{policy_name}**, "
                f"{value}"
            )

    # --------------------------------------------------------
    # ROOM RENT
    # --------------------------------------------------------

    if question_type == "room_rent":

        value = clean_value(
            get_field(
                document,
                "Room Rent"
            )
        )

        if value:

            return (
                f"For **{policy_name}**, "
                f"{value}"
            )

    # --------------------------------------------------------
    # CLAIM PROCESS
    # --------------------------------------------------------

    if question_type == "claim_process":

        value = clean_value(
            get_field(
                document,
                "Claim Process"
            )
        )

        if value:

            return (
                f"For **{policy_name}**, "
                f"{value}"
            )

    # --------------------------------------------------------
    # EXCLUSIONS
    # --------------------------------------------------------

    if question_type == "exclusions":

        value = clean_value(
            get_field(
                document,
                "Exclusions"
            )
        )

        if value:

            return (
                f"For **{policy_name}**, "
                f"{value}"
            )

    # --------------------------------------------------------
    # ELIGIBILITY
    # --------------------------------------------------------

    if question_type == "eligibility":

        value = clean_value(
            get_field(
                document,
                "Eligibility"
            )
        )

        if value:

            return (
                f"For **{policy_name}**, "
                f"{value}"
            )

    # --------------------------------------------------------
    # GENERAL FALLBACK
    # --------------------------------------------------------

    return (
        f"Here is the relevant information for "
        f"**{policy_name}**:\n\n"
        f"{document}\n\n"
        "Please refer to the complete policy terms "
        "and conditions before purchasing."
    )


# ============================================================
# Main Policy Q&A
# ============================================================

def answer_policy_question(question):

    results = search_policies(
        question,
        n_results=3
    )

    documents = extract_documents(results)

    if not documents:

        return (
            "I couldn't find relevant policy information "
            "in the available policy documents."
        )

    return build_answer(
        question,
        documents
    )