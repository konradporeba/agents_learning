# Lab notes

## Chat call

Model: `nvidia/nemotron-3.5-lightning:free`. Prompt price and completion price are both $0 per token. Temperature 0. The prompt was 40 tokens.

Reasoning tokens count toward `max_tokens`. If the model spends that whole budget thinking, the reply is empty.

Measured with `uv run labs/chat_call.py --starve` (`max_tokens` 80, reasoning left uncapped):

| Field | Value |
| --- | --- |
| `finish_reason` | `length` |
| `reasoning_tokens` | 80 |
| `completion_tokens` | 80 |
| `response` | `None` |
| `cost_usd` | 0 |

The reasoning text stopped mid-list. No answer sentence was produced. The first run, before `reasoning_tokens` was printed, had the same shape: `completion_tokens` 80 and `response: None`.

The normal call deals with that by capping reasoning at 120 tokens and setting `max_tokens` to 400, so tokens remain for the visible reply. The script also prints `finish_reason`, `reasoning_tokens`, and the reasoning text. `finish_reason: length` with `reasoning_tokens` equal to `completion_tokens` means the budget was used up before the answer. That normal call has not been re-run since the cap was added.

## Statelessness

Same model, temperature 0, reasoning capped at 120, `max_tokens` 400. Cost of each call was $0. `uv run labs/statelessness.py`.

The first call was told "the secret word is mangrove" and replied `mangrove` (35 prompt tokens).

A new call that asked for the secret word and did not include that turn replied: "I don't know, because this conversation does not contain a secret word you gave me." That call used 43 prompt tokens.

The same question, with the first user message and the assistant reply sent again, replied `mangrove`. That call used 73 prompt tokens. The model had no memory of the first call. The word came back only because the script sent the earlier messages again, and that resend is why the prompt was larger.
