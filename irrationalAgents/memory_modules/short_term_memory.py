import datetime
import json
from config.logger_config import setup_logger
from agents_modules.behavior.plan import *
from config.common_method import *

logger = setup_logger(__name__)


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

        self.memory_usage_threshold = 0.5

        if check_if_file_exists(short_memory_path):
            short_memory_load = json.load(
                open(short_memory_path, encoding='utf-8'))

            # Load data from JSON
            self.age = short_memory_load.get("age")
            self.curr_datetime = short_memory_load.get("curr_datetime")
            self.current_location = short_memory_load.get("current_location")
            self.short_term_goal_capacity = short_memory_load.get(
                "short_term_goal_capacity")
            self.short_term_goal = short_memory_load.get("short_term_goal", [])
            self.short_memory_capacity = short_memory_load.get(
                "short_memory_capacity")
            self.short_memory_for_plan = short_memory_load.get(
                "short_memory_for_plan", [])
            self.short_memory = short_memory_load.get("short_memory", [])
            self.basic_needs = short_memory_load.get("basic_needs", {})
            self.temporary_personality_changes = short_memory_load.get(
                "temporary_personality_changes", {})
            self.emotion = short_memory_load.get("emotion", {})

            # Load additional data from sample class
            if short_memory_load.get("curr_time"):
                self.curr_time = datetime.datetime.strptime(
                    short_memory_load["curr_time"], "%B %d, %Y, %H:%M:%S")
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

    def add_short_memory_4_plan(self, memory):

        self.short_memory_for_plan.extend(memory)
        # update not simply accumulate memory
        new_events_text = format_events_as_text(memory)

        if hasattr(self, 'recent_events'):
            self.recent_events += " " + new_events_text if new_events_text else ""
        else:
            self.recent_events = new_events_text
    
    def add_short_memory(self, memory):
        self.short_memory.extend(memory)
        self.recent_events = format_events_as_text(memory)
        logger.debug(f"short term memory: {self.short_memory}, recent events: {self.recent_events}")

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
                end_time = (start_time + timedelta(days=1)
                            ).replace(hour=0, minute=0)

            duration = end_time - start_time
            duration_minutes = duration.total_seconds() / 60
            intervals = math.ceil(duration_minutes / 15)

            #plan["intervals"] = intervals
            plan["intervals"] = f'{duration_minutes} minutes'


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
        
    def cleanup_short_memory(self):
        """
        If more than 80% (self.memory_usage_threshold) is used for short_memory_capacity, delete from the oldest event with moccupying == 1 until less than 80% is used.
        Default: 
            short_memory_capacity: 50
            memory_usage_threshold: 0.5
        """
        if not self.short_memory_capacity:
            return

        current_usage = len(self.short_memory) / self.short_memory_capacity

        while current_usage > self.memory_usage_threshold:
            remove_index = None
            for i, ev in enumerate(self.short_memory):
                if ev.get('moccupying', 1) == 1:
                    remove_index = i
                    break

            if remove_index is not None:
                logger.debug(
                    f"forget trivial event:{self.short_memory[remove_index]}")
                del self.short_memory[remove_index]
            else:
                break

            current_usage = len(self.short_memory) / self.short_memory_capacity

    def organize_memory(self, long_memory):
        """
        Migrate short_memory entries with moccupying ≥ 2 to LongTermMemory, and set their moccupying to 1.
        Move short-term memories with moccupying value of 2 or more into long-term memory, and reset their moccupying to 1.

        The node_type is determined by whether the portion of the description before the first ":" contains any of the following: thought, chatted, interacted, or moved.
        Use the text before the first colon in description to decide node_type, based on whether it includes one of: thought, chatted, interacted, or moved.

        If moccupying equals 3, set importance to 1.0; otherwise, set it to 0.5.
        Set importance to 1.0 if moccupying is 3; otherwise, set it to 0.5.

        Fields such as valence, arousal, S, P, O, poignancy, filling, expiration, and embedding have been removed.
        The fields valence, arousal, S, P, O, poignancy, filling, expiration, and embedding are no longer used or have been deleted.
        """

        for event in self.short_memory:
            mocc = event.get('moccupying', 1)
            if mocc >= 2:
                description = event.get('description', '')
                first_part = description.split(':', 1)[0].lower(
                ) if ':' in description else description.lower()
                logger.debug(f"first part: {first_part}, description: {description}")
                if 'thought' in first_part:
                    node_type = 'thought'
                elif 'chatted' in first_part:
                    node_type = 'chat'
                elif 'interacted' in first_part or 'moved' in first_part:
                    node_type = 'event'
                else:
                    node_type = 'event'

                importance = 1.0 if mocc == 3 else 0.5
                freshness = 1.0
                current_time = self.curr_datetime if self.curr_datetime else datetime.datetime.now()

                keywords_list = extract_keywords_for_long_term_memory(description)

                if node_type == 'thought':
                    long_memory.add_thought(
                        created=current_time,
                        description=description,
                        keywords=keywords_list,
                        importance=importance,
                        freshness=freshness,
                        moccupying=mocc
                    )
                elif node_type == 'chat':
                    long_memory.add_chat(
                        created=current_time,
                        description=description,
                        keywords=keywords_list,
                        importance=importance,
                        freshness=freshness,
                        moccupying=mocc
                    )
                else:
                    long_memory.add_event(
                        created=current_time,
                        description=description,
                        keywords=keywords_list,
                        importance=importance,
                        freshness=freshness,
                        moccupying=mocc
                    )

                event['moccupying'] = 1


def format_events_as_text(events):
    # Errors occur very frequently here.
    if not events:
        return ""

    formatted_events = []
    logger.debug(f"events: {events}")
    first_event = events[0]
    time_date = f"{first_event['time']} {first_event['date']}: "

    for event in events:
        event_text = f"{event['description']}"
        formatted_events.append(event_text)

    return time_date + " ".join(formatted_events)


def form_short_memory(agent):
    short_memory_list = generate_short_memory(agent.name, get_complex_mood(agent.short_memory.emotion_memory[-1]), agent.short_memory.personality_text, agent.relationships, agent.short_memory.short_memory_for_plan)
    if not short_memory_list:
        return []
    
    new_entries = []
    logger.info(f"short_memory_list: {short_memory_list}")
    for short_memory in short_memory_list['new_entries']:

        new_entry = {
            "time": short_memory['time'], 
            "date": short_memory['date'],
            "moccupying": short_memory['type'], 
            "description": short_memory['description']
        }
        new_entries.append(new_entry)
    if new_entries:
        agent.short_memory.emotion_memory.append(short_memory_list['new_emotion'])

    return new_entries