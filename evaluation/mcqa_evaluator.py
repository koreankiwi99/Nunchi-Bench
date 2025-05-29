import pandas as pd
import re
import argparse

def parse_choices(choice_text):
    """Parse multiline choices into {'A': 'choice text', ...}."""
    choices = {}
    if not isinstance(choice_text, str):
        return choices
    lines = choice_text.strip().split("\n")
    for line in lines:
        match = re.match(r"([A-D])\.\s*(.+)", line.strip())
        if match:
            letter, content = match.groups()
            choices[letter.strip()] = content.strip()
    return choices

def match_prediction(pred_text, choices_dict):
    """Match predicted output to a choice letter based on letter or choice text."""
    if not isinstance(pred_text, str):
        return None
    text = pred_text.strip().upper()

    # 1. Exact letter (A/B/C/D)
    match = re.search(r"\b([A-D])\b", text)
    if match:
        return match.group(1)

    # 2. "Answer: A", "Option B"
    match = re.search(r"(ANSWER|OPTION)[\s:]*([A-D])", text)
    if match:
        return match.group(2)

    # 3. Match choice content
    for letter, choice in choices_dict.items():
        if f"{letter}. {choice}".upper() in text:
            return letter
        if choice.upper() in text:
            return letter

    return None

def evaluate_mcqa(input_csv, response_csv, output_csv=None, language="eng"):
    df_input = pd.read_csv(input_csv)
    df_response = pd.read_csv(response_csv)

    if "id" not in df_response.columns:
        df_response["id"] = df_response["ID"]  # fallback

    results = []
    correct_count = 0

    for _, row in df_response.iterrows():
        qid = row["id"]
        output = row["output"]

        gold_row = df_input[df_input["ID"] == qid]
        if gold_row.empty:
            print(f"Skipping ID {qid} (not found in input)")
            continue

        gold_row = gold_row.iloc[0]
        gold_label = str(gold_row["label"]).strip().upper()
        choice_text = gold_row[f"{language}_choices"]
        choices_dict = parse_choices(choice_text)
        pred_letter = match_prediction(output, choices_dict)

        is_correct = (pred_letter == gold_label)
        if is_correct:
            correct_count += 1

        results.append({
            "id": qid,
            "predicted": pred_letter,
            "correct": gold_label,
            "is_correct": is_correct,
            "raw_output": output
        })

    total = len(results)
    accuracy = correct_count / total if total > 0 else 0
    print(f"✅ Evaluated {total} questions.")
    print(f"🎯 Accuracy: {accuracy:.2%} ({correct_count}/{total})")

    if output_csv:
        pd.DataFrame(results).to_csv(output_csv, index=False)
        print(f"📄 Results saved to {output_csv}")

    return accuracy

def main():
    parser = argparse.ArgumentParser(description="Evaluate MCQA model outputs.")
    parser.add_argument("--input_csv", required=True, help="Original dataset with correct labels")
    parser.add_argument("--response_csv", required=True, help="CSV with model responses")
    parser.add_argument("--output_csv", help="Path to save detailed evaluation results")
    parser.add_argument("--language", default="eng", choices=["eng", "kor"], help="Use English or Korean choices")

    args = parser.parse_args()
    evaluate_mcqa(
        input_csv=args.input_csv,
        response_csv=args.response_csv,
        output_csv=args.output_csv,
        language=args.language
    )

if __name__ == "__main__":
    main()