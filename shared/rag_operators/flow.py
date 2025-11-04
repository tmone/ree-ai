"""
RAG Flow Engine
Orchestrates operator execution with dynamic composition
"""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from .base import Operator, OperatorResult
import logging
from datetime import datetime


class FlowConfig(BaseModel):
    """Configuration for RAG flow"""
    name: str
    description: str = ""
    max_execution_time: float = 120.0  # 2 minutes
    stop_on_error: bool = True
    enable_logging: bool = True


class FlowExecutionResult(BaseModel):
    """Result from flow execution"""
    success: bool
    flow_name: str
    operator_results: List[OperatorResult] = []
    final_output: Any = None
    total_execution_time: float = 0.0
    error: Optional[str] = None
    metadata: Dict[str, Any] = {}

    class Config:
        arbitrary_types_allowed = True


class RAGFlow:
    """
    RAG Flow Engine

    Implements CTO's RAG Flow patterns:
    - Sequential execution
    - Conditional branching
    - Error handling
    - Performance tracking
    """

    def __init__(
        self,
        operators: List[Operator],
        config: Optional[FlowConfig] = None,
        logger: Optional[logging.Logger] = None
    ):
        self.operators = operators
        self.config = config or FlowConfig(name="default_flow")
        self.logger = logger or logging.getLogger(f"RAGFlow.{self.config.name}")

    async def execute(self, initial_input: Any) -> FlowExecutionResult:
        """
        Execute flow with sequential operator execution

        Args:
            initial_input: Initial input data

        Returns:
            FlowExecutionResult with all operator results
        """
        start_time = datetime.now()
        operator_results: List[OperatorResult] = []
        current_data = initial_input

        self.logger.info(f"🚀 Starting flow: {self.config.name} with {len(self.operators)} operators")

        try:
            for i, operator in enumerate(self.operators, 1):
                self.logger.info(f"▶️  [{i}/{len(self.operators)}] Executing: {operator.name}")

                # Execute operator
                result = await operator.safe_execute(current_data)
                operator_results.append(result)

                # Log result
                if result.success:
                    self.logger.info(f"✅ [{i}/{len(self.operators)}] {operator.name} succeeded ({result.execution_time:.2f}s)")
                else:
                    self.logger.error(f"❌ [{i}/{len(self.operators)}] {operator.name} failed: {result.error}")

                # Stop on error if configured
                if not result.success and self.config.stop_on_error:
                    return FlowExecutionResult(
                        success=False,
                        flow_name=self.config.name,
                        operator_results=operator_results,
                        final_output=None,
                        total_execution_time=(datetime.now() - start_time).total_seconds(),
                        error=f"Flow stopped at operator {operator.name}: {result.error}"
                    )

                # Pass output to next operator
                current_data = result.data

            # Flow completed successfully
            total_time = (datetime.now() - start_time).total_seconds()
            self.logger.info(f"🎉 Flow completed successfully in {total_time:.2f}s")

            return FlowExecutionResult(
                success=True,
                flow_name=self.config.name,
                operator_results=operator_results,
                final_output=current_data,
                total_execution_time=total_time,
                metadata={
                    "operator_count": len(self.operators),
                    "operator_names": [op.name for op in self.operators]
                }
            )

        except Exception as e:
            self.logger.error(f"💥 Flow failed with exception: {e}")
            return FlowExecutionResult(
                success=False,
                flow_name=self.config.name,
                operator_results=operator_results,
                final_output=None,
                total_execution_time=(datetime.now() - start_time).total_seconds(),
                error=str(e)
            )

    async def execute_with_retry(
        self,
        initial_input: Any,
        max_retries: int = 2,
        retry_condition: Optional[callable] = None
    ) -> FlowExecutionResult:
        """
        Execute flow with retry logic and quality checking

        Implements Agentic RAG pattern: Self-correction

        Args:
            initial_input: Initial input
            max_retries: Maximum retry attempts
            retry_condition: Function(result) -> bool to determine if retry needed

        Returns:
            FlowExecutionResult
        """
        attempts = 0

        while attempts <= max_retries:
            self.logger.info(f"🔄 Flow attempt {attempts + 1}/{max_retries + 1}")

            result = await self.execute(initial_input)

            # Check if retry needed
            if result.success:
                if retry_condition is None or not retry_condition(result):
                    # Success and no retry needed
                    return result

                self.logger.warning(f"⚠️  Retry condition triggered, retrying...")

            attempts += 1

        # Max retries exceeded
        self.logger.error(f"❌ Max retries ({max_retries}) exceeded")
        return result

    def add_operator(self, operator: Operator, position: Optional[int] = None):
        """
        Add operator to flow

        Args:
            operator: Operator to add
            position: Insert position (None = append)
        """
        if position is None:
            self.operators.append(operator)
        else:
            self.operators.insert(position, operator)

        self.logger.info(f"Added operator {operator.name} at position {position or len(self.operators)}")

    def remove_operator(self, name: str) -> bool:
        """
        Remove operator by name

        Args:
            name: Operator name

        Returns:
            True if removed, False if not found
        """
        for i, op in enumerate(self.operators):
            if op.name == name:
                self.operators.pop(i)
                self.logger.info(f"Removed operator {name}")
                return True

        self.logger.warning(f"Operator {name} not found")
        return False

    def __repr__(self) -> str:
        return f"<RAGFlow(name='{self.config.name}', operators={len(self.operators)})>"
