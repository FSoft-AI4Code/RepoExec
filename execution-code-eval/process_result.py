from datasets import load_dataset
import jsonlines, json
import os
from utils import parser, get_node_by_kind
from codetext.parser import PythonParser
import editdistance

import argparse
argument_parser = argparse.ArgumentParser()
argument_parser.add_argument('--dataset_name', default="Fsoft-AIC/RepoExec", type=str)
argument_parser.add_argument('--n_samples', help='full_context | medium_context | short_context', type=int, default=10)
argument_parser.add_argument('--subset', help='full_context | medium_context | short_context', type=str,
                    choices=["full_context", "medium_context", "short_context"])
# parser.add_argument('--run_gt', help='Execute the grouth truth solution', action="store_true")
argument_parser.add_argument('--prediction_dir', help='outputdir from models which contain generation.json file', type=str,
                    default="./results/predictions/repo-codegen-full-context/gpt-3.5")
args = argument_parser.parse_args()


n_samples = args.n_samples
set_name = args.subset
is_gpt = "gpt" in args.prediction_dir.lower()
src = args.prediction_dir
src_rs = os.path.join(src, "generations.json")
save_rs = os.path.join(src, "processed_generations.json")
datasrc = load_dataset(args.dataset_name)[set_name]


basic_import ="""
import sys
sys.path.insert(1, \"{}\")
import unittest, pytest
import math
import random
import re
import copy
import datetime
import itertools
import collections
import heapq
import statistics
import functools
import hashlib
import numpy
import numpy as np
import string
from typing import *
from collections import *
import pickle
import timeout_decorator
"""


with open(src_rs, "r") as f:
    generations = json.load(f)

def fix_import(original_content):
    ori_root = parser.parse(bytes(original_content, "utf8"))
    ori_root_node = ori_root.root_node
    future_imports = [x.text.decode() for x in get_node_by_kind(ori_root_node, kind= ["future_import_statement"])]
    

    if future_imports:
        for import_node in future_imports:
            original_content = original_content.replace(import_node.text.decode(), "")
        return "\n".join(future_imports) + "\n" + basic_import + "\n" + original_content
    else:
        return basic_import + "\n" + original_content

def get_actual_solution(dp):
    root = parser.parse(bytes(dp["check"], "utf8"))
    root_node = root.root_node

    function_nodes = PythonParser.get_function_list(root_node)
    for function_node in function_nodes:
        entry_point = PythonParser.get_function_metadata(function_node, dp["check"])["identifier"]

        if entry_point == dp["entry_point"]:
            return function_node.text.decode()
    return None



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