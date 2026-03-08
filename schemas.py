from pydantic import BaseModel
from typing import List, Optional

class LoginRequest(BaseModel):
    email: str
    password: str

class UserCreateRequest(BaseModel):
    email: str
    password: str
    role: str
    full_name: str
    client_name: Optional[str] = None
    project_name: Optional[str] = None

class UserUpdateRequest(BaseModel):
    full_name: Optional[str] = None
    role: Optional[str] = None
    client_name: Optional[str] = None
    project_name: Optional[str] = None

class TaskCreateRequest(BaseModel):
    title: str
    description: str
    task_date: str
    location: str
    admin_id: str
    assigned_spgs: List[str]

class TaskUpdateRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    task_date: Optional[str] = None
    location: Optional[str] = None
    assigned_spgs: Optional[List[str]] = None

class RecordingSubmitRequest(BaseModel):
    task_id: str
    spg_id: str
    transcript: str