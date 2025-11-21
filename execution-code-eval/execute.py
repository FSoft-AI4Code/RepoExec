import os, datasets
import json

import argparse
parser = argparse.ArgumentParser()
parser.add_argument('--subset', help='full_context | medium_context | short_context')
# parser.add_argument('--run_gt', help='Execute the grouth truth solution', action="store_true")
parser.add_argument('--prediction_dir', help='outputdir from models which contain generation.json file', 
                    default="./results/predictions/repo-codegen-full-context-v3/gpt-3.5")
parser.add_argument('--execution_dir', help='outputdir for saving execution results', 
                    default="./results/execution_rs/repo-codegen-full-context-v3/gpt-3.5")


args = parser.parse_args()

pred_dir = args.prediction_dir
save_dir = args.execution_dir
pip_cache_dir = os.path.join(os.getcwd(), "pip_cache")

if not os.path.exists(pip_cache_dir):
    os.makedirs(pip_cache_dir)
if not os.path.exists(save_dir):
    os.makedirs(save_dir)

data = datasets.load_dataset("Fsoft-AIC/RepoExec")
data = data[args.subset]
repo_dir = os.path.dirname(os.getcwd())
print(repo_dir)
print("All task:", len(data))

for task_id in range(len(data)):
    if os.path.exists(os.path.join(save_dir, f"results_{task_id}.jsonl")):
        continue
    project = data[task_id]["project"]

    os.system(f"sudo docker run --rm \
    -v {pred_dir}:/pred_dir:ro \
    -v {save_dir}:/rs_dir \
    -v {repo_dir}:/input:ro \
    -v {repo_dir}/data_with_test_case:/output:ro \
    -v {repo_dir}/{project}/:/package:ro \
    -v {pip_cache_dir}:/root/.cache/pip \
    codeeval-runner --task_id {task_id} --problem_file /pred_dir/processed_generations.json --rs_dir /rs_dir --timeout 120")
