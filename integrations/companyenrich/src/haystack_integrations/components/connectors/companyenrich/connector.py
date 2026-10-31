# SPDX-FileCopyrightText: 2026-present CompanyEnrich
#
# SPDX-License-Identifier: Apache-2.0

import math
from typing import Any, NoReturn

import httpx
from haystack import component, default_to_dict
from haystack.utils import Secret
from haystack.utils.requests_utils import async_request_with_retry, request_with_retry
from pydantic import StrictBool

from haystack_integrations.components.connectors.companyenrich._validation import prepare_request


@component
class CompanyEnrichCompanyEnricher:
    """
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
    """

    def __init__(
        self,
        *,
        api_key: Secret = Secret.from_env_var("COMPANYENRICH_API_KEY"),
        timeout: float = 30.0,
        max_retries: int = 0,
    ) -> None:
        """
        Initialize the component without resolving credentials or making network requests.

        :param api_key: CompanyEnrich API key, read from `COMPANYENRICH_API_KEY` by default.
        :param timeout: Positive, finite HTTP timeout in seconds.
        :param max_retries: Number of additional attempts on transient failures. Each can consume credits.
        :raises TypeError: The API key is not a `Secret`, or a numeric parameter has the wrong type.
        :raises ValueError: The timeout is not positive and finite, or the retry count is negative.
        """
        if not isinstance(api_key, Secret):
            message = "api_key must be a Haystack Secret"
            raise TypeError(message)
        if isinstance(timeout, bool) or not isinstance(timeout, (int, float)):
            message = "timeout must be a number"
            raise TypeError(message)
        if not math.isfinite(timeout) or timeout <= 0:
            message = "timeout must be positive and finite"
            raise ValueError(message)
        if type(max_retries) is not int:
            message = "max_retries must be an integer"
            raise TypeError(message)
        if max_retries < 0:
            message = "max_retries must be non-negative"
            raise ValueError(message)
        self.api_key = api_key
        self.timeout = timeout
        self.max_retries = max_retries
        self._headers: dict[str, str] | None = None

    def warm_up(self) -> None:
        """
        Resolve credentials once, without making a network request.

        :raises ValueError: The configured API key is missing or empty.
        """
        if self._headers is None:
            value = self.api_key.resolve_value()
            if not value or not value.strip():
                message = "A non-empty COMPANYENRICH_API_KEY is required"
                raise ValueError(message)
            self._headers = {"Authorization": f"Bearer {value.strip()}", "Accept": "application/json"}

    def to_dict(self) -> dict[str, Any]:
        """
        Serialize the component, preserving the credential reference and HTTP settings.

        :returns: Component type and serialized initialization parameters.
        """
        return default_to_dict(self, api_key=self.api_key, timeout=self.timeout, max_retries=self.max_retries)

    @component.output_types(profile=dict[str, Any])
    def run(
        self, domain: str, *, expand: list[str] | None = None, wait_for_enrichment: StrictBool | None = None
    ) -> dict[str, Any]:
        """
        Enrich one company domain.

        :param domain: Non-empty company domain, such as `stripe.com`, at most 1024 characters.
        :param expand: Optional workforce expansion.
        :param wait_for_enrichment: Explicit wait option; None preserves the API default.
        :returns: Dictionary with `profile`, containing the complete CompanyEnrich JSON object.
        :raises TypeError: The domain is not a string or the API response is not a JSON object.
        :raises ValueError: The domain is empty or too long, or credentials cannot be resolved.
        :raises httpx.HTTPStatusError: The API returns an unsuccessful HTTP status, including redirects.
        :raises httpx.RequestError: The HTTP request fails or times out.
        """
        try:
            response = request_with_retry(
                **self._request_kwargs(domain, expand=expand, wait_for_enrichment=wait_for_enrichment)
            )
        except httpx.HTTPStatusError as exc:
            self._raise_status(exc.response)
        except httpx.RequestError as exc:
            message = "CompanyEnrich request failed; check connectivity or timeout"
            raise type(exc)(message) from None
        return self._parse_response(response)

    @component.output_types(profile=dict[str, Any])
    async def run_async(
        self, domain: str, *, expand: list[str] | None = None, wait_for_enrichment: StrictBool | None = None
    ) -> dict[str, Any]:
        """
        Asynchronously enrich one company domain with native async HTTP I/O.

        :param domain: Non-empty company domain, such as `stripe.com`, at most 1024 characters.
        :param expand: Optional workforce expansion.
        :param wait_for_enrichment: Explicit wait option; None preserves the API default.
        :returns: Dictionary with `profile`, containing the complete CompanyEnrich JSON object.
        :raises TypeError: The domain is not a string or the API response is not a JSON object.
        :raises ValueError: The domain is empty or too long, or credentials cannot be resolved.
        :raises httpx.HTTPStatusError: The API returns an unsuccessful HTTP status, including redirects.
        :raises httpx.RequestError: The HTTP request fails or times out.
        """
        try:
            response = await async_request_with_retry(
                **self._request_kwargs(domain, expand=expand, wait_for_enrichment=wait_for_enrichment)
            )
        except httpx.HTTPStatusError as exc:
            self._raise_status(exc.response)
        except httpx.RequestError as exc:
            message = "CompanyEnrich request failed; check connectivity or timeout"
            raise type(exc)(message) from None
        return self._parse_response(response)

    def _request_kwargs(
        self, domain: str, *, expand: list[str] | None = None, wait_for_enrichment: StrictBool | None = None
    ) -> dict[str, Any]:
        if not isinstance(domain, str):
            message = "domain must be a string"
            raise TypeError(message)
        domain = domain.strip()
        if not domain or len(domain) > 1024:  # noqa: PLR2004
            message = "domain must contain between 1 and 1024 characters"
            raise ValueError(message)
        query: dict[str, Any] = {"domain": domain}
        if expand is not None:
            query["expand"] = expand
        if wait_for_enrichment is not None:
            query["waitForEnrichment"] = wait_for_enrichment
        _, _, query, _ = prepare_request("get_companies_enrich", query=query)
        self.warm_up()
        return {
            "attempts": self.max_retries + 1,
            "method": "GET",
            "url": "https://api.companyenrich.com/companies/enrich",
            "headers": self._headers,
            "params": query,
            "timeout": self.timeout,
            "follow_redirects": False,
        }

    @staticmethod
    def _parse_response(response: httpx.Response) -> dict[str, Any]:
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError:
            CompanyEnrichCompanyEnricher._raise_status(response)
        try:
            profile = response.json()
        except ValueError:
            message = "CompanyEnrich returned invalid JSON"
            raise ValueError(message) from None
        if not isinstance(profile, dict):
            message = "CompanyEnrich returned a JSON value that is not an object"
            raise TypeError(message)
        return {"profile": profile}

    @staticmethod
    def _raise_status(response: httpx.Response) -> NoReturn:
        message = f"CompanyEnrich returned HTTP {response.status_code}. Check credentials, credits and inputs."
        clean = httpx.Request(response.request.method, "https://api.companyenrich.com/companies/enrich")
        raise httpx.HTTPStatusError(
            message, request=clean, response=httpx.Response(response.status_code, request=clean)
        ) from None
