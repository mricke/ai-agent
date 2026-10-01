import os

schema_get_files_info = {
    "type": "function",
    "function": {
        "name": "get_files_info",
        "description": "Lists files in a specified directory relative to the working directory, providing file size and directory status",
        "parameters": {
            "type": "object",
            "properties": {
                "directory": {
                    "type": "string",
                    "description": "Directory path to list files from, relative to the working directory (default is the working directory itself)",
                },
            },
        },
    },
}

def get_files_info(working_directory: str, directory: str = ".") -> str:
    try:
        working_dir_abs: str = os.path.abspath(working_directory)
        target_dir: str = os.path.normpath(os.path.join(working_dir_abs, directory))
        # Will be True or False
        valid_target_dir = os.path.commonpath([working_dir_abs, target_dir]) == working_dir_abs
        if not valid_target_dir:
            return f'Error: Cannot list "{directory}" as it is outside the permitted working directory'
        if not os.path.isdir(target_dir):
            return f'Error: "{directory}" is not a directory'

        # iterate over target_dir to build and return a string of
        # each file in target_dir
        output_str: str = ""
        if directory == ".":
            output_str += "Result for current directory:\n"
        else:
            output_str += f"Result for '{directory}' directory:\n"
        for file in os.listdir(target_dir):
            output_str += f"  - {file}: \
file_size={os.path.getsize(os.path.join(target_dir, file))} \
bytes, is_dir={os.path.isdir(os.path.join(target_dir, file))}\n"
        return output_str[:-1]
    except Exception as e:
        return f'  Error: {e}'
    

