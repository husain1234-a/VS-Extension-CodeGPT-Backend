import ast
from typing import Dict, Any, List
import re


class CodeService:
    @staticmethod
    def parse_code(code: str) -> ast.AST:
        try:
            return ast.parse(code)
        except SyntaxError as e:
            raise Exception(f"Syntax error in code: {str(e)}")

    @staticmethod
    def analyze_structure(tree: ast.AST) -> Dict[str, Any]:
        analysis = {"imports": [], "functions": [], "classes": [], "complexity": 0}

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                analysis["imports"].extend(n.name for n in node.names)
            elif isinstance(node, ast.ImportFrom):
                analysis["imports"].append(f"{node.module}.{node.names[0].name}")
            elif isinstance(node, ast.FunctionDef):
                analysis["functions"].append(
                    {
                        "name": node.name,
                        "args": len(node.args.args),
                        "line_number": node.lineno,
                    }
                )
            elif isinstance(node, ast.ClassDef):
                analysis["classes"].append(
                    {
                        "name": node.name,
                        "methods": len(
                            [n for n in node.body if isinstance(n, ast.FunctionDef)]
                        ),
                        "line_number": node.lineno,
                    }
                )

        return analysis

    @staticmethod
    def refactor_code(code: str, refactor_type: str) -> str:
        if refactor_type == "format":
            return CodeService._format_code(code)
        elif refactor_type == "optimize_imports":
            return CodeService._optimize_imports(code)
        else:
            raise ValueError(f"Unsupported refactor type: {refactor_type}")

    @staticmethod
    def _format_code(code: str) -> str:
        try:
            tree = ast.parse(code)
            return ast.unparse(tree)
        except Exception as e:
            raise Exception(f"Code formatting failed: {str(e)}")

    @staticmethod
    def _optimize_imports(code: str) -> str:
        try:
            tree = ast.parse(code)
            imports = []
            for node in ast.walk(tree):
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    imports.append(ast.unparse(node))

            imports = sorted(set(imports))

            code_lines = code.split("\n")
            code_without_imports = [
                line
                for line in code_lines
                if not line.strip().startswith(("import ", "from "))
            ]

            return "\n".join(imports + [""] + code_without_imports)
        except Exception as e:
            raise Exception(f"Import optimization failed: {str(e)}")
