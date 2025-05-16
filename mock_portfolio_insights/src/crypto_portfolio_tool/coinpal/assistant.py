import json
import os
from typing import List, Dict, Any, Optional
from ..portfolio_insights.analyzer import PortfolioAnalyzer # To potentially fetch portfolio info
class CoinPalAssistant:
    def __init__(self, knowledge_base_path: Optional[str] = None, portfolio_analyzer: Optional[PortfolioAnalyzer] = None):
        if knowledge_base_path is None:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            knowledge_base_path = os.path.join(base_dir, 'knowledge_base.json')
        
        with open(knowledge_base_path, 'r') as f:
            self.kb: List[Dict[str, Any]] = json.load(f)
        
        self.portfolio_analyzer = portfolio_analyzer # For actions requiring portfolio data

    def _match_intent(self, user_query: str) -> Dict[str, Any]:
        user_query_lower = user_query.lower()
        best_match = None
        highest_score = 0

        for item in self.kb:
            if item["intent"] == "fallback": # Fallback is special
                continue

            score = 0
            matched_keywords_count = 0
            for keyword in item.get("keywords", []):
                if keyword in user_query_lower:
                    score += 1 # Simple scoring: 1 point per keyword match
                    matched_keywords_count +=1
            
            # Prioritize if all keywords for an intent are present
            if item.get("keywords") and matched_keywords_count == len(item.get("keywords")):
                score += len(item.get("keywords")) # Bonus for full keyword match

            if score > highest_score:
                highest_score = score
                best_match = item
        
        if best_match and highest_score > 0: # Require at least one keyword match
            return best_match
        else:
            # Find and return the fallback intent
            return next((item for item in self.kb if item["intent"] == "fallback"), 
                        {"intent": "error", "response": "Error: Fallback intent not found."})


    def process_query(self, user_query: str, user_id: Optional[str] = None) -> str:
        intent_data = self._match_intent(user_query)
        response = intent_data.get("response", "I'm not sure how to respond to that.")

        action = intent_data.get("action")
        if action:
            # Placeholder for action execution
            # In a real app, this might call other services or methods
            if action == "guide_transaction_delay":
                response += " (Mock Action: Would provide link to Coinbase help on delays)"
            elif action == "guide_account_verification":
                response += " (Mock Action: Would guide to Coinbase verification page)"
            elif action == "get_portfolio_summary" and self.portfolio_analyzer:
                if user_id:
                    try:
                        composition = self.portfolio_analyzer.get_portfolio_composition(user_id)
                        total_value = composition.get("total_portfolio_value", "N/A")
                        response = f"Your portfolio (user: {user_id}) is currently valued at approximately ${total_value}."
                    except Exception as e:
                        response = f"Sorry, I couldn't fetch the portfolio value for {user_id} right now. Error: {e}"
                else:
                    response = "Please provide your user ID so I can check the portfolio value."
            # Add more actions here
        
        return response