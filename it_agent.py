from strands import Agent, tool
from strands_tools import current_time, calculator, shell, use_agent
from dotenv import load_dotenv
import os

# --- Load API key from .env ---
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY  # Strands picks it up automatically

# --- Custom Troubleshooting Tools ---
@tool
def bluetooth_connectivity() -> str:
    result = shell("system_profiler SPBluetoothDataType | grep 'Connectable'")
    return f"Bluetooth Status:\n{result}"

@tool
def audio_connectivity() -> str:
    result = shell("system_profiler SPAudioDataType | grep 'Output Device'")
    return f"Audio Devices:\n{result}"

@tool
def wifi_troubleshoot() -> str:
    result = shell("/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport -I | grep 'SSID'")
    return f"Wi-Fi Status:\n{result}"

# --- Create the Agent ---
agent = Agent(
    tools=[current_time, calculator, shell, bluetooth_connectivity, audio_connectivity, wifi_troubleshoot, use_agent]
)

# --- Interactive usage ---
if __name__ == "__main__":
    print("🤖 IT Support Agent Ready! Type 'exit' to quit.\n")
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            break
        
        # use_agent dynamically picks tools based on the query
        response = agent.tool.use_agent(
            system_prompt=(
                "You are an IT Support Agent. "
                "Based on the user's query, decide which of the available tools to run and return the results."
            ),
            prompt=user_input,
            available_tools=[current_time, calculator, shell, bluetooth_connectivity, audio_connectivity, wifi_troubleshoot]
        )
        print(response)

