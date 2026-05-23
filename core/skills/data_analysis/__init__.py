"""
Módulo de Análisis de Datos.
Permite a Mónica interpretar archivos CSV, Excel y hacer cálculos matemáticos.
"""
import logging
import os

logger = logging.getLogger(__name__)

def analyze_csv(file_path: str) -> dict:
    """
    Analiza un archivo CSV y devuelve sus estadísticas descriptivas básicas.
    """
    if not os.path.exists(file_path):
        return {"status": "error", "message": f"El archivo {file_path} no existe."}
        
    try:
        import pandas as pd
        df = pd.read_csv(file_path)
        summary = df.describe(include='all').to_dict()
        columns = list(df.columns)
        rows = len(df)
        
        return {
            "status": "success", 
            "file": file_path,
            "rows": rows,
            "columns": columns,
            "summary": summary
        }
    except ImportError:
        return {"status": "error", "message": "Pandas no está instalado en este entorno local."}
    except Exception as e:
        logger.error(f"Error analizando CSV {file_path}: {e}")
        return {"status": "error", "message": str(e)}

def math_calculate(expression: str) -> dict:
    """
    Evalúa una expresión matemática simple de forma segura.
    """
    import ast
    import operator

    # Solo permite operadores matemáticos básicos
    allowed_operators = {
        ast.Add: operator.add, ast.Sub: operator.sub,
        ast.Mult: operator.mul, ast.Div: operator.truediv,
        ast.Pow: operator.pow, ast.BitXor: operator.xor,
        ast.USub: operator.neg
    }

    def eval_expr(node):
        if isinstance(node, ast.Num):
            return node.n
        elif isinstance(node, ast.BinOp):
            return allowed_operators[type(node.op)](eval_expr(node.left), eval_expr(node.right))
        elif isinstance(node, ast.UnaryOp):
            return allowed_operators[type(node.op)](eval_expr(node.operand))
        else:
            raise TypeError(node)

    try:
        result = eval_expr(ast.parse(expression, mode='eval').body)
        return {"status": "success", "expression": expression, "result": result}
    except Exception as e:
        return {"status": "error", "message": f"Expresión inválida: {e}"}
