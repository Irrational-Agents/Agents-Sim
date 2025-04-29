from prompt.llm_command_list import *
from config.common_method import *
from agents_modules.personality.emotion import *
from config.logger_config import setup_logger

logger = setup_logger(__name__)

'''
Notice: 
Description format: Agent A 'action' B: detailes
'''


def action(agent, next_action):
    if not next_action:
        logger.error(f"No next action for agent {agent.name}")
        return
    action_type = next_action['action']
    description = next_action['description']

    if action_type == "think":
        return handle_think(agent, description, agent.short_memory.recent_events)
    elif action_type == "chat":
        return handle_chat(agent, description, agent.short_memory.recent_events, agent.short_memory.short_memory_for_plan[-1])
    elif action_type == "interact":
        # @TODO the description of interact is not correct, need to be revised in prompt
        return handle_interact(agent, description)
    elif action_type == "move":
        # @TODO: 需要结合计算路径 unity_modules/path_planner.py
        return handle_move(agent, description)
    else:
        return handle_unknown_action(agent, action_type, description)


def handle_think(agent, description, recent_events_text):
    thoughts = generate_thought(agent.name, agent.formed_profile, get_complex_mood(
        agent.short_memory.emotion_memory[-1]), description, recent_events_text, agent.short_memory.curr_time, agent.short_memory.curr_date)

    new_entry = {
        "time": agent.short_memory.curr_time,
        "date": agent.short_memory.curr_date,
        "moccupying": 1,
        "description": f"{agent.name} thought about: {thoughts}",
        "emotion": agent.short_memory.emotion_memory[-1],
        "basic_needs": agent.short_memory.basic_needs
    }
    agent.short_memory.add_short_memory_4_plan([new_entry])
    logger.info(f"{agent.name} thought new entry: {new_entry}")
    return f"{thoughts}"


def handle_chat(agent, description, recent_events_text):
    # advance_time, advance_date = advance_time_by_15_minutes(agent.short_memory.curr_time, agent.short_memory.curr_date)

    conv = generate_conversation(agent.name, agent.formed_profile, get_complex_mood(
        agent.short_memory.emotion_memory[-1]), description, recent_events_text, agent.short_memory.curr_time, agent.short_memory.curr_date)

    new_entry = {
        "time": agent.short_memory.curr_time,
        "date": agent.short_memory.curr_date,
        "moccupying": 1,
        "description": f"{agent.name} is chatting with {conv['person']}: {conv['description']}",
        "emotion": agent.short_memory.emotion_memory[-1],
        "basic_needs": agent.short_memory.basic_needs
    }
    agent.short_memory.add_short_memory_4_plan([new_entry])
    logger.info(f"{agent.name} chatted with {conv['person']} new entry: {new_entry}")
    return conv


def handle_interact(agent, description):
    '''
    An agent can interact with items or event.

    new_entry = {
        "time": agent.short_memory.curr_date,
        "date": agent.short_memory.curr_date,
        "moccupying": 1,
        "description": f"{agent.name} interacted with {description}",
        "emotion": {
            "type": "engaged",
            "intensity": 5
        }
    }
    '''
    interaction = generate_interaction(agent.name, agent.formed_profile, get_complex_mood(
        agent.short_memory.emotion_memory[-1]), agent.short_memory.recent_events, description, agent.short_memory.curr_time, agent.short_memory.curr_date)

    new_entry = {
        "time": agent.short_memory.curr_time,
        "date": agent.short_memory.curr_date,
        "moccupying": 1,
        "description": f"{agent.name} interacted with {interaction['item']}: {interaction['description']}",
        "emotion": agent.short_memory.emotion_memory[-1],
        "basic_needs": agent.short_memory.basic_needs
    }

    agent.short_memory.add_short_memory_4_plan([new_entry])
    logger.info(f"{agent.name} interacted with {interaction['item']}: new entry: {new_entry}")
    return f"{interaction}"


def handle_move(agent, description):
    '''
    new_entry = {
        "time": agent.short_memory.curr_date,
        "date": agent.short_memory.curr_date,
        "moccupying": 1,
        "description": f"{agent.name} moved to {description}",
        "emotion": agent.short_memory.emotion_memory[-1]
    }
    '''
    # Using LLM obtains the destination in natural language form.
    destination = generate_move(agent.name, agent.formed_profile, get_complex_mood(
        agent.short_memory.emotion_memory[-1]), agent.short_memory.recent_events, description, agent.short_memory.curr_time, agent.short_memory.curr_date)

    new_entry = {
        "time": agent.short_memory.curr_time,
        "date": agent.short_memory.curr_date,
        "moccupying": 1,
        "description": f"{agent.name} moved: {destination}",
        "emotion": agent.short_memory.emotion_memory[-1],
        "basic_needs": agent.short_memory.basic_needs
    }

    agent.short_memory.add_short_memory_4_plan([new_entry])
    logger.info(f"{agent.name} Moved to new entry: {new_entry}")
    return f"{destination}"


def handle_unknown_action(agent, action_type, description):
    new_entry = {
        "time": agent.short_memory.curr_time,
        "date": agent.short_memory.curr_date,
        "moccupying": 1,
        "description": f"{agent.name} did: {action_type} - {description}",
        "emotion": agent.short_memory.emotion_memory[-1]
    }

    agent.short_memory.add_short_memory_4_plan([new_entry])
    logger.info(f"{agent.name} Attempted unknown action: {new_entry}")
    return f"Attempted unknown action: {action_type} - {description}"
