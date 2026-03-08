from fastapi import APIRouter, HTTPException
from schemas import LoginRequest
from database import supabase

router = APIRouter()

@router.post("/login")
async def login(req: LoginRequest):
    try:
        res = supabase.auth.sign_in_with_password({"email": req.email, "password": req.password})
        user_id = res.user.id
        profile = supabase.table("profiles").select("*").eq("id", user_id).execute()
        return {
            "message": "Login berhasil",
            "access_token": res.session.access_token,
            "user_data": profile.data[0] if profile.data else None
        }
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Login Gagal: {str(e)}")