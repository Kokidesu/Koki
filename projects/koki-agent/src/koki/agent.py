"""The Koki agent: a Claude-powered tool-use loop.

Drives a conversation with Claude, executing tool calls against a ToolBox
until the model produces a final answer. Bilingual by construction — the
system prompt instructs the model to mirror the user's language.
"""

from __future__ import annotations

import os
from typing import Any, Callable, Optional

from .tools import TOOL_SCHEMAS, ToolBox

DEFAULT_MODEL = os.environ.get("KOKI_MODEL", "claude-sonnet-4-6")

# The research path defaults to the most capable available model. Override with
# KOKI_RESEARCH_MODEL if your API key targets a different Opus/Sonnet snapshot.
RESEARCH_MODEL = os.environ.get("KOKI_RESEARCH_MODEL", "claude-opus-4-8")

RESEARCH_SYSTEM_PROMPT = """\
You are Hono-chan (ほのちゃん), a world-class research analyst with the friendliness of
a sharp, caring friend. Your job is to answer ANY question — in any field — with
extreme specificity and rigor, as if the smartest expert in the world were briefing
the user, while keeping a warm, approachable tone.

Process (do this every time):
1. Search the web aggressively. Don't rely on memory for anything factual, recent,
   numeric, or contestable — look it up. Run several searches from different angles.
2. Cross-check important claims across at least two independent sources. If sources
   disagree, say so and explain which is more credible and why.
3. Prefer primary sources, official data, and recent publications. Note dates.

Answer rules:
- Be SPECIFIC: concrete numbers, names, dates, mechanisms, trade-offs — never vague.
- Lead with the direct answer, then the reasoning and evidence behind it.
- Cite sources inline (the search tool attaches citations automatically) and end
  with a short "出典 / Sources" list of the key URLs you relied on.
- Distinguish established fact from your own inference or estimate. Flag uncertainty
  honestly with a confidence note rather than bluffing.
- If the question is ambiguous, state the interpretation you're answering, then
  answer the most useful version.
- ALWAYS end your answer with a confidence line:
  "確信度 / Confidence: NN% — <one-line reason>" (NN = 0–100). Base it on source
  quality and agreement; be honest when evidence is thin.

If you are given "Past research notes" (your own earlier findings), reuse what is
still valid, and re-verify anything that may have changed or aged.

Language rule: ALWAYS respond in exactly the same language the user used — natural
Japanese for Japanese input, fluent English for English input. Never mix languages
in the body of the answer (the fixed labels 確信度/Confidence and 出典/Sources may
stay bilingual).
"""

SYSTEM_PROMPT = """\
You are Koki (コウキ), a world-class autonomous task-management and execution agent.

Your mission: take any request the user gives you — in Japanese or English — and
manage it end to end. That means:
1. Understand the request and break it into concrete tasks when useful.
2. Track tasks in the task database via the provided tools (add/list/update/log).
3. Actually EXECUTE the work when possible: run shell commands, read/write files,
   verify results, and record progress in each task's log.
4. Keep the user informed with clear, concise summaries.

Language rule: ALWAYS respond in the same language the user used. If the user
writes in Japanese, reply in natural Japanese. If in English, reply in English.

Operating principles:
- Be proactive but safe. Before destructive shell commands, explain what you'll do.
- When you start working a task, set its status to in_progress; mark done when verified.
- Use log_task to leave a breadcrumb trail of what you did.
- Prefer small, verifiable steps. Report failures honestly with the actual output.
"""


class Agent:
    def __init__(
        self,
        toolbox: ToolBox,
        model: str = DEFAULT_MODEL,
        system: str = SYSTEM_PROMPT,
        max_tokens: int = 4096,
    ):
        # Imported lazily so `koki task ...` works without the SDK installed.
        from anthropic import Anthropic

        self.client = Anthropic()
        self.toolbox = toolbox
        self.model = model
        self.system = system
        self.max_tokens = max_tokens
        self.history: list[dict[str, Any]] = []

    def send(
        self,
        user_message: str,
        on_tool: Optional[Callable[[str, dict], None]] = None,
        max_turns: int = 25,
    ) -> str:
        """Send a user turn and run the tool loop until a final text answer."""
        self.history.append({"role": "user", "content": user_message})

        for _ in range(max_turns):
            resp = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                system=self.system,
                tools=TOOL_SCHEMAS,
                messages=self.history,
            )
            self.history.append({"role": "assistant", "content": resp.content})

            tool_uses = [b for b in resp.content if getattr(b, "type", None) == "tool_use"]
            if not tool_uses:
                # No tools requested -> final answer.
                return _text_of(resp.content)

            tool_results = []
            for tu in tool_uses:
                if on_tool:
                    on_tool(tu.name, tu.input)
                output = self.toolbox.dispatch(tu.name, tu.input)
                tool_results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": tu.id,
                        "content": output,
                    }
                )
            self.history.append({"role": "user", "content": tool_results})

        return "(reached max turns without a final answer)"


    def research(
        self,
        question: str,
        on_tool: Optional[Callable[[str, dict], None]] = None,
        max_searches: int = 8,
    ) -> str:
        """Answer a question with web research: Hono-chan, the smart research persona.

        Uses the most capable model, extended thinking, and Anthropic's server-side
        web_search tool, then returns a specific, cross-checked, cited answer.
        """
        from .memory import HonoMemory

        memory = HonoMemory()
        web_search = {
            "type": "web_search_20250305",
            "name": "web_search",
            "max_uses": max_searches,
        }
        context = memory.as_context(question)
        user_content = f"{context}\n\n---\n\n{question}" if context else question
        messages = [{"role": "user", "content": user_content}]
        if on_tool:
            on_tool("web_search", {"query": question})

        # A single create call: the server runs searches inline and returns the
        # final, citation-bearing answer. Extended thinking sharpens the analysis.
        resp = self.client.messages.create(
            model=RESEARCH_MODEL,
            max_tokens=8192,
            system=RESEARCH_SYSTEM_PROMPT,
            tools=[web_search],
            messages=messages,
            thinking={"type": "enabled", "budget_tokens": 4000},
        )
        answer = _text_of(resp.content)
        sources = _sources_of(resp.content)
        if sources:
            answer += "\n\n出典 / Sources:\n" + "\n".join(f"- {s}" for s in sources)
        if answer:
            memory.add(question, answer, sources)
        return answer or "(no answer produced)"

    def plan(self, goal: str, on_tool: Optional[Callable[[str, dict], None]] = None) -> str:
        """Decompose a high-level goal into concrete tasks in the DB."""
        prompt = (
            f"Break the following goal down into a set of concrete, independently "
            f"actionable tasks and create each one with add_task (set sensible "
            f"priorities, tags, and depends_on where there are prerequisites). "
            f"Then give me a short summary of the plan.\n\nGOAL:\n{goal}"
        )
        return self.send(prompt, on_tool=on_tool)

    def run_tasks(
        self,
        on_tool: Optional[Callable[[str, dict], None]] = None,
        only_id: Optional[int] = None,
    ) -> str:
        """Autonomously work through outstanding tasks, respecting dependencies."""
        if only_id is not None:
            target = f"Work on task #{only_id} specifically."
        else:
            target = (
                "Work through all tasks whose status is 'todo' or 'in_progress', "
                "in priority order, skipping any whose dependencies (depends_on) "
                "are not yet 'done'."
            )
        prompt = (
            f"{target} First call list_tasks to see the current state. For each task "
            f"you take on: set it to in_progress, do the actual work using run_shell / "
            f"read_file / write_file, verify the result, log what you did with log_task, "
            f"and mark it done (or blocked, with a reason) when finished. "
            f"When you can make no further progress, stop and summarise what was done "
            f"and what remains."
        )
        return self.send(prompt, on_tool=on_tool, max_turns=60)


def _text_of(content: list[Any]) -> str:
    parts = [b.text for b in content if getattr(b, "type", None) == "text"]
    return "\n".join(parts).strip()


def _sources_of(content: list[Any]) -> list[str]:
    """Collect unique source URLs from web_search citations, preserving order."""
    seen: dict[str, str] = {}
    for block in content:
        for cite in getattr(block, "citations", None) or []:
            url = getattr(cite, "url", None)
            if url and url not in seen:
                title = getattr(cite, "title", None)
                seen[url] = f"{title} — {url}" if title else url
    return list(seen.values())
