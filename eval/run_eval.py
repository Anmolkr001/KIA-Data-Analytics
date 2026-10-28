"""
Evaluation Runner for Ask Your Data Analytics Agent.
Runs the 15 benchmark CRM questions, compares against verified ground truth,
and outputs accuracy, latency, and category performance reports.
"""

import sys
import json
import time
from pathlib import Path
from typing import Dict, Any, List

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from ask_your_data.agent import AskYourDataAgent
from ask_your_data.data_loader import load_dataset
from ask_your_data.sandbox import SandboxedPandasExecutor

EVAL_DIR = ROOT_DIR / "eval"
QUESTIONS_FILE = EVAL_DIR / "test_questions.json"
REPORT_FILE = EVAL_DIR / "eval_report.json"


def evaluate_agent(provider: str = None) -> Dict[str, Any]:
    print("=" * 80)
    print("[EVAL] ASK YOUR DATA - BENCHMARK EVALUATION HARNESS")
    print("=" * 80)

    with open(QUESTIONS_FILE, "r", encoding="utf-8") as f:
        questions = json.load(f)

    df = load_dataset()
    executor = SandboxedPandasExecutor()
    agent = AskYourDataAgent(provider=provider)

    results = []
    correct_count = 0
    total_latency_ms = 0.0

    print(f"\nEvaluating {len(questions)} dealership analytics questions...\n")

    for q in questions:
        qid = q["id"]
        q_text = q["question"]
        category = q["category"]
        expected_val = q["expected_value"]
        m_type = q["metric_type"]
        tolerance = q.get("tolerance", 0.0)

        # 1. Run Ground Truth Code
        gt_res = executor.run(q["verification_code"], df)
        ground_truth = gt_res.output

        # 2. Run Agent
        t0 = time.time()
        agent_resp = agent.ask(q_text)
        latency = (time.time() - t0) * 1000
        total_latency_ms += latency

        # 3. Assess Correctness
        is_correct = False
        details = ""

        if agent_resp.success and agent_resp.df_result is not None:
            df_res = agent_resp.df_result
            # Check string representation across entire result dataframe
            df_str = df_res.to_string().lower()
            summary_str = (agent_resp.summary + " " + agent_resp.recommendation).lower()

            if m_type == "string":
                exp_str = str(expected_val).lower()
                if exp_str in df_str or exp_str in summary_str:
                    is_correct = True
                    details = f"Matched string '{expected_val}'"
                else:
                    details = f"Expected '{expected_val}' not found in result"

            elif m_type in ["percentage", "rate"]:
                exp_num = float(expected_val)
                # Search numeric columns in dataframe
                found_match = False
                for col in df_res.select_dtypes(include=["number"]).columns:
                    for val in df_res[col].dropna():
                        # Try both raw rate (0.1128) and percentage (11.28)
                        if abs(val - exp_num) <= tolerance or abs(val * 100 - exp_num) <= tolerance:
                            found_match = True
                            break
                    if found_match:
                        break

                if found_match or str(round(exp_num, 1)) in summary_str or str(round(exp_num, 2)) in summary_str:
                    is_correct = True
                    details = f"Matched rate {expected_val}% within +/-{tolerance}%"
                else:
                    details = f"Expected {expected_val}% (+/-{tolerance}%)"

            elif m_type == "count":
                exp_num = int(expected_val)
                found_match = False
                for col in df_res.select_dtypes(include=["number"]).columns:
                    if (df_res[col] == exp_num).any():
                        found_match = True
                        break

                if found_match or str(exp_num) in summary_str:
                    is_correct = True
                    details = f"Matched count {expected_val}"
                else:
                    details = f"Expected count {expected_val}"
        else:
            details = f"Execution failed: {agent_resp.error}"

        if is_correct:
            correct_count += 1
            status_tag = "[PASS]"
        else:
            status_tag = "[FAIL]"

        print(f"  {status_tag} Q{qid:02d} [{category}]: {q_text[:45]}... -> {details} ({latency:.0f}ms)")

        results.append({
            "id": qid,
            "question": q_text,
            "category": category,
            "expected": expected_val,
            "type": m_type,
            "correct": is_correct,
            "attempts": agent_resp.attempts,
            "latency_ms": round(latency, 1),
            "details": details,
        })

    accuracy_pct = round((correct_count / len(questions)) * 100, 2)
    avg_latency = round(total_latency_ms / len(questions), 1)

    # Category breakdown
    cat_stats = {}
    for r in results:
        cat = r["category"]
        if cat not in cat_stats:
            cat_stats[cat] = {"total": 0, "correct": 0}
        cat_stats[cat]["total"] += 1
        if r["correct"]:
            cat_stats[cat]["correct"] += 1

    summary_report = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "total_questions": len(questions),
        "passed": correct_count,
        "failed": len(questions) - correct_count,
        "accuracy_pct": accuracy_pct,
        "average_latency_ms": avg_latency,
        "category_breakdown": {
            cat: f"{data['correct']}/{data['total']} ({data['correct']/data['total']*100:.1f}%)"
            for cat, data in cat_stats.items()
        },
        "details": results,
    }

    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        json.dump(summary_report, f, indent=2)

    print("\n" + "=" * 80)
    print("[REPORT] EVALUATION SUMMARY REPORT")
    print("=" * 80)
    print(f"Total Questions Evaluated : {len(questions)}")
    print(f"Benchmark Accuracy        : {accuracy_pct}% ({correct_count}/{len(questions)} Passed)")
    print(f"Average Query Latency     : {avg_latency} ms")
    print("\nCategory Breakdown:")
    for cat, stat in summary_report["category_breakdown"].items():
        print(f"  * {cat:<20}: {stat}")
    print(f"\nFull report saved to: {REPORT_FILE}")
    print("=" * 80)

    return summary_report


if __name__ == "__main__":
    evaluate_agent()
