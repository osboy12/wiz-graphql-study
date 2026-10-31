# 02 — Reading & documenting a schema

## Introspection
Every spec-compliant server can describe itself via `__schema` / `__type`. `scripts/introspect.py` runs the standard introspection query and converts it to SDL using `graphql-core`'s `build_client_schema` + `print_schema`, writing `schema.graphql` (git-ignored — your tenant's schema stays local).

**Caveat:** vendors may disable or limit introspection in production. If it fails, use the vendor's API Explorer/docs instead.

## Interactive explorers
- **GraphiQL** (https://github.com/graphql/graphiql) — the reference in-browser IDE: autocomplete + docs pane.
- **Apollo Sandbox** (https://studio.apollographql.com/sandbox) — point at any endpoint, add an `Authorization: Bearer ...` header. Note: this sends your token from a browser to a third-party-hosted page; check policy first.
- **Wiz API Explorer** — inside the Wiz portal (login required). The safest option at work.

## Static docs generators
- **SpectaQL** (https://github.com/anvilco/spectaql) — static HTML from a schema file or introspection.
- **GraphDoc** (https://github.com/2fd/graphdoc) — similar, older.
Generate locally; don't publish your tenant's schema.

## VS Code
- Extension: *GraphQL: Language Feature Support* (`GraphQL.vscode-graphql`) + *GraphQL: Syntax Highlighting*.
- Formatter: Prettier formats `.graphql`.
- Add `graphql.config.yml` at repo root:
```yaml
schema: schema.graphql        # the dump from scripts/introspect.py
documents: examples/**/*.graphql
```
Now `.graphql` files get autocomplete, hover docs and validation against the real schema.

## Tips for exploring a big schema
- Start at `type Query` and search for the field you need.
- Follow `...Connection` types to find `nodes`, `pageInfo`.
- Look at `input ...Filters` types to see what you can filter by.
- `grep -n "^enum" schema.graphql` lists allowed values (e.g. entity types).
