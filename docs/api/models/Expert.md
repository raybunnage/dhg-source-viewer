[Back to README](../../README.md)

# Expert Class Documentation

## Overview
The `Expert` class represents a professional expert in the system, with support for aliases and core group membership.

## Properties

| Property | Type | Description |
|----------|------|-------------|
| id | uuid | Unique identifier for the expert (auto-generated) |
| expert_name | text | Unique name identifier for the expert (required) |
| full_name | text | Full name of the expert (required) |
| starting_ref_id | integer | Reference ID for the expert |
| is_in_core_group | boolean | Whether the expert is in the core group (defaults to false) |
| created_at | timestamp | Creation timestamp (auto-set) |
| updated_at | timestamp | Last update timestamp (auto-set) |
| created_by | uuid | ID of user who created the record |
| updated_by | uuid | ID of user who last updated the record |
| domain_id | uuid | Associated domain identifier |
| user_id | uuid | Associated user identifier |
| expertise_area | text | Area of expertise (defaults to 'General Knowledge') |
| bio | text | Expert's biography (defaults to 'No biography provided') |
| experience_years | integer | Years of experience (defaults to 0) |
| is_active | boolean | Whether the expert is currently active (defaults to true) |
| email_address | text | Email address (must be unique) |
| legacy_expert_id | bigint | Legacy system identifier |

## Methods

### async add(expert_name: str, full_name: str, email_address: str = None, additional_fields: dict = None)
Asynchronously creates a new expert record.

**Parameters:**
- `expert_name` (str): Unique name identifier for the expert
- `full_name` (str): Full name of the expert
- `email_address` (str, optional): Email address
- `additional_fields` (dict, optional): Additional expert information

**Returns:**
- `Promise<Object|null>`: Resolves to the created expert record or null if creation failed

### async get_all(additional_fields: dict = None)
Asynchronously retrieves all active experts.

**Returns:**
- `Promise<Object[]|null>`: Resolves to an array of expert records or null if none found

### async get_plus_by_name(expert_name: str, optional_fields: dict = None)
Asynchronously retrieves an expert by their expert_name.

**Parameters:**
- `expert_name` (str): Expert's unique name identifier
- `optional_fields` (dict, optional): Additional fields to retrieve

**Returns:**
- `Promise<Object|null>`: Resolves to the expert record or null if not found

### async get_by_id(expert_id: str)
Asynchronously retrieves an expert by their ID.

**Parameters:**
- `expert_id` (str): Expert's unique identifier

**Returns:**
- `Promise<Object|null>`: Resolves to the expert record or null if not found

### async update(expert_id: str, update_data: dict)
Asynchronously updates an expert's information.

**Parameters:**
- `expert_id` (str): Expert's unique identifier
- `update_data` (dict): Fields to update

**Returns:**
- `Promise<Object|null>`: Resolves to the updated expert record or null if update failed

### async delete(expert_id: str)
Asynchronously deletes an expert record.

**Parameters:**
- `expert_id` (str): Expert's unique identifier

**Returns:**
- `Promise<boolean>`: Resolves to true if deletion was successful, false otherwise

## Alias Management

### async add_alias(expert_name: str, alias_name: str)
Asynchronously adds an alias for an expert.

**Parameters:**
- `expert_name` (str): Expert's name identifier
- `alias_name` (str): Alias to add

**Returns:**
- `Promise<Object|null>`: Resolves to the created alias record or null if creation failed

### async get_aliases_by_expert_name(expert_name: str)
Asynchronously retrieves all aliases for an expert.

**Parameters:**
- `expert_name` (str): Expert's name identifier

**Returns:**
- `Promise<Object[]|null>`: Resolves to an array of alias records or null if none found

### async delete_alias(alias_id: str)
Asynchronously deletes an expert alias.

**Parameters:**
- `alias_id` (str): Alias unique identifier

**Returns:**
- `Promise<boolean>`: Resolves to true if deletion was successful, false otherwise 