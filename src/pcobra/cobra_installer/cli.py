"""CLI mínima para el instalador Cobra."""

from __future__ import annotations

import argparse

from .project import CobraInstallerError
from .runtime_builder import package_current_project


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="cobra-installer")
    parser.add_argument("project_root", nargs="?", default=".")
    parser.add_argument("--entrypoint")
    parser.add_argument("--output-dir")
    parser.add_argument("--name")
    parser.add_argument("--target", default="current")
    parser.add_argument(
        "--builder",
        choices=("local", "docker", "vm", "ci", "remote"),
        default="local",
        help="Builder futuro para aislar builds no nativos; solo local está implementado todavía.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        result = package_current_project(
            args.project_root,
            entrypoint=args.entrypoint,
            output_dir=args.output_dir,
            name=args.name,
            target=args.target,
            builder=args.builder,
            log_callback=print,
        )
    except CobraInstallerError as exc:
        print(f"Error: {exc}")
        return 1
    print(result.artifact_path or result.output_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
