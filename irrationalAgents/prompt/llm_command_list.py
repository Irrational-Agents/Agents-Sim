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
    with open(PROMPT_FILE_PATH + f'map_{type_}.txt', 'r', encoding='utf-8') as f:
        map = f.read()
    return map

@traceable(name="generate_plan")
def generate_plan(agent_name, agent_profile, current_emotion, recent_events, current_time, current_date, daily_plan=None):
    return run_prompt_task("generate_plan",
        agent_name=agent_name,
        agent_profile=agent_profile,
        current_emotion=current_emotion,
        recent_events=recent_events,
        current_time=current_time,
        current_date=current_date,
        daily_plan=daily_plan,
        _context=load_background('context'))

@traceable(name="generate_daily_plan")
def generate_daily_plan(agent_name, agent_profile, current_emotion, previous, current_date):
    return run_prompt_task("generate_daily_plan",
        agent_name=agent_name,
        agent_profile=agent_profile,
        current_emotion=current_emotion,
        previous=previous,
        current_date=current_date,
        _context=load_background('context'))

@traceable(name="generate_conversation")
def generate_conversation(agent_name, agent_profile, current_emotion, plan, recent_events, current_time, current_date):
    return run_prompt_task('generate_conversation',
        agent_name=agent_name,
        agent_profile=agent_profile,
        current_emotion=current_emotion,
        plan=plan,
        recent_events=recent_events,
        current_time=current_time,
        current_date=current_date
    )
    
@traceable(name="generate_thought")
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
    
@traceable(name="generate_move")
def generate_move(agent_name, agent_profile, current_emotion,recent_events, plan, current_time, current_date):
    return run_prompt_task('generate_move',
        agent_name=agent_name,
        agent_profile=agent_profile,
        current_emotion=current_emotion,
        plan=plan,
        recent_events=recent_events,
        current_time=current_time,
        current_date=current_date,
        _context=load_background('context')
    )
    
@traceable(name="generate_personality")
def generate_personality(traits):    
        traits_str = json.dumps(traits, indent=2) 
        return run_prompt_task('generate_personality', traits=traits_str)
        
@traceable(name="generate_short_memory")
def generate_short_memory(agent_name, current_emotion, personality_traits, relationships, past_memories):
    return run_prompt_task('generate_short_memory',
        agent_name=agent_name,
        current_emotion=current_emotion, 
        personality_traits=personality_traits,
        relationships=relationships,
        past_short_term_memories=past_memories
    )
    
@traceable(name="extract_keywords")
def extract_keywords_for_long_term_memory(description):
    return run_prompt_task('extract_keywords',
        description=description
    )
   
@traceable(name="plans_selection")
def plans_selection(plans, p_context, recent_events, biases=''):
    return run_prompt_task('plans_selection',
        plans=plans,
        biases=biases,
        events=recent_events,
        context=p_context
    )

def gpt_analyze_memory(goals, memories):
    pass