# SAIL to CGEN - Coding Challenge Solution

## Problem Statement
Convert structured data (JSON/YAML) to S-expression representation with well-defined schema and transformation semantics.

## Solution Overview
- **Input**: YAML/JSON files with structured data
- **Output**: S-expressions in Scheme/Lisp dialect
- **Language**: Python (for flexibility and robust parsing)
- **Features**: 
  - Type-aware conversion
  - Proper escaping and quoting
  - Nested structure handling
  - Multiple input formats support

## Schema Definition
- Strings: Convert to quoted strings with proper escaping
- Numbers: Convert to numeric literals
- Booleans: Convert to #t/#f
- Lists/Arrays: Convert to lists
- Objects/Maps: Convert to association lists with typed prefixes
- Dates: Convert to `make-date` function calls
- Null/None: Convert to `nil`

## Transformation Semantics
1. Preserve data types with appropriate Scheme representations
2. Use prefixed symbols (yaml:, json:) to maintain namespace
3. Recursive descent for nested structures
4. Special handling for common patterns (dates, quoted strings)

## Usage
```bash
python converter.py input.yaml
python converter.py input.json
```
