# export ANTHROPIC_API_KEY="YOUR_API"
# export OPENAI_API_KEY="YOUR_API"
export TOGETHER_API_KEY="YOUR_API"
MODELS=("deepseek-ai/DeepSeek-R1-Distill-Llama-70B-free")


for model in "${MODELS[@]}"; do
    python closed_llms_generate.py \
        --provider togetherai \
        --model ${model} \
        --prompt_type instructprompt \
        --save_dir /home/namlh31aic/Project/AI4Code/RepoExec/results/predictions/repoexec-full-context/InstructPrompt-DeepSeek-R1-Distill-Llama-70B
done