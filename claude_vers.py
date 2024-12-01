import os
import subprocess
import anthropic
from dotenv import load_dotenv
from PIL import Image
import pytesseract
import re
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.theme import Theme
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

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

# Load environment variables
BASE_DIRECTORY = os.getcwd()  # Use current working directory at the start

# Define local paths relative to BASE_DIRECTORY
START_DIRECTORY = os.path.join(BASE_DIRECTORY, "access")
PROMPT_FILE = os.path.join(BASE_DIRECTORY, "prompts", "bot.txt")#if you want to change your system prompt, change bot.txt to the name of the new file.
MODEL_NAME = "claude-3-5-sonnet-20240620"
OUTPUT_FILE = os.path.join(BASE_DIRECTORY, "outputs", "conversations.txt")
OCR_OUTPUT = os.path.join(BASE_DIRECTORY, "outputs")
PYTESSERACT_CMD = r"C:\Program Files\Tesseract-OCR\tesseract.exe"  # Path to Tesseract executable

client = anthropic.Anthropic()
pytesseract.pytesseract.tesseract_cmd = PYTESSERACT_CMD

def load_system_prompt():
    try:
        with open(PROMPT_FILE, "r", encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError:
        console.print(f"[error]Prompt file {PROMPT_FILE} not found.[/error]")
        raise
    except Exception as e:
        console.print(f"[error]Error loading system prompt: {str(e)}[/error]")
        raise

def call_api(messages, sys_prompt, MODEL_NAME):
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True
        ) as progress:
            progress.add_task("[info]Calling Claude API...", total=None)
            response = client.messages.create(
                model=MODEL_NAME, 
                max_tokens=1000, 
                temperature=0, 
                system=sys_prompt, 
                messages=messages
            )
        return response.content[0].text
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
        return f"Error: {e.stderr or 'No detailed error provided.'}"
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
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            # Use Syntax for syntax highlighting
            syntax = Syntax(content, "python", theme="monokai", line_numbers=True)
            console.print(Panel(syntax, title=f"File Contents: {file_path}", border_style="blue"))
            return content
    except Exception as e:
        console.print(f"[error]Error reading file: {str(e)}[/error]")
        return f"Error reading file: {str(e)}"

def write_file_contents(mode, file_path, content):
    try:
        content = re.sub(r'(?<!\\)\\n', '\n', content)
        with open(file_path, mode, encoding='utf-8') as file:
            file.write(content)
        console.print(f"[success]File {file_path} written successfully.[/success]")
        return f"File {file_path} written successfully."
    except Exception as e:
        console.print(f"[error]Error writing file: {str(e)}[/error]")
        return f"Error writing file: {str(e)}"

def save_conversation(OUTPUT_FILE, messages):
    try:
        with open(OUTPUT_FILE, "a", encoding='utf-8') as file:
            x = str(messages)
            file.write('{"messages": ' + x + "}")
            file.write("\n")
        console.print("[success]Conversation saved successfully.[/success]")
    except Exception as e:
        console.print(f"[error]Error saving conversation: {str(e)}[/error]")

def perform_ocr(file_path):
    try:
        image = Image.open(file_path)
        text = pytesseract.image_to_string(image)
        output_file_path = file_path.rsplit('.', 1)[0] + "_ocr_result.txt"
        output_file_path = os.path.join(OCR_OUTPUT, os.path.basename(output_file_path))

        with open(output_file_path, 'w', encoding='utf-8') as output_file:
            output_file.write(text)
        
        console.print(Panel(
            f"OCR Result saved to [bold]{output_file_path}[/bold]", 
            title="OCR Complete", 
            border_style="green"
        ))
        return f"OCR performed successfully. Text written to {output_file_path}."
    except Exception as e:
        console.print(f"[error]Error performing OCR: {str(e)}[/error]")
        return f"Error performing OCR: {str(e)}"
    
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
        "Claude Assistant Terminal", 
        title="Welcome", 
        border_style="blue"
    ))

    os.makedirs(START_DIRECTORY, exist_ok=True)

    system_prompt = load_system_prompt()
    
    console.print("[info]Enter your objective:[/info]")
    user_input = console.input("[bold]>>> [/bold]")
    messages = [{"role": "user", "content": [{"type": "text", "text": user_input}]}]

    os.chdir(START_DIRECTORY)

    while True:
        try:
            bot_response = call_api(messages, system_prompt, MODEL_NAME)
            console.print("\n[bold]Bot Response:[/bold]", Panel(bot_response, border_style="green"))

            if bot_response.lower() == "done":
                console.print("[success]Task completed.[/success]")
                messages.append({"role": "assistant", "content": bot_response})
                save_conversation(OUTPUT_FILE, messages)
                break

            command, *args = bot_response.split(maxsplit=1)
            arg = args[0] if args else ""

            if command.lower() == "ocr":
                output = perform_ocr(arg)
            elif command.lower() == "directory":
                output = change_working_directory(arg or ".")
            elif command.lower() == "list":
                output = list_directory_contents(arg or ".")
            elif command.lower() == "read":
                output = read_file_contents(arg)
            elif command.lower() == "write":
                mode, path, *content = arg.split(maxsplit=2)
                content = content[0] if content else ""
                output = write_file_contents(mode, path, content)
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