from components.lang_graph_component import LangGraphComponent
from components.mcp_component import MCPComponent
from components.cold_email_component import ColdEmailComponent
from components.voice_call_component import VoiceCallComponent
from components.analytics_component import AnalyticsComponent


def main():
    lang_graph = LangGraphComponent()
    mcp = MCPComponent()
    cold_email = ColdEmailComponent()
    voice_call = VoiceCallComponent()
    analytics = AnalyticsComponent()

    # Initialize the workflow
    lang_graph.initialize_workflow()

    # Plan the marketing campaign
    campaign_plan = mcp.plan_campaign()

    # Send emails based on the campaign plan
    cold_email.send_emails(campaign_plan)

    # Handle voice calls
    voice_call.handle_calls(campaign_plan)

    # Collect and analyze data
    analytics.collect_data(campaign_plan)
    analytics.analyze_data()


if __name__ == '__main__':
    main()