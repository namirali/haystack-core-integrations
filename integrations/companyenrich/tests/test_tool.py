# SPDX-FileCopyrightText: 2026-present CompanyEnrich
#
# SPDX-License-Identifier: Apache-2.0

import httpx
import respx
from haystack.utils import Secret

from haystack_integrations.tools.companyenrich import CompanyEnrichCompanyEnricherTool


def test_tool_schema_invocation_and_roundtrip(monkeypatch):
    monkeypatch.setenv("CUSTOM_COMPANYENRICH_KEY", "test-companyenrich-key")
    tool = CompanyEnrichCompanyEnricherTool(
        api_key=Secret.from_env_var("CUSTOM_COMPANYENRICH_KEY"),
        timeout=12,
        max_retries=2,
        name="enrich_account",
        description="Enrich a customer domain",
    )
    assert set(tool.parameters["properties"]) == {"domain", "expand", "wait_for_enrichment"}
    assert tool.parameters["required"] == ["domain"]
    serialized = tool.to_dict()
    assert "test-companyenrich-key" not in str(serialized)
    restored = CompanyEnrichCompanyEnricherTool.from_dict(serialized)
    assert restored.to_dict() == serialized
    with respx.mock as router:
        route = router.get("https://api.companyenrich.com/companies/enrich").mock(
            return_value=httpx.Response(200, json={"name": "Example", "domain": "example.com"})
        )
        assert restored.invoke(domain="example.com") == {"profile": {"name": "Example", "domain": "example.com"}}
        assert route.calls[0].request.headers["Authorization"] == "Bearer test-companyenrich-key"
