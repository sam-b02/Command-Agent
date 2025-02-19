# Command Agent

**Command Agent** is a python script that simulates a command-line interface which allows for LLM APIs to interact with your system and perform various system tasks. 

# Pointing out the obvious

This is completely unsafe and very stupid. There are no guardrails whatsoever. You are giving an LLM absolute control over your PC. Fun, but would not recommend you do this if you have anything valuable on your PC. 

## Requirements

### Prerequisites
- **Os**: Windows
- **Python**: >= 3.8
- **Tesseract OCR**: Installed and configured (update `PYTESSERACT_CMD` if necessary).
- **Claude API Access**: Valid API key loaded via `.env`.

### Python Libraries
Install dependencies via pip:
```bash
pip install anthropic python-dotenv rich pytesseract pillow
```

## Setup

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/sam-b02/Command-Agent
   cd Command-Agent
   ```

2. **Set Up Environment Variables**:
   - Create a `.env` file in the root directory.
   - Follow the structure of .env.example 
   - Add your Claude API key:
     ```plaintext
     ANTHROPIC_API_KEY=<your_api_key>
     ```

3. **Configure Paths**:
   - Ensure `PYTESSERACT_CMD` matches your local Tesseract OCR installation path.

## Usage

1. **Run the Program**:
   ```bash
   python claude_vers.py
   ```

2. **Interact via Console**:
   - The terminal prompts for your objective.
   - The bot will then gain control of your cmd, allowing it to accomplish the objective you give it.

3. **Supported Commands**:
   - **OCR**: `ocr <file_path>` - Extract text from an image.
   - **Directory**: `directory <path>` - Change the working directory.
   - **List**: `list <path>` - List directory contents.
   - **Read**: `read <file_path>` - Display file content with syntax highlighting.
   - **Write**: `write <mode> <file_path> <content>` - Write to a file (modes: `w`, `a`).
   - **Question**: `question <prompt>` - Ask for user input interactively.
   - Any valid shell command.

   Please Note - the bot cannot interact with any python file that requires inputs as of now. You will be forced to restart the program.

4. **Exit the Program**:
   - Press `Ctrl+C` at any time to exit.


## File Structure

```
project_root/
├── access/               # Default working directory
├── outputs/              # Contains saved conversations and OCR results
├── prompts/              # Directory for prompt files (e.g., `bot.txt`, `explore.txt`)
├── .env                  # Environment variables
├── main.py            # Claude version of the script
```

## Customization

1. **Choose System prompt**:
   - change `PROMPT_FILE` to one of two system prompts, located in the prompts directory


## License

The license for this project can be found [here.](LICENSE)

Ensure compliance with Tesseract's and Anthropic's licensing terms if redistributed.
