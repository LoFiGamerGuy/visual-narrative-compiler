"""Fail closed if Git tracks generated, sensitive, heavyweight, or out-of-scope files."""
from __future__ import annotations

import re
import subprocess
import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
ALLOWED_TOP = {
    ".env.example", ".gitignore", "AGENT_FIRST_PROMPT.md", "BUNDLE_PROVENANCE.json",
    "GAP_ANALYSIS.md", "GOAL.md", "MANIFEST.sha256", "README_CODEX_BOOTSTRAP.md",
    "VALIDATION_AT_PACKAGING.txt", "config", "docs", "manifests", "production",
    "public-controls", "research", "scripts", "src",
}
PUBLIC_CONTROLS = {
    "public-controls/g07a-no-change-r1.png": "867a05c2f3e35f196cd28a9d1dc1954f2ba862f62d33ae34df4f3161a3200436",
    "public-controls/g07a-role-id-r1.png": "0a7237f655492f4aea7618036b7bac1a5068882f113ae395188ab50abb5a2699",
}
PROHIBITED_SUFFIXES = {".safetensors", ".ckpt", ".pt", ".pth", ".onnx", ".gguf", ".key", ".pem"}
PROHIBITED_TOP = {"experiments", "private", "private_refs", "datasets", "loras", "ComfyUI", "models"}
ASSIGNMENT = re.compile(r"^(?:OPENAI|GEMINI|GOOGLE|XAI|BFL)_[A-Z0-9_]*(?:API_)?KEY=(.+)$")
TOKEN = re.compile(r"\b(?:sk-[A-Za-z0-9_-]{16,}|xai-[A-Za-z0-9_-]{16,})\b")


def main() -> int:
    completed = subprocess.run(["git", "ls-files", "-z"], cwd=ROOT, capture_output=True)
    if completed.returncode:
        print("failure: git ls-files failed")
        return 1
    paths = [Path(value.decode("utf-8")) for value in completed.stdout.split(b"\0") if value]
    failures = []
    for relative in paths:
        relative_text = relative.as_posix()
        if relative.parts[0] not in ALLOWED_TOP:
            failures.append(f"out-of-scope tracked path: {relative.as_posix()}")
        if relative.parts[0] in PROHIBITED_TOP:
            failures.append(f"prohibited tracked path component: {relative.as_posix()}")
        if relative.suffix.casefold() in PROHIBITED_SUFFIXES:
            failures.append(f"prohibited tracked extension: {relative.as_posix()}")
        path = ROOT / relative
        if path.is_file() and path.stat().st_size > 10 * 1024 * 1024:
            failures.append(f"tracked file exceeds 10 MiB source limit: {relative.as_posix()}")
        if path.is_file() and path.stat().st_size <= 2 * 1024 * 1024:
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            for line in text.splitlines():
                assignment = ASSIGNMENT.match(line.strip())
                if assignment and assignment.group(1).strip():
                    failures.append(f"nonblank provider credential assignment: {relative.as_posix()}")
                if TOKEN.search(line):
                    failures.append(f"provider-token-like text: {relative.as_posix()}")
        if relative.parts[0] == "public-controls":
            expected = PUBLIC_CONTROLS.get(relative_text)
            actual = hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None
            if expected is None or actual != expected:
                failures.append(f"unexpected or modified public control: {relative_text}")
    if {item.as_posix() for item in paths if item.parts[0] == "public-controls"} != set(PUBLIC_CONTROLS):
        failures.append("tracked public-control set differs from the two approved hash-pinned controls")
    remote = subprocess.run(["git", "remote", "get-url", "origin"], cwd=ROOT, capture_output=True, text=True)
    normalized_remote = remote.stdout.strip().removesuffix(".git")
    if remote.returncode or normalized_remote != "https://github.com/LoFiGamerGuy/visual-narrative-compiler":
        failures.append("origin remote is missing or unexpected")
    for failure in failures:
        print(f"failure: {failure}")
    if failures:
        return 1
    print(f"0 failures, 0 warnings ({len(paths)} tracked safe-source paths; origin verified)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
