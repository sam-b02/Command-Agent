import os
import subprocess
import anthropic
from dotenv import load_dotenv
from PIL import Image
import pytesseract

load_dotenv()

# Constants and configuration
# Core Paths
BASE_DIRECTORY = os.getcwd()  # Project root
START_DIRECTORY = os.path.join(BASE_DIRECTORY, "access")  # Initial working directory
PROMPT_FILE = os.path.join(BASE_DIRECTORY, "prompts", "bot.txt")  # System instructions

# Conversation Management
CONVERSATION_SUMMARY_MAX_LENGTH = 3000  # Token limit before summarization (None to disable summarization)
CONVERSATION_SUMMARY_PATH = os.path.join(BASE_DIRECTORY, "prompts", "summary.txt")

# API Configuration
MODEL_NAME = "claude-3-5-sonnet-20240620"  # Claude model selection

# Output Management
OUTPUT_FILE = os.path.join(BASE_DIRECTORY, "outputs", "conversations.txt")
OCR_OUTPUT = os.path.join(BASE_DIRECTORY, "outputs")
PYTESSERACT_CMD = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Token Limits
OUTPUT_TOKEN_LIMIT = 1000  # Standard response limit
SUMMARY_OUTPUT_TOKEN_LIMIT = 2000  # Summary response limit

client = anthropic.Anthropic()
pytesseract.pytesseract.tesseract_cmd = PYTESSERACT_CMD

def call_api(messages, sys_prompt, tokens=OUTPUT_TOKEN_LIMIT):
    try:
        response = client.messages.create(
            model=MODEL_NAME, 
            max_tokens=tokens, 
            temperature=0, 
            system=sys_prompt, 
            messages=messages
        )
        return response.content[0].text
    except Exception as e:
        print(f"Error in API call: {str(e)}")
        raise

def execute_command(command):
    try:
        result = subprocess.run(command, shell=True, check=True, text=True, capture_output=True)
        return result.stdout if result.stdout else " "
    except subprocess.CalledProcessError as e:
        return f"Error: {e.stderr or 'No detailed error provided.'}"
    except Exception as e:
        return f"Error: {str(e)}"

def list_directory_contents(path='.'):
    try:
        return '\n'.join(os.listdir(path)) if os.listdir(path) else "This directory is empty"
    except Exception as e:
        return f"Error listing directory contents: {str(e)}"

def read_file_contents(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"

def write_file_contents(mode, file_path, content):
    try:
        content = content.replace('\\n', '\n')
        with open(file_path, mode, encoding='utf-8') as file:
            file.write(content)
        return f"File {file_path} written successfully."
    except Exception as e:
        return f"Error writing file: {str(e)}"

def save_conversation(OUTPUT_FILE, messages):
    try:
        os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
        with open(OUTPUT_FILE, "a", encoding='utf-8') as file:
            file.write(f'{{"messages": {str(messages)}}}\n')
    except Exception as e:
        print(f"Error saving conversation: {str(e)}")

def perform_ocr(file_path):
    try:
        image = Image.open(file_path)
        text = pytesseract.image_to_string(image)
        output_file_path = os.path.join(OCR_OUTPUT, os.path.basename(file_path).rsplit('.', 1)[0] + "_ocr_result.txt")

        os.makedirs(OCR_OUTPUT, exist_ok=True)
        with open(output_file_path, 'w', encoding='utf-8') as output_file:
            output_file.write(text)
        
        return f"OCR performed successfully. Text written to {output_file_path}."
    except Exception as e:
        return f"Error performing OCR: {str(e)}"

def change_working_directory(new_dir):
    try:
        os.chdir(new_dir)
        return f"Current working directory changed to: {os.getcwd()}"
    except Exception as e:
        return f"Error changing directory: {str(e)}"

def ask_question(question):
    print(question)
    answer = input(">>> ")
    return answer if answer else "The user did not answer"

def summarize_conversation(messages, message_length):
    initial_message = messages[0]
    summary_prompt = read_file_contents(CONVERSATION_SUMMARY_PATH)
    try:
        summary = call_api(messages, summary_prompt, SUMMARY_OUTPUT_TOKEN_LIMIT)
        if not summary:
            raise ValueError("Empty summary returned from API")
        summary = summary.replace("\\n","\n")
        summary = summary.replace("\n\n", "\n")
        new_message_length = len(str(initial_message)) + len(summary)
        print(f"Messages have been summarized successfully: \n", summary)
        print(f"from {message_length} to {new_message_length} words, a change of {message_length - new_message_length}")
        return [initial_message, {"role": "assistant", "content": summary}], len(str(initial_message)) + len(summary)
    except Exception as e:
        print(f"Warning: Failed to summarize conversation: {e}, original messages will be used (HIGH TOKEN USAGE)")
        return messages, message_length

def main():
    os.makedirs(START_DIRECTORY, exist_ok=True)
    system_prompt = read_file_contents(PROMPT_FILE)
    user_input = input("Enter your objective: ")
    
    messages = [{"role": "user", "content": [{"type": "text", "text": user_input}]}]
    full_messages = messages.copy()
    messages_length = len(user_input)
    
    os.chdir(START_DIRECTORY)

    while True:
        try:
            bot_response = call_api(messages, system_prompt)
            print("\nBot Response:\n", bot_response)

            if bot_response.lower() == "done":
                messages.append({"role": "assistant", "content": bot_response})
                full_messages.append({"role": "assistant", "content": bot_response})
                save_conversation(OUTPUT_FILE, full_messages)
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

            print("\nOutput:\n", output)

            if not output:
                output = "output was empty"

            messages.append({"role": "assistant", "content": bot_response})
            messages.append({"role": "user", "content": output})
            full_messages.append({"role": "assistant", "content": bot_response})
            full_messages.append({"role": "user", "content": output})
            
            messages_length += len(bot_response) + len(output)

            print(f"\n {messages_length} tokens have been reached. \n")

            if CONVERSATION_SUMMARY_MAX_LENGTH is not None and messages_length >= CONVERSATION_SUMMARY_MAX_LENGTH:
                print(f"\nReached {int(messages_length)} estimated tokens, summarizing conversation...")
                messages, messages_length = summarize_conversation(messages, messages_length)
                full_messages.append({"role": "assistant", "content": "Conversation summarized:" + messages[1]["content"]})



        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"Error: {str(e)}")
            save_conversation(OUTPUT_FILE, full_messages)
            break

        
if __name__ == "__main__":
    main()