from __future__ import annotations

import base64
import cgi
import io
import json
import mimetypes
import platform
import shutil
import subprocess
import tempfile
import traceback
from datetime import datetime, timezone
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, unquote, urlparse

from .converter import ConvertRequest, convert, detect_mode
from .covers import BookMetadata, make_generated_cover, prepare_cover_image
from .images import IMAGE_EXTENSIONS, ImageOptions, is_image_path, process_image
from .metadata import clean_query, download_cover, search_metadata
from .profiles import get_profile
from .sources import ARCHIVE_EXTENSIONS, SourceError, iter_source_images
from .util import natural_key, slugify
from .writers import save_page_image


PROJECT_ROOT = Path(__file__).resolve().parents[3]
FRONTEND_DIR = PROJECT_ROOT / "frontend"
OUTPUT_ROOT = PROJECT_ROOT / "backend" / "dist" / "web"
HISTORY_PATH = OUTPUT_ROOT / "history.json"
DOCUMENT_EXTENSIONS = ARCHIVE_EXTENSIONS | {".pdf"}
SUPPORTED_EXTENSIONS = DOCUMENT_EXTENSIONS | IMAGE_EXTENSIONS


class KindleForgeHandler(SimpleHTTPRequestHandler):
    server_version = "KindleForge/0.3"

    def log_message(self, format: str, *args: object) -> None:
        return

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/api/health":
            self._send_json(
                {
                    "ok": True,
                    "version": self.server_version,
                    "endpoints": ["/api/history/clear", "/api/history/delete-files"],
                }
            )
            return
        if parsed.path == "/api/history":
            self._send_json({"items": _read_history()})
            return
        if parsed.path == "/api/open-output":
            self._handle_open_output(parsed.query)
            return
        if parsed.path == "/api/metadata":
            self._handle_metadata(parsed.query)
            return
        if parsed.path.startswith("/download/"):
            self._serve_download(parsed.path)
            return
        self._serve_frontend(parsed.path)

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/api/convert":
            self._handle_convert()
            return
        if parsed.path == "/api/preview":
            self._handle_preview()
            return
        if parsed.path == "/api/history/clear":
            self._handle_clear_history()
            return
        if parsed.path == "/api/history/delete-files":
            self._handle_delete_history_files()
            return
        self._send_json({"error": "Endpoint nao encontrado."}, HTTPStatus.NOT_FOUND)

    def _handle_convert(self) -> None:
        try:
            form = _read_form(self)
            file_items = _file_items(form, "file")
            if not file_items:
                self._send_json({"error": "Escolha um arquivo ou pasta para converter."}, HTTPStatus.BAD_REQUEST)
                return

            profile = get_profile(_field(form, "profile", "kindle11"))
            output_format = _field(form, "format", "epub")
            requested_mode = _field(form, "mode", "manga")
            author = _field(form, "author", "Unknown").strip() or "Unknown"
            series = _field(form, "series", "").strip()
            volume = _field(form, "volume", "").strip()
            language = _field(form, "language", "pt-BR").strip() or "pt-BR"
            publisher = _field(form, "publisher", "").strip()
            description = _field(form, "description", "").strip()
            cover_mode = _field(form, "coverMode", "first")
            cover_url = _field(form, "coverUrl", "").strip()
            group_mode = _field(form, "groupMode", "batch")
            split_size_mb = _int_field(form, "splitSizeMb", 200)
            quality = _int_field(form, "quality", 85)
            gamma = _float_field(form, "gamma", 1.0)
            pdf_zoom = _float_field(form, "pdfZoom", 1.0)
            crop = _bool_field(form, "crop", True)
            split_spreads = _bool_field(form, "splitSpreads", True)
            protect_first_page = _bool_field(form, "protectFirstPage", True)
            color = _bool_field(form, "color", False)
            dither = _bool_field(form, "dither", False)
            custom_cover = _file_items(form, "coverFile")

            input_groups = _input_groups(file_items, group_mode)
            results: list[dict[str, Any]] = []
            for group_index, group in enumerate(input_groups, start=1):
                title = _title_for_group(form, group, group_index, len(input_groups))
                job_id = _unique_job_id(slugify(title, "conversion"))
                job_dir = OUTPUT_ROOT / job_id
                source_dir = job_dir / "source"
                source_dir.mkdir(parents=True, exist_ok=True)

                input_path = _save_group(group, source_dir)
                input_summary = _input_payload(group)
                cover_path = None
                convert_cover_mode = cover_mode
                if custom_cover and cover_mode == "custom":
                    cover_path = _save_cover(custom_cover[0], job_dir)
                elif cover_url and cover_mode == "online":
                    cover_path = _save_online_cover(cover_url, job_dir)
                    convert_cover_mode = "custom"
                result = convert(
                    ConvertRequest(
                        input_path=input_path,
                        output_dir=job_dir,
                        profile=profile,
                        title=title,
                        author=author,
                        series=series,
                        volume=volume,
                        language=language,
                        publisher=publisher,
                        description=description,
                        mode=requested_mode,
                        output_format=output_format,
                        cover_mode=convert_cover_mode,
                        cover_path=cover_path,
                        split_size_mb=split_size_mb,
                        quality=quality,
                        crop=crop,
                        split_spreads=split_spreads,
                        protect_first_page=protect_first_page,
                        color=color,
                        dither=dither,
                        gamma=gamma,
                        pdf_zoom=pdf_zoom,
                    )
                )
                files = [_file_payload(job_id, path) for path in result.outputs]
                item = {
                    "jobId": job_id,
                    "title": result.title,
                    "mode": result.mode,
                    "pages": result.page_count,
                    "split": result.split,
                    "files": files,
                    "input": input_summary,
                    "outputSize": sum(file["size"] for file in files),
                    "outputUrl": f"/api/open-output?job={job_id}",
                    "createdAt": _now(),
                    "status": "done",
                }
                results.append(item)
                _append_history(item)

            payload: dict[str, Any] = {"items": results}
            if len(results) == 1:
                payload.update(results[0])
            self._send_json(payload)
        except (SourceError, ValueError, RuntimeError) as exc:
            self._send_json({"error": str(exc)}, HTTPStatus.BAD_REQUEST)
        except Exception as exc:  # pragma: no cover - last-resort API guard
            traceback.print_exc()
            self._send_json({"error": f"Falha inesperada: {exc}"}, HTTPStatus.INTERNAL_SERVER_ERROR)

    def _handle_preview(self) -> None:
        try:
            form = _read_form(self)
            file_items = _file_items(form, "file")
            if not file_items:
                self._send_json({"error": "Escolha um arquivo para gerar previa."}, HTTPStatus.BAD_REQUEST)
                return
            profile = get_profile(_field(form, "profile", "kindle11"))
            mode = _field(form, "mode", "manga")
            title = _field(form, "title", "").strip() or Path(file_items[0].filename).stem
            metadata = BookMetadata(
                title=title,
                author=_field(form, "author", "Unknown").strip() or "Unknown",
                series=_field(form, "series", "").strip(),
                volume=_field(form, "volume", "").strip(),
            )
            options = ImageOptions(
                profile=profile,
                mode=mode if mode != "auto" else "manga",
                crop=_bool_field(form, "crop", True),
                split_spreads=_bool_field(form, "splitSpreads", True),
                color=_bool_field(form, "color", False),
                dither=_bool_field(form, "dither", False),
                gamma=_float_field(form, "gamma", 1.0),
            )
            cover_mode = _field(form, "coverMode", "first")
            cover_url = _field(form, "coverUrl", "").strip()
            custom_cover = _file_items(form, "coverFile")
            previews: list[dict[str, Any]] = []
            with tempfile.TemporaryDirectory(prefix="kindle-forge-preview-") as temp:
                temp_path = Path(temp)
                input_path = _save_group([file_items[0]], temp_path / "source")
                if mode == "auto":
                    options = ImageOptions(
                        profile=options.profile,
                        mode=detect_mode(input_path, profile),
                        crop=options.crop,
                        split_spreads=options.split_spreads,
                        color=options.color,
                        dither=options.dither,
                        gamma=options.gamma,
                    )
                if cover_mode == "generated":
                    cover_image = make_generated_cover(metadata, profile)
                    previews.append(_preview_payload("Capa final", cover_image, "1072 x 1448 · capa gerada", "cover"))
                elif cover_mode == "custom" and custom_cover:
                    cover_path = _save_cover(custom_cover[0], temp_path)
                    cover_image = prepare_cover_image(cover_path, options)
                    previews.append(_preview_payload("Capa final", cover_image, "1072 x 1448 · capa personalizada", "cover"))
                elif cover_mode == "online" and cover_url:
                    cover_path = _save_online_cover(cover_url, temp_path)
                    cover_image = prepare_cover_image(cover_path, options)
                    previews.append(_preview_payload("Capa final", cover_image, "1072 x 1448 · capa online", "cover"))
                for source in iter_source_images(input_path, profile):
                    if not any(item["kind"] == "before" for item in previews):
                        detail = f"{source.image.width} x {source.image.height} · antes do corte"
                        previews.append(_preview_payload("Original — primeira página", source.image, detail, "before"))
                    for page in process_image(source.image, options):
                        mode_label = "color" if options.color else "grayscale"
                        margin = "margem cortada" if options.crop else "margem original"
                        detail = f"{page.width} x {page.height} · {mode_label} · {margin}"
                        previews.append(_preview_payload("Convertida — página Kindle", page, detail, "after"))
                        if len(previews) >= 5:
                            break
                    if len(previews) >= 5:
                        break
            self._send_json({"previews": previews, "images": [item["src"] for item in previews]})
        except (SourceError, ValueError, RuntimeError) as exc:
            self._send_json({"error": str(exc)}, HTTPStatus.BAD_REQUEST)
        except Exception as exc:  # pragma: no cover
            traceback.print_exc()
            self._send_json({"error": f"Falha inesperada: {exc}"}, HTTPStatus.INTERNAL_SERVER_ERROR)

    def _handle_metadata(self, query: str) -> None:
        params = parse_qs(query)
        raw_query = params.get("q", [""])[0].strip()
        kind = params.get("kind", ["auto"])[0].strip() or "auto"
        language = params.get("language", [""])[0].strip()
        if not raw_query:
            self._send_json({"items": []})
            return
        try:
            self._send_json({"query": clean_query(raw_query), "items": search_metadata(raw_query, kind=kind, language=language)})
        except Exception as exc:
            self._send_json({"error": f"Nao consegui buscar metadados: {exc}"}, HTTPStatus.BAD_GATEWAY)

    def _handle_clear_history(self) -> None:
        try:
            if HISTORY_PATH.exists():
                HISTORY_PATH.unlink()
            self._send_json({"ok": True, "items": []})
        except OSError as exc:
            self._send_json({"error": f"Nao consegui limpar a biblioteca: {exc}"}, HTTPStatus.INTERNAL_SERVER_ERROR)

    def _handle_delete_history_files(self) -> None:
        try:
            history = _read_history()
            deleted = 0
            for item in history:
                job_id = str(item.get("jobId", ""))
                target = (OUTPUT_ROOT / job_id).resolve()
                if job_id and _is_inside(target, OUTPUT_ROOT) and target.exists() and target.is_dir():
                    shutil.rmtree(target)
                    deleted += 1
            if HISTORY_PATH.exists():
                HISTORY_PATH.unlink()
            self._send_json({"ok": True, "deleted": deleted, "items": []})
        except OSError as exc:
            self._send_json({"error": f"Nao consegui apagar os arquivos: {exc}"}, HTTPStatus.INTERNAL_SERVER_ERROR)

    def _handle_open_output(self, query: str) -> None:
        params = parse_qs(query)
        job_id = params.get("job", [""])[0]
        target = (OUTPUT_ROOT / job_id).resolve() if job_id else OUTPUT_ROOT.resolve()
        if not _is_inside(target, OUTPUT_ROOT) or not target.exists():
            self._send_json({"error": "Pasta de saida nao encontrada."}, HTTPStatus.NOT_FOUND)
            return
        _open_path(target)
        self._send_json({"ok": True})

    def _serve_frontend(self, request_path: str) -> None:
        relative = request_path.lstrip("/") or "index.html"
        relative = unquote(relative)
        target = (FRONTEND_DIR / relative).resolve()
        if not _is_inside(target, FRONTEND_DIR) or not target.exists() or target.is_dir():
            target = FRONTEND_DIR / "index.html"
        self._send_file(target)

    def _serve_download(self, request_path: str) -> None:
        parts = [unquote(part) for part in request_path.split("/") if part]
        if len(parts) != 3:
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        _, job_id, file_name = parts
        target = (OUTPUT_ROOT / job_id / file_name).resolve()
        if not _is_inside(target, OUTPUT_ROOT) or not target.exists() or target.is_dir():
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        self._send_file(target, attachment=True)

    def _send_file(self, target: Path, attachment: bool = False) -> None:
        content_type = mimetypes.guess_type(target.name)[0] or "application/octet-stream"
        data = target.read_bytes()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        if target.suffix.lower() in {".html", ".js", ".css"}:
            self.send_header("Cache-Control", "no-store")
        if attachment:
            self.send_header("Content-Disposition", f'attachment; filename="{target.name}"')
        self.end_headers()
        self.wfile.write(data)

    def _send_json(self, payload: dict[str, Any], status: HTTPStatus = HTTPStatus.OK) -> None:
        data = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


def _read_form(handler: SimpleHTTPRequestHandler) -> cgi.FieldStorage:
    return cgi.FieldStorage(
        fp=handler.rfile,
        headers=handler.headers,
        environ={
            "REQUEST_METHOD": "POST",
            "CONTENT_TYPE": handler.headers.get("Content-Type", ""),
            "CONTENT_LENGTH": handler.headers.get("Content-Length", "0"),
        },
    )


def _file_items(form: cgi.FieldStorage, name: str) -> list[cgi.FieldStorage]:
    if name not in form:
        return []
    value = form[name]
    values = value if isinstance(value, list) else [value]
    return [item for item in values if getattr(item, "filename", "")]


def _input_groups(items: list[cgi.FieldStorage], group_mode: str) -> list[list[cgi.FieldStorage]]:
    usable = [item for item in items if Path(_upload_name(item)).suffix.lower() in SUPPORTED_EXTENSIONS]
    if not usable:
        raise SourceError("Nenhum arquivo suportado foi encontrado.")
    if group_mode in {"volume", "chapters"}:
        return [usable]
    if len(usable) > 1 and all(is_image_path(Path(_upload_name(item))) for item in usable):
        return [usable]
    return [[item] for item in sorted(usable, key=lambda item: natural_key(_upload_name(item)))]


def _title_for_group(form: cgi.FieldStorage, group: list[cgi.FieldStorage], group_index: int, group_count: int) -> str:
    requested = _field(form, "title", "").strip()
    if requested and group_count == 1:
        return requested
    if len(group) > 1:
        return requested or _guess_group_title(group)
    return Path(_upload_name(group[0])).stem


def _save_group(group: list[cgi.FieldStorage], source_dir: Path) -> Path:
    source_dir.mkdir(parents=True, exist_ok=True)
    if len(group) == 1:
        return _save_upload(group[0], source_dir)
    for index, item in enumerate(group, start=1):
        name = _upload_name(item)
        suffix = Path(name).suffix.lower()
        target = source_dir / f"{index:04d}-{slugify(Path(name).stem, 'page')}{suffix}"
        _write_upload(item, target)
    return source_dir


def _save_cover(item: cgi.FieldStorage, output_dir: Path) -> Path:
    suffix = Path(_upload_name(item)).suffix.lower() or ".jpg"
    target = output_dir / f"cover{suffix}"
    _write_upload(item, target)
    return target


def _save_online_cover(url: str, output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    data = download_cover(url)
    target = output_dir / "online-cover.jpg"
    target.write_bytes(data)
    return target


def _save_upload(item: cgi.FieldStorage, output_dir: Path) -> Path:
    name = _upload_name(item)
    suffix = Path(name).suffix.lower()
    safe_name = f"{slugify(Path(name).stem, 'input')}{suffix}"
    target = output_dir / safe_name
    _write_upload(item, target)
    return target


def _upload_name(item: cgi.FieldStorage) -> str:
    return str(getattr(item, "filename", "")).replace("\\", "/").strip("/")


def _guess_group_title(group: list[cgi.FieldStorage]) -> str:
    names = [Path(_upload_name(item)).stem for item in group]
    if not names:
        return "Volume"
    cleaned = [clean_query(name) for name in names]
    first_words = cleaned[0].split()
    while first_words:
        prefix = " ".join(first_words)
        if all(name.casefold().startswith(prefix.casefold()) for name in cleaned):
            return prefix
        first_words.pop()
    parent = Path(_upload_name(group[0])).parent.name
    return parent if parent and parent != "." else "Volume organizado"


def _write_upload(item: cgi.FieldStorage, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    item.file.seek(0)
    with target.open("wb") as output:
        while True:
            chunk = item.file.read(1024 * 1024)
            if not chunk:
                break
            output.write(chunk)


def _file_payload(job_id: str, path: Path) -> dict[str, Any]:
    return {
        "name": path.name,
        "url": f"/download/{job_id}/{path.name}",
        "size": path.stat().st_size,
    }


def _input_payload(group: list[cgi.FieldStorage]) -> dict[str, Any]:
    names = [_upload_name(item) for item in group]
    size = 0
    for item in group:
        item.file.seek(0, 2)
        size += item.file.tell()
        item.file.seek(0)
    return {
        "name": names[0] if len(names) == 1 else f"{len(names)} arquivos",
        "count": len(names),
        "size": size,
        "files": names[:12],
    }


def _image_data_url(image, quality: int) -> str:
    buffer = io.BytesIO()
    save_image = image.convert("RGB") if image.mode != "RGB" else image
    save_image.save(buffer, "JPEG", quality=quality, optimize=True)
    encoded = base64.b64encode(buffer.getvalue()).decode("ascii")
    return f"data:image/jpeg;base64,{encoded}"


def _preview_payload(label: str, image, detail: str, kind: str) -> dict[str, Any]:
    return {
        "label": label,
        "detail": detail,
        "kind": kind,
        "width": image.width,
        "height": image.height,
        "src": _image_data_url(image, 82),
    }


def _read_history() -> list[dict[str, Any]]:
    if not HISTORY_PATH.exists():
        return []
    try:
        return json.loads(HISTORY_PATH.read_text("utf-8"))[:80]
    except json.JSONDecodeError:
        return []


def _append_history(item: dict[str, Any]) -> None:
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    history = _read_history()
    history.insert(0, item)
    HISTORY_PATH.write_text(json.dumps(history[:80], indent=2), "utf-8")


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _field(form: cgi.FieldStorage, name: str, default: str) -> str:
    if name not in form:
        return default
    item = form[name]
    if isinstance(item, list):
        item = item[0]
    return str(item.value)


def _bool_field(form: cgi.FieldStorage, name: str, default: bool) -> bool:
    if name not in form:
        return default
    return _field(form, name, "false").lower() in {"1", "true", "yes", "on"}


def _int_field(form: cgi.FieldStorage, name: str, default: int) -> int:
    try:
        return int(_field(form, name, str(default)))
    except ValueError:
        return default


def _float_field(form: cgi.FieldStorage, name: str, default: float) -> float:
    try:
        return float(_field(form, name, str(default)))
    except ValueError:
        return default


def _is_inside(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def _unique_job_id(base: str) -> str:
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    candidate = base
    index = 2
    while (OUTPUT_ROOT / candidate).exists():
        candidate = f"{base}-{index}"
        index += 1
    return candidate


def _open_path(target: Path) -> None:
    system = platform.system()
    if system == "Darwin":
        subprocess.run(["open", str(target)], check=False)
    elif system == "Windows":
        subprocess.run(["explorer", str(target)], check=False)
    else:
        subprocess.run(["xdg-open", str(target)], check=False)


def main() -> int:
    host = "127.0.0.1"
    port = _pick_port(host, 8765)
    server = ThreadingHTTPServer((host, port), KindleForgeHandler)
    print(f"Kindle Forge aberto em http://{host}:{port}")
    print("Pressione Ctrl+C para encerrar.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nEncerrado.")
    finally:
        server.server_close()
    return 0


def _pick_port(host: str, start: int) -> int:
    import socket

    port = start
    while port < start + 100:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            if sock.connect_ex((host, port)) != 0:
                return port
        port += 1
    raise RuntimeError("Nao encontrei uma porta local livre.")


if __name__ == "__main__":
    raise SystemExit(main())
