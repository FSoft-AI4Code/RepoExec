import re

from evaluate import load

from lm_eval.base import Task

def create_all_tasks():
    """Creates a dictionary of tasks from a list of levels
    :return: {task_name: task}
        e.g. {multiple-py: Task, multiple-java: Task}
    """
    return {"instruct-repoexec-full-context": create_task("full_context"), "instruct-repoexec-medium-context": create_task("medium_context"), "instruct-repoexec-short-context": create_task("short_context"), 
            "instruct1-repoexec-full-context": create_task("full_context", 1), "instruct1-repoexec-medium-context": create_task("medium_context", 1), "instruct1-repoexec-short-context": create_task("short_context", 1)}

def create_task(data_split, instruct_type=0):
    class RepoExec(InstructRepoExec):
        def __init__(self, prompt="instruct"):
            super().__init__(data_split, prompt, instruct_type)

    return RepoExec

class InstructRepoExec(Task):
    """A task represents an entire benchmark including its dataset, problems,
    answers, generation settings and evaluation methods.
    """

    DATASET_PATH = "Fsoft-AIC/RepoExec"

    def __init__(self, data_split, prompt="instruct", instruct_type = 0):

        super().__init__(
            stop_words=["\nclass", "\ndef", "\n#", "\n@", "\nprint", "\nif", "\n```"],
            requires_execution=True,
        )
        self.prompt = prompt
        self.data_split = data_split

        self.instruct_type = instruct_type

    def get_dataset(self):
        """Returns dataset for the task or an iterable of any object, that get_prompt can handle"""
        return self.dataset[self.data_split]

    def get_reference(self, doc):
        """Builds the reference solution for the doc (sample from the test dataset)."""
        test_func = doc["check"]
        return "\n" + test_func

    def get_prompt_base(self, doc):
        if self.instruct_type == 0:
            return doc["prompt"]
        elif self.instruct_type == 1:
            return doc["target_function_prompt"]
    
    def get_instruction(self, doc):
        if self.instruct_type == 0:
            template ="""Write a Python function `{signature}` to solve the following problem:"""
            return template.format(signature= doc["function_signature"][:-1].replace("\\", "").replace("\n", ""))
        elif self.instruct_type == 1:
            template = """The provided code snippet includes necessary dependencies for implementing the `{function_name}` function. Write a Python function `{signature}` to solve the following problem:\n"""
            return doc["prompt"].replace(doc["target_function_prompt"].strip(), "") + "\n" + template.format(function_name=doc["entry_point"],  signature=doc["function_signature"][:-1].replace("\\", "").replace("\n", ""))
    

    def get_prompt(self, doc):
        instruction = self.get_instruction(doc)
        prompt_base = self.get_prompt_base(doc)
        context = doc["docstring"]

        if context is None:
            inp = instruction
        # `Context first then instruction` methods
        elif self.prompt in ["continue", "instruct"]:
            inp = context + "\n" + instruction
        else:
            inp = instruction + "\n" + context
        
        if self.prompt == "continue":
            assert context is None, "The `continue` prompt should only be used for HumanEvalSynthesize. Use `instruct` for HumanEvalFix and HumanEvalExplain."
            prompt = prompt_base
        elif self.prompt == "instruct":
            prompt = inp + "\n\n" + prompt_base
        elif self.prompt == "octocoder":
            prompt = f'Question: {inp}\n\nAnswer:\n{prompt_base}'
        elif self.prompt == "octogeex":
            prompt = f'Question: {inp.strip()}\n\nAnswer:\n{prompt_base}'            
        elif self.prompt == "starchat":
            # https://huggingface.co/HuggingFaceH4/starchat-beta
            prompt = f'<|system|>\n<|end|>\n<|user|>\n{inp}<|end|>\n<|assistant|>\n{prompt_base}'
        elif self.prompt == "starcodercommit":
            prompt = f'<commit_before><commit_msg>{inp}<commit_after>{prompt_base}'
        elif self.prompt == "instructcodet5p":
            # https://github.com/salesforce/CodeT5/blob/main/CodeT5%2B/humaneval/generate_codet5p.py#L89
            prompt = f'Below is an instruction that describes a task. Write a response that appropriately completes the request.\n\n### Instruction:\n{inp}\n\n### Response:{prompt_base}'       
        elif self.prompt == "wizardcoder":
            # https://github.com/nlpxucan/WizardLM/blob/main/WizardCoder/src/humaneval_gen.py#L37
            prompt = f'Below is an instruction that describes a task. Write a response that appropriately completes the request.\n\n### Instruction:\n{inp}\n\n### Response:\n{prompt_base}'
        elif self.prompt == "codellama":
            prompt = f"[INST] {inp.strip()} [/INST] {prompt_base}"
        else:
            raise NotImplementedError
        # Strip off the final \n to make the tokens more natural
        # Essentially, we want to make sure that if there was no distinction between
        # input & output, the tokens would be the same
        # E.g. for SantaCoder:
        # tokenize("""def hi()\n   return""")
        # ['def', 'Ġhi', '()', 'ĊĠĠ', 'Ġreturn']
        # So we need to split before the \n so that the input is
        # ['def', 'Ġhi', '()'] and the model can generate ['ĊĠĠ', 'Ġreturn']
        # If instead we provide def hi()\n the tokens will be
        # ['def', 'Ġhi', '()', 'Ċ'] and the model would need to generate ['ĠĠ', 'Ġreturn']
        # Which would be harder, as it's not the usual way these tokens are tokenized
        # i.e. the model has never seen the token sequence of ['()', 'Ċ', 'ĠĠ'], but only ['()', 'ĊĠĠ']
        # The same holds for Java, JS, Go, Rust, C++ tho the start sequences are slightly different

        prompt = prompt.strip()
        if doc["id"] == 1:
            print(prompt)
            
        return prompt
    
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
        generation = generation[len(prompt):]
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
