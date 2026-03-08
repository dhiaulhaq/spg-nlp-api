from fastapi import APIRouter, HTTPException, Depends
from schemas import UserCreateRequest, UserUpdateRequest
from database import supabase
from dependencies import verify_admin, verify_superadmin, verify_token

router = APIRouter()

@router.get("/")
async def get_all_users(current_user: str = Depends(verify_token)):
    try:
        res = supabase.table("profiles").select("*").is_("deleted_at", "null").execute()
        return {"message": "Berhasil mengambil data user", "data": res.data}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/")
async def create_user(req: UserCreateRequest, superadmin_id: str = Depends(verify_superadmin)):
    try:
        auth_res = supabase.auth.sign_up({"email": req.email, "password": req.password})
        new_user_id = auth_res.user.id
        profile_data = {
            "id": new_user_id, "role": req.role, "full_name": req.full_name,
            "client_name": req.client_name, "project_name": req.project_name
        }
        supabase.table("profiles").insert(profile_data).execute()
        return {"message": "User berhasil dibuat", "user_id": new_user_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.get("/{user_id}")
async def get_user_detail(user_id: str, current_user: str = Depends(verify_token)):
    try:
        res = supabase.table("profiles").select("*").is_("deleted_at", "null").eq("id", user_id).execute()
        if not res.data: raise HTTPException(status_code=404, detail="User tidak ditemukan")
        return {"message": "Berhasil mengambil detail user", "data": res.data[0]}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.put("/{user_id}")
async def update_user(user_id: str, req: UserUpdateRequest, admin_id: str = Depends(verify_admin)):
    try:
        update_data = {k: v for k, v in req.dict().items() if v is not None}
        if not update_data: return {"message": "Tidak ada data yang diupdate"}
        res = supabase.table("profiles").update(update_data).eq("id", user_id).is_("deleted_at", "null").execute()
        if not res.data: raise HTTPException(status_code=404, detail="User tidak ditemukan")
        return {"message": "User berhasil diupdate", "data": res.data[0]}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.delete("/{target_user_id}")
async def delete_user(target_user_id: str, superadmin_id: str = Depends(verify_superadmin)):
    try:
        res = supabase.table("profiles").update({"deleted_at": "now()"}).eq("id", target_user_id).is_("deleted_at", "null").execute()
        if not res.data: raise HTTPException(status_code=404, detail="User tidak ditemukan")
        return {"message": "User berhasil dihapus", "data": res.data[0]}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))