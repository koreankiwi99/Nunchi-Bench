import os
import pandas as pd

VARIANTS = ["kor_default", "eng_default", "kor_kor", "eng_kor"]
MODES = ["interpret", "trap"]

def extract_info_from_filename(path):
    base = os.path.basename(path)
    parts = base.split("_")
    model = "_".join(parts[:-3])  # model name (can contain underscores)
    mode = parts[-3]
    variant = parts[-2]
    return model, variant, mode

def summarize_by_variant_and_mode(eval_dir, output_base_dir):
    for mode in MODES:
        mode_dir = os.path.join(eval_dir, mode)
        if not os.path.exists(mode_dir):
            continue

        for variant in VARIANTS:
            variant_dir = os.path.join(mode_dir, variant)
            if not os.path.isdir(variant_dir):
                continue

            rows = []
            for fname in os.listdir(variant_dir):
                if not fname.endswith(".csv"):
                    continue
                fpath = os.path.join(variant_dir, fname)
                try:
                    model, _, _ = extract_info_from_filename(fpath)
                    df = pd.read_csv(fpath)
                    df = df[pd.to_numeric(df["score"], errors="coerce").notnull()]
                    total_score = df["score"].astype(float).sum()
                    avg_score = df["score"].astype(float).mean()
                    count = len(df)
                    rows.append({
                        "model": model,
                        "variant": variant,
                        "mode": mode,
                        "total_score": total_score,
                        "average_score": round(avg_score, 3),
                        "count": count
                    })
                except Exception as e:
                    print(f"❌ Failed to process {fpath}: {e}")

            if rows:
                output_path = os.path.join(output_base_dir, f"eval_score_summary_{mode}_{variant}.csv")
                pd.DataFrame(rows).to_csv(output_path, index=False)
                print(f"📄 Saved: {output_path}")

# Run the summarizer
summarize_by_variant_and_mode("results/model_outputs", "results")