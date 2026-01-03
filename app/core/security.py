def is_safe_sql(sql: str) -> bool:
    forbidden = ["DROP", "DELETE", "ALTER", "TRUNCATE", "GRANT", "REVOKE"]
    upper_sql = sql.upper()
    return not any(cmd in upper_sql for cmd in forbidden)