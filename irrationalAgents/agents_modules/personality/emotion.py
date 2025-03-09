from config import *
import logging
logger = logging.getLogger(__name__)

def emotion(self):
    self.current_state = {emotion: 0 for emotion in EMOTION_TYPES}
    self.mood = "neutral"
    return "OK"


def normalize_values():
    global emotion_values
    total = sum(emotion_values)
    if total == 0:
        emotion_values = [10 // len(EMOTION_TYPES)] * len(EMOTION_TYPES)
        emotion_values[0] += 10 % len(EMOTION_TYPES)
    else:
        emotion_values = [int(v * 10 / total) for v in emotion_values]
        while sum(emotion_values) < 10:
            emotion_values[emotion_values.index(min(emotion_values))] += 1

def update_emotion(emotion, value):
    if emotion not in EMOTION_TYPES:
        raise ValueError(f"Invalid emotion: {emotion}")
    index = EMOTION_TYPES.index(emotion)
    emotion_values[index] = value
    normalize_values()

def get_emotion_levels(emotion):
    return dict(zip(EMOTION_TYPES, emotion))

def get_complex_mood(emotion):
    levels = get_emotion_levels(emotion)
    logger.info('mood: %s', levels)
    primary_emotion = max(levels, key=levels.get)
    primary_intensity = levels[primary_emotion]

    if primary_intensity >= 7:
        intensity_prefix = "extremely"
    elif primary_intensity >= 5:
        intensity_prefix = "very"
    elif primary_intensity >= 3:
        intensity_prefix = "moderately"
    else:
        intensity_prefix = "slightly"

    secondary_emotions = [e for e, v in levels.items() if v >= 2 and e != primary_emotion]
    
    if not secondary_emotions:
        return f"{intensity_prefix} {primary_emotion}"
    elif len(secondary_emotions) == 1:
        return f"{intensity_prefix} {primary_emotion}, with a touch of {secondary_emotions[0]}"
    else:
        return f"{intensity_prefix} {primary_emotion}, mixed with {secondary_emotions[0]} and {secondary_emotions[1]}"

def print_emotional_state():
    print("Current emotional state:")
    for emotion, value in zip(EMOTION_TYPES, emotion_values):
        print(f"{emotion}: {value}")
    print(f"Current mood: {get_complex_mood()}")
    




