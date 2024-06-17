#! /bin/bash
export TRANSFORMERS_CACHE="/cm/archive/namlh35/.cache"
export HF_DATASETS_CACHE="/cm/archive/namlh35/cache"
export https_proxy=http://10.16.29.10:8080
export WANDB_DISABLED="true"
export TMPDIR=/cm/archive/namlh35/tmp

CUDA_VISIBLE_DEVICES=6,7 python3 -m accelerate.commands.launch --config_file ./scripts/generate_config.yaml main.py \
--model microsoft/phi-2 \
--tasks repo-codegen-full-context \
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
# --prompt wizardcoder \
# --load_in_8bit \


# CUDA_VISIBLE_DEVICES=6,7 python3 -m accelerate.commands.launch --config_file ./scripts/generate_config.yaml main.py \
#     --model /cm/archive/namlh35/instruction-tuning/multitask/CodeLlama-7b-dpo-nmd2k_apps_rlaif-v2 \
#     --use_auth_token \
#     --precision fp16 \
#     --task apps-competition \
#     --max_length_generation 1024 \
#     --max_new_tokens 512 \
#     --temperature 0.2 \
#     --do_sample True \
#     --n_samples 10 \
#     --batch_size 1 \
#     --trust_remote_code \
#     --save_generations \
#     --generation_only \
#     --save_generations_path /cm/archive/namlh35/AI4Code/code-gen-results/gen_results/apps/codellama-7b-dpo-nmd2k_apps_rlaif-competition/generations.json \
#     --metric_output_path /cm/archive/namlh35/AI4Code/code-gen-results/gen_results/apps/codellama-7b-dpo-nmd2k_apps_rlaif-competition/evaluation_results.json \
#     --peft_model /cm/archive/namlh35/instruction-tuning/multitask/CodeLlama-7b-dpo-nmd2k_apps_rlaif-v2  \