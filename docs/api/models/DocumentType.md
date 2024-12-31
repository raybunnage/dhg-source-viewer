[Back to README](../../README.md)

# DocumentType Class Documentation

## Overview
The `DocumentType` class represents different types of documents that can be processed in the system.

## Properties

| Property | Type | Description |
|----------|------|-------------|
| id | uuid | Unique identifier for the document type (auto-generated) |
| domain_id | uuid | Domain identifier (defaults to system domain) |
| document_type | string | Name of the document type |
| current_num_of_type | integer | Current count of documents of this type |
| description | string | Detailed description of the document type (optional) |
| mime_type | string | MIME type of the document (optional) |
| file_extension | string | File extension for the document type (optional) |
| document_type_counts | integer | Total count of documents of this type |
| category | string | Category of the document type (defaults to 'tbd') |
| is_active | boolean | Flag indicating if the document type is active (defaults to true) |
| created_by | uuid | ID of the user who created the document type |
| updated_by | uuid | ID of the user who last updated the document type |
| created_at | Date | Timestamp of when the document type was created |
| updated_at | Date | Timestamp of last update |
| version | integer | Version number of the document type (defaults to 1) |
| required_fields | object | JSON object defining required fields for this document type |
| legacy_document_type_id | bigint | ID reference to legacy system (optional) |
| is_ai_generated | boolean | Flag indicating if the document type is AI-generated (defaults to false) |

## Methods

### constructor(supabase_client)
Creates a new DocumentTypes instance.

**Parameters:**
- `supabase_client` (SupabaseClient): Supabase client instance for database operations

**Returns:**
- `DocumentType`: A new DocumentType instance

### async add(document_type, description?, mime_type?, file_extension?, category?, is_ai_generated?, additional_fields?)
Creates a new document type in the database.

**Parameters:**
- `document_type` (string): Name of the document type
- `description` (string, optional): Detailed description of the document type
- `mime_type` (string, optional): MIME type of the document (e.g., 'application/pdf')
- `file_extension` (string, optional): File extension without dot (e.g., 'pdf')
- `category` (string, optional): Category classification (defaults to 'tbd')
- `is_ai_generated` (boolean, optional): Whether the document is AI-generated (defaults to false)
- `additional_fields` (object, optional): Additional custom fields to store with the document type

**Returns:**
- `Promise<Object>`: The created document type object with all properties

### async get_by_id(document_type_id)
Retrieves a document type by its unique identifier.

**Parameters:**
- `document_type_id` (uuid): Unique identifier of the document type

**Returns:**
- `Promise<Object|null>`: The document type object if found, null otherwise

### async update(document_type_id, update_data)
Updates an existing document type with new data.

**Parameters:**
- `document_type_id` (uuid): Unique identifier of the document type to update
- `update_data` (object): Object containing fields to update. Valid fields include:
  - `document_type` (string, optional): New name
  - `description` (string, optional): New description
  - `mime_type` (string, optional): New MIME type
  - `file_extension` (string, optional): New file extension
  - `category` (string, optional): New category
  - `is_active` (boolean, optional): New active status
  - `required_fields` (object, optional): New required fields definition

**Returns:**
- `Promise<Object>`: The updated document type object

### async get_all(additional_fields?)
Retrieves all document types from the database.

**Parameters:**
- `additional_fields` (string[], optional): Array of additional fields to include in the response

**Returns:**
- `Promise<Object[]>`: Array of document type objects

### async get_plus_by_name(document_type, optional_fields?)
Retrieves a document type by name with optional additional fields.

**Parameters:**
- `document_type` (string): Name of the document type to retrieve
- `optional_fields` (string[], optional): Array of additional fields to include in the response

**Returns:**
- `Promise<Object|null>`: The document type object with requested fields if found, null otherwise

### async delete(document_type_id)
Deletes a document type from the database.

**Parameters:**
- `document_type_id` (uuid): Unique identifier of the document type to delete

**Returns:**
- `Promise<void>`: Resolves when deletion is complete

### async get_aliases_by_document_type(document_type)
Retrieves all aliases associated with a document type.

**Parameters:**
- `document_type` (string): Name of the document type to get aliases for

**Returns:**
- `Promise<string[]>`: Array of alias strings for the document type 