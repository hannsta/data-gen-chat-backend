from pydantic import BaseModel, Field, HttpUrl
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
from enum import Enum

# ElementType and TaggedElement removed - ChatGPT analyzes codebase directly

class StepAction(str, Enum):
    CLICK = "click"
    TYPE = "type"
    WAIT = "wait"
    NAVIGATE = "navigate"
    SCROLL = "scroll"
    HOVER = "hover"
    SELECT = "select"

class SimulationStep(BaseModel):
    action: StepAction = Field(..., description="Action to perform")
    selector: Optional[str] = Field(None, description="CSS selector for action target")
    value: Optional[str] = Field(None, description="Text to type or URL to navigate to")
    delay_ms: int = Field(1000, description="Delay after this step in milliseconds")
    description: Optional[str] = Field(None, description="Human-readable step description")

class UserJourneyPath(BaseModel):
    path_id: str = Field(..., description="Unique identifier for this user journey path")
    percentage: Optional[float] = Field(None, description="Percentage of users who follow this exact path (null if using user segments)", ge=0, le=100)
    description: str = Field(..., description="Human-readable description of user behavior")
    steps: List[SimulationStep] = Field(..., description="Exact sequence of steps this user type follows")

# New models for user segmentation
class Account(BaseModel):
    """Represents a B2B company/organization account"""
    account_id: str = Field(..., description="Unique company identifier (e.g. 'acmecorp')")
    attributes: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Company attributes (e.g. tier, industry)")
    user_count: int = Field(10, description="Number of users in this account", ge=1)

class UserSegment(BaseModel):
    """Defines a user segment with minimal metadata and path preferences"""
    segment_id: str = Field(..., description="Unique identifier for this user segment")
    percentage: float = Field(..., description="Percentage of total users in this segment", ge=0, le=100)
    description: str = Field(..., description="Human-readable description of this user segment")
    
    # Simplified metadata - just the essentials
    user_attributes: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Key user attributes for Pendo (e.g. plan_type, user_role)")
    
    # Path assignment logic
    path_preferences: Dict[str, float] = Field(..., description="Mapping of path_id to percentage preference for this segment")

class WorkflowDefinition(BaseModel):
    workflow_name: str = Field(..., description="Unique identifier for the workflow")
    description: Optional[str] = Field(None, description="Human-readable description")
    user_journey_paths: List[UserJourneyPath] = Field(..., description="Specific user journey paths with percentages")
    
    # Account and user segmentation structure
    accounts: Optional[List[Account]] = Field(None, description="B2B company accounts that will use the system")
    user_segments: Optional[List[UserSegment]] = Field(None, description="User segments with metadata and path preferences (enables advanced user stories)")
    
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional workflow metadata")
    
    def uses_segmentation(self) -> bool:
        """Check if this workflow uses user segmentation"""
        return self.user_segments is not None and len(self.user_segments) > 0
    
    def uses_accounts(self) -> bool:
        """Check if this workflow defines specific accounts"""
        return self.accounts is not None and len(self.accounts) > 0

class SessionRequest(BaseModel):
    workflow_name: str = Field(..., description="Name of workflow to execute")
    app_url: HttpUrl = Field(..., description="Live hosted app URL to simulate against")
    path_id: str = Field(..., description="User journey path identifier for this session")  
    user_id: str = Field(..., description="Simulated user identifier")
    timestamp: datetime = Field(..., description="When this session occurred")
    steps: List[SimulationStep] = Field(..., description="Exact steps to execute for this user journey")


class WorkflowSaveRequest(BaseModel):
    workflow_name: str = Field(..., description="Unique workflow identifier")
    app_url: HttpUrl = Field(..., description="Live hosted app URL")
    json_blob: Dict[str, Any] = Field(..., description="Complete workflow definition JSON")



class PendoEvent(BaseModel):
    id: Optional[int] = Field(None, description="Database record ID")
    session_id: int = Field(..., description="Associated session ID")
    event_type: str = Field(..., description="Type of Pendo event")
    url: str = Field(..., description="Pendo endpoint URL")
    payload: Dict[str, Any] = Field(..., description="Raw event payload")
    timestamp: datetime = Field(..., description="Event capture time")

# ExtractResponse removed - ChatGPT analyzes codebase directly

class SimulationResponse(BaseModel):
    session_id: int = Field(..., description="Created session record ID")
    events_captured: int = Field(..., description="Number of Pendo events intercepted")
    execution_time_ms: int = Field(..., description="Total simulation time")
    status: str = Field(..., description="Success/failure status")




# Streamlined execution schemas
class DirectExecutionRequest(BaseModel):
    workflow_json: WorkflowDefinition = Field(..., description="Complete workflow definition")
    app_url: HttpUrl = Field(..., description="Live app URL to execute against")
    user_count: int = Field(100, description="Total number of users to simulate")
    batch_size: int = Field(10, description="Number of users to process in each batch")
    test_mode: bool = Field(False, description="If true, only test recording with minimal delays and return validation results")

class DirectExecutionResponse(BaseModel):
    success: bool = Field(..., description="Whether execution completed successfully")
    workflow_name: str = Field(..., description="Name of the executed workflow")
    sessions_completed: int = Field(..., description="Number of user sessions generated")
    templates_recorded: int = Field(..., description="Number of path templates recorded")
    execution_time_seconds: float = Field(..., description="Total execution time")
    performance_note: Optional[str] = Field(None, description="Performance summary")
    error: Optional[str] = Field(None, description="Error message if failed")
    test_mode: bool = Field(False, description="Whether this was a test run")
    failed_actions: Optional[Dict[str, List[Dict]]] = Field(None, description="Failed actions by path (test mode only)")
    validation_summary: Optional[str] = Field(None, description="Summary of validation results (test mode only)") 