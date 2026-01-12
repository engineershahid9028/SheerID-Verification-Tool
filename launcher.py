import subprocess
import os

TOOLS = {
    "boltnew": "boltnew-verify-tool/main.py",
    "canva": "canva-teacher-tool/main.py",
    "k12": "k12-verify-tool/main.py",
    "one": "one-verify-tool/main.py",
    "perplexity": "perplexity-verify-tool/main.py",
    "spotify": "spotify-verify-tool/main.py",
    "veterans": "veterans-verify-tool/main.py",
    "youtube": "youtube-verify-tool/main.py",
}

def run_tool(tool_name):
    tool_name = tool_name.lower()

    if tool_name not in TOOLS:
        return f"❌ Tool '{tool_name}' not found.\nAvailable tools: {', '.join(TOOLS.keys())}"

    script_path = TOOLS[tool_name]

    if not os.path.exists(script_path):
        return f"❌ Script not found: {script_path}"

    try:
        result = subprocess.run(
            ["python", script_path],
            capture_output=True,
            text=True,
            timeout=300
        )
        output = result.stdout + "\n" + result.stderr
        return output.strip() or "✅ Tool finished successfully."

    except Exception as e:
        return f"❌ Error running tool: {str(e)}"
