# SPDX-FileCopyrightText: 2026-present CompanyEnrich
#
# SPDX-License-Identifier: Apache-2.0

"""One-request CompanyEnrich components with full JSON results."""

from typing import Any, Literal

import httpx
from haystack import component, default_to_dict
from haystack.utils import Secret
from pydantic import StrictBool, StrictInt

from haystack_integrations.components.connectors.companyenrich._core import core_arguments
from haystack_integrations.components.connectors.companyenrich._validation import prepare_request
from haystack_integrations.components.connectors.companyenrich.connector import CompanyEnrichCompanyEnricher


class _CompanyEnrichRequest:
    def __init__(
        self, *, api_key: Secret = Secret.from_env_var("COMPANYENRICH_API_KEY"), timeout: float = 30.0
    ) -> None:
        """
        Configure one-request components without resolving credentials.

        :param api_key: Environment reference or Haystack Secret for the API key.
        :param timeout: Positive finite timeout in seconds; defaults to 30.
        """
        self._connection = CompanyEnrichCompanyEnricher(api_key=api_key, timeout=timeout, max_retries=0)
        self.api_key = api_key
        self.timeout = timeout

    def to_dict(self) -> dict[str, Any]:
        """Serialize the credential reference and timeout without resolving the secret."""
        return default_to_dict(self, api_key=self.api_key, timeout=self.timeout)

    def _kwargs(self, operation: str, values: dict[str, Any] | None = None, **advanced: Any) -> dict[str, Any]:
        if values is not None:
            body, query = core_arguments(operation, values)
            advanced = {"body": body, "query": query}
        method, path, query, body = prepare_request(operation, **advanced)
        self._connection.warm_up()
        return {
            "method": method,
            "url": "https://api.companyenrich.com" + path,
            "headers": self._connection._headers,
            "params": query or None,
            "json": body,
        }

    @staticmethod
    def _result(response: httpx.Response) -> dict[str, Any]:
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError:
            message = f"CompanyEnrich returned HTTP {response.status_code}. Check credentials, credits and inputs."
            clean = httpx.Request(response.request.method, str(response.request.url).split("?")[0])
            raise httpx.HTTPStatusError(
                message, request=clean, response=httpx.Response(response.status_code, request=clean)
            ) from None
        try:
            return {"data": response.json()}
        except ValueError:
            message = "CompanyEnrich returned invalid JSON"
            raise ValueError(message) from None

    def _execute(self, operation: str, values: dict[str, Any] | None = None, **advanced: Any) -> dict[str, Any]:
        kwargs = self._kwargs(operation, values, **advanced)
        try:
            with httpx.Client(timeout=self.timeout, follow_redirects=False) as client:
                response = client.request(**kwargs)
        except httpx.RequestError as exc:
            message = "CompanyEnrich request failed; check connectivity or timeout"
            raise type(exc)(message) from None
        return self._result(response)

    async def _execute_async(
        self, operation: str, values: dict[str, Any] | None = None, **advanced: Any
    ) -> dict[str, Any]:
        kwargs = self._kwargs(operation, values, **advanced)
        try:
            async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=False) as client:
                response = await client.request(**kwargs)
        except httpx.RequestError as exc:
            message = "CompanyEnrich request failed; check connectivity or timeout"
            raise type(exc)(message) from None
        return self._result(response)


@component
class CompanyEnrichCompanySearch(_CompanyEnrichRequest):
    """Call post_companies_search once and preserve the full response under data."""

    @component.output_types(data=Any)
    def run(
        self,
        semantic_query: str | None = None,
        *,
        query: str | None = None,
        filters: dict[str, Any] | None = None,
        page: StrictInt = 1,
        page_size: StrictInt = 5,
        expand: list[str] | None = None,
    ) -> dict[str, Any]:
        """
        Call the CompanyEnrich operation once.

        :param semantic_query: Optional semantic company description, up to 500 characters.
        :param query: Optional literal company query, up to 250 characters.
        :param filters: Full documented API filters; dedicated non-null fields take precedence.
        :param page: One-based page number; page times page_size must not exceed 10,000.
        :param page_size: Results per page from 1 to 100; defaults to 5.
        :param expand: Documented expansions: workforce for companies or education for people.
        :returns: Complete JSON response under data, preserving objects, arrays and numbers.
        """
        return self._execute(
            "post_companies_search",
            {
                "semantic_query": semantic_query,
                "query": query,
                "filters": filters,
                "page": page,
                "page_size": page_size,
                "expand": expand,
            },
        )

    @component.output_types(data=Any)
    async def run_async(
        self,
        semantic_query: str | None = None,
        *,
        query: str | None = None,
        filters: dict[str, Any] | None = None,
        page: StrictInt = 1,
        page_size: StrictInt = 5,
        expand: list[str] | None = None,
    ) -> dict[str, Any]:
        """
        Asynchronously call the CompanyEnrich operation once.

        :param semantic_query: Optional semantic company description, up to 500 characters.
        :param query: Optional literal company query, up to 250 characters.
        :param filters: Full documented API filters; dedicated non-null fields take precedence.
        :param page: One-based page number; page times page_size must not exceed 10,000.
        :param page_size: Results per page from 1 to 100; defaults to 5.
        :param expand: Documented expansions: workforce for companies or education for people.
        :returns: Complete JSON response under data, preserving objects, arrays and numbers.
        """
        return await self._execute_async(
            "post_companies_search",
            {
                "semantic_query": semantic_query,
                "query": query,
                "filters": filters,
                "page": page,
                "page_size": page_size,
                "expand": expand,
            },
        )


@component
class CompanyEnrichSimilarCompanies(_CompanyEnrichRequest):
    """Call post_companies_similar once and preserve the full response under data."""

    @component.output_types(data=Any)
    def run(
        self,
        domains: list[str],
        *,
        filters: dict[str, Any] | None = None,
        page: StrictInt = 1,
        page_size: StrictInt = 5,
        expand: list[str] | None = None,
        wait_for_enrichment: StrictBool | None = None,
    ) -> dict[str, Any]:
        """
        Call the CompanyEnrich operation once.

        :param domains: Seed domains (1-10) or batch domains (1-50), depending on the operation.
        :param filters: Full documented API filters; dedicated non-null fields take precedence.
        :param page: One-based page number; page times page_size must not exceed 10,000.
        :param page_size: Results per page from 1 to 100; defaults to 5.
        :param expand: Documented expansions: workforce for companies or education for people.
        :param wait_for_enrichment: Explicit wait option where documented; None preserves the API default.
        :returns: Complete JSON response under data, preserving objects, arrays and numbers.
        """
        return self._execute(
            "post_companies_similar",
            {
                "domains": domains,
                "filters": filters,
                "page": page,
                "page_size": page_size,
                "expand": expand,
                "wait_for_enrichment": wait_for_enrichment,
            },
        )

    @component.output_types(data=Any)
    async def run_async(
        self,
        domains: list[str],
        *,
        filters: dict[str, Any] | None = None,
        page: StrictInt = 1,
        page_size: StrictInt = 5,
        expand: list[str] | None = None,
        wait_for_enrichment: StrictBool | None = None,
    ) -> dict[str, Any]:
        """
        Asynchronously call the CompanyEnrich operation once.

        :param domains: Seed domains (1-10) or batch domains (1-50), depending on the operation.
        :param filters: Full documented API filters; dedicated non-null fields take precedence.
        :param page: One-based page number; page times page_size must not exceed 10,000.
        :param page_size: Results per page from 1 to 100; defaults to 5.
        :param expand: Documented expansions: workforce for companies or education for people.
        :param wait_for_enrichment: Explicit wait option where documented; None preserves the API default.
        :returns: Complete JSON response under data, preserving objects, arrays and numbers.
        """
        return await self._execute_async(
            "post_companies_similar",
            {
                "domains": domains,
                "filters": filters,
                "page": page,
                "page_size": page_size,
                "expand": expand,
                "wait_for_enrichment": wait_for_enrichment,
            },
        )


@component
class CompanyEnrichPeopleSearch(_CompanyEnrichRequest):
    """Call post_people_search once and preserve the full response under data."""

    @component.output_types(data=Any)
    def run(
        self, filters: dict[str, Any], *, page: StrictInt = 1, page_size: StrictInt = 5, expand: list[str] | None = None
    ) -> dict[str, Any]:
        """
        Call the CompanyEnrich operation once.

        :param filters: Full documented API filters; dedicated non-null fields take precedence.
        :param page: One-based page number; page times page_size must not exceed 10,000.
        :param page_size: Results per page from 1 to 100; defaults to 5.
        :param expand: Documented expansions: workforce for companies or education for people.
        :returns: Complete JSON response under data, preserving objects, arrays and numbers.
        """
        return self._execute(
            "post_people_search", {"filters": filters, "page": page, "page_size": page_size, "expand": expand}
        )

    @component.output_types(data=Any)
    async def run_async(
        self, filters: dict[str, Any], *, page: StrictInt = 1, page_size: StrictInt = 5, expand: list[str] | None = None
    ) -> dict[str, Any]:
        """
        Asynchronously call the CompanyEnrich operation once.

        :param filters: Full documented API filters; dedicated non-null fields take precedence.
        :param page: One-based page number; page times page_size must not exceed 10,000.
        :param page_size: Results per page from 1 to 100; defaults to 5.
        :param expand: Documented expansions: workforce for companies or education for people.
        :returns: Complete JSON response under data, preserving objects, arrays and numbers.
        """
        return await self._execute_async(
            "post_people_search", {"filters": filters, "page": page, "page_size": page_size, "expand": expand}
        )


@component
class CompanyEnrichPersonLookup(_CompanyEnrichRequest):
    """Call post_people_lookup once and preserve the full response under data."""

    @component.output_types(data=Any)
    def run(self, email: str, *, expand: list[str] | None = None) -> dict[str, Any]:
        """
        Call the CompanyEnrich operation once.

        :param email: Nonempty email for person and company lookup.
        :param expand: Documented expansions: workforce for companies or education for people.
        :returns: Complete JSON response under data, preserving objects, arrays and numbers.
        """
        return self._execute("post_people_lookup", {"email": email, "expand": expand})

    @component.output_types(data=Any)
    async def run_async(self, email: str, *, expand: list[str] | None = None) -> dict[str, Any]:
        """
        Asynchronously call the CompanyEnrich operation once.

        :param email: Nonempty email for person and company lookup.
        :param expand: Documented expansions: workforce for companies or education for people.
        :returns: Complete JSON response under data, preserving objects, arrays and numbers.
        """
        return await self._execute_async("post_people_lookup", {"email": email, "expand": expand})


@component
class CompanyEnrichWorkforce(_CompanyEnrichRequest):
    """Call get_companies_workforce once and preserve the full response under data."""

    @component.output_types(data=Any)
    def run(self, *, company_id: str | None = None, domain: str | None = None) -> dict[str, Any]:
        """
        Call the CompanyEnrich operation once.

        :param company_id: Company UUID; workforce requires exactly one of company_id or domain.
        :param domain: Company domain; workforce requires exactly one of company_id or domain.
        :returns: Complete JSON response under data, preserving objects, arrays and numbers.
        """
        return self._execute("get_companies_workforce", {"company_id": company_id, "domain": domain})

    @component.output_types(data=Any)
    async def run_async(self, *, company_id: str | None = None, domain: str | None = None) -> dict[str, Any]:
        """
        Asynchronously call the CompanyEnrich operation once.

        :param company_id: Company UUID; workforce requires exactly one of company_id or domain.
        :param domain: Company domain; workforce requires exactly one of company_id or domain.
        :returns: Complete JSON response under data, preserving objects, arrays and numbers.
        """
        return await self._execute_async("get_companies_workforce", {"company_id": company_id, "domain": domain})


@component
class CompanyEnrichCompanyMatcher(_CompanyEnrichRequest):
    """Call post_companies_enrich once and preserve the full response under data."""

    @component.output_types(data=Any)
    def run(self, properties: dict[str, Any], *, expand: list[str] | None = None) -> dict[str, Any]:
        """
        Call the CompanyEnrich operation once.

        :param properties: At least one documented nonempty company name or social property.
        :param expand: Documented expansions: workforce for companies or education for people.
        :returns: Complete JSON response under data, preserving objects, arrays and numbers.
        """
        return self._execute("post_companies_enrich", {"properties": properties, "expand": expand})

    @component.output_types(data=Any)
    async def run_async(self, properties: dict[str, Any], *, expand: list[str] | None = None) -> dict[str, Any]:
        """
        Asynchronously call the CompanyEnrich operation once.

        :param properties: At least one documented nonempty company name or social property.
        :param expand: Documented expansions: workforce for companies or education for people.
        :returns: Complete JSON response under data, preserving objects, arrays and numbers.
        """
        return await self._execute_async("post_companies_enrich", {"properties": properties, "expand": expand})


@component
class CompanyEnrichBatchEnricher(_CompanyEnrichRequest):
    """Call post_companies_enrich_batch once and preserve the full response under data."""

    @component.output_types(data=Any)
    def run(self, domains: list[str], *, expand: list[str] | None = None) -> dict[str, Any]:
        """
        Call the CompanyEnrich operation once.

        :param domains: Seed domains (1-10) or batch domains (1-50), depending on the operation.
        :param expand: Documented expansions: workforce for companies or education for people.
        :returns: Complete JSON response under data, preserving objects, arrays and numbers.
        """
        return self._execute("post_companies_enrich_batch", {"domains": domains, "expand": expand})

    @component.output_types(data=Any)
    async def run_async(self, domains: list[str], *, expand: list[str] | None = None) -> dict[str, Any]:
        """
        Asynchronously call the CompanyEnrich operation once.

        :param domains: Seed domains (1-10) or batch domains (1-50), depending on the operation.
        :param expand: Documented expansions: workforce for companies or education for people.
        :returns: Complete JSON response under data, preserving objects, arrays and numbers.
        """
        return await self._execute_async("post_companies_enrich_batch", {"domains": domains, "expand": expand})


@component
class CompanyEnrichCompanyById(_CompanyEnrichRequest):
    """Call get_companies once and preserve the full response under data."""

    @component.output_types(data=Any)
    def run(self, company_id: str, *, expand: list[str] | None = None) -> dict[str, Any]:
        """
        Call the CompanyEnrich operation once.

        :param company_id: Company UUID; workforce requires exactly one of company_id or domain.
        :param expand: Documented expansions: workforce for companies or education for people.
        :returns: Complete JSON response under data, preserving objects, arrays and numbers.
        """
        return self._execute("get_companies", {"company_id": company_id, "expand": expand})

    @component.output_types(data=Any)
    async def run_async(self, company_id: str, *, expand: list[str] | None = None) -> dict[str, Any]:
        """
        Asynchronously call the CompanyEnrich operation once.

        :param company_id: Company UUID; workforce requires exactly one of company_id or domain.
        :param expand: Documented expansions: workforce for companies or education for people.
        :returns: Complete JSON response under data, preserving objects, arrays and numbers.
        """
        return await self._execute_async("get_companies", {"company_id": company_id, "expand": expand})


@component
class CompanyEnrichPersonById(_CompanyEnrichRequest):
    """Call get_people once and preserve the full response under data."""

    @component.output_types(data=Any)
    def run(self, person_id: str | StrictInt, *, expand: list[str] | None = None) -> dict[str, Any]:
        """
        Call the CompanyEnrich operation once.

        :param person_id: Positive int64 person ID, also accepted as a decimal string.
        :param expand: Documented expansions: workforce for companies or education for people.
        :returns: Complete JSON response under data, preserving objects, arrays and numbers.
        """
        return self._execute("get_people", {"person_id": person_id, "expand": expand})

    @component.output_types(data=Any)
    async def run_async(self, person_id: str | StrictInt, *, expand: list[str] | None = None) -> dict[str, Any]:
        """
        Asynchronously call the CompanyEnrich operation once.

        :param person_id: Positive int64 person ID, also accepted as a decimal string.
        :param expand: Documented expansions: workforce for companies or education for people.
        :returns: Complete JSON response under data, preserving objects, arrays and numbers.
        """
        return await self._execute_async("get_people", {"person_id": person_id, "expand": expand})


@component
class CompanyEnrichSearchCount(_CompanyEnrichRequest):
    """Call post_companies_search_count once and preserve the full response under data."""

    @component.output_types(data=Any)
    def run(
        self, semantic_query: str | None = None, *, query: str | None = None, filters: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """
        Call the CompanyEnrich operation once.

        :param semantic_query: Optional semantic company description, up to 500 characters.
        :param query: Optional literal company query, up to 250 characters.
        :param filters: Full documented API filters; dedicated non-null fields take precedence.
        :returns: Complete JSON response under data, preserving objects, arrays and numbers.
        """
        return self._execute(
            "post_companies_search_count", {"semantic_query": semantic_query, "query": query, "filters": filters}
        )

    @component.output_types(data=Any)
    async def run_async(
        self, semantic_query: str | None = None, *, query: str | None = None, filters: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """
        Asynchronously call the CompanyEnrich operation once.

        :param semantic_query: Optional semantic company description, up to 500 characters.
        :param query: Optional literal company query, up to 250 characters.
        :param filters: Full documented API filters; dedicated non-null fields take precedence.
        :returns: Complete JSON response under data, preserving objects, arrays and numbers.
        """
        return await self._execute_async(
            "post_companies_search_count", {"semantic_query": semantic_query, "query": query, "filters": filters}
        )


@component
class CompanyEnrichSimilarCount(_CompanyEnrichRequest):
    """Call post_companies_similar_count once and preserve the full response under data."""

    @component.output_types(data=Any)
    def run(
        self,
        domains: list[str],
        *,
        filters: dict[str, Any] | None = None,
        wait_for_enrichment: StrictBool | None = None,
    ) -> dict[str, Any]:
        """
        Call the CompanyEnrich operation once.

        :param domains: Seed domains (1-10) or batch domains (1-50), depending on the operation.
        :param filters: Full documented API filters; dedicated non-null fields take precedence.
        :param wait_for_enrichment: Explicit wait option where documented; None preserves the API default.
        :returns: Complete JSON response under data, preserving objects, arrays and numbers.
        """
        return self._execute(
            "post_companies_similar_count",
            {"domains": domains, "filters": filters, "wait_for_enrichment": wait_for_enrichment},
        )

    @component.output_types(data=Any)
    async def run_async(
        self,
        domains: list[str],
        *,
        filters: dict[str, Any] | None = None,
        wait_for_enrichment: StrictBool | None = None,
    ) -> dict[str, Any]:
        """
        Asynchronously call the CompanyEnrich operation once.

        :param domains: Seed domains (1-10) or batch domains (1-50), depending on the operation.
        :param filters: Full documented API filters; dedicated non-null fields take precedence.
        :param wait_for_enrichment: Explicit wait option where documented; None preserves the API default.
        :returns: Complete JSON response under data, preserving objects, arrays and numbers.
        """
        return await self._execute_async(
            "post_companies_similar_count",
            {"domains": domains, "filters": filters, "wait_for_enrichment": wait_for_enrichment},
        )


CompanyEnrichOperation = Literal[
    "get_companies_enrich",
    "post_companies_enrich",
    "post_companies_enrich_batch",
    "get_companies_workforce",
    "get_companies_autocomplete",
    "post_companies_enrich_bulk",
    "get_companies_enrich_bulk_jobid",
    "get_companies_enrich_bulk_jobs",
    "post_companies_search",
    "post_companies_search_preview",
    "post_companies_search_count",
    "post_companies_search_scroll",
    "get_companies",
    "post_companies_search_async",
    "get_companies_search_async_jobid",
    "get_companies_search_async_jobs",
    "post_companies_similar",
    "post_companies_similar_preview",
    "post_companies_similar_count",
    "post_companies_similar_scroll",
    "post_people_lookup",
    "get_people",
    "post_people_search",
    "post_people_search_scroll",
    "get_people_email",
    "post_people_email_bulk",
    "get_people_email_bulk_jobid",
    "get_people_education",
    "post_people_search_async",
    "get_people_search_async_jobid",
    "get_people_search_async_jobs",
    "get_jobs",
    "get_jobs_jobid",
    "get_geo_regions",
    "get_geo_countries_countrycode",
    "post_geo_countries",
    "post_geo_states",
    "post_geo_cities",
    "get_industries",
    "get_keywords_autocomplete",
    "get_technologies_autocomplete",
    "get_positions_autocomplete",
]


@component
class CompanyEnrichAdvancedRequest(_CompanyEnrichRequest):
    """Call one of 42 fixed operations; beta email calls require explicit opt-in."""

    @component.output_types(data=Any)
    def run(
        self,
        operation: CompanyEnrichOperation,
        *,
        body: dict[str, Any] | None = None,
        query: dict[str, Any] | None = None,
        path_parameters: dict[str, Any] | None = None,
        allow_beta: StrictBool = False,
    ) -> dict[str, Any]:
        """
        Execute one fixed operation without pagination, retries, polling or downloads.

        :param operation: Fixed documented operation enum; excludes saved lists and /me.
        :param body: Full JSON body object; jobs require explicit count, items or domains.
        :param query: Documented query parameters; unknown fields are rejected.
        :param path_parameters: Required path values, validated and percent-encoded.
        :param allow_beta: Explicit opt-in for the three beta email operations.
        :returns: Full JSON response under data; result URLs are not followed.
        """
        return self._execute(operation, body=body, query=query, path_parameters=path_parameters, allow_beta=allow_beta)

    @component.output_types(data=Any)
    async def run_async(
        self,
        operation: CompanyEnrichOperation,
        *,
        body: dict[str, Any] | None = None,
        query: dict[str, Any] | None = None,
        path_parameters: dict[str, Any] | None = None,
        allow_beta: StrictBool = False,
    ) -> dict[str, Any]:
        """
        Execute one fixed operation without pagination, retries, polling or downloads.

        :param operation: Fixed documented operation enum; excludes saved lists and /me.
        :param body: Full JSON body object; jobs require explicit count, items or domains.
        :param query: Documented query parameters; unknown fields are rejected.
        :param path_parameters: Required path values, validated and percent-encoded.
        :param allow_beta: Explicit opt-in for the three beta email operations.
        :returns: Full JSON response under data; result URLs are not followed.
        """
        return await self._execute_async(
            operation, body=body, query=query, path_parameters=path_parameters, allow_beta=allow_beta
        )
