from datasets import load_dataset
import jsonlines, json
import os
from utils import parser, get_node_by_kind
from codetext.parser import PythonParser
import textwrap

import argparse
argument_parser = argparse.ArgumentParser()
argument_parser.add_argument('--dataset_name', default="Fsoft-AIC/RepoExec", type=str)
argument_parser.add_argument('--n_samples', help='full_context | medium_context | short_context', type=int, default=10)
argument_parser.add_argument('--subset', help='full_context | medium_context | short_context', type=str,
                    choices=["full_context", "medium_context", "short_context"])
# parser.add_argument('--run_gt', help='Execute the grouth truth solution', action="store_true")
argument_parser.add_argument('--prediction_dir', help='outputdir from models which contain generation.json file', type=str,
                    default="./results/predictions/repo-codegen-full-context/gpt-3.5")
argument_parser.add_argument('--is_gpt', action="store_true")
argument_parser.add_argument('--is_api', action="store_true")
args = argument_parser.parse_args()


n_samples = args.n_samples
set_name = args.subset
is_api_call = args.is_api
is_gpt = args.is_gpt or is_api_call
src = args.prediction_dir
src_rs = os.path.join(src, "generations.json")
save_rs = os.path.join(src, "processed_generations.json")
datasrc = load_dataset(args.dataset_name)[set_name]

with open(src_rs, "r") as f:
    generations = json.load(f)

def get_actual_solution(dp):
    root = parser.parse(bytes(dp["check"], "utf8"))
    root_node = root.root_node

    function_nodes = PythonParser.get_function_list(root_node)
    for function_node in function_nodes:
        entry_point = PythonParser.get_function_metadata(function_node, dp["check"])["identifier"]

        if entry_point == dp["entry_point"]:
            return function_node.text.decode()
    return None

def gpt_code_parser(response):
    if "```python" in response:
        parsed_code = response[response.index("```python") + len("```python"):]
        return parsed_code[:parsed_code.rfind("```")]
    elif "```" in response:
        parsed_code = response[response.index("```") + len("```"):]
        return parsed_code[:parsed_code.rfind("```")]
    else:
        return response

print(datasrc)
# exit()

wrong_process = 0
processed_generations = []
num_gen_tasks = len(generations)
print(num_gen_tasks)

actual_id = 0
for task_id, generation in enumerate(generations):
    if num_gen_tasks > len(datasrc) and task_id not in datasrc["id"]:
        continue
    
    all_test = []
    all_predictions = []

    if datasrc[actual_id]["solution"] not in datasrc[actual_id]["check"]:
        actual_solution = get_actual_solution(datasrc[actual_id])
    else:
        actual_solution = datasrc[actual_id]["solution"]

    for gen_id, gen_rs in enumerate(generation[:n_samples]):
        if "[/INST]" in gen_rs:
            gen_rs = gen_rs.split("[/INST]")[1].strip()

        if is_gpt:
            if is_api_call:
                if "</think>" in gen_rs["prediction"]:
                    gen_rs["prediction"] = gen_rs["prediction"].split("</think>")[-1]#.replace("        ", "    ")
                if is_instruct:
                    gen_rs = gpt_code_parser(gen_rs["prediction"])
                else:
                    if not gpt_code_parser(gen_rs["prediction"]).strip("\n").startswith("    "):
                        gen_rs = datasrc[actual_id]["target_function_prompt"] + textwrap.indent(gpt_code_parser(gen_rs["prediction"]), prefix="    ")
                    else:
                        gen_rs = datasrc[actual_id]["target_function_prompt"] + gpt_code_parser(gen_rs["prediction"])
            else:
                solution_body = None
                if datasrc[actual_id]["target_function_prompt"].strip() in gen_rs:
                    solution_body = gen_rs[gen_rs.index(datasrc[actual_id]["target_function_prompt"].strip()) + len(datasrc[actual_id]["target_function_prompt"].strip()): ]

                    if not solution_body.startswith("\n    ") and not solution_body.startswith("def") and not solution_body.startswith("\ndef"):
                        solution_body = "\n    " + solution_body.strip()
                    else:
                        solution_body = None
                
                if solution_body is not None:
                    gen_rs = datasrc[actual_id]["target_function_prompt"].strip() + solution_body

                
        solution_fn = None

        try:
            if datasrc[actual_id]["target_function_prompt"].strip() in gen_rs and not is_gpt:
                solution_fn = gen_rs[gen_rs.index(datasrc[actual_id]["target_function_prompt"].strip()): ]
            else:
                root = parser.parse(bytes(gen_rs, "utf8"))
                root_node = root.root_node

                function_nodes = get_node_by_kind(root_node, kind= ["function_definition"])[::-1]
                for function_node in function_nodes:
                    function_name = PythonParser.get_function_metadata(function_node, gen_rs)['identifier']
                    if function_name == datasrc[actual_id]["entry_point"]:
                        solution_fn = function_node.text.decode()
                        break
        except Exception as e:
            print(e)
            solution_fn = ""
            print(actual_id, "cannot find solution for {} for task id {}".format(datasrc[actual_id]["entry_point"], datasrc[actual_id]["id"]))


        if solution_fn is None:
            solution_fn = ""
            print(actual_id, "cannot find solution for {} for task id {}".format(datasrc[actual_id]["entry_point"], datasrc[actual_id]["id"]))

        all_predictions.append(solution_fn)
        test_case = datasrc[actual_id]["check"]

        assert actual_solution in test_case
        test_case = test_case.replace(actual_solution, solution_fn)

        all_test.append(test_case)
        
    processed_generations.append({
        "task_id": actual_id,
        "project": datasrc[actual_id]["project"],
        "module":  datasrc[actual_id]["module"],
        "predictions": all_predictions,
        "test": all_test
        })
    actual_id += 1

with jsonlines.open(save_rs, mode='w') as writer:
    writer.write_all(processed_generations)
