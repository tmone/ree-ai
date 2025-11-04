"""
Base Operator Classes
Foundation for Modular RAG Architecture
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, List
from pydantic import BaseModel
from datetime import datetime
import logging


class OperatorConfig(BaseModel):
    """Configuration for operators"""
    enabled: bool = True
    timeout: float = 30.0
    retry_on_failure: bool = False
    max_retries: int = 3
    custom_params: Dict[str, Any] = {}


class OperatorResult(BaseModel):
    """Result from operator execution"""
    success: bool
    data: Any
    metadata: Dict[str, Any] = {}
    error: Optional[str] = None
    execution_time: float = 0.0
    timestamp: datetime = datetime.now()

    class Config:
        arbitrary_types_allowed = True


class Operator(ABC):
    """
    Base class for all RAG operators

    Implements CTO's Modular RAG Architecture:
    - Each operator is independent and swappable
    - Operators can be chained in flows
    - Configuration-driven behavior
    """

    def __init__(
        self,
        name: str,
        config: Optional[OperatorConfig] = None,
        logger: Optional[logging.Logger] = None
    ):
        self.name = name
        self.config = config or OperatorConfig()
        self.logger = logger or logging.getLogger(f"operator.{name}")

    @abstractmethod
    async def execute(self, input_data: Any) -> OperatorResult:
        """
        Execute operator logic

        Args:
            input_data: Input data (type varies by operator)

        Returns:
            OperatorResult with success status and output data
        """
        pass

    @abstractmethod
    def validate_input(self, input_data: Any) -> bool:
        """
        Validate input data format

        Args:
            input_data: Data to validate

        Returns:
            True if valid, False otherwise
        """
        pass

    async def safe_execute(self, input_data: Any) -> OperatorResult:
        """
        Execute with error handling and retries

        Args:
            input_data: Input data

        Returns:
            OperatorResult (success or error)
        """
        start_time = datetime.now()

        # Validate input
        if not self.validate_input(input_data):
            return OperatorResult(
                success=False,
                data=None,
                error=f"Invalid input for operator {self.name}",
                execution_time=0.0
            )

        # Execute with retries if configured
        attempts = 0
        max_attempts = self.config.max_retries if self.config.retry_on_failure else 1

        while attempts < max_attempts:
            try:
                result = await self.execute(input_data)
                result.execution_time = (datetime.now() - start_time).total_seconds()
                return result

            except Exception as e:
                attempts += 1
                self.logger.error(f"Operator {self.name} failed (attempt {attempts}/{max_attempts}): {e}")

                if attempts >= max_attempts:
                    return OperatorResult(
                        success=False,
                        data=None,
                        error=str(e),
                        execution_time=(datetime.now() - start_time).total_seconds()
                    )

        # Should never reach here
        return OperatorResult(
            success=False,
            data=None,
            error="Unknown error",
            execution_time=(datetime.now() - start_time).total_seconds()
        )

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(name='{self.name}')>"


class PreRetrievalOperator(Operator):
    """Base class for pre-retrieval operators (query transformation)"""
    pass


class RetrievalOperator(Operator):
    """Base class for retrieval operators"""
    pass


class PostRetrievalOperator(Operator):
    """Base class for post-retrieval operators (reranking, filtering)"""
    pass


class GenerationOperator(Operator):
    """Base class for generation operators"""
    pass


class OrchestrationOperator(Operator):
    """Base class for orchestration operators (flow control)"""
    pass
