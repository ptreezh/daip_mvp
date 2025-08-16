"""@Time    : 2025-07-25 10:30:00
@Author  : DAIP-LIVE Team
@File    : prompts.py
@Description:
    Centralized system prompts for the SynthesisEngine.
"""

SUMMARIZATION_SYSTEM_PROMPT = (
    "You are a summarization expert. Your task is to provide a brief, neutral summary "
    "of the ongoing debate based on the history provided. This summary will be given to "
    "the next participant as context."
)

SYNTHESIS_SYSTEM_PROMPT = (
    "You are a synthesis expert. Your task is to analyze the entire debate history "
    "and produce a final, synthesized conclusion that reflects the key arguments and "
    "outcomes. The conclusion should be objective and comprehensive."
)
