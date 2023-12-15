[![Push to Replicate](https://github.com/Arboreal-AI/llama-2-7b-chat/actions/workflows/main.yml/badge.svg)](https://github.com/Arboreal-AI/llama-2-7b-chat/actions/workflows/main.yml)

# llama-2-7b-chat
A cog wrapper for Llama-2-7b-Chat for deployment on Replicate and elsewhere

This packaged model uses the mainline GPTQ quantization provided by [TheBloke/Llama-2-7B-Chat-GPTQ](https://huggingface.co/TheBloke/Llama-2-7B-Chat-GPTQ) with the [HuggingFace Transformers library](https://huggingface.co/docs/transformers/index).

## Prompt Notes

The prompt template of this packaging does not wrap the input prompt in any special tokens. Users should handle prompt formatting themselves per instructions here: [Replicate Blog: How to Prompt Llama](https://replicate.com/blog/how-to-prompt-llama).

```
    prompt_template = f"""[INST] <<SYS>>
    {system_prompt}
    <</SYS>> [/INST]
    {prompt}"""
```

## Parameters

This model exposes support for the [ExponentialDecayLengthPenalty](https://huggingface.co/docs/transformers/main/en/internal/generation_utils#transformers.ExponentialDecayLengthPenalty) logit processer in the HuggingFace transformers library. This processor increases the likelihood of the end-of-sequence (EOS) token after the starting point number of tokens have been generated. See the linked documentation for further details on the `exponential_decay_start` and `exponential_decay_factor` parameters. The default `exponential_decay_factor` of `1.0` will not change the likelihood of the EOS token during generation.


> LogitsProcessor that exponentially increases the score of the eos_token_id after start_index has been reached. This allows generating shorter sequences without having a hard cutoff, allowing the eos_token to be predicted in a meaningful position.
