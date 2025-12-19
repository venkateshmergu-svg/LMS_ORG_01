"""
Custom exceptions for the Leave Management System.
"""
from typing import Any, Dict, Optional


class LMSException(Exception):
    """Base exception for all LMS exceptions."""
    
    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.error_code = error_code or "LMS_ERROR"
        self.details = details or {}
        super().__init__(self.message)


# Policy Engine Exceptions
class PolicyException(LMSException):
    """Base exception for policy-related errors."""
    pass


class PolicyNotFoundException(PolicyException):
    """Raised when a policy is not found."""
    
    def __init__(self, policy_id: Any):
        super().__init__(
            message=f"Policy not found: {policy_id}",
            error_code="POLICY_NOT_FOUND",
            details={"policy_id": str(policy_id)}
        )


class PolicyValidationException(PolicyException):
    """Raised when policy validation fails."""
    
    def __init__(self, message: str, violations: Optional[list] = None):
        super().__init__(
            message=message,
            error_code="POLICY_VALIDATION_FAILED",
            details={"violations": violations or []}
        )


class InsufficientBalanceException(PolicyException):
    """Raised when leave balance is insufficient."""
    
    def __init__(self, available: float, requested: float, leave_type: str):
        super().__init__(
            message=f"Insufficient {leave_type} balance: {available} available, {requested} requested",
            error_code="INSUFFICIENT_BALANCE",
            details={
                "available": available,
                "requested": requested,
                "leave_type": leave_type
            }
        )


class EligibilityException(PolicyException):
    """Raised when eligibility criteria not met."""
    
    def __init__(self, message: str, criteria: Optional[Dict] = None):
        super().__init__(
            message=message,
            error_code="ELIGIBILITY_NOT_MET",
            details={"criteria": criteria or {}}
        )


# Workflow Engine Exceptions
class WorkflowException(LMSException):
    """Base exception for workflow-related errors."""
    pass


class WorkflowNotFoundException(WorkflowException):
    """Raised when workflow configuration is not found."""
    
    def __init__(self, workflow_id: Any = None, leave_type: Optional[str] = None):
        details = {}
        if workflow_id:
            details["workflow_id"] = str(workflow_id)
        if leave_type:
            details["leave_type"] = leave_type
        super().__init__(
            message="Workflow not found",
            error_code="WORKFLOW_NOT_FOUND",
            details=details
        )


class WorkflowStateException(WorkflowException):
    """Raised when invalid workflow state transition is attempted."""
    
    def __init__(self, current_state: str, attempted_action: str):
        super().__init__(
            message=f"Invalid state transition: cannot {attempted_action} from {current_state}",
            error_code="INVALID_STATE_TRANSITION",
            details={
                "current_state": current_state,
                "attempted_action": attempted_action
            }
        )


class ApprovalException(WorkflowException):
    """Raised when approval action fails."""
    
    def __init__(self, message: str, approver_id: Any = None):
        super().__init__(
            message=message,
            error_code="APPROVAL_FAILED",
            details={"approver_id": str(approver_id) if approver_id else None}
        )


class DelegationException(WorkflowException):
    """Raised when delegation action fails."""
    
    def __init__(self, message: str):
        super().__init__(
            message=message,
            error_code="DELEGATION_FAILED"
        )


class EscalationException(WorkflowException):
    """Raised when escalation action fails."""
    
    def __init__(self, message: str):
        super().__init__(
            message=message,
            error_code="ESCALATION_FAILED"
        )


# Leave Engine Exceptions
class LeaveException(LMSException):
    """Base exception for leave-related errors."""
    pass


class LeaveRequestNotFoundException(LeaveException):
    """Raised when a leave request is not found."""
    
    def __init__(self, request_id: Any):
        super().__init__(
            message=f"Leave request not found: {request_id}",
            error_code="LEAVE_REQUEST_NOT_FOUND",
            details={"request_id": str(request_id)}
        )


class LeaveTypeNotFoundException(LeaveException):
    """Raised when a leave type is not found."""
    
    def __init__(self, leave_type_id: Any = None, leave_type_code: Optional[str] = None):
        details = {}
        if leave_type_id:
            details["leave_type_id"] = str(leave_type_id)
        if leave_type_code:
            details["leave_type_code"] = leave_type_code
        super().__init__(
            message="Leave type not found",
            error_code="LEAVE_TYPE_NOT_FOUND",
            details=details
        )


class LeaveOverlapException(LeaveException):
    """Raised when leave dates overlap with existing requests."""
    
    def __init__(self, overlapping_dates: list):
        super().__init__(
            message="Leave dates overlap with existing requests",
            error_code="LEAVE_OVERLAP",
            details={"overlapping_dates": overlapping_dates}
        )


class EncashmentException(LeaveException):
    """Raised when leave encashment fails."""
    
    def __init__(self, message: str, leave_type: Optional[str] = None):
        super().__init__(
            message=message,
            error_code="ENCASHMENT_FAILED",
            details={"leave_type": leave_type}
        )


# Repository Exceptions
class RepositoryException(LMSException):
    """Base exception for repository-related errors."""
    pass


class EntityNotFoundException(RepositoryException):
    """Raised when an entity is not found in the database."""
    
    def __init__(self, entity_type: str, entity_id: Any):
        super().__init__(
            message=f"{entity_type} not found: {entity_id}",
            error_code="ENTITY_NOT_FOUND",
            details={
                "entity_type": entity_type,
                "entity_id": str(entity_id)
            }
        )


class DuplicateEntityException(RepositoryException):
    """Raised when attempting to create a duplicate entity."""
    
    def __init__(self, entity_type: str, field: str, value: Any):
        super().__init__(
            message=f"{entity_type} with {field}={value} already exists",
            error_code="DUPLICATE_ENTITY",
            details={
                "entity_type": entity_type,
                "field": field,
                "value": str(value)
            }
        )


# Authorization Exceptions
class AuthorizationException(LMSException):
    """Base exception for authorization-related errors."""
    pass


class PermissionDeniedException(AuthorizationException):
    """Raised when user lacks required permission."""
    
    def __init__(self, action: str, resource: Optional[str] = None):
        super().__init__(
            message=f"Permission denied for action: {action}",
            error_code="PERMISSION_DENIED",
            details={
                "action": action,
                "resource": resource
            }
        )


class InactiveUserException(AuthorizationException):
    """Raised when inactive user attempts action."""
    
    def __init__(self, user_id: Any):
        super().__init__(
            message="User account is not active",
            error_code="INACTIVE_USER",
            details={"user_id": str(user_id)}
        )
