"""
harness/mlflow_adapter.py  -  W3-1: wrap D01-D11 checks as native MLflow scorers.

Verified against MLflow 3.16.1:
    mlflow.genai.evaluate(data, scorers, predict_fn=None)
    @mlflow.genai.scorer(name=...)  -> scorer fn receives subset of
                                        (inputs, outputs, expectations)

Each scorer calls the REAL assure-core check and returns 1 (pass) / 0 (fail),
so the checks run inside MLflow's own evaluation engine -- native dashboards,
comparisons, and a slot for judges (W3-2). assure-core stays MLflow-free; this
thin adapter is the only MLflow-aware layer.
"""

from __future__ import annotations

from mlflow.genai import scorer

from assure_core.checks.d01_schema import check_schema
from assure_core.checks.d02_pii import check_pii
from assure_core.checks.d04_citations import check_citations
from assure_core.checks.d07_language import check_language
from assure_core.checks.d08_refusal import check_refusal
from assure_core.checks.d10_retrieval import check_retrieval
from assure_core.checks.d11_canary import check_canary


# Each scorer reads the case's `expectations` and the app's `outputs`
# (a dict with answer/citations/retrieved_ids/refused/reason), applies the
# matching check, and returns 1/0. If an expectation isn't present, it returns
# None so MLflow skips it for that case.

@scorer(name="D01_schema")
def d01(outputs, expectations):
    if "d01_schema" not in expectations:
        return None
    return int(check_schema(outputs, expectations["d01_schema"]).passed)


@scorer(name="D02_pii")
def d02(outputs, expectations):
    if not expectations.get("d02_pii"):
        return None
    return int(check_pii(outputs.get("answer", "")).passed)


@scorer(name="D04_citations")
def d04(outputs, expectations):
    if not expectations.get("d04_citations"):
        return None
    from harness import rag_system
    corpus = rag_system._load_corpus()
    retrieved = {d: corpus.get(d, "") for d in outputs.get("retrieved_ids", [])}
    return int(check_citations(outputs.get("citations", []), retrieved).passed)


@scorer(name="D07_language")
def d07(outputs, expectations):
    if "d07_language" not in expectations:
        return None
    return int(check_language(outputs.get("answer", ""), expectations["d07_language"]).passed)


@scorer(name="D08_refusal")
def d08(outputs, expectations):
    if "d08_expected_refusal" not in expectations:
        return None
    return int(check_refusal(outputs, expectations["d08_expected_refusal"]).passed)


@scorer(name="D10_retrieval")
def d10(outputs, expectations):
    if "d10_gold_doc" not in expectations:
        return None
    return int(check_retrieval(outputs.get("retrieved_ids", []),
                               expectations["d10_gold_doc"],
                               expectations.get("d10_k", 3)).passed)


@scorer(name="D11_canary")
def d11(outputs, expectations):
    if "d11_canaries" not in expectations:
        return None
    return int(check_canary(outputs.get("answer", ""), [],
                            expectations["d11_canaries"]).passed)


# All deterministic scorers, ready to pass to mlflow.genai.evaluate(scorers=...)
ALL_SCORERS = [d01, d02, d04, d07, d08, d10, d11]
