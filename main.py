import os
from dotenv import load_dotenv
from openai import OpenAI
import json
import argparse
from prompts import system_prompt
from call_function import available_functions, call_function

def main():
    parser = argparse.ArgumentParser(description="Chatbot")
    parser.add_argument("user_prompt", type=str, help="User prompt")
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
        {"role": "user", "content": args.user_prompt},
    ]

    for api_request in range(20):
        response = client.chat.completions.create(
            model="openrouter/free",
            messages=messages,
            tools=available_functions,
            temperature=0,
        )
    
        message = response.choices[0].message 

        if response.usage == None:
            print("No response returned from API request.")
            exit(1)
        elif response.choices[0].message.tool_calls and api_request == 19 and args.verbose:
            print("Maxed out on API requests.")
            print(f'Prompt tokens: {token_usage["prompt"]}')
            print(f"Response tokens: {token_usage["completion"]}")
            exit(1)
        elif response.choices[0].message.tool_calls and api_request == 19:
            print("Maxed out on API requests.")
            exit(1)
        elif args.verbose and response.choices[0].message.tool_calls == None:
            token_usage["prompt"] += response.usage.prompt_tokens
            token_usage["completion"] += response.usage.completion_tokens
            print(f"User prompt: {args.user_prompt}")
            print(f'Prompt tokens: {token_usage["prompt"]}')
            print(f"Response tokens: {token_usage["completion"]}")
            print(f"Response:\n{response.choices[0].message.content}")
            break
        elif not args.verbose and response.choices[0].message.tool_calls == None:
            print(f"Response:\n{response.choices[0].message.content}")
            break
        elif args.verbose and response.choices[0].message.tool_calls:
            token_usage["prompt"] += response.usage.prompt_tokens
            token_usage["completion"] += response.usage.completion_tokens
            for tool_call in message.tool_calls:
                function_args = json.loads(tool_call.function.arguments or "{}")
                result_message = call_function(tool_call, verbose=True)
                messages.append(result_message)
        elif not args.verbose and response.choices[0].message.tool_calls:
            for tool_call in message.tool_calls:
                function_args = json.loads(tool_call.function.arguments or "{}")
                result_message = call_function(tool_call)
                messages.append(result_message)

if __name__ == "__main__":
    main()
