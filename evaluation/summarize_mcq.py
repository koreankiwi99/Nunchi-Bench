import os
import pandas as pd
import argparse

def summarize_mcqa_results(language_dir, language):
    summary = []

    for file in os.listdir(language_dir):
        if not file.endswith(".csv"):
            continue

        path = os.path.join(language_dir, file)
        try:
            df = pd.read_csv(path)
            if "correct" not in df.columns:
                continue

            num_questions = len(df)
            num_correct = df["correct"].sum()
            accuracy = num_correct / num_questions if num_questions else 0.0

            model_name = file.split("_")[0]

            summary.append({
                "model_name": model_name,
                "language": language,
                "file": file,
                "num_questions": num_questions,
                "num_correct": num_correct,
                "accuracy": f"{accuracy:.2%}"
            })
        except Exception as e:
            print(f"❌ Failed to process {file}: {e}")

    return pd.DataFrame(summary)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mcq_dir", default="results/model_outputs/mcq", help="Base path to MCQ results")
    parser.add_argument("--language", required=True, choices=["eng", "kor"], help="Subdirectory for language (e.g., eng or kor)")
    parser.add_argument("--output_csv", help="Path to save summary CSV (default: results/mcq_summary_{lang}.csv)")
    args = parser.parse_args()

    language_dir = os.path.join(args.mcq_dir, args.language)
    if not os.path.exists(language_dir):
        raise FileNotFoundError(f"Directory not found: {language_dir}")

    df_summary = summarize_mcqa_results(language_dir, args.language)

    if df_summary.empty:
        print("❌ No completed results found.")
    else:
        print(df_summary.to_string(index=False))

    # Default output path
    output_path = args.output_csv or f"results/mcq_summary_{args.language}.csv"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df_summary.to_csv(output_path, index=False)
    print(f"📄 Summary saved to: {output_path}")

if __name__ == "__main__":
    main()