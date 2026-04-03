"""Agentic capability tests -- simulating autonomous agent work."""

from __future__ import annotations

from llm_bench.models import Difficulty, TestCase

# ===================================================================
# AGENTIC 1: Tool Call Planning (multi-step tool use sequencing)
# ===================================================================
TOOL_CALL_PLANNING = TestCase(
    id="agentic-tool-planning",
    name="Tool Call Planning",
    category="agentic",
    difficulty=Difficulty.EXTREME,
    system_prompt=(
        "You are an autonomous coding agent. You have access to these tools:\n"
        "\n"
        "- file_search(pattern: str, directory: str) -> list[str]\n"
        "  Finds files matching a glob pattern in the given directory.\n"
        "\n"
        "- grep(pattern: str, file_paths: list[str]) -> list[{file: str, line: int, text: str}]\n"
        "  Searches for a regex pattern across the given files. Returns matching lines.\n"
        "\n"
        "- count(items: list) -> int\n"
        "  Returns the count of items in a list.\n"
        "\n"
        "- read_file(path: str) -> str\n"
        "  Reads and returns the full contents of a file.\n"
        "\n"
        "- write_file(path: str, content: str) -> bool\n"
        "  Writes content to the given path. Returns true on success.\n"
        "\n"
        "When given a task, output ONLY a JSON array of tool calls in execution order. "
        "Each tool call is an object with 'tool' (string) and 'args' (object) fields. "
        "Do not include any explanation, markdown, or text outside the JSON."
    ),
    user_prompt=(
        "Task: Find all Python files in the /workspace/src directory that contain "
        "TODO comments, count how many files have them, and write a summary report "
        "to /workspace/reports/todo-summary.md listing each file path and its TODO count.\n"
        "\n"
        "Output the tool call sequence as a JSON array."
    ),
    verify="instruction_follow",
    metadata={
        "checks": [
            {"type": "is_valid_json", "value": True},
            {"type": "contains", "value": "grep"},
            {"type": "contains", "value": "TODO"},
            {"type": "contains", "value": "write_file"},
            {"type": "contains", "value": "file_search"},
        ],
    },
)

# ===================================================================
# AGENTIC 2: Error Recovery (diagnose and fix failed tool calls)
# ===================================================================
ERROR_RECOVERY = TestCase(
    id="agentic-error-recovery",
    name="Error Recovery",
    category="agentic",
    difficulty=Difficulty.EXTREME,
    system_prompt=(
        "You are an autonomous agent debugging a failed API integration. "
        "When a tool call fails, you must:\n"
        "1. Identify the root cause from the error response\n"
        "2. Explain the issue in one sentence\n"
        "3. Output the corrected tool call as JSON\n"
        "\n"
        "Respond as JSON with fields: "
        '"root_cause" (string), "corrected_call" (object with "endpoint", "method", "body" fields). '
        "No markdown fences. No extra text."
    ),
    user_prompt=(
        "The following API call just failed:\n"
        "\n"
        "POST /api/v2/users/invite\n"
        "Request body:\n"
        '{"name": "John Doe", "email": "john.doe", "role": "editor", "team_id": 42}\n'
        "\n"
        "Response: 422 Unprocessable Entity\n"
        "{\n"
        '  "errors": [\n'
        '    {"field": "email", "message": "must be a valid email address", "received": "john.doe"}\n'
        "  ]\n"
        "}\n"
        "\n"
        "Diagnose and provide the corrected call."
    ),
    verify="instruction_follow",
    metadata={
        "checks": [
            {"type": "is_valid_json", "value": True},
            {"type": "contains", "value": "root_cause"},
            {"type": "contains", "value": "@"},
            {"type": "not_contains", "value": '"john.doe"'},
        ],
    },
)

# ===================================================================
# AGENTIC 3: Context Handoff (continue another agent's work)
# ===================================================================
CONTEXT_HANDOFF = TestCase(
    id="agentic-context-handoff",
    name="Context Handoff",
    category="agentic",
    difficulty=Difficulty.HARD,
    system_prompt=(
        "You are Agent B, picking up a database migration task from Agent A. "
        "Agent A has completed part of the work and left you a handoff note. "
        "Continue from where Agent A stopped. Do NOT redo any completed work. "
        "Output your migration plan as a numbered list of SQL statements or actions."
    ),
    user_prompt=(
        "=== HANDOFF NOTE FROM AGENT A ===\n"
        "\n"
        "Migration: Legacy monolith DB -> new microservices schema\n"
        "Total tables to migrate: 5 (users, products, orders, inventory, analytics)\n"
        "\n"
        "COMPLETED (do not touch):\n"
        "- [x] users table: migrated to auth-service DB, added uuid primary key, "
        "backfilled from integer IDs, foreign key references updated\n"
        "- [x] products table: migrated to catalog-service DB, split blob column "
        "into structured fields (name, description, metadata jsonb), indexed on sku\n"
        "- [x] orders table: migrated to order-service DB, partitioned by created_at "
        "(monthly), added composite index on (user_id, status)\n"
        "\n"
        "REMAINING (your job):\n"
        "- [ ] inventory table: needs to move to warehouse-service DB. Currently has "
        "product_id (integer FK to old products), warehouse_code (varchar), qty_on_hand "
        "(integer), last_restock (timestamp). Must update product_id to reference new "
        "catalog-service uuid. Add check constraint qty_on_hand >= 0.\n"
        "- [ ] analytics table: needs to move to analytics-service DB. Currently 420M rows. "
        "Has event_type (varchar), user_id (integer FK to old users), payload (jsonb), "
        "created_at (timestamp). Must update user_id to uuid reference. Needs partitioning "
        "by created_at (weekly) due to volume. Consider columnar storage for query performance.\n"
        "\n"
        "CONSTRAINTS:\n"
        "- Zero downtime required. Use logical replication during cutover.\n"
        "- All FKs referencing old integer IDs must be updated to new UUIDs.\n"
        "- Rollback plan required for each table.\n"
        "=== END HANDOFF ===\n"
        "\n"
        "Continue the migration. Cover both remaining tables with specific SQL/actions."
    ),
    verify="instruction_follow",
    metadata={
        "checks": [
            {"type": "contains", "value": "inventory"},
            {"type": "contains", "value": "analytics"},
            {"type": "contains", "value": "uuid"},
            {"type": "contains", "value": "partition"},
            {"type": "not_contains", "value": "CREATE TABLE users"},
            {"type": "not_contains", "value": "CREATE TABLE products"},
            {"type": "not_contains", "value": "CREATE TABLE orders"},
        ],
    },
)

# ===================================================================
# AGENTIC 4: Scope Judgment (restraint under ambiguity)
# ===================================================================
SCOPE_JUDGMENT = TestCase(
    id="agentic-scope-judgment",
    name="Scope Judgment",
    category="agentic",
    difficulty=Difficulty.HARD,
    system_prompt=(
        "You are an autonomous coding agent working on a large production codebase. "
        "You have full write access to the repository. "
        "When a request is ambiguous or lacks critical context, you MUST ask clarifying "
        "questions before taking action. Making assumptions on production code is dangerous. "
        "Never write code until you understand the problem."
    ),
    user_prompt=(
        "User message: \"Fix the authentication\"\n"
        "\n"
        "Context available to you:\n"
        "- The repo has 340 files across 12 services\n"
        "- There are 3 auth-related modules: OAuth2 login flow, API key validation, "
        "and JWT session management\n"
        "- No error logs, stack traces, or bug reports were provided\n"
        "- No tests are currently failing\n"
        "\n"
        "Respond to the user."
    ),
    verify="instruction_follow",
    metadata={
        "checks": [
            {"type": "contains", "value": "?"},
            {"type": "not_contains", "value": "```"},
            {"type": "not_contains", "value": "def "},
            {"type": "not_contains", "value": "function "},
            {"type": "max_words", "value": 150},
        ],
    },
)

# ===================================================================
# AGENTIC 5: Self-Correction (learn from test failures)
# ===================================================================
SELF_CORRECTION = TestCase(
    id="agentic-self-correction",
    name="Self-Correction",
    category="agentic",
    difficulty=Difficulty.EXTREME,
    system_prompt=(
        "You are an autonomous agent that wrote a function, but it failed tests. "
        "Analyze the test failures and produce a corrected version. "
        "Output only the corrected Python function. No explanation."
    ),
    user_prompt=(
        "Your previous implementation:\n"
        "```python\n"
        "def merge_intervals(intervals: list[tuple[int, int]]) -> list[tuple[int, int]]:\n"
        '    """Merge overlapping intervals. Returns sorted, non-overlapping intervals."""\n'
        "    if not intervals:\n"
        "        return []\n"
        "    intervals.sort()\n"
        "    merged = [intervals[0]]\n"
        "    for start, end in intervals[1:]:\n"
        "        if start <= merged[-1][1]:\n"
        "            merged[-1] = (merged[-1][0], end)\n"
        "        else:\n"
        "            merged.append((start, end))\n"
        "    return merged\n"
        "```\n"
        "\n"
        "Test results (3 of 5 passed, 2 FAILED):\n"
        "\n"
        "PASSED: merge_intervals([(1,3),(2,6),(8,10)]) == [(1,6),(8,10)]\n"
        "PASSED: merge_intervals([]) == []\n"
        "PASSED: merge_intervals([(1,4),(4,5)]) == [(1,5)]\n"
        "FAILED: merge_intervals([(1,10),(2,3),(4,5)]) \n"
        "  Expected: [(1,10)]\n"
        "  Got:      [(1,5)]\n"
        "FAILED: merge_intervals([(5,5),(5,5),(5,5)]) \n"
        "  Expected: [(5,5)]\n"
        "  Got:      [(5,5),(5,5),(5,5)]\n"
        "\n"
        "Fix the function to pass all tests. Output only the corrected code."
    ),
    verify="code_gen",
    metadata={
        "test_code": (
            "# Test all 5 cases\n"
            "assert merge_intervals([(1,3),(2,6),(8,10)]) == [(1,6),(8,10)]\n"
            "assert merge_intervals([]) == []\n"
            "assert merge_intervals([(1,4),(4,5)]) == [(1,5)]\n"
            "assert merge_intervals([(1,10),(2,3),(4,5)]) == [(1,10)]\n"
            "assert merge_intervals([(5,5),(5,5),(5,5)]) == [(5,5)]\n"
            "# Additional edge cases\n"
            "assert merge_intervals([(1,100),(2,3),(4,50),(60,70)]) == [(1,100)]\n"
            "assert merge_intervals([(1,2)]) == [(1,2)]\n"
            "print('ALL TESTS PASSED')\n"
        ),
    },
)

# ===================================================================
# AGENTIC 6: Parallel Decomposition (architectural task splitting)
# ===================================================================
PARALLEL_DECOMPOSITION = TestCase(
    id="agentic-parallel-decomp",
    name="Parallel Decomposition",
    category="agentic",
    difficulty=Difficulty.HARD,
    system_prompt=(
        "You are a task orchestrator for a team of autonomous coding agents. "
        "Given a complex task, decompose it into subtasks and identify which can "
        "run in parallel vs which have sequential dependencies. "
        "Output as JSON with fields: "
        '"parallel_groups" (list of lists -- each inner list is a group of tasks that can run simultaneously), '
        '"rationale" (string explaining dependency reasoning). '
        "Tasks within the same group run in parallel. Groups execute sequentially (group 1 before group 2, etc). "
        "No markdown fences."
    ),
    user_prompt=(
        "Task: Set up a new user-notifications microservice from scratch.\n"
        "\n"
        "Required deliverables:\n"
        "1. PostgreSQL schema (notifications table, preferences table, delivery_log table)\n"
        "2. REST API endpoints (GET /notifications, POST /notifications, PATCH /notifications/:id/read, "
        "GET /preferences, PUT /preferences)\n"
        "3. Authentication middleware (validate JWT, extract user_id, reject expired tokens)\n"
        "4. WebSocket endpoint for real-time push (/ws/notifications)\n"
        "5. Unit tests for all API endpoints\n"
        "6. Integration tests (API -> DB round-trip, WebSocket delivery)\n"
        "7. Dockerfile and docker-compose.yml (app + postgres + redis for WebSocket pub/sub)\n"
        "8. CI pipeline config (lint, test, build, push image)\n"
        "9. OpenAPI spec / documentation\n"
        "\n"
        "Decompose into parallel groups and sequential dependencies."
    ),
    verify="instruction_follow",
    metadata={
        "checks": [
            {"type": "is_valid_json", "value": True},
            {"type": "contains", "value": "parallel"},
            {"type": "contains", "value": "sequential"},
            {"type": "contains", "value": "rationale"},
        ],
    },
)

# ===================================================================
# AGENTIC 7: Information Triage (find root cause in noisy logs)
# ===================================================================
INFORMATION_TRIAGE = TestCase(
    id="agentic-info-triage",
    name="Information Triage",
    category="agentic",
    difficulty=Difficulty.HARD,
    system_prompt=(
        "You are a production incident responder. Analyze the log output and identify "
        "the root cause of the failure. Ignore warnings and noise that are not the actual problem. "
        "Respond with JSON: "
        '{"root_cause": "one sentence", "evidence": "the relevant log line", "severity": "critical|high|medium|low", '
        '"action": "immediate fix recommendation"}. '
        "No markdown fences."
    ),
    user_prompt=(
        "Service: order-processing-worker\n"
        "Incident: Orders stuck in 'pending' state for 12+ minutes\n"
        "\n"
        "=== LOGS (last 5 minutes) ===\n"
        "2026-04-03T14:00:01Z INFO  [worker-3] Processing order #98431, items: 2\n"
        "2026-04-03T14:00:01Z INFO  [worker-1] Processing order #98429, items: 5\n"
        "2026-04-03T14:00:02Z WARN  [pool] Connection pool at 80% capacity (16/20)\n"
        "2026-04-03T14:00:02Z INFO  [worker-2] Order #98430 payment validated\n"
        "2026-04-03T14:00:03Z INFO  [worker-3] Order #98431 payment validated\n"
        "2026-04-03T14:00:03Z WARN  [metrics] Latency p99 elevated: 2340ms (threshold: 2000ms)\n"
        "2026-04-03T14:00:04Z INFO  [worker-1] Reserving inventory for order #98429\n"
        "2026-04-03T14:00:04Z INFO  [worker-2] Reserving inventory for order #98430\n"
        "2026-04-03T14:00:05Z INFO  [worker-3] Reserving inventory for order #98431\n"
        "2026-04-03T14:00:05Z WARN  [cache] Redis SLOWLOG: command took 450ms\n"
        "2026-04-03T14:00:06Z INFO  [worker-1] Inventory reserved for #98429\n"
        "2026-04-03T14:00:06Z ERROR [worker-2] Failed to acquire distributed lock: "
        "lock 'inventory:warehouse-7' held by worker-9 (expired ) -- "
        "lock server returned DEADLOCK_DETECTED, all waiters timed out after 30s\n"
        "2026-04-03T14:00:06Z INFO  [worker-3] Inventory reserved for #98431\n"
        "2026-04-03T14:00:07Z WARN  [pool] Connection pool at 85% capacity (17/20)\n"
        "2026-04-03T14:00:07Z INFO  [worker-1] Charging payment for #98429\n"
        "2026-04-03T14:00:08Z ERROR [worker-2] Order #98430 failed: could not complete "
        "inventory reservation -- upstream lock failure\n"
        "2026-04-03T14:00:08Z INFO  [worker-2] Requeueing order #98430, attempt 4/5\n"
        "2026-04-03T14:00:09Z WARN  [metrics] Latency p99 elevated: 3100ms (threshold: 2000ms)\n"
        "2026-04-03T14:00:09Z INFO  [worker-3] Charging payment for #98431\n"
        "2026-04-03T14:00:10Z WARN  [cache] Redis SLOWLOG: command took 380ms\n"
        "2026-04-03T14:00:10Z INFO  [heartbeat] All workers alive: worker-1, worker-2, worker-3\n"
        "2026-04-03T14:00:11Z ERROR [worker-2] Failed to acquire distributed lock: "
        "lock 'inventory:warehouse-7' held by worker-9 (expired) -- DEADLOCK_DETECTED\n"
        "2026-04-03T14:00:12Z ERROR [worker-2] Order #98430 failed: inventory reservation "
        "timeout, attempt 5/5 EXHAUSTED\n"
        "2026-04-03T14:00:12Z ERROR [worker-2] Order #98430 moved to DEAD_LETTER queue\n"
        "2026-04-03T14:00:13Z INFO  [worker-1] Order #98429 completed successfully\n"
        "2026-04-03T14:00:13Z INFO  [worker-3] Order #98431 completed successfully\n"
        "2026-04-03T14:00:14Z WARN  [pool] Connection pool at 75% capacity (15/20)\n"
        "2026-04-03T14:00:14Z WARN  [metrics] Dead letter queue size: 23 (threshold: 10)\n"
        "=== END LOGS ===\n"
        "\n"
        "What is the root cause? Not the symptoms -- the actual underlying issue."
    ),
    verify="instruction_follow",
    metadata={
        "checks": [
            {"type": "is_valid_json", "value": True},
            {"type": "contains", "value": "root_cause"},
            {"type": "regex_match", "value": "(?i)deadlock|lock.*expired|worker-9|distributed.lock"},
            {"type": "not_contains", "value": "SLOWLOG"},
            {"type": "not_contains", "value": "connection pool"},
        ],
    },
)


AGENTIC_TESTS: list[TestCase] = [
    TOOL_CALL_PLANNING,
    ERROR_RECOVERY,
    CONTEXT_HANDOFF,
    SCOPE_JUDGMENT,
    SELF_CORRECTION,
    PARALLEL_DECOMPOSITION,
    INFORMATION_TRIAGE,
]
