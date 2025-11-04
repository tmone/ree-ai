"""
Operator Registry
Dynamic registration and discovery of operators
"""
from typing import Dict, Type, Optional, List
from .base import Operator
import logging


class OperatorRegistry:
    """
    Registry for RAG operators

    Enables:
    - Dynamic operator registration
    - Operator discovery by name/type
    - Operator instantiation with config
    """

    def __init__(self):
        self._operators: Dict[str, Type[Operator]] = {}
        self.logger = logging.getLogger("OperatorRegistry")

    def register(self, name: str, operator_class: Type[Operator]):
        """
        Register an operator class

        Args:
            name: Unique operator name
            operator_class: Operator class to register
        """
        if name in self._operators:
            self.logger.warning(f"Overwriting existing operator: {name}")

        self._operators[name] = operator_class
        self.logger.info(f"Registered operator: {name} ({operator_class.__name__})")

    def get(self, name: str) -> Optional[Type[Operator]]:
        """
        Get operator class by name

        Args:
            name: Operator name

        Returns:
            Operator class or None if not found
        """
        return self._operators.get(name)

    def create(self, name: str, **kwargs) -> Optional[Operator]:
        """
        Create operator instance

        Args:
            name: Operator name
            **kwargs: Arguments for operator constructor

        Returns:
            Operator instance or None if not found
        """
        operator_class = self.get(name)
        if operator_class is None:
            self.logger.error(f"Operator not found: {name}")
            return None

        try:
            return operator_class(**kwargs)
        except Exception as e:
            self.logger.error(f"Failed to create operator {name}: {e}")
            return None

    def list_operators(self) -> List[str]:
        """
        List all registered operators

        Returns:
            List of operator names
        """
        return list(self._operators.keys())

    def list_by_type(self, operator_type: Type[Operator]) -> List[str]:
        """
        List operators of specific type

        Args:
            operator_type: Base operator type (e.g., PreRetrievalOperator)

        Returns:
            List of matching operator names
        """
        return [
            name for name, cls in self._operators.items()
            if issubclass(cls, operator_type)
        ]

    def clear(self):
        """Clear all registered operators"""
        self._operators.clear()
        self.logger.info("Cleared all operators")


# Global registry instance
global_registry = OperatorRegistry()


def register_operator(name: str):
    """
    Decorator to register operator classes

    Usage:
        @register_operator("document_grader")
        class DocumentGraderOperator(PostRetrievalOperator):
            pass
    """
    def decorator(cls: Type[Operator]):
        global_registry.register(name, cls)
        return cls
    return decorator
