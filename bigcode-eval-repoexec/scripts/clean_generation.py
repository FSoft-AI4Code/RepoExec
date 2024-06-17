
import json

path = "/cm/archive/namlh35/AI4Code/code-gen-results/gen_results/apps/codellama-7b-sft-nmd2k_apps_rlaif-competition/generations.json"

with open(path, "r") as f:
    gen = json.load(f)

for task_id, task in enumerate(gen):
    for genid, pred in enumerate(task):
        gen[task_id][genid] = pred.split("</s>")[0]


with open("/cm/archive/namlh35/AI4Code/code-gen-results/gen_results/apps/codellama-7b-sft-nmd2k_apps_rlaif-competition/clean_generations.json", "w") as f:
    json.dump(gen, f)