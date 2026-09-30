import asyncio
import hashlib
import re
from pathlib import Path

from pypdf import PdfReader
from qdrant_client import AsyncQdrantClient

from .config import settings

_client: AsyncQdrantClient | None = None

PARAGRAPH = re.compile(r"\n\s*\n")
AGENT = re.compile(r"^[A-Z]+$")


def client() -> AsyncQdrantClient:
    global _client
    if _client is None:
        _client = AsyncQdrantClient(url=settings.qdrant_url, timeout=settings.qdrant_timeout)
        _client.set_model(settings.embed_model)
    return _client


def chunk(text: str, size: int | None = None, overlap: int | None = None) -> list[str]:
    size = size or settings.chunk_size
    overlap = overlap or settings.chunk_overlap
    paragraphs = [p.strip() for p in PARAGRAPH.split(text) if p.strip()]
    chunks: list[str] = []
    buffer = ""
    for para in paragraphs:
        if len(buffer) + len(para) + 2 <= size:
            buffer = f"{buffer}\n\n{para}" if buffer else para
            continue
        if buffer:
            chunks.append(buffer)
        while len(para) > size:
            chunks.append(para[:size])
            para = para[size - overlap :]
        buffer = para
    if buffer:
        chunks.append(buffer)
    return [c for c in chunks if len(c) > 40]


def read_document(path: Path) -> str:
    if path.suffix.lower() == ".pdf":
        return "\n\n".join(page.extract_text() or "" for page in PdfReader(str(path)).pages)
    return path.read_text(encoding="utf-8", errors="replace")


def category_of(name: str) -> str | None:
    stem = Path(name).stem.upper()
    return stem if AGENT.match(stem) else None


async def index_texts(items: list[tuple[str, str]]) -> int:
    documents, metadata, ids = [], [], []
    for source, text in items:
        for position, piece in enumerate(chunk(text)):
            documents.append(piece)
            metadata.append(
                {"source": source, "position": position, "category": category_of(source)}
            )
            digest = hashlib.sha1(f"{source}:{position}:{piece[:64]}".encode()).hexdigest()
            ids.append(int(digest[:15], 16))
    if not documents:
        return 0
    for attempt in range(2):
        try:
            await client().add(
                collection_name=settings.kb_collection,
                documents=documents,
                metadata=metadata,
                ids=ids,
                batch_size=64,
            )
            break
        except Exception:
            if attempt:
                raise
            await asyncio.sleep(1)
    return len(documents)


async def index_directory(directory: str) -> tuple[int, int]:
    root = Path(directory)
    if not root.exists():
        return 0, 0
    files = [p for p in root.rglob("*") if p.suffix.lower() in {".md", ".txt", ".pdf"}]
    items = [(p.name, read_document(p)) for p in files]
    return len(files), await index_texts(items)


async def search(query: str, top_k: int | None = None) -> list[dict]:
    try:
        hits = await client().query(
            collection_name=settings.kb_collection,
            query_text=query,
            limit=top_k or settings.top_k,
        )
    except Exception:
        return []
    return [
        {
            "source": h.metadata.get("source", "unknown"),
            "score": round(h.score, 4),
            "text": h.document,
            "category": h.metadata.get("category"),
        }
        for h in hits
        if h.score >= settings.min_score
    ]


async def collection_size() -> int:
    try:
        return (await client().count(settings.kb_collection)).count
    except Exception:
        return 0
