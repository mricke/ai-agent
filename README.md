# AI-agent

An OpenAI compatible Human-in-the-loop AI agent 

Warning: **This is a toy AI agent I have created for personal use. While I have taken reasonable measures to ensure that it only has access to a specified directory, you probably shouldn't run this unless you know what you're doing.**

Currently supports 4 functions:
- list directory contents
- get file contents of plain text files
- write to file
- runs python scripts

### Requirements

Assumes you have [uv](https://docs.astral.sh/uv/getting-started/installation/) installed on your system to manage python dependencies such as:

- python >= 3.13

### Installation

In the root directory run `uv sync`

#### Configuration

This agent requires a config.yaml file in the root directory to work. E.g.:

```
AgentConfig:
  model_name: "openrouter/free"
  base_url: "https://openrouter.ai/api/v1"
  api_key: "OPENROUTER_API_KEY"
  working_directory: "/path/to/directory/tools/have/access/to"
  chat_log_file_path: "/path/to/.chat_log.txt"
  temperature: 0
  reasoning_effort: "none"
```

In the above example, `OPENROUTER_API_KEY` would need to be defined in .env file.

#### Venv

To activate your virtual environment do the following:

##### Linux / MacOS

`source .venv/bin/activate`  (or whichever shell of your choice)

##### Windows

- `.venv\bin\activate.ps1` for powershell
- `.venv\bin\activate.bat` for command prompt

### Example usage

- In the root directory run:
  - `uv run main.py --verbose`
  
- Other options include:
  - `-w`, `--working_dir` to change the directory tools have access to
  - `-q`, `--quiet` to turn off prompt history and chat log
