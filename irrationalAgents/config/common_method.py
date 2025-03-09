from datetime import datetime, timedelta
import os
import json

def check_if_file_exists(curr_file): 
  try: 
    with open(curr_file) as f_analysis_file: pass
    return True
  except: 
    return False

def convert_name2id(name):
    return name.lower().replace(" ", "_")
def convert_id2name(id: str) -> str:
    return ' '.join(word.capitalize() for word in id.split('_'))

def profile_to_narrative(profile):
    narrative = []
    
    # Basic information
    name = profile.get("name", "The person")
    narrative.append(f"{name}")
    
    if "birthday" in profile:
        narrative.append(f", born on {profile['birthday']},")
    
    # Description
    if "description" in profile:
        description = " ".join(profile["description"])
        narrative.append(f" {description}")
    
    # Goals
    if "goals" in profile:
        goals = profile["goals"]
        for goal in goals:
            if "long_term" in goal:
                narrative.append(f" {name.split()[0]}'s long-term goal is to {goal['long_term'].lower()}.")
            elif "mid_term" in goal:
                mid_term_goals = goal["mid_term"]
                for mid_goal in mid_term_goals:
                    goal_desc = mid_goal.get("description", "")
                    goal_deadline = mid_goal.get("deadline", "")
                    if goal_desc:
                        narrative.append(f" As a mid-term goal, {name.split()[0]} aims to {goal_desc.lower()}")
                        if goal_deadline:
                            narrative.append(f" by {goal_deadline}.")
                        else:
                            narrative.append(".")
    
    # Important memories or additional information
    if "important_memories" in profile:
        memories = profile["important_memories"]
        for key, value in memories.items():
              narrative.append(f" {name.split()[0]}'s {key.replace('_', ' ')} is {value}.")
    
    return " ".join(narrative)


def advance_time_by_15_minutes(curr_time, curr_date):
    current_datetime = datetime.strptime(f"{curr_date} {curr_time}", "%Y-%m-%d %H:%M")
    
    advanced_datetime = current_datetime + timedelta(minutes=15)

    advanced_time = advanced_datetime.strftime("%H:%M")
    advanced_date = advanced_datetime.strftime("%Y-%m-%d")
    
    return advanced_time, advanced_date