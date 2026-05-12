from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Optional

from .converter import ConvertError, ConvertRequest, convert
from .profiles import get_profile
from .sources import SourceError


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="kindle-forge",
        description="Convert comics, manga, manhwa and PDFs for e-readers and tablets.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    convert_parser = subparsers.add_parser("convert", help="Convert one input file or folder.")
    convert_parser.add_argument("input", type=Path, help="PDF, CBZ, CBR, archive, folder, or image.")
    convert_parser.add_argument("-o", "--output", type=Path, default=Path("dist"), help="Output directory.")
    convert_parser.add_argument("--profile", default="kindle11", help="Device profile. Default: kindle11.")
    convert_parser.add_argument("--title", help="Book title. Defaults to input file name.")
    convert_parser.add_argument("--author", default="Unknown", help="Book author metadata.")
    convert_parser.add_argument("--series", default="", help="Series metadata.")
    convert_parser.add_argument("--volume", default="", help="Volume metadata.")
    convert_parser.add_argument("--publisher", default="", help="Publisher metadata.")
    convert_parser.add_argument("--description", default="", help="Description metadata.")
    convert_parser.add_argument(
        "--mode",
        choices=["auto", "manga", "comic", "webtoon"],
        default="manga",
        help="Reading/layout mode. Default: manga.",
    )
    convert_parser.add_argument(
        "--format",
        default="epub",
        help="Output format: epub, cbz, pdf, comma-separated list, or all. Default: epub.",
    )
    convert_parser.add_argument("--quality", type=int, default=85, help="JPEG quality from 1 to 95.")
    convert_parser.add_argument(
        "--cover",
        choices=["first", "generated", "custom", "none"],
        default="first",
        help="Cover strategy. Default: first.",
    )
    convert_parser.add_argument("--cover-file", type=Path, help="Cover image when --cover custom is used.")
    convert_parser.add_argument("--split-size-mb", type=int, default=200, help="Split output around this size. Use 0 to disable.")
    convert_parser.add_argument("--gamma", type=float, default=1.0, help="Gamma adjustment. Values below 1 darken.")
    convert_parser.add_argument("--pdf-zoom", type=float, default=1.0, help="Extra render zoom for PDF pages.")
    convert_parser.add_argument("--no-crop", action="store_true", help="Disable automatic border cropping.")
    convert_parser.add_argument("--no-split-spreads", action="store_true", help="Disable double-page splitting.")
    convert_parser.add_argument("--color", action="store_true", help="Preserve color instead of grayscale.")
    convert_parser.add_argument("--dither", action="store_true", help="Use grayscale dithering.")
    convert_parser.add_argument("--no-upscale", action="store_true", help="Do not enlarge pages smaller than Kindle.")
    return parser


def main(argv: Optional[list[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "convert":
        if not 1 <= args.quality <= 95:
            parser.error("--quality must be between 1 and 95")
        if args.pdf_zoom <= 0:
            parser.error("--pdf-zoom must be greater than 0")

        try:
            profile = get_profile(args.profile)
            result = convert(
                ConvertRequest(
                    input_path=args.input,
                    output_dir=args.output,
                    profile=profile,
                    title=args.title,
                    author=args.author,
                    series=args.series,
                    volume=args.volume,
                    publisher=args.publisher,
                    description=args.description,
                    mode=args.mode,
                    output_format=args.format,
                    cover_mode=args.cover,
                    cover_path=args.cover_file,
                    split_size_mb=args.split_size_mb,
                    quality=args.quality,
                    crop=not args.no_crop,
                    split_spreads=not args.no_split_spreads,
                    color=args.color,
                    dither=args.dither,
                    upscale=not args.no_upscale,
                    gamma=args.gamma,
                    pdf_zoom=args.pdf_zoom,
                )
            )
        except (ConvertError, SourceError, ValueError) as exc:
            print(f"Error: {exc}", file=sys.stderr)
            return 2

        print(f"Converted '{result.title}' into {result.page_count} Kindle page(s).")
        for output in result.outputs:
            print(output)
        return 0

    parser.error("Unknown command")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
