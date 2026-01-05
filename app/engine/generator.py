from app.engine.indexer import build_schema_index
import os
from llama_index.core import StorageContext, load_index_from_storage
from app.engine.indexer import build_schema_index
import logging

# Initialize logging to see errors in your console
logger = logging.getLogger(__name__)

PERSIST_DIR_SCHEMA = "./storage/schema"
PERSIST_DIR_COLUMN = "./storage/column"

def get_or_create_index():
    # Check if the storage directory exists and contains data
    if os.path.exists(PERSIST_DIR_SCHEMA) and os.path.exists(PERSIST_DIR_COLUMN):
        print("Loading index from local storage...")
        storage_context_schema = StorageContext.from_defaults(persist_dir=PERSIST_DIR_SCHEMA)
        storage_context_column = StorageContext.from_defaults(persist_dir=PERSIST_DIR_COLUMN)
        index_schema = load_index_from_storage(storage_context_schema)
        index_column = load_index_from_storage(storage_context_column)
    else:
        print("Local index not found. Building and saving new schema index...")
        index_schema, index_column = build_schema_index()
        # Ensure the directory exists and save the index
        index_schema._index.storage_context.persist(persist_dir=PERSIST_DIR_SCHEMA)
        index_column.storage_context.persist(persist_dir=PERSIST_DIR_COLUMN)

    
    return index_schema, index_column

def generate_sql_and_execute(user_query: str):
    try:
        # 1. Initialize the retriever
        # This can fail if obj_index is None or not initialized
        sch_index, col_index= get_or_create_index()
        table_retriever = sch_index.as_retriever(similarity_top_k=5)
        column_retriever = col_index.as_retriever(similarity_top_k=10)

        # 2. Perform the retrieval
        # This is where the vector search happens; can fail on connection issues
        retrieved_nodes= table_retriever.retrieve(user_query)
        retrieved_nodes_col= column_retriever.retrieve(user_query)

        if not retrieved_nodes and not columns:
            return {
                "status": "success",
                "message": "No relevant tables or columns found for the query.",
                "retrieved_items": []
            }

        # 3. Parse findings
        results = []
        results_col = []
        for item in retrieved_nodes:

            table_name = "Unknown"
            score = 0
            content = ""
            columns = ""
            
            # Check if it's a NodeWithScore object
            if hasattr(item, "node") and hasattr(item, "score"):
                # Standard LlamaIndex NodeWithScore behavior
                node = item.node
                table_name = node.metadata.get("name", "Unknown") if node.metadata else "Unknown"
                score = round(item.score, 4) if item.score else 0
                content = node.get_content()
            else:
                # Fallback: treat as object with table_name attribute
                table_name = getattr(item, "table_name", "Unknown")
                score = "N/A"
                content = str(item)

            results.append({
                "table_name": table_name,
                "score": score,
                "content_preview": content
            })
        
        for item in retrieved_nodes_col:
            if hasattr(item, "node") and hasattr(item, "score"):
                # Standard LlamaIndex NodeWithScore behavior
                node = item.node
                col_name = node.metadata if node.metadata else "Unknown"
                score = round(item.score, 4) if item.score else 0
            else:
                # Fallback: treat as object with table_name attribute
                col_name = getattr(item, "table_name", "Unknown")
                score = "N/A"

            results_col.append({
                "col_name": col_name,
                "score": score
            })

        
        return {
            "status": "success",
            "retrieved_items": results,
            "retrieved_columns": results_col,
            "message": None,
            "error_type": None
        }

    except AttributeError as e:
        logger.error(f"Index Error: Ensure obj_index is properly initialized. Details: {e}")
        return {"status": "error", "error_type": "InitializationError", "message": str(e)}

    except Exception as e:
        # Catch-all for unexpected issues (Vector DB timeouts, etc.)
        logger.exception("An unexpected error occurred during table retrieval")
        return {
            "status": "error",
            "error_type": type(e).__name__,
            "message": "Failed to retrieve tables. Check server logs for details."
        }