"""
Predefined intent patterns for comprehensive intent recognition.
"""
from typing import Dict, List


# Debate history intent patterns
DEBATE_HISTORY_PATTERNS: Dict[str, List[str]] = {
    "list_debates": [
        r"show.*debates?",
        r"list.*debates?",
        r"what.*debates?.*there",
        r"show.*history",
        r"show.*debate.*history",
        r"view.*debates?",
        r"debates?.*history",
        r"show.*previous.*debate",
        r"show.*past.*debate",
        r"show.*completed.*debate",
        r"show.*recent.*debate",
        r"display.*debate.*list",
        r"get.*debate.*list"
    ],
    "show_specific_debate": [
        r"show.*debate.*(\w+)",
        r"display.*debate.*(\w+)",
        r"view.*debate.*(\w+)",
        r"show.*session.*(\w+)",
        r"show.*debate.*session.*(\w+)",
        r"show.*results.*for.*debate.*(\w+)",
        r"show.*results.*for.*session.*(\w+)",
        r"show.*latest.*debate",
        r"show.*recent.*debate",
        r"show.*most.*recent.*debate",
        r"show.*last.*debate",
        r"show.*recent.*results",
        r"show.*latest.*results"
    ],
    "search_debates": [
        r"find.*debates?.*about.*(.*)",
        r"search.*debates?.*about.*(.*)",
        r"look.*for.*debates?.*about.*(.*)",
        r"find.*debate.*on.*(.*)",
        r"search.*debate.*on.*(.*)"
    ]
}


# Document conversion intent patterns
DOCUMENT_CONVERSION_PATTERNS: Dict[str, List[str]] = {
    "convert": [
        r"convert.*to.*(\w+)",
        r"change.*format.*to.*(\w+)",
        r"transform.*to.*(\w+)",
        r"convert.*file.*to.*(\w+)",
        r"change.*from.*(\w+).*to.*(\w+)",
        r"format.*converter",
        r"format.*transformation",
        r"file.*conversion",
        r"convert.*document",
        r"change.*document.*format"
    ]
}


# Wiki management intent patterns
WIKI_MANAGEMENT_PATTERNS: Dict[str, List[str]] = {
    "create_wiki": [
        r"create.*wiki.*page",
        r"create.*page.*about",
        r"make.*wiki.*page",
        r"new.*wiki.*page",
        r"add.*to.*wiki",
        r"write.*wiki.*page"
    ],
    "list_wiki": [
        r"list.*wikis?",
        r"show.*wiki.*list",
        r"show.*wiki.*pages?",
        r"list.*wiki.*pages?",
        r"what.*wikis?.*there"
    ],
    "export_wiki": [
        r"export.*wiki",
        r"save.*wiki",
        r"download.*wiki",
        r"extract.*wiki"
    ],
    "search_wiki": [
        r"find.*wiki.*about.*(.*)",
        r"search.*wiki.*for.*(.*)",
        r"look.*for.*page.*about.*(.*)",
        r"wiki.*search.*for.*(.*)"
    ]
}


# Paper download intent patterns
PAPER_DOWNLOAD_PATTERNS: Dict[str, List[str]] = {
    "download_paper": [
        r"download.*paper.*(.*)",
        r"fetch.*paper.*(.*)",
        r"get.*research.*(.*)",
        r"find.*article.*(.*)",
        r"search.*papers?.*about.*(.*)",
        r"get.*academic.*(.*)",
        r"download.*research.*(.*)",
        r"get.*research.*paper",
        r"download.*article"
    ],
    "list_papers": [
        r"show.*papers?",
        r"list.*papers?",
        r"what.*papers?.*downloaded",
        r"view.*downloaded.*papers?",
        r"show.*downloaded.*articles"
    ]
}


# Session management intent patterns
SESSION_MANAGEMENT_PATTERNS: Dict[str, List[str]] = {
    "list_sessions": [
        r"show.*sessions?",
        r"list.*sessions?",
        r"what.*sessions?.*there",
        r"show.*history",
        r"view.*chat.*history",
        r"show.*chat.*history",
        r"list.*conversations?",
        r"show.*conversations?",
        r"what.*have.*we.*talked.*about"
    ],
    "view_specific_session": [
        r"show.*session.*(\w+)",
        r"view.*session.*(\w+)",
        r"show.*conversation.*(\w+)",
        r"view.*conversation.*(\w+)",
        r"show.*chat.*(\w+)",
        r"view.*chat.*(\w+)"
    ],
    "clear_sessions": [
        r"clear.*sessions?",
        r"delete.*history",
        r"erase.*chat.*history",
        r"reset.*sessions?",
        r"start.*fresh",
        r"new.*session",
        r"restart.*conversation"
    ]
}


# Role management intent patterns
ROLE_MANAGEMENT_PATTERNS: Dict[str, List[str]] = {
    "list_roles": [
        r"show.*roles?",
        r"list.*roles?",
        r"what.*roles?.*available",
        r"view.*roles?",
        r"show.*available.*roles?",
        r"what.*can.*roles.*do"
    ],
    "view_role": [
        r"show.*role.*(\w+)",
        r"view.*role.*(\w+)",
        r"tell.*me.*about.*role.*(\w+)",
        r"describe.*role.*(\w+)",
        r"role.*information.*(\w+)"
    ]
}


# Model management intent patterns
MODEL_MANAGEMENT_PATTERNS: Dict[str, List[str]] = {
    "list_models": [
        r"show.*models?",
        r"list.*models?",
        r"what.*models?.*available",
        r"view.*available.*models?",
        r"list.*available.*models?",
        r"show.*LLM.*models?",
        r"what.*can.*models.*do"
    ],
    "switch_model": [
        r"use.*model.*(\w+)",
        r"switch.*to.*model.*(\w+)",
        r"change.*model.*to.*(\w+)",
        r"switch.*to.*(\w+)"
    ]
}