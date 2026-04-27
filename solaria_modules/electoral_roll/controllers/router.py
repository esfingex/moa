from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from app.core.views.templates import templates
from app.core.security import get_current_user

router = APIRouter(prefix='/electoral_roll', tags=['Electoral Roll'])


@router.get('/custom_page', response_class=HTMLResponse)
async def custom_page(request: Request, user=Depends(get_current_user)):
    return templates.TemplateResponse(
        request,
        "electoral_roll_custom.html",
        {
            "user": user,
            "title": "Electoral Roll Custom Page"
        }
    )
