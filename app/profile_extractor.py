# app/policy_qa.py

try:
    # Works when running from project root, e.g.
    # python -m app.test_policy_qa
    from .rag import search_policies
except ImportError:
    # Works when running:
    # python app/test_policy_qa.py
    from rag import search_policies


# ============================================================
# Convert RAG results into a list of documents
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

    if not isinstance(document, str):
        return None

    target = field_name.strip().lower()

    for line in document.splitlines():

        line = line.strip()

        if ":" not in line:
            continue

        key, value = line.split(":", 1)

        if key.strip().lower() == target:

            value = value.strip()

            # Remove trailing period only where useful
            if value.endswith("."):
                value = value[:-1].strip()

            return value

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
# Extract policy ID
# ============================================================

def get_policy_id(document):

    return (
        get_field(document, "Policy ID")
        or "Unknown"
    )


# ============================================================
# Find policy explicitly mentioned in question
# ============================================================

def find_matching_policy(question, documents):

    if not documents:
        return None

    question_lower = question.lower()

    # First look for exact policy name
    for document in documents:

        policy_name = get_policy_name(document)

        if (
            policy_name != "Unknown Policy"
            and policy_name.lower() in question_lower
        ):
            return document

    # Then try policy ID
    for document in documents:

        policy_id = get_policy_id(document)

        if (
            policy_id != "Unknown"
            and policy_id.lower() in question_lower
        ):
            return document

    # Fall back to first RAG result
    return documents[0]


# ============================================================
# Detect which field the customer is asking about
# ============================================================

def detect_question_field(question):

    q = question.lower()

    # --------------------------------------------------------
    # Maternity
    # --------------------------------------------------------

    if any(word in q for word in [
        "maternity",
        "pregnancy"
    ]):

        return "Maternity"

    # --------------------------------------------------------
    # Premium
    # --------------------------------------------------------

    if any(word in q for word in [
        "premium",
        "cost",
        "price",
        "pay",
        "annual payment"
    ]):

        return "Annual Premium"

    # --------------------------------------------------------
    # Coverage
    # --------------------------------------------------------

    if any(word in q for word in [
        "coverage",
        "cover",
        "insured amount",
        "sum insured",
        "insurance amount"
    ]):

        return "Coverage"

    # --------------------------------------------------------
    # Waiting period
    # --------------------------------------------------------

    if any(word in q for word in [
        "waiting period",
        "wait period",
        "how long do i wait",
        "how long is the wait"
    ]):

        return "Waiting Period"

    # --------------------------------------------------------
    # Deductible
    # --------------------------------------------------------

    if any(word in q for word in [
        "deductible",
        "deductible amount"
    ]):

        return "Deductible"

    # --------------------------------------------------------
    # Eligibility
    # --------------------------------------------------------

    if any(word in q for word in [
        "eligible",
        "eligibility",
        "age limit",
        "age requirement",
        "maximum age",
        "minimum age"
    ]):

        return "Eligibility"

    # --------------------------------------------------------
    # Pre-existing diseases
    # --------------------------------------------------------

    if any(word in q for word in [
        "pre-existing",
        "pre existing",
        "existing disease",
        "existing diseases"
    ]):

        return "Pre-existing Diseases"

    # --------------------------------------------------------
    # Hospitalization
    # --------------------------------------------------------

    if any(word in q for word in [
        "hospitalization",
        "hospitalisation",
        "hospital expenses",
        "hospital expense"
    ]):

        return "Hospitalization"

    # --------------------------------------------------------
    # Room rent
    # --------------------------------------------------------

    if any(word in q for word in [
        "room rent",
        "room-rent",
        "room limit",
        "room category"
    ]):

        return "Room Rent"

    # --------------------------------------------------------
    # Network hospitals
    # --------------------------------------------------------

    if any(word in q for word in [
        "network hospital",
        "network hospitals",
        "cashless hospital",
        "cashless hospitals"
    ]):

        return "Network Hospitals"

    # --------------------------------------------------------
    # Claim process
    # --------------------------------------------------------

    if any(word in q for word in [
        "claim process",
        "how to claim",
        "file a claim",
        "submit a claim",
        "claims"
    ]):

        return "Claim Process"

    # --------------------------------------------------------
    # Exclusions
    # --------------------------------------------------------

    if any(word in q for word in [
        "exclusion",
        "exclusions",
        "not covered",
        "doesn't cover",
        "does not cover"
    ]):

        return "Exclusions"

    return None


# ============================================================
# Convert policy field name to actual document field
# ============================================================

def get_answer_value(document, field_name):

    # Most fields directly match the document
    value = get_field(document, field_name)

    if value is not None:
        return value

    return None


# ============================================================
# Build a concise answer
# ============================================================

def build_answer(question, results):

    documents = extract_documents(results)

    if not documents:

        return (
            "I couldn't find relevant policy information "
            "in the available policy documents."
        )

    document = find_matching_policy(
        question,
        documents
    )

    if not document:

        return (
            "I couldn't find a relevant insurance policy "
            "for your question."
        )

    policy_name = get_policy_name(document)

    field = detect_question_field(question)

    # ========================================================
    # If a specific field was detected, answer only that field
    # ========================================================

    if field:

        value = get_answer_value(
            document,
            field
        )

        if value is None:

            return (
                f"I couldn't find information about "
                f"{field.lower()} for **{policy_name}** "
                f"in the available policy document."
            )

        # ----------------------------------------------------
        # Friendly answers for specific fields
        # ----------------------------------------------------

        if field == "Maternity":

            return (
                f"**{policy_name}** provides "
                f"**{value.lower()}**."
            )

        if field == "Annual Premium":

            return (
                f"The annual premium for **{policy_name}** "
                f"is **{value}**."
            )

        if field == "Coverage":

            return (
                f"**{policy_name}** provides **{value}**."
            )

        if field == "Waiting Period":

            return (
                f"The initial waiting period for "
                f"**{policy_name}** is **{value}**."
            )

        if field == "Deductible":

            return (
                f"The deductible for **{policy_name}** "
                f"is **{value}**."
            )

        if field == "Eligibility":

            return (
                f"The eligibility requirements for "
                f"**{policy_name}** are: **{value}**."
            )

        if field == "Pre-existing Diseases":

            return (
                f"For **{policy_name}**, pre-existing diseases "
                f"are covered as follows: **{value}**."
            )

        if field == "Hospitalization":

            return (
                f"Hospitalization under **{policy_name}** "
                f"is covered as follows: **{value}**."
            )

        if field == "Room Rent":

            return (
                f"The room-rent provision for "
                f"**{policy_name}** is: **{value}**."
            )

        if field == "Network Hospitals":

            return (
                f"The network hospital provision for "
                f"**{policy_name}** is: **{value}**."
            )

        if field == "Claim Process":

            return (
                f"The claim process for **{policy_name}** "
                f"is: **{value}**."
            )

        if field == "Exclusions":

            return (
                f"The exclusions for **{policy_name}** are: "
                f"**{value}**."
            )

    # ========================================================
    # General policy question
    # ========================================================

    return (
        f"Here is the relevant information for "
        f"**{policy_name}**:\n\n"
        f"{document}\n\n"
        "Please refer to the complete policy terms "
        "and conditions before purchasing."
    )


# ============================================================
# Main Policy Q&A function
# ============================================================

def answer_policy_question(question):

    results = search_policies(
        question,
        n_results=3
    )

    return build_answer(
        question,
        results
    )