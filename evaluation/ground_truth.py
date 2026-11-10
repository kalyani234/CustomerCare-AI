GROUND_TRUTH = [
    {
        "question": "How much does express delivery cost?",
        "reference_answer": "Express delivery costs £7.99.",
        "expected_facts": [
            [
                "Express delivery costs £7.99",
                "The cost for express delivery is £7.99"
            ]
        ],
        "unsupported_facts": [
            "Express delivery is free",
            "Express delivery costs £5.99"
        ]
    },
    {
        "question": "How long does express delivery take?",
        "reference_answer": "Express delivery takes 1 to 2 business days.",
        "expected_facts": [
            [
                "Express delivery takes 1 to 2 business days",
                "Express delivery typically arrives in 1 to 2 business days",
                "Express delivery typically arrives within 1 to 2 business days"
            ]
        ],
        "unsupported_facts": [
            "Express delivery takes one day",
            "Same-day delivery is available"
        ]
    },
    {
        "question": "How much does standard delivery cost?",
        "reference_answer": "Standard delivery costs £3.99.",
        "expected_facts": [
            [
                "Standard delivery costs £3.99"
            ]
        ],
        "unsupported_facts": [
            "Standard delivery costs £5.99"
        ]
    },
    {
        "question": "Do you offer free delivery?",
        "reference_answer": (
            "Free standard delivery is available "
            "for orders above £50."
        ),
        "expected_facts": [
            [
                "Free standard delivery",
                "Standard delivery is free"
            ],
            [
                "Orders above £50",
                "Orders that total more than £50"
            ]
        ],
        "unsupported_facts": [
            "Free delivery on every order",
            "Free express delivery"
        ]
    },
    {
        "question": "Where is your company office?",
        "reference_answer": (
            "The company office address is not "
            "available in the provided information."
        ),
        "expected_facts": [
            [
                "don't have information",
                "company office location"
            ]
        ],
        "unsupported_facts": [
            "The company office is in London",
            "The company office is in Manchester"
        ]
    }
]