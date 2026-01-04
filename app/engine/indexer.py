from sqlalchemy import create_engine, inspect
from llama_index.core import SQLDatabase, VectorStoreIndex, Settings
from llama_index.core.objects import (
    SQLTableNodeMapping,
    ObjectIndex,
    SQLTableSchema,
)
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from app.core.config import settings
Settings.llm = None
Settings.embed_model = HuggingFaceEmbedding(
        model_name="BAAI/bge-small-en-v1.5"
    )

def build_schema_index():
    # 2. Connect to DB
    engine = create_engine(settings.DATABASE_URL)
    sql_database = SQLDatabase(engine)
    inspector = inspect(engine)
    table_names = inspector.get_table_names()

    # 3. Create schema metadata objects
    table_schema_objs = []
    for table in table_names:
        columns = [col["name"] for col in inspector.get_columns(table)]
        table_text = f"Table: {table}. Columns: {', '.join(columns)}"

        table_schema_objs.append(
            SQLTableSchema(
                table_name=table,
                context_str=table_text,
            )
        )

    # 4. Map tables to nodes
    node_mapping = SQLTableNodeMapping(sql_database)

    # 5. Create object index using local embeddings
    obj_index = ObjectIndex.from_objects(
        table_schema_objs,
        node_mapping,
        index_cls=VectorStoreIndex,
    )

    print("Schema Index built successfully with local embeddings!")
    return obj_index
