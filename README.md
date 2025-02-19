# Command Agent

**Command Agent** is a Python framework that enables AI language models (in particular, Claude) to interact with your system through a controlled command-line interface. In short, It serves as a makeshift bridge between file systems and LLMS.

## IMMEDIATE NOTE

### THIS IS A DANGEROUS AND STUPID (albeit funny) THING TO DO. IT DOES NOT HAVE SAFETY CHECKS, IT DOES NOT HAVE SANDBOXING, NOTHING. BE CAREFUL.

## Installation

### System Requirements

Before installing Command Agent, ensure your system meets these prerequisites:

- Operating System: Windows
- Python: Version 3.8 or higher
- Tesseract OCR: Latest stable version
- Claude API Access: Valid API key from Anthropic

### Installation Steps

1. First, clone the repository and navigate to the project directory:
   ```bash
   git clone https://github.com/sam-b02/Command-Agent
   cd Command-Agent
   ```

2. Install the required Python dependencies:
   ```bash
   pip install anthropic python-dotenv Pillow pytesseract
   ```

3. Configure your environment:
   - Create a new `.env` file in the root directory
   - Add your Anthropic API key:
     ```plaintext
     ANTHROPIC_API_KEY=your_key_here
     ```

4. Update the system configuration in the code:
   - Set the correct path for `PYTESSERACT_CMD`
   - Verify all paths in the configuration section match your system

## Usage Guide

### Starting the Agent


1. Customize the program to suit your needs:
   - See Architecture below for specifics

2. Run the program:
   ```bash
   python main.py
   ```

3. Set objectives:
   - Input your objective to give the AI a goal.
   - Monitor the AI as it attempts the task
   - Remember that you can hit Ctrl+C to cancel whatever it's doing, if it's getting out of hand.

## Architecture

Command agent is pretty cool. It's got a bunch of commands and components it can use to accomplish the task you set out.

### Core Components

#### Available Commands

The system supports these primary command categories:

**File Operations:**
```
list [path]           - Display directory contents
read [file_path]      - Show file contents
write [mode] [path] [content] - Write to file
```

**Navigation:**
```
directory            - Show current location
directory [path]     - Change working directory
```

**Document Analysis:**
```
OCR [file_path]  - Performs OCR on file
```

**System Interaction:**
```
question [prompt]    - Request user input for issues
[system command]     - Execute (ANY) valid CMD commands
```

### Configuration

The system uses these important configuration constants:

```python
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
```

## Operating Modes

Command Agent supports two primary operating modes:

1. **Guided Mode**
   - Uses instructions from `bot.txt`
   - Follows specific user objectives
   - Maintains structured command execution
   - Focuses on task completion

2. **Autonomous Mode**
   - Uses instructions from `explore.txt`
   - Performs independent system exploration
   - Much more risk likely - more fun, less work.

## Project Structure

The repository follows this organization:
```
project_root/
├── access/               # Default working directory
├── outputs/             
│   ├── conversations/    # Conversation logs
│   └── analysis/        # Document processing results
├── prompts/             
│   ├── bot.txt          # Guided mode instructions
│   ├── explore.txt      # Autonomous mode instructions
│   └── summary.txt      # Conversation summarization rules
└── .env                 # Environment configuration
```

## Limitations and Considerations

Command Agent has several important limitations to consider:

- Windows-only compatibility
- Cannot run scripts that require inputs
- Absence of sandboxing mechanisms (NONE)
- Memory constraints with large files

## Future Development

Current development priorities include:

- Implementing unified file analysis capabilities
- Adding screen capture functionality
- Developing mouse movement control

## License

This project is licensed under [LICENSE]. When using or redistributing, ensure compliance with all third-party licenses, including:
- Tesseract OCR
- Anthropic's Claude API
- Other included dependencies
