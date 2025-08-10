#!/usr/bin/env python3
"""
SAIL to CGEN - Final Optimized Converter
Production-ready converter from YAML/JSON to S-expressions

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
    """Production-ready converter with comprehensive error handling"""
    
    def __init__(self, namespace_prefix: str = "data", pretty_print: bool = False):
        self.namespace_prefix = namespace_prefix
        self.pretty_print = pretty_print
        self.indent_level = 0
        self.indent_size = 2
    
    def convert(self, data: Any, key: str = None) -> str:
        """Main conversion method with type dispatch"""
        type_handlers = {
            dict: self._convert_dict,
            list: self._convert_list,
            str: self._convert_string,
            int: self._convert_number,
            float: self._convert_number,
            bool: self._convert_boolean,
            type(None): self._convert_null,
        }
        
        handler = type_handlers.get(type(data), self._convert_unknown)
        return handler(data, key)
    
    def _convert_dict(self, data: Dict, key: str = None) -> str:
        """Convert dictionary to S-expression"""
        items = []
        
        for k, v in data.items():
            # Special handling for dates
            if self._is_date_field(k, v):
                items.append(self._convert_date(v, k))
            # Special handling for items arrays
            elif k == 'items' and isinstance(v, list):
                items.append(self._convert_items_list(v, k))
            else:
                converted_value = self.convert(v)
                items.append(f"({self.namespace_prefix}:{k} {converted_value})")
        
        content = self._join_items(items)
        return content if key is None else content
    
    def _convert_list(self, data: List, key: str = None) -> str:
        """Convert list to S-expression"""
        items = [self.convert(item, 'item' if key == 'items' else None) for item in data]
        content = ' '.join(items)
        
        if key:
            return f"({self.namespace_prefix}:{key} {content})"
        return f"({content})"
    
    def _convert_items_list(self, data: List, key: str) -> str:
        """Special handling for items list"""
        items = [self.convert(item, 'item') for item in data]
        return f"({self.namespace_prefix}:{key} {' '.join(items)})"
    
    def _convert_string(self, data: str, key: str = None) -> str:
        """Convert string with intelligent formatting"""
        # Part numbers and IDs (alphanumeric starting with letter)
        if re.match(r'^[A-Z]\d+$', data):
            return f"'{data}"
        
        # Proper string escaping
        escaped = data.replace('\\', '\\\\').replace('"', '\\"')
        return f'"{escaped}"'
    
    def _convert_number(self, data: Union[int, float], key: str = None) -> str:
        """Convert numeric values"""
        return str(data)
    
    def _convert_boolean(self, data: bool, key: str = None) -> str:
        """Convert boolean to Scheme format"""
        return "#t" if data else "#f"
    
    def _convert_null(self, data: None, key: str = None) -> str:
        """Convert null/None to nil"""
        return "nil"
    
    def _convert_unknown(self, data: Any, key: str = None) -> str:
        """Fallback for unknown types"""
        return f'"{str(data)}"'
    
    def _is_date_field(self, key: str, value: Any) -> bool:
        """Detect date fields"""
        if not isinstance(value, str):
            return False
        
        date_keywords = ['date', 'timestamp', 'created', 'updated', 'time', 'when']
        if key.lower() in date_keywords:
            return True
        
        # Pattern-based detection
        date_patterns = [
            r'\d{4}-\d{2}-\d{2}',  # YYYY-MM-DD
            r'\d{2}/\d{2}/\d{4}',  # DD/MM/YYYY or MM/DD/YYYY
            r'\d{4}/\d{2}/\d{2}',  # YYYY/MM/DD
        ]
        
        return any(re.match(pattern, value) for pattern in date_patterns)
    
    def _convert_date(self, date_str: str, key: str) -> str:
        """Convert date string to make-date call"""
        try:
            formats = ['%Y-%m-%d', '%Y/%m/%d', '%d/%m/%Y', '%m/%d/%Y']
            
            for fmt in formats:
                try:
                    parsed_date = datetime.strptime(date_str, fmt)
                    return f"({self.namespace_prefix}:{key} (make-date {parsed_date.year} {parsed_date.month:02d} {parsed_date.day:02d}))"
                except ValueError:
                    continue
            
            # If parsing fails, treat as string
            return f"({self.namespace_prefix}:{key} \"{date_str}\")"
            
        except Exception:
            return f"({self.namespace_prefix}:{key} \"{date_str}\")"
    
    def _join_items(self, items: List[str]) -> str:
        """Join items with optional pretty printing"""
        if not self.pretty_print:
            return f"({' '.join(items)})"
        
        if not items:
            return "()"
        
        if len(items) == 1:
            return f"({items[0]})"
        
        # Multi-line formatting
        indent = '  ' * (self.indent_level + 1)
        formatted_items = f"\n{indent}" + f"\n{indent}".join(items) + f"\n{'  ' * self.indent_level}"
        return f"({formatted_items})"


def load_data(file_path: str) -> tuple[Any, str]:
    """Load and detect file format"""
    path = Path(file_path)
    
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    with open(path, 'r', encoding='utf-8') as file:
        content = file.read()
        
        # Format detection
        if path.suffix.lower() in ['.yaml', '.yml']:
            return yaml.safe_load(content), 'yaml'
        elif path.suffix.lower() == '.json':
            return json.loads(content), 'json'
        else:
            # Auto-detect
            try:
                data = json.loads(content)
                return data, 'json'
            except json.JSONDecodeError:
                try:
                    data = yaml.safe_load(content)
                    return data, 'yaml'
                except yaml.YAMLError:
                    raise ValueError("Unable to parse as JSON or YAML")


def print_usage():
    """Print usage information"""
    print("SAIL to CGEN - S-Expression Converter")
    print("Usage: python final_converter.py <input_file> [options]")
    print()
    print("Options:")
    print("  --pretty     Enable pretty printing with indentation")
    print("  --help       Show this help message")
    print()
    print("Supported formats: .json, .yaml, .yml")
    print("Auto-detects format if extension is missing")


def main():
    """Main entry point"""
    if len(sys.argv) < 2 or '--help' in sys.argv:
        print_usage()
        sys.exit(0 if '--help' in sys.argv else 1)
    
    input_file = sys.argv[1]
    pretty_print = '--pretty' in sys.argv
    
    try:
        # Load and convert
        data, format_type = load_data(input_file)
        converter = SExpressionConverter(namespace_prefix=format_type, pretty_print=pretty_print)
        s_expression = converter.convert(data)
        
        print(s_expression)
        
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Conversion error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
