import traceback
import io
import urllib
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from db import mongodb_manager
from utils.logger import logger

router = APIRouter()

@router.get("/download/{db_name}/{filename}")
async def download(db_name : str, filename: str):
    """
    Retrieves a file from MongoDB based on the filename 
    and streams it back to the user.
    """

    try:
        file_size, content_stream = mongodb_manager.get_file_source(db_name, filename, "source_files")
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