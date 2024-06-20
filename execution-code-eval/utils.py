from codetext.parser import PythonParser
from tree_sitter import Language, Parser
import tree_sitter
from typing import List
import pandas as pd


# TEST_BASE = "/datadrive/namlh31/testgen/codamosa/replication"
# good_modules = "./good_modules.csv"
# modules = pd.read_csv(good_modules, header=None)
# MODULE_LIST = {}
# for module in modules.values.tolist():
#     if module[0] not in MODULE_LIST:
#         MODULE_LIST[module[0]] = []
#     MODULE_LIST[module[0]].append(module[1])

PY_LANGUAGE = Language('./my-languages.so', 'python')
parser = Parser()
parser.set_language(PY_LANGUAGE)

def traverse_type(node, results, kind, ignore_kind) -> None:
    # logger.warn('From version 0.0.6, we move `traverse_type` to `get_node_by_kind`')
    
    if kind is None:
        results.append(node)
    elif node.type in kind:
        results.append(node)
    if not node.children:
        return
    for n in node.children:
        if n.type in ignore_kind:
            continue
        traverse_type(n, results, kind, ignore_kind)


def get_node_by_kind(root: tree_sitter.Node, kind=None, ignore_kind= []) -> List:
    """
    Get all nodes with specific type
    
    Args:
        root (tree_sitter.Node): Tree sitter root node
        kind (List[str]): (node's) type that want to get
    
    Return:
        List[tree_sitter.Node]: List of all 
    """

    node_list = []
    traverse_type(root, node_list, kind=kind, ignore_kind= ignore_kind)
    return node_list

def fix_white_space(string):
    return " ".join(string.split())