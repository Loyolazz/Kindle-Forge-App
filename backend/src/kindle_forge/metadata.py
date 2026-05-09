from __future__ import annotations

import json
import re
import html as html_lib
import urllib.parse
import urllib.request
from dataclasses import dataclass, asdict
from typing import Any, Optional


USER_AGENT = "KindleForge/0.2 (local metadata lookup)"


@dataclass(frozen=True)
class MetadataCandidate:
    source: str
    title: str
    author: str = ""
    series: str = ""
    volume: str = ""
    publisher: str = ""
    language: str = ""
    description: str = ""
    year: str = ""
    cover_url: str = ""
    external_url: str = ""
    confidence: int = 0
    warning: str = ""

    def payload(self) -> dict[str, str]:
        return {key: value for key, value in asdict(self).items() if value}


def search_metadata(query: str, limit: int = 8, kind: str = "auto", language: str = "") -> list[dict[str, str]]:
    cleaned = clean_query(query)
    if not cleaned:
        return []

    candidates: list[MetadataCandidate] = []
    searchers = [_search_mangadex, _search_google_books, _search_open_library]
    if kind == "manga":
        searchers = [_search_mangadex, _search_google_books, _search_open_library]
    elif kind in {"comic", "book", "lightnovel"}:
        searchers = [_search_google_books, _search_open_library, _search_mangadex]

    for searcher in searchers:
        try:
            candidates.extend(searcher(cleaned, limit=limit))
        except Exception:
            continue

    scored = sorted((_with_score(candidate, cleaned) for candidate in candidates), key=lambda item: item.confidence, reverse=True)
    seen: set[tuple[str, str]] = set()
    unique: list[dict[str, str]] = []
    for candidate in scored:
        key = (candidate.source, candidate.title.casefold())
        if key in seen:
            continue
        seen.add(key)
        unique.append(candidate.payload())
        if len(unique) >= limit:
            break
    return unique


def clean_query(value: str) -> str:
    value = html_lib.unescape(value)
    text = re.sub(r"\.[a-z0-9]{2,5}$", "", value.strip(), flags=re.I)
    text = re.sub(r"[_\-.]+", " ", text)
    text = re.sub(r"\b(chapter|capitulo|capítulo|cap|ch|vol|volume|v)\s*\d+([.,]\d+)?\b", " ", text, flags=re.I)
    text = re.sub(r"\b\d{3,4}\b", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text or value.strip()


def download_cover(url: str, timeout: int = 15) -> bytes:
    if not url.startswith(("https://", "http://")):
        raise ValueError("URL de capa invalida.")
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        content_type = response.headers.get("Content-Type", "")
        if "image" not in content_type:
            raise ValueError("A URL nao retornou uma imagem.")
        return response.read(10 * 1024 * 1024)


def _search_mangadex(query: str, limit: int) -> list[MetadataCandidate]:
    params = urllib.parse.urlencode(
        [
            ("title", query),
            ("limit", str(min(limit, 5))),
            ("includes[]", "author"),
            ("includes[]", "artist"),
            ("includes[]", "cover_art"),
            ("order[relevance]", "desc"),
        ]
    )
    data = _get_json(f"https://api.mangadex.org/manga?{params}")
    results: list[MetadataCandidate] = []
    for item in data.get("data", []):
        manga_id = item.get("id", "")
        attributes = item.get("attributes", {})
        title = _clean_text(_localized(attributes.get("title", {})) or query)
        description = _clean_text(_localized(attributes.get("description", {})))
        year = str(attributes.get("year") or "")
        authors: list[str] = []
        cover_url = ""
        for relationship in item.get("relationships", []):
            rel_type = relationship.get("type")
            rel_attr = relationship.get("attributes", {})
            if rel_type in {"author", "artist"} and rel_attr.get("name"):
                authors.append(rel_attr["name"])
            if rel_type == "cover_art" and manga_id and rel_attr.get("fileName"):
                cover_url = f"https://uploads.mangadex.org/covers/{manga_id}/{rel_attr['fileName']}.512.jpg"
        results.append(
            MetadataCandidate(
                source="MangaDex",
                title=title,
                author=_clean_text(", ".join(dict.fromkeys(authors))),
                series=title,
                description=description,
                year=year,
                cover_url=cover_url,
                external_url=f"https://mangadex.org/title/{manga_id}" if manga_id else "",
            )
        )
    return results


def _search_google_books(query: str, limit: int) -> list[MetadataCandidate]:
    params = urllib.parse.urlencode({"q": f"intitle:{query}", "maxResults": min(limit, 5), "printType": "books"})
    data = _get_json(f"https://www.googleapis.com/books/v1/volumes?{params}")
    results: list[MetadataCandidate] = []
    for item in data.get("items", []):
        info = item.get("volumeInfo", {})
        image_links = info.get("imageLinks", {})
        cover = image_links.get("large") or image_links.get("thumbnail") or ""
        if cover.startswith("http://"):
            cover = "https://" + cover[len("http://") :]
        title = _clean_text(info.get("title") or query)
        subtitle = info.get("subtitle")
        if subtitle and subtitle.casefold() not in title.casefold():
            title = f"{title}: {subtitle}"
        results.append(
            MetadataCandidate(
                source="Google Books",
                title=title,
                author=_clean_text(", ".join(info.get("authors", []))),
                series=_clean_text(info.get("title", "")),
                publisher=_clean_text(info.get("publisher", "")),
                language=info.get("language", ""),
                description=_clean_text(info.get("description", "")),
                year=str(info.get("publishedDate", ""))[:4],
                cover_url=cover,
                external_url=info.get("infoLink", ""),
            )
        )
    return results


def _search_open_library(query: str, limit: int) -> list[MetadataCandidate]:
    params = urllib.parse.urlencode(
        {
            "title": query,
            "limit": min(limit, 5),
            "fields": "key,title,author_name,first_publish_year,cover_i,publisher,language",
        }
    )
    data = _get_json(f"https://openlibrary.org/search.json?{params}")
    results: list[MetadataCandidate] = []
    for item in data.get("docs", []):
        cover_id = item.get("cover_i")
        publishers = item.get("publisher") or []
        languages = item.get("language") or []
        key = item.get("key", "")
        results.append(
            MetadataCandidate(
                source="Open Library",
                title=_clean_text(item.get("title") or query),
                author=_clean_text(", ".join(item.get("author_name") or [])),
                series=_clean_text(item.get("title") or query),
                publisher=_clean_text(publishers[0] if publishers else ""),
                language=languages[0] if languages else "",
                year=str(item.get("first_publish_year") or ""),
                cover_url=f"https://covers.openlibrary.org/b/id/{cover_id}-L.jpg" if cover_id else "",
                external_url=f"https://openlibrary.org{key}" if key else "",
            )
        )
    return results


def _get_json(url: str, timeout: int = 12) -> dict[str, Any]:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def _localized(values: Any) -> str:
    if not isinstance(values, dict):
        return ""
    for key in ("pt-br", "pt", "en", "ja-ro", "ja"):
        value = values.get(key)
        if value:
            return value
    for value in values.values():
        if value:
            return str(value)
    return ""


def _clean_text(value: str) -> str:
    text = html_lib.unescape(str(value or ""))
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _with_score(candidate: MetadataCandidate, query: str) -> MetadataCandidate:
    query_norm = _norm(query)
    title_norm = _norm(candidate.title)
    query_tokens = set(query_norm.split())
    title_tokens = set(title_norm.split())
    if not query_tokens or not title_tokens:
        score = 0
    elif title_norm == query_norm:
        score = 100
    elif title_norm.startswith(query_norm) or query_norm in title_norm:
        score = 88
    else:
        overlap = len(query_tokens & title_tokens) / max(1, len(query_tokens))
        score = int(35 + overlap * 45)
        if overlap < 0.5:
            score = min(score, 45)
    if candidate.source == "MangaDex" and score >= 60:
        score += 4
    score = max(0, min(100, score))
    warning = ""
    if score < 65:
        warning = f"Baixa confiança: pode nao corresponder a '{query}'."
    return MetadataCandidate(
        source=candidate.source,
        title=candidate.title,
        author=candidate.author,
        series=candidate.series,
        volume=candidate.volume,
        publisher=candidate.publisher,
        language=candidate.language,
        description=candidate.description,
        year=candidate.year,
        cover_url=candidate.cover_url,
        external_url=candidate.external_url,
        confidence=score,
        warning=warning,
    )


def _norm(value: str) -> str:
    text = html_lib.unescape(value).casefold()
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()
