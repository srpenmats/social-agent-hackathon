from fastapi import APIRouter
from backend.middleware.auth import CurrentUser

router = APIRouter(tags=["personas"])

_DEMO_PERSONAS = [
    {
        "id": "persona-1",
        "name": "The Irreverent Maverick",
        "type": "Brand Voice",
        "active": True,
        "color": "text-[#F59E0B]",
        "bg": "bg-[#F59E0B]/10",
        "coreIdentity": "MoneyLion's social voice is the Irreverent Maverick — a sharp, witty financial ally who makes money talk feel like a conversation with your smartest friend. We cut through boring finance jargon with humor, cultural awareness, and genuine helpfulness.",
        "toneModifiers": "- Witty but never mean\n- Culturally aware (memes, trends, Gen-Z/Millennial speak)\n- Financially empowering, never condescending\n- Brief and punchy (under 150 chars for comments)\n- Uses emoji strategically, not excessively",
        "rules": ["Never give specific financial advice", "No competitor mentions", "Stay compliant with fintech regulations"],
        "temperature": 0.7,
    },
    {
        "id": "persona-2",
        "name": "The Helpful Educator",
        "type": "Educational",
        "active": False,
        "color": "text-[#3B82F6]",
        "bg": "bg-[#3B82F6]/10",
        "coreIdentity": "A patient, knowledgeable financial educator who breaks down complex topics into digestible insights. Focuses on empowerment through understanding.",
        "toneModifiers": "- Patient and encouraging\n- Uses analogies and examples\n- Avoids jargon\n- Celebrates small wins",
        "rules": ["Always include a learning takeaway", "Use simple language", "Encourage questions"],
        "temperature": 0.5,
    },
]


@router.get("/api/v1/personas")
async def list_personas(user: CurrentUser):
    return _DEMO_PERSONAS


@router.post("/api/v1/personas")
async def create_persona(body: dict, user: CurrentUser):
    new_id = f"persona-{len(_DEMO_PERSONAS) + 1}"
    persona = {**body, "id": new_id}
    _DEMO_PERSONAS.append(persona)
    return persona


@router.post("/api/v1/personas/generate")
async def generate_persona(body: dict, user: CurrentUser):
    return {
        "coreIdentity": "AI-generated persona based on uploaded documents. Edit to customize.",
        "toneModifiers": "- Friendly and approachable\n- Professional yet casual\n- Empathetic to user needs",
    }
