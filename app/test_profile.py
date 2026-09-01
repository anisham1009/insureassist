
from profile_extractor import analyze_customer_message


messages = [

    "I'm 35 years old and my budget is ₹15,000 per year. "
    "I need at least 10 lakh coverage with maternity.",

    "I am 42 years old. I can spend around 20k annually "
    "and need 15 lakh health insurance.",

    "I'm 30 and I want maternity coverage. "
    "My budget is 12k.",

    "Which policy would you recommend for me?",

    "Does HealthSecure Plus cover maternity?",

]


for message in messages:

    print("\n")
    print("=" * 70)

    print("Customer:")
    print(message)

    result = analyze_customer_message(
        message
    )

    print("\nDetected Intent:")
    print(result["intent"])

    print("\nExtracted Profile:")
    print(result["profile"])

    print("=" * 70)

