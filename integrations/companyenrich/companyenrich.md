---
title: "CompanyEnrich"
id: integrations-companyenrich
description: "CompanyEnrich integration for Haystack"
slug: "/integrations-companyenrich"
---


## haystack_integrations.components.connectors.companyenrich.connector

### CompanyEnrichCompanyEnricher

Retrieve a structured company profile from CompanyEnrich by domain.

Uses the [CompanyEnrich enrichment API](https://docs.companyenrich.com/reference/get_companies-enrich).
Each request consumes one CompanyEnrich credit. Retries are disabled by default because a retry
can consume another credit. The complete API profile is preserved, including optional fields.

### Usage example

```python
from haystack_integrations.components.connectors.companyenrich import CompanyEnrichCompanyEnricher

enricher = CompanyEnrichCompanyEnricher()  # Reads COMPANYENRICH_API_KEY during warm-up.
result = enricher.run(domain="stripe.com")
print(result["profile"]["name"])
```

#### __init__

```python
__init__(
    *,
    api_key: Secret = Secret.from_env_var("COMPANYENRICH_API_KEY"),
    timeout: float = 30.0,
    max_retries: int = 0
) -> None
```

Initialize the component without resolving credentials or making network requests.

**Parameters:**

- **api_key** (<code>Secret</code>) – CompanyEnrich API key, read from `COMPANYENRICH_API_KEY` by default.
- **timeout** (<code>float</code>) – Positive, finite HTTP timeout in seconds.
- **max_retries** (<code>int</code>) – Number of additional attempts on transient failures. Each can consume credits.

**Raises:**

- <code>TypeError</code> – The API key is not a `Secret`, or a numeric parameter has the wrong type.
- <code>ValueError</code> – The timeout is not positive and finite, or the retry count is negative.

#### warm_up

```python
warm_up() -> None
```

Resolve credentials once, without making a network request.

**Raises:**

- <code>ValueError</code> – The configured API key is missing or empty.

#### to_dict

```python
to_dict() -> dict[str, Any]
```

Serialize the component, preserving the credential reference and HTTP settings.

**Returns:**

- <code>dict\[str, Any\]</code> – Component type and serialized initialization parameters.

#### run

```python
run(
    domain: str,
    *,
    expand: list[str] | None = None,
    wait_for_enrichment: StrictBool | None = None
) -> dict[str, Any]
```

Enrich one company domain.

**Parameters:**

- **domain** (<code>str</code>) – Non-empty company domain, such as `stripe.com`, at most 1024 characters.
- **expand** (<code>list\[str\] | None</code>) – Optional workforce expansion.
- **wait_for_enrichment** (<code>StrictBool | None</code>) – Explicit wait option; None preserves the API default.

**Returns:**

- <code>dict\[str, Any\]</code> – Dictionary with `profile`, containing the complete CompanyEnrich JSON object.

**Raises:**

- <code>TypeError</code> – The domain is not a string or the API response is not a JSON object.
- <code>ValueError</code> – The domain is empty or too long, or credentials cannot be resolved.
- <code>httpx.HTTPStatusError</code> – The API returns an unsuccessful HTTP status, including redirects.
- <code>httpx.RequestError</code> – The HTTP request fails or times out.

#### run_async

```python
run_async(
    domain: str,
    *,
    expand: list[str] | None = None,
    wait_for_enrichment: StrictBool | None = None
) -> dict[str, Any]
```

Asynchronously enrich one company domain with native async HTTP I/O.

**Parameters:**

- **domain** (<code>str</code>) – Non-empty company domain, such as `stripe.com`, at most 1024 characters.
- **expand** (<code>list\[str\] | None</code>) – Optional workforce expansion.
- **wait_for_enrichment** (<code>StrictBool | None</code>) – Explicit wait option; None preserves the API default.

**Returns:**

- <code>dict\[str, Any\]</code> – Dictionary with `profile`, containing the complete CompanyEnrich JSON object.

**Raises:**

- <code>TypeError</code> – The domain is not a string or the API response is not a JSON object.
- <code>ValueError</code> – The domain is empty or too long, or credentials cannot be resolved.
- <code>httpx.HTTPStatusError</code> – The API returns an unsuccessful HTTP status, including redirects.
- <code>httpx.RequestError</code> – The HTTP request fails or times out.

## haystack_integrations.components.connectors.companyenrich.operations

One-request CompanyEnrich components with full JSON results.

### CompanyEnrichCompanySearch

Bases: <code>\_CompanyEnrichRequest</code>

Call post_companies_search once and preserve the full response under data.

#### run

```python
run(
    semantic_query: str | None = None,
    *,
    query: str | None = None,
    filters: dict[str, Any] | None = None,
    page: StrictInt = 1,
    page_size: StrictInt = 5,
    expand: list[str] | None = None
) -> dict[str, Any]
```

Call the CompanyEnrich operation once.

**Parameters:**

- **semantic_query** (<code>str | None</code>) – Optional semantic company description, up to 500 characters.
- **query** (<code>str | None</code>) – Optional literal company query, up to 250 characters.
- **filters** (<code>dict\[str, Any\] | None</code>) – Full documented API filters; dedicated non-null fields take precedence.
- **page** (<code>StrictInt</code>) – One-based page number; page times page_size must not exceed 10,000.
- **page_size** (<code>StrictInt</code>) – Results per page from 1 to 100; defaults to 5.
- **expand** (<code>list\[str\] | None</code>) – Documented expansions: workforce for companies or education for people.

**Returns:**

- <code>dict\[str, Any\]</code> – Complete JSON response under data, preserving objects, arrays and numbers.

#### run_async

```python
run_async(
    semantic_query: str | None = None,
    *,
    query: str | None = None,
    filters: dict[str, Any] | None = None,
    page: StrictInt = 1,
    page_size: StrictInt = 5,
    expand: list[str] | None = None
) -> dict[str, Any]
```

Asynchronously call the CompanyEnrich operation once.

**Parameters:**

- **semantic_query** (<code>str | None</code>) – Optional semantic company description, up to 500 characters.
- **query** (<code>str | None</code>) – Optional literal company query, up to 250 characters.
- **filters** (<code>dict\[str, Any\] | None</code>) – Full documented API filters; dedicated non-null fields take precedence.
- **page** (<code>StrictInt</code>) – One-based page number; page times page_size must not exceed 10,000.
- **page_size** (<code>StrictInt</code>) – Results per page from 1 to 100; defaults to 5.
- **expand** (<code>list\[str\] | None</code>) – Documented expansions: workforce for companies or education for people.

**Returns:**

- <code>dict\[str, Any\]</code> – Complete JSON response under data, preserving objects, arrays and numbers.

### CompanyEnrichSimilarCompanies

Bases: <code>\_CompanyEnrichRequest</code>

Call post_companies_similar once and preserve the full response under data.

#### run

```python
run(
    domains: list[str],
    *,
    filters: dict[str, Any] | None = None,
    page: StrictInt = 1,
    page_size: StrictInt = 5,
    expand: list[str] | None = None,
    wait_for_enrichment: StrictBool | None = None
) -> dict[str, Any]
```

Call the CompanyEnrich operation once.

**Parameters:**

- **domains** (<code>list\[str\]</code>) – Seed domains (1-10) or batch domains (1-50), depending on the operation.
- **filters** (<code>dict\[str, Any\] | None</code>) – Full documented API filters; dedicated non-null fields take precedence.
- **page** (<code>StrictInt</code>) – One-based page number; page times page_size must not exceed 10,000.
- **page_size** (<code>StrictInt</code>) – Results per page from 1 to 100; defaults to 5.
- **expand** (<code>list\[str\] | None</code>) – Documented expansions: workforce for companies or education for people.
- **wait_for_enrichment** (<code>StrictBool | None</code>) – Explicit wait option where documented; None preserves the API default.

**Returns:**

- <code>dict\[str, Any\]</code> – Complete JSON response under data, preserving objects, arrays and numbers.

#### run_async

```python
run_async(
    domains: list[str],
    *,
    filters: dict[str, Any] | None = None,
    page: StrictInt = 1,
    page_size: StrictInt = 5,
    expand: list[str] | None = None,
    wait_for_enrichment: StrictBool | None = None
) -> dict[str, Any]
```

Asynchronously call the CompanyEnrich operation once.

**Parameters:**

- **domains** (<code>list\[str\]</code>) – Seed domains (1-10) or batch domains (1-50), depending on the operation.
- **filters** (<code>dict\[str, Any\] | None</code>) – Full documented API filters; dedicated non-null fields take precedence.
- **page** (<code>StrictInt</code>) – One-based page number; page times page_size must not exceed 10,000.
- **page_size** (<code>StrictInt</code>) – Results per page from 1 to 100; defaults to 5.
- **expand** (<code>list\[str\] | None</code>) – Documented expansions: workforce for companies or education for people.
- **wait_for_enrichment** (<code>StrictBool | None</code>) – Explicit wait option where documented; None preserves the API default.

**Returns:**

- <code>dict\[str, Any\]</code> – Complete JSON response under data, preserving objects, arrays and numbers.

### CompanyEnrichPeopleSearch

Bases: <code>\_CompanyEnrichRequest</code>

Call post_people_search once and preserve the full response under data.

#### run

```python
run(
    filters: dict[str, Any],
    *,
    page: StrictInt = 1,
    page_size: StrictInt = 5,
    expand: list[str] | None = None
) -> dict[str, Any]
```

Call the CompanyEnrich operation once.

**Parameters:**

- **filters** (<code>dict\[str, Any\]</code>) – Full documented API filters; dedicated non-null fields take precedence.
- **page** (<code>StrictInt</code>) – One-based page number; page times page_size must not exceed 10,000.
- **page_size** (<code>StrictInt</code>) – Results per page from 1 to 100; defaults to 5.
- **expand** (<code>list\[str\] | None</code>) – Documented expansions: workforce for companies or education for people.

**Returns:**

- <code>dict\[str, Any\]</code> – Complete JSON response under data, preserving objects, arrays and numbers.

#### run_async

```python
run_async(
    filters: dict[str, Any],
    *,
    page: StrictInt = 1,
    page_size: StrictInt = 5,
    expand: list[str] | None = None
) -> dict[str, Any]
```

Asynchronously call the CompanyEnrich operation once.

**Parameters:**

- **filters** (<code>dict\[str, Any\]</code>) – Full documented API filters; dedicated non-null fields take precedence.
- **page** (<code>StrictInt</code>) – One-based page number; page times page_size must not exceed 10,000.
- **page_size** (<code>StrictInt</code>) – Results per page from 1 to 100; defaults to 5.
- **expand** (<code>list\[str\] | None</code>) – Documented expansions: workforce for companies or education for people.

**Returns:**

- <code>dict\[str, Any\]</code> – Complete JSON response under data, preserving objects, arrays and numbers.

### CompanyEnrichPersonLookup

Bases: <code>\_CompanyEnrichRequest</code>

Call post_people_lookup once and preserve the full response under data.

#### run

```python
run(email: str, *, expand: list[str] | None = None) -> dict[str, Any]
```

Call the CompanyEnrich operation once.

**Parameters:**

- **email** (<code>str</code>) – Nonempty email for person and company lookup.
- **expand** (<code>list\[str\] | None</code>) – Documented expansions: workforce for companies or education for people.

**Returns:**

- <code>dict\[str, Any\]</code> – Complete JSON response under data, preserving objects, arrays and numbers.

#### run_async

```python
run_async(email: str, *, expand: list[str] | None = None) -> dict[str, Any]
```

Asynchronously call the CompanyEnrich operation once.

**Parameters:**

- **email** (<code>str</code>) – Nonempty email for person and company lookup.
- **expand** (<code>list\[str\] | None</code>) – Documented expansions: workforce for companies or education for people.

**Returns:**

- <code>dict\[str, Any\]</code> – Complete JSON response under data, preserving objects, arrays and numbers.

### CompanyEnrichWorkforce

Bases: <code>\_CompanyEnrichRequest</code>

Call get_companies_workforce once and preserve the full response under data.

#### run

```python
run(
    *, company_id: str | None = None, domain: str | None = None
) -> dict[str, Any]
```

Call the CompanyEnrich operation once.

**Parameters:**

- **company_id** (<code>str | None</code>) – Company UUID; workforce requires exactly one of company_id or domain.
- **domain** (<code>str | None</code>) – Company domain; workforce requires exactly one of company_id or domain.

**Returns:**

- <code>dict\[str, Any\]</code> – Complete JSON response under data, preserving objects, arrays and numbers.

#### run_async

```python
run_async(
    *, company_id: str | None = None, domain: str | None = None
) -> dict[str, Any]
```

Asynchronously call the CompanyEnrich operation once.

**Parameters:**

- **company_id** (<code>str | None</code>) – Company UUID; workforce requires exactly one of company_id or domain.
- **domain** (<code>str | None</code>) – Company domain; workforce requires exactly one of company_id or domain.

**Returns:**

- <code>dict\[str, Any\]</code> – Complete JSON response under data, preserving objects, arrays and numbers.

### CompanyEnrichCompanyMatcher

Bases: <code>\_CompanyEnrichRequest</code>

Call post_companies_enrich once and preserve the full response under data.

#### run

```python
run(
    properties: dict[str, Any], *, expand: list[str] | None = None
) -> dict[str, Any]
```

Call the CompanyEnrich operation once.

**Parameters:**

- **properties** (<code>dict\[str, Any\]</code>) – At least one documented nonempty company name or social property.
- **expand** (<code>list\[str\] | None</code>) – Documented expansions: workforce for companies or education for people.

**Returns:**

- <code>dict\[str, Any\]</code> – Complete JSON response under data, preserving objects, arrays and numbers.

#### run_async

```python
run_async(
    properties: dict[str, Any], *, expand: list[str] | None = None
) -> dict[str, Any]
```

Asynchronously call the CompanyEnrich operation once.

**Parameters:**

- **properties** (<code>dict\[str, Any\]</code>) – At least one documented nonempty company name or social property.
- **expand** (<code>list\[str\] | None</code>) – Documented expansions: workforce for companies or education for people.

**Returns:**

- <code>dict\[str, Any\]</code> – Complete JSON response under data, preserving objects, arrays and numbers.

### CompanyEnrichBatchEnricher

Bases: <code>\_CompanyEnrichRequest</code>

Call post_companies_enrich_batch once and preserve the full response under data.

#### run

```python
run(domains: list[str], *, expand: list[str] | None = None) -> dict[str, Any]
```

Call the CompanyEnrich operation once.

**Parameters:**

- **domains** (<code>list\[str\]</code>) – Seed domains (1-10) or batch domains (1-50), depending on the operation.
- **expand** (<code>list\[str\] | None</code>) – Documented expansions: workforce for companies or education for people.

**Returns:**

- <code>dict\[str, Any\]</code> – Complete JSON response under data, preserving objects, arrays and numbers.

#### run_async

```python
run_async(
    domains: list[str], *, expand: list[str] | None = None
) -> dict[str, Any]
```

Asynchronously call the CompanyEnrich operation once.

**Parameters:**

- **domains** (<code>list\[str\]</code>) – Seed domains (1-10) or batch domains (1-50), depending on the operation.
- **expand** (<code>list\[str\] | None</code>) – Documented expansions: workforce for companies or education for people.

**Returns:**

- <code>dict\[str, Any\]</code> – Complete JSON response under data, preserving objects, arrays and numbers.

### CompanyEnrichCompanyById

Bases: <code>\_CompanyEnrichRequest</code>

Call get_companies once and preserve the full response under data.

#### run

```python
run(company_id: str, *, expand: list[str] | None = None) -> dict[str, Any]
```

Call the CompanyEnrich operation once.

**Parameters:**

- **company_id** (<code>str</code>) – Company UUID; workforce requires exactly one of company_id or domain.
- **expand** (<code>list\[str\] | None</code>) – Documented expansions: workforce for companies or education for people.

**Returns:**

- <code>dict\[str, Any\]</code> – Complete JSON response under data, preserving objects, arrays and numbers.

#### run_async

```python
run_async(
    company_id: str, *, expand: list[str] | None = None
) -> dict[str, Any]
```

Asynchronously call the CompanyEnrich operation once.

**Parameters:**

- **company_id** (<code>str</code>) – Company UUID; workforce requires exactly one of company_id or domain.
- **expand** (<code>list\[str\] | None</code>) – Documented expansions: workforce for companies or education for people.

**Returns:**

- <code>dict\[str, Any\]</code> – Complete JSON response under data, preserving objects, arrays and numbers.

### CompanyEnrichPersonById

Bases: <code>\_CompanyEnrichRequest</code>

Call get_people once and preserve the full response under data.

#### run

```python
run(
    person_id: str | StrictInt, *, expand: list[str] | None = None
) -> dict[str, Any]
```

Call the CompanyEnrich operation once.

**Parameters:**

- **person_id** (<code>str | StrictInt</code>) – Positive int64 person ID, also accepted as a decimal string.
- **expand** (<code>list\[str\] | None</code>) – Documented expansions: workforce for companies or education for people.

**Returns:**

- <code>dict\[str, Any\]</code> – Complete JSON response under data, preserving objects, arrays and numbers.

#### run_async

```python
run_async(
    person_id: str | StrictInt, *, expand: list[str] | None = None
) -> dict[str, Any]
```

Asynchronously call the CompanyEnrich operation once.

**Parameters:**

- **person_id** (<code>str | StrictInt</code>) – Positive int64 person ID, also accepted as a decimal string.
- **expand** (<code>list\[str\] | None</code>) – Documented expansions: workforce for companies or education for people.

**Returns:**

- <code>dict\[str, Any\]</code> – Complete JSON response under data, preserving objects, arrays and numbers.

### CompanyEnrichSearchCount

Bases: <code>\_CompanyEnrichRequest</code>

Call post_companies_search_count once and preserve the full response under data.

#### run

```python
run(
    semantic_query: str | None = None,
    *,
    query: str | None = None,
    filters: dict[str, Any] | None = None
) -> dict[str, Any]
```

Call the CompanyEnrich operation once.

**Parameters:**

- **semantic_query** (<code>str | None</code>) – Optional semantic company description, up to 500 characters.
- **query** (<code>str | None</code>) – Optional literal company query, up to 250 characters.
- **filters** (<code>dict\[str, Any\] | None</code>) – Full documented API filters; dedicated non-null fields take precedence.

**Returns:**

- <code>dict\[str, Any\]</code> – Complete JSON response under data, preserving objects, arrays and numbers.

#### run_async

```python
run_async(
    semantic_query: str | None = None,
    *,
    query: str | None = None,
    filters: dict[str, Any] | None = None
) -> dict[str, Any]
```

Asynchronously call the CompanyEnrich operation once.

**Parameters:**

- **semantic_query** (<code>str | None</code>) – Optional semantic company description, up to 500 characters.
- **query** (<code>str | None</code>) – Optional literal company query, up to 250 characters.
- **filters** (<code>dict\[str, Any\] | None</code>) – Full documented API filters; dedicated non-null fields take precedence.

**Returns:**

- <code>dict\[str, Any\]</code> – Complete JSON response under data, preserving objects, arrays and numbers.

### CompanyEnrichSimilarCount

Bases: <code>\_CompanyEnrichRequest</code>

Call post_companies_similar_count once and preserve the full response under data.

#### run

```python
run(
    domains: list[str],
    *,
    filters: dict[str, Any] | None = None,
    wait_for_enrichment: StrictBool | None = None
) -> dict[str, Any]
```

Call the CompanyEnrich operation once.

**Parameters:**

- **domains** (<code>list\[str\]</code>) – Seed domains (1-10) or batch domains (1-50), depending on the operation.
- **filters** (<code>dict\[str, Any\] | None</code>) – Full documented API filters; dedicated non-null fields take precedence.
- **wait_for_enrichment** (<code>StrictBool | None</code>) – Explicit wait option where documented; None preserves the API default.

**Returns:**

- <code>dict\[str, Any\]</code> – Complete JSON response under data, preserving objects, arrays and numbers.

#### run_async

```python
run_async(
    domains: list[str],
    *,
    filters: dict[str, Any] | None = None,
    wait_for_enrichment: StrictBool | None = None
) -> dict[str, Any]
```

Asynchronously call the CompanyEnrich operation once.

**Parameters:**

- **domains** (<code>list\[str\]</code>) – Seed domains (1-10) or batch domains (1-50), depending on the operation.
- **filters** (<code>dict\[str, Any\] | None</code>) – Full documented API filters; dedicated non-null fields take precedence.
- **wait_for_enrichment** (<code>StrictBool | None</code>) – Explicit wait option where documented; None preserves the API default.

**Returns:**

- <code>dict\[str, Any\]</code> – Complete JSON response under data, preserving objects, arrays and numbers.

### CompanyEnrichAdvancedRequest

Bases: <code>\_CompanyEnrichRequest</code>

Call one of 42 fixed operations; beta email calls require explicit opt-in.

#### run

```python
run(
    operation: CompanyEnrichOperation,
    *,
    body: dict[str, Any] | None = None,
    query: dict[str, Any] | None = None,
    path_parameters: dict[str, Any] | None = None,
    allow_beta: StrictBool = False
) -> dict[str, Any]
```

Execute one fixed operation without pagination, retries, polling or downloads.

**Parameters:**

- **operation** (<code>CompanyEnrichOperation</code>) – Fixed documented operation enum; excludes saved lists and /me.
- **body** (<code>dict\[str, Any\] | None</code>) – Full JSON body object; jobs require explicit count, items or domains.
- **query** (<code>dict\[str, Any\] | None</code>) – Documented query parameters; unknown fields are rejected.
- **path_parameters** (<code>dict\[str, Any\] | None</code>) – Required path values, validated and percent-encoded.
- **allow_beta** (<code>StrictBool</code>) – Explicit opt-in for the three beta email operations.

**Returns:**

- <code>dict\[str, Any\]</code> – Full JSON response under data; result URLs are not followed.

#### run_async

```python
run_async(
    operation: CompanyEnrichOperation,
    *,
    body: dict[str, Any] | None = None,
    query: dict[str, Any] | None = None,
    path_parameters: dict[str, Any] | None = None,
    allow_beta: StrictBool = False
) -> dict[str, Any]
```

Execute one fixed operation without pagination, retries, polling or downloads.

**Parameters:**

- **operation** (<code>CompanyEnrichOperation</code>) – Fixed documented operation enum; excludes saved lists and /me.
- **body** (<code>dict\[str, Any\] | None</code>) – Full JSON body object; jobs require explicit count, items or domains.
- **query** (<code>dict\[str, Any\] | None</code>) – Documented query parameters; unknown fields are rejected.
- **path_parameters** (<code>dict\[str, Any\] | None</code>) – Required path values, validated and percent-encoded.
- **allow_beta** (<code>StrictBool</code>) – Explicit opt-in for the three beta email operations.

**Returns:**

- <code>dict\[str, Any\]</code> – Full JSON response under data; result URLs are not followed.

## haystack_integrations.tools.companyenrich.tool

### CompanyEnrichCompanyEnricherTool

Bases: <code>ComponentTool</code>

Expose company domain enrichment to a Haystack Agent or ToolInvoker.

The LLM supplies the domain and optional expansion/wait settings.
The API key remains a credential reference outside the tool schema.
Results contain the full CompanyEnrich profile. Each request consumes one credit.

#### __init__

```python
__init__(
    *,
    api_key: Secret = Secret.from_env_var("COMPANYENRICH_API_KEY"),
    timeout: float = 30.0,
    max_retries: int = 0,
    name: str = "companyenrich_enrich_company",
    description: str = "Retrieve a structured company profile by domain. Consumes one CompanyEnrich credit."
) -> None
```

Initialize the tool without resolving credentials or sending requests.

**Parameters:**

- **api_key** (<code>Secret</code>) – CompanyEnrich API key, read from `COMPANYENRICH_API_KEY` by default.
- **timeout** (<code>float</code>) – Positive, finite HTTP timeout in seconds.
- **max_retries** (<code>int</code>) – Additional attempts on transient failures; each can consume credits.
- **name** (<code>str</code>) – Name exposed to the language model.
- **description** (<code>str</code>) – Description exposed to the language model.

#### to_dict

```python
to_dict() -> dict[str, Any]
```

Serialize the tool and all constructor parameters.

**Returns:**

- <code>dict\[str, Any\]</code> – Tool type and serialized initialization data.

#### from_dict

```python
from_dict(data: dict[str, Any]) -> CompanyEnrichCompanyEnricherTool
```

Deserialize a tool, including its credential reference.

**Parameters:**

- **data** (<code>dict\[str, Any\]</code>) – Serialized tool type and initialization data.

**Returns:**

- <code>CompanyEnrichCompanyEnricherTool</code> – Restored tool.

## haystack_integrations.tools.companyenrich.toolset

### CompanyEnrichToolset

Bases: <code>Toolset</code>

Thirteen discoverable tools: twelve core operations and one fixed advanced selector.

#### __init__

```python
__init__(
    *,
    api_key: Secret = Secret.from_env_var("COMPANYENRICH_API_KEY"),
    timeout: float = 30.0
) -> None
```

Create all tools without resolving credentials or making requests.

**Parameters:**

- **api_key** (<code>Secret</code>) – Credential reference; never exposed as a model input.
- **timeout** (<code>float</code>) – Positive finite HTTP timeout, default 30 seconds.

#### to_dict

```python
to_dict() -> dict[str, Any]
```

Serialize the toolset with its credential reference.

#### from_dict

```python
from_dict(data: dict[str, Any]) -> CompanyEnrichToolset
```

Restore a toolset without resolving the API key or calling the API.
