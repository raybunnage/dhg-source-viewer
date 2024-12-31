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
- `supabase_client`: Supabase client instance for database operations

### async add(document_type, description?, mime_type?, file_extension?, category?, is_ai_generated?, additional_fields?)
Creates a new document type.

**Parameters:**
- `document_type` (string): Name of the document type
- `description` (string, optional): Description of the document type
- `mime_type` (string, optional): MIME type
- `file_extension` (string, optional): File extension
- `category` (string, optional): Category
- `is_ai_generated` (boolean, optional): Whether the document is AI-generated
- `additional_fields` (object, optional): Any additional fields to store

**Returns:**
- `Promise<Object>` - The created document type

### async get_by_id(document_type_id)
Retrieves a document type by ID.

### async update(document_type_id, update_data)
Updates an existing document type.

### async get_all(additional_fields?)
Retrieves all document types.

### async get_plus_by_name(document_type, optional_fields?)
Retrieves a document type by name with optional additional fields.

### async delete(document_type_id)
Deletes a document type.

### async get_aliases_by_document_type(document_type)
Retrieves aliases for a document type. 