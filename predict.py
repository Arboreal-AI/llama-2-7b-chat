# Prediction interface for Cog ⚙️
# https://github.com/replicate/cog/blob/main/docs/python.md

import contextlib
import typing as tp
import builtins

from cog import BasePredictor, Input
import torch
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    TextIteratorStreamer,
    set_seed,
)

MODEL_NAME = "TheBloke/Llama-2-7B-Chat-GPTQ"
MODEL_CACHE = "cache"

MODEL_DEST = "Llama-2-7B-Chat-GPTQ"
TOKEN_DEST = "Llama-2-7B-Chat-GPTQ"


@contextlib.contextmanager
def delay_prints(
    REALLY_EAT_MY_PRINT_STATEMENTS: bool = False,
) -> tp.Iterator[tp.Callable]:
    lines = []

    def delayed_print(*args: tp.Any, **kwargs: tp.Any) -> None:
        lines.append((args, kwargs))

    if REALLY_EAT_MY_PRINT_STATEMENTS:
        builtins.print, _print = delayed_print, builtins.print
    try:
        yield delayed_print
    finally:
        if REALLY_EAT_MY_PRINT_STATEMENTS:
            builtins.print = _print
        for args, kwargs in lines:
            print(*args, **kwargs)

    return delay_prints


class Predictor(BasePredictor):
    def setup(self) -> None:
        """Load the model into memory to make running multiple predictions efficient"""
        self.tokenizer = AutoTokenizer.from_pretrained(
            MODEL_DEST, use_fast=True, cache_dir=MODEL_CACHE
        )

        model = AutoModelForCausalLM.from_pretrained(
            MODEL_DEST, device_map="auto", trust_remote_code=False, revision="main"
        )

        # Pytorch 2 optimization
        self.model = torch.compile(model)

    def predict(
        self,
        prompt: str = Input(
            description="Prompt to send to Llama v2",
            default="[INST]Tell me about AI[/INST]",
        ),
        system_prompt: str = Input(
            description="System prompt that helps guide system behavior",
            default="You are a helpful, respectful and honest assistant. Always answer as helpfully as possible, while being safe.  Your answers should not include any harmful, unethical, racist, sexist, toxic, dangerous, or illegal content. Please ensure that your responses are socially unbiased and positive in nature. If a question does not make any sense, or is not factually coherent, explain why instead of answering something not correct. If you don't know the answer to a question, please don't share false information.",
        ),
        max_new_tokens: int = Input(
            description="Number of new tokens", ge=1, le=4096, default=512
        ),
        temperature: float = Input(
            description="Randomness of outputs, 0 is deterministic, greater than 1 is random",
            ge=0,
            le=5,
            default=1.0,
        ),
        top_p: float = Input(
            description="When decoding text, samples from the top p percentage of most likely tokens; lower to ignore less likely tokens",
            ge=0.01,
            le=1,
            default=0.95,
        ),
        repetition_penalty: float = Input(
            description="Penalty for repeated words in generated text; 1 is no penalty, values greater than 1 discourage repetition, less than 1 encourage it",
            ge=0,
            le=5,
            default=1.0,
        ),
        exponential_decay_start: int = Input(
            description="Number of tokens to wait before starting exponential decay.",
            default=512,
            ge=0,
            le=4096,
        ),
        exponential_decay_factor: float = Input(
            description="Decay factor for LogitProcessor exponential decay.",
            default=1.0,
            ge=1.0,
            le=10.0,
        ),
        skip_prompt: bool = Input(
            description="Whether to skip the prompt to .generate() or not. Useful e.g. for chatbots.",
            default=True,
        ),
        random_seed: int = Input(
            description="Random seed for reproducibility. Set to 0 for no random seed.",
            default=0,
        ),
    ) -> str:
        """Run a single prediction on the model"""
        with delay_prints() as print:
            complete_prompt = f"""[INST] <<SYS>>
            {system_prompt}
            <</SYS>> [/INST]
            {prompt}"""
            if random_seed:
                set_seed(random_seed)
            print(f"Your formatted prompt is: \n{complete_prompt}")
            input_ids = self.tokenizer(
                complete_prompt, return_tensors="pt"
            ).input_ids.cuda()
            streamer = TextIteratorStreamer(
                self.tokenizer,
                timeout=10.0,
                skip_prompt=skip_prompt,
                skip_special_tokens=True,
            )
            self.model.generate(
                inputs=input_ids,
                streamer=streamer,
                temperature=temperature,
                top_p=top_p,
                repetition_penalty=repetition_penalty,
                max_new_tokens=max_new_tokens,
                exponential_decay_length_penalty=(
                    exponential_decay_start,
                    exponential_decay_factor,
                ),
                do_sample=True,
            )
            return "".join([out for out in streamer])
