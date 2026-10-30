# SPDX-FileCopyrightText: 2026-present CompanyEnrich
#
# SPDX-License-Identifier: Apache-2.0

from typing import Any

from haystack import default_from_dict, default_to_dict
from haystack.tools import ComponentTool
from haystack.utils import Secret

from haystack_integrations.components.connectors.companyenrich import CompanyEnrichCompanyEnricher


class CompanyEnrichCompanyEnricherTool(ComponentTool):
    """
    Expose company domain enrichment to a Haystack Agent or ToolInvoker.

    The LLM supplies only the domain; the API key remains a credential reference outside the tool schema.
    Results contain the full CompanyEnrich profile. Each request consumes one credit.
    """

    def __init__(
        self,
        *,
        api_key: Secret = Secret.from_env_var("COMPANYENRICH_API_KEY"),
        timeout: float = 30.0,
        max_retries: int = 0,
        name: str = "companyenrich_enrich_company",
        description: str = "Retrieve a structured company profile by domain. Consumes one CompanyEnrich credit.",
    ) -> None:
        """
        Initialize the tool without resolving credentials or sending requests.

        :param api_key: CompanyEnrich API key, read from `COMPANYENRICH_API_KEY` by default.
        :param timeout: Positive, finite HTTP timeout in seconds.
        :param max_retries: Additional attempts on transient failures; each can consume credits.
        :param name: Name exposed to the language model.
        :param description: Description exposed to the language model.
        """
        self.api_key = api_key
        self.timeout = timeout
        self.max_retries = max_retries
        super().__init__(
            component=CompanyEnrichCompanyEnricher(api_key=api_key, timeout=timeout, max_retries=max_retries),
            name=name,
            description=description,
        )

    def to_dict(self) -> dict[str, Any]:
        """
        Serialize the tool and all constructor parameters.

        :returns: Tool type and serialized initialization data.
        """
        serialized = default_to_dict(
            self,
            api_key=self.api_key,
            timeout=self.timeout,
            max_retries=self.max_retries,
            name=self.name,
            description=self.description,
        )
        return {"type": serialized["type"], "data": serialized["init_parameters"]}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CompanyEnrichCompanyEnricherTool":
        """
        Deserialize a tool, including its credential reference.

        :param data: Serialized tool type and initialization data.
        :returns: Restored tool.
        """
        return default_from_dict(cls, {"type": data["type"], "init_parameters": dict(data["data"])})
