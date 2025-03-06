import os
import sys
import json
import pandas as pd
import argparse
from string import ascii_uppercase
from tqdm import tqdm
from datasets import load_dataset
import time
import concurrent.futures
from openai import OpenAI

import os
import anthropic


def args():
    opt = argparse.ArgumentParser()
    opt.add_argument("--model", type=str, default="")
    opt.add_argument("--prompt_type", type=str, default="baseprompt")
    opt.add_argument("--save_dir", type=str, default="")
    opt.add_argument("--provider", type=str, choices=["togetherai", "anthropic", "openai"], default="togetherai")
    return opt.parse_args()


def setup_client(provider):
    if provider == "togetherai":
        client = OpenAI(
            api_key=os.environ.get("TOGETHER_API_KEY"),
            base_url="https://api.together.xyz/v1",
        )
    elif provider == "anthropic":
        api_key = os.environ["ANTHROPIC_API_KEY"]
        client = anthropic.Anthropic(api_key=api_key)
    else:
        client = OpenAI(
            api_key=os.environ.get("OPENAI_API_KEY"),
        )

    return client


def request_generate(prompt, client, model, is_anthropic):
    try:
        if not is_anthropic:
            response = client.chat.completions.create(
                            model=model,
                            messages=[{"role": "user", "content": prompt}]
                        )
            answer = response.choices[0].message.content
        else:
            message = client.messages.create(
                model=model,
                max_tokens=4000,
                temperature=0.0,
                system="You are a coding assitant.",
                messages=[{"role": "user", "content": prompt}]
            )
            answer = message.content[0].text
    except:
        answer = ""

    return answer


def get_prompt_base(doc):
    return "Do not response with whole code and only response with the implementation for the `{}` using the below signature.\n\n".format(doc["entry_point"]) + doc["target_function_prompt"]

def get_instruction(doc):
    template = """The provided code snippet includes necessary dependencies for implementing the {function_name} function. Write a Python function {signature} to solve the following problem:"""
    return doc["prompt"].replace(doc["target_function_prompt"].strip(), "") + "\n" + template.format(function_name=doc["entry_point"],  signature=doc["function_signature"][:-1].replace("\\", "").replace("\n", ""))


def get_prompt(doc):
    instruction = get_instruction(doc)
    prompt_base = get_prompt_base(doc)
    context = doc["docstring"]

    inp = instruction + "\n" + context + "\n"
    prompt = inp + prompt_base
    prompt = prompt.strip()
    if doc["id"] == 1:
        print(prompt)
        
    return prompt

def main():
    opt = args()
    is_anthropic= "claude" in opt.model.lower()


    dataset = load_dataset("Fsoft-AIC/RepoExec", split="full_context")

    if opt.prompt_type == "baseprompt":
        prompts = ["Complete below code for function `{}`. Only reponse with the complete part not the whole code or function signature.\n\n{}".format(function_name, code) for function_name, code in zip(dataset["entry_point"], dataset["prompt"])]
        print(prompts[0])
    else:
        prompts = [get_prompt(x) for x in dataset]

    done = []
    if os.path.exists(os.path.join(opt.save_dir, "generations.json")):
        with open(os.path.join(opt.save_dir, "generations.json"), 'r') as f:
            done = json.load(f)
    if done:
        prompts = prompts[done[-1]["task_id"]+1:]

    print(f"Number of prompts: {len(prompts)}")
    bs = 1
    batches = [prompts[i:i+bs] for i in range(0, len(prompts), bs)]

    if not os.path.exists(opt.save_dir):
        os.mkdir(opt.save_dir)

    client = setup_client(opt.provider)

    for batch in tqdm(batches):

        item = request_generate(batch[0], client, opt.model, is_anthropic)

        done.append({"task_id": len(done), "prediction": item})

        with open(os.path.join(opt.save_dir, "generations.json"), "w") as file:
            json.dump(fp=file, indent=4, obj=done)


if __name__ == "__main__":
    main()