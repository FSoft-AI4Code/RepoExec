#! /bin/bash
export HF_HOME=".cache"
export HF_DATASETS_CACHE=".cache"

CUDA_VISIBLE_DEVICES=0,1 python3 -m accelerate.commands.launch --config_file ./scripts/generate_config.yaml main.py \
--model microsoft/phi-1 \
--tasks repoexec-full-context \
--generation_only \
--do_sample True \
--temperature 0.2 \
--top_p 0.95 \
--top_k 0 \
--n_samples 2 \
--batch_size 2 \
--generation_only \
--save_generations \
--trust_remote_code \
--save_generations_path ../results/predictions/repoexec-full-context/BasePrompt-phi-2/generations.json \
--max_length_generation 1280 \
--max_new_tokens 512 \
--precision fp16 \
# --token YOUR_ACCESS_TOKEN \
