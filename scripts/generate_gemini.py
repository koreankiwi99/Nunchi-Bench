import argparse
import csv
import os
import pandas as pd
import google.generativeai as genai

MCQ_COLUMNS = ["id", "question", "choices", "output", "correct"]
INTERPRET_COLUMNS = ["id", "idx", "question", "response", "eval", "score"]
VARIANTS = ["kor_default", "eng_default", "kor_kor", "eng_kor"]

def init_gemini(api_key, model_name):
    genai.configure(api_key=api_key)
    return genai.GenerativeModel(model_name)

def generate_response(model, prompt, config):
    response = model.generate_content(prompt, generation_config=config)
    return response.text.strip()

def load_prompt_template(path):
    with open(path, encoding="utf-8") as f:
        return f.read()

def fill_template(template, question, choices):
    return template.replace("{QUESTION}", question).replace("{OPTIONS}", choices)

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)

def get_output_path(mode, language_or_variant, model_name):
    base_mode = "trap" if mode == "trap" else mode
    base = f"results/model_outputs/{base_mode}/{language_or_variant}"
    ensure_dir(base)
    return f"{base}/{model_name}_{mode}_{language_or_variant}.csv"

def run_mcq(model, df, language, model_name, prompt_template, prompt_dir):
    output_csv = get_output_path("mcq", language, model_name)
    gen_config = genai.types.GenerationConfig(candidate_count=1, max_output_tokens=1000, temperature=0.0)
    done_ids = set()
    if os.path.exists(output_csv):
        with open(output_csv, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                done_ids.add(int(row["id"]))

    with open(output_csv, "a", newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if os.stat(output_csv).st_size == 0:
            writer.writerow(MCQ_COLUMNS)

        for _, row in df.iterrows():
            qid = int(row["ID"])
            if qid in done_ids:
                continue
            question = row[f"{language}_question"]
            choices = row[f"{language}_choices"]
            prompt = fill_template(prompt_template, question, choices)
            with open(f"{prompt_dir}/prompt_{qid}.txt", "w", encoding="utf-8") as pf:
                pf.write(prompt)
            try:
                response = generate_response(model, prompt, gen_config)
                writer.writerow([qid, question, choices, response, None])
                print(f"✅ MCQ ID {qid} saved")
            except Exception as e:
                print(f"❌ Failed MCQ ID {qid}: {e}")

def run_interpret_or_trap(model, df, variant, model_name, mode):
    output_csv = get_output_path(mode, variant, model_name)
    gen_config = genai.types.GenerationConfig(candidate_count=1, max_output_tokens=2048, temperature=0.0)
    done = set()
    if os.path.exists(output_csv):
        with open(output_csv, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                done.add((int(row["id"]), int(row["idx"])))

    with open(output_csv, "a", newline='', encoding="utf-8") as f:
        writer = csv.writer(f)
        if os.stat(output_csv).st_size == 0:
            writer.writerow(INTERPRET_COLUMNS)

        for idx, row in df.iterrows():
            qid = int(row["ID"])
            for _, v in enumerate(VARIANTS):
                if v not in variant:
                    continue
                if (qid, idx) in done:
                    continue
                input_text = row[v]
                prompt = input_text
                try:
                    response = generate_response(model, prompt, gen_config)
                    writer.writerow([qid, idx, input_text, response, None, None])
                    print(f"✅ {mode.title()} ID {qid}, idx {idx} saved")
                except Exception as e:
                    print(f"❌ Failed {mode.title()} ID {qid}, idx {idx}: {e}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--api_key", required=True)
    parser.add_argument("--mode", choices=["mcq", "interpret", "trap"], required=True)
    parser.add_argument("--model_name", required=True)
    parser.add_argument("--input_csv", required=True)
    parser.add_argument("--variant", type=str, choices=VARIANTS, help=f"Which variant to process. Must be one of: {', '.join(VARIANTS)}")
    parser.add_argument("--language", help="For mcq mode, e.g., eng or kor")
    parser.add_argument("--prompt_eng_txt", default="prompts/mcq_prompt_eng.txt")
    parser.add_argument("--prompt_kor_txt", default="prompts/mcq_prompt_kor.txt")
    parser.add_argument("--prompt_dir", default="debug/prompts")
    args = parser.parse_args()

    model = init_gemini(args.api_key, args.model_name)
    df = pd.read_csv(args.input_csv)
    ensure_dir(args.prompt_dir)

    if args.mode == "mcq":
        template = load_prompt_template(args.prompt_eng_txt if args.language == "eng" else args.prompt_kor_txt)
        prompt_dir = f'{args.prompt_dir}/{args.mode}-{args.language}-{args.model_name}/'
        ensure_dir(prompt_dir)
        run_mcq(model, df, args.language, args.model_name, template, prompt_dir)
    else:
        run_interpret_or_trap(model, df, args.variant, args.model_name, args.mode)

if __name__ == "__main__":
    main()