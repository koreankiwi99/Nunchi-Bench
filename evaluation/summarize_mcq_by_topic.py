import argparse
import os
import pandas as pd
from glob import glob

def extract_model_name(path):
    # Assumes filename like: claude-opus-4-20250514_mcq_eng.csv
    return os.path.basename(path).split("_")[0]

def summarize_mcqa_by_topic(mcq_dir, language, output_path):
    input_dir = os.path.join(mcq_dir, language)
    csv_files = glob(os.path.join(input_dir, "*.csv"))

    results = {}

    for file in csv_files:
        model_name = extract_model_name(file)
        try:
            df = pd.read_csv(file)
            if "id" not in df.columns or "correct" not in df.columns:
                continue

            for _, row in df.iterrows():
                qid = row["id"]
                is_correct = bool(row["correct"])

                if qid not in results:
                    results[qid] = {
                        "total_attempts": 0,
                        "correct_count": 0,
                        "wrong_models": []
                    }

                results[qid]["total_attempts"] += 1
                if is_correct:
                    results[qid]["correct_count"] += 1
                else:
                    results[qid]["wrong_models"].append(model_name)

        except Exception as e:
            print(f"❌ Failed to process {file}: {e}")

    # Format into DataFrame
    rows = []
    for qid, data in sorted(results.items()):
        rows.append({
            "id": qid,
            "total_attempts": data["total_attempts"],
            "correct_count": data["correct_count"],
            "wrong_models": ", ".join(data["wrong_models"])
        })

    df_summary = pd.DataFrame(rows)
    df_summary.to_csv(output_path, index=False)
    print(f"✅ Saved topic-wise MCQA summary to {output_path}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mcq_dir", default="results/model_outputs/mcq", help="Root directory of MCQA outputs")
    parser.add_argument("--language", required=True, choices=["eng", "kor"], help="Language folder (eng or kor)")
    parser.add_argument("--output_csv", help="Path to save topic summary")

    args = parser.parse_args()
    if not args.output_csv:
        args.output_csv = f"results/mcq_summary_by_topic_{args.language}.csv"

    summarize_mcqa_by_topic(args.mcq_dir, args.language, args.output_csv)

if __name__ == "__main__":
    main()
