from app.engine.indexer import build_schema_index
import os
from llama_index.core import StorageContext, load_index_from_storage
from app.engine.indexer import build_schema_index

PERSIST_DIR = "./storage"

def get_or_create_index():
    # Check if the storage directory exists and contains data
    if os.path.exists(PERSIST_DIR) and os.listdir(PERSIST_DIR):
        print("Loading index from local storage...")
        storage_context = StorageContext.from_defaults(persist_dir=PERSIST_DIR)
        index = load_index_from_storage(storage_context)
    else:
        print("Local index not found. Building and saving new schema index...")
        index = build_schema_index()
        # Ensure the directory exists and save the index
        index._index.storage_context.persist(persist_dir=PERSIST_DIR)
    
    return index

# Initialize once globally
obj_index = get_or_create_index()
# llm = OpenAI(model="gpt-4o-mini", temperature=0)

import logging

# Initialize logging to see errors in your console
logger = logging.getLogger(__name__)

def generate_sql_and_execute(user_query: str):
    try:
        # 1. Initialize the retriever
        # This can fail if obj_index is None or not initialized
        table_retriever = obj_index.as_retriever(similarity_top_k=5)

        # 2. Perform the retrieval
        # This is where the vector search happens; can fail on connection issues
        retrieved_nodes = table_retriever.retrieve(user_query)

        if not retrieved_nodes:
            return {
                "status": "success",
                "message": "No relevant tables found for the query.",
                "retrieved_items": []
            }

        # 3. Parse findings
        results = []
        for item in retrieved_nodes:

            table_name = "Unknown"
            score = 0
            content = ""
            
            # Check if it's a NodeWithScore object
            if hasattr(item, "node") and hasattr(item, "score"):
                # Standard LlamaIndex NodeWithScore behavior
                node = item.node
                table_name = node.metadata.get("table_name", "Unknown") if node.metadata else "Unknown"
                score = round(item.score, 4) if item.score else 0
                content = node.get_content()
            else:
                # Fallback: treat as object with table_name attribute
                table_name = getattr(item, "table_name", "Unknown")
                score = "N/A"
                content = str(item)
            
            print(f"Extracted table_name: {table_name}")
            print(f"Score: {score}")
            print(f"Content: {content}")

            results.append({
                "table_name": table_name,
                "score": score,
                "content_preview": content
            })
        
        return {
            "status": "success",
            "retrieved_items": results
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