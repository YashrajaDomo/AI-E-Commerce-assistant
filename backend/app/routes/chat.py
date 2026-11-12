from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.repositories.product_repository import get_all_products, get_product_by_name, get_products_by_ids
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.ai_service import compare_products, generate_product_response, generate_recommendation, get_openai_response, parse_user_query
from app.utils.search_utils import get_category_from_text

router = APIRouter(prefix="/api", tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
def chat_with_ai(request: ChatRequest, db: Session = Depends(get_db)):
    message = request.message.strip()
    if not message:
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    parsed = parse_user_query(message)
    category = parsed.get("category")
    min_price = parsed.get("min_price")
    max_price = parsed.get("max_price")
    keywords = parsed.get("keywords", [])

    products = get_all_products(
        db,
        category=category,
        min_price=min_price,
        max_price=max_price,
        min_rating=None,
        query=" ".join(keywords) if keywords else None,
    )

    if "compare" in message.lower() and " and " in message.lower():
        compare_words = message.lower().split("compare", 1)[1].strip()
        product_names = [name.strip() for name in compare_words.split(" and ") if name.strip()]
        comparison_products = []
        for name in product_names:
            product = get_product_by_name(db, name)
            if product:
                comparison_products.append(product)
        if comparison_products:
            response_message = compare_products(comparison_products)
            return ChatResponse(message=response_message, products=comparison_products)

    if not products:
        response_message = "I couldn't find matching products for that request."
        return ChatResponse(message=response_message, products=[])

    recommended = generate_recommendation(message, products)
    top_products = recommended[:3]

    llm_response = get_openai_response(message)
    if llm_response:
        response_message = llm_response
    else:
        response_message = generate_product_response(message, top_products)

    return ChatResponse(message=response_message, products=top_products)
