import editdistance
from datasets import load_dataset
import os
import gdown
import json
from codebleu import calc_codebleu
import evaluate
import numpy as np
from utils import get_node_by_kind, parser

def get_identifier(code):
    root_node = parser.parse(bytes(code, "utf8")).root_node
    identifiers = set([x.text.decode() for x in get_node_by_kind(root_node, kind=["identifier"])])
    return identifiers

def overlap_identifier_rate(generation, solution):
    generation_identifiers = get_identifier(generation)
    solution_identifiers = get_identifier(solution)
    return len(generation_identifiers.intersection(solution_identifiers)) / len(solution_identifiers)

def get_dependency_identifiers(code, entry_point, solution):
    solution_iden = get_identifier(solution)

    root = parser.parse(bytes(code, "utf8"))
    root_node = root.root_node

    dependencies = []

    for node in root_node.children:
        if "import" in node.type:
            for iden in get_node_by_kind(node, kind=["identifier"]):
                dep_iden = iden.text.decode()
                if dep_iden != entry_point and dep_iden in solution_iden:
                   dependencies.append(dep_iden) 
        else:
            dep_iden = get_node_by_kind(node, kind=["identifier"])
            if dep_iden:
                dep_iden = dep_iden[0].text.decode()
                if dep_iden != entry_point and dep_iden in solution_iden:
                    dependencies.append(dep_iden)
    return set(dependencies)
        
def dependencies_rate(gt_dep,pred_dep):
    cnt = 0
    for dep in set(gt_dep):
        if dep in pred_dep:
            cnt += 1

    return cnt /len(set(gt_dep))



src = "./results/examples/execution_rs/repoexec-full-context/BasePrompt-phi-2"
datasrc = load_dataset("Fsoft-AIC/RepoExec")["full_context"]
print(datasrc)

ES = []
CodeBLEU = []
Identifier_rate = []
DEP_rate = []

generations = []
solutions = []

rs_files = sorted([(filename, int(filename.split("_")[1].split(".")[0])) for filename in os.listdir(src) if "passk" not in filename], key=lambda x: x[1])

task_id = 0

for filename, id in rs_files:
    if "passk" in filename:
        continue
    
    ori_solution = datasrc[task_id]["solution"]

    if datasrc[task_id]["target_function_prompt"].strip() not in ori_solution:
        solution = "\n".join(ori_solution.strip().splitlines()[len(datasrc[task_id]["target_function_prompt"].strip().splitlines()):]) 
    else:
        solution = ori_solution.replace(datasrc[task_id]["target_function_prompt"].strip(), "").strip()
    dependencies = get_dependency_identifiers(datasrc[task_id]["prompt"], datasrc[task_id]["entry_point"], solution)
    
    pred_id = 0
    with open(os.path.join(src, filename), "r") as f:
        for line in f:
            data = json.loads(line) # only tanking the 1st solution
            
            ori_generation = data["generation"]

            if datasrc[task_id]["target_function_prompt"].strip() not in ori_generation:
                generation = "\n".join(ori_generation.strip().splitlines()[len(datasrc[task_id]["target_function_prompt"].strip().splitlines()):])         
            else:
                generation = ori_generation.replace(datasrc[task_id]["target_function_prompt"].strip(), "").strip()
            
            if pred_id == 0:
                CodeBLEU.append(calc_codebleu([solution], [generation], lang="python", weights=(0.25, 0.25, 0.25, 0.25), tokenizer=None)["codebleu"])
                ES.append(editdistance.eval(" ".join(solution.split()), " ".join(generation.split())))
                generations.append(" ".join(generation.split()))
                solutions.append(" ".join(solution.split()))
             
            Identifier_rate.append(overlap_identifier_rate(generation=generation, solution=solution))
            if dependencies:
                DEP_rate.append(dependencies_rate(dependencies, get_identifier(generation)))
            pred_id += 1
    task_id += 1

bleu = evaluate.load("bleu")


rs = {
    "ES": np.mean(ES),
    "BLEU": bleu.compute(predictions=generations, references=solutions)['bleu'],
    "CodeBLEU": np.mean(CodeBLEU),
    "Iden rate": np.mean(Identifier_rate),
    "DEP rate": np.mean(DEP_rate)
}

print(json.dumps(rs, indent=4))
with open(os.path.join(src, "not_passk.json"), "w") as f:
    json.dump(rs, f, indent=4) 

# print("ES:", np.mean(ES))
# print("BLEU:", bleu.compute(predictions=generations, references=solutions)['bleu'])
# print("CodeBLEU", np.mean(CodeBLEU))
# print("Iden rate", np.mean(Identifier_rate))
# print("DEP rate", np.mean(DEP_rate))
