import os
from dotenv import load_dotenv
from openai import OpenAI
import json
import argparse
from prompts import system_prompt
from call_function import available_functions, call_function

def assistant_schema_append_tools(tool_calls: object, messages: list) -> None:
    tool_call_lst: list = []
    for tool_call in tool_calls:
        tool_call_lst.append({"id": tool_call.id, "type": tool_call.type, "function": \
                              {"name": tool_call.function.name, "arguments": tool_call.function.arguments}})
    messages.append({"role": "assistant", "content": None, "tool_calls": tool_call_lst})

def main():
    parser = argparse.ArgumentParser(description="Chatbot")
    # I want to prompt the user after the loop starts, is neater
    #parser.add_argument("user_prompt", type=str, help="User prompt")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    args = parser.parse_args()

    load_dotenv()
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if api_key == None:
        raise Exception("OPENROUTER_API_KEY not found in .env")

    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )

    token_usage = {"prompt": 0, "completion": 0}

    messages = [
        {"role": "system", "content": system_prompt},
    ]

    # I need a sort of HItL style control-flow
    for api_request in range(20):

        user_prompt: str = input("\n> ")
        print("")
        if user_prompt == "/q" or user_prompt == "quit":
            exit(0)

        messages.append({"role": "user", "content": user_prompt})

        response = client.chat.completions.create(
            model="openrouter/free",
            messages=messages,
            tools=available_functions,
            #temperature=0,
            reasoning_effort="none",
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
                messages.append({"role": "assistant", "content": message.content})

            case False, None:
                print(f"Response:\n\n{message.content}")
                messages.append({"role": "assistant", "content": message.content})

            case True, list:
                token_usage["prompt"] += response.usage.prompt_tokens
                token_usage["completion"] += response.usage.completion_tokens
                print(f'Prompt tokens: {response.usage.prompt_tokens}')
                print(f"Response tokens: {response.usage.completion_tokens}\n")
                assistant_schema_append_tools(message.tool_calls, messages)

                for tool_call in message.tool_calls:
                    function_args = json.loads(tool_call.function.arguments or "{}")
                    result_message = call_function(tool_call, verbose=True)
                    messages.append(result_message)
                    print(f"\nResponse:\n\n{result_message["content"]}")

            case False, list:
                assistant_schema_append_tools(message.tool_calls, messages)
                for tool_call in message.tool_calls:
                    function_args = json.loads(tool_call.function.arguments or "{}")
                    result_message = call_function(tool_call)
                    messages.append(result_message)
                    print(f"Response:\n\n{result_message["content"]}")


if __name__ == "__main__":
    main()
