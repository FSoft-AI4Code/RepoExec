<div align="center">

# RepoExec: Evaluate Code Generation with a Repository-Level Executable Benchmark

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT) [![arXiv](https://img.shields.io/badge/2406.11927-red?style=flat&label=arXiv&color=red)](https://arxiv.org/html/2406.11927v1) [![ExecRepo on HuggingFace datasets](https://img.shields.io/badge/%F0%9F%A4%97%20Datasets-RepoExec-yellow?style=flat)](https://huggingface.co/datasets/Fsoft-AIC/RepoExec) [![Homepage](https://img.shields.io/badge/RepoExec-blue?style=flat&label=WebPage&color=blue)](https://fsoft-ai4code.github.io/repoexec/)  [![Leaderboard](https://custom-icon-badges.demolab.com/badge/Leaderboard-E39842?style=flat&logo=barchart&label=%20)]() 
</div>

# Introduction
RepoExec is a novel benchmark designed to evaluate code generation at the repository level with a focus on executability and correctness. This benchmark addresses the gaps in existing systems by emphasizing real-world applicability and providing a comprehensive assessment of code functionality. It aims to provide a comprehensive evaluation of code functionality and alignment with developer intent, paving the way for more reliable and applicable CodeLLMs in real-world scenarios.

# Dataset
[RepoExec](https://huggingface.co/datasets/Fsoft-AIC/RepoExec) is available at Huggingface datasets.

```python
from datasets import load_dataset

# RepoExec contains 3 subsets, corresponding to the detail of the context level
# full_context || medium_context || short_context
dataset = load_dataset("Fsoft-AIC/RepoExec")
```

Examples:

```python
# full context
import base64
import random
import unicodedata
import zlib
from typing import Union
from uuid import uuid4
from ._regex import *
from .errors import InvalidInputError
from .validation import is_snake_case, is_full_string, is_camel_case, is_integer, is_string

CAMEL_CASE_REPLACE_RE = re.compile(r'([a-z]|[A-Z]+)(?=[A-Z])')

class InvalidInputError(TypeError):
    """
    Custom error raised when received object is not a string as expected.
    """

    def __init__(self, input_data: Any):
        """
        :param input_data: Any received object
        """
        type_name = type(input_data).__name__
        msg = 'Expected "str", received "{}"'.format(type_name)
        super().__init__(msg)

def is_string(obj: Any) -> bool:
    """
    Checks if an object is a string.

    *Example:*

    >>> is_string('foo') # returns true
    >>> is_string(b'foo') # returns false

    :param obj: Object to test.
    :return: True if string, false otherwise.
    """
    return isinstance(obj, str)

def is_camel_case(input_string: Any) -> bool:
    """
    Checks if a string is formatted as camel case.

    A string is considered camel case when:

    - it's composed only by letters ([a-zA-Z]) and optionally numbers ([0-9])
    - it contains both lowercase and uppercase letters
    - it does not start with a number

    *Examples:*

    >>> is_camel_case('MyString') # returns true
    >>> is_camel_case('mystring') # returns false

    :param input_string: String to test.
    :type input_string: str
    :return: True for a camel case string, false otherwise.
    """
    return is_full_string(input_string) and CAMEL_CASE_TEST_RE.match(input_string) is not None
  
def camel_case_to_snake(input_string, separator='_'):
    """
    Convert a camel case string into a snake case one.
    (The original string is returned if is not a valid camel case string)

    *Example:*

    >>> camel_case_to_snake('ThisIsACamelStringTest') # returns 'this_is_a_camel_case_string_test'

    :param input_string: String to convert.
    :type input_string: str
    :param separator: Sign to use as separator.
    :type separator: str
    :return: Converted string.
    """
```

```python
# medium context
import base64
import random
import unicodedata
import zlib
from typing import Union
from uuid import uuid4
from ._regex import *
from .errors import InvalidInputError
from .validation import is_snake_case, is_full_string, is_camel_case, is_integer, is_string

CAMEL_CASE_REPLACE_RE = re.compile(r'([a-z]|[A-Z]+)(?=[A-Z])')

class InvalidInputError(TypeError):
    """
    Custom error raised when received object is not a string as expected.
    """

    def __init__(self, input_data: Any):
        """
        :param input_data: Any received object
        """

def is_string(obj: Any) -> bool:
    """
    Checks if an object is a string.

    *Example:*

    >>> is_string('foo') # returns true
    >>> is_string(b'foo') # returns false

    :param obj: Object to test.
    :return: True if string, false otherwise.
    """

def is_camel_case(input_string: Any) -> bool:
    """
    Checks if a string is formatted as camel case.

    A string is considered camel case when:

    - it's composed only by letters ([a-zA-Z]) and optionally numbers ([0-9])
    - it contains both lowercase and uppercase letters
    - it does not start with a number

    *Examples:*

    >>> is_camel_case('MyString') # returns true
    >>> is_camel_case('mystring') # returns false

    :param input_string: String to test.
    :type input_string: str
    :return: True for a camel case string, false otherwise.
    """
  
def camel_case_to_snake(input_string, separator='_'):
    """
    Convert a camel case string into a snake case one.
    (The original string is returned if is not a valid camel case string)

    *Example:*

    >>> camel_case_to_snake('ThisIsACamelStringTest') # returns 'this_is_a_camel_case_string_test'

    :param input_string: String to convert.
    :type input_string: str
    :param separator: Sign to use as separator.
    :type separator: str
    :return: Converted string.
    """
```

```python
# small context
import base64
import random
import unicodedata
import zlib
from typing import Union
from uuid import uuid4
from ._regex import *
from .errors import InvalidInputError
from .validation import is_snake_case, is_full_string, is_camel_case, is_integer, is_string

CAMEL_CASE_REPLACE_RE = re.compile(r'([a-z]|[A-Z]+)(?=[A-Z])')

class InvalidInputError(TypeError):

    def __init__(self, input_data: Any):

def is_string(obj: Any) -> bool:

def is_camel_case(input_string: Any) -> bool:
  
def camel_case_to_snake(input_string, separator='_'):
    """
    Convert a camel case string into a snake case one.
    (The original string is returned if is not a valid camel case string)

    *Example:*

    >>> camel_case_to_snake('ThisIsACamelStringTest') # returns 'this_is_a_camel_case_string_test'

    :param input_string: String to convert.
    :type input_string: str
    :param separator: Sign to use as separator.
    :type separator: str
    :return: Converted string.
    """
```

# Quickstart Guide
Clone RepoExec:
```
git clone https://github.com/FSoft-AI4Code/RepoExec.git 
```
## Set up for model generation
```
cd RepoExec/bigcode-eval-repoexec
pip install -e .
```

## Set up for execution
```
cd RepoExec/execution-code-eval
docker build -t codeeval-runner -f docker/Dockerfile --platform linux/amd64 .
```

## Evaluation

Script examples to run evaluation are contained in [`scripts`](https://github.com/FSoft-AI4Code/RepoExec/tree/master/code_eval/scripts)

### LLMs generation

```
cd RepoExec/bigcode-eval-repoexec
pip install -e .
```

Example scripts are in [phi-2-generation](https://github.com/FSoft-AI4Code/RepoExec/blob/master/bigcode-eval-repoexec/scripts/generation.sh)

There are 2 kinds of prompts: BasePrompt and InstructPrompt:
- To use BasePrompt, specify the `--tasks` argument to `repoexec-{full|medium|short}-context`.
- To use InstructPrompt, specify the `--tasks` argument to `instruct-repoexec-{full|medium|short}-context` and `prompt` argument to use the template specific for each model (e.g. `--prompt codellama` for CodeLlama series).


After running the generation script, generation result will be a nested list of prediction for each problem in the dataset and is saved to a `generations.json` file. See the example in [phi-2 prediction](https://github.com/FSoft-AI4Code/RepoExec/tree/master/results/examples/predictions/repoexec-full-context/BasePrompt-phi-2)

Example:
```python
[[pred_11, pred_12, pred13], [pred_21, pred_22, pred_23], ...]
```

**Note**: if you use a close-source model (e.g ChatGPT), please use your custom script. This currently supports only an open-source model.

### Process output
Process to acquire the target function from prediction and save to json file. 

```
python3 process_result.py \
--subset medium_context \
--prediction_dir ../results/examples/predictions/repoexec-full-context/BasePrompt-phi-2 \
```

### Execution
Execute the generated function of the model to obtain the execution output.

```python
python3 execute.py --subset full_context \
--prediction_dir ../results/examples/predictions/repoexec-full-context/BasePrompt-phi-2 \
--execution_dir ../results/examples/execution_rs/repoexec-full-context/BasePrompt-phi-2 \
```

### Calculate pass@k
```python
python3 passk.py --execution_dir ../results/examples/execution_rs/repoexec-full-context/BasePrompt-phi-2
```


# Citing RepoExec
More details can be found in our [paper](https://github.com/FSoft-AI4Code/RepoExec/blob/master/paper/main.pdf). 

If you're using RepoExec, please cite using this BibTeX:
```bibtex
@article{nam2024repoexec,
  title={RepoExec: Evaluate Code Generation with a Repository-Level Executable Benchmark},
  author={Hai, Nam Le and Manh, Dung Nguyen and Bui, Nghi DQ},
  journal={arXiv preprint arXiv:2406.11927v1},
  year={2024}
}
```

# Acknowledgements
This codebase is adapted from:
- [bigcode-evaluation-harness](https://github.com/bigcode-project/bigcode-evaluation-harness/tree/main)
- [HumanEval](https://github.com/openai/human-eval)

# Contact us
If you have any questions, comments or suggestions, please do not hesitate to contact us.
- Website: [fpt-aicenter](https://www.fpt-aicenter.com/ai-residency/)
- Email: support.ailab@fpt.com

# License
[MIT License](LICENSE)
