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

### add(expert_name: str, full_name: str, email_address: str = None, additional_fields: dict = None)
Creates a new expert record.

**Parameters:**
- `expert_name` (str): Unique name identifier for the expert
- `full_name` (str): Full name of the expert
- `email_address` (str, optional): Email address
- `additional_fields` (dict, optional): Additional expert information

**Returns:**
- `dict | None` - Created expert record or None if failed

### get_all(additional_fields: dict = None)
Retrieves all active experts.

**Returns:**
- `list | None` - List of expert records or None if none found

### get_plus_by_name(expert_name: str, optional_fields: dict = None)
Retrieves an expert by their expert_name.

**Parameters:**
- `expert_name` (str): Expert's unique name identifier
- `optional_fields` (dict, optional): Additional fields to retrieve

**Returns:**
- `dict | None` - Expert record or None if not found

### get_by_id(expert_id: str)
Retrieves an expert by their ID.

**Parameters:**
- `expert_id` (str): Expert's unique identifier

**Returns:**
- `dict | None` - Expert record or None if not found

### update(expert_id: str, update_data: dict)
Updates an expert's information.

**Parameters:**
- `expert_id` (str): Expert's unique identifier
- `update_data` (dict): Fields to update

**Returns:**
- `dict | None` - Updated expert record or None if failed

### delete(expert_id: str)
Deletes an expert record.

**Parameters:**
- `expert_id` (str): Expert's unique identifier

**Returns:**
- `bool` - True if successful, False otherwise

## Alias Management

### add_alias(expert_name: str, alias_name: str)
Adds an alias for an expert.

**Parameters:**
- `expert_name` (str): Expert's name identifier
- `alias_name` (str): Alias to add

**Returns:**
- `dict | None` - Created alias record or None if failed

### get_aliases_by_expert_name(expert_name: str)
Retrieves all aliases for an expert.

**Parameters:**
- `expert_name` (str): Expert's name identifier

**Returns:**
- `list | None` - List of alias records or None if none found

### delete_alias(alias_id: str)
Deletes an expert alias.

**Parameters:**
- `alias_id` (str): Alias unique identifier

**Returns:**
- `bool` - True if successful, False otherwise 