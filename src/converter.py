#!/usr/bin/env python3
"""
SAIL to CGEN - Coding Challenge
Converter from YAML/JSON to S-expressions

Author: GitHub Copilot Solution
Date: August 10, 2025
"""

import json
import yaml
import sys
import re
from datetime import datetime
from typing import Any, Dict, List, Union
from pathlib import Path


class SExpressionConverter:
    """Converts structured data to S-expression format"""
    
    def __init__(self, namespace_prefix: str = "yaml"):
        self.namespace_prefix = namespace_prefix
        self.indent_level = 0
        self.indent_size = 2
    
    def convert(self, data: Any, key: str = None) -> str:
        """Main conversion method"""
        if isinstance(data, dict):
            return self._convert_dict(data, key)
        elif isinstance(data, list):
            return self._convert_list(data, key)
        elif isinstance(data, str):
            return self._convert_string(data, key)
        elif isinstance(data, (int, float)):
            return self._convert_number(data, key)
        elif isinstance(data, bool):
            return self._convert_boolean(data, key)
        elif data is None:
            return self._convert_null(data, key)
        else:
            return self._convert_unknown(data, key)
    
    def _convert_dict(self, data: Dict, key: str = None) -> str:
        """Convert dictionary to S-expression"""
        items = []
        
        for k, v in data.items():
            # Special handling for common patterns
            if self._is_date_field(k, v):
                items.append(self._convert_date(v, k))
            elif k in ['items'] and isinstance(v, list):
                items.append(self._convert_items_list(v, k))
            else:
                converted_value = self.convert(v)
                items.append(f"({self.namespace_prefix}:{k} {converted_value})")
        
        if key:
            return f"({self.namespace_prefix}:{key} {' '.join(items)})"
        else:
            return f"({' '.join(items)})"
    
    def _convert_list(self, data: List, key: str = None) -> str:
        """Convert list to S-expression"""
        items = []
        for item in data:
            if isinstance(item, dict) and key == 'items':
                # Special handling for items list
                items.append(self.convert(item, 'item'))
            else:
                items.append(self.convert(item))
        
        list_content = ' '.join(items)
        if key:
            return f"({self.namespace_prefix}:{key} {list_content})"
        else:
            return f"({list_content})"
    
    def _convert_items_list(self, data: List, key: str) -> str:
        """Special handling for items list"""
        items = []
        for item in data:
            items.append(self.convert(item, 'item'))
        return f"({self.namespace_prefix}:{key} {' '.join(items)})"
    
    def _convert_string(self, data: str, key: str = None) -> str:
        """Convert string with proper escaping"""
        # Check if it's a part number or ID (starts with letter+numbers)
        if re.match(r'^[A-Z]\d+$', data):
            return f"'{data}"
        
        # Escape quotes and special characters
        escaped = data.replace('\\', '\\\\').replace('"', '\\"')
        return f'"{escaped}"'
    
    def _convert_number(self, data: Union[int, float], key: str = None) -> str:
        """Convert number"""
        return str(data)
    
    def _convert_boolean(self, data: bool, key: str = None) -> str:
        """Convert boolean to Scheme format"""
        return "#t" if data else "#f"
    
    def _convert_null(self, data: None, key: str = None) -> str:
        """Convert null to nil"""
        return "nil"
    
    def _convert_unknown(self, data: Any, key: str = None) -> str:
        """Convert unknown types"""
        return f'"{str(data)}"'
    
    def _is_date_field(self, key: str, value: Any) -> bool:
        """Check if field represents a date"""
        date_keywords = ['date', 'timestamp', 'created', 'updated', 'time']
        return key.lower() in date_keywords and isinstance(value, str)
    
    def _convert_date(self, date_str: str, key: str) -> str:
        """Convert date string to make-date call"""
        try:
            # Try to parse common date formats
            formats = ['%Y-%m-%d', '%Y/%m/%d', '%d/%m/%Y', '%m/%d/%Y']
            parsed_date = None
            
            for fmt in formats:
                try:
                    parsed_date = datetime.strptime(date_str, fmt)
                    break
                except ValueError:
                    continue
            
            if parsed_date:
                return f"({self.namespace_prefix}:{key} (make-date {parsed_date.year} {parsed_date.month:02d} {parsed_date.day:02d}))"
            else:
                # If parsing fails, treat as string
                return f"({self.namespace_prefix}:{key} \"{date_str}\")"
        except:
            return f"({self.namespace_prefix}:{key} \"{date_str}\")"


def load_data(file_path: str) -> Any:
    """Load data from YAML or JSON file"""
    path = Path(file_path)
    
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    with open(path, 'r', encoding='utf-8') as file:
        if path.suffix.lower() in ['.yaml', '.yml']:
            return yaml.safe_load(file), 'yaml'
        elif path.suffix.lower() == '.json':
            return json.load(file), 'json'
        else:
            # Try to detect format
            content = file.read()
            file.seek(0)
            
            try:
                return yaml.safe_load(file), 'yaml'
            except:
                try:
                    return json.loads(content), 'json'
                except:
                    raise ValueError("Unable to parse file as YAML or JSON")


def main():
    """Main function"""
    if len(sys.argv) != 2:
        print("Usage: python converter.py <input_file>")
        print("Supported formats: .yaml, .yml, .json")
        sys.exit(1)
    
    input_file = sys.argv[1]
    
    try:
        # Load data
        data, format_type = load_data(input_file)
        
        # Convert to S-expression
        converter = SExpressionConverter(namespace_prefix=format_type)
        s_expression = converter.convert(data)
        
        # Output result
        print(s_expression)
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
