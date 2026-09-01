from profile_extractor import analyze_customer_message
from recommendation import recommend_policies
from policy_qa import answer_policy_question


class ConversationManager:

    def __init__(self):
        self.customer_profile = {}
        self.last_policy = None

    def process_message(self, message):

        message = message.strip()

        if not message:
            return "Please enter a question."

        # ============================================================
        # Analyze customer message
        # ============================================================

        result = analyze_customer_message(message)

        # Support the existing profile_extractor return format
        if isinstance(result, tuple):

            intent = result[0]

            if len(result) > 1:
                profile = result[1]
            else:
                profile = {}

        elif isinstance(result, dict):

            intent = result.get("intent", "general")
            profile = result.get("profile", {})

        else:

            intent = "general"
            profile = {}

        # Make absolutely sure profile is a dictionary
        if not isinstance(profile, dict):
            profile = {}

        # Update customer profile
        self.customer_profile.update(profile)

        # ============================================================
        # RECOMMENDATION
        # ============================================================

        if intent == "recommendation":

            if not self.customer_profile:

                return (
                    "I'd be happy to recommend a policy. "
                    "Please tell me your age, annual budget, "
                    "and desired coverage."
                )

            recommendations = recommend_policies(
                self.customer_profile,
                top_n=3
            )

            if not recommendations:

                return (
                    "I couldn't find suitable policies "
                    "based on your requirements."
                )

            response = (
                "Based on your requirements, here are "
                "the policies I recommend:\n\n"
            )

            for i, recommendation in enumerate(
                recommendations,
                1
            ):

                response += (
                    f"{i}. {recommendation['policy_name']} "
                    f"({recommendation['policy_id']})\n"
                    f"   Annual Premium: "
                    f"₹{recommendation['annual_premium']:,}\n"
                    f"   Coverage: "
                    f"₹{recommendation['coverage_amount']:,}\n"
                    f"   Recommendation Score: "
                    f"{recommendation['score']}\n"
                    "   Why it matches:\n"
                )

                for reason in recommendation["reasons"]:

                    response += f"   - {reason}\n"

                response += "\n"

            # Remember top recommended policy
            self.last_policy = recommendations[0]["policy_name"]

            return response.strip()

        # ============================================================
        # POLICY QUESTION
        # ============================================================

        if intent == "policy_question":

            question = message

            # --------------------------------------------------------
            # If we already know the policy from previous conversation,
            # use it for follow-up questions.
            # --------------------------------------------------------

            if self.last_policy:

                question_lower = question.lower()

                policy_already_mentioned = (
                    self.last_policy.lower()
                    in question_lower
                )

                if not policy_already_mentioned:

                    question = (
                        f"Regarding {self.last_policy}: "
                        f"{question}"
                    )

            answer = answer_policy_question(question)

            # --------------------------------------------------------
            # Remember policy from answer if we don't already have one
            # --------------------------------------------------------

            if not self.last_policy:

                for line in answer.splitlines():

                    if line.startswith("Policy Name:"):

                        self.last_policy = (
                            line.split(":", 1)[1].strip()
                        )

                        break

            return answer

        # ============================================================
        # GENERAL
        # ============================================================

        if intent == "general":

            return (
                "I can help you compare health insurance policies, "
                "understand coverage, premiums, waiting periods, "
                "deductibles, maternity benefits, and exclusions."
            )

        # ============================================================
        # FALLBACK
        # ============================================================

        return (
            "I can help you with health insurance policies. "
            "You can ask about coverage, premiums, maternity, "
            "waiting periods, deductibles, or policy recommendations."
        )