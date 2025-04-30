                self.plan_journeys(
                    "Sakura Sato" :[
                        [(126, 46), (122, 25), "Walking to library"],  
                        {   # after first journey
                            "activity": "think",
                            "description": "Lord of the Rings"
                        },
                        "Wait for 50 steps" # no updates for next 50 steps
                        [(122, 25), (126, 46), "Returning from library"],
                        {   # after second journey
                            "activity": "think",
                            "description": ["That was a great book"]
                        },
                    ]
                )