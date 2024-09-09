from transformers import (
    AutoTokenizer, 
    pipeline, 
    logging,
    AutoModelForCausalLM
) 
from file_reader import read_file

import argparse
import warnings

warnings.filterwarnings("ignore")
logging.set_verbosity(logging.CRITICAL)

parser = argparse.ArgumentParser()
parser.add_argument(
    '--prompt',
    default='Tell me about AI',
    help='the user prompt/question',
    type=str
)
parser.add_argument(
    '--system-agenda',
    '-sa',
    dest='system_agenda',
    help='what should the system do, summarize, answer a question...',
    default="You are a helpful, respectful and honest assistant. Always answer as helpfully as possible, while being safe. Your answers should not include any harmful, unethical, racist, sexist, toxic, dangerous, or illegal content. Please ensure that your responses are socially unbiased and positive in nature. If a question does not make any sense, or is not factually coherent, explain why instead of answering something not correct. If you don't know the answer to a question, please don't share false information."
)
parser.add_argument(
    '--limit',
    default=11000,
    type=int,
    help='set limit for how many characeters to use from the prompt, \
          -1 indicates to use the whole prompt, ⬆️ character ⬆️ vram needed'
)
parser.add_argument(
    '--new-tokens',
    default=512,
    type=int,
    help='maximum new tokens to be generated by the model'
)
parser.add_argument(
    '--model-path',
    dest='model_path',
    default='Llama-2-7b-Chat-GPTQ'
)
parser.add_argument(
    '--model-base',
    dest='model_base',
    default='gptq-4bit-128g-actorder_True'
)
args = parser.parse_args()

EXTS = ['.txt', '.pdf']

use_triton = False
device = 'cuda:0'

tokenizer = AutoTokenizer.from_pretrained(args.model_path, use_fast=True)

model = AutoModelForCausalLM.from_pretrained(
    args.model_path,
    device_map="auto",
    trust_remote_code=False,
    revision=args.model_base,
)

prompt = args.prompt
# Assuming it may be file ends with `EXTS`.
for ext in EXTS:
    if args.prompt.endswith(ext):
        prompt = read_file(args.prompt)
    
system_message = args.system_agenda
prompt_template=f'''[INST] <<SYS>>
{system_message}
<</SYS>>
{prompt} [/INST]'''

if args.limit != -1:
    prompt_template = prompt_template[:args.limit] + ' [/INST]'
pipe = pipeline(
    "text-generation",
    model=model,
    tokenizer=tokenizer,
    max_new_tokens=args.new_tokens,
    temperature=0.7,
    top_p=0.95,
    repetition_penalty=1.15,
)

model_outputs = pipe(prompt_template)[0]['generated_text']
outputs = model_outputs.split('[/INST]')[-1]
print(outputs)