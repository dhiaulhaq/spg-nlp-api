from fastapi import APIRouter, HTTPException, Depends
from schemas import RecordingSubmitRequest
from database import supabase
from dependencies import verify_admin, verify_token
from nlp_engine import CustomNLPEvaluator

router = APIRouter()

@router.get("/")
async def get_all_recordings(current_user: str = Depends(verify_token)):
    try:
        res = supabase.table("recordings").select("*, spg:profiles(full_name), task:tasks(title)").is_("deleted_at", "null").order("created_at", desc=True).execute()
        return {"message": "Berhasil mengambil data recording", "data": res.data}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.post("/")
async def submit_recording(req: RecordingSubmitRequest, current_user: str = Depends(verify_token)):
    try:
        evaluator = CustomNLPEvaluator(req.transcript)
        total_skor, detail_nlp_json = evaluator.run_evaluation()
        recording_data = {
            "task_id": req.task_id, "spg_id": req.spg_id, "transcript": req.transcript,
            "total_score": total_skor, "nlp_detail": detail_nlp_json
        }
        res = supabase.table("recordings").insert(recording_data).execute()
        return {
            "message": "Recording berhasil dinilai dan disimpan",
            "total_score": total_skor, "recording_id": res.data[0]['id'], "nlp_detail": detail_nlp_json
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{recording_id}")
async def get_recording_detail(recording_id: str, current_user: str = Depends(verify_token)):
    try:
        res = supabase.table("recordings").select("*, spg:profiles(*), task:tasks(title, location, created_by)").is_("deleted_at", "null").eq("id", recording_id).execute()
        if not res.data: raise HTTPException(status_code=404, detail="Recording tidak ditemukan")
        return {"message": "Berhasil mengambil detail recording", "data": res.data[0]}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{recording_id}")
async def delete_recording(recording_id: str, admin_id: str = Depends(verify_admin)):
    try:
        res = supabase.table("recordings").update({"deleted_at": "now()"}).eq("id", recording_id).is_("deleted_at", "null").execute()
        if not res.data: raise HTTPException(status_code=404, detail="Recording tidak ditemukan")
        return {"message": "Recording berhasil dihapus", "data": res.data[0]}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))