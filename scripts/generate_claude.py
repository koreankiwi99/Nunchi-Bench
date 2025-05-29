import argparse
import csv
import os
import pandas as pd
import anthropic

MCQ_COLUMNS = ["id", "question", "choices", "output", "correct"]
INTERPRET_COLUMNS = ["id", "idx", "question", "response", "eval", "score"]
VARIANTS = ["kor_default", "eng_default", "kor_kor", "eng_kor"]

def init_claude(api_key):
    return anthropic.Anthropic(api_key=api_key)

def generate_response(client, model_name, prompt, max_tokens=1000, temperature=0.0):
    try:
        response = client.messages.create(
            model=model_name,
            max_tokens=max_tokens,
            temperature=temperature,
            system="You are a helpful assistant.",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text.strip()
    except Exception as e:
        print(f"Claude generation failed: {e}")
        return "[NO RESPONSE]"

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

def run_mcq(client, model_name, df, language, model_id, prompt_template, prompt_dir):
    output_csv = get_output_path("mcq", language, model_id)
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
                response = generate_response(client, model_name, prompt)
                if response == "[NO RESPONSE]":
                    raise ValueError("Empty or failed response, skipping save.")
                writer.writerow([qid, question, choices, response, None])
                print(f"✅ MCQ ID {qid} saved")
            except Exception as e:
                print(f"❌ Failed MCQ ID {qid}: {e}")

def run_interpret_or_trap(client, model_name, df, variant, model_id, mode):
    output_csv = get_output_path(mode, variant, model_id)
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
                if v != variant:
                    continue
                if (qid, idx) in done:
                    continue
                input_text = row[v]
                prompt = f"input: {input_text}"
                try:
                    response = generate_response(client, model_name, prompt, max_tokens=2048)
                    if response == "[NO RESPONSE]":
                        raise ValueError("Empty or failed response, skipping save.")
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

    client = init_claude(args.api_key)
    df = pd.read_csv(args.input_csv)
    ensure_dir(args.prompt_dir)

    if args.mode == "mcq":
        template = load_prompt_template(args.prompt_eng_txt if args.language == "eng" else args.prompt_kor_txt)
        prompt_dir = f'{args.prompt_dir}/{args.mode}-{args.language}-{args.model_name}/'
        ensure_dir(prompt_dir)
        run_mcq(client, args.model_name, df, args.language, args.model_name, template, prompt_dir)
    else:
        run_interpret_or_trap(client, args.model_name, df, args.variant, args.model_name, args.mode)

if __name__ == "__main__":
    main()