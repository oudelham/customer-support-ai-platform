# Evaluation Plan

The original portfolio specification calls for RAGAS metrics, tool-call accuracy,
resolution rate, user satisfaction, load testing, and prompt regression testing.

This implementation provides the retrieval evaluation primitives and a test
foundation. The next production increment should add a fixed evaluation dataset
with expected sources and expected tool calls.

Recommended CI gates:

- unit tests pass
- retrieval precision@5 does not regress beyond a configured threshold
- no unauthorized write-tool call in safety tests
- tool-call argument validation passes
- latency p95 remains below the service SLO
- prompt changes run the regression suite
