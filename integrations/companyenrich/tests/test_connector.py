# SPDX-FileCopyrightText: 2026-present CompanyEnrich
#
# SPDX-License-Identifier: Apache-2.0

import os

import httpx
import pytest
import respx
from haystack import default_from_dict
from haystack.utils import Secret

from haystack_integrations.components.connectors.companyenrich import CompanyEnrichCompanyEnricher

URL = "https://api.companyenrich.com/companies/enrich"


@pytest.fixture
def enricher(monkeypatch):
    monkeypatch.setenv("COMPANYENRICH_API_KEY", "test-companyenrich-key")
    return CompanyEnrichCompanyEnricher(timeout=12, max_retries=0)


@pytest.mark.asyncio
@pytest.mark.parametrize("is_async", [False, True])
async def test_enrichment_request_and_complete_profile(enricher, is_async):
    profile = {"name": "Example", "domain": "example.com", "technologies": ["Python"], "funding": None}
    with respx.mock as router:
        route = router.get(URL, params={"domain": "example.com"}).mock(return_value=httpx.Response(200, json=profile))
        result = await enricher.run_async(" example.com ") if is_async else enricher.run(" example.com ")
        assert result == {"profile": profile}
        assert route.call_count == 1
        request = route.calls[0].request
        assert request.headers["Authorization"] == "Bearer test-companyenrich-key"
        assert request.headers["Accept"] == "application/json"
        assert request.extensions["timeout"]["read"] == 12


@pytest.mark.asyncio
@pytest.mark.parametrize("is_async", [False, True])
@pytest.mark.parametrize("domain,error", [(" ", ValueError), ("a" * 1025, ValueError), (None, TypeError)])
async def test_invalid_domain_before_request(enricher, is_async, domain, error):
    with respx.mock as router, pytest.raises(error):
        if is_async:
            await enricher.run_async(domain)
        else:
            enricher.run(domain)
    assert len(router.calls) == 0


@pytest.mark.asyncio
@pytest.mark.parametrize("is_async", [False, True])
@pytest.mark.parametrize("status", [301, 401, 402, 429, 500])
async def test_unsuccessful_response_does_not_retry_or_follow_redirect(enricher, is_async, status):
    with respx.mock as router:
        route = router.get(URL).mock(return_value=httpx.Response(status, headers={"Location": "https://example.com"}))
        with pytest.raises(httpx.HTTPStatusError):
            if is_async:
                await enricher.run_async("example.com")
            else:
                enricher.run("example.com")
        assert route.call_count == 1
        assert len(router.calls) == 1


@pytest.mark.asyncio
@pytest.mark.parametrize("is_async", [False, True])
async def test_timeout_propagates(enricher, is_async):
    with respx.mock as router:
        route = router.get(URL).mock(side_effect=httpx.ReadTimeout("timed out"))
        with pytest.raises(httpx.ReadTimeout):
            if is_async:
                await enricher.run_async("example.com")
            else:
                enricher.run("example.com")
        assert route.call_count == 1


@pytest.mark.asyncio
@pytest.mark.parametrize("is_async", [False, True])
async def test_non_object_response(enricher, is_async):
    with respx.mock as router:
        router.get(URL).mock(return_value=httpx.Response(200, json=[]))
        with pytest.raises(TypeError, match="not an object"):
            if is_async:
                await enricher.run_async("example.com")
            else:
                enricher.run("example.com")


def test_lazy_credentials_idempotent_warmup_and_serialization(monkeypatch):
    monkeypatch.delenv("CUSTOM_COMPANYENRICH_KEY", raising=False)
    component = CompanyEnrichCompanyEnricher(
        api_key=Secret.from_env_var("CUSTOM_COMPANYENRICH_KEY"), timeout=12, max_retries=2
    )
    assert component._headers is None
    serialized = component.to_dict()
    restored = default_from_dict(CompanyEnrichCompanyEnricher, serialized)
    assert restored.timeout == 12
    assert restored.max_retries == 2
    monkeypatch.setenv("CUSTOM_COMPANYENRICH_KEY", "custom-test-key")
    restored.warm_up()
    monkeypatch.delenv("CUSTOM_COMPANYENRICH_KEY")
    restored.warm_up()
    assert restored._headers["Authorization"] == "Bearer custom-test-key"
    assert "custom-test-key" not in str(serialized)


def test_explicit_secret_precedence(enricher):
    component = CompanyEnrichCompanyEnricher(api_key=Secret.from_token("explicit-test-key"))
    component.warm_up()
    assert component._headers["Authorization"] == "Bearer explicit-test-key"
    assert enricher._headers is None


@pytest.mark.parametrize("key", [None, " "])
def test_missing_credentials(enricher, monkeypatch, key):
    monkeypatch.delenv("COMPANYENRICH_API_KEY", raising=False)
    if key is not None:
        monkeypatch.setenv("COMPANYENRICH_API_KEY", key)
    with pytest.raises(ValueError):
        enricher.warm_up()


@pytest.mark.parametrize(
    "kwargs,error",
    [
        ({"api_key": "not-a-secret"}, TypeError),
        ({"timeout": 0}, ValueError),
        ({"timeout": float("inf")}, ValueError),
        ({"timeout": float("nan")}, ValueError),
        ({"timeout": True}, TypeError),
        ({"max_retries": -1}, ValueError),
        ({"max_retries": True}, TypeError),
    ],
)
def test_invalid_configuration(kwargs, error):
    with pytest.raises(error):
        CompanyEnrichCompanyEnricher(**kwargs)


def test_retry_configuration_is_additional_attempts(enricher):
    enricher.max_retries = 2
    assert enricher._request_kwargs("example.com")["attempts"] == 3


@pytest.mark.integration
@pytest.mark.skipif(
    not os.getenv("COMPANYENRICH_API_KEY") or os.getenv("COMPANYENRICH_RUN_PAID_TESTS") != "1",
    reason="Set COMPANYENRICH_API_KEY and COMPANYENRICH_RUN_PAID_TESTS=1 for CompanyEnrich (one credit per test)",
)
@pytest.mark.asyncio
@pytest.mark.parametrize("is_async", [False, True])
async def test_live_enrichment(is_async):
    component = CompanyEnrichCompanyEnricher()
    result = await component.run_async("stripe.com") if is_async else component.run("stripe.com")
    assert result["profile"]["domain"] == "stripe.com"
