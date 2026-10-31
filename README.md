# wiz-graphql-study

Personal study repo: learn GraphQL, then learn the patterns used by the Wiz (cloud security) GraphQL API / Security Graph.

## Safety rules (this repo is PUBLIC)
- **No employer data.** No tenant URLs, tenant/project/resource IDs, query results, screenshots, or credentials.
- Only generic GraphQL material and Wiz patterns from **public** sources (cited in the docs).
- Anything not confirmed publicly is marked **"verify in your tenant's API Explorer"**.
- Credentials live only in a local `.env` (git-ignored). Schema dumps and outputs are git-ignored too.

## Layout
```
docs/01-graphql-basics.md     GraphQL for Python devs
docs/02-reading-a-schema.md   introspection, SDL, explorers, VS Code setup
docs/03-wiz-api-patterns.md   auth flow, graphSearch, pagination, limits
examples/*.graphql            generic sample queries
scripts/wiz_client.py         tiny auth + query client (requests)
scripts/introspect.py         dump schema to schema.graphql
scripts/run_query.py          run a .graphql file with JSON variables (+ auto-paginate)
```

## Using it at work
1. Read the docs in the browser on GitHub (read-only is fine).
2. On your work machine: download the repo as ZIP (or `git clone` the public URL).
3. `python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`
4. `cp .env.example .env` and fill in the service-account values from your Wiz admin. Never commit `.env`.
5. `python scripts/introspect.py` (if introspection is allowed), then e.g.
   `python scripts/run_query.py examples/wiz_graph_search.graphql --vars examples/wiz_graph_search.vars.json --paginate graphSearch`
6. Keep results local. Follow your employer's policy on API use.
