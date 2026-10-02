# AI-agent

A basic AI agent which uses the Openrouter free-tier.

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

#### Venv

To activate your virtual environment do the following:

##### Linux / MacOS

`source .venv/bin/activate`  (or whichever shell of your choice)

##### Windows

- `.venv\bin\activate.ps1` for powershell
- `.venv\bin\activate.bat` for command prompt

### Example usage

- In the root directory run:
  - `uv run main.py "use get_file_contents on README.md" --verbose`
