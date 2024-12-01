#NOT UPDATED; USE CLAUDE_VERS.PY INSTEAD

import os
import subprocess
from openai import OpenAI
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
import re

# Load environment variables from .env file
load_dotenv()

# Custom theme for consistent styling
custom_theme = Theme({
    "info": "cyan",
    "warning": "yellow",
    "error": "bold red",
    "success": "bold green"
})

# Initialize console with custom theme
console = Console(theme=custom_theme)

ACCESS_DIRECTORY = "access"
PROMPT_FILE = r"prompts\bot.txt"
MODEL_NAME = "gpt-4o-mini"
OUTPUT_FILE = "conversation.txt"
client = OpenAI()

def load_system_prompt():
    try:
        with open(PROMPT_FILE, "r") as file:
            return file.read()
    except FileNotFoundError:
        console.print(f"[error]Prompt file {PROMPT_FILE} not found.[/error]")
        raise
    except Exception as e:
        console.print(f"[error]Error loading system prompt: {str(e)}[/error]")
        raise

def call_api(messages):
    try:
        response = client.chat.completions.create(model=MODEL_NAME, messages=messages)
        return response.choices[0].message.content
    except Exception as e:
        console.print(f"[error]Error in API call: {str(e)}[/error]")
        raise

def execute_command(command):
    try:
        result = subprocess.run(command, shell=True, check=True, text=True, capture_output=True)
        if len(result.stdout) == 0:
            return " "
        return result.stdout
    except subprocess.CalledProcessError as e:
        console.print(f"[error]Command execution failed: {str(e)}[/error]")
        return f"Error: {e.stderr}"
    except Exception as e:
        console.print(f"[error]An error occurred while executing the command: {str(e)}[/error]")
        return f"Error: {str(e)}"

def list_directory_contents(path='.'):
    try:
        contents = os.listdir(path)
        if contents:
            # Create a rich table for directory contents
            table = Table(title=f"Directory Contents: {path}")
            table.add_column("Name", style="cyan")
            table.add_column("Type", style="magenta")
            
            for item in contents:
                item_path = os.path.join(path, item)
                item_type = "Folder" if os.path.isdir(item_path) else "File"
                table.add_row(item, item_type)
            
            console.print(table)
            return '\n'.join(contents)
        return "This directory is empty"
    except Exception as e:
        console.print(f"[error]Error listing directory contents: {str(e)}[/error]")
        return f"Error listing directory contents: {str(e)}"

def read_file_contents(file_path):
    try:
        with open(file_path, 'r') as file:
            content = file.read()
            # Use Syntax for syntax highlighting
            syntax = Syntax(content, "python", theme="monokai", line_numbers=True)
            console.print(Panel(syntax, title=f"File Contents: {file_path}", border_style="blue"))
            return content
    except Exception as e:
        console.print(f"[error]Error reading file: {str(e)}[/error]")
        return f"Error reading file: {str(e)}"

def write_file_contents(file_path, content):
    try:
        content = re.sub(r'(?<!\\)\\n', '\n', content)
        with open(file_path, 'w') as file:
            file.write(content)
        console.print(f"[success]File {file_path} written successfully.[/success]")
        return f"File {file_path} written successfully."
    except Exception as e:
        console.print(f"[error]Error writing file: {str(e)}[/error]")
        return f"Error writing file: {str(e)}"

def save_conversation(OUTPUT_FILE, messages):
    try:
        os.makedirs(ACCESS_DIRECTORY, exist_ok=True)
        with open(OUTPUT_FILE, "a", encoding='utf-8') as file:
            file.write('{"messages": ' + str(messages) + "}")
            file.write("\n")
        console.print("[success]Conversation saved successfully.[/success]")
    except Exception as e:
        console.print(f"[error]Error saving conversation: {str(e)}[/error]")

def change_working_directory(new_dir):
    if new_dir != ".":
        try:
            os.chdir(new_dir)
            current_dir = os.getcwd()
            console.print(f"[success]Current working directory changed to: [bold]{current_dir}[/bold][/success]")
            return f"Current working directory has been changed to: {current_dir}"
        except FileNotFoundError:
            console.print(f"[error]Error: The directory '{new_dir}' does not exist.[/error]")
            return f"Error: The directory '{new_dir}' does not exist."
        except PermissionError:
            console.print(f"[error]Error: You do not have permission to access '{new_dir}'.[/error]")
            return f"Error: You do not have permission to access '{new_dir}'."
        except Exception as e:
            console.print(f"[error]Error changing directory: {str(e)}[/error]")
            return f"Error changing directory: {str(e)}"
    else:
        current_dir = os.getcwd()
        console.print(f"[info]Current working directory is: [bold]{current_dir}[/bold][/info]")
        return f"Current working directory is: {current_dir}"

def ask_question(question):
    console.print(f"[info]{question}[/info]")
    answer = console.input("[bold]>>> [/bold]")
    return answer if len(answer) != 0 else "The user did not answer"
    
def main():
    # Clear screen and show welcome banner
    console.clear()
    console.print(Panel(
        "AI Command Terminal", 
        title="Welcome", 
        border_style="blue"
    ))

    system_prompt = load_system_prompt()
    messages = [{"role": "system", "content": system_prompt}]

    console.print("[info]Enter your objective:[/info]")
    user_input = console.input("[bold]>>> [/bold]")
    messages.append({"role": "user", "content": user_input})

    os.makedirs(ACCESS_DIRECTORY, exist_ok=True)
    os.chdir(ACCESS_DIRECTORY)

    while True:
        try:
            bot_response = call_api(messages)
            console.print("\n[bold]Bot Response:[/bold]", Panel(bot_response, border_style="green"))

            if bot_response.lower() == "done":
                console.print("[success]Task completed.[/success]")
                messages.append({"role": "assistant", "content": bot_response})
                save_conversation(OUTPUT_FILE, messages)
                break

            command, *args = bot_response.split(maxsplit=1)
            arg = args[0] if args else ""

            if command.lower() == "directory":
                output = change_working_directory(arg)
            elif command.lower() == "list":
                output = list_directory_contents(arg or ".")
            elif command.lower() == "read":
                output = read_file_contents(arg)
            elif command.lower() == "write":
                mode, path, *content = arg.split(maxsplit=2)
                content = content[0] if content else ""
                output = write_file_contents(path, content)
            elif command.lower() == "question":
                output = ask_question(arg)
            else:
                output = execute_command(bot_response)

            console.print(f"\n[info]Output:[/info]", Panel(output, border_style="cyan"))

            if len(output) == 0:
                output = "output was empty"

            messages.append({"role": "assistant", "content": bot_response})
            messages.append({"role": "user", "content": output})

        except KeyboardInterrupt:
            console.print("\n[warning]Exiting...[/warning]")
            break
        except Exception as e:
            console.print(f"[error]Error: {str(e)}[/error]")
            break

if __name__ == "__main__":
    main()