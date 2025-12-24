import traceback
import urllib
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse

from routers import MongoDBManagerDependency
from utils.logger import logger

router = APIRouter()

@router.get("/download/{db_name}/{collection_name}/{filename}")
async def download_file(mongo_db : MongoDBManagerDependency, db_name : str, collection_name, filename: str):
    """
    Retrieves a file from MongoDB based on the filename 
    and streams it back to the user.
    """
    if not mongo_db.check_db_existence(db_name) or not mongo_db.check_collection_existence(db_name, collection_name):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Database '{db_name}' or Collection '{collection_name}' not found in the database."
        )

    try:
        file_size, _, content_stream = mongo_db.get_file_from_gridfs_by_filename(db_name, collection_name, filename)
        def file_iterator():
            chunk_size = 4096
            while True:
                chunk = content_stream.read(chunk_size)
                if not chunk:
                    break
                yield chunk
            content_stream.close()

        content_type = "application/octet-stream"
        if filename.lower().endswith('.txt'):
            content_type = "text/plain"
        elif filename.lower().endswith('.pdf'):
            content_type = "application/pdf"
        elif filename.lower().endswith('.docx'):
            content_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"

        encoded_filename = encoded_filename = urllib.parse.quote(filename)

        headers = {
            'Content-Disposition': f'attachment;  filename*=UTF-8\'\'{encoded_filename}',
            'Content-Length': file_size
        }

        return StreamingResponse(
            file_iterator(),
            media_type=content_type,
            headers=headers
        )
    
    except HTTPException:
        raise
        
    except Exception as e:
        error = traceback.format_exc()
        logger.error(f"Error downloading file: {str(error)}")
        raise HTTPException(status_code=500, detail=f"Error downloading file: {str(e)}")

@router.get("/download/{db_name}/{collection_name}/{filename}/{file_id}/{chunk_index}")
async def download_page(
    mongo_db : MongoDBManagerDependency,
    db_name : str, 
    collection_name, 
    filename : str, 
    file_id: str, 
    chunk_index : int
):
    """
    Retrieves a file from MongoDB based on the filename 
    and streams it back to the user.
    """
    if not mongo_db.check_db_existence(db_name) or not mongo_db.check_collection_existence(db_name, collection_name):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Database '{db_name}' or Collection '{collection_name}' not found in the database."
        )

    try:
        search_record = {"fileId" : file_id, "chunk_index" : chunk_index}
        file_size, content_stream = mongo_db.get_file_from_collection(db_name, collection_name, search_record)
        def file_iterator():
            chunk_size = 4096
            while True:
                chunk = content_stream.read(chunk_size)
                if not chunk:
                    break
                yield chunk
            content_stream.close()

        filename = f"{filename}_page_{chunk_index}.jpg"
        content_type = "application/octet-stream"
        if filename.lower().endswith(('.jpg', '.jpeg')):
            content_type = "image/jpeg"

        encoded_filename = encoded_filename = urllib.parse.quote(filename)

        headers = {
            'Content-Disposition': f'attachment;  filename*=UTF-8\'\'{encoded_filename}',
            'Content-Length': file_size
        }

        return StreamingResponse(
            file_iterator(),
            media_type=content_type,
            headers=headers
        )
    
    except HTTPException:
        raise
        
    except Exception as e:
        error = traceback.format_exc()
        logger.error(f"Error downloading file: {str(error)}")
        raise HTTPException(status_code=500, detail=f"Error downloading file: {str(e)}")