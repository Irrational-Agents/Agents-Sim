
# BASIC_FUNCTION_SCHEMA = {
#     "parameters": {
#         "type": "object",
#         "properties": {
#             "resp": {# here to add Json schema},
#         },
#         "required": ["resp"],
#         "additionalProperties": False
#     }
# }


PROMPT_CONFIG = {
    "generate_plan": {
        "files": ["plan_prompt.txt", "action_prompt.txt"],
        "stream": ["description_list"],
        "system": "You are an AI assistant tasked with creating plans based on recent events and current context.",
        "type": "json",
        "function_schema": [{
            "name": "generate_plan_schema",
            "parameters": {
                "type": "object",
                "properties": {
                    "resp": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "description": {
                                    "type": "string"
                                }
                            },
                            "additionalProperties": False,
                            "required": ["description"]
                        }
                    }
                },
                "required": ["resp"],
                "additionalProperties": False
            }
        },
        {
            "name": "generate_action_schema",
            "parameters": {
                "type": "object",
                "properties": {
                    "resp": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "action": {
                                    "type": "string"
                                },
                                "description": {
                                    "type": "string"
                                }
                            },
                            "additionalProperties": False,
                            "required": ["description", "action"]
                        }
                    }
                },
                "required": ["resp"],
                "additionalProperties": False
            }
        }
        ]
    },
    "generate_daily_plan": {
        "files": ["daily_plan_prompt.txt"],
        "system": "You are an AI assistant tasked with generating a character's daily schedule by combining given information.",
        "type": "json",
        "function_schema": [{
            "name": "generate_daily_plan_schema",
            "parameters": {
                "type": "object",
                "properties": {
                    "resp": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "time": {
                                    "type": "string"
                                },
                                "activity": {
                                    "type": "string"
                                },
                                "moccupying": {
                                    "type": "integer"
                                }
                            },
                            "required": [
                                "time",
                                "activity",
                                "moccupying"
                            ],
                            "additionalProperties": False
                        }
                    }
                },
                "required": ["resp"],
                "additionalProperties": False
            }
        }]
    },
    "generate_conversation": {
        "files": ["conv_prompt.txt"],
        "system": "You are an AI assistant tasked with generating brief, context-appropriate actions or conversations based on given plans and events.",
        "type": "json",
         "function_schema": [{
            "name": "generate_conversation_schema",
            "parameters": {
                "type": "object",
                "properties": {
                    "resp": {
                        "type": "object",
                        "properties": {
                            "person": {
                                "type": "string"
                            },
                            "description": {
                                "type": "string"
                            }
                        },
                        "additionalProperties": False,
                        "required": [
                            "person",
                            "description"
                        ]
                    }
                },
                "required": ["resp"],
                "additionalProperties": False
            }
        }]
    },
     "generate_interaction": {
        "files": ["interaction_prompt.txt"],
        "system": "Y",
        "type": "json",
          "function_schema": [{
            "name": "generate_conversation_schema",
            "parameters": {
                "type": "object",
                "properties": {
                    "resp": {
                        "type": "object",
                        "properties": {
                            "item": {
                                "type": "string"
                            },
                            "description": {
                                "type": "string"
                            }
                        },
                        "additionalProperties": False,
                        "required": [
                            "item",
                            "description"
                        ]
                    }
                },
                "required": ["resp"],
                "additionalProperties": False
            }
        }]
    },
    "generate_thought": {
        "files": ["think_prompt.txt"],
        "system": "You are an AI assistant tasked with generating the thought process for an NPC based on a given plan.",
        "type": "text"
    },
    "generate_move": {
        "files": ["move_prompt.txt"],
        "system": "You are an AI assistant tasked with generating the best destination based on the given plan and events.",
        "type": "text"
    },
    "generate_personality": {
        "files": ["personality_prompt.txt"],
        "system": "You are an AI assistant specialized in creating concise and insightful personality profiles based on given personality traits.",
        "type": "text"
    },
    "generate_short_memory": {
        "files": ["short_memory_prompt.txt"],
        "system": "You are an AI assistant tasked with updating an agent's short-term memory and emotional state based on perceived events and context.",
        "type": "json",
        "function_schema": [{
            "name": "generate_short_memory_schema",
            "parameters": {
                "type": "object",
                "properties": {
                    "resp": {
                        "type": "object",
                        "properties": {
                            "new_emotion": {
                                "type": "array",
                                "items": {
                                    "type": "number"
                                }
                            },
                            "new_entries": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "type": {
                                            "type": "number"
                                        },
                                        "description": {
                                            "type": "string"
                                        },
                                        "time": {
                                            "type": "string"
                                        },
                                        "date": {
                                            "type": "string"
                                        }
                                    },
                                    "required": [
                                        "type",
                                        "description",
                                        "time",
                                        "date"
                                    ],
                                    "additionalProperties": False
                                }
                            }
                        },
                        "required": [
                            "new_emotion",
                            "new_entries"
                        ],
                        "additionalProperties": False
                    },
                },
                "required": ["resp"],
                "additionalProperties": False
            }
        }]
    },
    "extract_keywords": {
        "files": ["extract_keywords_prompt.txt"],
        "system": "You are an intelligent assistant designed to extract meaningful entities and keywords for long-term memory indexing.",
        "type": "json",
        "function_schema": [{
            "name": "extract_keywords_schema",
            "parameters": {
                "type": "object",
                "properties": {
                    "resp": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        }
                    }
                },
                "required": ["resp"],
                "additionalProperties": False
            }
        }]
    },
    "plans_selection": {
        "files": ["plans_selection_prompt.txt"],
        "system": "You are an AI assistant designed to mimic human decision-making. Your task is to choose the most appropriate decision from a set of given plans based on a detailed profile of a person,including their personality, past experiences, and biases.",
        "type": "json",
        "function_schema": [{
            "name": "plans_selection_schema",
            "parameters": {
                "type": "object",
                "properties": {
                    "resp": {
                        "type": "object",
                        "properties": {
                            "action": {
                                "type": "string"
                            },
                            "description": {
                                "type": "string"
                            }
                        },
                        "additionalProperties": False,
                        "required": [
                            "action",
                            "description"
                        ]
                    }
                },
                "required": ["resp"],
                "additionalProperties": False
            }
        }]
    },
    "gpt_analyze_needs":{
        "files": ["gpt_analyze_needs.txt"],
        "system": "You are an AI assistant designed to analyze how activities affect a human's basic needs.",
        "type": "json",
        "function_schema": [{
            "name": "gpt_analyze_needs_schema",
            "parameters": {
                "type": "object",
                "properties": {
                    "resp": {
                        "type": "object",
                        "properties": {
                            "new_emotion": {
                                "type": "array",
                                "items": {
                                    "type": "number"
                                }
                            },
                            "new_basic_needs": {
                                "type": "object",
                                "properties": {
                                    "fullness": {
                                        "type": "number"
                                    },
                                    "social": {
                                        "type": "number"
                                    },
                                    "fun": {
                                        "type": "number"
                                    },
                                    "health": {
                                        "type": "number"
                                    },
                                    "energy": {
                                        "type": "number"
                                    }
                                },
                                "additionalProperties": False,
                                "required": [
                                    "fullness",
                                    "social",
                                    "fun",
                                    "health",
                                    "energy"
                                ]
                            }
                        },
                        "required": [
                        "new_emotion",
                        "new_basic_needs"
                    ],
                    "additionalProperties": False
                    },      
                },
                "required": ["resp"],
                "additionalProperties": False
            }
        }]
    }
}
