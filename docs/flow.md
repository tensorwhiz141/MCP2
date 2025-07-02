This is the working of the entire project:
1)User Input (via CLI or API)

2)MCP Adapter receives the query

3)Based on method and target:

4)Calls calendar_agent for reminders

5)Calls real_gmail_agent to send mail

6)Calls math_agent for math problems

7)Agent processes message using its handle_process()

8)Results returned to user or pushed to other services

*base_agent.py*
Base class for all agents.

Handles:

Logging

Capability declaration

Message processing

Agent-to-agent communication

Defines:

MCPMessage: Communication format

AgentCapability: Metadata for what each agent can do

*calendar_agent.py*
Parses and manages calendar events and reminders

Handles queries like:

“Remind me to call at 3 PM”

“Schedule meeting tomorrow”

Stores events in in-memory lists

*real_gmail_agent.py*
Sends actual emails using Gmail SMTP

Uses:

.env credentials (GMAIL_EMAIL, GMAIL_APP_PASSWORD)

Professional email templates

Can be used in workflow pipelines to notify users

*gmail_agent.py*
More advanced Gmail handler using Gmail API (via google-api-python-client)

Can:

Read inbox

Send templated emails

Search messages

*math_agent.py*
Solves math expressions and word problems

Understands natural language like:

“What is 15% of 300?”

“Calculate area of a circle with radius 5”

Uses eval safely for math expressions

*mcp_adapter.py*
Routes incoming messages from pipelines to correct agents

Can call methods like process, send_email, info, etc.

*mongodb_utils.py, mongodb_connection.py*
Handle MongoDB connection

Provide:

Safe inserts

Reconnection logic

Index creation

*file_utils.py, ocr_utils.py*
Handle file reading, cleaning

Perform OCR on documents, especially PDFs and images

*uploads/*
Temporary storage for uploaded files such as:

PDFs

Images

Signature photos
workflows/
Pipelines that connect multiple agents to accomplish tasks.

*archive_search_agent.py*
Reads PDF or scanned docs

Extracts text via OCR

Runs document summarization or question answering

*live_data_agent.py*
Pulls real-time data (e.g., weather, news)

Useful for generating summaries or alerts

