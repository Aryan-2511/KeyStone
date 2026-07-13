"""Colab QLoRA fine-tune for the triage router — FINETUNE-SPIKE-01, Phase 2.

This runs on **Colab** (a free T4 GPU is enough), NOT in the Keystone repo env — it needs
`torch` / `transformers` / `peft` / `trl` / `bitsandbytes`, which are deliberately NOT Keystone
dependencies (the repo stays lean and on-prem, Python 3.12 / uv). This file lives OUTSIDE the
gate-scanned dirs (`src` / `tests` / `scripts`) and imports its heavy deps at top level in
Colab-cell style. Copy it (or paste it cell-by-cell) into a Colab notebook; full step-by-step
instructions live in ``docs/paper/finetune_spike.md`` (§ "Phase 2 — Colab training").

What it does:
  1. loads the contamination-checked chat dataset (train_chat.jsonl — produce it locally with
     `make finetune-data`, then upload it to the Colab session);
  2. QLoRA-fine-tunes a small base (default Qwen2.5-3B-Instruct, the MATCHED CONTROL vs the
     general-3B baseline) on the triage router task;
  3. merges the adapter and saves the model so it can be converted to GGUF and run on-prem
     via Ollama (the same seam that serves qwen2.5:3b today).

Honesty note: the labels are the transparent policy's decisions, so this DISTILLS the policy —
it cannot beat it. The point is only whether a specialized small model reaches the bounded
decision the general 3B missed on held-out cases. Do NOT tune anything to flatter the number.

Data-residency: the uploaded data is SYNTHETIC (no PII), so training on Colab is fine — nothing
sensitive leaves any trust boundary. Deployment inference is on-prem. "Trained on synthetic data,
deployed on-prem" — never "trained on-prem."
"""

# --- Cell 1: install (run first in Colab) -------------------------------------------------
# !pip install -q -U "transformers>=4.44" "peft>=0.12" "trl>=0.9" "bitsandbytes>=0.43" \
#     "datasets>=2.20" "accelerate>=0.33"

# --- Cell 2: imports + config -------------------------------------------------------------
import torch
from datasets import load_dataset
from peft import LoraConfig
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from trl import SFTConfig, SFTTrainer

BASE_MODEL = (
    "Qwen/Qwen2.5-3B-Instruct"  # MATCHED CONTROL (specialized-3B vs general-3B)
)
# Optional smaller bases — the task is tiny, so these are worth a cheap cross-check:
#   "Qwen/Qwen2.5-1.5B-Instruct", "Qwen/Qwen2.5-0.5B-Instruct"
TRAIN_FILE = "train_chat.jsonl"  # upload the file produced by `make finetune-data`
OUTPUT_DIR = "keystone-triage-ft"
EPOCHS = 3
LR = 2e-4
MAX_SEQ_LEN = 1024


# --- Cell 3: train ------------------------------------------------------------------------
def main() -> None:
    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    quant = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16,
        bnb_4bit_use_double_quant=True,
    )
    model = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL,
        quantization_config=quant,
        device_map="auto",
        torch_dtype=torch.bfloat16,
    )

    # The dataset is chat-format {"messages": [...]}; apply the model's chat template so the
    # assistant target ("ROUTE: <route>") is learned exactly as the eval will prompt for it.
    ds = load_dataset("json", data_files=TRAIN_FILE, split="train")

    def render(example: dict) -> dict:
        return {
            "text": tokenizer.apply_chat_template(
                example["messages"], tokenize=False, add_generation_prompt=False
            )
        }

    ds = ds.map(render, remove_columns=ds.column_names)

    peft_config = LoraConfig(
        r=16,
        lora_alpha=32,
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM",
        target_modules=[
            "q_proj",
            "k_proj",
            "v_proj",
            "o_proj",
            "gate_proj",
            "up_proj",
            "down_proj",
        ],
    )

    trainer = SFTTrainer(
        model=model,
        train_dataset=ds,
        peft_config=peft_config,
        args=SFTConfig(
            output_dir=OUTPUT_DIR,
            num_train_epochs=EPOCHS,
            per_device_train_batch_size=8,
            gradient_accumulation_steps=2,
            learning_rate=LR,
            logging_steps=10,
            max_length=MAX_SEQ_LEN,  # TRL >=0.20 renamed this from `max_seq_length`
            bf16=True,
            report_to="none",
        ),
    )
    trainer.train()

    # Merge the adapter into the base and save, then convert to GGUF for Ollama (see docs).
    merged = trainer.model.merge_and_unload()
    merged.save_pretrained(f"{OUTPUT_DIR}-merged")
    tokenizer.save_pretrained(f"{OUTPUT_DIR}-merged")
    print(
        f"Done. Merged model in {OUTPUT_DIR}-merged/ — convert to GGUF and pull into Ollama."
    )


if __name__ == "__main__":
    main()
