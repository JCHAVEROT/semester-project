import json
import os
import re
import ast
from openai import OpenAI


PROMPT_PATH = "prompts"
GRAPH_PATH = "graphs"


def load_json_dict(path):
    with open(path, "r") as f:
        return json.load(f)


def strip_json_markers(data: str) -> str:
    return re.sub(r"^```(?:json)?\n|```$", "", data.strip())


def load_prompt(task_type, base_dir=""):
    filename = "data_synthetization.json" if task_type == "Data Synthetization" else "data_augmentation.json"
    path = os.path.join(base_dir, PROMPT_PATH, filename)
    prompt_data = load_json_dict(path)
    prompt_text = prompt_data["prompt"]

    # Insert graph into prompt
    with open(os.path.join(base_dir, GRAPH_PATH, "graph.txt"), "r") as g:
        graph = ast.literal_eval(g.read())
    prompt_text = prompt_text.replace("[GRAPH]", graph)
    
    return prompt_text


def send_to_openai(api_key, model, prompt, user_input):
    client = OpenAI(api_key=api_key)
    response = client.responses.create(
        instructions=prompt,
        model=model,
        input=user_input,
    )
    result = response.to_dict()["output"][0]["content"][0]["text"]
    return strip_json_markers(result)