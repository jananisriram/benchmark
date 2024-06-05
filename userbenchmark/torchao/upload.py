import os
import csv
import torchao
from typing import List


def _get_model_set(filename: str):
    if "timm_models" in filename:
        return "timm"
    if "huggingface" in filename:
        return "huggingface"
    if "torchbench" in filename:
        return "torchbench"
    raise RuntimeError(f"Unknown model set from filename: {filename}")


def post_ci_process(output_files: List[str]):
    for path in output_files:
        perf_stats = []
        modelset = _get_model_set(path)
        test_name = f"torchao_{modelset}_perf"
        runner = "gcp_a100"
        job_id = 0
        workflow_run_id = os.environ.get("WORKFLOW_RUN_ID", 0)
        workflow_run_attempt = os.environ.get("WORKFLOW_RUN_ATTEMPT", 0)
        filename = os.path.splitext(os.path.basename(path))[0]
        head_repo = "pytorch/ao"
        head_branch = "main"
        head_sha = torchao.__version__
        print(f"Processing file {path} ")
        with open(path) as csvfile:
            reader = csv.DictReader(csvfile, delimiter=",")

            for row in reader:
                row.update(
                    {
                        "workflow_id": workflow_run_id,  # type: ignore[dict-item]
                        "run_attempt": workflow_run_attempt,  # type: ignore[dict-item]
                        "test_name": test_name,
                        "runner": runner,
                        "job_id": job_id,
                        "filename": filename,
                        "head_repo": head_repo,
                        "head_branch": head_branch,
                        "head_sha": head_sha,
                    }
                )
                perf_stats.append(row)

        # Write the decorated CSV file
        with open(path) as csvfile:
            writer = csv.DictWriter(csvfile)

            for i, row in enumerate(perf_stats):
                if i == 0:
                    writer.fieldnames = row.keys()
                    writer.writeheader()
                writer.writerow(row)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--test-file", type=str, help="Add file to test.")
    args = parser.parse_args()
    post_ci_process(args.test_file)