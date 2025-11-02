import re

from .state import SmartSQLPipelineState
from db import sql_manager
from llm import sql_generation_llm
from utils.logger import logger

PERSIAN_SQL_PROMPT = (
    "You are a SQL expert. Given an input question in Persian, first understand the intent,"
    "then create a SQL query in T-SQL format for microsoft my sql server that answers the question.\n"
    "Schema information:\n"
    "{schema}\n"
    "Core Table Definitions\n"
    "1. tblAKHDossier (Main Table)\n"
    "Each row in tblAKHDossier represents a single dossier (case file).\n"
    "A dossier may contain metadata such as:\n"
    "- Identification (ID) --> Example : 'پرونده شماره 142' --> ID = 142"
    "- tracking fields (Code, FoldNo, CreateDate, etc.)\n"
    "- Legal and administrative attributes (JudicatoryGeographicalLocationID, FolderTypeID, StatusTypeID, ResualtID, etc.)\n"
    "- References to people, lawyers, clerks, and geographical areas (ComplainID, ConvictID, ClerkID, AdviserID, etc.)\n"
    "- Property or asset information (PropertyType, Area, Monetaryvalue, MelkNo, Block, etc.)\n"
    "- Status and result tracking (StatusID, ResualtDate, DossierImportanceTypeID, etc.)\n"
    "- Textual or descriptive notes (Note, DossierNikName, RefrenceName, etc.)\n\n"
    "This table is the central entity — all other dossier-related tables connect directly or indirectly to it.\n"
    "Each row = One legal/administrative dossier record.\n\n"
    "2. tblAKHDossierRow (Document Table)\n"
    "Each row in tblAKHDossierRow represents a document or action item related to a specific dossier.\n"
    "It is linked to tblAKHDossier via the DossierID field.\n\n"
    "A tblAKHDossierRow maybe called these in persian : زیرپرونده اطلاعات پرونده پرونده های جانبی"
    "A dossier can have multiple rows (documents), such as:\n"
    "- Incoming/outgoing communications (KindEnterExitID, SenderPersonID, ReceiverPersonID)\n"
    "- Document metadata (DocCode, KindDocID, GroupID, DoneDate, DocDate, AnswerDate)\n"
    "- Legal details (KindDocLegalNatureID, ExpertJusticeTypeLID, CertaintyID)\n"
    "- References to sources and sub-documents (SourceId, SourceTable, SourceId2, SourceTable2)\n"
    "- Descriptive or HTML notes (Notes, Notes_HTML)\n\n"
    "Each row = One document, correspondence, or step within a dossier.\n\n"
    "Relationship Summary:\n"
    "- tblAKHDossierRow.DossierID → tblAKHDossier.ID : Links documents to their parent dossier\n"
    "- tblAKHDossier ↔ Other tables (e.g., tblPerson, tblAKHClerk, tblAKHLawyer) : Provides contextual information\n"
    "- Type tables ending with 'TypeL' (e.g., tblAKHDossierStatusTypeL, tblAKHKindDocTypeL) : Contain description labels for status, kind, or classification fields\n\n"
    "Instructions for the Model:\n"
    "- Treat tblAKHDossier as the main entity describing a dossier or case.\n"
    "- Treat tblAKHDossierRow as the collection of related documents or actions belonging to that dossier.\n"
    "- Use foreign keys and type tables to interpret meaning (e.g., status IDs, result types, geographical locations).\n"
    "- Try to be thorough when getting the information and get tables id mentioned in the main id as well.\n"
    "- Notes and fields that have text should be used when the user asks for final results or the subjects of a dossier"
    "Question in Persian: {question}\n\n"
    "Note: Use proper T-SQL syntax and consider Persian text encoding in filters.\n"
    "The query should be executable and include only the necessary columns.\n"
    "Do not include any explanations, only return the SQL query.\n\n"
    "SQL Query:"
)

def clean_sql(sql: str) -> str:
    # Remove Markdown code fences like ```sql ... ```
    return re.sub(r"^```(?:sql)?|```$", "", sql.strip(), flags=re.MULTILINE).strip()

def generate_sql(question: str) -> str:
    """Generate SQL query from Persian question"""

    schema = sql_manager.get_combined_schema()
    prompt = PERSIAN_SQL_PROMPT.format(question=question, schema=schema)

    response = sql_generation_llm.llm.invoke([{"role": "user", "content": prompt}])

    sql_query = response.content.strip()
    sql_query = clean_sql(sql_query)

    logger.info(f"================\n\n{sql_query}\n\n=================")
    
    return sql_query

def execute_sql(state: SmartSQLPipelineState) -> str:
    """Execute SQL to get information rows"""

    question = state["messages"][-1].content

    for _ in range(2):
        result = ""
        try:
            sql_query = generate_sql(question)
            extracted_data = sql_manager.execute_sql(sql_query)

            for row in extracted_data:
                for key in row.keys():
                    result += f"{key}: {row[key]}"
                result += "\n"
            break
        except Exception as e:
            logger.info(f"Sql error : {str(e)}")

    return {"messages": [{"role": "user", "content": result}]}