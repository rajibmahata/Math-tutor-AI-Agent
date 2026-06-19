"""SymPy Math Verification — deterministic answer checking."""

import re
import logging

logger = logging.getLogger(__name__)


def verify_answer(student_answer: str, question: str) -> dict:
    """
    Verify a student's math answer using SymPy for computational problems.
    Returns {"is_correct": bool, "expected": str, "actual": str, "method": str}

    For non-computational answers (text explanations), returns is_correct=None.
    """
    try:
        # Extract mathematical expressions
        student_expr = _extract_math(student_answer)
        question_expr = _extract_math_from_question(question)

        if not student_expr or not question_expr:
            return {
                "is_correct": None,
                "expected": question_expr or "unknown",
                "actual": student_expr or "unknown",
                "method": "no_math_detected",
            }

        from sympy import sympify, simplify, N, Eq
        from sympy.parsing.sympy_parser import (
            parse_expr,
            standard_transformations,
            implicit_multiplication_application,
            convert_xor,
        )

        transformations = standard_transformations + (
            implicit_multiplication_application,
            convert_xor,
        )

        # Parse and evaluate
        student_parsed = parse_expr(student_expr, transformations=transformations)
        question_parsed = parse_expr(question_expr, transformations=transformations)

        # Compare: exact equality or numerical equivalence
        try:
            is_equal = bool(simplify(student_parsed - question_parsed) == 0)
        except Exception:
            # Try numeric comparison
            try:
                student_val = float(N(student_parsed))
                question_val = float(N(question_parsed))
                is_equal = abs(student_val - question_val) < 1e-10
            except Exception:
                is_equal = False

        return {
            "is_correct": is_equal,
            "expected": str(question_parsed),
            "actual": str(student_parsed),
            "method": "sympy_algebraic",
        }

    except Exception as e:
        logger.debug(f"SymPy verification failed (non-critical): {e}")
        return {
            "is_correct": None,
            "expected": None,
            "actual": None,
            "method": "sympy_error",
        }


def _extract_math(text: str) -> str | None:
    """Extract a mathematical expression from text."""
    if not text:
        return None

    # If it's purely a number, return it
    text = text.strip()
    if re.match(r"^-?\d+\.?\d*$", text):
        return text

    # Try to find LaTeX expressions $...$ or $$...$$
    latex_match = re.search(r"\$([^$]+)\$", text)
    if latex_match:
        return latex_match.group(1).strip()

    # Try to extract "= number" pattern
    eq_match = re.search(r"=\s*(-?[\d.]+)", text)
    if eq_match:
        return eq_match.group(1)

    # Try basic arithmetic: "number operator number"
    arith_match = re.match(
        r"^(-?\d+\.?\d*)\s*([+\-*/×÷])\s*(-?\d+\.?\d*)$", text
    )
    if arith_match:
        a, op, b = arith_match.groups()
        op_map = {"×": "*", "÷": "/", "x": "*"}
        op = op_map.get(op, op)
        return f"({a}) {op} ({b})"

    # Return the text as-is, SymPy will try to parse it
    return text


def _extract_math_from_question(question: str) -> str | None:
    """Extract the expected answer from a question (what needs to be computed)."""
    if not question:
        return None

    # Common patterns in math questions
    # "What is 12 + 5?" → "12 + 5"
    patterns = [
        r"[Ww]hat is\s+(.+?)\??$",
        r"[Cc]alculate\s+(.+?)\??$",
        r"[Ss]olve\s+(.+?)\??$",
        r"[Ff]ind\s+(.+?)\??$",
        r"[Ee]valuate\s+(.+?)\??$",
    ]

    for pattern in patterns:
        match = re.search(pattern, question)
        if match:
            expr = match.group(1).strip().rstrip("?").rstrip(".")
            # Clean up: remove trailing words
            expr = re.sub(r"\s+equals?\s*$", "", expr, flags=re.IGNORECASE)
            return expr

    # Try LaTeX
    latex_match = re.search(r"\$([^$]+)\$", question)
    if latex_match:
        return latex_match.group(1).strip()

    return None
