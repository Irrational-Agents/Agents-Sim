import datetime
import json
import sys

from agents_modules.behavior.plan import *
sys.path.append('../../')

from config.common_method import *

class ShortTermMemory:
    def __init__(self, short_memory_path):
        # quick access. can be removed
        self.short_memory_path = short_memory_path

        self.vision_r = 4
        self.att_bandwidth = 3
        self.retention = 5
        self.recent_events = ""
        self.personality_text = ""
        self.emotion_memory = []

        # WORLD INFORMATION
        self.curr_datetime = None
        self.curr_date = None
        self.curr_time = None
        self.curr_tile = None

        # REFLECTION VARIABLES
        self.daily_reflection_time = 60 * 3
        self.daily_reflection_size = 5
        self.overlap_reflect_th = 2
        self.kw_strg_event_reflect_th = 4
        self.kw_strg_thought_reflect_th = 4
        

        # New reflection variables
        self.recency_w = 1
        self.relevance_w = 1
        self.importance_w = 1
        self.recency_decay = 0.99
        self.importance_trigger_max = 150
        self.importance_trigger_curr = self.importance_trigger_max
        self.importance_ele_n = 0 
        self.thought_count = 5

        if check_if_file_exists(short_memory_path):
            short_memory_load = json.load(open(short_memory_path, encoding='utf-8'))

            # Load data from JSON
            self.age = short_memory_load.get("age")
            self.current_status = short_memory_load.get("current_status")
            self.current_location = short_memory_load.get("current_location")
            self.short_term_goal_capacity = short_memory_load.get("short_term_goal_capacity")
            self.short_term_goal = short_memory_load.get("short_term_goal", [])
            self.short_memory_capacity = short_memory_load.get("short_memory_capacity")
            self.short_memory_for_plan = short_memory_load.get("short_memory_for_plan", [])
            self.short_memory = short_memory_load.get("short_memory", [])
            self.basic_needs = short_memory_load.get("basic_needs", {})
            self.temporary_personality_changes = short_memory_load.get("temporary_personality_changes", {})
            self.emotion = short_memory_load.get("emotion", {})

            # Load additional data from sample class
            if short_memory_load.get("curr_time"):
                self.curr_time = datetime.datetime.strptime(short_memory_load["curr_time"], "%B %d, %Y, %H:%M:%S")
            self.curr_tile = short_memory_load.get("curr_tile")
            self.daily_plan_req = short_memory_load.get("daily_plan_req")

            self.recent_events = format_events_as_text(self.short_memory)


    def save(self, out_json):
        short_memory = {
            'age': self.age,
            'current_location': self.current_location,
            'short_term_goal_capacity': self.short_term_goal_capacity,
            'short_term_goal': self.short_term_goal,
            'short_memory_capacity': self.short_memory_capacity,
            'short_memory_for_plan': self.short_memory_for_plan,
            'daily_plan_req': self.daily_plan_req,
            'short_memory': self.short_memory,
            'basic_needs': self.basic_needs,
            'temporary_personality_changes': self.temporary_personality_changes,
            'emotion': self.emotion
        }

        out_json = self.short_memory_path
    
        with open(out_json, "w", encoding='utf-8') as outfile:
            json.dump(short_memory, outfile, ensure_ascii=False, indent=2)

    def get_current_plan(self):
        if not self.curr_time:
            return None
        current_time = self.curr_time.strftime("%H:%M")
        for plan in self.short_memory_for_plan:
            if plan['time'] > current_time:
                return plan
        return None

    def add_short_memory(self, memory):

        self.short_memory.extend(memory)
        # update not simply accumulate memory
        new_events_text = format_events_as_text(memory)
    
        if hasattr(self, 'recent_events'):
            self.recent_events += " " + new_events_text if new_events_text else ""
        else:
            self.recent_events = new_events_text


    def update_basic_need(self, need, value):
        if need in self.basic_needs:
            self.basic_needs[need] = value

    def get_personality_change(self, trait):
        return self.temporary_personality_changes.get(trait, 0)

    def set_personality_change(self, trait, value):
        self.temporary_personality_changes[trait] = value

    def get_current_emotion(self):
        return self.emotion

    def get_basic_needs(self):
        return self.basic_needs
    
    def intervals4plan(self, plans):
        # calulate mocupying for each plan
        for i, plan in enumerate(plans):
            start_time = datetime.strptime(plan["time"], "%H:%M")
            
            if i < len(plans) - 1:
                end_time = datetime.strptime(plans[i + 1]["time"], "%H:%M")
            else:
                # For the last plan, set end time to next day's 00:00
                end_time = (start_time + timedelta(days=1)).replace(hour=0, minute=0)
            
            duration = end_time - start_time
            duration_minutes = duration.total_seconds() / 60
            intervals = math.ceil(duration_minutes / 15)
            
            plan["intervals"] = intervals

        return plans
    
    def get_current_daily_plan(self):
        plans = self.daily_plan_req
        current_time = datetime.strptime(self.curr_time, "%H:%M").time()
        
        for i, plan in enumerate(plans):
            plan_time = datetime.strptime(plan["time"], "%H:%M").time()
            
            if plan_time > current_time:
                return plans[i-1] if i > 0 else None
        
        return plans[-1]  # 如果当前时间晚于所有计划，返回最后一个计划
    
    def get_f_daily_schedule_index(self, advance=0):

        today_min_elapsed = 0
        today_min_elapsed += self.curr_time.hour * 60
        today_min_elapsed += self.curr_time.minute
        today_min_elapsed += advance

        x = 0
        for task, duration in self.f_daily_schedule: 
            x += duration
        x = 0
        for task, duration in self.f_daily_schedule_hourly_org: 
            x += duration

        # We then calculate the current index based on that. 
        curr_index = 0
        elapsed = 0
        for task, duration in self.f_daily_schedule: 
            elapsed += duration
        if elapsed > today_min_elapsed: 
            return curr_index
        curr_index += 1

        return curr_index
    
def format_events_as_text(events):
    # Errors occur very frequently here.
    if not events:
        return ""

    formatted_events = []
    print(events)
    first_event = events[0]
    time_date = f"{first_event['time']} {first_event['date']}: "
    
    for event in events:
        event_text = f"{event['description']}"
        formatted_events.append(event_text)
    
    return time_date + " ".join(formatted_events)