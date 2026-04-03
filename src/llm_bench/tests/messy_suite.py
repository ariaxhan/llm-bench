"""Messy suite — real-world garbage inputs that models face in production.

Typos, broken JSON, garbled OCR, mixed formats, multilingual code,
partial data, spreadsheet chaos. Nothing is clean. Nothing is sanitized.
"""

from __future__ import annotations

from llm_bench.models import Difficulty, TestCase

# ===================================================================
# MESSY 1: Broken JSON Repair
# ===================================================================
BROKEN_JSON_REPAIR = TestCase(
    id="messy-broken-json",
    name="Broken JSON Repair",
    category="extraction",
    difficulty=Difficulty.HARD,
    system_prompt="You are a data engineer. Fix broken JSON into valid JSON. Return ONLY the corrected JSON, nothing else. No explanations, no markdown fences.",
    user_prompt="""\
Fix this broken JSON. It was copy-pasted from a config file and has multiple syntax errors. Return valid JSON only.

{name: 'Alice', age: 30, roles: ['admin', 'user',], // primary user
 active: True,
 metadata: {joined: '2024-01-15', last_login: '2024-03-20',},
 tags: ['vip', 'beta-tester',]
}
""",
    verify="instruction_follow",
    metadata={
        "checks": [
            {"type": "is_valid_json", "value": True},
            {"type": "contains", "value": "Alice"},
            {"type": "contains", "value": "30"},
            {"type": "not_contains", "value": "//"},
            {"type": "not_contains", "value": "```"},
        ],
    },
)

# ===================================================================
# MESSY 2: Typo-Riddled Instructions
# ===================================================================
TYPO_RIDDLED_INSTRUCTIONS = TestCase(
    id="messy-typo-instructions",
    name="Typo-Riddled Instructions",
    category="code",
    difficulty=Difficulty.MEDIUM,
    system_prompt="You are a Python developer. Write clean, working code based on the user's request, even if the request contains typos. Return the code in a Python code block.",
    user_prompt="""\
Wirte a funtion taht takes a lst of numbrs and retruns the avarage. Ignroe any non-numreic valuse in teh lst. Nme it `calc_avg`. If teh lst is emtpy or has no numreic valuse, retrun 0.0.

Exampel: calc_avg([1, 2, 3, "x", 4]) shuold retrun 2.5
""",
    verify="code_gen",
    metadata={
        "test_code": (
            "assert calc_avg([1, 2, 3, 'x', 4]) == 2.5\n"
            "assert calc_avg([]) == 0.0\n"
            "assert calc_avg(['a', 'b', 'c']) == 0.0\n"
            "assert calc_avg([10]) == 10.0\n"
            "assert calc_avg([1, None, 2, 'bad', 3]) == 2.0\n"
        ),
    },
)

# ===================================================================
# MESSY 3: Mixed Format Extraction
# ===================================================================
MIXED_FORMAT_EXTRACTION = TestCase(
    id="messy-mixed-formats",
    name="Mixed Format Extraction",
    category="extraction",
    difficulty=Difficulty.HARD,
    system_prompt="You are a data consolidation tool. Extract and merge structured data from any format. Return ONLY a single clean JSON array. No markdown, no explanations.",
    user_prompt="""\
These are our project dependencies from different docs that got concatenated during a Confluence export. Merge them into one clean JSON array of objects with fields: name, version, license.

## Dependencies (from architecture doc)

| Package | Version | License |
|---------|---------|---------|
| fastapi | 0.104.1 | MIT |
| pydantic | 2.5.0 | MIT |

Then from the devops YAML:
---
dependencies:
  - name: uvicorn
    version: "0.24.0"
    license: BSD-3-Clause
  - name: httpx
    version: "0.25.2"
    license: BSD-3-Clause

And someone pasted this from a CSV export in Slack:
name,version,license
sqlalchemy,2.0.23,MIT
alembic,1.13.0,MIT

Also Maria mentioned in standup: "oh we also use redis-py 5.0.1, it's MIT licensed"
""",
    verify="instruction_follow",
    metadata={
        "checks": [
            {"type": "is_valid_json", "value": True},
            {"type": "contains", "value": "fastapi"},
            {"type": "contains", "value": "uvicorn"},
            {"type": "contains", "value": "sqlalchemy"},
            {"type": "contains", "value": "redis"},
            {"type": "not_contains", "value": "```"},
            {"type": "not_contains", "value": "---"},
        ],
    },
)

# ===================================================================
# MESSY 4: Garbled OCR Comprehension
# ===================================================================
GARBLED_OCR_COMPREHENSION = TestCase(
    id="messy-garbled-ocr",
    name="Garbled OCR Comprehension",
    category="extraction",
    difficulty=Difficulty.EXTREME,
    system_prompt="You are an incident report parser. Extract structured data from text that may contain OCR errors, character substitutions, and formatting artifacts. Return ONLY valid JSON.",
    user_prompt="""\
This was scanned from a printed incident report. The OCR quality is terrible. Extract the key facts.

---
INCID3NT REP0RT #4872

Tlie server retu1med a 5O3 error at l4:32 0n March 2lst. Tlie datahase c0nnecti0n pool was exliausted (max: l00 c0nnections). Appr0ximately 2,3OO requests were dr0pped 0ver a l2-minute wind0w.

R00t cause: Tlie nightly ETL j0b (cron: O 3 * * *) fai1ed to c1ose c0nnections pr0perly after a partial fai1ure at O3:l5. Leaked c0nnections acccumu1ated unti1 tlie pool was fu1l.

Res0luti0n: Increased pool s1ze to 2OO, added c0nnection timeout of 3O sec0nds, and dep1oyed a c0nnection 1eak detect0r that ki11s idle c0nnections after 5 minutes.

Sever1ty: P1 | Team: Platform Eng | 0n-cal1: J. Nakamura
---

Return JSON with: incident_id, error_code, time, date, root_cause, requests_dropped, resolution (as array of actions), severity, team, oncall
""",
    verify="instruction_follow",
    metadata={
        "checks": [
            {"type": "is_valid_json", "value": True},
            {"type": "contains", "value": "503"},
            {"type": "contains", "value": "14:32"},
            {"type": "contains", "value": "200"},
            {"type": "contains", "value": "30"},
            {"type": "contains", "value": "Nakamura"},
            {"type": "not_contains", "value": "```"},
        ],
    },
)

# ===================================================================
# MESSY 5: Partial Information Decision
# ===================================================================
PARTIAL_INFORMATION_DECISION = TestCase(
    id="messy-partial-info",
    name="Partial Information Decision",
    category="reasoning",
    difficulty=Difficulty.HARD,
    system_prompt="You are a senior architect. When information is incomplete, make a clear recommendation anyway. State your assumptions explicitly. Do not hedge or present multiple options equally.",
    user_prompt="""\
Quick question from Slack (the PM is waiting):

"We need a message queue for the new notifications service. Here's what I know:
- Must handle 10K msgs/sec sustained, 50K burst
- Needs dead letter queue for failed deliveries
- Budget: finance hasn't approved anything yet, assume we need to justify cost
- Team: 4 backend devs, mostly Python, one knows Go
- Cloud: we're on AWS but the CTO keeps talking about going multi-cloud
- Compliance: probably SOC2 but legal hasn't confirmed
- Timeline: MVP in 3 weeks

Pick one. Tell me what you'd go with and what assumptions you're making about the unknowns."

Respond in under 200 words. Be direct. Pick ONE technology.
""",
    verify="draft_email",
    metadata={
        "min_words": 60,
        "max_words": 210,
        "required_points": [
            {"keywords": ["SQS", "RabbitMQ", "Kafka", "Redis", "NATS", "Pulsar", "queue"]},
            {"keywords": ["assum", "assuming", "assumption"]},
            {"keywords": ["unknown", "unclear", "unconfirmed", "not decided", "not confirmed", "gap"]},
        ],
        "tone": "professional",
    },
)

# ===================================================================
# MESSY 6: Mixed Language Code (Bug Hunt)
# ===================================================================
MIXED_LANGUAGE_CODE = TestCase(
    id="messy-mixed-lang-code",
    name="Mixed Language Code Bug Hunt",
    category="code",
    difficulty=Difficulty.HARD,
    system_prompt="You are a code reviewer. Find the bug in the following code. The variable names are in Japanese and comments in Spanish, but the bug is a logic error that transcends language. Explain what the bug is and how to fix it.",
    user_prompt="""\
Find the bug in this function. Don't get distracted by the naming conventions.

```python
def calcular_promedio(datos_lista):
    \"\"\"Calculate the weighted average of scored items.

    Each item is a dict with 'valor' (value) and 'peso' (weight).
    Returns the weighted average as a float.
    \"\"\"
    # Inicializar acumuladores
    suma_total = 0
    peso_total = 0

    for elemento in datos_lista:
        valor_actual = elemento['valor']   # el valor numerico
        peso_actual = elemento['peso']     # la importancia relativa

        # Acumular el valor ponderado
        suma_total += valor_actual * peso_actual
        peso_total += peso_actual

    # Calcular y devolver el promedio ponderado
    promedio = suma_total / peso_total
    return promedio


# Este test deberia funcionar pero falla con lista vacia
resultados = []
print(calcular_promedio(resultados))
```
""",
    verify="bug_detection",
    metadata={
        "bug_keywords": [
            "division by zero",
            "ZeroDivisionError",
            "empty",
            "divide by zero",
            "peso_total is 0",
            "zero division",
        ],
        "fix_keywords": [
            "check if",
            "len(",
            "peso_total == 0",
            "not datos_lista",
            "if peso_total",
            "guard",
            "empty list",
        ],
        "false_positives": [
            "encoding",
            "unicode",
            "variable naming",
            "import",
        ],
    },
)

# ===================================================================
# MESSY 7: Spreadsheet Chaos
# ===================================================================
SPREADSHEET_CHAOS = TestCase(
    id="messy-spreadsheet-chaos",
    name="Spreadsheet Chaos",
    category="extraction",
    difficulty=Difficulty.EXTREME,
    system_prompt="You are a data cleaning tool. Parse messy tabular data into clean JSON. Handle inconsistent delimiters, broken rows, and formatting artifacts. Return ONLY a valid JSON array of objects. No markdown, no explanations.",
    user_prompt="""\
Someone copy-pasted this from Excel into a Jira ticket. Parse it into clean JSON.

Name\tDepartment,Start Date,Salary
"Chen, Wei"\tEngineering\t2023-01-15\t145000
Martinez, Sofia,Design,2023-03-01,128000

"O'Brien, Patrick"	Engineering	2022-11-30	152000
,,,,
Johnson, Amy\tMarketing,2024-01-10\t98000
"Kim, Jun-seo",Engineering,"2023-06,15",140000

Park  Minji\tDesign\t2023-09-01   115000

Notes: Jun-seo's start date got mangled, it should be 2023-06-15. Minji is missing a comma in the original sheet.

Return a JSON array of employee objects with fields: name, department, start_date (YYYY-MM-DD), salary (integer). Fix obvious errors. Exclude the empty row and notes.
""",
    verify="instruction_follow",
    metadata={
        "checks": [
            {"type": "is_valid_json", "value": True},
            {"type": "contains", "value": "Chen, Wei"},
            {"type": "contains", "value": "Martinez"},
            {"type": "contains", "value": "O'Brien"},
            {"type": "contains", "value": "145000"},
            {"type": "contains", "value": "2023-06-15"},
            {"type": "max_lines", "value": 20},
            {"type": "not_contains", "value": "```"},
        ],
    },
)


MESSY_TESTS: list[TestCase] = [
    BROKEN_JSON_REPAIR,
    TYPO_RIDDLED_INSTRUCTIONS,
    MIXED_FORMAT_EXTRACTION,
    GARBLED_OCR_COMPREHENSION,
    PARTIAL_INFORMATION_DECISION,
    MIXED_LANGUAGE_CODE,
    SPREADSHEET_CHAOS,
]
