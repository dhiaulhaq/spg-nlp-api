from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from database import supabase

security = HTTPBearer()

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        user_res = supabase.auth.get_user(token)
        return user_res.user.id
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Sesi tidak valid atau token kadaluarsa: {str(e)}")

async def verify_admin(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        user_res = supabase.auth.get_user(token)
        user_id = user_res.user.id
        
        profile_res = supabase.table("profiles").select("role").eq("id", user_id).execute()
        if not profile_res.data:
            raise HTTPException(status_code=403, detail="Profil tidak ditemukan")
            
        role = profile_res.data[0]["role"]
        if role not in ["admin", "superadmin"]:
            raise HTTPException(status_code=403, detail="Akses ditolak: Hanya Admin dan Superadmin yang diizinkan")
            
        return user_id
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Sesi tidak valid atau akses ditolak: {str(e)}")
    
async def verify_superadmin(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        user_res = supabase.auth.get_user(token)
        user_id = user_res.user.id
        
        profile_res = supabase.table("profiles").select("role").eq("id", user_id).execute()
        if not profile_res.data:
            raise HTTPException(status_code=403, detail="Profil tidak ditemukan")
            
        role = profile_res.data[0]["role"]
        if role != "superadmin":
            raise HTTPException(status_code=403, detail="Akses ditolak: Hanya Superadmin yang diizinkan untuk aksi ini")
            
        return user_id
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Sesi tidak valid atau akses ditolak: {str(e)}")