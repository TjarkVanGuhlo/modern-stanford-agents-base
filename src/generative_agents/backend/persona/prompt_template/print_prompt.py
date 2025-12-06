"""
Author: Joon Sung Park (joonspk@stanford.edu)

File: print_prompt.py
Description: For printing prompts when the setting for verbose is set to True.
"""

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from generative_agents.backend.persona.persona import Persona

__all__ = [
    "print_run_prompts",
]

##############################################################################
#                    PERSONA Chapter 1: Prompt Structures                    #
##############################################################################


def print_run_prompts(
    prompt_template: str | None = None,
    persona: "Persona | None" = None,
    gpt_param: dict[str, Any] | None = None,
    prompt_input: str | list[str] | None = None,
    prompt: str | None = None,
    output: Any = None,
) -> None:
    print(f"=== {prompt_template}")
    print("~~~ persona    ---------------------------------------------------")
    print(persona.name if persona else "None", "\n")
    print("~~~ gpt_param ----------------------------------------------------")
    print(gpt_param, "\n")
    print("~~~ prompt_input    ----------------------------------------------")
    print(prompt_input, "\n")
    print("~~~ prompt    ----------------------------------------------------")
    print(prompt, "\n")
    print("~~~ output    ----------------------------------------------------")
    print(output, "\n")
    print("=== END ==========================================================")
    print("\n\n\n")
