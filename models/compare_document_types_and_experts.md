# Comparison: DocumentType and Expert Models

## Documentation Structure Inconsistencies

1. **Method Documentation Format:**
   - `Expert.md` has more detailed method documentation with clear "Parameters" and "Returns" sections
   - `DocumentType.md` has inconsistent method documentation - some methods lack parameter/return details

2. **Constructor Documentation:**
   - `DocumentType.md` documents the constructor
   - `Expert.md` doesn't mention a constructor at all

## Properties Comparison

### Common Properties
- `id` (uuid)
- `created_at`
- `updated_at`
- `created_by`
- `updated_by`
- `domain_id`
- `is_active`
- `legacy_*_id`

### Inconsistencies in Property Types
- Timestamp types are inconsistent:
  - `Expert`: uses "timestamp"
  - `DocumentType`: uses "Date"

## Method Comparison

### Common Methods
- `add()`
- `get_all()`
- `get_plus_by_name()`
- `get_by_id()`
- `update()`
- `delete()`
- Both have alias-related methods

### Inconsistencies

1. **Async/Promise Handling:**
   - `DocumentType.md` explicitly mentions async/Promise returns
   - `Expert.md` doesn't specify if methods are async

2. **Parameter Types:**
   - `DocumentType.md` uses "string" type
   - `Expert.md` uses "str" type (Python-style)

3. **Return Types:**
   - `Expert.md` uses `dict | None` format
   - `DocumentType.md` uses `Promise<Object>` format

## Recommendations for Improvement

1. **Standardize Method Documentation:**
   - Use consistent format for Parameters and Returns sections
   - Standardize type naming (`string` vs `str`)
   - Clearly document async/Promise behavior

2. **Constructor Documentation:**
   - Add constructor documentation to `Expert.md`
   - Or remove it from `DocumentType.md` if not needed

3. **Type Consistency:**
   - Use consistent date/timestamp type names
   - Standardize return type documentation format

4. **Optional Parameters:**
   - Standardize how optional parameters are marked (? vs optional)
   - Use consistent format for default values

5. **Alias Management:**
   - Consider moving alias-related methods to a separate section in both docs
   - Use consistent method names (`get_aliases_by_expert_name` vs `get_aliases_by_document_type`) 