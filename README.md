# Column Pruning & Metadata Filtering for NL → SQL

## Why This Matters

Real-world databases have hundreds of tables and thousands of columns. Passing the full schema into an NL → SQL system leads to:
- High token usage and cost
- Slower inference
- Ambiguous joins
- Incorrect SQL generation

## Column Pruning

Column pruning selects only the **minimal set of columns** needed to answer a user query (metrics, dimensions, time fields), removing irrelevant or technical columns.

## Metadata Filtering

Metadata adds business meaning to raw schemas and helps:
- Map natural language to columns
- Distinguish metrics vs dimensions
- Infer safe joins
- Avoid legacy or unused fields

## Key Idea

> **NL → SQL accuracy depends more on schema reduction than prompt quality.**

Column pruning and metadata filtering are essential for scalable, reliable NL → SQL workflows.
