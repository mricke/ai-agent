import os
from dotenv import load_dotenv
from pydantic import BaseModel
import yaml
from openai import OpenAI
import json
import argparse
from prompt_toolkit import prompt
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompts import system_prompt
from call_function import available_functions, call_function

class AgentConfig(BaseModel):
    model_name: str
    base_url: str
    api_key: str
    working_directory: str
    chat_log_file_path: str
    temperature: float
    reasoning_effort: str

def write_to_chat_log(log_path: str, content: str) -> None:
    with open(log_path, 'a') as f:
        f.write(content)
    f.closed

def load_config(path: str) -> AgentConfig:
    with open(path, 'r') as f:
        data = yaml.safe_load(f)
    return AgentConfig(**data['AgentConfig'])

config = load_config("config.yaml")

def assistant_schema_append_tools(tool_calls: object, messages: list) -> None:
    tool_call_lst: list = []
    for tool_call in tool_calls:
        tool_call_lst.append({"id": tool_call.id, "type": tool_call.type, "function": \
                              {"name": tool_call.function.name, "arguments": tool_call.function.arguments}})
    messages.append({"role": "assistant", "content": None, "tool_calls": tool_call_lst})

def main():
    parser = argparse.ArgumentParser(description="Chatbot")
    # vvv Useful in overriding the working directory, otherwise defined in config.yaml
    parser.add_argument("-w", "--working_dir", type=str, default=config.working_directory, \
                        help="The directory where tools will run.")
    parser.add_argument("-q", "--quiet", action="store_true", help="Disables chat log output")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output")
    args = parser.parse_args()

    if not args.quiet:
        history = FileHistory('.history.txt')
        session = PromptSession(history=history)
    else:
        session = PromptSession()

    load_dotenv()
    api_key = os.environ.get(config.api_key)
    if api_key == None:
        raise Exception(f"{config.api_key} not found in .env")

    client = OpenAI(
        base_url=config.base_url,
        api_key=api_key,
    )

    token_usage = {"prompt": 0, "completion": 0}

    messages = [
        {"role": "system", "content": system_prompt},
    ]

    # I need a sort of HItL style control-flow
    for api_request in range(20):

        user_prompt: str = session.prompt("\n> ")
        print("")
        if user_prompt == "/q" or user_prompt == "quit":
            exit(0)

        messages.append({"role": "user", "content": user_prompt})

        response = client.chat.completions.create(
            model=config.model_name,
            messages=messages,
            tools=available_functions,
            #temperature=0,
            reasoning_effort=config.reasoning_effort,
        )
    
        message = response.choices[0].message 

        if response.usage == None:
            print("\nNo response returned from API request.")
            exit(1)
        elif message.tool_calls and api_request == 19 and args.verbose:
            print("\nMaxed out on API requests.")
            print(f'Prompt tokens: {token_usage["prompt"]}')
            print(f"Response tokens: {token_usage["completion"]}")
            exit(1)
        elif message.tool_calls and api_request == 19:
            print("\nMaxed out on API requests.")
            exit(1)
        match args.verbose, message.tool_calls:
            case True, None:
                token_usage["prompt"] += response.usage.prompt_tokens
                token_usage["completion"] += response.usage.completion_tokens
                print(f'Prompt tokens: {response.usage.prompt_tokens}')
                print(f"Response tokens: {response.usage.completion_tokens}\n")
                print(f"Response:\n\n{message.content}")
                if not args.quiet: write_to_chat_log(config.chat_log_file_path, f'Assistant:\n\n{message.content}\n\n')
                messages.append({"role": "assistant", "content": message.content})

            case False, None:
                print(f"Response:\n\n{message.content}")
                if not args.quiet: write_to_chat_log(config.chat_log_file_path, f'Assistant:\n\n{message.content}\n\n')
                messages.append({"role": "assistant", "content": message.content})

            case True, list:
                token_usage["prompt"] += response.usage.prompt_tokens
                token_usage["completion"] += response.usage.completion_tokens
                print(f'Prompt tokens: {response.usage.prompt_tokens}')
                print(f"Response tokens: {response.usage.completion_tokens}\n")
                assistant_schema_append_tools(message.tool_calls, messages)

                for tool_call in message.tool_calls:
                    function_args = json.loads(tool_call.function.arguments or "{}")
                    result_message = call_function(tool_call, args.working_dir, verbose=True)
                    messages.append(result_message)
                    print(f"\nResponse:\n\n{result_message["content"]}")
                    if not args.quiet: write_to_chat_log(config.chat_log_file_path, \
                                      f'- Calling function: {tool_call.function.name}({function_args})"):\n\n{result_message["content"]}\n\n')

            case False, list:
                assistant_schema_append_tools(message.tool_calls, messages)
                for tool_call in message.tool_calls:
                    function_args = json.loads(tool_call.function.arguments or "{}")
                    result_message = call_function(tool_call, args.working_dir)
                    messages.append(result_message)
                    print(f"\nResponse:\n\n{result_message["content"]}")
                    if not args.quiet: write_to_chat_log(config.chat_log_file_path, \
                                      f'- Calling function: {tool_call.function.name}"):\n\n{result_message["content"]}\n\n')


if __name__ == "__main__":
    main()
