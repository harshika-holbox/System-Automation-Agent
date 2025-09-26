# import os
# import json
# import asyncio
# import re
# from openai import OpenAI
# from dotenv import load_dotenv
# from strands_tools.use_computer import use_computer
# load_dotenv()


# os.environ["BYPASS_TOOL_CONSENT"] = "true"



# api_key = os.getenv("OPENAI_API_KEY")
# if not api_key:
#     print("FATAL ERROR: OPENAI_API_KEY not found in your .env file or environment variables.")
#     print("Please ensure a .env file is in the same directory with your key, e.g., OPENAI_API_KEY='sk-...'")
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
#     This is the core of our semantic clicking ability.
#     """
#     try:
#         # This regex is robust for finding text and its center coordinates from the formatted string.
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
#     The core of the agent's intelligence, now upgraded for reliability and semantic actions.
#     """
#     print("[Brain] 🧠 Thinking: Analyzing screen and history to decide the next logical step...")
    
#     action_history = "\n".join(f"{i+1}. {action}" for i, action in enumerate(history))

#     system_prompt = f"""
#     You are an expert AI agent controlling a computer to achieve a user's goal.
#     Based on the user's goal, your recent action history, and the current screen content, return the single next action.

#     **Your Reasoning Process:**
#     1.  **Goal Analysis:** What is the core task? Which application is needed (e.g., 'System Settings', 'Google Chrome')?
#     2.  **Screen Analysis:** Am I in the right application? If not, the first step is to open it.
#     3.  **History Review:** What have I tried already? Am I repeating myself? If my last action didn't change the screen, I must try something different.
#     4.  **Action Decision:** Choose the single most logical next step.

#     **Available Actions (Prioritize `click_text` for reliability):**
#     - `click_text(text='...')`:  Finds the specified text on the screen and clicks its center. This is the MOST RELIABLE way to click.
#     - `type(text='...')`: Types the given text into the currently focused input field.
#     - `hotkey(hotkey_str='...')`: Presses a key combination (e.g., 'enter').
#     - `open_app(app_name='...')`: Opens an application.
#     - `stop(reason='...')`: Stops the agent ONLY when the goal is fully achieved or you are stuck.
#     - `click(x=..., y=...)`: As a last resort, if there is no text to identify an element, click specific coordinates.

#     **CRITICAL RULES:**
#     1.  Your response MUST BE ONLY the function call, using keyword arguments (e.g., `text=...`). NO MARKDOWN, NO EXPLANATIONS.
#     2.  PREFER `click_text` over `click(x, y)`.
#     3.  If you are stuck in a loop, you MUST return `stop(reason='Stuck in a loop.')`.
#     """

#     user_prompt = f"""
#     My Goal: "{goal}"

#     My Recent Action History:
#     ---
#     {action_history if action_history else "No actions taken yet."}
#     ---

#     Current Screen Content:
#     ---
#     {screen_analysis_text}
#     ---

#     Based on my goal, history, and the screen, what is the single, exact command I should run next?
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
#             print(f"[Brain] ✅ LLM decided: {cleaned_action_str}")
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

#     for i in range(15):
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
#             if len(action_history) > 4:
#                 action_history.pop(0)

#             # --- ROBUST PARSER ---
#             # This parser correctly handles keyword arguments and prevents crashes.
#             action_name = action_str.split("(", 1)[0]
#             args_str = action_str[len(action_name)+1:-1]
            
#             args = {}
#             if args_str:
#                 # This regex correctly splits arguments, respecting quotes.
#                 for arg in re.split(r',\s*(?![^"]*"(?:(?:[^"]*"){2})*[^"]*$)', args_str):
#                     # Ensure the argument is a key-value pair to prevent unpacking errors.
#                     if '=' in arg:
#                         key, value = arg.split('=', 1)
#                         key = key.strip()
#                         # Clean up the value
#                         value = value.strip().strip("'\"")
#                         # Try to convert to int if possible
#                         try:
#                             args[key] = int(value)
#                         except ValueError:
#                             args[key] = value
#                     else:
#                         # Handle cases where the LLM might forget a keyword (less likely with new prompt)
#                         # For now, we will treat this as an error.
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


# --- NEW, MORE ROBUST HELPER FUNCTIONS ---

def parse_screen_into_elements(screen_analysis_text: str):
    """
    Parses the raw screen analysis text into a structured list of UI elements.
    Each element is a dictionary with text and coordinates.
    """
    elements = []
    try:
        # This regex finds all occurrences of a Text element and its corresponding Center coordinates
        pattern = re.compile(r"Text: '(.*?)'.*?Center: \((\d+), (\d+)\)", re.DOTALL)
        matches = pattern.finditer(screen_analysis_text)
        for match in matches:
            text = match.group(1).strip()
            x = int(match.group(2))
            y = int(match.group(3))
            if text: # Only add elements that have text
                elements.append({'text': text, 'x': x, 'y': y})
    except Exception as e:
        print(f"[Helper] Error parsing screen elements: {e}")
    return elements

def find_best_match_element(elements: list, keywords_str: str):
    """
    Finds the single best element from a list that matches the most keywords.
    This is much more resilient to OCR errors than looking for an exact match.
    """
    keywords = keywords_str.lower().split()
    if not keywords:
        return None

    best_match = {'score': 0, 'element': None}

    for element in elements:
        element_text_lower = element['text'].lower()
        score = 0
        for keyword in keywords:
            if keyword in element_text_lower:
                score += 1
        
        # Prioritize elements that match more keywords
        if score > best_match['score']:
            best_match['score'] = score
            best_match['element'] = element

    # Only return a match if at least one keyword was found (score > 0)
    if best_match['element']:
        print(f"[Helper] Best match found: '{best_match['element']['text']}' with score {best_match['score']}")
        return best_match['element']
    
    return None

def find_exact_match_element(elements: list, text_to_find: str):
    """
    Finds an element by matching the exact text, case-insensitively.
    """
    text_to_find_lower = text_to_find.lower()
    for element in elements:
        if element['text'].lower() == text_to_find_lower:
            return element
    return None

def get_next_action_from_llm(goal: str, history: list[str], screen_analysis_text: str):
    """
    The agent's brain, now with a strictly enforced logical workflow.
    """
    print("[Brain] 🧠 Thinking with AWS Bedrock: Following strict step-by-step workflow...")
    
    action_history = "\n".join(f"{i+1}. {action}" for i, action in enumerate(history))
    model_id = "anthropic.claude-3-sonnet-20240229-v1:0"

    system_prompt = f"""
    You are a methodical and precise AI agent controlling a computer. You MUST follow a strict, hierarchical workflow to achieve the user's goal. Do not skip steps.

    **Your Strict Step-by-Step Workflow:**

    1.  **Step 1: Application Check.**
        - Analyze the screen. Is the correct application for the goal (e.g., 'System Settings', 'Google Chrome') currently open and active?
        - If NO: Your ONLY action is `open_app(app_name='...')`. Do nothing else.

    2.  **Step 2: Navigation.**
        - If the correct application is open, but you are not on the right screen/menu, you must navigate.
        - Use `click_text(text='...')` to click on reliable, static UI elements like 'Bluetooth', 'Display', 'Network', 'Settings'. This is the primary tool for navigation.

    3.  **Step 3: Interaction.**
        - ONLY when you are on the correct screen, interact with the specific target.
        - Use `click_keywords(keywords='...')` to find and click on dynamic or complex elements (e.g., a device name, a specific file, a button with changing text like 'Connect' or 'Pair'). This is the primary tool for interaction with the final target.

    4.  **Step 4: Self-Correction.**
        - If an action FAILS, do not repeat it. Re-analyze the screen from Step 1 and decide on a new, different action. For example, if `click_text` fails, maybe the text is slightly different, and `click_keywords` is a better choice for that element.

    **Available Actions:**
    - `open_app(app_name='...')`: **Use first** to get into the right context.
    - `click_text(text='...')`: **Use for navigation** on static menu items.
    - `click_keywords(keywords='...')`: **Use for interaction** with dynamic targets on the correct screen.
    - `type(text='...')`: Types text.
    - `hotkey(hotkey_str='...')`: Presses a key combination (e.g., 'enter').
    - `stop(reason='...')`: Stops when the goal is achieved or you are stuck after multiple different attempts.

    **CRITICAL RULE:** Always respond with ONLY the function call. No explanations. Follow the workflow. Do not jump ahead.
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

    for i in range(15):
        print(f"\n--- Step {i+1} ---")

        # --- Stuck Detector ---
        if len(action_history) >= 3 and action_history[-1] == action_history[-2] == action_history[-3] and "FAILED" in action_history[-1]:
            print("[Agent] 🚨 Detected a repeating failure loop. The same action has failed three times. Stopping.")
            break

        # --- 1. Secrenshorts ..for agent visiblity 
        print("[Agent] 👀 Analyzing the screen...")
        screen_analysis_result = use_computer(action="analyze_screen")
        if screen_analysis_result['status'] != 'success':
            print("[Agent] ❌ Error: Could not see the screen. Stopping.")
            break
        screen_content = screen_analysis_result['content'][0]['text']
        
        # Parse the raw text into a structured list of elements
        screen_elements = parse_screen_into_elements(screen_content)
        if not screen_elements:
            print("[Agent] ⚠️ Warning: Could not parse any interactable elements from the screen.")
            # We still pass the raw content to the LLM so it has some context
            pass


        # --- 2. THINK ---
        action_str = get_next_action_from_llm(goal, action_history, screen_content)
        
        # --- 3. ACT ---
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
                for arg in re.split(r',\s*(?![^"]*"(?:(?:[^"]*"){2})*[^"]*$)', args_str):
                    if '=' in arg:
                        key, value = arg.split('=', 1)
                        args[key.strip()] = value.strip().strip("'\"")

            print(f"[Agent] 🦾 Executing: {action_name} with arguments {args}")

            action_successful = False
            if action_name == "click_text":
                element_to_click = find_exact_match_element(screen_elements, args.get("text", ""))
                if element_to_click:
                    use_computer(action='click', x=element_to_click['x'], y=element_to_click['y'])
                    action_successful = True
            elif action_name == "click_keywords":
                element_to_click = find_best_match_element(screen_elements, args.get("keywords", ""))
                if element_to_click:
                    use_computer(action='click', x=element_to_click['x'], y=element_to_click['y'])
                    action_successful = True
            else:
                use_computer(action=action_name, **args)
                action_successful = True # Assume success for non-click actions for now

            if not action_successful:
                print(f"[Agent] ❌ Action Failed: '{action_name}' could not find its target.")
                action_history[-1] = f"FAILED: {action_history[-1]}"

            await asyncio.sleep(2.5)
        except Exception as e:
            action_history[-1] = f"FAILED: {action_history[-1]} (Exception: {e})"
            print(f"[Agent] ❌ Error executing action '{action_str}': {e}")
            await asyncio.sleep(1)

    print("\n[Agent] Loop finished.")

if __name__ == "__main__":
    asyncio.run(run_agent_loop())



###1st open ai based 
### 2nd aws based 