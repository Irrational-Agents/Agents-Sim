from prompt.llm_command_list import *
from collections import Counter

def growth(self):
    
    self.agent = 0
        
def get_personality(personality): 
    return generate_personality(extract_traits(personality))

def extract_traits(personality_traits):
    #  “Big Five Personality Dimensions: Characteristics of Individuals with High- and Low-Value Combinations of Dimensions”.
    traits_matrix = {
        "openness": {
            "agreeableness": {
                "high": {
                    "high": ["Idealistic", "diplomatic", "deep", "tactful", "genial"],
                    "low": ["Shrewd", "eccentric", "individualistic"]
                },
                "low": {
                    "high": ["Simple", "dependent"],
                    "low": ["Coarse", "tactless", "curt", "narrow-minded", "callous"]
                }
            },
            "conscientiousness": {
                "high": {
                    "high": ["Analytical", "perceptive", "informative", "articulate", "dignified"],
                    "low": ["Unconventional", "quirky"]
                },
                "low": {
                    "high": ["Traditional", "conventional"],
                    "low": ["Shortsighted", "foolhardy", "illogical", "immature", "haphazard"]
                }
            },
            "extraversion": {
                "high": {
                    "high": ["Worldly", "theatrical", "eloquent", "inquisitive", "intense"],
                    "low": ["Introspective", "meditative", "contemplating", "self-examining", "inner-directed"]
                },
                "low": {
                    "high": ["Verbose", "unscrupulous", "pompous"],
                    "low": ["Predictable", "unimaginative", "somber", "apathetic", "unadventurous"]
                }
            },
            "neuroticism": {
                "high": {
                    "high": ["Excitable", "passionate", "sensual"],
                    "low": ["Heartfelt", "versatile", "creative", "intellectual", "insightful"]
                },
                "low": {
                    "high": ["Easily rattled", "easily irked", "apprehensive"],
                    "low": ["Imperturbable", "insensitive"]
                }
            }
        },
        "agreeableness": {
            "openness": {
                "high": {
                    "high": ["Genial", "tactful", "diplomatic", "deep", "idealistic"],
                    "low": ["Dependent", "simple"]
                },
                "low": {
                    "high": ["Shrewd", "eccentric", "individualistic"],
                    "low": ["Coarse", "tactless", "curt", "narrow-minded", "callous"]
                }
            },
            "conscientiousness": {
                "high": {
                    "high": ["Helpful", "cooperative", "considerate", "respectful", "polite"],
                    "low": ["Unpretentious", "self-effacing"]
                },
                "low": {
                    "high": ["Strict", "rigid", "stern"],
                    "low": ["Inconsiderate", "impolite", "distrustful", "uncooperative", "thoughtless"]
                }
            },
            "extraversion": {
                "high": {
                    "high": ["Effervescent", "happy", "friendly", "merry", "jovial"],
                    "low": ["Soft-hearted", "agreeable", "obliging", "humble", "lenient"]
                },
                "low": {
                    "high": ["Bullheaded", "abrupt", "crude", "combative", "rough"],
                    "low": ["Cynical", "wary of others", "reclusive", "detached", "impersonal"]
                }
            },
            "neuroticism": {
                "high": {
                    "high": ["Sentimental", "affectionate", "sensitive", "soft", "passionate"],
                    "low": ["Generous", "pleasant", "tolerant", "peaceful", "flexible"]
                },
                "low": {
                    "high": ["Critical", "selfish", "ill-tempered", "antagonistic", "grumpy"],
                    "low": ["Insensitive", "unaffectionate", "passionless", "unemotional"]
                }
            }
        },
        "conscientiousness": {
            "openness": {
                "high": {
                    "high": ["Sophisticated", "perfectionistic", "industrious", "dignified", "refined"],
                    "low": ["Traditional", "conventional"]
                },
                "low": {
                    "high": ["Unconventional", "quirky"],
                    "low": ["Foolhardy", "illogical", "immature", "haphazard", "lax"]
                }
            },
            "agreeableness": {
                "high": {
                    "high": ["Dependable", "responsible", "reliable", "mannerly", "considerate"],
                    "low": ["Stern", "strict", "rigid"]
                },
                "low": {
                    "high": ["Unpretentious", "self-effacing"],
                    "low": ["Rash", "uncooperative", "unreliable", "distrustful", "thoughtless"]
                }
            },
            "extraversion": {
                "high": {
                    "high": ["Ambitious", "alert", "firm", "purposeful", "competitive"],
                    "low": ["Cautious", "confident", "punctual", "formal", "thrifty"]
                },
                "low": {
                    "high": ["Unruly", "boisterous", "reckless", "devil-may-care", "demonstrative"],
                    "low": ["Indecisive", "aimless", "wishy-washy", "noncommittal", "unambitious"]
                }
            },
            "neuroticism": {
                "high": {
                    "high": ["Particular", "high-strung"],
                    "low": ["Thorough", "steady", "consistent", "self-disciplined", "logical"]
                },
                "low": {
                    "high": ["Scatterbrained", "inconsistent", "erratic", "forgetful", "impulsive"],
                    "low": ["Informal", "low-key"]
                }
            }
        },
        "extraversion": {
            "openness": {
                "high": {
                    "high": ["Expressive", "candid", "dramatic", "spontaneous", "witty"],
                    "low": ["Verbose", "unscrupulous", "pompous"]
                },
                "low": {
                    "high": ["Inner-directed", "introspective", "meditative", "contemplating", "self-examining"],
                    "low": ["Somber", "meek", "unadventurous", "passive", "apathetic"]
                }
            },
            "agreeableness": {
                "high": {
                    "high": ["Social", "energetic", "enthusiastic", "communicative", "vibrant"],
                    "low": ["Opinionated", "forceful", "domineering", "boastful", "bossy"]
                },
                "low": {
                    "high": ["Unaggressive", "humble", "submissive", "timid", "compliant"],
                    "low": ["Skeptical", "wary of others", "seclusive", "uncommunicative", "unsociable"]
                }
            },
            "conscientiousness": {
                "high": {
                    "high": ["Active", "competitive", "persistent", "ambitious", "purposeful"],
                    "low": ["Boisterous", "mischievous", "exhibitionistic", "gregarious", "demonstrative"]
                },
                "low": {
                    "high": ["Restrained", "serious", "discreet", "cautious", "principled"],
                    "low": ["Indirect", "unenergetic", "sluggish", "non-persistent", "vague"]
                }
            },
            "neuroticism": {
                "high": {
                    "high": ["Explosive", "wordy", "extravagant", "volatile", "flirtatious"],
                    "low": ["Confident", "bold", "assured", "uninhibited", "courageous"]
                },
                "low": {
                    "high": ["Guarded", "pessimistic", "secretive", "cowardly"],
                    "low": ["Tranquil", "sedate", "placid", "impartial", "unassuming"]
                }
            }
        },
        "neuroticism": {
            "openness": {
                "high": {
                    "high": ["Excitable", "passionate", "sensual"],
                    "low": ["Easily rattled", "easily irked", "apprehensive"]
                },
                "low": {
                    "high": ["Heartfelt", "versatile", "creative", "intellectual", "insightful"],
                    "low": ["Imperturbable", "insensitive"]
                }
            },
            "agreeableness": {
                "high": {
                    "high": ["Emotional", "gullible", "affectionate", "sensitive", "soft"],
                    "low": ["Temperamental", "irritable", "quarrelsome", "impatient", "grumpy"]
                },
                "low": {
                    "high": ["Patient", "relaxed", "undemanding", "down-to-earth"],
                    "low": ["Unemotional", "insensitive", "unaffectionate", "passionless"]
                }
            },
            "conscientiousness": {
                "high": {
                    "high": ["Particular", "high-strung"],
                    "low": ["Compulsive", "nosy", "self-indulgent", "forgetful", "impulsive"]
                },
                "low": {
                    "high": ["Rational", "objective", "steady", "logical", "decisive"],
                    "low": ["Informal", "low-key"]
                }
            },
            "extraversion": {
                "high": {
                    "high": ["Excitable", "wordy", "flirtatious", "explosive", "extravagant"],
                    "low": ["Guarded", "fretful", "insecure", "pessimistic", "secretive"]
                },
                "low": {
                    "high": ["Unselfconscious", "weariless", "indefatigable"],
                    "low": ["Unassuming", "unexcitable", "placid", "tranquil"]
                }
            }
        }
    }

    def get_level(score):
        return "high" if score > 5 else "low"

    def get_strength(score1, score2):
        total = score1 + (10 - score2)
        if total >= 18 or total <= 2:
            return "strongly"
        elif 8 <= total <= 12:
            return "moderately"
        else:
            return "somewhat"

    trait_scores = Counter()

    for primary, primary_score in personality_traits.items():
        for secondary, secondary_score in personality_traits.items():
            if primary != secondary:
                primary_level = get_level(primary_score)
                secondary_level = get_level(secondary_score)
                strength = get_strength(primary_score, secondary_score)

                if primary in traits_matrix and secondary in traits_matrix[primary]:
                    traits = traits_matrix[primary][secondary][primary_level][secondary_level]
                    for trait in traits:
                        trait_scores[trait] += {"strongly": 3, "moderately": 2, "somewhat": 1}[strength]
    
    # 結果を形式（強度 + 特性名）に変換
    result = []
    for trait, score in traits:
        if score >= 3:
            strength = "strongly"
        elif score == 2:
            strength = "moderately"
        else:
            strength = "somewhat"
        result.append(f"{strength} {trait}")
    
    return result
