#!/usr/bin/env python3
"""
Dynamic Pendo Workflow Simulation
=================================

Loads workflow definitions from JSON files and simulates realistic user behavior
using live Pendo events via automated browser workflows.

Features:
- Load workflow definitions from JSON files at runtime
- Configurable app URLs and backend endpoints
- Historical simulation across time ranges
- CLI control for batch size, user count, and duration

Author: ChatGPT for Pendo SEs
"""

import requests
import asyncio
import nest_asyncio
import json
import os
import sys
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.simulator.simulate import record_and_replay

# =============================================================================
# CONFIGURATION
# =============================================================================

DEFAULT_BACKEND_URL = "http://localhost:8000"

# =============================================================================
# WORKFLOW LOADER
# =============================================================================

def load_workflow_from_file(filepath: str) -> Optional[Dict[str, Any]]:
    """Load workflow definition from JSON file"""
    try:
        with open(filepath, 'r') as f:
            workflow = json.load(f)
        
        # Validate required fields
        required_fields = ['workflow_name', 'description', 'user_journey_paths']
        for field in required_fields:
            if field not in workflow:
                print(f"❌ Missing required field '{field}' in workflow JSON")
                return None
        
        # Validate user journey paths
        total_percentage = sum(path.get('percentage', 0) for path in workflow['user_journey_paths'])
        if abs(total_percentage - 100.0) > 0.1:  # Allow small floating point errors
            print(f"⚠️  Warning: Path percentages sum to {total_percentage}% (should be 100%)")
        
        print(f"✅ Loaded workflow: {workflow['workflow_name']}")
        print(f"   • Description: {workflow['description']}")
        print(f"   • Paths: {len(workflow['user_journey_paths'])}")
        return workflow
        
    except FileNotFoundError:
        print(f"❌ Workflow file not found: {filepath}")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in workflow file: {e}")
        return None
    except Exception as e:
        print(f"❌ Error loading workflow: {e}")
        return None

    

# =============================================================================
# BACKEND OPERATIONS
# =============================================================================

def check_backend_health(backend_url: str) -> bool:
    """Check if backend is available"""
    try:
        res = requests.get(f"{backend_url}/health", timeout=5)
        return res.status_code == 200
    except Exception as e:
        print(f"❌ Backend not reachable: {e}")
        return False

def save_workflow_to_backend(workflow: Dict[str, Any], app_url: str, backend_url: str) -> bool:
    """Save workflow definition to backend"""
    try:
        res = requests.post(f"{backend_url}/save_workflow_json", json={
            "workflow_name": workflow["workflow_name"],
            "app_url": app_url,
            "json_blob": workflow
        })
        return res.status_code == 200
    except Exception as e:
        print(f"❌ Failed to save workflow: {e}")
        return False

# =============================================================================
# SIMULATION LOGIC
# =============================================================================

class DynamicWorkflowSimulator:
    def __init__(self, backend_url: str = DEFAULT_BACKEND_URL):
        self.backend_url = backend_url
    
    async def run_simulation(self, 
                           workflow_file: str,
                           app_url: str,
                           user_count: int = 1,
                           batch_size: int = 1) -> bool:
        """Run complete simulation from workflow file"""
        
        print(f"\n🤖 Dynamic Workflow Simulation")
        print("=" * 60)
        
        # Phase 1: Load workflow
        print(f"\n📋 PHASE 1: Loading Workflow Definition")
        print(f"📄 Loading from: {workflow_file}")
        workflow = load_workflow_from_file(workflow_file)
        if not workflow:
            return False
        
        # Phase 2: Backend setup
        print(f"\n🎯 PHASE 2: Backend Setup")
        print(f"🔍 Checking backend at {self.backend_url}...")
        if not check_backend_health(self.backend_url):
            print("❌ Backend unavailable — start the simulator backend first.")
            return False
        print("✅ Backend online")
        
        # Phase 3: Save workflow
        print(f"\n💾 PHASE 3: Registering Workflow")
        if save_workflow_to_backend(workflow, app_url, self.backend_url):
            print(f"✅ Registered: {workflow['workflow_name']}")
        else:
            print("❌ Registration failed.")
            return False
        
        # Phase 4: Run simulation
        print(f"\n🚀 PHASE 4: Running Simulation")
        print(f"🎯 Target: {app_url}")
        print(f"👥 Users: {user_count} in batches of {batch_size}")
        
        result = await record_and_replay(
            workflow_name=workflow["workflow_name"],
            app_url=app_url,
            user_journey_paths=workflow["user_journey_paths"],
            total_users=user_count,
            batch_size=batch_size
        )
        
        if result:
            print(f"\n✅ PHASE 5: Simulation Complete")
            self._print_insights(workflow)
            return True
        else:
            print("❌ Simulation failed")
            return False
    
    def _print_insights(self, workflow: Dict[str, Any]):
        """Print workflow insights and summary"""
        print(f"\n📊 Workflow Insights: {workflow['workflow_name']}")
        print(f"📝 {workflow['description']}")
        
        for path in workflow["user_journey_paths"]:
            steps_count = len(path["steps"])
            duration_est = sum(step.get("delay_ms", 0) for step in path["steps"]) // 1000
            print(f"   • {path['description']} ({path['percentage']}%) → {steps_count} steps, ~{duration_est}s")
        
        metadata = workflow.get("metadata", {})
        print(f"\n💡 Key Metrics:")
        print(f"   - Total behavior variants: {metadata.get('total_paths', 'N/A')}")
        print(f"   - Average session: ~{metadata.get('estimated_avg_duration_ms', 0)//1000}s")
        print(f"   - Focus area: {metadata.get('focus', 'general_behavior').replace('_', ' ').title()}")

# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

async def run_workflow_simulation(workflow_file: str, 
                                app_url: str,
                                user_count: int = 1,
                                batch_size: int = 1,
                                backend_url: str = DEFAULT_BACKEND_URL) -> bool:
    """Convenience function to run a complete workflow simulation"""
    simulator = DynamicWorkflowSimulator(backend_url)
    return await simulator.run_simulation(workflow_file, app_url, user_count, batch_size)

def sync_run_workflow(workflow_file: str,
                     app_url: str, 
                     user_count: int = 1,
                     batch_size: int = 1,
                     test_mode: bool = False,
                     backend_url: str = DEFAULT_BACKEND_URL) -> Dict[str, Any]:
    """Direct API call to execute_workflow endpoint - supports all backend features"""
    import requests
    
    # Load workflow
    workflow = load_workflow_from_file(workflow_file)
    
    # Prepare request
    request_data = {
        "workflow_json": workflow,
        "app_url": app_url,
        "user_count": user_count,
        "batch_size": batch_size,
        "test_mode": test_mode
    }
    
    try:
        print(f"🚀 Calling execute_workflow endpoint...")
        print(f"   • Workflow: {workflow['workflow_name']}")
        print(f"   • App URL: {app_url}")
        print(f"   • Users: {user_count} (batch: {batch_size})")
        print(f"   • Test mode: {test_mode}")
        print(f"   • Mode: Stateless (no database)")
        
        response = requests.post(
            f"{backend_url}/execute_workflow",
            json=request_data,
            timeout=600 if not test_mode else 300  # 5 minutes for test mode
        )
        
        if response.status_code == 200:
            result = response.json()
            
            if test_mode:
                print(f"🧪 Test completed in {result['execution_time_seconds']}s")
                
                # First check if the backend reported a failure
                if not result.get('success', False):
                    error_msg = result.get('error', 'Unknown error')
                    print(f"❌ TEST FAILED - Backend error: {error_msg}")
                    return result
                
                # If backend success=True, check for failed actions
                failed_actions = result.get('failed_actions', {})
                
                # Count total failures across all paths
                total_failures = 0
                if failed_actions:
                    total_failures = sum(len(failures) for failures in failed_actions.values() if failures)
                
                if total_failures > 0:
                    print(f"❌ TEST FAILED - {total_failures} failed actions found:")
                    
                    for path_id, failures in failed_actions.items():
                        if failures:
                            print(f"  📍 {path_id}: {len(failures)} failures")
                            for failure in failures:
                                step = failure.get('step', '?')
                                action = failure.get('action', 'unknown')
                                selector = failure.get('selector', 'N/A')
                                error = failure.get('error', 'Unknown error')
                                # Simplify error message - just get the first line
                                error_short = error.split('\n')[0] if '\n' in error else error
                                print(f"    Step {step} ({action}): {selector}")
                                print(f"    Error: {error_short}")
                else:
                    print(f"✅ TEST PASSED - All selectors validated successfully!")
            else:
                # Non-test mode - check backend success
                if not result.get('success', False):
                    error_msg = result.get('error', 'Unknown error')
                    print(f"❌ EXECUTION FAILED - Backend error: {error_msg}")
                    return result
                
                print(f"✅ Execution completed in {result['execution_time_seconds']}s")
                print(f"📊 Sessions: {result['sessions_completed']}")
                print(f"📝 Templates: {result['templates_recorded']}")
            
            return result
        else:
            print(f"❌ HTTP Error {response.status_code}: {response.text}")
            return {"success": False, "error": f"HTTP {response.status_code}"}
            
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return {"success": False, "error": str(e)}

# =============================================================================
# CLI INTERFACE
# =============================================================================

def main():
    """CLI interface for the dynamic workflow simulator"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Dynamic Pendo Workflow Simulator')
    parser.add_argument('workflow_file', help='Path to workflow JSON file')
    parser.add_argument('app_url', help='Live app URL to simulate against')
    parser.add_argument('--users', type=int, default=1, help='Number of users to simulate')
    parser.add_argument('--batch-size', type=int, default=1, help='Batch size for simulation')
    parser.add_argument('--backend', default=DEFAULT_BACKEND_URL, help='Backend URL')
    parser.add_argument('--create-template', help='Create a template workflow file')
    
    args = parser.parse_args()
    
    if args.create_template:
        save_workflow_template(args.create_template)
        return
    
    print(f"🚀 Starting simulation...")
    print(f"📄 Workflow: {args.workflow_file}")
    print(f"🎯 App: {args.app_url}")
    print(f"👥 Users: {args.users} (batches of {args.batch_size})")
    
    success = sync_run_workflow(
        workflow_file=args.workflow_file,
        app_url=args.app_url,
        user_count=args.users,
        batch_size=args.batch_size,
        backend_url=args.backend
    )
    
    if success:
        print(f"\n🎉 Simulation Complete!")
    else:
        print(f"\n❌ Simulation Failed!")
        exit(1)

if __name__ == "__main__":
    main() 