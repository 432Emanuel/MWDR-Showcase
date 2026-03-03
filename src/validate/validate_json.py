#!/usr/bin/env python3
"""
JSON Validator for MWDR Showcase.

Usage:
    python src/validate/validate_json.py
    python src/validate/validate_json.py --path data/
    python src/validate/validate_json.py --schema standard_node
    python src/validate/validate_json.py --json-report report.json
    python src/validate/validate_json.py --routing-config src/validate/schema_routing.json
"""

import argparse
import fnmatch
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    from jsonschema import ValidationError, validate

    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False
    ValidationError = Exception


class JSONValidator:
    """Validator for JSON files with explicit schema routing and quality metrics."""

    def __init__(
        self,
        root_path: str = ".",
        forced_schema: Optional[str] = None,
        routing_config: Optional[str] = None
    ):
        # Scan root: controls which files are traversed by --path.
        self.root_path = Path(root_path).resolve()
        self.forced_schema = forced_schema
        self.routing_config_path = routing_config
        self.routing_rules: List[Dict[str, str]] = []
        self.schema_cache: Dict[str, Dict[str, Any]] = {}
        self.repo_root = self._determine_repo_root()
        self.routing_config_resolved_path: Optional[Path] = None
        
        if self.routing_config_path:
            self._load_routing_config()

        # Built-in schemas for backward compatibility
        self.builtin_schemas: Dict[str, Dict[str, Any]] = {
            "standard_node": {
                "type": "object",
                "required": ["id", "name"],
                "properties": {
                    "id": {"type": "string"},
                    "name": {"type": "string"},
                    "description": {"type": "string"},
                    "type": {"type": "string"},
                    "metadata": {"type": "object"},
                    "epistemic_layer": {"type": "string", "pattern": "^L[0-4]$"},
                    "resonance_layer": {"type": "string", "pattern": "^R[0-5]$"},
                },
            },
            "human_cartography_individual": {
                "type": "object",
                "required": ["individual_id", "name", "potential_position"],
                "properties": {
                    "individual_id": {"type": "string"},
                    "name": {"type": "string"},
                    "birth_year": {"type": "integer"},
                    "nationality": {"type": "string"},
                    "potential_position": {"type": "object"},
                    "world_edges": {"type": "array"},
                    "metadata": {"type": "object"},
                },
            },
            "build_on_old": {
                "type": "object",
                "required": ["metadata"],
                "properties": {
                    "concepts": {"type": "array"},
                    "patterns": {"type": "array"},
                    "rules": {"type": "array"},
                    "metadata": {"type": "object"},
                },
            },
        }

        self.metrics = {
            "total_files_scanned": 0,
            "parsed_ok": 0,
            "syntax_errors": 0,
            "schema_valid": 0,
            "schema_invalid": 0,
            "schema_missing": 0,
        }

        self.syntax_error_items: List[Dict[str, str]] = []
        self.schema_invalid_items: List[Dict[str, str]] = []
        self.schema_missing_items: List[Dict[str, str]] = []

    def _determine_repo_root(self) -> Path:
        """
        Determine a stable repository root for routing/glob/schema resolution.

        Strategy:
        1) Walk ancestors from scan path, cwd, and this script location.
        2) Prefer directories containing .git.
        3) Fallback to directory containing src/.
        4) Final fallback: current working directory.
        """
        starts = [self.root_path, Path.cwd().resolve(), Path(__file__).resolve().parent]

        def walk_ancestors(start: Path):
            yield start
            yield from start.parents

        visited_git = set()
        for start in starts:
            for candidate in walk_ancestors(start):
                key = str(candidate)
                if key in visited_git:
                    continue
                visited_git.add(key)
                if (candidate / ".git").exists():
                    return candidate

        visited_src = set()
        for start in starts:
            for candidate in walk_ancestors(start):
                key = str(candidate)
                if key in visited_src:
                    continue
                visited_src.add(key)
                if (candidate / "src").is_dir():
                    return candidate

        return Path.cwd().resolve()

    def _load_routing_config(self) -> None:
        """Load and validate schema routing configuration."""
        config_path = Path(self.routing_config_path)
        if not config_path.is_absolute():
            config_path = self.repo_root / config_path
        
        if not config_path.exists():
            print(f"Warning: Routing config not found at {config_path}", file=sys.stderr)
            return
        
        self.routing_config_resolved_path = config_path
        
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
            
            rules = config.get("rules", [])
            valid_rules = []
            
            for rule in rules:
                schema_path = rule.get("schema")
                if not schema_path:
                    continue
                
                # Validate schema file exists
                full_schema_path = self.repo_root / schema_path
                if not full_schema_path.exists():
                    print(
                        f"Warning: Schema file not found for rule '{rule.get('glob')}': {schema_path}",
                        file=sys.stderr
                    )
                    continue
                
                valid_rules.append(rule)
            
            self.routing_rules = valid_rules
            if valid_rules:
                print(f"Loaded {len(valid_rules)} routing rules from {config_path}")
        
        except Exception as exc:
            print(f"Warning: Failed to load routing config: {exc}", file=sys.stderr)

    def _get_relative_path(self, file_path: Path) -> str:
        """Get relative path from repo root, with fallback to normalized path string."""
        try:
            return str(file_path.resolve().relative_to(self.repo_root))
        except ValueError:
            # File is not under root_path, use normalized absolute path
            return str(file_path.resolve()).replace("\\", "/")

    def _match_routing_rule(self, file_path: Path) -> Optional[str]:
        """
        Find most specific matching routing rule (longest glob pattern wins).
        Returns schema path or None if no match.
        """
        if not self.routing_rules:
            return None
        
        path_str = self._get_relative_path(file_path)
        matches = []
        
        for rule in self.routing_rules:
            glob_pattern = rule.get("glob", "")
            if fnmatch.fnmatch(path_str, glob_pattern):
                schema_path = rule.get("schema")
                if schema_path:
                    matches.append((glob_pattern, schema_path))
        
        if not matches:
            return None
        
        # Sort by glob pattern length (descending) - most specific first
        matches.sort(key=lambda x: len(x[0]), reverse=True)
        return matches[0][1]

    def _load_schema_from_file(self, schema_path: str) -> Dict[str, Any]:
        """Load schema from file with caching."""
        if schema_path in self.schema_cache:
            return self.schema_cache[schema_path]
        
        full_path = self.repo_root / schema_path
        try:
            with open(full_path, "r", encoding="utf-8") as f:
                schema = json.load(f)
            
            self.schema_cache[schema_path] = schema
            return schema
        
        except Exception as exc:
            raise RuntimeError(f"Failed to load schema from {schema_path}: {exc}")

    def validate_file(self, file_path: Path) -> None:
        """Validate a single JSON file and update metrics."""
        self.metrics["total_files_scanned"] += 1

        try:
            with open(file_path, "r", encoding="utf-8") as handle:
                data = json.load(handle)
            self.metrics["parsed_ok"] += 1
        except json.JSONDecodeError as exc:
            self.metrics["syntax_errors"] += 1
            self.syntax_error_items.append(
                {
                    "file": str(file_path),
                    "message": f"{exc.msg} at line {exc.lineno} column {exc.colno}",
                }
            )
            return
        except Exception as exc:
            self.metrics["syntax_errors"] += 1
            self.syntax_error_items.append({"file": str(file_path), "message": str(exc)})
            return

        schema, schema_reason = self._determine_schema(file_path, data)
        if schema is None:
            self.metrics["schema_missing"] += 1
            self.schema_missing_items.append({"file": str(file_path), "reason": schema_reason})
            return

        if HAS_JSONSCHEMA:
            try:
                validate(instance=data, schema=schema)
                self.metrics["schema_valid"] += 1
            except ValidationError as exc:
                self.metrics["schema_invalid"] += 1
                self.schema_invalid_items.append(
                    {
                        "file": str(file_path),
                        "schema": schema_reason,
                        "message": exc.message,
                    }
                )
        else:
            ok, msg = self._basic_validate(data, schema)
            if ok:
                self.metrics["schema_valid"] += 1
            else:
                self.metrics["schema_invalid"] += 1
                self.schema_invalid_items.append(
                    {"file": str(file_path), "schema": schema_reason, "message": msg}
                )

    def _determine_schema(self, file_path: Path, data: Any) -> Tuple[Optional[Dict[str, Any]], str]:
        """
        Determine schema for a file using routing config or hardcoded fallback.
        Returns (schema_dict, reason_string) or (None, reason_string) if no match.
        """
        # 1. Forced schema overrides everything
        if self.forced_schema is not None:
            if self.forced_schema in self.builtin_schemas:
                return self.builtin_schemas[self.forced_schema], f"forced_by_cli:{self.forced_schema}"
            return None, f"forced_schema '{self.forced_schema}' not found in built-in schemas"

        # 2. Try routing config (external schema files)
        if self.routing_rules:
            schema_path = self._match_routing_rule(file_path)
            if schema_path:
                try:
                    schema = self._load_schema_from_file(schema_path)
                    return schema, f"routing:{schema_path}"
                except Exception as exc:
                    return None, f"routing_failed: {exc}"

        # 3. Minimal hardcoded fallback (for backward compatibility)
        path_str = str(file_path).replace("\\", "/")

        if "data/human_cartography/individuals/" in path_str:
            return self.builtin_schemas.get("human_cartography_individual"), "builtin:human_cartography_individual"

        if "data/modules/build_on_old/" in path_str:
            if isinstance(data, dict) and "metadata" in data:
                return self.builtin_schemas.get("build_on_old"), "builtin:build_on_old"
            return None, "no build_on_old schema match (missing top-level metadata)"

        # 4. No match found
        return None, "no schema mapping rule"

    def _basic_validate(self, data: Any, schema: Dict[str, Any]) -> Tuple[bool, str]:
        """Basic validator used when jsonschema is not installed."""
        if schema.get("type") == "object" and not isinstance(data, dict):
            return False, f"Expected object, got {type(data).__name__}"

        required = schema.get("required", [])
        for field in required:
            if not isinstance(data, dict) or field not in data:
                return False, f"Missing required field: {field}"

        properties = schema.get("properties", {})
        for field, field_schema in properties.items():
            if field not in data:
                continue
            value = data[field]
            expected_type = field_schema.get("type")
            if expected_type == "string" and not isinstance(value, str):
                return False, f"Field '{field}' should be string, got {type(value).__name__}"
            if expected_type == "integer" and not isinstance(value, int):
                return False, f"Field '{field}' should be integer, got {type(value).__name__}"
            if expected_type == "array" and not isinstance(value, list):
                return False, f"Field '{field}' should be array, got {type(value).__name__}"
            if expected_type == "object" and not isinstance(value, dict):
                return False, f"Field '{field}' should be object, got {type(value).__name__}"

        return True, ""

    def validate_directory(self, path: Path) -> None:
        """Validate one file or recursively validate all JSON files in a directory."""
        if not path.exists():
            raise FileNotFoundError(f"Path does not exist: {path}")

        if path.is_file():
            if path.suffix.lower() == ".json":
                self.validate_file(path)
            return

        json_files = sorted(path.rglob("*.json"))
        for json_file in json_files:
            self.validate_file(json_file)

    def build_report(self) -> Dict[str, Any]:
        return {
            "metrics": self.metrics,
            "syntax_errors": self.syntax_error_items,
            "schema_invalid": self.schema_invalid_items,
            "schema_missing": self.schema_missing_items,
            "jsonschema_available": HAS_JSONSCHEMA,
            "forced_schema": self.forced_schema,
            "root_path": str(self.root_path),
            "repo_root": str(self.repo_root),
            "routing_config_resolved": (
                str(self.routing_config_resolved_path)
                if self.routing_config_resolved_path is not None
                else None
            ),
        }

    def print_summary(self) -> int:
        """Print concise summary and return process exit code."""
        print("\nValidation Summary")
        print("==================")
        for key in (
            "total_files_scanned",
            "parsed_ok",
            "syntax_errors",
            "schema_valid",
            "schema_invalid",
            "schema_missing",
        ):
            print(f"{key}: {self.metrics[key]}")

        def print_examples(title: str, items: List[Dict[str, str]], key: str) -> None:
            if not items:
                return
            print(f"\n{title} (showing up to 10)")
            for item in items[:10]:
                print(f"- {item['file']}: {item[key]}")

        print_examples("Syntax Errors", self.syntax_error_items, "message")
        print_examples("Schema Invalid", self.schema_invalid_items, "message")
        print_examples("Schema Missing", self.schema_missing_items, "reason")

        # schema_missing is informational; syntax/schema_invalid indicate failing validation.
        if self.metrics["syntax_errors"] > 0 or self.metrics["schema_invalid"] > 0:
            print("\nResult: FAIL")
            return 1

        print("\nResult: PASS")
        return 0


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Validate JSON files in MWDR Showcase"
    )
    parser.add_argument(
        "--path",
        type=str,
        default=".",
        help="Path to validate (default: current directory)",
    )
    parser.add_argument(
        "--schema",
        type=str,
        choices=["standard_node", "human_cartography_individual", "build_on_old"],
        help="Force schema for all scanned files",
    )
    parser.add_argument(
        "--routing-config",
        type=str,
        default="src/validate/schema_routing.json",
        help="Path to schema routing configuration JSON",
    )
    parser.add_argument(
        "--json-report",
        type=str,
        help="Write machine-readable report JSON to file path, or '-' for stdout",
    )
    args = parser.parse_args()

    if not HAS_JSONSCHEMA:
        print("Warning: jsonschema library not found. Using basic validation.")
        print("Install with: pip install jsonschema\n")

    validator = JSONValidator(
        root_path=args.path,
        forced_schema=args.schema,
        routing_config=args.routing_config
    )
    try:
        validator.validate_directory(Path(args.path))
    except FileNotFoundError as exc:
        print(f"Error: {exc}")
        sys.exit(1)

    report = validator.build_report()
    if args.json_report:
        payload = json.dumps(report, indent=2, ensure_ascii=False)
        if args.json_report == "-":
            print("\nJSON Report")
            print("===========")
            print(payload)
        else:
            report_path = Path(args.json_report)
            report_path.write_text(payload + "\n", encoding="utf-8")
            print(f"\nWrote JSON report: {report_path}")

    sys.exit(validator.print_summary())


if __name__ == "__main__":
    main()
