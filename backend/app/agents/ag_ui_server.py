from ag_ui_adk import create_ag_ui_app
from app.agents.clinic_agent import runner
from app.core.config import settings

# Create AG-UI ASGI application
ag_ui_app = create_ag_ui_app(
    runner=runner,
    # Optional: customize the agent name
    agent_name="clinic_billing_agent"
)
