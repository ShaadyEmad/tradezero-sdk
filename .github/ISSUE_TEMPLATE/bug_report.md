---
name: Bug Report
about: Report a bug or unexpected behaviour in tradezero-sdk
title: "[Bug] "
labels: bug
assignees: ''
---

## SDK Version

```python
import tradezero
print(tradezero.__version__)
```

<!-- paste output here -->

## Python Version

<!-- e.g., Python 3.11.9 -->

## Describe the Bug

<!-- A clear and concise description of what is wrong. -->

## Minimal Reproducible Example

```python
from tradezero import TradeZeroClient

# Replace real credentials with "xxx"
with TradeZeroClient(api_key="xxx", api_secret="xxx") as client:
    # your minimal example here
    ...
```

## Expected Behaviour

<!-- What should have happened? -->

## Actual Behaviour

<!-- What happened instead? Include the full traceback. -->

## Additional Context

<!-- Any other context, TradeZero API docs links, or related issues. -->
