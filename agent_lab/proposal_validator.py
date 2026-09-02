from dataclasses import dataclass
from pathlib import Path
import re

from agent_lab.workflow import WorkflowTask


@dataclass
class ValidationResult:
    valid: bool
    issues: list[str]


class ProposalValidator:
    """
    Validates specialist proposals against:

    - actual repository state
    - specialist scope
    - project technology
    - proposed agent handoffs
    - security constraints
    - implementation-planning requirements

    The validator distinguishes between:

    1. Claims that a repository path already exists.
    2. New files/directories proposed for implementation.
    """

    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def validate(
        self,
        task: WorkflowTask,
        proposal: str,
    ) -> ValidationResult:

        issues: list[str] = []
        proposal_lower = proposal.lower()

        # =========================================================
        # 1. BASIC PROPOSAL REQUIREMENTS
        # =========================================================

        if not proposal.strip():
            issues.append(
                "Specialist returned an empty proposal."
            )

        if "status:" not in proposal_lower:
            issues.append(
                "Proposal does not contain a final STATUS declaration."
            )

        # =========================================================
        # 2. REPOSITORY INSPECTION
        # =========================================================

        if not self._demonstrates_repository_inspection(
            proposal_lower
        ):
            issues.append(
                "Proposal does not demonstrate that the specialist "
                "inspected the existing repository."
            )

        # =========================================================
        # 3. VALIDATE EXISTING REPOSITORY CLAIMS
        # =========================================================

        existing_claims = self._extract_existing_path_claims(
            proposal
        )

        for claimed_path in existing_claims:

            normalized = claimed_path.strip().rstrip(
                ".,:;)"
            )

            if not self._looks_like_repository_path(
                normalized
            ):
                continue

            path = self.repo_root / normalized

            if not path.exists():
                issues.append(
                    "Specialist claims existing repository path "
                    f"'{normalized}' exists, but it does not exist."
                )

        # =========================================================
        # 4. DETECT ACTUAL PROJECT STACK
        # =========================================================

        existing_stacks: list[str] = []

        if (self.repo_root / "agent_lab").exists():
            existing_stacks.append("Python")

        if (self.repo_root / "frontend").exists():
            existing_stacks.append("React/TypeScript")

        # =========================================================
        # 5. TECHNOLOGY COMPATIBILITY
        # =========================================================

        if existing_stacks:

            incompatible_patterns = [
                "dotnet test",
                "c# / typescript",
                "c# / csharp",
                ".cs",
                "asp.net",
                "django",
                "spring boot",
            ]

            for pattern in incompatible_patterns:

                if pattern in proposal_lower:

                    issues.append(
                        "Proposal introduces technology outside "
                        f"the detected project stack "
                        f"({', '.join(existing_stacks)}): "
                        f"'{pattern}'."
                    )

        # =========================================================
        # 6. SCOPE PROTECTION
        # =========================================================

        allowed_scope = {

            "architect": [
                "architecture",
                "system",
                "component",
                "interface",
                "dependency",
                "design",
            ],

            "blockchain": [
                "blockchain",
                "transaction",
                "provider",
                "evidence",
                "provenance",
            ],

            "graph": [
                "graph",
                "transaction",
                "evidence",
                "address",
                "wallet",
            ],

            "risk": [
                "risk",
                "rule",
                "score",
                "decision",
                "evidence",
            ],

            "platform": [
                "api",
                "backend",
                "platform",
                "service",
                "evidence",
                "risk",
            ],

            "copilot": [
                "copilot",
                "nemotron",
                "evidence",
                "grounding",
                "validation",
            ],

            "ui": [
                "ui",
                "frontend",
                "interface",
                "investigation",
                "graph",
                "risk",
                "copilot",
            ],
        }

        keywords = allowed_scope.get(
            task.agent,
            []
        )

        if keywords:

            relevant = any(
                keyword in proposal_lower
                for keyword in keywords
            )

            if not relevant:

                issues.append(
                    "Proposal does not appear to address "
                    f"the assigned {task.agent} scope."
                )

        # =========================================================
        # 7. VALIDATE PROPOSED AGENT HANDOFFS
        # =========================================================

        valid_agents = {
            "architect",
            "blockchain",
            "graph",
            "risk",
            "platform",
            "copilot",
            "ui",
        }

        # Only detect EXPLICIT delegation/handoff language.
        #
        # This prevents ordinary phrases such as:
        #
        #   "Provider Agent"
        #   "Evidence Creation Agent"
        #   "Data Normalizer Agent"
        #
        # from being incorrectly treated as workflow agents.
        #
        # A real workflow handoff must use language such as:
        #
        #   "handoff to graph agent"
        #   "delegate to risk agent"
        #   "assign to platform agent"
        #   "pass this task to copilot agent"

        handoff_patterns = [
            r"handoff\s+(?:to|with)\s+(?:the\s+)?([A-Za-z]+)\s+agent",
            r"delegate\s+(?:to|with)\s+(?:the\s+)?([A-Za-z]+)\s+agent",
            r"assign\s+(?:to|with)\s+(?:the\s+)?([A-Za-z]+)\s+agent",
            r"pass\s+(?:this\s+)?(?:task|work)\s+to\s+(?:the\s+)?([A-Za-z]+)\s+agent",
            r"handed\s+(?:off\s+)?to\s+(?:the\s+)?([A-Za-z]+)\s+agent",
            r"send\s+(?:the\s+)?(?:task|work)\s+to\s+(?:the\s+)?([A-Za-z]+)\s+agent",
        ]

        detected_handoffs: set[str] = set()

        for pattern in handoff_patterns:

            matches = re.findall(
                pattern,
                proposal,
                flags=re.IGNORECASE,
            )

            for match in matches:

                if isinstance(match, tuple):
                    match = match[0]

                agent_name = match.lower().strip()

                if agent_name == task.agent:
                    continue

                detected_handoffs.add(agent_name)

        for agent_name in sorted(detected_handoffs):

            if agent_name not in valid_agents:

                issues.append(
                    "Proposal explicitly hands work to an agent "
                    "that is not defined in the CryptoTrace workflow: "
                    f"'{agent_name}'."
                )

        # =========================================================
        # 8. FORBIDDEN AUTONOMOUS BEHAVIOR
        # =========================================================

        forbidden_patterns = [

            "make the final risk decision",

            "override the risk engine",

            "ignore human approval",

            "without human approval",

            "autonomously approve",

            "bypass human approval",

            "skip human approval",

            "implement without approval",

        ]

        for pattern in forbidden_patterns:

            if pattern in proposal_lower:

                issues.append(
                    "Proposal contains forbidden autonomous "
                    f"behavior: '{pattern}'."
                )

        # =========================================================
        # 9. IMPLEMENTATION PLANNING SANITY CHECKS
        # =========================================================

        implementation_terms = [
            "implementation",
            "artifact",
            "test",
            "input",
            "output",
            "interface",
        ]

        missing_terms = [
            term
            for term in implementation_terms
            if term not in proposal_lower
        ]

        if len(missing_terms) >= 4:

            issues.append(
                "Proposal does not contain enough concrete "
                "implementation planning."
            )

        # =========================================================
        # 10. FINAL RESULT
        # =========================================================

        return ValidationResult(
            valid=len(issues) == 0,
            issues=issues,
        )

    # =============================================================
    # EXISTING PATH CLAIM DETECTION
    # =============================================================

    def _extract_existing_path_claims(
        self,
        proposal: str,
    ) -> list[str]:

        """
        Extract only paths that the specialist explicitly
        describes as EXISTING.

        Examples:

            "src/foo.py currently contains..."
            "existing file src/foo.py"
            "src/foo.py already exists"

        Proposed files are intentionally ignored:

            "create src/foo.py"
            "new artifact src/foo.py"
            "src/foo.py must be added"
        """

        claims: list[str] = []

        patterns = [

            # "currently contains src/foo.py"
            r"(?:currently contains|currently has|"
            r"currently defines|currently includes|"
            r"already contains|already has|"
            r"existing file|existing files|"
            r"existing module|existing directory|"
            r"located at)\s+[`']?"
            r"((?:src|agent_lab|frontend|tests|config)"
            r"(?:[\\/][A-Za-z0-9_.-]+)+)",

            # "src/foo.py currently exists"
            r"((?:src|agent_lab|frontend|tests|config)"
            r"(?:[\\/][A-Za-z0-9_.-]+)+)"
            r"\s+(?:currently|already)\s+"
            r"(?:exists|contains|has|defines)",

            # "src/foo.py is an existing file"
            r"((?:src|agent_lab|frontend|tests|config)"
            r"(?:[\\/][A-Za-z0-9_.-]+)+)"
            r"\s+is\s+an?\s+existing\s+"
            r"(?:file|module|directory)",

        ]

        for pattern in patterns:

            matches = re.findall(
                pattern,
                proposal,
                flags=re.IGNORECASE,
            )

            for match in matches:

                if isinstance(match, tuple):
                    match = match[0]

                claims.append(match)

        return list(
            dict.fromkeys(claims)
        )

    # =============================================================
    # REPOSITORY PATH DETECTION
    # =============================================================

    @staticmethod
    def _looks_like_repository_path(
        value: str,
    ) -> bool:

        if value.startswith(
            (
                "http://",
                "https://",
            )
        ):
            return False

        return value.startswith(
            (
                "src/",
                "src\\",
                "agent_lab/",
                "agent_lab\\",
                "frontend/",
                "frontend\\",
                "tests/",
                "tests\\",
                "config/",
                "config\\",
            )
        )

    # =============================================================
    # REPOSITORY INSPECTION CHECK
    # =============================================================

    @staticmethod
    def _demonstrates_repository_inspection(
        proposal_lower: str,
    ) -> bool:

        inspection_terms = [

            "repository inspection",

            "existing repository",

            "current repository",

            "repository root",

            "existing files",

            "existing file",

            "current state",

            "current project",

            "inspected the repository",

            "inspect the repository",

            "repository contains",

            "repository structure",

            "the following items are present",

            "the following files",

            "following directories",

            "path (relative to repo root)",

        ]

        return any(
            term in proposal_lower
            for term in inspection_terms
        )