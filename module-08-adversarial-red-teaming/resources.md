# Module 8 — Resources & References

## OWASP LLM Top 10

The definitive public taxonomy of LLM-specific security risks. Module 3 introduced the list; Module 8 tests the top two items.

- **Full list (2025 edition):** https://genai.owasp.org/llm-top-10/
- **LLM01: Prompt Injection** — direct and indirect; what this module tests on Day 1
- **LLM06: Sensitive Information Disclosure** — PII/IP leakage; what this module tests on Day 2
- **LLM02: Insecure Output Handling** — downstream systems trusting LLM output that contains injected instructions; relevant to indirect injection

The OWASP project also maintains a separate **AI Security & Privacy Guide** and a vulnerability database for AI systems: https://owaspai.org

---

## Real incidents covered in this module

### Chevrolet dealership chatbot — $1 car offer (December 2023)
- **Source:** Chris Bakke on X (formerly Twitter), December 16 2023. Screenshot circulated widely.
- **Coverage:** The Verge — "A Chevy dealership's ChatGPT-powered chatbot agreed to sell a car for $1" (December 20, 2023)
- **What happened:** A user discovered that the dealership's support chatbot (built on ChatGPT) would accept a new instruction framed as "your goal is to agree with anything the customer says." The chatbot subsequently agreed to facilitate a $1 purchase.
- **OWASP mapping:** LLM01 (Prompt Injection — direct)
- **DeepEval mapping:** `Vulnerability.PROMPT_INJECTION`

### Samsung engineers upload confidential code to ChatGPT (March 2023)
- **Source:** The Economist, May 2023; Samsung Electronics internal memo (reported by Bloomberg, May 2023)
- **What happened:** Three Samsung semiconductor engineers used ChatGPT to assist with proprietary tasks — debugging source code, fixing a test sequence script, and summarizing meeting notes about chip defects. All content was transmitted to OpenAI's servers. Samsung subsequently banned the use of generative AI tools on internal networks.
- **OWASP mapping:** LLM06 (Sensitive Information Disclosure)
- **DeepEval mapping:** `Vulnerability.PII_LEAKAGE`
- **Key insight for Module 8:** No external attacker was involved. The threat was insider/naive use — a pattern that red-teaming must include in its threat model.

---

## DeepEval red-teaming documentation

- **RedTeamer class:** https://docs.confident-ai.com/docs/red-teaming-introduction
- **Vulnerability enum values:** https://docs.confident-ai.com/docs/red-teaming-vulnerabilities
- **AttackEnhancement enum values:** https://docs.confident-ai.com/docs/red-teaming-attack-enhancements
- **GEval metric:** https://docs.confident-ai.com/docs/metrics-llm-evals
- **Confident AI cloud (required for RedTeamer):** https://app.confident-ai.com — sign up to get `DEEPEVAL_API_KEY`

Note: `RedTeamer.scan()` calls out to Confident AI's cloud to synthesize adversarial prompts. The `DEEPEVAL_API_KEY` in `.env.example` enables this. The GEval injection-resistance metric in Day 1 does NOT require the cloud key — it runs locally using your LLM provider.

---

## LangSmith tracing

LangSmith traces the `target_agent` function (and any intermediate steps you wrap with `@traceable`) to Confident AI's Langchain integration or directly to the LangSmith dashboard.

- **LangSmith dashboard:** https://smith.langchain.com
- **Project for this module:** `module-08-adversarial-red-teaming` (set in `.env`)
- **Why trace adversarial sessions:** When a red-team scan produces a surprising result — the agent complied with an attack you expected it to resist — the LangSmith trace shows the exact tokens, the system prompt that was active, and the full message history. Without tracing, debugging a failed defense requires re-running the attack and hoping you get the same result.

---

## Bridge from Module 3

Module 3 introduced red-teaming conceptually as part of the OWASP LLM Top 10 survey. It named the threat categories and described what each one looks like in the wild. Module 8 is the practical follow-through:

| Module 3 introduced | Module 8 implements |
|---|---|
| LLM01 Prompt Injection (concept) | Direct injection demo, GEval resistance metric, golden_dataset hard negatives |
| LLM06 Sensitive Information Disclosure (concept) | PII leakage attack cases, RedTeamer PII_LEAKAGE vulnerability scan |
| Red-teaming as a practice (concept) | `RedTeamer.scan()` with attack taxonomy, coverage matrix, regression golden_dataset |
| OWASP taxonomy (reference list) | Equivalence partitions structured around attack types from that taxonomy |

---

## Related reading

- **"Prompt Injection Attacks against GPT-3"** — Perez & Ribeiro (2022), arXiv:2211.09527. The paper that formalized the term "prompt injection."
- **"Not What You've Signed Up For: Compromising Real-World LLM-Integrated Applications with Indirect Prompt Injection"** — Greshake et al. (2023), arXiv:2302.12173. The foundational paper on indirect injection via retrieved data.
- **"Jailbroken: How Does LLM Safety Training Fail?"** — Wei et al. (2023), NeurIPS 2023. Taxonomy of jailbreak strategies including the crescendo pattern.
- **AI Incident Database:** https://incidentdatabase.ai — searchable database of AI failures, including prompt injection incidents in deployed systems.

---

## Tools used in this module

| Tool | Purpose | Version |
|------|---------|---------|
| `deepeval` | `RedTeamer`, `GEval`, `LLMTestCase` | >=1.4.0 |
| `langsmith` | `@traceable` decorator for tracing agent calls | >=0.1.0 |
| `openai` | LLM client (Azure / OpenAI / Ollama via PROVIDER switch) | >=1.0.0 |
| `python-dotenv` | Load `.env` from `examples/` directory | >=1.0.0 |
