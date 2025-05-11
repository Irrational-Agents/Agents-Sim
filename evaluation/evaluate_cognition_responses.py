'''
Author: Yifei Wang
Github: ephiewangyf@gmail.com
Date: 2025-05-06 19:15:01
LastEditors: ephie && ephiewangyf@gmail.com
LastEditTime: 2025-05-06 20:33:08
FilePath: /Agents-Sim/evaluation/evaluate_cognition_responses.py
Description: 
'''
import numpy as np
from scipy.special import rel_entr

def evaluate_responses(agent_results, reference_answers):
    top1_matches = []
    kl_divergences = []
    explanation_notes = []

    for result in agent_results:
        qid = result["id"]
        ref = next((item for item in reference_answers if item["id"] == qid), None)
        if not ref:
            continue

        agent_answer = result.get("answer", "")
        agent_probs = result.get("probs", {})
        explanation = result.get("explanation", "")

        # Top-1 match (for CRT only or moral questions if mode choice exists)
        if "correct_answer" in ref:
            correct = ref["correct_answer"]
            match = int(agent_answer == correct)
            top1_matches.append(match)
        elif "expected_ranking" in ref:
            expected_top = ref["expected_ranking"][0]
            match = int(agent_answer == expected_top)
            top1_matches.append(match)

        # KL divergence (for moral questions with expected_human_distribution)
        if "expected_human_distribution" in ref and agent_probs:
            p = np.array([ref["expected_human_distribution"].get(opt, 1e-6) for opt in ["A", "B"]])
            q = np.array([agent_probs.get(opt, 1e-6) for opt in ["A", "B"]])
            kl = np.sum(rel_entr(p, q))
            kl_divergences.append(kl)

        # Explanation review (placeholder)
        explanation_notes.append({
            "id": qid,
            "explanation": explanation,
            "note": ref.get("note", "")
        })

    return {
        "top1_accuracy": round(np.mean(top1_matches), 3) if top1_matches else None,
        "average_kl_divergence": round(np.mean(kl_divergences), 4) if kl_divergences else None,
        "explanation_analysis": explanation_notes
    }
