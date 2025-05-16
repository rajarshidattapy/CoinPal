from typing import Optional, Any, List, Dict
import json 

from crypto_portfolio_tool.api_clients.asset_news_api import AssetNewsAPIClient
from crypto_portfolio_tool.api_clients.llm_client import LLMInsightsClient
from ..core.models import Portfolio


class RecommendationEngine:
    def __init__(self, llm_client: Optional[LLMInsightsClient] = None):
        self.llm_client = llm_client

    def generate_recommendations(
        self,
        portfolio: Portfolio,
        composition_details: Dict,
        all_asset_specific_insights: Optional[Dict] = None
    ) -> List[str]:
        recommendations = []
        fetched_hhi_score = composition_details.get("hhi_score")
        hhi_good_diversification_message = ""
        # Use robust hhi_value_str formatting from the new code
        hhi_value_str = f"{fetched_hhi_score:.0f}" if fetched_hhi_score is not None else "N/A"

        # HHI Rule
        if fetched_hhi_score is not None:
            if fetched_hhi_score > 2500:
                basic_hhi_rec = (
                    f"Your portfolio HHI is {hhi_value_str}, indicating high concentration. "
                    "Consider diversifying to manage risk."
                )
                recommendations.append(basic_hhi_rec)

                # --- GenAI Enhancement for High HHI ---
                if self.llm_client and all_asset_specific_insights:
                    top_concentrated_asset_detail = None
                    # Ensure 'asset_composition' exists and is a list
                    asset_composition_list = composition_details.get("asset_composition", [])
                    if isinstance(asset_composition_list, list) and asset_composition_list:
                        try:
                            sorted_assets = sorted(
                                asset_composition_list,
                                key=lambda x: x.get("percentage", 0.0) or 0.0, # handle None for percentage
                                reverse=True
                            )
                            if sorted_assets:
                                top_concentrated_asset_detail = sorted_assets[0]
                        except TypeError as e:
                            print(f"[RECO_ENGINE_WARN] Could not sort asset_composition for GenAI HHI: {e}")


                    if top_concentrated_asset_detail:
                        asset_id_raw = top_concentrated_asset_detail.get("asset_id")
                        asset_name = top_concentrated_asset_detail.get("name")
                        asset_percentage = top_concentrated_asset_detail.get("percentage")

                        if asset_id_raw and asset_name is not None and asset_percentage is not None:
                            asset_id = str(asset_id_raw).upper() # Ensure asset_id is string before .upper()
                            
                            asset_insights = all_asset_specific_insights.get(asset_id)
                            news_context = "No specific recent news summaries available for LLM context."
                            
                            if asset_insights and asset_insights.get("processed_news"):
                                news_snippets = []
                                # Ensure processed_news is a list
                                processed_news_list = asset_insights["processed_news"]
                                if isinstance(processed_news_list, list):
                                    for news_item in processed_news_list[:2]: # Use top 2 processed news
                                        # Ensure news_item is a dict before calling .get()
                                        if isinstance(news_item, dict):
                                            news_snippets.append(
                                                f"- Headline: '{news_item.get('original_headline', 'N/A')}'; "
                                                f"LLM Summary: '{news_item.get('llm_summary', 'N/A')}'; "
                                                f"LLM Sentiment: {news_item.get('llm_sentiment_label', 'N/A')}"
                                            )
                                if news_snippets:
                                    news_context = "Recent news insights:\n" + "\n".join(news_snippets)
                            
                            prompt = (
                                f"A user's crypto portfolio has an HHI of {hhi_value_str}, indicating high concentration. "
                                f"The most concentrated asset is {asset_name} ({asset_id}) at {asset_percentage:.2f}%. "
                                f"{news_context}\n\n"
                                "Provide a brief (1-2 sentences) additional insight or cautionary note regarding this concentration, "
                                "considering the HHI and the provided news context for the concentrated asset. "
                                "Frame it as an observation, not direct financial advice. Be concise and focus on potential implications of concentration given the news."
                            )
                            system_prompt = "You are a helpful portfolio analysis assistant providing concise, objective observations."
                            
                            # For debugging the prompt:
                            # print(f"\n[DEBUG] GenAI HHI Prompt for {asset_id}:\n{prompt}\n")

                            llm_contextual_insight = self.llm_client.generate_text(prompt, system_message=system_prompt)
                            
                            if llm_contextual_insight:
                                recommendations.append(f"GenAI Context on Concentration: {llm_contextual_insight.strip()}")
                            else:
                                recommendations.append("Further AI-driven context on portfolio concentration could not be generated at this time.")
                        else:
                            print(f"[RECO_ENGINE_WARN] Missing details in top_concentrated_asset_detail for GenAI HHI: {top_concentrated_asset_detail}")


            elif fetched_hhi_score > 1500:
                recommendations.append(
                    f"Your portfolio HHI is {hhi_value_str}, indicating moderate concentration. "
                    "You might review your largest holdings."
                )
            elif fetched_hhi_score <= 1500:
                hhi_good_diversification_message = f"Your Portfolio HHI is {hhi_value_str}, suggesting good diversification."
                recommendations.append(hhi_good_diversification_message)
        else:
            recommendations.append(
                "Could not calculate portfolio concentration (HHI). Please check the data."
            )

        # Rule 1: Diversification based on a single asset concentration (Existing User Rule)
        if portfolio.assets: # Check if portfolio.assets is not None and not empty
            asset_composition_list = composition_details.get("asset_composition", [])
            if isinstance(asset_composition_list, list):
                for asset_comp in asset_composition_list:
                    if isinstance(asset_comp, dict) and (asset_comp.get("percentage", 0.0) or 0.0) > 60: # Example threshold
                        recommendations.append(
                            f"Specific Alert: Your portfolio is heavily concentrated ({asset_comp.get('percentage', 0.0):.2f}%) in {asset_comp.get('name', 'N/A')}."
                        )
                        break # One such warning is enough

        # Rule 2: Cash balance too high (Existing User Rule)
        cash_percentage = composition_details.get("cash_percentage", 0.0) or 0.0 # Ensure it's a float
        if cash_percentage > 30: # Example threshold
            recommendations.append(
                f"You have a significant cash balance ({cash_percentage:.2f}%). Consider deploying some capital if market conditions are favorable."
            )

        # Rule 3: Based on (mocked) historical performance (Existing User Rule)
        if portfolio.historical_summary:
            if portfolio.historical_summary.seven_d_change_percent is not None and \
               portfolio.historical_summary.seven_d_change_percent < -10: # Lost >10% in 7 days
                recommendations.append(
                    "Your portfolio has seen a significant drop in the last 7 days. Review your holdings and market news."
                )

        # Rule 5: Asset-specific negative sentiment (using LLM processed sentiment)
        if all_asset_specific_insights and portfolio.assets:
            for port_asset in portfolio.assets: # Iterate through assets in the actual portfolio
                asset_id_upper = port_asset.asset_id.upper()
                # Get the insights for this specific asset from the passed-in dictionary
                asset_insights_data = all_asset_specific_insights.get(asset_id_upper)

                if asset_insights_data and not asset_insights_data.get("error") and \
                   isinstance(asset_insights_data.get("processed_news"), list): # Check if processed_news is a list
                    
                    negative_news_count = 0
                    for news_item in asset_insights_data["processed_news"]:
                        if isinstance(news_item, dict) and "negative" in (news_item.get("llm_sentiment_label", "") or "").lower():
                            negative_news_count += 1
                    
                    if negative_news_count >= 1: 
                        recommendations.append(
                            f"GenAI Processed News: Recent sentiment for {port_asset.name} ({port_asset.asset_id}) "
                            "has some negative indicators. Consider reviewing the news summaries."
                        )

        # Fallback Logic (Existing User Logic - seems reasonable)
        actionable_recommendations_count = 0
        for rec in recommendations:
            # Exclude positive HHI messages or calculation errors from "actionable" count
            if "HHI" in rec and ("good diversification" in rec or "suggesting good" in rec):
                continue
            if "Could not calculate" in rec:
                continue
            # Exclude AI context not generated message if it's the only one
            if "could not be generated" in rec and len(recommendations) == 1 and actionable_recommendations_count == 0:
                pass # Don't count this as actionable if it's the only message
            elif "could not be generated" in rec: # If other recs exist, don't count it
                continue

            actionable_recommendations_count += 1

        if actionable_recommendations_count == 0:
            if hhi_good_diversification_message and not any("concentration" in rec.lower() for rec in recommendations):
                # If HHI was good and no other issues were flagged, add a positive note.
                if not any("Overall, things look good" in rec for rec in recommendations): # Avoid duplicate general messages
                    recommendations.append("Overall, things look good. Continue monitoring market conditions and your investment goals.")
            elif not recommendations: # If truly no recommendations were generated at all
                recommendations.append("Your portfolio looks reasonable based on current checks. Keep monitoring!")
            # If there was an HHI calculation error, or an AI generation error, and nothing else, that's the primary message.
            # The current logic for actionable_recommendations_count handles this.

        return recommendations