# 03 — Wiz API patterns (from public sources)

> Everything here is collected from **public** third-party integration docs (links below). Wiz's own docs (docs.wiz.io) need a login. Treat items marked ⚠️ as **verify in your tenant's API Explorer**.

## Auth flow (OAuth 2.0 client credentials)
1. An admin creates a **service account** (Settings → Access Management → Service Accounts, type *Custom Integration (GraphQL API)*) with scopes such as `read:all` or narrower (e.g. `read:vulnerabilities`). You get a **client ID** and **client secret** (secret shown once).
2. Exchange for a token:
```
POST https://auth.app.wiz.io/oauth/token
Content-Type: application/x-www-form-urlencoded

grant_type=client_credentials&client_id=...&client_secret=...&audience=wiz-api
```
   - Commercial (Cognito): `https://auth.app.wiz.io/oauth/token`, audience `wiz-api`.
   - Legacy Auth0 tenants: `https://auth.wiz.io/oauth/token`, audience `beyond-api`. ⚠️
   - Gov tenants use other hosts (e.g. `auth.app.wiz.us`, `auth.gov.wiz.io`). ⚠️
   - Response contains `access_token` (and `expires_in`) — cache and refresh before expiry.
3. Call the **regional** endpoint with a Bearer token:
```
POST https://api.<region>.app.wiz.io/graphql
Authorization: Bearer <access_token>
```
   Region (e.g. `us1`, `eu1`, `us17`) is in the portal under *User icon → Tenant Info*. Wrong region → 401 even with a valid token.

## graphSearch (Security Graph)
Graph queries use one GraphQL field, `graphSearch`, with the actual graph pattern passed as a nested JSON **variable** of type `GraphEntityQueryInput`:
```graphql
query GraphSearch($query: GraphEntityQueryInput, $first: Int, $after: String, $quick: Boolean) {
  graphSearch(query: $query, first: $first, after: $after, quick: $quick, projectId: "*") {
    totalCount
    maxCountReached
    pageInfo { hasNextPage endCursor }
    nodes { entities { id name type } }
  }
}
```
Variables:
```json
{
  "first": 50,
  "quick": true,
  "query": {
    "type": ["NETWORK_ADDRESS"],
    "where": {"address": {"EQUALS": ["10.0.0.1"]}},
    "relationships": [{
      "type": [{"type": "OWNS", "reverse": true}],
      "with": {"type": ["NETWORK_INTERFACE"], "select": true}
    }]
  }
}
```
Shape of `GraphEntityQueryInput` (per public Terraform-provider source): `type` (list of entity-type enums), `where` (property predicates like `{"prop": {"EQUALS": [...]}}`), `relationships` (list of `{type: [{type, reverse}], with: <nested query>, negate, optional}`), `select`, `aggregate`, `aggregateConstraint`, `as`.

- `nodes[].entities` is a list: one entry per `select: true` node in the pattern (a "path"). ⚠️
- `quick: true` = faster, possibly less ordered/complete; `false` for stable ordering. ⚠️
- Easiest way to build queries: build the search in the portal's **Security Graph** UI, then use its "show query"/copy-as-API option. ⚠️ (feature name may vary)
- Valid entity types, relationship types, and property names: check enums `GraphEntityTypeValue`/`GraphRelationshipType` in your schema. ⚠️

## Other common root fields (seen in public integrations) ⚠️
`issues`/`issuesV2`, `vulnerabilityFindings`, `cloudResources`, `users`, `projects`, `cloudConfigurationRules`. Names and filters change across API versions — confirm in the explorer.

## Pagination loop
Standard Relay: `first` + `after`, read `pageInfo { hasNextPage endCursor }`. Public integrations cite a max page size of around 500 for many fields (some say up to 5000). ⚠️ `scripts/run_query.py --paginate <field>` implements the loop.

## Rate limits ⚠️
Wiz enforces API rate limits (commonly quoted as a few requests/second per service account) and returns HTTP 429 when exceeded. Not verified from an official public page — check docs.wiz.io. The client retries with backoff on 429/5xx.

## Sources (public)
- Swimlane Wiz auth guide: https://docs.swimlane.com/authentication-guides/wiz
- Synqly Wiz setup: https://docs.synqly.com/guides/provider-configuration/wiz-vulnerability-setup
- Compyl Wiz integration: https://compyl.readme.io/docs/wiz-integration
- Terraform provider (GraphEntityQueryInput types): https://github.com/AxtonGrams/terraform-provider-wiz
- QloudX graphSearch example: https://www.qloudx.com/whos-talking-to-prod-auditing-cross-environment-traffic-before-you-segment-a-flat-aws-network/
