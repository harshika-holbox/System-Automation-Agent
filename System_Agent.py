###IMprove codes
####open ai based 


# import os
# import json
# import asyncio
# import re
# from openai import OpenAI
# from dotenv import load_dotenv
# from strands_tools.use_computer import use_computer


# load_dotenv()

# os.environ["BYPASS_TOOL_CONSENT"] = "true" # | now agent won't ask for permission every time it wants to use a tool |


# # --- AGENT CONFIGURATION ---
# DEFAULT_BROWSER = "Google Chrome" 
# TERMINAL_APP = "Terminal"


# # Securely load the API key from the environment.
# api_key = os.getenv("OPENAI_API_KEY")
# if not api_key:
#     print("FATAL ERROR: OPENAI_API_KEY not found please set it in your .env file.")
#     exit()

# try:
#     client = OpenAI(api_key=api_key)
# except Exception as e:
#     print(f"Error initializing OpenAI client: {e}")
#     exit()


# # --- HELPER FUNCTION FOR SEMANTIC ACTIONS ---

# def find_element_coordinates(screen_analysis_text: str, text_to_find: str):
#     """
#     Parses the screen analysis to find the coordinates of a given text element.
#     """
#     try:
#         pattern = re.compile(f"Text: '{re.escape(text_to_find)}'.*?Center: \\((\\d+), (\\d+)\\)", re.IGNORECASE | re.DOTALL)
#         match = pattern.search(screen_analysis_text)
#         if match:
#             x, y = int(match.group(1)), int(match.group(2))
#             return {'x': x, 'y': y}
#     except Exception:
#         pass
        
#     return None


# def get_next_action_from_llm(goal: str, history: list[str], screen_analysis_text: str):
#     """
#     The core of the agent's intelligence, now upgraded with Chain of Thought planning.
#     """
#     print("[Brain] 🧠 Thinking: Deconstructing goal and forming a plan...")
    
#     action_history = "\n".join(f"{i+1}. {action}" for i, action in enumerate(history))

#     # --- THIS IS THE NEW, SMARTER BRAIN ---
#     system_prompt = f"""
#     You are an expert AI agent controlling a computer. Your decisions are driven by a structured planning process.

#     **Your Reasoning Process: Chain of Thought (CoT) Planning**
#     Before deciding on an action, you MUST reason step-by-step. This is your internal monologue and is CRITICAL for success.

#     1.  **Deconstruct Goal:** What is the ultimate objective and all its parts?
#         * *Example Goal:* "Open WhatsApp and say 'all the best' to the contact 'Nothing'."
#         * *Deconstruction:* I need to navigate to the WhatsApp app, find a specific contact named 'Nothing', and then type a specific message into the chat with them.

#     2.  **Formulate a High-Level Plan:** Create a checklist of actions to reach the goal.
#         * *Example Plan:*
#             1. Open the 'WhatsApp' application.
#             2. Find the search bar to look for contacts.
#             3. Type 'Nothing' into the search bar.
#             4. Click on the 'Nothing' contact in the search results.
#             5. Find the message input field.
#             6. Type 'all the best' into the message field.
#             7. Press enter to send.

#     3.  **Execute Next Step:** Compare your plan to the current screen. What is the single next action required to advance your plan?
#         * *Example Screen Analysis:* "I see the main WhatsApp window with a list of recent chats. I see a search bar with the text 'Search or start new chat'."
#         * *Example Decision:* My plan says the next step is to find the search bar. The screen confirms it's there. Therefore, the correct action is `click_text(text='Search or start new chat')`.

#     **Application Selection Logic:**
#     - **Specific App First:** If the goal names an app (e.g., 'WhatsApp'), prioritize `open_app`.
#     - **Browser for Web Tasks:** For generic web tasks (e.g., 'search for...'), use `open_app(app_name='{DEFAULT_BROWSER}')`.
#     - **Terminal for Commands:** For command-line tasks, use `open_app(app_name='{TERMINAL_APP}')`.

#     **Available Actions:**
#     - `open_app(app_name='...')`: Opens an application.
#     - `click_text(text='...')`: Clicks on-screen text. This is for navigation and pressing buttons.
#     - `type(text='...')`: Types text into a field you have ALREADY FOCUSED ON by clicking.
#     - `hotkey(hotkey_str='...')`: Presses a key combination (e.g., 'enter').
#     - `stop(reason='...')`: Stops when the plan is complete or you are irrecoverably stuck.
#     - `click(x=..., y=...)`: Fallback for clicking non-text elements, based on your plan.

#     **CRITICAL RULES:**
#     1.  Your response MUST BE ONLY the single function call for the next step in your plan. NO MARKDOWN, NO EXPLANATIONS.
#     2.  **Stick to the plan.** Do not get distracted by elements on the screen that are not part of your current step. If your plan is to type, then `type()`. Don't click something else.
#     """

#     user_prompt = f"""
#     My Goal: "{goal}"

#     My Recent Action History:
#     ---
#     {action_history if action_history else "No plan initiated yet."}
#     ---

#     Current Screen Content:
#     ---
#     {screen_analysis_text}
#     ---

#     Following my internal Chain of Thought plan, what is the single, exact command I must run now?
#     """

#     try:
#         response = client.chat.completions.create(
#             model="gpt-4o",
#             messages=[
#                 {"role": "system", "content": system_prompt},
#                 {"role": "user", "content": user_prompt},
#             ],
#             temperature=0.0,
#             max_tokens=200,
#         )
#         action_str = response.choices[0].message.content.strip()
        
#         match = re.search(r"(\w+\(.*\))", action_str)
#         if match:
#             cleaned_action_str = match.group(1)
#             print(f"[Brain] ✅ Plan step decided: {cleaned_action_str}")
#             return cleaned_action_str
#         else:
#             return "stop(reason='Could not parse LLM response.')"

#     except Exception as e:
#         return f"stop(reason='LLM API error: {e}')"


# async def run_agent_loop():
#     """The main SEE-THINK-ACT loop of the agent."""
    
#     goal = input("Please enter your high-level goal: ")
#     print(f"[Agent] Roger that. Working on goal: '{goal}'")

#     action_history = []

#     for i in range(20): # Increased step limit for more complex tasks
#         print(f"\n--- Step {i+1} ---")

#         # --- 1. SEE ---
#         print("[Agent] 👀 Analyzing the screen...")
#         screen_analysis_result = use_computer(action="analyze_screen")
        
#         if screen_analysis_result['status'] != 'success':
#             print("[Agent] ❌ Error: Could not see the screen. Stopping.")
#             break
            
#         screen_content = screen_analysis_result['content'][0]['text']

#         # --- 2. THINK ---
#         action_str = get_next_action_from_llm(goal, action_history, screen_content)
        
#         # --- 3. ACT ---
#         if not action_str or action_str.startswith("stop"):
#             print(f"[Agent] ⏹️  Stopping. LLM reason: {action_str}")
#             break
        
#         try:
#             action_history.append(action_str)
#             if len(action_history) > 5: # Keep a slightly longer history
#                 action_history.pop(0)

#             # --- ROBUST PARSER ---
#             action_name = action_str.split("(", 1)[0]
#             args_str = action_str[len(action_name)+1:-1]
            
#             args = {}
#             if args_str:
#                 for arg in re.split(r',\s*(?![^"]*"(?:(?:[^"]*"){2})*[^"]*$)', args_str):
#                     if '=' in arg:
#                         key, value = arg.split('=', 1)
#                         key = key.strip()
#                         value = value.strip().strip("'\"")
#                         try:
#                             args[key] = int(value)
#                         except ValueError:
#                             args[key] = value
#                     else:
#                         print(f"[Agent] ❌ Malformed argument from LLM: '{arg}'. Skipping action.")
#                         continue


#             print(f"[Agent] 🦾 Executing: {action_name} with arguments {args}")

#             # --- SEMANTIC ACTION HANDLER ---
#             if action_name == "click_text":
#                 text_to_click = args.get("text")
#                 if not text_to_click:
#                     raise ValueError("Missing 'text' argument for click_text")
                
#                 coords = find_element_coordinates(screen_content, text_to_click)
#                 if coords:
#                     use_computer(action='click', x=coords['x'], y=coords['y'])
#                 else:
#                     print(f"[Agent] ❌ Action Failed: Could not find text '{text_to_click}' on the screen.")
#                     action_history[-1] = f"FAILED: {action_history[-1]}"
#             else:
#                 # Execute all other actions directly
#                 use_computer(action=action_name, **args)
            
#             await asyncio.sleep(2.5)

#         except Exception as e:
#             print(f"[Agent] ❌ Error executing action '{action_str}': {e}")
#             break

#     print("\n[Agent] Loop finished.")

# if __name__ == "__main__":
#     asyncio.run(run_agent_loop())



###aws based 

import os
import json
import asyncio
import re
import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv
from strands_tools.use_computer import use_computer

# Load environment variables from .env file
load_dotenv()

os.environ["BYPASS_TOOL_CONSENT"] = "true"

# --- AWS Bedrock Client Initialization ---
try:
    aws_region = os.getenv("AWS_REGION", "us-east-1")
    bedrock_client = boto3.client(service_name='bedrock-runtime', region_name=aws_region)
except Exception as e:
    print(f"FATAL ERROR: Could not initialize AWS Bedrock client: {e}")
    print("Please ensure your AWS credentials and region are configured correctly.")
    exit()


# --- HELPER FUNCTIONS FOR SEMANTIC ACTIONS ---

def parse_screen_into_elements(screen_analysis_text: str):
    """Parses raw screen analysis text into a structured list of UI elements."""
    elements = []
    try:
        pattern = re.compile(r"Text: '(.*?)'.*?Center: \((\d+), (\d+)\)", re.DOTALL)
        matches = pattern.finditer(screen_analysis_text)
        for match in matches:
            text = match.group(1).strip()
            x = int(match.group(2))
            y = int(match.group(3))
            if text:
                elements.append({'text': text, 'x': x, 'y': y})
    except Exception as e:
        print(f"[Helper] Error parsing screen elements: {e}")
    return elements

def find_best_match_element(elements: list, keywords_str: str):
    """Finds the single best element from a list that matches the most keywords."""
    keywords = keywords_str.lower().split()
    if not keywords: return None

    best_match = {'score': 0, 'element': None}

    for element in elements:
        element_text_lower = element['text'].lower()
        score = 0
        for keyword in keywords:
            if keyword in element_text_lower:
                score += 1
        
        if score > best_match['score']:
            best_match['score'] = score
            best_match['element'] = element

    if best_match['element']:
        print(f"[Helper] Best match found: '{best_match['element']['text']}' with score {best_match['score']}")
        return best_match['element']
    
    return None

def find_exact_match_element(elements: list, text_to_find: str):
    """Finds an element by matching the exact text, case-insensitively."""
    text_to_find_lower = text_to_find.lower()
    for element in elements:
        if element['text'].lower() == text_to_find_lower:
            return element
    return None

def get_next_action_from_llm(goal: str, history: list[str], screen_analysis_text: str):
    """The agent's brain, upgraded with a web-browsing workflow."""
    print("[Brain] 🧠 Thinking with AWS Bedrock: Following web-aware workflow...")
    
    action_history = "\n".join(f"{i+1}. {action}" for i, action in enumerate(history))
    model_id = "anthropic.claude-3-sonnet-20240229-v1:0"

    system_prompt = f"""
    You are a methodical AI agent controlling a computer. You MUST follow a strict, multi-level workflow to achieve the user's goal, especially for web tasks.

    **Your Strict Step-by-Step Workflow:**

    1.  **Step 1: Application Check.**
        - Is the correct application (e.g., 'Google Chrome') open?
        - If NO: Your ONLY action is `open_app(app_name='...')`.

    2.  **Step 2: Website Check (for Web Goals).**
        - If the goal involves a website, analyze the screen. Am I on the correct URL (e.g., makemytrip.com)?
        - If NO: Your ONLY action is `browse(url='...')`. Do not try to click elements that don't exist yet.

    3.  **Step 3: On-Page Navigation & Interaction.**
        - Once you are on the correct application and website, you can navigate and interact.
        - Use `click_text(text='...')` for static, reliable UI elements (e.g., 'Flights', 'Search', 'Login').
        - Use `click_keywords(keywords='...')` to find and click dynamic or complex elements (e.g., a specific search result, a calendar date).
        - Use `type(text='...')` to fill in text fields like 'From', 'To', or search bars.

    4.  **Step 4: Self-Correction.**
        - If an action FAILS, do not repeat it. Re-analyze the screen from Step 1 and decide on a new, different action.

    **Available Actions:**
    - `open_app(app_name='...')`: Opens an application.
    - `browse(url='...')`: Navigates the current browser to a specific URL. CRITICAL for web tasks.
    - `click_text(text='...')`: Clicks an element with exact text.
    - `click_keywords(keywords='...')`: Clicks the element that best matches a set of keywords.
    - `type(text='...')`: Types text into the focused element.
    - `hotkey(hotkey_str='...')`: Presses a key combination (e.g., 'enter').
    - `stop(reason='...')`: Stops when the goal is achieved or you are stuck.

    **CRITICAL RULES:**
    1.  Always respond with ONLY the function call. No explanations.
    2.  Follow the workflow in order. Do not skip from `open_app` to `click_keywords` on a website task. You MUST use `browse` in between.
    3.  For `click_keywords`, provide a simple space-separated string of words (e.g., `keywords='flights from delhi'`). DO NOT use brackets `[]` or commas in the value.
    """

    user_prompt = f"""
    My Goal: "{goal}"

    My Recent Action History:
    ---
    {action_history if action_history else "No actions taken yet."}
    ---

    Current Screen Content:
    ---
    {screen_analysis_text}
    ---

    Following the strict workflow, what is the single, logical next command I must run?
    """
    
    body = json.dumps({
        "anthropic_version": "bedrock-2023-05-31", "max_tokens": 200, "system": system_prompt,
        "messages": [{"role": "user", "content": user_prompt}]
    })
    
    try:
        response = bedrock_client.invoke_model(body=body, modelId=model_id)
        response_body = json.loads(response.get('body').read())
        action_str = response_body['content'][0]['text'].strip()
        match = re.search(r"(\w+\(.*\))", action_str)
        if match:
            cleaned_action_str = match.group(1)
            print(f"[Brain] ✅ Bedrock decided: {cleaned_action_str}")
            return cleaned_action_str
        return "stop(reason='Could not parse LLM response.')"
    except ClientError as e:
        return f"stop(reason='Bedrock API error: {e.response['Error']['Message']}')"


async def run_agent_loop():
    """The main SEE-THINK-ACT loop of the agent."""
    goal = input("Please enter your high-level goal: ")
    print(f"[Agent] Roger that. Working on goal: '{goal}'")
    action_history = []

    for i in range(20): # Increased step limit for more complex tasks
        print(f"\n--- Step {i+1} ---")

        if len(action_history) >= 3 and action_history[-1] == action_history[-2] == action_history[-3] and "FAILED" in action_history[-1]:
            print("[Agent] 🚨 Detected a repeating failure loop. Stopping.")
            break

        print("[Agent] 👀 Analyzing the screen...")
        screen_analysis_result = use_computer(action="analyze_screen")
        if screen_analysis_result['status'] != 'success':
            print("[Agent] ❌ Error: Could not see the screen. Stopping.")
            break
        screen_content = screen_analysis_result['content'][0]['text']
        screen_elements = parse_screen_into_elements(screen_content)

        action_str = get_next_action_from_llm(goal, action_history, screen_content)
        
        if not action_str or action_str.startswith("stop"):
            print(f"[Agent] ⏹️  Stopping. Reason: {action_str}")
            break
        
        try:
            action_history.append(action_str)
            if len(action_history) > 5: action_history.pop(0)

            action_name = action_str.split("(", 1)[0]
            args_str = action_str[len(action_name)+1:-1]
            args = {}
            if args_str:
                # Robustly parse key-value arguments
                for part in re.split(r",\s*(?=\w+=)", args_str):
                    if '=' in part:
                        key, value = part.split('=', 1)
                        args[key.strip()] = value.strip().strip("'\"")

            print(f"[Agent] 🦾 Executing: {action_name} with arguments {args}")

            action_successful = False
            # --- ACTION EXECUTION LOGIC ---
            if action_name == "click_text":
                element = find_exact_match_element(screen_elements, args.get("text", ""))
                if element:
                    use_computer(action='click', x=element['x'], y=element['y'])
                    action_successful = True
            elif action_name == "click_keywords":
                element = find_best_match_element(screen_elements, args.get("keywords", ""))
                if element:
                    use_computer(action='click', x=element['x'], y=element['y'])
                    action_successful = True
            else:
                # Direct passthrough for other actions like browse, type, open_app
                use_computer(action=action_name, **args)
                action_successful = True

            if not action_successful:
                print(f"[Agent] ❌ Action Failed: '{action_name}' could not find its target.")
                action_history[-1] = f"FAILED: {action_history[-1]}"

            await asyncio.sleep(3) # Slightly longer sleep for web pages to load
        except Exception as e:
            action_history[-1] = f"FAILED: {action_history[-1]} (Exception: {e})"
            print(f"[Agent] ❌ Error executing action '{action_str}': {e}")
            await asyncio.sleep(1)

    print("\n[Agent] Loop finished.")

if __name__ == "__main__":
    asyncio.run(run_agent_loop())