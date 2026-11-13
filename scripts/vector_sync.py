#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml>=6", "httpx>=0.27", "qdrant-client>=1.9"]
# ///
"""Mirror the family-system workspace into a Qdrant collection.

The git repository is the source of truth. This index is disposable: deleting the
collection and re-running loses nothing.

  plan      chunk the workspace and report what would change (no embedding calls)
  sync      embed new or changed chunks, upsert them, delete chunks that no longer exist
  query     semantic search: vector_sync.py query "how does my brother react to ..."
  status    collection point count and configuration
  drop      delete the collection

Configuration comes from environment variables (the skill loads them from the user's
profile.env; see docs/vector-store.md):

  FAMSYS_QDRANT_URL         Qdrant server URL, e.g. http://localhost:6333
  FAMSYS_QDRANT_PATH        or a local folder for Qdrant's embedded mode (no server)
  FAMSYS_QDRANT_API_KEY_ENV name of the env var holding the Qdrant API key, if any
  FAMSYS_COLLECTION         default: family-system
  FAMSYS_EMBED_BASE_URL     OpenAI-compatible base URL, default https://api.openai.com/v1
                            (Ollama: http://localhost:11434/v1)
  FAMSYS_EMBED_MODEL        default text-embedding-3-small
  FAMSYS_EMBED_API_KEY_ENV  name of the env var holding the embedding key, default OPENAI_API_KEY

Output: JSON on stdout.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import uuid
from pathlib import Path

import httpx
import yaml
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointIdsList, PointStruct, VectorParams

MARKER = ".family-systems-context"
NS = uuid.UUID("6f1c6c1e-6b0e-4f5e-9d55-3f3a8f6a1a10")
MAX_CHARS = 1800
INCLUDE = ["family-overview.md", "vocabulary.md", "actors/*.md", "sources/*.md"]


def env(key: str, default: str = "") -> str:
    return os.environ.get(key, default).strip()


def find_root(start: Path) -> Path:
    for d in [start, *start.parents]:
        if (d / MARKER).is_file():
            return d
    sys.exit(json.dumps({"error": f"no {MARKER} marker found from {start} upward; pass --root"}))


def split_frontmatter(text: str) -> tuple[dict, str]:
    m = re.match(r"^---\n(.*?)\n---\n?(.*)$", text, re.S)
    if not m:
        return {}, text
    try:
        return (yaml.safe_load(m.group(1)) or {}), m.group(2)
    except yaml.YAMLError:
        return {}, m.group(2)


def chunk_file(root: Path, path: Path) -> list[dict]:
    rel = path.relative_to(root).as_posix()
    fm, body = split_frontmatter(path.read_text(encoding="utf-8"))
    body = re.sub(r"<!--.*?-->", "", body, flags=re.S)          # template guidance
    body = re.sub(r"```mermaid.*?```", "", body, flags=re.S)    # generated diagram
    kind = "overview" if rel == "family-overview.md" else rel.split("/")[0].rstrip("s")
    title = str(fm.get("name") or path.stem)
    # Split on level-2 headings; keep the heading path in each chunk's text.
    sections, head, buf = [], "", []
    for line in body.splitlines():
        if line.startswith("## "):
            if "".join(buf).strip():
                sections.append((head, "\n".join(buf).strip()))
            head, buf = line[3:].strip(), []
        else:
            buf.append(line)
    if "".join(buf).strip():
        sections.append((head, "\n".join(buf).strip()))
    chunks = []
    for head, text in sections:
        if re.fullmatch(r"(Not yet captured\.?|[-|:\s]*|- YYYY-MM-DD: file created\.)", text):
            continue
        parts, cur = [], ""
        for para in re.split(r"\n\s*\n", text):
            if cur and len(cur) + len(para) > MAX_CHARS:
                parts.append(cur)
                cur = ""
            cur = f"{cur}\n\n{para}" if cur else para
        if cur:
            parts.append(cur)
        for i, part in enumerate(parts):
            prefix = f"{title} ({rel})" + (f" > {head}" if head else "")
            content = f"{prefix}\n\n{part}"
            key = f"{rel}#{head}#{i}"
            chunks.append({
                "id": str(uuid.uuid5(NS, key)),
                "text": content,
                "hash": hashlib.sha256(content.encode()).hexdigest(),
                "path": rel,
                "section": head,
                "kind": kind,
                "actor": path.stem if kind == "actor" else None,
                "relation": fm.get("relation"),
                "date": str(fm.get("date") or fm.get("updated") or ""),
            })
    return chunks


def collect(root: Path) -> list[dict]:
    out = []
    for pattern in INCLUDE:
        for p in sorted(root.glob(pattern)):
            if p.name.startswith("_") or p.name == "README.md":
                continue
            out.extend(chunk_file(root, p))
    return out


def client() -> tuple[QdrantClient, str]:
    url, path = env("FAMSYS_QDRANT_URL"), env("FAMSYS_QDRANT_PATH")
    key_env = env("FAMSYS_QDRANT_API_KEY_ENV")
    api_key = os.environ.get(key_env) if key_env else None
    if url:
        return QdrantClient(url=url, api_key=api_key), f"qdrant server {url}"
    if path:
        p = Path(os.path.expanduser(path))
        p.mkdir(parents=True, exist_ok=True)
        return QdrantClient(path=str(p)), f"qdrant local folder {p}"
    sys.exit(json.dumps({"error": "set FAMSYS_QDRANT_URL or FAMSYS_QDRANT_PATH (see docs/vector-store.md)"}))


def embed(texts: list[str]) -> list[list[float]]:
    base = env("FAMSYS_EMBED_BASE_URL", "https://api.openai.com/v1").rstrip("/")
    model = env("FAMSYS_EMBED_MODEL", "text-embedding-3-small")
    key_env = env("FAMSYS_EMBED_API_KEY_ENV", "OPENAI_API_KEY")
    key = os.environ.get(key_env, "")
    headers = {"Authorization": f"Bearer {key}"} if key else {}
    vectors: list[list[float]] = []
    with httpx.Client(timeout=120) as h:
        for i in range(0, len(texts), 64):
            r = h.post(f"{base}/embeddings", headers=headers, json={"model": model, "input": texts[i:i + 64]})
            if r.status_code >= 400:
                sys.exit(json.dumps({"error": f"embedding request failed: HTTP {r.status_code}", "body": r.text[:500]}))
            data = sorted(r.json()["data"], key=lambda d: d["index"])
            vectors.extend(d["embedding"] for d in data)
    return vectors


def existing(qc: QdrantClient, coll: str) -> dict[str, str]:
    if not qc.collection_exists(coll):
        return {}
    seen, offset = {}, None
    while True:
        points, offset = qc.scroll(coll, limit=256, offset=offset, with_payload=["hash"], with_vectors=False)
        for p in points:
            seen[str(p.id)] = (p.payload or {}).get("hash", "")
        if offset is None:
            return seen


def git_head(root: Path) -> str | None:
    try:
        return subprocess.run(["git", "-C", str(root), "rev-parse", "--short", "HEAD"],
                              capture_output=True, text=True, check=True).stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["plan", "sync", "query", "status", "drop"])
    ap.add_argument("text", nargs="?")
    ap.add_argument("--root", type=Path)
    ap.add_argument("--top", type=int, default=6)
    args = ap.parse_args()
    coll = env("FAMSYS_COLLECTION", "family-system")

    if args.cmd in ("plan", "sync"):
        root = (args.root or find_root(Path.cwd())).resolve()
        chunks = collect(root)
        qc, where = client()
        have = existing(qc, coll)
        want = {c["id"]: c for c in chunks}
        changed = [c for c in chunks if have.get(c["id"]) != c["hash"]]
        stale = [i for i in have if i not in want]
        result = {"store": where, "collection": coll, "chunks": len(chunks),
                  "to_embed": len(changed), "to_delete": len(stale),
                  "files": sorted({c["path"] for c in changed})}
        if args.cmd == "sync":
            commit = git_head(root)
            if changed:
                vectors = embed([c["text"] for c in changed])
                if not qc.collection_exists(coll):
                    qc.create_collection(coll, vectors_config=VectorParams(size=len(vectors[0]), distance=Distance.COSINE))
                qc.upsert(coll, points=[
                    PointStruct(id=c["id"], vector=v, payload={**{k: c[k] for k in c if k != "id"}, "commit": commit})
                    for c, v in zip(changed, vectors)
                ])
            if stale:
                qc.delete(coll, points_selector=PointIdsList(points=stale))
            result.update({"synced": True, "commit": commit})
        print(json.dumps(result))
        return

    qc, where = client()
    if args.cmd == "status":
        if not qc.collection_exists(coll):
            print(json.dumps({"store": where, "collection": coll, "exists": False}))
            return
        print(json.dumps({"store": where, "collection": coll, "exists": True,
                          "points": qc.count(coll, exact=True).count}))
    elif args.cmd == "drop":
        if qc.collection_exists(coll):
            qc.delete_collection(coll)
        print(json.dumps({"store": where, "collection": coll, "dropped": True}))
    elif args.cmd == "query":
        if not args.text:
            sys.exit(json.dumps({"error": "query needs text"}))
        vec = embed([args.text])[0]
        hits = qc.query_points(coll, query=vec, limit=args.top, with_payload=True).points
        print(json.dumps({"query": args.text, "hits": [
            {"score": round(h.score, 4), "path": h.payload.get("path"), "section": h.payload.get("section"),
             "text": h.payload.get("text")} for h in hits]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
