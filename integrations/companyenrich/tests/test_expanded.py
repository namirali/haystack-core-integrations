# SPDX-FileCopyrightText: 2026-present CompanyEnrich
#
# SPDX-License-Identifier: Apache-2.0

import json
from pathlib import Path

import httpx
import pytest
import respx
from haystack import Pipeline, default_from_dict
from haystack.utils import Secret

from haystack_integrations.components.connectors import companyenrich as components
from haystack_integrations.components.connectors.companyenrich._catalog import OPERATIONS
from haystack_integrations.tools.companyenrich import CompanyEnrichToolset

CASES = json.loads(Path(__file__).with_name("companyenrich_operations.json").read_text())
CORE = [
    [
        "CompanyEnrichCompanyEnricher",
        "companyenrich_enrich_company",
        {"domain": "example.com", "expand": ["workforce"], "wait_for_enrichment": False},
        "GET",
        "/companies/enrich",
    ],
    [
        "CompanyEnrichCompanySearch",
        "companyenrich_search_companies",
        {
            "filters": {"countries": ["US"], "query": "literal", "future": {"nested": [None]}},
            "semantic_query": "software",
            "expand": ["workforce"],
        },
        "POST",
        "/companies/search",
    ],
    [
        "CompanyEnrichSimilarCompanies",
        "companyenrich_similar_companies",
        {
            "domains": ["example.com"],
            "filters": {"minScore": 0.7},
            "expand": ["workforce"],
            "wait_for_enrichment": False,
        },
        "POST",
        "/companies/similar",
    ],
    [
        "CompanyEnrichPeopleSearch",
        "companyenrich_search_people",
        {"filters": {"companyFilter": {"domains": ["example.com"]}}, "expand": ["education"]},
        "POST",
        "/people/search",
    ],
    [
        "CompanyEnrichPersonLookup",
        "companyenrich_lookup_person",
        {"email": "person@example.com", "expand": ["education"]},
        "POST",
        "/people/lookup",
    ],
    [
        "CompanyEnrichWorkforce",
        "companyenrich_company_workforce",
        {"domain": "example.com"},
        "GET",
        "/companies/workforce",
    ],
    [
        "CompanyEnrichCompanyMatcher",
        "companyenrich_match_company",
        {"properties": {"linkedinId": "123"}},
        "POST",
        "/companies/enrich",
    ],
    [
        "CompanyEnrichBatchEnricher",
        "companyenrich_enrich_batch",
        {"domains": ["example.com"]},
        "POST",
        "/companies/enrich/batch",
    ],
    [
        "CompanyEnrichCompanyById",
        "companyenrich_company_by_id",
        {"company_id": "123e4567-e89b-12d3-a456-426614174000"},
        "GET",
        "/companies",
    ],
    ["CompanyEnrichPersonById", "companyenrich_person_by_id", {"person_id": "9007199254740993"}, "GET", "/people"],
    [
        "CompanyEnrichSearchCount",
        "companyenrich_search_count",
        {"filters": {"countries": ["US"]}},
        "POST",
        "/companies/search/count",
    ],
    [
        "CompanyEnrichSimilarCount",
        "companyenrich_similar_count",
        {"domains": ["example.com"], "filters": {"minScore": 0.5}},
        "POST",
        "/companies/similar/count",
    ],
]
INVALID = [
    ("get_me", {}),
    ("post_companies_search_async", {"body": {"count": 1, "similar": {}}}),
    ("post_companies_similar_count", {"body": {"domain": "example.com"}}),
    ("post_companies_similar_count", {"body": {"domains": ["example.com"], "domain": "example.com"}}),
    ("get_companies_enrich", {"query": {"domain": "", "Authorization": "x"}}),
    ("get_companies_workforce", {"query": {}}),
    ("get_companies_workforce", {"query": {"domain": "example.com", "id": "123e4567-e89b-12d3-a456-426614174000"}}),
    ("post_companies_enrich", {"body": {}}),
    (
        "post_companies_enrich_batch",
        {
            "body": {
                "domains": [
                    "x",
                    "x",
                    "x",
                    "x",
                    "x",
                    "x",
                    "x",
                    "x",
                    "x",
                    "x",
                    "x",
                    "x",
                    "x",
                    "x",
                    "x",
                    "x",
                    "x",
                    "x",
                    "x",
                    "x",
                    "x",
                    "x",
                    "x",
                    "x",
                    "x",
                    "x",
                    "x",
                    "x",
                    "x",
                    "x",
                    "x",
                    "x",
                    "x",
                    "x",
                    "x",
                    "x",
                    "x",
                    "x",
                    "x",
                    "x",
                    "x",
                    "x",
                    "x",
                    "x",
                    "x",
                    "x",
                    "x",
                    "x",
                    "x",
                    "x",
                    "x",
                ]
            }
        },
    ),
    ("post_companies_search", {"body": {"page": True}}),
    ("post_companies_search", {"body": {"page": 1001}}),
    (
        "post_companies_search",
        {"body": {"semanticQuery": "x" * 501}},
    ),
    ("post_companies_similar", {"body": {"domains": []}}),
    ("post_people_lookup", {"body": {"email": " "}}),
    ("get_people", {"query": {"id": "9223372036854775808"}}),
    ("get_people_email", {"query": {"id": "1"}}),
    ("post_people_email_bulk", {"allow_beta": True, "body": {"items": []}}),
    ("post_companies_search_async", {"body": {}}),
    ("post_people_search_async", {"body": {"count": 50001}}),
    ("get_jobs_jobid", {"path_parameters": {"jobId": "../../me"}}),
]


@pytest.fixture
def _credentials(monkeypatch):
    monkeypatch.setenv("COMPANYENRICH_API_KEY", "test-key")


@pytest.mark.asyncio
@pytest.mark.parametrize("is_async", [False, True])
@pytest.mark.parametrize("case", CASES, ids=lambda c: c["operation"])
async def test_advanced_all_operations_once_full_json(_credentials, case, is_async):
    instance = components.CompanyEnrichAdvancedRequest()
    inputs = {k: case[k] for k in ("operation", "body", "query", "path_parameters", "allow_beta")}
    with respx.mock as router:
        route = router.route(method=case["method"], url="https://api.companyenrich.com" + case["path"]).mock(
            return_value=httpx.Response(200, json=case["result"])
        )
        result = await instance.run_async(**inputs) if is_async else instance.run(**inputs)
        assert len(router.calls) == 1
    assert result == {"data": case["result"]}
    assert route.call_count == 1
    assert route.calls[0].request.headers["Authorization"] == "Bearer test-key"


@pytest.mark.asyncio
@pytest.mark.parametrize("is_async", [False, True])
@pytest.mark.parametrize("cls,name,inputs,method,path", CORE)
async def test_core_component_and_registered_tool(_credentials, cls, name, inputs, method, path, is_async):
    value = (
        0
        if path.endswith("/count")
        else [{"future": {"value": None}}]
        if path.endswith("/batch")
        else {"future": {"value": None}}
    )
    instance = getattr(components, cls)()
    with respx.mock as router:
        route = router.route(method=method, url="https://api.companyenrich.com" + path).mock(
            return_value=httpx.Response(200, json=value)
        )
        result = await instance.run_async(**inputs) if is_async else instance.run(**inputs)
        assert result == {"profile" if cls == "CompanyEnrichCompanyEnricher" else "data": value}
        request = route.calls[-1].request
        if "filters" in inputs:
            body = json.loads(request.content)
            for key, filter_value in inputs["filters"].items():
                assert body[key] == filter_value
        if "expand" in inputs:
            assert request.url.params.get_list("expand") == inputs["expand"]
        if "wait_for_enrichment" in inputs:
            assert request.url.params["waitForEnrichment"] == "false"
        tools = {t.name: t for t in CompanyEnrichToolset()}
        assert tools[name].invoke(**inputs) == result
        assert route.call_count == 2


def test_registry_schemas_serialization_and_pipeline(_credentials):
    toolset = CompanyEnrichToolset(api_key=Secret.from_env_var("COMPANYENRICH_API_KEY"), timeout=12)
    tools = list(toolset)
    assert len(tools) == 13
    for tool in tools:
        assert "api_key" not in tool.parameters["properties"]
    advanced = next(t for t in tools if t.name == "companyenrich_advanced_request")
    assert set(advanced.parameters["properties"]["operation"]["enum"]) == set(OPERATIONS)
    serialized = toolset.to_dict()
    assert "test-key" not in str(serialized)
    restored = CompanyEnrichToolset.from_dict(serialized)
    assert restored.to_dict() == serialized
    for name in components.__all__:
        instance = getattr(components, name)(timeout=12)
        assert default_from_dict(type(instance), instance.to_dict()).to_dict() == instance.to_dict()
        pipeline = Pipeline()
        pipeline.add_component("data", instance)
        roundtrip = Pipeline.loads(pipeline.dumps())
        assert isinstance(roundtrip.get_component("data"), type(instance))


@pytest.mark.asyncio
@pytest.mark.parametrize("is_async", [False, True])
@pytest.mark.parametrize("operation,kwargs", INVALID)
async def test_invalid_before_network(_credentials, operation, kwargs, is_async):
    with respx.mock as router, pytest.raises((ValueError, TypeError)):
        instance = components.CompanyEnrichAdvancedRequest()
        if is_async:
            await instance.run_async(operation, **kwargs)
        else:
            instance.run(operation, **kwargs)
    assert not router.calls


@pytest.mark.asyncio
@pytest.mark.parametrize("is_async", [False, True])
@pytest.mark.parametrize("status", [307, 401, 402, 429, 500])
async def test_paid_failures_sanitized_no_retry_redirect_or_download(_credentials, is_async, status):
    with respx.mock as router:
        route = router.post("https://api.companyenrich.com/companies/search/async").mock(
            return_value=httpx.Response(
                status, text="test-key private upstream body", headers={"Location": "https://example.com"}
            )
        )
        instance = components.CompanyEnrichAdvancedRequest()
        with pytest.raises(httpx.HTTPStatusError) as exc:
            if is_async:
                await instance.run_async("post_companies_search_async", body={"count": 1})
            else:
                instance.run("post_companies_search_async", body={"count": 1})
        assert route.call_count == 1
        assert len(router.calls) == 1
        assert "test-key" not in str(exc.value)
        assert "private upstream body" not in str(exc.value)


@pytest.mark.asyncio
@pytest.mark.parametrize("is_async", [False, True])
async def test_async_job_urls_returned_without_download(_credentials, is_async):
    value = {"id": "123e4567-e89b-12d3-a456-426614174000", "resultUrl": "https://example.com/result", "future": None}
    with respx.mock as router:
        route = router.post("https://api.companyenrich.com/companies/search/async").mock(
            return_value=httpx.Response(200, json=value)
        )
        instance = components.CompanyEnrichAdvancedRequest()
        result = (
            await instance.run_async("post_companies_search_async", body={"count": 1})
            if is_async
            else instance.run("post_companies_search_async", body={"count": 1})
        )
        assert result == {"data": value}
        assert route.call_count == 1
        assert len(router.calls) == 1


@pytest.mark.asyncio
@pytest.mark.parametrize("is_async", [False, True])
async def test_legacy_errors_sanitize_exception_attributes(_credentials, is_async):
    with respx.mock as router:
        route = router.get("https://api.companyenrich.com/companies/enrich").mock(
            return_value=httpx.Response(429, text="test-key private response")
        )
        instance = components.CompanyEnrichCompanyEnricher()
        with pytest.raises(httpx.HTTPStatusError) as exc:
            if is_async:
                await instance.run_async("example.com")
            else:
                instance.run("example.com")
        assert route.call_count == 1
        assert "Authorization" not in exc.value.request.headers
        assert exc.value.response.content == b""
        assert "test-key" not in str(exc.value)


@pytest.mark.asyncio
@pytest.mark.parametrize("is_async", [False, True])
async def test_legacy_timeout_sanitized_without_attached_request(_credentials, is_async):
    request = httpx.Request("GET", "https://api.companyenrich.com", headers={"Authorization": "Bearer test-key"})
    with respx.mock as router:
        route = router.get("https://api.companyenrich.com/companies/enrich").mock(
            side_effect=httpx.ReadTimeout("test-key private message", request=request)
        )
        instance = components.CompanyEnrichCompanyEnricher()
        with pytest.raises(httpx.ReadTimeout) as exc:
            if is_async:
                await instance.run_async("example.com")
            else:
                instance.run("example.com")
        assert route.call_count == 1
        assert "test-key" not in str(exc.value)
        assert exc.value._request is None


@pytest.mark.asyncio
@pytest.mark.parametrize("is_async", [False, True])
@pytest.mark.parametrize(
    "name,inputs",
    [
        ("companyenrich_search_companies", {"filters": {"countries": ["US"]}, "page": True}),
        ("companyenrich_search_people", {"filters": {}, "page_size": True}),
        ("companyenrich_person_by_id", {"person_id": True}),
        (
            "companyenrich_advanced_request",
            {"operation": "get_people_email", "query": {"id": "1"}, "allow_beta": "true"},
        ),
        ("companyenrich_enrich_company", {"domain": "example.com", "wait_for_enrichment": "true"}),
    ],
)
async def test_registered_tools_reject_coerced_boolean_inputs(_credentials, is_async, name, inputs):
    tools = {tool.name: tool for tool in CompanyEnrichToolset()}
    with respx.mock as router, pytest.raises(Exception) as exc:
        if is_async:
            await tools[name].invoke_async(**inputs)
        else:
            tools[name].invoke(**inputs)
    assert "validation" in str(exc.value).lower() or "valid" in str(exc.value).lower()
    assert not router.calls
