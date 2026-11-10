EVALUATION_DATASET = [
    {
        "question": "How much does express delivery cost?",
        "expected_keywords": ["£7.99"],
        "unsupported_phrases": [
            "special arrangements are possible",
            "free express delivery"
        ]
    },
    {
        "question": "How long does express delivery take?",
        "expected_keywords": ["1 to 2 business days"],
        "unsupported_phrases": [
            "same-day delivery",
            "next-day guaranteed"
        ]
    },
    {
        "question": "How much does standard delivery cost?",
        "expected_keywords": ["£3.99"],
        "unsupported_phrases": [
            "standard delivery is free"
        ]
    },
    {
        "question": "Do you offer free delivery?",
        "expected_keywords": ["free", "£50"],
        "unsupported_phrases": [
            "free delivery on every order"
        ]
    },
    {
        "question": "Where is your company office?",
        "expected_keywords": ["company office", "information"],
        "unsupported_phrases": [
            "London office",
            "Manchester office"
        ]
    }
]