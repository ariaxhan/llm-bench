"""Model Familiarity Engine — replay bootstrap.

Mines Aria's Claude .jsonl logs into replayable task tuples, redacts secrets
(fail-closed) before anything leaves for a third-party model, replays the task
through non-Claude models, and characterizes how they diverge from the known
outcome. See VISION.md and _meta/commissions/active/2026-06-27-model-familiarity-engine.md.
"""
