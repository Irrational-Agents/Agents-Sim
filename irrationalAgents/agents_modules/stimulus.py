from memory_modules.short_term_memory import *
from agents_modules.personality.emotion import *
from prompt.llm_command_list import *

def stimulus(agent, events):

    # nearby_tiles = maze.get_nearby_tiles(persona.scratch.curr_tile, persona.scratch.vision_r)
    # Get all the surrounding information from Unity here

    percept_events_set = set()
    percept_events_list = []
    

    for event in events:
        # todo: 
        # if its new day, then no events wwill be triggered
        # only need to append percept_object_list
        #description = f"Kenta Takahashi chatted with Sato Sakura:'{event}'"
        description = event
        percept_events_list.append(description)

    # form short memory and add memory to short memory stream
    agent.short_memory.add_short_memory(form_short_memory(agent, percept_events_list))
    
    # determine_thinking_system()
    return "sys1"



def incident():
    return

def form_short_memory(agent, percept_events_list):
    short_memory_list = generate_short_memory(agent.name, get_complex_mood(agent.short_memory.emotion_memory[-1]), agent.short_memory.personality_text, agent.relationships, agent.short_memory.recent_events, percept_events_list)
    agent.short_memory.emotion_memory.append(short_memory_list['new_emotion'])
    new_entries = []

    for short_memory in short_memory_list['new_entries']:

        new_entry = {
            "time": agent.short_memory.curr_time,
            "date": agent.short_memory.curr_date,
            "moccupying": short_memory['type'], 
            "description": short_memory['description'],
        }
        new_entries.append(new_entry)
    
    return new_entries


    
def retrieve(agent, perceived): 
    retrieved = dict()
    for event in perceived: 
        retrieved[event.description] = dict()
        retrieved[event.description]["curr_event"] = event
        
        relevant_events = agent.long_memory.retrieve_relevant_events(
                            event.subject, event.predicate, event.object)
        retrieved[event.description]["events"] = list(relevant_events)

        relevant_thoughts = agent.long_memory.retrieve_relevant_thoughts(
                            event.subject, event.predicate, event.object)
        retrieved[event.description]["thoughts"] = list(relevant_thoughts)
        
    return retrieved

def determine_thinking_system(intensity: int, novelty: int, time_constraint: int) -> str:
    '''
    system1_score = 0
    system2_score = 0
    
    # Emotion intensity
    if max(events) >= 7:
        system1_score += 2
    elif max(events) >= 5:
        system1_score += 1
    
    # Stimulus novelty
    if novelty > 7:
        system2_score += 2
    elif novelty > 4:
        system2_score += 1
    
    # Time constraint
    if time_constraint > 7:
        system1_score += 2
    elif time_constraint > 4:
        system1_score += 1
    
    # Cognitive load
    if cognitive_load > 7:
        system1_score += 2
    elif cognitive_load > 4:
        system1_score += 1
    
    # Past experience
    if sum(past_experiences.values()) > 10:
        system1_score += 1
    
    return "System 1" if system1_score >= system2_score else "System 2"
    '''
    return "System 1"