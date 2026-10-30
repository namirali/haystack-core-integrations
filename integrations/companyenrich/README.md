# companyenrich-haystack

Company domain enrichment for Haystack pipelines and agents, using
[CompanyEnrich](https://companyenrich.com/) and its
[API reference](https://docs.companyenrich.com/reference/get_companies-enrich).

`CompanyEnrichCompanyEnricher` returns the complete profile under `profile` and supports native
`run_async()`. `CompanyEnrichCompanyEnricherTool` exposes the same operation to agents. Set
`COMPANYENRICH_API_KEY` to a key from the [CompanyEnrich dashboard](https://app.companyenrich.com/).
Each enrichment request consumes one credit; retries default to zero and never follow redirects.

Install this proposed integration from source with `uv pip install -e integrations/companyenrich`.

## Contributing

Refer to the general [Contribution Guidelines](https://github.com/deepset-ai/haystack-core-integrations/blob/main/CONTRIBUTING.md).

From this integration directory, run `hatch run test:unit` for mocked tests. Live tests additionally
require `COMPANYENRICH_API_KEY` and `COMPANYENRICH_RUN_PAID_TESTS=1`; `hatch run test:integration`
makes two enrichment calls and consumes two credits. No live tests are needed for the mocked suite.
