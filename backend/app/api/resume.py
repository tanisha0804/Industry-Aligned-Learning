from fastapi import APIRouter
from pathlib import Path
from app.core.data_processor import run_all_processing

router = APIRouter()

@router.post("/process-all")
def process_all_data():
    base_data_dir = Path(__file__).resolve().parents[1] / "data"
    run_all_processing(base_data_dir)
    return {"status": "All PDFs processed successfully"}
