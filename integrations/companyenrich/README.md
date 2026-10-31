# companyenrich-haystack

Company and people data for Haystack pipelines and agents using [CompanyEnrich](https://companyenrich.com/).
Set `COMPANYENRICH_API_KEY` to a key from the [dashboard](https://app.companyenrich.com/).
Install this proposed integration from source with `uv pip install -e integrations/companyenrich`.

`CompanyEnrichToolset()` exposes twelve core operations and an advanced tool with 42 fixed API operations.
Each operation also has a native sync/async component. The original `CompanyEnrichCompanyEnricher` and
`CompanyEnrichCompanyEnricherTool` preserve their names and `profile` output. New components return the complete
JSON response under `data`, preserving arrays, numbers (including zero), metadata and future fields.

```python
from haystack_integrations.components.connectors.companyenrich import CompanyEnrichPeopleSearch
from haystack_integrations.tools.companyenrich import CompanyEnrichToolset

people = CompanyEnrichPeopleSearch().run(
    filters={"companyFilter": {"domains": ["stripe.com"]}}, expand=["education"], page_size=5
)
tools = CompanyEnrichToolset()  # Pass to an Agent or ToolInvoker.
```

Core components: `CompanyEnrichCompanyEnricher`, `CompanyEnrichCompanySearch`, `CompanyEnrichSimilarCompanies`,
`CompanyEnrichPeopleSearch`, `CompanyEnrichPersonLookup`, `CompanyEnrichWorkforce`, `CompanyEnrichCompanyMatcher`,
`CompanyEnrichBatchEnricher`, `CompanyEnrichCompanyById`, `CompanyEnrichPersonById`, `CompanyEnrichSearchCount`,
and `CompanyEnrichSimilarCount`. All support `run` and native `run_async`.

Search filters are preserved in full; dedicated non-null fields override corresponding filter values. Supported
`expand` and `wait_for_enrichment` inputs map to the documented query parameters. Search defaults to page 1 and
5 results, with page size 1–100 and a 10,000-result page window. Lookalikes accept 1–10 domains; batch accepts 1–50.
Workforce requires exactly one company UUID or domain. Person IDs accept positive int64 integers or decimal strings.

`CompanyEnrichAdvancedRequest` accepts `operation`, `body`, `query`, `path_parameters` and `allow_beta=False`.
Its fixed enum covers preview/count/scroll, education, geography/taxonomy, async exports, bulk enrichment and job
lifecycle in addition to the core routes. Saved-list administration and `/me` are excluded. Three beta email routes
require explicit boolean opt-in. Advanced page/scroll requests default to 10 results. Export jobs require an explicit
count from 1 to 50,000. Identifiers, required inputs, bounds and unknown query/path fields are checked before HTTP.

Every new call makes one request to the fixed HTTPS API with redirects disabled. There is no automatic retry,
pagination, polling or result-URL download. The legacy enricher keeps its explicit `max_retries` option for compatibility;
it defaults to zero and each additional attempt can consume credits. HTTP errors are sanitized, including attached
request headers and response bodies. See the [API reference](https://docs.companyenrich.com/reference) for schemas and
current credit costs. No authenticated or billable API calls were made to validate this proposal.

## Contributing

Follow the [Contribution Guidelines](https://github.com/deepset-ai/haystack-core-integrations/blob/main/CONTRIBUTING.md).
From this integration directory, run `hatch run test:unit`, `hatch run test:types`, `hatch run fmt-check`, and `hatch build`.
Live tests require `COMPANYENRICH_API_KEY` and `COMPANYENRICH_RUN_PAID_TESTS=1`; `hatch run test:integration` makes two
enrichment calls and consumes two credits. Live validation and upstream proposal approval remain prerequisites for an
upstream PR. The optional CI workflow remains an inert sidecar pending the contributor token's workflow scope.
