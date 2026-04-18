import argparse
import os
import secrets
import string
import sys


def _make_id(length: int) -> str:
    alphabet = string.ascii_lowercase + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


def _candidate_name(prefix: str, id_value: str, ext: str) -> str:
    if ext and not ext.startswith("."):
        ext = "." + ext
    return f"{prefix}{id_value}{ext}"


def generate_unique_name(
    *,
    parent_dir: str,
    prefix: str,
    ext: str,
    length: int,
    max_retries: int,
) -> str:
    if not os.path.isabs(parent_dir):
        parent_dir = os.path.abspath(parent_dir)
    if not os.path.isdir(parent_dir):
        raise FileNotFoundError(parent_dir)

    for _ in range(max_retries):
        id_value = _make_id(length)
        name = _candidate_name(prefix, id_value, ext)
        if not os.path.exists(os.path.join(parent_dir, name)):
            return name

    raise RuntimeError("failed to generate a unique id within retry limit")


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--parent", required=True)
    parser.add_argument("--prefix", required=True)
    parser.add_argument("--ext", default="")
    parser.add_argument("--length", type=int, default=8)
    parser.add_argument("--max-retries", type=int, default=5)
    parser.add_argument("--id-only", action="store_true")
    args = parser.parse_args(argv)

    name = generate_unique_name(
        parent_dir=args.parent,
        prefix=args.prefix,
        ext=args.ext,
        length=args.length,
        max_retries=args.max_retries,
    )

    if args.id_only:
        if not name.startswith(args.prefix):
            print(name)
            return 0
        base = name[len(args.prefix) :]
        if args.ext:
            ext = args.ext if args.ext.startswith(".") else "." + args.ext
            if base.endswith(ext):
                base = base[: -len(ext)]
        print(base)
        return 0

    print(name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
