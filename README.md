<div align="center">

# On the Impacts of Contexts on Repository-Level Code Generation

<img src="./asset/repoexec_logo.png" width="120px" alt="logo">

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT) [![arXiv](https://img.shields.io/badge/2406.11927-red?style=flat&label=arXiv)](https://arxiv.org/abs/2406.11927v4) [![ExecRepo on HuggingFace datasets](https://img.shields.io/badge/%F0%9F%A4%97%20Datasets-RepoExec-f9a602?style=flat)](https://huggingface.co/datasets/Fsoft-AIC/RepoExec) [![Homepage](https://custom-icon-badges.demolab.com/badge/WebPage-1a4f76?style=flat&logo=web)](https://fsoft-ai4code.github.io/repoexec/)  [![Leaderboard](https://custom-icon-badges.demolab.com/badge/Leaderboard-orange?style=flat&logo=barchart&label=%20)](https://repoexec.github.io/) 

</div>

# Introduction
RepoExec is a novel benchmark designed to evaluate code generation at the repository level with a focus on executability and correctness. This benchmark addresses the gaps in existing systems by emphasizing real-world applicability and providing a comprehensive assessment of code functionality. It aims to provide a comprehensive evaluation of code functionality and alignment with developer intent, paving the way for more reliable and applicable CodeLLMs in real-world scenarios.

# Dataset
[RepoExec](https://huggingface.co/datasets/Fsoft-AIC/RepoExec) is available at Huggingface datasets. The instruction-tuning data used in our work is presented in [RepoExec-Instruct](https://huggingface.co/datasets/Fsoft-AIC/RepoExec-Instruct).

```python
from datasets import load_dataset

# RepoExec contains 3 subsets, corresponding to the detail of the context level
# full_context || medium_context || small_context
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
## Set up RepoExec:
```
git clone https://github.com/FSoft-AI4Code/RepoExec.git 
cd RepoExec
unzip test-apps.zip
pip install -r requirement
```
## Set up for model generation
```
cd RepoExec/bigcode-eval-repoexec
pip install -e .
```

## Set up for execution
```
cd RepoExec/execution-code-eval
(sudo) docker build -t codeeval-runner -f Dockerfile --platform linux/amd64 .
```

## Evaluation

Script examples to run evaluation are contained in [`scripts`](https://github.com/FSoft-AI4Code/RepoExec/tree/master/execution-code-eval/scripts)

### LLMs generation

```
cd RepoExec/bigcode-eval-repoexec
pip install -e .
```

Example scripts are in [phi-2-generation](https://github.com/FSoft-AI4Code/RepoExec/blob/master/bigcode-eval-repoexec/scripts/generation.sh)

There are 2 kinds of prompts: BasePrompt and InstructPrompt:
- To use BasePrompt, specify the `--tasks` argument to `repoexec-{full|medium|small}-context`.
- To use InstructPrompt, specify the `--tasks` argument to `instruct-repoexec-{full|medium|small}-context` and `prompt` argument to use the template specific for each model (e.g. `--prompt codellama` for CodeLlama series).


After running the generation script, generation result will be a nested list of prediction for each problem in the dataset and is saved to a `generations.json` file. See the example in [phi-2 prediction](https://github.com/FSoft-AI4Code/RepoExec/tree/master/results/examples/predictions/repoexec-full-context/BasePrompt-phi-2)

Example:
```python
[[pred_11, pred_12, pred13], [pred_21, pred_22, pred_23], ...]
```

**Note**: If you're using a closed-source model (such as gpt-4o-turbo), please follow these scripts [`api_llms_generate.py`](./execution-code-eval/api_llms_generate.py) and [`api_llms_infer.sh`](./execution-code-eval/scripts/api_llms_infer.sh) to run the process, and don't forget to export your API key.

### Process output
Process to acquire the target function from prediction and save to json file. 

```
python3 process_result.py \
--subset medium_context \
--prediction_dir ../results/examples/predictions/repoexec-full-context/BasePrompt-phi-2 \
```

**Note**: For closed-source models that require API calls, after collecting the generated responses, run `process_result` with the additional `--is_api` flag to process the results properly.

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

### Calculate DIR
```python
python3 get_dir.py --execution_dir ../results/examples/execution_rs/repoexec-full-context/BasePrompt-phi-2
```

# Dependency Extraction Tool
Please see [this repo](https://github.com/FSoft-AI4Code/pydep) for tool usage.

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
- Corresponding Author: namlh@soict.hust.edu.vn

# License
[MIT License](LICENSE)
