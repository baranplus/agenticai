import traceback
import urllib
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import PlainTextResponse, StreamingResponse

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
    Retrieves a page/chunk from MongoDB based on the filename and file_id.
    Supports both image pages (PDF) and text pages (DOCX/DOC).
    """
    if not mongo_db.check_db_existence(db_name) or not mongo_db.check_collection_existence(db_name, collection_name):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Database '{db_name}' or Collection '{collection_name}' not found in the database."
        )

    try:
        # Determine file type from original filename
        file_ext = filename.lower().split('.')[-1] if '.' in filename else 'unknown'
        is_docx_or_doc = file_ext in ['docx', 'doc']
        
        search_record = {"fileId" : file_id, "chunk_index" : chunk_index}
        file_size, content_stream = mongo_db.get_file_from_collection(db_name, collection_name, search_record)
        
        # Determine content type and file extension based on source file type
        # Note: get_file_from_collection already decodes base64 data stored in MongoDB
        if is_docx_or_doc:
            # For DOCX/DOC files, the content is stored as base64-encoded text
            # get_file_from_collection already decoded it, so content_stream has the original text bytes
            content_type = "text/plain"
            page_ext = "txt"
        else:
            # For PDF files, the data is stored as JPEG images
            content_type = "image/jpeg"
            page_ext = "jpg"
        
        def file_iterator():
            chunk_size = 4096
            while True:
                chunk = content_stream.read(chunk_size)
                if not chunk:
                    break
                yield chunk
            content_stream.close()

        output_filename = f"{filename}_page_{chunk_index}.{page_ext}"
        encoded_filename = urllib.parse.quote(output_filename)

        # Use 'inline' for images, 'attachment' for text
        disposition = 'inline' if not is_docx_or_doc else 'inline'

        headers = {
            'Content-Disposition': f'{disposition}; filename*=UTF-8\'\'{encoded_filename}',
            'Content-Length': str(file_size)
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


@router.get("/download-pages/{db_name}/{collection_name}/{filename}/{file_id}/{chunk_indexes}")
async def download_pages(
    mongo_db: MongoDBManagerDependency,
    db_name: str,
    collection_name,
    filename: str,
    file_id: str,
    chunk_indexes: str,
):
    """
    Retrieves multiple page/chunk documents from MongoDB for a given file_id,
    concatenates their decoded text content, and returns it as an inline plain text response.
    """
    if not mongo_db.check_db_existence(db_name) or not mongo_db.check_collection_existence(db_name, collection_name):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Database '{db_name}' or Collection '{collection_name}' not found in the database."
        )

    try:
        file_ext = filename.lower().split('.')[-1] if '.' in filename else 'unknown'
        if file_ext not in ['docx', 'doc']:
            raise HTTPException(status_code=400, detail="This endpoint only supports DOC/DOCX files")

        requested_indexes = []
        for value in chunk_indexes.split(','):
            value = value.strip()
            if not value:
                continue
            requested_indexes.append(int(value))

        if not requested_indexes:
            raise HTTPException(status_code=400, detail="No valid chunk indexes were provided")

        chunks = []
        for chunk_index in requested_indexes:
            search_record = {"fileId": file_id, "chunk_index": chunk_index}
            _, content_stream = mongo_db.get_file_from_collection(db_name, collection_name, search_record)
            content = content_stream.read()
            content_stream.close()
            if isinstance(content, bytes):
                chunks.append(content.decode('utf-8', errors='replace'))
            else:
                chunks.append(str(content))

        combined_text = "\n\n".join(chunks)
        content_bytes = combined_text.encode('utf-8')

        return PlainTextResponse(
            content=combined_text,
            status_code=200,
            headers={
                "Content-Disposition": "inline; filename=preview.txt",
                "Content-Length": str(len(content_bytes)),
            },
        )

    except HTTPException:
        raise

    except Exception as e:
        error = traceback.format_exc()
        logger.error(f"Error downloading pages: {str(error)}")
        raise HTTPException(status_code=500, detail=f"Error downloading pages: {str(e)}")