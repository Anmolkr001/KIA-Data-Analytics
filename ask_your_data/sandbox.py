"""
Restricted Sandboxed Pandas Executor for Ask Your Data.
Blocks imports, arbitrary eval/exec, file I/O, network/OS access, and enforces execution timeouts.
"""

import ast
import io
import time
import contextlib
import threading
import queue
from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple
import pandas as pd
import numpy as np

from ask_your_data.config import SANDBOX_TIMEOUT_SECONDS

# Forbidden built-in / identifier names
FORBIDDEN_CALLS = {
    "eval", "exec", "open", "compile", "getattr", "setattr", "delattr",
    "__import__", "globals", "locals", "vars", "input", "breakpoint",
    "exit", "quit", "help", "reload", "memoryview", "classmethod", "staticmethod"
}

FORBIDDEN_MODULES = {
    "os", "sys", "subprocess", "shutil", "socket", "requests", "urllib",
    "pathlib", "builtins", "posix", "nt", "importlib", "pip", "pty", "commands"
}

FORBIDDEN_METHODS = {
    "to_csv", "to_excel", "to_sql", "to_parquet", "to_pickle", "to_json",
    "to_feather", "to_stata", "to_hdf", "to_clipboard", "to_markdown", "to_html"
}

# Strictly safe builtins whitelist
SAFE_BUILTINS = {
    "abs": abs,
    "all": all,
    "any": any,
    "bool": bool,
    "dict": dict,
    "enumerate": enumerate,
    "filter": filter,
    "float": float,
    "int": int,
    "isinstance": isinstance,
    "issubclass": issubclass,
    "len": len,
    "list": list,
    "map": map,
    "max": max,
    "min": min,
    "pow": pow,
    "range": range,
    "reversed": reversed,
    "round": round,
    "set": set,
    "sorted": sorted,
    "str": str,
    "sum": sum,
    "tuple": tuple,
    "zip": zip,
    "True": True,
    "False": False,
    "None": None,
    "print": print,
}


class SecurityViolationError(Exception):
    """Raised when generated code violates sandboxing security rules."""
    pass


class CodeSecurityValidator(ast.NodeVisitor):
    """
    AST Visitor that scans code for forbidden operations, imports,
    dunder attribute access, and filesystem writing.
    """

    def visit_Import(self, node: ast.Import):
        raise SecurityViolationError("Imports are strictly forbidden in query code.")

    def visit_ImportFrom(self, node: ast.ImportFrom):
        raise SecurityViolationError("Imports are strictly forbidden in query code.")

    def visit_Call(self, node: ast.Call):
        # Check direct function call names
        if isinstance(node.func, ast.Name):
            if node.func.id in FORBIDDEN_CALLS:
                raise SecurityViolationError(f"Call to '{node.func.id}()' is strictly forbidden.")
            if node.func.id in FORBIDDEN_MODULES:
                raise SecurityViolationError(f"Access to '{node.func.id}' is strictly forbidden.")

        # Check method calls (e.g. df.to_csv())
        elif isinstance(node.func, ast.Attribute):
            method_name = node.func.attr
            if method_name in FORBIDDEN_METHODS:
                raise SecurityViolationError(f"Method '{method_name}()' writes to disk and is prohibited.")
            if method_name.startswith("_"):
                raise SecurityViolationError(f"Access to private/dunder attribute '{method_name}' is forbidden.")

        self.generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute):
        # Disallow private/dunder attribute access
        if node.attr.startswith("_"):
            raise SecurityViolationError(f"Access to private/dunder attribute '{node.attr}' is forbidden.")
        if node.attr in FORBIDDEN_MODULES:
            raise SecurityViolationError(f"Access to module attribute '{node.attr}' is forbidden.")
        self.generic_visit(node)

    def visit_While(self, node: ast.While):
        raise SecurityViolationError("'while' loops are not permitted in queries. Use vectorized pandas operations.")

    def visit_Name(self, node: ast.Name):
        if node.id in FORBIDDEN_MODULES:
            raise SecurityViolationError(f"Direct reference to '{node.id}' is forbidden.")
        self.generic_visit(node)


@dataclass
class ExecutionResult:
    """Structured container for sandbox execution outcomes."""
    success: bool
    output: Any
    df_result: Optional[pd.DataFrame] = None
    stdout: str = ""
    error: Optional[str] = None
    execution_time_ms: float = 0.0
    row_count: int = 0
    column_names: Optional[list] = None

    def to_display_markdown(self, max_rows: int = 15) -> str:
        """Formats the result into a clean markdown table or text summary."""
        if not self.success:
            return f"[Error] Execution Error: `{self.error}`"

        if self.df_result is not None:
            if self.df_result.empty:
                return "[Warning] Query executed successfully, but returned 0 rows."
            
            preview = self.df_result.head(max_rows)
            # Use markdown formatting
            return preview.to_markdown(index=False)
        
        return str(self.output)


class SandboxedPandasExecutor:
    """Executes pandas code safely inside a restricted sandbox."""

    def __init__(self, timeout_seconds: int = SANDBOX_TIMEOUT_SECONDS):
        self.timeout_seconds = timeout_seconds

    def validate_code(self, code: str) -> None:
        """Parses and validates code AST against security rules."""
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            raise SyntaxError(f"Syntax error in code: {e}")

        validator = CodeSecurityValidator()
        validator.visit(tree)

    def _execute_internal(self, code: str, df: pd.DataFrame) -> Tuple[Any, Optional[pd.DataFrame], str]:
        """Runs the code in a sandbox environment and captures result and stdout."""
        # Create a defensive copy so modifications do not corrupt master dataset
        df_copy = df.copy()

        # Build clean environment
        sandbox_globals: Dict[str, Any] = {
            "__builtins__": SAFE_BUILTINS,
            "pd": pd,
            "np": np,
            "df": df_copy,
        }
        sandbox_locals: Dict[str, Any] = {}

        # Capture print outputs
        stdout_capture = io.StringIO()

        # Parse AST to check if the last statement is an expression
        parsed = ast.parse(code)
        has_expr_return = False
        expr_code = None

        if parsed.body and isinstance(parsed.body[-1], ast.Expr):
            has_expr_return = True
            # Split off the last expression to evaluate its value
            last_expr = parsed.body.pop()
            exec_code = compile(parsed, filename="<sandbox>", mode="exec")
            expr_code = compile(ast.Expression(body=last_expr.value), filename="<sandbox>", mode="eval")
        else:
            exec_code = compile(parsed, filename="<sandbox>", mode="exec")

        with contextlib.redirect_stdout(stdout_capture):
            exec(exec_code, sandbox_globals, sandbox_locals)
            
            # If last node was an expression, eval it
            if has_expr_return and expr_code is not None:
                eval_val = eval(expr_code, sandbox_globals, sandbox_locals)
                sandbox_locals["result"] = eval_val

        captured_stdout = stdout_capture.getvalue()

        # Extract result
        result = None
        if "result" in sandbox_locals:
            result = sandbox_locals["result"]
        elif "res" in sandbox_locals:
            result = sandbox_locals["res"]
        elif "output" in sandbox_locals:
            result = sandbox_locals["output"]
        elif "df_result" in sandbox_locals:
            result = sandbox_locals["df_result"]
        else:
            # Check if any new variable was assigned
            keys = [k for k in sandbox_locals if k not in ["df_copy"]]
            if len(keys) == 1:
                result = sandbox_locals[keys[0]]
            elif not keys and captured_stdout:
                result = captured_stdout.strip()

        # Standardize result to DataFrame if applicable
        df_result = None
        if isinstance(result, pd.DataFrame):
            df_result = result.reset_index() if result.index.name or not isinstance(result.index, pd.RangeIndex) else result
        elif isinstance(result, pd.Series):
            df_result = result.reset_index()
            if len(df_result.columns) == 2 and df_result.columns[1] == 0:
                df_result.columns = [df_result.columns[0], "value"]
        elif isinstance(result, (int, float, np.number, str, bool)):
            df_result = pd.DataFrame([{"metric_value": result}])

        return result, df_result, captured_stdout

    def run(self, code: str, df: pd.DataFrame) -> ExecutionResult:
        """
        Executes code with validation and timeout protection.
        Returns a structured ExecutionResult.
        """
        start_time = time.time()
        
        # 1. Clean code snippet (strip markdown blocks if LLM included them)
        cleaned_code = code.strip()
        if cleaned_code.startswith("```python"):
            cleaned_code = cleaned_code[9:]
        elif cleaned_code.startswith("```"):
            cleaned_code = cleaned_code[3:]
        if cleaned_code.endswith("```"):
            cleaned_code = cleaned_code[:-3]
        cleaned_code = cleaned_code.strip()

        # 2. Security validation
        try:
            self.validate_code(cleaned_code)
        except (SecurityViolationError, SyntaxError) as e:
            elapsed = (time.time() - start_time) * 1000
            return ExecutionResult(
                success=False,
                output=None,
                error=f"Security/Syntax Error: {str(e)}",
                execution_time_ms=elapsed
            )

        # 3. Timeout protected execution with daemon thread
        result_queue: queue.Queue = queue.Queue()

        def worker():
            try:
                res = self._execute_internal(cleaned_code, df)
                result_queue.put(("SUCCESS", res))
            except Exception as exc:
                result_queue.put(("ERROR", exc))

        thread = threading.Thread(target=worker, daemon=True)
        thread.start()
        thread.join(timeout=self.timeout_seconds)

        elapsed = (time.time() - start_time) * 1000

        if thread.is_alive():
            return ExecutionResult(
                success=False,
                output=None,
                error=f"Execution timed out after {self.timeout_seconds} seconds.",
                execution_time_ms=elapsed
            )

        try:
            status, payload = result_queue.get_nowait()
            if status == "ERROR":
                return ExecutionResult(
                    success=False,
                    output=None,
                    error=f"Runtime Error: {type(payload).__name__}: {str(payload)}",
                    execution_time_ms=elapsed
                )
            
            raw_result, df_result, stdout = payload
            row_count = len(df_result) if df_result is not None else 0
            col_names = df_result.columns.tolist() if df_result is not None else None

            return ExecutionResult(
                success=True,
                output=raw_result,
                df_result=df_result,
                stdout=stdout,
                execution_time_ms=elapsed,
                row_count=row_count,
                column_names=col_names
            )
        except Exception as e:
            return ExecutionResult(
                success=False,
                output=None,
                error=f"Execution Error: {str(e)}",
                execution_time_ms=elapsed
            )
