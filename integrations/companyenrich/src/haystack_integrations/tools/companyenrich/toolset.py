# SPDX-FileCopyrightText: 2026-present CompanyEnrich
#
# SPDX-License-Identifier: Apache-2.0

from typing import Any

from haystack import default_from_dict, default_to_dict
from haystack.tools import ComponentTool, Tool, Toolset
from haystack.utils import Secret

from haystack_integrations.components.connectors import companyenrich
from haystack_integrations.tools.companyenrich.tool import CompanyEnrichCompanyEnricherTool


class CompanyEnrichToolset(Toolset):
    """Thirteen discoverable tools: twelve core operations and one fixed advanced selector."""

    def __init__(
        self, *, api_key: Secret = Secret.from_env_var("COMPANYENRICH_API_KEY"), timeout: float = 30.0
    ) -> None:
        """
        Create all tools without resolving credentials or making requests.

        :param api_key: Credential reference; never exposed as a model input.
        :param timeout: Positive finite HTTP timeout, default 30 seconds.
        """
        self.api_key = api_key
        self.timeout = timeout
        tools: list[Tool] = [CompanyEnrichCompanyEnricherTool(api_key=api_key, timeout=timeout)]
        tools.append(
            ComponentTool(
                component=companyenrich.CompanyEnrichCompanySearch(api_key=api_key, timeout=timeout),
                name="companyenrich_search_companies",
                description="post_companies_search; one request, may consume credits; full response.",
            )
        )
        tools.append(
            ComponentTool(
                component=companyenrich.CompanyEnrichSimilarCompanies(api_key=api_key, timeout=timeout),
                name="companyenrich_similar_companies",
                description="post_companies_similar; one request, may consume credits; full response.",
            )
        )
        tools.append(
            ComponentTool(
                component=companyenrich.CompanyEnrichPeopleSearch(api_key=api_key, timeout=timeout),
                name="companyenrich_search_people",
                description="post_people_search; one request, may consume credits; full response.",
            )
        )
        tools.append(
            ComponentTool(
                component=companyenrich.CompanyEnrichPersonLookup(api_key=api_key, timeout=timeout),
                name="companyenrich_lookup_person",
                description="post_people_lookup; one request, may consume credits; full response.",
            )
        )
        tools.append(
            ComponentTool(
                component=companyenrich.CompanyEnrichWorkforce(api_key=api_key, timeout=timeout),
                name="companyenrich_company_workforce",
                description="get_companies_workforce; one request, may consume credits; full response.",
            )
        )
        tools.append(
            ComponentTool(
                component=companyenrich.CompanyEnrichCompanyMatcher(api_key=api_key, timeout=timeout),
                name="companyenrich_match_company",
                description="post_companies_enrich; one request, may consume credits; full response.",
            )
        )
        tools.append(
            ComponentTool(
                component=companyenrich.CompanyEnrichBatchEnricher(api_key=api_key, timeout=timeout),
                name="companyenrich_enrich_batch",
                description="post_companies_enrich_batch; one request, may consume credits; full response.",
            )
        )
        tools.append(
            ComponentTool(
                component=companyenrich.CompanyEnrichCompanyById(api_key=api_key, timeout=timeout),
                name="companyenrich_company_by_id",
                description="get_companies; one request, may consume credits; full response.",
            )
        )
        tools.append(
            ComponentTool(
                component=companyenrich.CompanyEnrichPersonById(api_key=api_key, timeout=timeout),
                name="companyenrich_person_by_id",
                description="get_people; one request, may consume credits; full response.",
            )
        )
        tools.append(
            ComponentTool(
                component=companyenrich.CompanyEnrichSearchCount(api_key=api_key, timeout=timeout),
                name="companyenrich_search_count",
                description="post_companies_search_count; one request, may consume credits; full response.",
            )
        )
        tools.append(
            ComponentTool(
                component=companyenrich.CompanyEnrichSimilarCount(api_key=api_key, timeout=timeout),
                name="companyenrich_similar_count",
                description="post_companies_similar_count; one request, may consume credits; full response.",
            )
        )
        tools.append(
            ComponentTool(
                component=companyenrich.CompanyEnrichAdvancedRequest(api_key=api_key, timeout=timeout),
                name="companyenrich_advanced_request",
                description=(
                    "One of 42 fixed operations; beta email requires allow_beta. "
                    "No retries, polling or downloads. May consume credits."
                ),
            )
        )
        super().__init__(tools=tools)

    def to_dict(self) -> dict[str, Any]:
        """Serialize the toolset with its credential reference."""
        serialized = default_to_dict(self, api_key=self.api_key, timeout=self.timeout)
        return {"type": serialized["type"], "data": serialized["init_parameters"]}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CompanyEnrichToolset":
        """Restore a toolset without resolving the API key or calling the API."""
        return default_from_dict(cls, {"type": data["type"], "init_parameters": dict(data["data"])})
