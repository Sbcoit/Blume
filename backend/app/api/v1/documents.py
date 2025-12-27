"""
Document processing endpoints
"""
from fastapi import APIRouter, Depends, UploadFile, File, BackgroundTasks
from sqlalchemy.orm import Session
from app.core.dependencies import get_database
from app.api.v1.auth import get_current_user_id
from app.processors.document_processor import DocumentProcessor
from app.services.agent.agent import AgentService
from uuid import UUID

router = APIRouter(prefix="/documents", tags=["documents"])


async def process_document_background(
    db: Session,
    user_id: UUID,
    file_data: bytes,
    filename: str,
    agent: AgentService,
    processor: DocumentProcessor
):
    """Background task to process document"""
    try:
        # Process document
        result = await processor.process(file_data, filename)
        
        # Extract text
        text = await processor.extract_text(file_data, filename)
        
        # Process with agent
        task_data = {
            "input": f"Analyze this document: {filename}\n\nContent:\n{text}",
            "type": "document",
            "metadata": result
        }
        
        await agent.process_task(task_data)
    except Exception as e:
        print(f"Error processing document: {e}")


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_database)
):
    """Upload and process a document"""
    # Read file
    file_data = await file.read()
    
    # Process in background
    processor = DocumentProcessor()
    agent = AgentService()
    
    background_tasks.add_task(
        process_document_background,
        db=db,
        user_id=UUID(user_id),
        file_data=file_data,
        filename=file.filename or "unknown",
        agent=agent,
        processor=processor
    )
    
    return {
        "status": "uploaded",
        "filename": file.filename,
        "message": "Document is being processed"
    }
