import os
import csv
import pandas as pd
from glob import glob
import openai
from tqdm import tqdm

STATEMENT_FILE = "data/nunchi_mcq.csv"
SYSTEM_PROMPTS = {
    "interpret": "prompts/eval_system_prompt_interpret.txt",
    "trap": "prompts/eval_system_prompt_trap.txt"
}
VARIANTS = ["kor_default", "eng_default", "kor_kor", "eng_kor"]
MODEL = "gpt-4-turbo-2024-04-09"

def load_statements(path):
    df = pd.read_csv(path)
    return {int(row["ID"]): (row["eng_contents"], row["kor_contents"]) for _, row in df.iterrows()}

def load_system_prompt(mode):
    with open(SYSTEM_PROMPTS[mode], encoding="utf-8") as f:
        return f.read()

def generate_eval(system, prompt, client):
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": prompt}
            ],
            temperature=0.0,
            max_tokens=100
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"❌ GPT evaluation failed: {e}")
        return ""

def process_file(file_path, statements, mode, client):
    df = pd.read_csv(file_path)
    df["eval"] = df["eval"].astype("object")
    if "eval" not in df.columns or "score" not in df.columns:
        print(f"❌ Missing 'eval' or 'score' columns in {file_path}")
        return

    system_prompt = load_system_prompt(mode)
    modified = False

    for i, row in tqdm(df.iterrows()):
        if pd.notna(row["eval"]) and row["eval"] != "":
            continue

        qid = int(row["id"])
        idx = int(row["idx"])
        question = row["question"]
        response = row["response"]

        if qid not in statements:
            print(f"❌ Missing statement for ID {qid}")
            continue

        eng_stmt, kor_stmt = statements[qid]
        user_prompt = f"Statement: {eng_stmt} / {kor_stmt}\nScenario: {question}\nResponse: {response}"
        evaluation = generate_eval(system_prompt, user_prompt, client)

        if evaluation:
            df.at[i, "eval"] = evaluation
            try:
                df.at[i, "score"] = int(evaluation.split()[0])
            except:
                df.at[i, "score"] = None
        modified = True

    if modified:
        df.to_csv(file_path, index=False)
        print(f"💾 Updated: {file_path}")
    else:
        print(f"✅ No changes needed: {file_path}")

def evaluate_directory(mode, variant, client):
    path = f"results/model_outputs/{mode}/{variant}"
    statements = load_statements(STATEMENT_FILE)
    files = glob(os.path.join(path, "*.csv"))
    for file in files:
        process_file(file, statements, mode, client)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["interpret", "trap"], required=True)
    parser.add_argument("--variant", choices=VARIANTS, required=True)
    parser.add_argument("--api_key", required=True)
    args = parser.parse_args()

    client = openai.OpenAI(api_key=args.api_key)
    evaluate_directory(args.mode, args.variant, client)