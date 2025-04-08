"""Local LLM chat application using Ollama and Flask."""

import subprocess
import time
import os
import sys
import re
import signal
import logging
from flask import Flask, render_template, request, jsonify
from rich.console import Console
from rich.panel import Panel
import ollama

# Configuration
MODEL_NAME = "deepseek-r1:7b"
OLLAMA_PORT = 11434
FLASK_HOST = "0.0.0.0"
FLASK_PORT = 5000
OLLAMA_URL = f"http://localhost:{OLLAMA_PORT}"
OLLAMA_API_URL = f"{OLLAMA_URL}/api"

# Uses Rich console for prettier output
console = Console()

# Disable Flask's default logging
log = logging.getLogger("werkzeug")
log.setLevel(logging.ERROR)

# Initialize Flask app with minimal logging
app = Flask(__name__)
app.logger.disabled = True
cli = sys.modules["flask.cli"]
cli.show_server_banner = lambda *args, **kwargs: None

# Global variable to track ollama process
ollama_process = None


def check_command_exists(command):
    """Check if a command exists in the system."""
    try:
        subprocess.run(
            ["which", command],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        return True
    except subprocess.CalledProcessError:
        return False


def check_ollama_running():
    """Check if Ollama server is running."""
    import ollama

    try:
        # Try to list models to check if Ollama is running
        ollama.list()
        return True
    except Exception:
        return False


def start_ollama_server():
    """Start Ollama server as a background process."""
    console.print("Starting Ollama server...", style="yellow")

    try:
        # Start ollama in background and redirect output
        with open("ollama.log", "w") as log_file:
            process = subprocess.Popen(
                ["ollama", "serve"],
                stdout=log_file,
                stderr=log_file,
                preexec_fn=os.setsid,
            )

        # Wait for Ollama to start
        max_attempts = 10
        attempts = 0
        while attempts < max_attempts:
            if check_ollama_running():
                console.print("✓ Ollama server is running", style="green")
                return process

            console.print("Waiting for Ollama server to start...", style="yellow")
            time.sleep(1)
            attempts += 1

        console.print(
            "Failed to start Ollama server after multiple attempts", style="red"
        )
        return None

    except Exception as e:
        console.print(f"Error starting Ollama server: {e}", style="red")
        return None


def check_model_exists(model_name):
    """Check if the model is already downloaded."""
    try:
        # Get the list of models from Ollama
        models_response = ollama.list()

        # Debug the response structure
        # console.print(f"Models response: {models_response}", style="blue")

        # Extract model names from the response
        model_names = []
        for model in models_response.models:
            # The model itself is an object with a 'model' attribute that contains the name
            model_names.append(model.model)

        # console.print(f"Available models: {model_names}", style="blue")
        return model_name in model_names
    except Exception as e:
        console.print(f"Error checking model existence: {e}", style="red")
        return False


def pull_model(model_name):
    """Pull the specified model."""
    console.print(f"Downloading model '{model_name}'...", style="yellow")
    console.print(
        "This might take several minutes depending on your internet speed.",
        style="yellow",
    )

    try:
        # Run ollama pull with real-time output
        process = subprocess.Popen(
            ["ollama", "pull", model_name],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )

        # Print output in real-time
        for line in iter(process.stdout.readline, ""):
            line = line.strip()
            if line:
                console.print(f"  {line}", style="blue")

        process.stdout.close()
        return_code = process.wait()

        if return_code == 0:
            console.print(
                f"✓ Model '{model_name}' downloaded successfully", style="green"
            )
            return True
        else:
            console.print(f"Failed to download model '{model_name}'", style="red")
            return False

    except Exception as e:
        console.print(f"Error downloading model: {e}", style="red")
        return False


def setup():
    """Set up the Ollama server and model."""
    global ollama_process

    console.print(
        Panel.fit("Local LLM Chat Application", border_style="blue", title="Starting")
    )

    # Check if Ollama is installed
    if not check_command_exists("ollama"):
        console.print(
            "Ollama is not installed. Please install it from https://ollama.ai",
            style="red",
        )
        return False

    console.print("✓ Ollama is installed", style="green")

    # Check if Ollama is already running
    if not check_ollama_running():
        ollama_process = start_ollama_server()
        if not ollama_process:
            return False
    else:
        console.print("✓ Ollama server is already running", style="green")

    # Check if model exists
    if not check_model_exists(MODEL_NAME):
        console.print(f"Model '{MODEL_NAME}' not found locally", style="yellow")
        if not pull_model(MODEL_NAME):
            return False
    else:
        console.print(f"✓ Model '{MODEL_NAME}' is available", style="green")

    return True


def shutdown_server():
    """Shutdown the Ollama server if we started it."""
    global ollama_process
    if ollama_process:
        try:
            os.killpg(os.getpgid(ollama_process.pid), signal.SIGTERM)
            console.print("Ollama server stopped", style="yellow")
        except Exception as e:
            console.print(f"Error stopping Ollama server: {e}", style="red")


def remove_thinking(text):
    """Remove thinking blocks and clean up formatting."""
    # Remove anything between <think> and </think>
    cleaned_text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)  # RegEx - a nessessary evil

    # Fix any multiple consecutive blank lines
    cleaned_text = re.sub(r"\n\s*\n+", "\n\n", cleaned_text)

    # Remove leading/trailing whitespace
    return cleaned_text.strip()


# Flask routes
@app.route("/")
def index():
    """Render the main page."""
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    """Handle chat requests from the frontend."""
    import ollama

    data = request.json
    user_message = data.get("message", "")

    if not user_message.strip():
        return jsonify({"error": "Empty message"}), 400

    try:
        # Use ollama client library instead of direct API requests
        response = ollama.generate(
            model=MODEL_NAME,
            prompt=user_message,
        )

        # Get response from the completion
        llm_response = response.get(
            "response", "Sorry, I could not generate a response."
        )

        # Clean the response by removing thinking blocks and extra whitespace
        llm_response = remove_thinking(llm_response)

        return jsonify({"message": llm_response, "model": "Chompers"})
    except ollama.ResponseError:
        return jsonify(
            {"error": "Failed to connect to Ollama. Is Ollama running?"}
        ), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    try:
        # Setup Ollama and model
        if not setup():
            console.print("Setup failed. Exiting.", style="red")
            sys.exit(1)

        # Start web server
        console.print("\nStarting web server on http://localhost:5000", style="green")
        console.print("Press Ctrl+C to stop the application\n", style="bold")
        app.run(host=FLASK_HOST, port=FLASK_PORT, debug=False, use_reloader=False)

    except KeyboardInterrupt:
        console.print("\nShutting down...", style="yellow")
    except Exception as e:
        console.print(f"\nError: {e}", style="red")
    finally:
        shutdown_server()
        console.print("Application stopped successfully", style="green")
