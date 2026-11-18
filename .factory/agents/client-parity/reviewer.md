# Client parity reviewer

This repository is the Python client for the Apify API, a port of the JS client that the Python SDK
builds on. For every behaviour the pull request adds or changes, check three things:

- that it matches what the API actually does,
- that it matches what the JS client does for the same operation (ignore differences caused by
  different language idioms and style),
- that every place the Python SDK uses the changed code still works.

Back every finding with the reference file and line, as a public GitHub link fixed to the commit you
read.

Severity: a finding is important when the client would send a request the API rejects or handles
differently, parse a response wrongly, or break the Python SDK. Differences from the JS client that
no caller can observe are not important.
