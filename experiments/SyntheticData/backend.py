import json
import os
import re
import ast
from openai import OpenAI


PROMPT_PATH = "prompts"
GRAPH_PATH = "graphs"
EVAL_PATH = "eval"


def load_json_dict(path):
    with open(path, "r") as f:
        return json.load(f)


def strip_json_markers(data: str) -> str:
    return re.sub(r"^```(?:json)?\n|```$", "", data.strip())


def load_prompt(task_type, base_dir=""):
    if task_type == "Data Synthetization":
        filename = "data_synthetization.json"
    elif task_type == "Data Augmentation":
        filename = "data_augmentation.json"
    elif task_type == "Curriculum Generation":
        filename = "learning_curriculums.json"
    else:
        raise ValueError(f"Unknown task type: {task_type}")

    path = os.path.join(base_dir, PROMPT_PATH, filename)
    prompt_data = load_json_dict(path)
    prompt_text = prompt_data["prompt"]

    if "[GRAPH]" in prompt_text:
        graph_path = os.path.join(base_dir, GRAPH_PATH, "graph.txt")
        try:
            with open(graph_path, "r") as g:
                graph = ast.literal_eval(g.read())
                prompt_text = prompt_text.replace("[GRAPH]", graph)
        except Exception as e:
            raise RuntimeError(f"Failed to load or parse graph: {e}")

    return prompt_text


def load_questions(base_dir=""):
    path = os.path.join(base_dir, EVAL_PATH, "human_questions_synthetic.json")
    question_text = load_json_dict(path)
    
    return question_text


def send_to_openai(api_key, model, prompt, user_input):
    client = OpenAI(api_key=api_key)
    response = client.responses.create(
        instructions=prompt,
        model=model,
        input=user_input,
    )
    result = response.to_dict()["output"][0]["content"][0]["text"]
    return strip_json_markers(result)