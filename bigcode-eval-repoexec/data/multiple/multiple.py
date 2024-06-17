import json
import datasets
from pathlib import Path

logger = datasets.logging.get_logger(__name__)

_CITATION = """\
@article{cassano:multipl-e,
  author = {Cassano, Federico and Gouwar, John and Nguyen, Daniel and Nguyen, Sydney and
            Phipps-Costin, Luna and Pinckney, Donald and Yee, Ming-Ho and Zi, Yangtian and
            Anderson, Carolyn Jane and Feldman, Molly Q and Guha, Arjun and
            Greenberg, Michael and Jangda, Abhinav},
  title = {{MultiPL-E}: A Scalable and Polyglot Approach to Benchmarking Neural Code Generation},
  journal = "{IEEE} Transactions of Software Engineering (TSE)",
  year = 2023
}"""

_DESCRIPTION = """\
MultiPL-E is a dataset for evaluating large language models for code \
generation that supports 18 programming languages. It takes the OpenAI \
"HumanEval" and the MBPP Python benchmarks and uses little compilers to \
translate them to other languages. It is easy to add support for new languages \
and benchmarks.
"""

_SRCDATA = [ "humaneval", "mbpp" ]

_LANGUAGES = [ 
    "cpp", "cs", "d", "go", "java", "jl", "js", "lua", "php", "pl", "py", "r", 
    "rb", "rkt", "rs", "scala", "sh", "swift", "ts"
]

_VARIATIONS = [ "keep", "transform", "reworded", "remove" ]

class MultiPLEBuilderConfig(datasets.BuilderConfig):
    """BuilderConfig for MultiPLEBuilderConfig."""

    def __init__(
        self,
        srcdata,
        language,
        variation,
        **kwargs,
    ):
        self.language = language
        self.variation = variation
        self.srcdata = srcdata
        name = f"{srcdata}-{language}"
        if variation != "reworded":
            name = f"{name}-{variation}"
        kwargs["name"] = name
        super(MultiPLEBuilderConfig, self).__init__(**kwargs)

def _is_interesting(srcdata: str, variation: str):
    if srcdata == "humaneval":
        return True
    if srcdata == "mbpp":
        # MBPP does not have doctests, so these are the only interesting
        # variations
        return variation in [ "keep", "reworded" ]

class MultiPLE(datasets.GeneratorBasedBuilder):
    BUILDER_CONFIG_CLASS = MultiPLEBuilderConfig

    BUILDER_CONFIGS = [
        MultiPLEBuilderConfig(
            srcdata=srcdata,
            language=language,
            variation=variation,
            version=datasets.Version("2.1.0"))
        for srcdata in _SRCDATA
        for language in _LANGUAGES 
        for variation in _VARIATIONS
        if _is_interesting(srcdata, variation)
    ]

    DEFAULT_CONFIG_NAME = "humaneval-cpp"

    def _info(self):
        return datasets.DatasetInfo(
            description=_DESCRIPTION,
            license="MIT",
            features=datasets.Features({
                "name": datasets.Value("string"),
                "language": datasets.Value("string"),
                "prompt": datasets.Value("string"),
                "doctests": datasets.Value("string"),
                "original": datasets.Value("string"),
                "prompt_terminology": datasets.Value("string"),
                "tests": datasets.Value("string"),
                "stop_tokens": datasets.features.Sequence(datasets.Value("string")),
            }),
            supervised_keys=None,
            homepage="https://nuprl.github.io/MultiPL-E/",
            citation=_CITATION,
            task_templates=[]
        )

    def _split_generators(self, dl_manager: datasets.DownloadManager):
        files = dl_manager.download(
            f"/home/namlh35/namlh31/project/AI4Code/bigcode-evaluation-harness/data/multiple/{self.config.srcdata}-{self.config.language}-{self.config.variation}.json"
        )
        return [
            datasets.SplitGenerator(
                name=datasets.Split.TEST,
                gen_kwargs={
                    "filepath": files,
                }
            )
        ]

    def _generate_examples(self, filepath):
        with open(filepath, encoding="utf-8") as f:
            data = json.load(f)
            for id_, row in enumerate(data):
                yield id_, row