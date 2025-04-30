def get_journey():
    """
    Get the journey of the player.
    """
    return {
        "Kenta Takahashi": [            
            {
                "activity": "think",
                "description": "What a wonderful day! Maybe cafe is open now."
            }, 
            "Wait for 100 steps",
            [(53, 14), (72, 19), "Walking to Cafe"],
            "Wait for 1000 steps",
        ],
        "Sakura Sato": [
            {
                "activity": "think",
                "description": "I’m free today, so going to the library to read a book."
            },
            "Wait for 100 steps",
            [(126, 46), (122, 25), "Walking to library"],
            {
                "activity": "think",
                "description": "Maybe I can read 'Lord of the Rings' or 'Harry Potter'? Or just nap between bookshelves?"
            },
            "Wait for 150 steps",
            {
                "activity": "chat",
                "description": ["", "Zhang San", "Yeah, I love 'Lord of the Rings'. Which character do you like, Zhang?"],
            },
            "Wait for 30 steps",
            {
                "activity": "chat",
                "description": ["Zhang San", "Sakura Sato", "Definitely Aragorn. Sword skills, cool beard... what’s not to love?"],
            },
            "Wait for 20 steps",
            {
                "activity": "chat",
                "description": ["Sakura Sato", "Zhang San", "True, but I like Sam. He carried Frodo *and* the emotional weight of the entire story."],
            },
            "Wait for 25 steps",
            {
                "activity": "chat",
                "description": ["Zhang San", "Sakura Sato", "Fair. Sam’s the real MVP. Also, 10/10 cooking skills."],
            },
            "Wait for 15 steps",
            {
                "activity": "chat",
                "description": ["Sakura Sato", "Zhang San", "Next time we go to Mordor, I’m bringing Sam and snacks."],
            },
            [(122, 25), (73, 19), "Walking to Cafe"]
        ],
        "Zhang San": [
            {
                "activity": "think",
                "description": "Life is boring. Maybe I’ll go to the library. Books are cheaper than therapy."
            },
            "Wait for 100 steps",
            [(26, 18), (110, 23), "Walking to Library"],
            {
                "activity": "think",
                "description": "Is Sakura reading 'Lord of the Rings'? If she says Gollum is her favorite, I'm running."
            },
            "Wait for 100 steps",
            {
                "activity": "chat",
                "description": ["", "Sakura Sato", "Are you reading 'Lord of the Rings'?"],
            },
            "Wait for 30 steps",
            {
                "activity": "chat",
                "description": ["Sakura Sato", "Zhang San", "Yeah, I love 'Lord of the Rings'. Which character do you like, Zhang?"],
            },
            "Wait for 20 steps",
            {
                "activity": "chat",
                "description": ["Zhang San", "Sakura Sato", "Definitely Aragorn. Sword skills, cool beard... what’s not to love?"],
            },
            "Wait for 25 steps",
            {
                "activity": "chat",
                "description": ["Sakura Sato", "Zhang San", "True, but I like Sam. He carried Frodo *and* the emotional weight of the entire story."],
            },
            "Wait for 20 steps",
            {
                "activity": "chat",
                "description": ["Zhang San", "Sakura Sato", "Fair. Sam’s the real MVP. Also, 10/10 cooking skills."],
            },
            "Wait for 15 steps",
            {
                "activity": "chat",
                "description": ["Sakura Sato", "Zhang San", "Next time we go to Mordor, I’m bringing Sam and snacks."],
            },
            [(110, 23), (70, 19), "Walking to Cafe"]
        ]
    }
