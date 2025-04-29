import os
from openai import OpenAI
import json
from langsmith import traceable
from langsmith.wrappers import wrap_openai
from config.logger_config import setup_logger
from config.config import PROMPT_FILE_PATH
from prompt.prompt_runner import run_prompt_task

logger = setup_logger(__name__)

api_key = os.getenv('OPENAI_API_KEY')
client = wrap_openai(OpenAI(api_key=api_key))


def load_background(type_):
    with open(PROMPT_FILE_PATH + f'map/map_{type_}.txt', 'r', encoding='utf-8') as f:
        map = f.read()
    return map


def generate_plan(tracer, agent_name, agent_profile, current_emotion, recent_events, current_time, current_date, basic_needs, perception, daily_plan=None):
    return run_prompt_task("generate_plan",
                           agent_tracer=tracer,
                           agent_name=agent_name,
                           agent_profile=agent_profile,
                           current_emotion=current_emotion,
                           recent_events=recent_events,
                           current_time=current_time,
                           current_date=current_date,
                           daily_plan=daily_plan,
                           basic_needs=basic_needs,
                           current_perception=perception
                           _context=load_background('overview'))


def generate_daily_plan(tracer, agent_name, agent_profile, current_emotion, previous, current_date):
    return run_prompt_task("generate_daily_plan",
                           agent_tracer=tracer,
                           agent_name=agent_name,
                           agent_profile=agent_profile,
                           current_emotion=current_emotion,
                           previous=previous,
                           current_date=current_date,
                           _context=load_background('overview'))


def generate_conversation(tracer, agent_name, agent_profile, current_emotion, plan, recent_events, current_time, current_date, current_perception):
    return run_prompt_task('generate_conversation',
                           agent_tracer=tracer,
                           agent_name=agent_name,
                           agent_profile=agent_profile,
                           current_emotion=current_emotion,
                           plan=plan,
                           recent_events=recent_events,
                           current_time=current_time,
                           current_date=current_date,
                           current_perception=current_perception
                           )


def generate_thought(tracer, agent_name, agent_profile, current_emotion, plan, recent_events, current_time, current_date):
    return run_prompt_task('generate_thought',
                           agent_tracer=tracer,
                           agent_name=agent_name,
                           agent_profile=agent_profile,
                           current_emotion=current_emotion,
                           plan=plan,
                           recent_events=recent_events,
                           current_time=current_time,
                           current_date=current_date
                           )


def generate_move(tracer, agent_name, agent_profile, current_emotion, recent_events, plan, current_time, current_date):
    return run_prompt_task('generate_move',
                           agent_tracer=tracer,
                           agent_name=agent_name,
                           agent_profile=agent_profile,
                           current_emotion=current_emotion,
                           plan=plan,
                           recent_events=recent_events,
                           current_time=current_time,
                           current_date=current_date,
                           _context=load_background('spaces')
                           )


def generate_interaction(tracer, agent_name, agent_profile, current_emotion, recent_events, plan, current_time, current_date, location, current_perception):
    return run_prompt_task('generate_interaction',
                           agent_tracer=tracer,
                           agent_name=agent_name,
                           agent_profile=agent_profile,
                           current_emotion=current_emotion,
                           plan=plan,
                           recent_events=recent_events,
                           current_time=current_time,
                           current_date=current_date,
                           location=location,
                           current_perception=current_perception,
                           _context=load_background('items')
                           )


def generate_personality(tracer, traits):
    traits_str = json.dumps(traits, indent=2)
    return run_prompt_task('generate_personality', agent_tracer=tracer, traits=traits_str)


def generate_short_memory(tracer, agent_name, current_emotion, personality_traits, relationships, past_memories):
    return run_prompt_task('generate_short_memory',
                           agent_tracer=tracer,
                           agent_name=agent_name,
                           current_emotion=current_emotion,
                           personality_traits=personality_traits,
                           relationships=relationships,
                           past_short_term_memories=past_memories
                           )


def extract_keywords_for_long_term_memory(tracer, description):
    return run_prompt_task('extract_keywords',
                           agent_tracer=tracer,
                           text=description
                           )


def plans_selection(tracer, plans, p_context, recent_events, basic_needs, biases=''):
    return run_prompt_task('plans_selection',
                           agent_tracer=tracer,
                           plans=plans,
                           biases=biases,
                           events=recent_events,
                           basic_needs=basic_needs,
                           context=p_context
                           )


def gpt_analyze_memory(goals, memories):
    pass


def gpt_analyze_needs(tracer, agent_name, agent_profile, current_emotion, action, description, basic_needs):
    return run_prompt_task('gpt_analyze_needs',
                           agent_tracer=tracer,
                           agent_name=agent_name,
                           agent_profile=agent_profile,
                           current_emotion=current_emotion,
                           action=action,
                           description=description,
                           basic_needs=basic_needs
                           )
