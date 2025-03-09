from datetime import datetime, timedelta
import math
import logging
from prompt.llm_command_list import *
from agents_modules.personality.emotion import *

logger = logging.getLogger(__name__)


def plan(agent, new_day):

    daily_plan = []
    if new_day:
        daily_plan = daily_planning(agent)
        agent.short_memory.daily_plan_req = agent.short_memory.intervals4plan(
            daily_plan)
    plan_list = create_plan(agent)
    logger.info(f"plan: {plan_list}")
    return plan_list


def daily_planning(agent):
    # Need eed to finish long_memory system
    #
    # the difference between fist day and new day is that the first day doesn't have previous,
    # the subsequent days have long_memory(previous).
    # So here I use get_summarized_latest_events, could use another retrieve method in the future
    previous = agent.long_memory.get_summarized_latest_events(0)
    return generate_daily_plan(
        agent.name, agent.formed_profile,
        get_complex_mood(agent.short_memory.emotion_memory[-1]),
        previous,
        agent.short_memory.curr_date)


def create_plan(agent):
    # GPTを使用してプランを生成
    return generate_plan(
        agent.name, agent.formed_profile,
        get_complex_mood(agent.short_memory.emotion_memory[-1]),
        agent.short_memory.recent_events,
        agent.short_memory.curr_time,
        agent.short_memory.curr_date,
        agent.short_memory.get_current_daily_plan())
