import os
import json
from langsmith import traceable
from config.logger_config import setup_logger
from config.config import PROMPT_FILE_PATH
from prompt.prompt_runner import run_prompt_task

logger = setup_logger(__name__)

api_key = os.getenv('OPENAI_API_KEY')


def load_background(type_):
    with open(PROMPT_FILE_PATH + f'map/map_{type_}.txt', 'r', encoding='utf-8') as f:
        map = f.read()
    return map


@traceable(name='generate_plan', run_type='prompt')
def generate_plan(agent_name, agent_profile, current_emotion, recent_events, current_time, current_date, basic_needs, perception, daily_plan=None):
    return run_prompt_task("generate_plan",

                           agent_name=agent_name,
                           agent_profile=agent_profile,
                           current_emotion=current_emotion,
                           recent_events=recent_events,
                           current_time=current_time,
                           current_date=current_date,
                           daily_plan=daily_plan,
                           basic_needs=basic_needs,
                           current_perception=perception,
                           _context=load_background('overview'))


@traceable(name='generate_daily_plan', run_type='prompt')
def generate_daily_plan(agent_name, agent_profile, current_emotion, previous, current_date):
    return run_prompt_task("generate_daily_plan",
                           agent_name=agent_name,
                           agent_profile=agent_profile,
                           current_emotion=current_emotion,
                           previous=previous,
                           current_date=current_date,
                           _context=load_background('overview'))


@traceable(name='generate_conversation', run_type='prompt')
def generate_conversation(agent_name, agent_profile, current_emotion, plan, recent_events, current_time, current_date, current_perception):
    return run_prompt_task('generate_conversation',
                           agent_name=agent_name,
                           agent_profile=agent_profile,
                           current_emotion=current_emotion,
                           plan=plan,
                           recent_events=recent_events,
                           current_time=current_time,
                           current_date=current_date,
                           current_perception=current_perception
                           )


@traceable(name='generate_thought', run_type='prompt')
def generate_thought(agent_name, agent_profile, current_emotion, plan, recent_events, current_time, current_date):
    return run_prompt_task('generate_thought',

                           agent_name=agent_name,
                           agent_profile=agent_profile,
                           current_emotion=current_emotion,
                           plan=plan,
                           recent_events=recent_events,
                           current_time=current_time,
                           current_date=current_date
                           )


@traceable(name='generate_move', run_type='prompt')
def generate_move(agent_name, agent_profile, current_emotion, recent_events, plan, current_time, current_date):
    return run_prompt_task('generate_move',

                           agent_name=agent_name,
                           agent_profile=agent_profile,
                           current_emotion=current_emotion,
                           plan=plan,
                           recent_events=recent_events,
                           current_time=current_time,
                           current_date=current_date,
                           _context=load_background('spaces')
                           )


@traceable(name='generate_interaction', run_type='prompt')
def generate_interaction(agent_name, agent_profile, current_emotion, recent_events, plan, current_time, current_date, location, current_perception):
    return run_prompt_task('generate_interaction',
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


@traceable(name='generate_personality')
def generate_personality(traits):
    traits_str = json.dumps(traits, indent=2)
    return run_prompt_task('generate_personality', agent_tracer=None, traits=traits_str)


@traceable(name='generate_short_memory', run_type='prompt')
def generate_short_memory(agent_name, current_emotion, personality_traits, relationships, past_memories):
    return run_prompt_task('generate_short_memory',
                           agent_name=agent_name,
                           current_emotion=current_emotion,
                           personality_traits=personality_traits,
                           relationships=relationships,
                           past_short_term_memories=past_memories
                           )


@traceable(name='extract_keywords_for_long_term_memory', run_type='prompt')
def extract_keywords_for_long_term_memory(description):
    return run_prompt_task('extract_keywords',

                           text=description
                           )


@traceable(name='plans_selection', run_type='prompt')
def plans_selection(plans, p_context, recent_events, basic_needs, biases=''):
    return run_prompt_task('plans_selection',

                           plans=plans,
                           biases=biases,
                           events=recent_events,
                           basic_needs=basic_needs,
                           context=p_context
                           )


def gpt_analyze_memory(goals, memories):
    pass


@traceable(name='gpt_analyze_needs', run_type='prompt')
def gpt_analyze_needs(agent_name, agent_profile, current_emotion, action, description, basic_needs):
    return run_prompt_task('gpt_analyze_needs',

                           agent_name=agent_name,
                           agent_profile=agent_profile,
                           current_emotion=current_emotion,
                           action=action,
                           description=description,
                           basic_needs=basic_needs
                           )
