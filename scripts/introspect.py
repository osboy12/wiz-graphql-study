"""Dump the API schema as SDL to schema.graphql (git-ignored). Needs introspection enabled."""
import argparse
from pathlib import Path

from graphql import build_client_schema, get_introspection_query, print_schema

from wiz_client import WizClient


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("-o", "--output", default="schema.graphql")
    p.add_argument("--json", help="also save raw introspection JSON here")
    args = p.parse_args()

    data = WizClient().query(get_introspection_query(descriptions=True))
    if args.json:
        import json
        Path(args.json).write_text(json.dumps(data, indent=2))
    sdl = print_schema(build_client_schema(data))
    Path(args.output).write_text(sdl)
    print(f"Wrote {args.output} ({len(sdl.splitlines())} lines)")


if __name__ == "__main__":
    main()
