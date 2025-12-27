class RiskScorer:
    def __init__(self):
        self.base_score = 100  # Perfect score starts at 100

    def calculate_score(self, all_risks):
        """
        Calculates a document health score (0-100).
        Args:
            all_risks (list): List of risk dictionaries from the detector.
        """
        total_penalty = 0

        for risk in all_risks:
            total_penalty += risk['weight']

        # Ensure score doesn't drop below 0
        final_score = max(0, self.base_score - total_penalty)
        return final_score

    def get_risk_level(self, score):
        if score >= 85:
            return "Low Risk 🟢"
        elif score >= 60:
            return "Medium Risk 🟡"
        else:
            return "High Risk 🔴"
