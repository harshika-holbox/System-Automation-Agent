from strands import Agent, tool
from strands_tools import current_time, calculator, shell

# --- Custom Troubleshooting Tools ---

@tool
def bluetooth_connectivity() -> str:
    """
    Troubleshoot Bluetooth connectivity on macOS.
    """
    # Example macOS command to check Bluetooth status
    result = shell("system_profiler SPBluetoothDataType | grep 'Connectable'")
    return f"Bluetooth Status:\n{result}"


@tool
def audio_connectivity() -> str:
    """
    Troubleshoot Audio connectivity on macOS.
    """
    # Example command to list audio devices
    result = shell("system_profiler SPAudioDataType | grep 'Output Device'")
    return f"Audio Devices:\n{result}"


@tool
def wifi_troubleshoot() -> str:
    """
    Troubleshoot Wi-Fi connectivity issues on macOS.
    """
    # Example command to check Wi-Fi status
    result = shell("/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport -I | grep 'SSID'")
    return f"Wi-Fi Status:\n{result}"

# --- Create the Agent with tools ---
agent = Agent(
    tools=[current_time, calculator, shell, bluetooth_connectivity, audio_connectivity, wifi_troubleshoot]
)

# --- Example usage ---
if __name__ == "__main__":
    message = """
    Please perform system troubleshooting:
    1. Check Bluetooth connectivity
    2. Check Audio connectivity
    3. Diagnose Wi-Fi issues
    """
    agent(message)
