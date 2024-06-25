import re

from evaluate import load

from lm_eval.base import Task

def create_all_tasks():
    """Creates a dictionary of tasks from a list of levels
    """
    return {"repoexec-full-context": create_task(True, "full_context"), 
            "repoexec-medium-context": create_task(True, "medium_context"), 
            "repoexec-small-context": create_task(True, "small_context")}


def create_task(strip_prompt, data_split):
    class RepoExec(GeneralRepoExec):
        def __init__(self):
            super().__init__(strip_prompt, data_split)

    return RepoExec


class GeneralRepoExec(Task):
    """A task represents an entire benchmark including its dataset, problems,
    answers, generation settings and evaluation methods.
    """

    DATASET_PATH = "Fsoft-AIC/RepoExec"

    def __init__(self, strip_prompt, data_split):
        super().__init__(
            stop_words=["\nclass", "\ndef", "\n#", "\n@", "\nprint", "\nif", "\n```"],
            requires_execution=True,
        )
        self.strip_prompt = strip_prompt
        self.data_split = data_split

    def get_dataset(self):
        """Returns dataset for the task or an iterable of any object, that get_prompt can handle"""
        data = self.dataset[self.data_split]
        print(data[0]["prompt"])
        return data

    def get_prompt(self, doc):
        """Builds the prompt for the LM to generate from."""
        if self.strip_prompt:
            return doc["prompt"].strip()
        else:
            return doc["prompt"]

    def get_reference(self, doc):
        """Builds the reference solution for the doc (sample from the test dataset)."""
        test_func = doc["check"]
        return test_func

    @staticmethod
    def _stop_at_stop_token(decoded_string, stop_tokens):
        """
        Produces the prefix of decoded_string that ends at the first occurrence of
        a stop_token.
        WARNING: the decoded_string *must not* include the prompt, which may have stop tokens
        itself.
        """
        min_stop_index = len(decoded_string)
        for stop_token in stop_tokens:
            stop_index = decoded_string.find(stop_token)
            if stop_index != -1 and stop_index < min_stop_index:
                min_stop_index = stop_index
        return decoded_string[:min_stop_index]

    def postprocess_generation(self, generation, idx):
        """Defines the postprocessing for a LM generation.
        :param generation: str
            code generation from LM
        :param idx: int
            index of doc in the dataset to which the generation belongs
            (not used for Humaneval-Task)
        """
        prompt = self.get_prompt(self.dataset[self.data_split][idx])
        generation = generation[len(prompt) :]
        return prompt + self._stop_at_stop_token(generation, self.stop_words)

    def process_results(self, generations, references):
        """Takes the list of LM generations and evaluates them against ground truth references,
        returning the metric for the generations.
        :param generations: list(list(str))
            list of lists containing generations
        :param references: list(str)
            list of str containing refrences
        """
        code_metric = load("code_eval")
        results, _ = code_metric.compute(
            references=references,
            predictions=generations,
        )
        return results
