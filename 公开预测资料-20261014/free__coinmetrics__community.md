> For the complete documentation index, see [llms.txt](https://gitbook-docs.coinmetrics.io/llms.txt). Markdown versions of documentation pages are available by appending `.md` to page URLs; this page is available as [Markdown](https://gitbook-docs.coinmetrics.io/packages/coin-metrics-community-data.md).

# Coin Metrics Community Data

{% hint style="info" %}
Available to the community under the [Creative Commons](https://creativecommons.org/licenses/by-nc/4.0/) license.
{% endhint %}

## Community Data Offering

**Coin Metrics Community Metrics**(Community [API](https://docs.coinmetrics.io/api-reference), [Data Visualization](/data-visualization.md)) is a subset of our Network Data Pro and Market Data Pro data available for free for community use.

**Atlas Community** (Community [API](https://docs.coinmetrics.io/api/v4/#tag/List-of-blockchain-entities-v2), [Atlas Explorer](https://atlas.coinmetrics.io/)) is a limited history access to our Atlas data set for free use by the community. This is available for limited assets and 30 days of history.

**Reference Rates Community** (Community [API](https://docs.coinmetrics.io/api-reference), [Data Visualization](/data-visualization.md)) provides access to all of our reference rates with a limited amount of history for our more granular resolutions. This is available and limited to the last 7 data points.

For more info on our Community terms and offerings see our [Labs](https://coinmetrics.io/cm-labs/) page.

## Community Access Limits

The Community HTTP API root endpoint URL is `https://api.coinmetrics.io/v4`. API key is not required when accessing community endpoints.

## Rate limits

The community version of API has the limit of 10 requests per 6 seconds sliding window for an IP address.


---

# Agent Instructions
This documentation is published with GitBook. GitBook is the documentation platform designed so that both humans and AI agents can read, navigate, and reason over technical content effectively. Learn more at gitbook.com.

## Querying This Documentation
If you need additional information that is not directly available in this page, you can query the documentation by asking a question.

Perform an HTTP GET request on the following URL with the `ask` and `goal` query parameters:

```
GET https://gitbook-docs.coinmetrics.io/packages/coin-metrics-community-data.md?ask=<question>&goal=<user_goal>
```

`ask` is the immediate question: it should be specific, self-contained, and written in natural language.
`goal` is what the user is ultimately trying to achieve, the reason they need the answer. Sharing it helps GitBook give you a better, more relevant answer. A goal is most helpful when it describes the outcome the user wants rather than restating the question. For example, with `ask=how do I create an API token`, a goal like `automate deployments from our CI pipeline` lets GitBook tailor the answer to that use case.

The response will contain a direct answer to the question and relevant excerpts and sources from the documentation.

Use this mechanism when the answer is not explicitly present in the current page, you need clarification or additional context, or you want to retrieve related documentation sections.
