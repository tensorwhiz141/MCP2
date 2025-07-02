Functionality:

Contains autonomous agents that perform specific tasks.

Key Files:

base_agent.py: Abstract class for all agents with standard communication methods.

calendar_agent.py: Parses text to schedule events/reminders.

real_gmail_agent.py: Sends emails via Gmail SMTP using templates.

gmail_agent.py: Uses Gmail API to read/search/send emails.

math_agent.py: Solves mathematical expressions and word problems.

live_data_agent.py: (If exists) Fetches and analyzes real-time information.

archive_search_agent.py: Searches archived documents based on queries.

Capabilities:

Email, calendar, math, OCR, weather, document analysis.

Extensible using AgentCapability interface.

