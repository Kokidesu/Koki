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
