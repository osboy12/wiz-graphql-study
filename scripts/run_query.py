"""Run a .graphql file with JSON variables; optionally auto-paginate a connection field.

Examples:
  python scripts/run_query.py examples/basics_typename.graphql
  python scripts/run_query.py examples/wiz_graph_search.graphql \
      --vars examples/wiz_graph_search.vars.json --paginate graphSearch --max-items 500 -o outputs/vms.json
"""
import argparse
import json
from itertools import islice
from pathlib import Path

from wiz_client import WizClient


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("query_file")
    p.add_argument("--vars", help="JSON file or inline JSON string")
    p.add_argument("--paginate", metavar="FIELD", help="root connection field to page through")
    p.add_argument("--max-items", type=int, default=None)
    p.add_argument("-o", "--output", help="write JSON here (e.g. outputs/x.json; git-ignored)")
    args = p.parse_args()

    query = Path(args.query_file).read_text()
    variables = {}
    if args.vars:
        src = Path(args.vars)
        variables = json.loads(src.read_text() if src.exists() else args.vars)

    client = WizClient()
    if args.paginate:
        result = list(islice(client.paginate(query, variables, args.paginate), args.max_items))
    else:
        result = client.query(query, variables)

    text = json.dumps(result, indent=2)
    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(text)
        print(f"Wrote {args.output}")
    else:
        print(text)


if __name__ == "__main__":
    main()
