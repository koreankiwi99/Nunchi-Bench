import pandas as pd
import re
import os
import argparse

def parse_choices(choice_text):
    choices = {}
    if not isinstance(choice_text, str):
        return choices
    for line in choice_text.strip().split("\n"):
        match = re.match(r"([A-D])\.\s*(.+)", line.strip())
        if match:
            letter, content = match.groups()
            choices[letter.strip()] = content.strip()
    return choices

def match_prediction(pred_text, choices_dict):
    if not isinstance(pred_text, str):
        return None
    text = pred_text.strip().upper()

    match = re.search(r"\b([A-D])\b", text)
    if match:
        return match.group(1)

    match = re.search(r"(ANSWER|OPTION)[\s:]*([A-D])", text)
    if match:
        return match.group(2)

    for letter, choice in choices_dict.items():
        if f"{letter}. {choice}".upper() in text or choice.upper() in text:
            return letter
    return None

def evaluate_mcqa(input_csv, response_csv, language="eng"):
    df_input = pd.read_csv(input_csv)
    df_response = pd.read_csv(response_csv)

    if "id" not in df_response.columns and "ID" in df_response.columns:
        df_response["id"] = df_response["ID"]

    if "correct" in df_response.columns and df_response["correct"].notnull().all():
        print(f"✅ Skipping already evaluated: {os.path.basename(response_csv)}")
        return

    correct_count = 0
    for i, row in df_response.iterrows():
        if "correct" in df_response.columns and pd.notnull(row.get("correct", None)):
            continue

        qid = row["id"]
        output = row["output"]

        gold_row = df_input[df_input["ID"] == qid]
        if gold_row.empty:
            print(f"⚠️ Skipping ID {qid} (not in input)")
            continue

        gold_row = gold_row.iloc[0]
        gold_label = str(gold_row["label"]).strip().upper()
        choices_dict = parse_choices(gold_row[f"{language}_choices"])
        pred_letter = match_prediction(output, choices_dict)

        is_correct = pred_letter == gold_label
        correct_count += int(is_correct)

        df_response.at[i, "correct"] = is_correct

    total = len(df_response)
    accuracy = correct_count / total if total > 0 else 0
    print(f"🎯 {os.path.basename(response_csv)}: {correct_count}/{total} = {accuracy:.2%}")
    df_response.to_csv(response_csv, index=False)

def evaluate_all_files(input_csv, base_dir, language="eng"):
    for root, _, files in os.walk(base_dir):
        for file in files:
            if file.endswith(".csv"):
                full_path = os.path.join(root, file)
                try:
                    evaluate_mcqa(input_csv, full_path, language)
                except Exception as e:
                    print(f"❌ Failed on {full_path}: {e}")

def main():
    parser = argparse.ArgumentParser(description="Evaluate all MCQA CSVs under a directory recursively.")
    parser.add_argument("--input_csv", required=True, help="Path to reference MCQA file with labels.")
    parser.add_argument("--mcq_dir", required=True, help="Path to directory containing MCQA model outputs.")
    parser.add_argument("--language", default="eng", choices=["eng", "kor"], help="Choice language.")
    args = parser.parse_args()

    evaluate_all_files(args.input_csv, args.mcq_dir, args.language)

if __name__ == "__main__":
    main()