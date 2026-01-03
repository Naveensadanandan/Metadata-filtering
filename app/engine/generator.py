from llama_index.core.indices.struct_store import SQLTableRetrieverQueryEngine
from llama_index.llms.openai import OpenAI
from app.engine.indexer import build_schema_index
from app.core.config import settings

# Initialize once
obj_index = build_schema_index()
llm = OpenAI(model="gpt-4-turbo", temperature=0)

def generate_sql_and_execute(user_query: str):
    # 1. Retrieve specific tables
    # This retriever looks at the vectors we built in Step B
    # It filters out 90% of the irrelevant tables.
    table_retriever = obj_index.as_retriever(similarity_top_k=5)

    # 2. Create the Query Engine with the filtered schema
    query_engine = SQLTableRetrieverQueryEngine(
        sql_database=obj_index._object_node_mapping.sql_database,
        table_retriever=table_retriever,
        llm=llm
    )

    # 3. Execute (RAG Flow: Retrieve Schema -> Generate SQL -> Run SQL)
    response = query_engine.query(user_query)
    
    # Return both the answer and the raw SQL for transparency
    return {
        "answer": str(response),
        "generated_sql": response.metadata.get("sql_query", "N/A")
    }