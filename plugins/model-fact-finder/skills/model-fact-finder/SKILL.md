---
name: model-fact-finder
description: Use when you need to pin down the integration facts of an AI model/provider — which modalities it supports (text/image/video/vision), which parameters are tunable and exactly how each is passed (field name, allowed values, where it goes in the request body), how large its context window is, and how to authenticate. Typical uses: scoping a new model's capabilities before integrating it, or verifying that a model's params/context are configured correctly.
---

# Model Fact Finder — pin down a model's integration facts

Produce **one structured model-fact report**: which modalities the model supports, which parameters it has, how each parameter is passed, how large the context is, and how to authenticate. The report is for downstream consumers (filling config, generating integration code, etc.) — this skill only **gets the facts right**, it does not decide how they're used.

**Iron rule: NEVER answer from memory.** Model names, context windows, parameter field names, and API ids are facts that **go stale and are easy to get wrong** — you MUST first WebSearch for the provider's official API docs, WebFetch and read them, and only then conclude. Real failures from answering from memory: the model name doesn't exist at all, the id was misspelled, the context window was wrong, an unsupported parameter was treated as supported. If you can't find it, say so plainly — don't make it up.

## Verification checklist (confirm each item against official docs)

For the target model/provider, verify each item:

1. **Real model id** — the exact string the API's `model` field accepts.
   - Use the version currently in service; don't use an old version or marketing name from memory.
   - A gateway slug (OpenRouter, etc.) is **not** the native id — check the gateway's own models list (e.g. OpenRouter `/api/v1/models`); it may carry a date or a `~latest` routing alias.

2. **Supported modalities** — what input/output each supports:
   - Input: plain text? images (vision)? audio?
   - Output: text? image generation? video generation?
   - Confirm vision per model (within one provider, some support it and some don't).

3. **Context window + max output** — context window (token count) and max output tokens. Get the exact numbers from the official pricing/models docs; don't estimate.

4. **Tunable parameters — for each parameter, nail down three things**:
   - **Name + semantics**: what the parameter does.
   - **Type/values**: enum (list all legal values), number (range/minimum), boolean toggle, free text.
   - **How it's passed into the request body**: what the field name is and where it nests. Providers differ a lot; examples:
     - reasoning/thinking: OpenAI uses `reasoning_effort` (enum minimal/low/medium/high, gpt-5.5+ adds xhigh); Anthropic uses a `thinking` object (a budget token count or adaptive); DeepSeek uses a `thinking.type` toggle; OpenRouter normalizes to a unified `reasoning` object (either an effort enum or max_tokens).
     - images: the legal enum values for size/quality; how an image-to-image reference image is passed.
   - **Key: judge per model, don't generalize.** Different models from the same provider have different params (some have reasoning, some don't); if a param isn't supported, explicitly mark it "unsupported" — don't assume.
   - Look for the docs' "supported parameters" / "API reference" / "capabilities" sections; for OpenRouter check `/api/v1/models`'s `supported_parameters` (a per-model string[]).

5. **Auth + endpoint** — baseUrl, auth method (Bearer key / custom header / env var), and the page to obtain a key.

## Output format

When done, report in this structure (cite a **source link** for each item so it can be re-checked):

```
Model: <display name> (id: <real model id>)
Provider: <vendor> | Protocol: <OpenAI-compatible / Anthropic-native / …>
Modalities: input[text/image/…] output[text/image/video]
Context: <context window> | Max output: <max output>
Auth: <method> | baseUrl: <endpoint> | Get key: <link>
Parameters:
  - <name>: <type> <values/range> → request body field <field>  // <semantics/how to use>
  - <name>: unsupported
Sources: <list of official doc URLs>
```

Mark any item you couldn't confirm as "not confirmed in docs" — never fill in a guessed value.

## Don't

- ❌ Give a model name/context/parameter from memory (it goes stale and is wrong — that's the entire reason this skill exists).
- ❌ Treat a marketing name or old version as the model id; treat a gateway slug as the native id.
- ❌ Generalize "all of this vendor's models support X" — confirm per model.
- ❌ Overstep into "how to fill this into some config / which file to write" — this skill only produces the fact report; landing it is the downstream consumer's job (catalog tooling, etc.).
