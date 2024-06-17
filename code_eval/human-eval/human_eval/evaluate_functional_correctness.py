import fire
import sys

from human_eval.data import HUMAN_EVAL
from human_eval.evaluation import evaluate_functional_correctness


def entry_point(
    task_id: int,
    k: str = "1,10,100",
    n_workers: int = 4,
    timeout: float = 3.0,
    problem_file: str = HUMAN_EVAL,
    rs_dir: str = "/output",
    ignore_damage= False,
):
    """
    Evaluates the functional correctness of generated samples, and writes
    results to f"{sample_file}_results.jsonl.gz"
    """
    k = list(map(int, k.split(",")))
    results = evaluate_functional_correctness(task_id, k, n_workers, timeout, problem_file, rs_dir, ignore_damage)
    print(results)


def main():
    fire.Fire(entry_point)


sys.exit(main())
