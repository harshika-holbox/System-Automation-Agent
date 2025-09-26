# Autonomous Desktop Agent

This project is an implementation of an autonomous AI agent capable of understanding high-level goals and controlling a desktop computer to achieve them. It uses a Large Language Model (LLM) as its 'brain' and the Strands Agent toolkit for computer interaction.

The agent is designed to be provider-agnostic, with clear instructions for using either **AWS Bedrock** or **OpenAI** as the reasoning engine.

-----

## Core Technologies

  * **LLM Brain**:
      * **AWS Bedrock** (via `boto3` SDK, using models like Anthropic Claude 3 Sonnet)
      * **OpenAI** (via `openai` SDK, using models like GPT-4o)
  * **Computer Interaction**: **Strands Agent** (`strands-tools` library) for screen analysis and control.
  * **Orchestration**: Python 3
  * **Environment Management**: `dotenv` for handling API keys securely.

-----

## ⚙️ Setup and Installation

Follow these steps to get the agent running on your local machine.

### 1\. Prerequisites

  * Python 3.8 or higher.
  * Access to either an AWS account with Bedrock enabled or an OpenAI API key.

### 2\. Clone the Repository

Clone this project to your local machine:

```bash
git clone <your-repository-url>
cd <your-repository-directory>
```

### 3\. Create and Activate a Virtual Environment

It's highly recommended to use a virtual environment to manage project dependencies.

  * **On macOS / Linux:**
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```
  * **On Windows:**
    ```bash
    python -m venv .venv
    .\.venv\Scripts\activate
    ```

### 4\. Install Dependencies

Create a file named `requirements.txt` in your project directory and add the following lines:

```text:requirements.txt
strands-tools
python-dotenv
boto3        # Required for AWS Bedrock
openai       # Required for OpenAI
```

Now, install these dependencies using pip:

```bash
pip install -r requirements.txt
```

### 5\. Configure Environment Variables

This is the most important step for connecting to your chosen LLM provider.

1.  Create a file named `.env` in the root of your project directory.
2.  Copy the contents of the appropriate section below into your `.env` file.

#### For AWS Bedrock Users:

```env:.env
# --- AWS Bedrock Configuration ---
# Ensure the IAM user has Bedrock access permissions.
AWS_ACCESS_KEY_ID=YOUR_AWS_ACCESS_KEY
AWS_SECRET_ACCESS_KEY=YOUR_AWS_SECRET_KEY
AWS_REGION=us-east-1 # Or your preferred AWS region
```

#### For OpenAI Users:

```env:.env
# --- OpenAI Configuration ---
OPENAI_API_KEY=sk-YOUR_OPENAI_API_KEY
```

**Note:** Only fill in the variables for the one provider you intend to use.

-----

## ▶️ How to Run the Agent

Once the setup is complete, you can run the agent with a single command. The script will prompt you to enter your high-level goal.

```bash
python desktop_agent.py
```

-----

## 🤖 How It Works: The Agent's Workflow

The agent operates on a simple yet powerful **"SEE ➡️ THINK ➡️ ACT"** loop.

### 1\. SEE: The Eyes of the Agent 👀

  * **Tool**: `strands_tools.use_computer(action="analyze_screen")`
  * **Process**: The agent captures the current screen content. It uses Optical Character Recognition (OCR) to identify all visible text elements and their coordinates, creating a structured "map" of what's on the screen.

### 2\. THINK: The Brain of the Agent 🧠

  * **Tool**: AWS Bedrock or OpenAI LLM
  * **Process**: The agent sends a detailed prompt to the LLM. This prompt includes:
    1.  The overall **Goal**.
    2.  The recent **Action History** (including any failed actions).
    3.  The complete **Screen Content** from the "SEE" step.
    4.  A **Strict Workflow** that forces the agent to think methodically (e.g., open an app first, then browse to a URL, then interact with elements).
  * The LLM analyzes this information and decides on the single, most logical next action to take.

### 3\. ACT: The Hands of the Agent 🦾

  * **Tool**: `strands_tools.use_computer(...)`
  * **Process**: The agent takes the command decided by the LLM (e.g., `click_keywords(...)`) and executes it using the `use_computer` function. This can be a mouse click, typing text, or opening an application.

This loop repeats, allowing the agent to get continuous feedback from the screen and adjust its strategy until the goal is achieved or it reaches a stopping condition.

-----

## 🧰 Modifying the Code for Your LLM Provider

The `desktop_agent.py` script needs to be pointed to the correct LLM. Open the file and navigate to the `get_next_action_from_llm` function.

#### To use AWS Bedrock:

Ensure the **boto3/Bedrock** client code is active.

```python
# ... inside get_next_action_from_llm ...
try:
    # This section should be active for AWS Bedrock
    aws_region = os.getenv("AWS_REGION", "us-east-1")
    bedrock_client = boto3.client(service_name='bedrock-runtime', region_name=aws_region)
    
    # ... Bedrock API call logic ...
    response = bedrock_client.invoke_model(...)

except Exception as e:
    # ...
```

#### To use OpenAI:

You will need to modify the function to use the OpenAI client instead.

```python
# ... inside get_next_action_from_llm ...
try:
    # This section should be active for OpenAI
    api_key = os.getenv("OPENAI_API_KEY")
    client = OpenAI(api_key=api_key)

    # ... OpenAI API call logic ...
    response = client.chat.completions.create(...)

except Exception as e:
    # ...
```
