from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app.agent import LabAgent
from app.tracing import LANGFUSE_SDK_AVAILABLE, get_langfuse_client, tracing_enabled


PROMPT_NAME = "day13-chat"
PROMPT_V1 = """Feature={{feature}}
Docs={{docs}}
Question={{message}}

Answer concisely using the retrieved documents when relevant."""
PROMPT_V2 = """Feature={{feature}}
Docs={{docs}}
Question={{message}}

Answer in at most three concise bullet points and cite the retrieved context when relevant."""


def get_label(client, name: str, label: str):
    return client.get_prompt(
        name,
        label=label,
        type="text",
        cache_ttl_seconds=0,
        fetch_timeout_seconds=10,
        max_retries=0,
    )


def get_label_or_none(client, name: str, label: str):
    try:
        prompt = get_label(client, name, label)
    except Exception:
        return None
    return None if getattr(prompt, "is_fallback", False) else prompt


def print_status(client, name: str) -> None:
    for label in ("baseline", "candidate", "production"):
        prompt = get_label_or_none(client, name, label)
        if prompt is None:
            print(f"{label}: not found")
        else:
            print(f"{label}: version={prompt.version}, labels={','.join(prompt.labels)}")


def setup_versions(client, name: str) -> None:
    baseline = get_label_or_none(client, name, "baseline")
    if baseline is None:
        baseline = client.create_prompt(
            name=name,
            prompt=PROMPT_V1,
            labels=["baseline", "production"],
            tags=["day13", "checkpoint2"],
            type="text",
            commit_message="Checkpoint 2 baseline prompt",
        )
        print(f"Created baseline version {baseline.version}")
    else:
        print(f"Baseline already exists at version {baseline.version}")

    candidate = get_label_or_none(client, name, "candidate")
    if candidate is None:
        candidate = client.create_prompt(
            name=name,
            prompt=PROMPT_V2,
            labels=["candidate"],
            tags=["day13", "checkpoint2"],
            type="text",
            commit_message="Checkpoint 2 candidate prompt",
        )
        print(f"Created candidate version {candidate.version}")
    else:
        print(f"Candidate already exists at version {candidate.version}")


def move_production(client, name: str, target: str) -> None:
    baseline = get_label(client, name, "baseline")
    candidate = get_label(client, name, "candidate")
    if target == "candidate":
        client.update_prompt(name=name, version=int(baseline.version), new_labels=["baseline"])
        client.update_prompt(name=name, version=int(candidate.version), new_labels=["candidate", "production"])
    else:
        client.update_prompt(name=name, version=int(candidate.version), new_labels=["candidate"])
        client.update_prompt(name=name, version=int(baseline.version), new_labels=["baseline", "production"])
    print(f"production now points to {target}")


def create_evidence_traces(client, name: str) -> None:
    agent = LabAgent()
    for label in ("baseline", "candidate"):
        os.environ["LANGFUSE_PROMPT_NAME"] = name
        os.environ["LANGFUSE_PROMPT_LABEL"] = label
        with client.start_as_current_span(
            name="checkpoint2-prompt-evidence",
            metadata={"evidence": "checkpoint2", "requested_prompt_label": label},
        ):
            result = agent.run(
                user_id="checkpoint2-user",
                feature="qa",
                session_id="checkpoint2-prompt-comparison",
                message="How do metrics, traces, and logs work together?",
            )
            trace_id = client.get_current_trace_id()
            trace_url = client.get_trace_url(trace_id=trace_id)
        client.flush()
        print(
            f"{label}: trace_id={trace_id} latency_ms={result.latency_ms} "
            f"url={trace_url or 'open Langfuse Tracing'}"
        )


def main() -> int:
    load_dotenv(REPO_ROOT / ".env")
    parser = argparse.ArgumentParser(description="Manage Checkpoint 2 prompt versions in Langfuse")
    parser.add_argument("action", choices=("status", "setup", "trace", "promote", "rollback"))
    parser.add_argument("--name", default=os.getenv("LANGFUSE_PROMPT_NAME", PROMPT_NAME))
    args = parser.parse_args()

    if not LANGFUSE_SDK_AVAILABLE:
        parser.error(
            "langfuse package is not installed in the active Python environment. "
            "Please activate your virtual environment (e.g., .\\.venv\\Scripts\\Activate.ps1) "
            "or run: pip install -r requirements.txt"
        )
    if not tracing_enabled():
        parser.error("LANGFUSE_PUBLIC_KEY and LANGFUSE_SECRET_KEY must be configured in .env")

    client = get_langfuse_client()
    if args.action == "status":
        print_status(client, args.name)
    elif args.action == "setup":
        setup_versions(client, args.name)
        print_status(client, args.name)
    elif args.action == "trace":
        create_evidence_traces(client, args.name)
    elif args.action == "promote":
        move_production(client, args.name, "candidate")
        print_status(client, args.name)
    elif args.action == "rollback":
        move_production(client, args.name, "baseline")
        print_status(client, args.name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
