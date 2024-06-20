from typing import List, Union, Iterable, Dict
import numpy as np
import os
import json
from datasets import load_dataset

def estimate_pass_at_k(
    num_samples: Union[int, List[int], np.ndarray],
    num_correct: Union[List[int], np.ndarray],
    k: int
) -> np.ndarray:
    """
    Estimates pass@k of each problem and returns them in an array.
    """

    def estimator(n: int, c: int, k: int) -> float:
        """
        Calculates 1 - comb(n - c, k) / comb(n, k).
        """
        if n - c < k:
            return 1.0
        return 1.0 - np.prod(1.0 - k / np.arange(n - c + 1, n + 1))

    if isinstance(num_samples, int):
        import itertools
        num_samples_it = itertools.repeat(num_samples, len(num_correct))
    else:
        assert len(num_samples) == len(num_correct)
        num_samples_it = iter(num_samples)

    return np.array([estimator(int(n), int(c), k) for n, c in zip(num_samples_it, num_correct)])

import argparse
parser = argparse.ArgumentParser()
parser.add_argument('--n_samples', help='full_context | medium_context | short_context', type=int, default=10)
parser.add_argument('--execution_dir', help='outputdir for saving execution results', 
                    default="./results/execution_rs/repo-codegen-full-context-v3/gpt-3.5")
parser.add_argument('--isContained', help='Execute all function (True) or only non-contained function (False)', 
                    action="store_true")


args = parser.parse_args()


k = [1, 5, 10]
n_samples = args.n_samples
isContained = args.isContained
rs_src= args.execution_dir
total, correct = [], []

dataset = load_dataset("Fsoft-AIC/RepoExec")["full_context"]

no_task = 0
contained_func = 0

print(len(os.listdir(rs_src)))
for task in os.listdir(rs_src):

    if "passk" in task:
        continue
    task_id = int(task.split("_")[-1].split(".")[0])
    
    if not isContained and dataset[task_id]["isContained"]:
        contained_func += 1
        continue

    with open(os.path.join(rs_src, task), "r") as f:
        results = [json.loads(dp) for dp in f][:n_samples]

    results = sorted(results, key= lambda x: x["prediction_id"])
    
    passed = [r["passed"] for r in results]

    assert len(passed) == n_samples
    total.append(len(passed))
    correct.append(sum(passed))

    no_task += 1

print("number of task:", no_task)
total = np.array(total)
correct = np.array(correct)

ks = k
pass_at_k = {f"pass@{k}": estimate_pass_at_k(total, correct, k).mean()
                for k in ks if (total >= k).all()}

with open(os.path.join(rs_src, f"passk_{isContained}.json"), "w") as f:
    json.dump(pass_at_k, f)
print(pass_at_k)