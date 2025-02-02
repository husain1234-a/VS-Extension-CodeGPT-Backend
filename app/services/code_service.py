import re
import ast
from typing import Dict, Any, List


class CodeService:
    @staticmethod
    def parse_code(code: str) -> ast.AST:
        """
        Parses a string of Python code into an Abstract Syntax Tree (AST).

        Args:
            code (str): A string representing the Python code to parse.

        Returns:
            ast.AST: The root of the AST tree representing the parsed code.

        Raises:
            Exception: If there is a syntax error in the provided code.
        """

        try:
            return ast.parse(code)
        except SyntaxError as e:
            raise Exception(f"Syntax error in code: {str(e)}")

    @staticmethod
    def analyze_structure(tree: ast.AST) -> Dict[str, Any]:
        """
        Analyzes the structure of an Abstract Syntax Tree (AST) representing Python code.

        The analysis includes a count of imports, functions, classes, and the complexity of the code.

        Args:
            tree (ast.AST): The root of the AST tree representing the Python code to analyze.

        Returns:
            Dict[str, Any]: A dictionary containing the analysis of the code structure.

        """

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
        """
        Refactors the given code according to the specified type.

        Args:
            code (str): The code to refactor.
            refactor_type (str): The type of refactoring to perform, either "format" or "optimize_imports".

        Returns:
            str: The refactored code.

        Raises:
            ValueError: If refactor_type is not "format" or "optimize_imports".
        """

        if refactor_type == "format":
            return CodeService._format_code(code)
        elif refactor_type == "optimize_imports":
            return CodeService._optimize_imports(code)
        else:
            raise ValueError(f"Unsupported refactor type: {refactor_type}")

    @staticmethod
    def _format_code(code: str) -> str:
        """
        Format the given code according to PEP 8 conventions.

        Args:
            code (str): The code to format.

        Returns:
            str: The formatted code.

        Raises:
            Exception: If code formatting fails.
        """

        try:
            tree = ast.parse(code)
            return ast.unparse(tree)
        except Exception as e:
            raise Exception(f"Code formatting failed: {str(e)}")

    @staticmethod
    def _optimize_imports(code: str) -> str:
        """
        Reorders imports in the given code according to PEP 8 conventions.

        Args:
            code (str): The code to reorder imports in.

        Returns:
            str: The code with reordered imports.

        Raises:
            Exception: If code analysis fails.
        """
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
