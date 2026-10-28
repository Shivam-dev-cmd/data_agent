# Agentic AI Data Agent

An AI-powered data agent that accepts natural-language requests and routes them to specialized agents. The SQL Analyst handles database questions, while the ETL Analyst extracts and transforms data.

## Features

- **Natural-language routing:** Classifies requests as SQL or ETL tasks.
- **SQL analysis:** Uses database schema context to generate and execute queries.
- **ETL operations:** Extracts JSON data from APIs and transforms tabular data.
- **Multiple LLM providers:** Supports Groq and OpenRouter, with model selection by task.
- **Structured state:** Uses Pydantic schemas with LangGraph workflows.

## Architecture

```text
                         User request
                              |
                              v
                    Data Agent (router)
                       /           \
                      v             v
             SQL Analyst Agent   ETL Analyst Agent
                      |             |
                PostgreSQL      APIs and files
```

### Request flow

1. The user submits a natural-language request.
2. The Data Agent classifies it as a SQL or ETL task.
3. The request is routed to the corresponding specialist agent.
4. The specialist performs the requested operation and returns a result.

## Requirements

- Python 3.14 or newer
- PostgreSQL for SQL operations
- An API key for the selected LLM provider

## Installation

1. Clone the repository and move into the project directory:

   ```bash
   git clone https://github.com/Shivam-dev-cmd/data_agent.git
   cd data_agent
   ```

2. Create and activate a virtual environment:

   ```powershell
   # Windows PowerShell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

   ```bash
   # macOS/Linux
   python -m venv .venv
   source .venv/bin/activate
   ```

3. Install the project dependencies. With [uv](https://docs.astral.sh/uv/):

   ```bash
   uv sync
   ```

   Or install the project with pip:

   ```bash
   pip install -e .
   ```

## Configuration

Create a `.env` file in the project root. Choose a provider and set the matching API key:

```dotenv
# Provider: groq (default) or openrouter
LLM_PROVIDER=groq
GROQ_API_KEY=your_groq_api_key

# For OpenRouter, use this instead:
# LLM_PROVIDER=openrouter
# OPENROUTER_API_KEY=your_openrouter_api_key

# PostgreSQL connection
host=localhost
port=5432
user=postgres
password=your_database_password
database=data_agent_db
```

Keep `.env` private. It is excluded from Git by `.gitignore`; never commit API keys, passwords, or other credentials.

The provider defaults to `groq` if `LLM_PROVIDER` is not set. The model assignments for each task are configured in [`utils/llm_pick.py`](utils/llm_pick.py).

## Usage

Run the application from the project root:

```bash
python main.py
```

You can also invoke the Data Agent from Python:

```python
from langchain_core.messages import HumanMessage
from agents.data_agent import data_agent

response = data_agent.invoke(
    {
        "messages": [
            HumanMessage(
                content="Show me the top 5 users with the highest ratings"
            )
        ],
        "route_response": "",
    }
)

print(response)
```

### Example requests

- **SQL:** “Show me the average rating for each vehicle type.”
- **Extract:** “Extract data from an API endpoint and save it as CSV.”
- **Transform:** “Filter `rides.csv` to include only rides with a rating above 4.5.”

## Project structure

```text
Data_Agent/
├── agents/                 # Router and specialist agents
├── Models/                 # Pydantic schemas
├── data/                   # Sample datasets and ETL output
├── src/data_agent/         # Installable package
├── utils/                  # Database, ETL, and LLM utilities
├── feed_db.py              # Database initialization script
├── main.py                 # Application entry point
├── pyproject.toml          # Project metadata and dependencies
└── README.md
```

## Agents

### Data Agent

The main router classifies requests and dispatches them to the SQL Analyst or ETL Analyst.

### SQL Analyst

Uses database schema information to prepare SQL queries, validate them, execute them, and return results.

### ETL Analyst

Extracts JSON data from API endpoints and transforms data files using Pandas where available. Supported file formats include CSV, JSON, and Parquet.

## Data models

The agent workflows use schemas defined in `Models/schema.py`:

- `AgentSchema`: SQL Analyst state
- `ETLAgentSchema`: ETL Analyst state
- `RouterSchema`: Router classification result
- `DataAgentSchema`: Main Data Agent state

## Development

To add an agent:

1. Add its implementation under `agents/`.
2. Define or update its state schema in `Models/schema.py`.
3. Add the routing behavior to the Data Agent.
4. Update this README with the new behavior.

ETL tools are implemented in [`utils/etl_tools.py`](utils/etl_tools.py), and LLM provider/model selection is configured in [`utils/llm_pick.py`](utils/llm_pick.py).

## Troubleshooting

| Problem | What to check |
| --- | --- |
| Database connection fails | Confirm PostgreSQL is running and the values in `.env` are correct. |
| API key is missing | Set the key for the provider selected by `LLM_PROVIDER`. |
| A module cannot be found | Activate the virtual environment and install the project dependencies. |
| A query is rejected | Check that the request is supported and does not ask for a prohibited database operation. |
