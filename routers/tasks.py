from fastapi import APIRouter, HTTPException, Depends
from schemas import TaskCreateRequest, TaskUpdateRequest
from database import supabase
from dependencies import verify_admin, verify_token

router = APIRouter()

@router.get("/")
async def get_all_tasks(current_user: str = Depends(verify_token)):
    try:
        res = supabase.table("tasks").select("*").is_("deleted_at", "null").order("task_date", desc=True).execute()
        return {"message": "Berhasil mengambil data task", "data": res.data}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.post("/")
async def create_task(req: TaskCreateRequest, admin_id: str = Depends(verify_admin)):
    try:
        task_data = {
            "title": req.title, "description": req.description, "task_date": req.task_date,
            "location": req.location, "created_by": req.admin_id, "assigned_spgs": req.assigned_spgs
        }
        res = supabase.table("tasks").insert(task_data).execute()
        return {"message": "Task berhasil dibuat", "data": res.data}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{task_id}")
async def get_task_detail(task_id: str, current_user: str = Depends(verify_token)):
    try:
        res = supabase.table("tasks").select("*, creator:profiles!tasks_created_by_fkey(full_name, role)").is_("deleted_at", "null").eq("id", task_id).execute()
        if not res.data: raise HTTPException(status_code=404, detail="Task tidak ditemukan")
        return {"message": "Berhasil mengambil detail task", "data": res.data[0]}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.put("/{task_id}")
async def update_task(task_id: str, req: TaskUpdateRequest, admin_id: str = Depends(verify_admin)):
    try:
        update_data = {k: v for k, v in req.dict().items() if v is not None}
        if not update_data: return {"message": "Tidak ada data yang diupdate"}
        res = supabase.table("tasks").update(update_data).eq("id", task_id).is_("deleted_at", "null").execute()
        if not res.data: raise HTTPException(status_code=404, detail="Task tidak ditemukan")
        return {"message": "Task berhasil diupdate", "data": res.data[0]}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.delete("/{task_id}")
async def delete_task(task_id: str, admin_id: str = Depends(verify_admin)):
    try:
        res = supabase.table("tasks").update({"deleted_at": "now()"}).eq("id", task_id).is_("deleted_at", "null").execute()
        if not res.data: raise HTTPException(status_code=404, detail="Task tidak ditemukan")
        return {"message": "Task berhasil dihapus", "data": res.data[0]}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))