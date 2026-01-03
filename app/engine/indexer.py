from sqlalchemy import create_engine, inspect
from llama_index.core import SQLDatabase, VectorStoreIndex
from llama_index.core.objects import SQLTableNodeMapping, ObjectIndex, SQLTableSchema
from app.core.config import settings

def build_schema_index():
    engine = create_engine(settings.DATABASE_URL)
    # 1. Connect to DB and inspect tables
    sql_database = SQLDatabase(engine)
    inspector = inspect(engine)
    table_names = inspector.get_table_names()

    # 2. Create Schema Objects (Metadata for the LLM)
    table_schema_objs = []
    for table in table_names:
        # Fetch columns to create a rich description
        columns = [col['name'] for col in inspector.get_columns(table)]
        table_text = f"Table: {table}. Columns: {', '.join(columns)}"
        
        table_schema_objs.append(
            SQLTableSchema(table_name=table, context_str=table_text)
        )

    # 3. Map Tables to Nodes
    node_mapping = SQLTableNodeMapping(sql_database)
    
    # 4. Create the Object Index (This indexes the metadata, not the data rows!)
    obj_index = ObjectIndex.from_objects(
        table_schema_objs,
        node_mapping,
        index_cls=VectorStoreIndex,
    )
    
    print("Schema Index built successfully!")
    return obj_index