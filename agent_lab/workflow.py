from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal
import json


Agent = Literal[
    "blockchain",
    "graph",
    "risk",
    "platform",
    "copilot",
    "ui",
]

TaskStatus = Literal[
    "pending",
    "ready",
    "running",
    "completed",
    "blocked",
    "failed",
]


@dataclass
class WorkflowTask:
    task_id: str
    agent: Agent
    objective: str
    depends_on: list[str] = field(default_factory=list)
    status: TaskStatus = "pending"


# ------------------------------------------------------------------
# WORKFLOW DEFINITION
# ------------------------------------------------------------------

V1_WORKFLOW: list[WorkflowTask] = [
    WorkflowTask(
        task_id="blockchain-001",
        agent="blockchain",
        objective=(
            "Implement the blockchain/data foundation for the first "
            "CryptoTrace vertical slice, including normalized transaction "
            "data, provider abstraction, evidence creation, and provenance."
        ),
    ),

    WorkflowTask(
        task_id="graph-001",
        agent="graph",
        objective=(
            "Implement the transaction graph layer using the blockchain "
            "contracts and evidence produced by blockchain-001."
        ),
        depends_on=["blockchain-001"],
    ),

    WorkflowTask(
        task_id="risk-001",
        agent="risk",
        objective=(
            "Implement the deterministic CryptoTrace Risk and Decision "
            "Engine using approved parameters, rules, scoring, and evidence "
            "references."
        ),
        depends_on=["graph-001"],
    ),

    WorkflowTask(
        task_id="platform-001",
        agent="platform",
        objective=(
            "Implement the backend/API layer that exposes investigation "
            "data, risk results, provenance, and the Structured Evidence "
            "Packet."
        ),
        depends_on=["risk-001"],
    ),

    WorkflowTask(
        task_id="copilot-001",
        agent="copilot",
        objective=(
            "Implement the V1 Nemotron Copilot capabilities: evidence "
            "summarization, risk-factor explanation, and evidence-grounded "
            "Q&A with validation and graceful failure."
        ),
        depends_on=["platform-001"],
    ),

    WorkflowTask(
        task_id="ui-001",
        agent="ui",
        objective=(
            "Integrate the CryptoTrace frontend with the completed backend "
            "vertical slice and expose investigation, graph, risk, evidence, "
            "and Copilot workflows."
        ),
        depends_on=["copilot-001"],
    ),

    WorkflowTask(
        task_id="integration-001",
        agent="platform",
        objective=(
            "Run the complete end-to-end CryptoTrace vertical slice, verify "
            "all contracts, execute tests, and report remaining failures."
        ),
        depends_on=["ui-001"],
    ),
]


# ------------------------------------------------------------------
# PERSISTENT STATE
# ------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parent.parent
STATE_DIR = REPO_ROOT / "tasks"
STATE_FILE = STATE_DIR / "workflow_state.json"


def _default_state() -> dict[str, str]:
    return {
        task.task_id: task.status
        for task in V1_WORKFLOW
    }


def _load_state() -> dict[str, str]:
    """
    Load persistent workflow state.

    If no state file exists yet, initialize it from V1_WORKFLOW.
    """

    STATE_DIR.mkdir(parents=True, exist_ok=True)

    if not STATE_FILE.exists():
        state = _default_state()
        _save_state(state)
        return state

    try:
        with STATE_FILE.open("r", encoding="utf-8") as f:
            state = json.load(f)

        if not isinstance(state, dict):
            raise ValueError("Workflow state must be a JSON object.")

        return state

    except (json.JSONDecodeError, OSError, ValueError):
        # If state is corrupted, safely rebuild it.
        state = _default_state()
        _save_state(state)
        return state


def _save_state(state: dict[str, str]) -> None:
    """
    Persist workflow state atomically.
    """

    STATE_DIR.mkdir(parents=True, exist_ok=True)

    temp_file = STATE_FILE.with_suffix(".tmp")

    with temp_file.open("w", encoding="utf-8") as f:
        json.dump(
            state,
            f,
            indent=2,
            sort_keys=True,
        )

    temp_file.replace(STATE_FILE)


def _apply_persistent_state() -> None:
    """
    Apply saved statuses to the in-memory workflow definition.
    """

    state = _load_state()

    for task in V1_WORKFLOW:
        saved_status = state.get(task.task_id)

        if saved_status in {
            "pending",
            "ready",
            "running",
            "completed",
            "blocked",
            "failed",
        }:
            task.status = saved_status


def _persist_current_state() -> None:
    state = {
        task.task_id: task.status
        for task in V1_WORKFLOW
    }

    _save_state(state)


# ------------------------------------------------------------------
# TASK ACCESS
# ------------------------------------------------------------------

def get_task(task_id: str) -> WorkflowTask:
    _apply_persistent_state()

    for task in V1_WORKFLOW:
        if task.task_id == task_id:
            return task

    raise ValueError(f"Unknown workflow task: {task_id}")


def dependencies_completed(task: WorkflowTask) -> bool:
    _apply_persistent_state()

    return all(
        get_task(dependency).status == "completed"
        for dependency in task.depends_on
    )


# ------------------------------------------------------------------
# READY TASKS
# ------------------------------------------------------------------

def get_ready_tasks() -> list[WorkflowTask]:
    """
    Return tasks that are ready to execute.

    A task is ready when:
    - it is pending and all dependencies are completed, OR
    - it is already marked ready and all dependencies are completed.
    """

    _apply_persistent_state()

    ready: list[WorkflowTask] = []
    state_changed = False

    for task in V1_WORKFLOW:

        if not dependencies_completed(task):
            continue

        if task.status == "pending":
            task.status = "ready"
            state_changed = True

        if task.status == "ready":
            ready.append(task)

    if state_changed:
        _persist_current_state()

    return ready


# ------------------------------------------------------------------
# STATUS MANAGEMENT
# ------------------------------------------------------------------

def set_task_status(
    task_id: str,
    status: TaskStatus,
) -> WorkflowTask:
    """
    Persist a task status change.

    This is the function the Lead/implementation runner should call
    whenever a task changes lifecycle state.
    """

    _apply_persistent_state()

    task = None

    for candidate in V1_WORKFLOW:
        if candidate.task_id == task_id:
            task = candidate
            break

    if task is None:
        raise ValueError(f"Unknown workflow task: {task_id}")

    task.status = status

    _persist_current_state()

    return task


def reset_workflow() -> None:
    """
    Reset every V1 task to pending.

    Useful during development/testing only.
    """

    state = _default_state()
    _save_state(state)

    _apply_persistent_state()


# ------------------------------------------------------------------
# DEBUG / INSPECTION
# ------------------------------------------------------------------

def get_workflow_status() -> list[dict[str, str]]:
    """
    Return the complete workflow state.
    """

    _apply_persistent_state()

    return [
        {
            "task_id": task.task_id,
            "agent": task.agent,
            "status": task.status,
        }
        for task in V1_WORKFLOW
    ]