[Back to README](../README.md)

# Supabase Service API Documentation

## Overview
The `SupabaseService` class provides methods for interacting with Supabase database tables, handling authentication, and performing CRUD operations.

## Methods

### select_from_table(table_name: str, fields: dict, where_filters: list = None)
Retrieves records from a specified table with optional filtering.

**Parameters:**
- `table_name` (str): Name of the table to query
- `fields` (dict): Fields to select (use "*" for all fields)
- `where_filters` (list, optional): List of filter tuples in format (column, operator, value)

**Returns:**
- `dict | None` - Query results or None if failed

### update_table(table_name: str, update_fields: dict, where_filters: list)
Updates records in a specified table that match the given filters.

**Parameters:**
- `table_name` (str): Name of the table to update
- `update_fields` (dict): Fields and values to update
- `where_filters` (list): List of filter tuples in format (column, operator, value)

**Returns:**
- `dict | None` - Updated record or None if failed

### insert_into_table(table_name: str, insert_fields: dict, upsert: bool = False)
Inserts new records into a specified table.

**Parameters:**
- `table_name` (str): Name of the table to insert into
- `insert_fields` (dict): Fields and values to insert
- `upsert` (bool, optional): Whether to perform an upsert operation

**Returns:**
- `dict | None` - Inserted record or None if failed

### delete_from_table(table_name: str, where_filters: list)
Deletes records from a specified table that match the given filters.

**Parameters:**
- `table_name` (str): Name of the table to delete from
- `where_filters` (list): List of filter tuples in format (column, operator, value)

**Returns:**
- `bool` - True if deletion was successful, False otherwise

### login(email: str, password: str)
Authenticates a user with Supabase.

**Parameters:**
- `email` (str): User's email address
- `password` (str): User's password

**Returns:**
- Authentication data or None if failed

### logout()
Signs out the current user.

**Returns:**
- None

### reset_password(email: str)
Sends a password reset email to the specified address.

**Parameters:**
- `email` (str): Email address to send reset link to

**Returns:**
- `bool` - True if reset email was sent successfully, False otherwise 