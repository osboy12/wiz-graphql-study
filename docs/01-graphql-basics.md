# 01 — GraphQL basics (for Python people)

GraphQL = one HTTP endpoint (usually `POST /graphql`) taking JSON `{"query": "...", "variables": {...}}`.
You ask for exactly the fields you want; the response mirrors the shape of your query.

Python analogy: the schema is a set of typed `dataclass`es; a query is like picking attributes off nested objects; the server returns a `dict` shaped like your selection.

## Queries and fields
```graphql
query {
  users(first: 2) {      # field with an argument
    nodes { id name }    # sub-selection: you must name scalar leaves
  }
}
```
Response:
```json
{"data": {"users": {"nodes": [{"id": "1", "name": "Ada"}, {"id": "2", "name": "Linus"}]}}}
```

## Arguments
Any field can take arguments (`first: 10`, `filterBy: {...}`). Think keyword args: `users(first=10)`.

## Variables
Don't string-format values into queries (same reason you don't f-string SQL). Declare typed variables:
```graphql
query ListUsers($first: Int!, $after: String) {
  users(first: $first, after: $after) { nodes { id } }
}
```
and send `{"first": 50, "after": null}` as `variables`. `!` means non-null (required). `[String!]` is a list.

## Aliases
Rename a field in the result, or call the same field twice:
```graphql
query { admins: users(role: ADMIN) { totalCount }  readers: users(role: READER) { totalCount } }
```

## Fragments
Reusable field sets (like a shared mixin):
```graphql
fragment UserBits on User { id name email }
query { users(first: 5) { nodes { ...UserBits } } }
```
Inline fragments pick fields by concrete type on unions/interfaces: `... on VirtualMachine { region }`.

## Pagination (Relay-style connections)
Lists are often a *connection*:
```graphql
users(first: 100, after: $cursor) {
  nodes { id }                  # or edges { cursor node { id } }
  pageInfo { hasNextPage endCursor }
  totalCount                    # sometimes available
}
```
Loop in Python:
```python
cursor = None
while True:
    data = run(query, {"first": 100, "after": cursor})["users"]
    yield from data["nodes"]
    if not data["pageInfo"]["hasNextPage"]:
        break
    cursor = data["pageInfo"]["endCursor"]
```

## Errors
HTTP status is often 200 even when things fail. Always check the `errors` array:
```json
{"data": null, "errors": [{"message": "Cannot query field 'foo' on type 'User'", "path": ["users"]}]}
```
Partial success is possible: both `data` and `errors` can be present. Rate limiting / auth issues may show as HTTP 429/401/403.

## Introspection
The schema is queryable: `{ __schema { types { name } } }` or `{ __type(name: "User") { fields { name type { name kind } } } }`. Tools use this to build docs/autocomplete. See doc 02.

## Reading SDL (Schema Definition Language)
```graphql
type User {
  id: ID!
  name: String
  projects(first: Int, after: String): ProjectConnection!
}
enum Role { ADMIN READER }
input UserFilters { role: [Role!] search: String }
scalar DateTime
```
- `type` = output object, `input` = argument object, `enum` = fixed choices, `scalar` = leaf value.
- `interface`/`union` = polymorphism (use inline fragments).
- `Query` type = entry points; `Mutation` = writes (you probably want read-only).

Free reference: https://graphql.org/learn/
