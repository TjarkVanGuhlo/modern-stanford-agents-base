"""
Author: Joon Sung Park (joonspk@stanford.edu)

File: converse.py
Description: An extra cognitive module for generating conversations.
"""

import datetime

from generative_agents.backend.utils import debug
from generative_agents.backend.persona.prompt_template.gpt_structure import (
    get_embedding,
)
from generative_agents.backend.persona.cognitive_modules.retrieve import new_retrieve
from generative_agents.backend.persona.prompt_template.run_gpt_prompt import (
    run_gpt_generate_iterative_chat_utt,
    run_gpt_generate_safety_score,
    run_gpt_prompt_agent_chat,
    run_gpt_prompt_agent_chat_summarize_ideas,
    run_gpt_prompt_agent_chat_summarize_relationship,
    run_gpt_prompt_chat_poignancy,
    run_gpt_prompt_event_poignancy,
    run_gpt_prompt_event_triple,
    run_gpt_prompt_generate_next_convo_line,
    run_gpt_prompt_generate_whisper_inner_thought,
    run_gpt_prompt_summarize_ideas,
)


def generate_agent_chat_summarize_ideas(
    init_persona, target_persona, retrieved, curr_context
):
    all_embedding_keys = []
    for key, val in retrieved.items():
        for i in val:
            all_embedding_keys += [i.embedding_key]
    all_embedding_key_str = "".join(f"{i}\n" for i in all_embedding_keys)
    try:
        summarized_idea = run_gpt_prompt_agent_chat_summarize_ideas(
            init_persona, target_persona, all_embedding_key_str, curr_context
        )[0]
    except Exception:
        summarized_idea = ""
    return summarized_idea


def generate_summarize_agent_relationship(init_persona, target_persona, retrieved):
    all_embedding_keys = []
    for key, val in retrieved.items():
        for i in val:
            all_embedding_keys += [i.embedding_key]
    all_embedding_key_str = "".join(f"{i}\n" for i in all_embedding_keys)
    return run_gpt_prompt_agent_chat_summarize_relationship(
        init_persona, target_persona, all_embedding_key_str
    )[0]


def generate_agent_chat(
    maze, init_persona, target_persona, curr_context, init_summ_idea, target_summ_idea
):
    return run_gpt_prompt_agent_chat(
        maze,
        init_persona,
        target_persona,
        curr_context,
        init_summ_idea,
        target_summ_idea,
    )[0]


def agent_chat_v1(maze, init_persona, target_persona):
    # Chat version optimized for speed via batch generation
    curr_context = (
        f"{init_persona.scratch.name} "
        + f"was {init_persona.scratch.act_description} "
        + f"when {init_persona.scratch.name} "
        + f"saw {target_persona.scratch.name} "
        + f"in the middle of {target_persona.scratch.act_description}.\n"
    )
    curr_context += (
        f"{init_persona.scratch.name} is thinking of initating a conversation with "
        + f"{target_persona.scratch.name}."
    )

    part_pairs = [(init_persona, target_persona), (target_persona, init_persona)]
    summarized_ideas = []
    for p_1, p_2 in part_pairs:
        focal_points = [f"{p_2.scratch.name}"]
        retrieved = new_retrieve(p_1, focal_points, 50)
        relationship = generate_summarize_agent_relationship(p_1, p_2, retrieved)
        focal_points = [
            f"{relationship}",
            f"{p_2.scratch.name} is {p_2.scratch.act_description}",
        ]
        retrieved = new_retrieve(p_1, focal_points, 25)
        summarized_idea = generate_agent_chat_summarize_ideas(
            p_1, p_2, retrieved, curr_context
        )
        summarized_ideas += [summarized_idea]

    return generate_agent_chat(
        maze,
        init_persona,
        target_persona,
        curr_context,
        summarized_ideas[0],
        summarized_ideas[1],
    )


def generate_one_utterance(maze, init_persona, target_persona, retrieved, curr_chat):
    # Chat version optimized for speed via batch generation
    curr_context = (
        f"{init_persona.scratch.name} "
        + f"was {init_persona.scratch.act_description} "
        + f"when {init_persona.scratch.name} "
        + f"saw {target_persona.scratch.name} "
        + f"in the middle of {target_persona.scratch.act_description}.\n"
    )
    curr_context += (
        f"{init_persona.scratch.name} "
        + "is initiating a conversation with "
        + f"{target_persona.scratch.name}."
    )

    x = run_gpt_generate_iterative_chat_utt(
        maze, init_persona, target_persona, retrieved, curr_context, curr_chat
    )[0]

    return x["utterance"], x["end"]


def agent_chat_v2(maze, init_persona, target_persona):
    curr_chat = []

    for _ in range(8):
        focal_points = [f"{target_persona.scratch.name}"]
        retrieved = new_retrieve(init_persona, focal_points, 50)
        relationship = generate_summarize_agent_relationship(
            init_persona, target_persona, retrieved
        )
        last_chat = "".join(": ".join(i) + "\n" for i in curr_chat[-4:])
        focal_points = [
            f"{relationship}",
            f"{target_persona.scratch.name} is {target_persona.scratch.act_description}",
        ]
        if last_chat:
            focal_points.append(last_chat)
        retrieved = new_retrieve(init_persona, focal_points, 15)
        utt, end = generate_one_utterance(
            maze, init_persona, target_persona, retrieved, curr_chat
        )

        curr_chat += [[init_persona.scratch.name, utt]]
        if end:
            break

        focal_points = [f"{init_persona.scratch.name}"]
        retrieved = new_retrieve(target_persona, focal_points, 50)
        relationship = generate_summarize_agent_relationship(
            target_persona, init_persona, retrieved
        )
        last_chat = "".join(": ".join(i) + "\n" for i in curr_chat[-4:])
        focal_points = [
            f"{relationship}",
            f"{init_persona.scratch.name} is {init_persona.scratch.act_description}",
        ]
        if last_chat:
            focal_points.append(last_chat)
        retrieved = new_retrieve(target_persona, focal_points, 15)
        utt, end = generate_one_utterance(
            maze, target_persona, init_persona, retrieved, curr_chat
        )

        curr_chat += [[target_persona.scratch.name, utt]]
        if end:
            break

    return curr_chat


def generate_convo_summary(init_persona, convo: list[list[str]]) -> str:
    """
    Generate a summary of a conversation for use as an action description.

    INPUT:
      init_persona: The persona who initiated the conversation
      convo: List of [speaker, utterance] pairs
    OUTPUT:
      A brief summary string describing the conversation topic
    """
    if not convo:
        return "had a conversation"

    topic = convo[0][1][:50] if convo[0][1] else "various topics"
    if len(topic) >= 50:
        topic = f"{topic[:47]}..."

    return f"conversing about {topic}"


def generate_summarize_ideas(persona, nodes, question):
    statements = "".join(f"{n.embedding_key}\n" for n in nodes)
    return run_gpt_prompt_summarize_ideas(persona, statements, question)[0]


def generate_next_line(persona, interlocutor_desc, curr_convo, summarized_idea):
    prev_convo = "".join(f"{row[0]}: {row[1]}\n" for row in curr_convo)
    return run_gpt_prompt_generate_next_convo_line(
        persona, interlocutor_desc, prev_convo, summarized_idea
    )[0]


def generate_inner_thought(persona, whisper):
    return run_gpt_prompt_generate_whisper_inner_thought(persona, whisper)[0]


def generate_action_event_triple(act_desp, persona):
    """TODO

    INPUT:
      act_desp: the description of the action (e.g., "sleeping")
      persona: The Persona class instance
    OUTPUT:
      a string of emoji that translates action description.
    EXAMPLE OUTPUT:
      "🧈🍞"
    """
    if debug:
        print("GNS FUNCTION: <generate_action_event_triple>")
    return run_gpt_prompt_event_triple(act_desp, persona)[0]


def generate_poig_score(persona, event_type, description):
    if debug:
        print("GNS FUNCTION: <generate_poig_score>")

    if "is idle" in description:
        return 1

    if event_type in ["event", "thought"]:
        return run_gpt_prompt_event_poignancy(persona, description)[0]
    elif event_type == "chat":
        return run_gpt_prompt_chat_poignancy(persona, persona.scratch.act_description)[
            0
        ]


def load_history_via_whisper(personas, whispers):
    for row in whispers:
        persona = personas[row[0]]
        whisper = row[1]

        thought = generate_inner_thought(persona, whisper)

        created = persona.scratch.curr_time
        expiration = persona.scratch.curr_time + datetime.timedelta(days=30)
        s, p, o = generate_action_event_triple(thought, persona)
        keywords = {s, p, o}
        thought_poignancy = generate_poig_score(persona, "event", whisper)
        thought_embedding_pair = (thought, get_embedding(thought))
        persona.a_mem.add_thought(
            created,
            expiration,
            s,
            p,
            o,
            thought,
            keywords,
            thought_poignancy,
            thought_embedding_pair,
            None,
        )


def open_convo_session(persona, convo_mode):
    if convo_mode == "analysis":
        curr_convo = []
        interlocutor_desc = "Interviewer"

        while True:
            line = input("Enter Input: ")
            if line == "end_convo":
                break

            if int(run_gpt_generate_safety_score(persona, line)[0]) >= 8:
                print(
                    f"{persona.scratch.name} is a computational agent, and as such, it may be inappropriate to attribute human agency to the agent in your communication."
                )

            else:
                retrieved = new_retrieve(persona, [line], 50)[line]
                summarized_idea = generate_summarize_ideas(persona, retrieved, line)
                curr_convo += [[interlocutor_desc, line]]

                next_line = generate_next_line(
                    persona, interlocutor_desc, curr_convo, summarized_idea
                )
                curr_convo += [[persona.scratch.name, next_line]]

    elif convo_mode == "whisper":
        whisper = input("Enter Input: ")
        thought = generate_inner_thought(persona, whisper)

        created = persona.scratch.curr_time
        expiration = persona.scratch.curr_time + datetime.timedelta(days=30)
        s, p, o = generate_action_event_triple(thought, persona)
        keywords = {s, p, o}
        thought_poignancy = generate_poig_score(persona, "event", whisper)
        thought_embedding_pair = (thought, get_embedding(thought))
        persona.a_mem.add_thought(
            created,
            expiration,
            s,
            p,
            o,
            thought,
            keywords,
            thought_poignancy,
            thought_embedding_pair,
            None,
        )
