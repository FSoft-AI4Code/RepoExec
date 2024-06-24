#! /bin/bash
export TRANSFORMERS_CACHE=".cache"
export HF_DATASETS_CACHE="/.cache"

CUDA_VISIBLE_DEVICES=6,7 python3 -m accelerate.commands.launch --config_file ./scripts/generate_config.yaml main.py \
--model microsoft/phi-2 \
--tasks repoexec-full-context \
--generation_only \
--do_sample True \
--temperature 0.2 \
--n_samples 10 \
--batch_size 2 \
--generation_only \
--save_generations \
--trust_remote_code \
--save_generations_path ./results/examples/predictions/repo-codegen-full-context/BasePrompt-phi-2/generations.json \
--max_length_generation 1280 \
--max_new_tokens 512 \
--precision fp16 \
--use_auth_token \
