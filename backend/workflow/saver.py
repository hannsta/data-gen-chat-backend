from typing import Dict, Any, Optional, List
import json
from datetime import datetime

# Database imports removed - now stateless
from ..models.schemas import WorkflowDefinition, WorkflowSaveRequest


class WorkflowSaver:
    def __init__(self):
        pass  # Now stateless
    
    def save_workflow(self, request: WorkflowSaveRequest) -> bool:
        """Save a workflow definition (stateless - always returns True)"""
        try:
            print(f"📄 Workflow '{request.workflow_name}' processed (stateless mode)")
            print(f"   • App URL: {request.app_url}")
            print(f"   • Timestamp: {datetime.utcnow().isoformat()}")
            return True
            
        except Exception as e:
            print(f"Error processing workflow {request.workflow_name}: {str(e)}")
            return False
    
    def get_workflow(self, workflow_name: str) -> Optional[WorkflowDefinition]:
        """Retrieve a workflow definition (stateless - returns None)"""
        print(f"📄 Workflow retrieval '{workflow_name}' not available in stateless mode")
        return None
    
    def list_workflows(self) -> List[Dict[str, str]]:
        """Get list of all workflows (stateless - returns empty list)"""
        print("📄 Workflow listing not available in stateless mode")
        return []
    
    def delete_workflow(self, workflow_name: str) -> bool:
        """Delete a workflow (stateless - always returns True)"""
        print(f"📄 Workflow deletion '{workflow_name}' processed (stateless mode)")
        return True
    
    def get_workflow_raw_json(self, workflow_name: str) -> Optional[Dict[str, Any]]:
        """Get the raw JSON blob for a workflow (stateless - returns None)"""
        print(f"📄 Raw JSON retrieval '{workflow_name}' not available in stateless mode")
        return None

# Global workflow saver instance  
workflow_saver = WorkflowSaver() 