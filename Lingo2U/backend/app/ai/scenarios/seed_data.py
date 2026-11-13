from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import Scenario

INITIAL_SCENARIOS = [
    {
        "slug": "introductions",
        "title": "Introductions",
        "description": "Meet someone new and talk about your name, country, and hobbies.",
        "difficulty": "A1",
        "tutor_role": "Friendly neighbor meeting you for the first time",
        "goal": "Introduce yourself, say where you are from, and share one hobby.",
        "target_vocab": ["name", "from", "country", "city", "live", "like", "hobby", "music", "nice", "meet"],
        "target_patterns": ["My name is...", "I am from...", "I live in...", "I like..."],
        "suggested_turns": 6,
        "sort_order": 1,
    },
    {
        "slug": "ordering-food",
        "title": "Ordering Food",
        "description": "Order a meal and a drink at a friendly cafe.",
        "difficulty": "A1",
        "tutor_role": "Cafe waiter taking your order",
        "goal": "Order something to eat and drink, and ask for the bill.",
        "target_vocab": ["menu", "water", "coffee", "tea", "sandwich", "salad", "hot", "cold", "bill", "please"],
        "target_patterns": ["Can I have...?", "I would like...", "How much is it?", "Thank you."],
        "suggested_turns": 6,
        "sort_order": 2,
    },
    {
        "slug": "shopping",
        "title": "Shopping for Clothes",
        "description": "Ask for sizes, colors, and prices in a clothing store.",
        "difficulty": "A1",
        "tutor_role": "Helpful shop assistant in a clothes store",
        "goal": "Find a shirt or jacket in your size and color, and check the price.",
        "target_vocab": ["shirt", "jacket", "shoes", "size", "small", "medium", "large", "blue", "black", "price"],
        "target_patterns": ["Do you have this in...?", "I am looking for...", "Can I try it on?", "It is too big."],
        "suggested_turns": 6,
        "sort_order": 3,
    },
    {
        "slug": "daily-routine",
        "title": "Daily Routine",
        "description": "Talk about what you do in the morning, afternoon, and evening.",
        "difficulty": "A1",
        "tutor_role": "English tutor asking about your day",
        "goal": "Describe when you wake up, work or study, and relax.",
        "target_vocab": ["wake up", "morning", "breakfast", "work", "study", "lunch", "dinner", "watch", "sleep", "usually"],
        "target_patterns": ["I wake up at...", "In the morning, I...", "After work, I...", "I go to bed at..."],
        "suggested_turns": 7,
        "sort_order": 4,
    },
    {
        "slug": "asking-for-directions",
        "title": "Asking for Directions",
        "description": "Ask how to find the train station, bank, or pharmacy.",
        "difficulty": "A2",
        "tutor_role": "Local resident on the street helping you find a place",
        "goal": "Ask where a place is and confirm how to walk there.",
        "target_vocab": ["where", "station", "bank", "pharmacy", "street", "left", "right", "straight", "near", "far"],
        "target_patterns": ["Excuse me, where is...?", "How do I get to...?", "Is it far from here?", "Turn left at..."],
        "suggested_turns": 6,
        "sort_order": 5,
    },
    {
        "slug": "workplace-chat",
        "title": "Simple Workplace Chat",
        "description": "Have a short morning chat with a coworker about your day and tasks.",
        "difficulty": "A2",
        "tutor_role": "Friendly coworker at the office",
        "goal": "Greet your coworker, talk about your weekend or today's tasks.",
        "target_vocab": ["morning", "weekend", "busy", "meeting", "email", "project", "help", "today", "coffee", "ready"],
        "target_patterns": ["How was your weekend?", "I have a meeting at...", "I am working on...", "Can you help me with...?"],
        "suggested_turns": 7,
        "sort_order": 6,
    },
]


async def seed_scenarios(db: AsyncSession) -> None:
    for item in INITIAL_SCENARIOS:
        exists = await db.scalar(select(Scenario).where(Scenario.slug == item["slug"]))
        if not exists:
            db.add(Scenario(**item))
    await db.commit()
