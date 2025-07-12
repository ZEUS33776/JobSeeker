from fastapi import APIRouter
from app.services.resume_ingestor import extract_text_from_pdf
from fastapi import UploadFile,File
from app.services.llm_extractor import extract_keywords_from_llm
from app.services.search_engine import search_google
from fastapi import Form
# from app.services.query_builder import build_queries_from_keywords
router=APIRouter()

@router.post("/resume/upload")
async def upload_resume(role: str = Form(...), file: UploadFile = File(...)):

    try:
        text=extract_text_from_pdf(file.file)
       
        resume_info=extract_keywords_from_llm(resume=text,role=role)
        print(f"LLM Response: {resume_info}")  # Debug line
        # queries=build_queries_from_keywords(resume_info)
        parsed_info={"Skills":resume_info.get("skills", []),"Role":resume_info.get("role", ""),"Role_Variants":resume_info.get("role_variants", []),"search_queries":resume_info.get("queries", [])}
        search_results=search_google(parsed_info["search_queries"])
        return {"parsed_info":parsed_info,"search_results":search_results}
    except Exception as e:
        return {"error":str(e)}