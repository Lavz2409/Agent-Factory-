class FinalReportCompilerAgent:
    def __init__(self):
        pass

    def compile_report(self, swot_data: dict) -> str:
        """
        Combines all agent outputs into a final report.
        
        Args:
            swot_data (dict): Data from the SWOT Analysis Agent.
        
        Returns:
            str: A structured final report.
        """
        report_sections = [
            self._compile_input_analysis(swot_data.get('input_analysis', {})),
            self._compile_market_research(swot_data.get('market_research', {})),
            self._compile_competitor_analysis(swot_data.get('competitor_analysis', {})),
            self._compile_positioning(swot_data.get('positioning', {})),
            self._compile_use_cases(swot_data.get('use_cases', {})),
            self._compile_marketing_strategy(swot_data.get('marketing_strategy', {})),
            self._compile_campaigns(swot_data.get('campaigns', [])),
            self._compile_growth_hacks(swot_data.get('growth_hacks', {})),
            self._compile_swot_analysis(swot_data.get('swot_analysis', {}))
        ]

        final_report = "\n\n".join(report_sections)
        return final_report

    def _compile_input_analysis(self, data: dict) -> str:
        return f"Input Analysis:\nProduct Type: {data.get('product_type', 'N/A')}\nDomain: {data.get('domain', 'N/A')}\nComplexity Level: {data.get('complexity_level', 'N/A')}"

    def _compile_market_research(self, data: dict) -> str:
        return f"Market Research:\nCategory: {data.get('category', 'N/A')}\nTrends: {', '.join(data.get('trends', []))}\nCustomer Pain Points: {', '.join(data.get('pain_points', []))}\nMarket Maturity: {data.get('maturity', 'N/A')}"

    def _compile_competitor_analysis(self, data: dict) -> str:
        competitors = data.get('competitors', [])
        competitor_details = "\n".join([f"Name: {comp['name']}, Features: {comp['features']}, Strengths: {comp['strengths']}, Weaknesses: {comp['weaknesses']}, Positioning: {comp['positioning']}" for comp in competitors])
        return f"Competitor Analysis:\n{competitor_details}"

    def _compile_positioning(self, data: dict) -> str:
        return f"Positioning:\nUSP: {data.get('usp', 'N/A')}\nPositioning Statement: {data.get('statement', 'N/A')}\nBrand Tone: {data.get('tone', 'N/A')}"

    def _compile_use_cases(self, data: dict) -> str:
        return f"Use Cases:\nPrimary Users: {', '.join(data.get('primary_users', []))}\nSecondary Users: {', '.join(data.get('secondary_users', []))}\nIndustries: {', '.join(data.get('industries', []))}"

    def _compile_marketing_strategy(self, data: dict) -> str:
        organic = data.get('organic', {})
        paid = data.get('paid', {})
        community = data.get('community', {})
        partnership = data.get('partnership', {})
        return (
            f"Marketing Strategy:\n"
            f"Organic Strategy:\nSEO Angles: {organic.get('seo', 'N/A')}\nContent Strategy: {organic.get('content', 'N/A')}\n"
            f"Paid Strategy:\nAd Channels: {paid.get('channels', 'N/A')}\nMessaging Angles: {paid.get('messaging', 'N/A')}\n"
            f"Community Strategy:\nPlatforms: {community.get('platforms', 'N/A')}\nEngagement Tactics: {community.get('tactics', 'N/A')}\n"
            f"Partnership Strategy:\nPartners: {partnership.get('partners', 'N/A')}"
        )

    def _compile_campaigns(self, data: list) -> str:
        campaigns = "\n".join([f"Name: {camp['name']}, Hook: {camp['hook']}, Tagline: {camp['tagline']}, Core Message: {camp['core_message']}" for camp in data])
        return f"Campaigns:\n{campaigns}"

    def _compile_growth_hacks(self, data: dict) -> str:
        return (
            f"Growth Hacking:\n"
            f"Viral Loops: {', '.join(data.get('viral_loops', []))}\n"
            f"Adoption Strategies: {', '.join(data.get('adoption_strategies', []))}\n"
            f"Integration Growth: {', '.join(data.get('integration_growth', []))}"
        )

    def _compile_swot_analysis(self, data: dict) -> str:
        return (
            f"SWOT Analysis:\n"
            f"Strengths: {', '.join(data.get('strengths', []))}\n"
            f"Weaknesses: {', '.join(data.get('weaknesses', []))}\n"
            f"Opportunities: {', '.join(data.get('opportunities', []))}\n"
            f"Threats: {', '.join(data.get('threats', []))}"
        )