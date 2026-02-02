# circuit-a2a-langgraph-quickstart
## 🌟 Purpose

This version demonstrates a **minimal  setup** using Google's [Agent-to-Agent (A2A)](https://github.com/google/A2A) protocol via the official **`a2a-python` SDK**.

It includes:
- A single **Joke agent** which returns a random joke
- A single **A2A client** that sends messages and receives responses

---

## 🚀 Features

- ✅ Minimal working agent with Langraph + LLM
- ✅ Fully async A2A client using the SDK

---

## 📦 Project Structure

```bash
circuit-a2a-langgraph-quickstart/
→ app/
    agent.py             # Joke agent logic
    agent_executor.py    # Executor that connects the agent to A2A runtime
    llm.py              # LLM wrapper for the agent
    schema.py           # Agent schema definition
    JsksCache.py        # JWKS caching utility    
    oauth2_middleware.py  # OAuth2 middleware for token validation
    __main__.py          # Starts the agent server (entry point)
    __init__.py          # Required to treat this folder as a module

→ client/
    client.py               # A2A SDK client that streams messages to the agent
README.md                  # You're reading it!
requirements.txt           # Python dependencies

````

---

## 🛠️ Prerequisites

* Python 3.12+
* `pip install -r requirements.txt` to install dependencies

---

## ⚙️ Setup & Installation

```bash
git clone https://github.com/cisco-dd-enterprise-aiml-eng/circuit-a2a-langgraph-quickstart
cd circuit-a2a-langgraph-quickstart
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
## 🧪 Running the Project

### 🔧 Environment Variables
Set the following environment variables in your terminal or `.env` file:
```bash
# LLM Specific
export GOOGLE_API_KEY="your-llm-api-key"
export CIRCUIT_LLM_API_CLIENT_ID="your-llm-client-id"
export CIRCUIT_LLM_API_CLIENT_SECRET="your-llm-client-secret"
export CIRCUIT_LLM_API_MODEL_NAME="gpt-4o"  # or gpt-4o-mini, gpt-3.5-turbo
export CIRCUIT_LLM_API_ENDPOINT="https://chat-ai.cisco.com"
export CIRCUIT_LLM_API_VERSION="version"

#Token validation is required for A2A Agent requests. You will receive these details after L1 approval of your registered agent.
export JWKS_URI="https://your-jwks-uri-here"
export AUDIENCE="audience-here"
export ISSUER="issuer-here"
export CIRCUIT_CLIENT_ID="your-client-id"
````
### 🟢 Step 1: Start the Greeting Agent Server

```bash
python3 app --host 0.0.0.0 --port 8080

```

This launches the agent server at `http://localhost:8080`.

### 🟡 Step 2: Run the A2A Client

```bash
cd circuit-a2a-langgraph-quickstart
source .venv/bin/activate
python3 client/test_client.py
```

This will connect to the agent server and send a message. You should see the agent's response in the terminal.
### 🔴 Step 3: Stop the Agent Server
Press `Ctrl+C` in the terminal where the agent server is running to stop it.
---

## 📜 Notes
- This is a minimal example to demonstrate the A2A protocol using the `a2a-python` SDK with langGraph agent.
- After registering an agent on CIRCUIT UI, enable the oAuth code flow i.e Un-comment the lines from 143 to 162 in `oauth2_middleware.py`.

# circuit-a2a-langraph
