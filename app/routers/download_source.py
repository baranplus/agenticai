import traceback
import urllib
from html import escape

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import HTMLResponse, PlainTextResponse, StreamingResponse

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

@router.get("/download-pages-html/{db_name}/{collection_name}/{filename}/{file_id}/{chunk_indexes}")
async def download_pages_html(
    mongo_db: MongoDBManagerDependency,
    db_name: str,
    collection_name,
    filename: str,
    file_id: str,
    chunk_indexes: str,
):
    """
    Retrieves multiple page/chunk documents from MongoDB, combines their text,
    and returns a polished RTL HTML preview that is centered and styled for readability.
    """
    if not mongo_db.check_db_existence(db_name) or not mongo_db.check_collection_existence(db_name, collection_name):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Database '{db_name}' or Collection '{collection_name}' not found in the database."
        )

    try:
        file_ext = filename.lower().split('.')[-1] if '.' in filename else 'unknown'
        if file_ext not in ['docx', 'doc', 'unknown']:
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
            try:
                search_record = {"fileId": file_id, "chunk_index": chunk_index}
                _, content_stream = mongo_db.get_file_from_collection(db_name, collection_name, search_record)
                content = content_stream.read()
                content_stream.close()
                if isinstance(content, bytes):
                    decoded = content.decode('utf-8', errors='replace')
                else:
                    decoded = str(content)
                if decoded.strip():
                    chunks.append(decoded)
            except Exception as e:
                logger.error(f"Error retrieving chunk {chunk_index}: {str(e)}")
                continue

        combined_text = "\n\n".join(chunks)
        if not combined_text.strip():
            combined_text = "No content available."

        escaped_text = escape(combined_text)
        html_content = f"""<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>{escape(filename)} Preview</title>
    <style>
        :root {{
            color-scheme: light;
            --bg-start: #f5f7ff;
            --bg-end: #eef2ff;
            --card-bg: rgba(255, 255, 255, 0.92);
            --text-main: #1f2937;
            --text-muted: #475569;
            --border: rgba(148, 163, 184, 0.35);
            --shadow: 0 20px 60px rgba(15, 23, 42, 0.12);
        }}
        * {{ box-sizing: border-box; }}
        body {{
            margin: 0;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 24px;
            background: linear-gradient(135deg, var(--bg-start) 0%, var(--bg-end) 100%);
            font-family: 'Vazirmatn', 'Segoe UI', Tahoma, Arial, sans-serif;
            color: var(--text-main);
        }}
        .card {{
            width: min(92vw, 900px);
            max-height: 85vh;
            overflow: auto;
            background: var(--card-bg);
            border: 1px solid var(--border);
            border-radius: 24px;
            box-shadow: var(--shadow);
            backdrop-filter: blur(12px);
            padding: 28px 32px;
        }}
        .title {{
            margin: 0 0 16px;
            text-align: center;
            font-size: 1.1rem;
            font-weight: 700;
            color: #0f172a;
        }}
        .content {{
            direction: rtl;
            text-align: right;
            white-space: pre-wrap;
            line-height: 1.9;
            font-size: 1rem;
            color: var(--text-main);
            word-break: break-word;
        }}
        .meta {{
            margin-top: 16px;
            text-align: center;
            font-size: 0.9rem;
            color: var(--text-muted);
        }}
        @media (max-width: 768px) {{
            .card {{ padding: 22px 18px; border-radius: 18px; }}
            .content {{ font-size: 0.95rem; }}
        }}
    </style>
</head>
<body>
    <main class="card">
        <h1 class="title">پیش‌نمایش متن</h1>
        <div class="meta">صفحات تقریبی {requested_indexes[0] + 1},{requested_indexes[1] + 1},{requested_indexes[2] + 1}</div>
        <div class="content">{escaped_text}</div>
        <div class="meta">{escape(filename)} • بخش‌های منتخب</div>
    </main>
</body>
</html>
"""

        return HTMLResponse(
            content=html_content,
            status_code=200,
            headers={
                "Content-Disposition": "inline; filename=preview.html",
                "Content-Type": "text/html; charset=utf-8",
            },
        )

    except HTTPException:
        raise

    except Exception as e:
        error = traceback.format_exc()
        logger.error(f"Error rendering HTML preview: {str(error)}")
        raise HTTPException(status_code=500, detail=f"Error rendering HTML preview: {str(e)}")
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
        if file_ext not in ['docx', 'doc', 'unknown']:
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
            try:
                search_record = {"fileId": file_id, "chunk_index": chunk_index}
                _, content_stream = mongo_db.get_file_from_collection(db_name, collection_name, search_record)
                content = content_stream.read()
                content_stream.close()
                if isinstance(content, bytes):
                    chunks.append(content.decode('utf-8', errors='replace'))
                else:
                    chunks.append(str(content))
            except Exception as e:
                logger.error(f"Error retrieving chunk {chunk_index}: {str(e)}")
                continue

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