import os
import subprocess

schema_run_python_file = {
    "type": "function",
    "function": {
        "name": "run_python_file",
        "description": "runs python file from supplied file path relative to working directory with optional arguments",
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "file path of python file to be run, relative to the working directory",
                },
                "args": {
                    "type": "array",
                    "description": "Optional arguments that can be supplied to python script",
                },
            },
        },
    },
}

def run_python_file(
    working_directory: str, file_path: str, args: list[str] | None = None
) -> str:
    try:
        working_dir_abs: str = os.path.abspath(working_directory)
        target_file: str = os.path.normpath(os.path.join(working_dir_abs, file_path))
        # Will be True or False
        valid_target_file = os.path.commonpath([working_dir_abs, target_file]) == working_dir_abs
        if not valid_target_file:
            return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'
        if not os.path.isfile(target_file):
            return f'Error: "{file_path}" does not exist or is not a regular file'
        if not target_file.endswith(".py"):
            return f'Error: "{file_path}" is not a Python file'

        command = ["python", target_file]
        if type(args) == list:
            command.extend(args)

        ex_command = subprocess.run(command, capture_output=True, text=True, timeout=30)

        if ex_command.returncode != 0:
            return f'Process exited with code {ex_command.returncode}'
        if len(ex_command.stdout) == 0 and len(ex_command.stderr) == 0:
            return "No output produced"

        output_str: str = ""

        if len(ex_command.stdout) > 0:
            output_str += f'STDOUT: {ex_command.stdout}'
        if len(ex_command.stderr) > 0:
            output_str += f'\nSTDERR: {ex_command.stderr}'

        return output_str


    except Exception as e:
        return f'Error: executing Python file {e}'
