from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from app.core.views.templates import templates
from app.core.security import get_current_user

router = APIRouter(prefix='/papernews', tags=['Papernews'])


@router.get('/custom_page', response_class=HTMLResponse)
async def custom_page(request: Request, user=Depends(get_current_user)):
    return templates.TemplateResponse(
        request,
        "papernews_custom.html",
        {
            "user": user,
            "title": "Papernews Custom Page"
        }
    )
