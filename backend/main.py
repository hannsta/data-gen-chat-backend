import time
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .models.schemas import DirectExecutionRequest, DirectExecutionResponse
from .simulator.simulate import record_and_replay

app = FastAPI(
    title="Pendo Data Generation API", 
    description="Streamlined API for validating and executing Pendo workflow simulations",
    version="2.0.0"
)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "Pendo Data Generation API - Streamlined Version",
        "version": "2.0.0",
        "endpoints": {
            "health": "GET /health",
            "execute_workflow": "POST /execute_workflow"
        }
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "database": "none", "mode": "stateless"}

@app.post("/execute_workflow", response_model=DirectExecutionResponse)
async def execute_workflow(request: DirectExecutionRequest):
    """
    Single endpoint to validate and execute Pendo workflow simulations.
    
    Two modes:
    1. test_mode=true: Fast validation of selectors (~30-60 seconds)
    2. test_mode=false: Full execution with specified user count
    
    No database dependencies - completely stateless operation.
    """
    
    start_time = time.time()
    
    try:
        workflow_data = request.workflow_json
        
        # Extract workflow information
        workflow_name = workflow_data.workflow_name
        app_url = str(request.app_url)
        user_journey_paths = [path.dict() for path in workflow_data.user_journey_paths]
        
        # Execute the complete workflow
        result = await record_and_replay(
            workflow_name=workflow_name,
            app_url=app_url,
            user_journey_paths=user_journey_paths,
            total_users=request.user_count,
            batch_size=request.batch_size,
            test_mode=request.test_mode
        )
        
        execution_time = time.time() - start_time
        
        if result and result.get('success', False):
            response = DirectExecutionResponse(
                success=True,
                workflow_name=workflow_name,
                sessions_completed=result.get('sessions_completed', 0),
                templates_recorded=result.get('templates_recorded', len(user_journey_paths)),
                execution_time_seconds=round(execution_time, 2),
                performance_note=result.get('performance_note', f'Completed in {execution_time:.1f}s'),
                test_mode=request.test_mode,
                failed_actions=result.get('failed_actions') if request.test_mode else None,
                validation_summary=result.get('validation_summary') if request.test_mode else None
            )
            
            return response
            
        else:
            error_msg = result.get('error', 'Unknown execution error') if result else 'Execution returned no result'
            return DirectExecutionResponse(
                success=False,
                workflow_name=workflow_name,
                sessions_completed=0,
                templates_recorded=0,
                execution_time_seconds=round(execution_time, 2),
                error=error_msg,
                test_mode=request.test_mode
            )
            
    except Exception as e:
        execution_time = time.time() - start_time
        return DirectExecutionResponse(
            success=False,
            workflow_name=request.workflow_json.workflow_name if hasattr(request.workflow_json, 'workflow_name') else 'unknown',
            sessions_completed=0,
            templates_recorded=0,
            execution_time_seconds=round(execution_time, 2),
            error=str(e),
            test_mode=request.test_mode
        ) 