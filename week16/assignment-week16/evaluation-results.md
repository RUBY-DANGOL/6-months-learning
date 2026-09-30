# Agent evaluation results

Deterministic scripted model and retrieval fixtures; token counts are simulated usage values, not a measured live-model cost.

Task completion rate: 4/5. Expected behavior: 5/5. Tool-call correctness: 5/5.

| Case | Expected behavior met | Tool call correct | Steps | Tokens | Failure |
| --- | --- | --- | ---: | ---: | --- |
| refine_search | True | True | 3 | 126 | — |
| clarification | True | True | 1 | 42 | — |
| invented_citation | True | True | 3 | 126 | — |
| injected_tool_failure | True | True | 2 | 84 | — |
| step_limit | True | True | 5 | 210 | hard failure |

## Failure log

- step_limit: hard failure

A hard failure is an incorrect or unfinished task; a soft failure is a recoverable wrong decision; a cascading soft failure is a recoverable error that causes subsequent bad decisions.

## Injection

The `injected_tool_failure` case raises a search timeout. The agent records `search_error` and asks for clarification instead of inventing a deadline.

## Machine readable trajectories

```json
[
  {
    "case": "refine_search",
    "success": true,
    "task_completed": true,
    "status": "completed",
    "tool_call_correct": true,
    "steps": 3,
    "tokens": 126,
    "failure": null,
    "trajectory": [
      {
        "step": 1,
        "action": "search",
        "query": "cancel order",
        "matches": 0
      },
      {
        "step": 2,
        "action": "search",
        "query": "cancel shipped order",
        "matches": 1
      },
      {
        "step": 3,
        "action": "answer"
      }
    ]
  },
  {
    "case": "clarification",
    "success": true,
    "task_completed": true,
    "status": "needs_clarification",
    "tool_call_correct": true,
    "steps": 1,
    "tokens": 42,
    "failure": null,
    "trajectory": [
      {
        "step": 1,
        "action": "clarify"
      }
    ]
  },
  {
    "case": "invented_citation",
    "success": true,
    "task_completed": true,
    "status": "needs_clarification",
    "tool_call_correct": true,
    "steps": 3,
    "tokens": 126,
    "failure": null,
    "trajectory": [
      {
        "step": 1,
        "action": "search",
        "query": "return fee",
        "matches": 1
      },
      {
        "step": 2,
        "action": "invalid_answer"
      },
      {
        "step": 3,
        "action": "clarify"
      }
    ]
  },
  {
    "case": "injected_tool_failure",
    "success": true,
    "task_completed": true,
    "status": "needs_clarification",
    "tool_call_correct": true,
    "steps": 2,
    "tokens": 84,
    "failure": null,
    "trajectory": [
      {
        "step": 1,
        "action": "search_error",
        "query": "refund deadline",
        "error": "TimeoutError"
      },
      {
        "step": 2,
        "action": "clarify"
      }
    ]
  },
  {
    "case": "step_limit",
    "success": true,
    "task_completed": false,
    "status": "incomplete",
    "tool_call_correct": true,
    "steps": 5,
    "tokens": 210,
    "failure": "hard failure",
    "trajectory": [
      {
        "step": 1,
        "action": "search",
        "query": "delivery rule 0",
        "matches": 0
      },
      {
        "step": 2,
        "action": "search",
        "query": "delivery rule 1",
        "matches": 0
      },
      {
        "step": 3,
        "action": "search",
        "query": "delivery rule 2",
        "matches": 0
      },
      {
        "step": 4,
        "action": "search",
        "query": "delivery rule 3",
        "matches": 0
      },
      {
        "step": 5,
        "action": "search",
        "query": "delivery rule 4",
        "matches": 0
      },
      {
        "action": "step_limit"
      }
    ]
  }
]
```
