import asyncio
import time
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from playwright.async_api import async_playwright
import random

from ..models.schemas import SessionRequest, SimulationStep, StepAction, SimulationResponse
from .pendo_capture import PendoCapture, PendoReplay

class Simulator:
    """Unified simulation system using Pendo request capture and replay"""
    
    def __init__(self):
        pass
    
    async def _smart_wait_for_dynamic_content(self, page, path: str, test_mode: bool = False):
        """Automatically wait for dynamic content based on the navigation path"""
        
        # Define path-specific selectors that commonly need extra loading time
        dynamic_content_selectors = {
            '/locations': [
                '[data-pendo-id="locations-grid"]',
                '[data-pendo-id="location-search-input"]',
                '[data-pendo-id="location-cards-container"]'
            ],
            '/dashboard': [
                '[data-pendo-id="dashboard-metrics"]',
                '[data-pendo-id="chart-container"]'
            ],
            '/shipments': [
                '[data-pendo-id="shipments-table"]',
                '[data-pendo-id="table-header-status"]'
            ],
            '/reports': [
                '[data-pendo-id="reports-grid"]',
                '[data-pendo-id="report-filters"]'
            ]
        }
        
        # Check if this path has known dynamic content
        selectors_to_wait_for = []
        for known_path, selectors in dynamic_content_selectors.items():
            if path.startswith(known_path):
                selectors_to_wait_for = selectors
                break
        
        if not selectors_to_wait_for:
            print(f"   ℹ️ No known dynamic content for path: {path}")
            return
        
        print(f"   🎯 Smart wait: Checking for dynamic content on {path}")
        
        # Progressive timeout strategy
        base_timeout = 2000 if test_mode else 4000
        max_timeout = 5000 if test_mode else 8000
        
        for selector in selectors_to_wait_for:
            try:
                print(f"   ⏳ Waiting for dynamic element: {selector}")
                await page.wait_for_selector(selector, state='visible', timeout=base_timeout)
                print(f"   ✅ Found dynamic element: {selector}")
                return  # Found at least one key element, we're good
                
            except Exception as e:
                print(f"   ⏸️ Element not found with base timeout: {selector}")
                
                # Try with longer timeout for this specific selector
                try:
                    print(f"   ⏳ Retrying with extended timeout: {selector}")
                    await page.wait_for_selector(selector, state='visible', timeout=max_timeout - base_timeout)
                    print(f"   ✅ Found dynamic element (extended wait): {selector}")
                    return  # Found it with extended timeout
                    
                except Exception as extended_error:
                    print(f"   ⚠️ Still not found: {selector} - continuing to next selector")
                    continue
        
        # If we get here, none of the expected selectors were found
        print(f"   ⚠️ No expected dynamic elements found for {path} - page may still be loading")
        
        # Fall back to a reasonable wait time
        fallback_wait = 1000 if test_mode else 2000
        print(f"   ⏳ Fallback wait: {fallback_wait}ms for dynamic content to load")
        await page.wait_for_timeout(fallback_wait)
    
    def _is_dynamic_selector(self, selector: str) -> bool:
        """Check if a selector is likely to be dynamically loaded content"""
        dynamic_patterns = [
            'location-card',
            'location-search',
            'locations-grid',
            'table-header',
            'shipments-table',
            'dashboard-metrics',
            'chart-container',
            'reports-grid',
            'report-filters',
            'view-details',
            'data-grid',
            'search-results',
            'filter-dropdown',
            'dynamic-content'
        ]
        
        selector_lower = selector.lower()
        return any(pattern in selector_lower for pattern in dynamic_patterns)
        
    async def simulate_session(self, request: SessionRequest) -> SimulationResponse:
        """Execute a single user session (for testing individual paths)"""
        print(f"🎯 Single session simulation not implemented - use record_and_replay for bulk simulation")
        return SimulationResponse(
            session_id=0,
            events_captured=0,
            execution_time_ms=0,
            status="not_implemented"
        )
    
    async def record_workflow_templates(self, workflow_name: str, app_url: str, user_journey_paths: List[Dict[str, Any]], test_mode: bool = False):
        """Record Pendo request templates for all paths in a workflow"""
        from playwright.async_api import async_playwright
        
        print(f"🎬 Recording templates for {workflow_name}")
        
        capture = PendoCapture()
        
        # Track failed actions across all paths
        failed_actions_log = {}
        
        async with async_playwright() as p:
            # Use headless=True for production deployment
            headless_mode = True  # Set to False for local development debugging
            browser = await p.chromium.launch(headless=headless_mode)
            
            for path in user_journey_paths:
                path_id = path['path_id']
                steps = path['steps']
                
                print(f"📹 Recording path: {path_id}")
                
                page = await browser.new_page()
                sequence = 0
                total_requests = 0
                pendo_requests = 0
                failed_actions_log[path_id] = []
                

                
                # Track current step for delay information
                current_step = None
                
                # Set up request interception for this path with step context
                async def intercept_for_path(route):
                    nonlocal sequence, total_requests, pendo_requests, current_step
                    total_requests += 1
                    # Pass original delay from current step
                    original_delay = current_step.get('delay_ms', 1000) if current_step else 1000
                    was_captured = await capture.intercept_pendo_request(route, path_id, sequence, original_delay)
                    if was_captured:
                        sequence += 1
                        pendo_requests += 1
                
                # Update the route with the new intercept function
                await page.route("**/*pendo.io*/**", intercept_for_path)
                
                # Execute the steps for this path
                for i, step in enumerate(steps, 1):
                    try:
                        current_step = step  # Update current step for delay context
                        print(f"🎬 Recording {path_id} - Step {i}: {step.get('description', step['action'])}")
                        
                        if step['action'] == 'navigate':
                            # Properly handle URL concatenation to avoid double slashes
                            base_url = app_url.rstrip('/')  # Remove trailing slash from base URL
                            path = step['value']
                            if not path.startswith('/'):
                                path = '/' + path  # Ensure path starts with slash
                            url = f"{base_url}{path}"
                            print(f"   → Navigating to: {url}")
                            await page.goto(url)
                            if not test_mode:
                                # Only wait for networkidle in normal mode (for Pendo capture)
                                await page.wait_for_load_state('networkidle', timeout=45000)
                            else:
                                # In test mode, just wait for DOM to be ready
                                await page.wait_for_load_state('domcontentloaded')
                            
                            # Always wait for page stability after navigation - increased for dynamic content
                            print(f"   ⏳ Waiting for page to stabilize after navigation...")
                            stabilization_wait = 2000  # Back to original 2 second wait
                            await page.wait_for_timeout(stabilization_wait)
                            
                            # Smart wait for dynamic content based on the path
                            await self._smart_wait_for_dynamic_content(page, step['value'], test_mode)
                            
                            # Extra wait to ensure Pendo is fully loaded (only in normal mode)
                            # Skip Pendo initialization wait in test mode - we only care about selector validation
                            if not test_mode:
                                pendo_wait = 3000  # Allow Pendo to initialize
                                await page.wait_for_timeout(pendo_wait)  # Wait for Pendo to initialize
                            
                            # Skip Pendo status check in test mode - we only care about selector validation
                            if not test_mode:
                                # Check what Pendo objects are available
                                try:
                                    pendo_info = await page.evaluate("""
                                        () => {
                                            return {
                                                hasPendo: typeof window.pendo !== 'undefined',
                                                hasTrack: typeof window.pendo !== 'undefined' && typeof window.pendo.track === 'function',
                                                hasVisitorId: window.pendo && window.pendo.get_visitor_id ? window.pendo.get_visitor_id() : null,
                                                pendoMethods: window.pendo ? Object.keys(window.pendo).slice(0, 10) : []
                                            };
                                        }
                                    """)
                                    print(f"   🔍 Pendo status: {pendo_info}")
                                except Exception as e:
                                    print(f"   ⚠️ Could not check Pendo status: {e}")
                                
                                print(f"   ⏳ Waited for Pendo initialization")
                            
                        elif step['action'] == 'click':
                            selector = step['selector']
                            print(f"   → Clicking: {selector}")
                            
                            # Check if previous step was navigate and this selector might need extra time
                            previous_step = steps[i-2] if i > 1 else None
                            needs_extra_wait = (previous_step and 
                                              previous_step.get('action') == 'navigate' and
                                              self._is_dynamic_selector(selector))
                            
                            # Wait for element and check if it exists
                            try:
                                # Use step-level timeout_ms if provided, otherwise use smart defaults
                                step_timeout = step.get('timeout_ms')
                                if step_timeout:
                                    selector_timeout = step_timeout
                                elif needs_extra_wait:
                                    selector_timeout = 5000 if test_mode else 8000  # Back to original values
                                    print(f"   🎯 Using extended timeout for post-navigation dynamic element")
                                else:
                                    selector_timeout = 3000 if test_mode else 5000  # Standard timeout
                                
                                print(f"   ⏳ Waiting for selector with {selector_timeout}ms timeout...")
                                await page.wait_for_selector(selector, timeout=selector_timeout)
                                element = await page.query_selector(selector)
                                if element:
                                    print(f"   ✅ Element found: {selector}")
                                    await page.click(selector)
                                    print(f"   ✅ Click executed: {selector}")
                                    
                                    # Brief wait after click for any UI updates (like dropdowns opening)
                                    brief_wait = 200 if test_mode else 400
                                    await page.wait_for_timeout(brief_wait)
                                    
                                    # Skip Pendo event capture wait in test mode - we only care about selector validation
                                    if not test_mode:
                                        print(f"   ⏳ Brief wait for Pendo click events...")
                                        click_wait = 500  # Wait for event capture
                                        await page.wait_for_timeout(click_wait)  # Brief wait for event capture
                                        print(f"   ⏳ Continuing...")
                                else:
                                    print(f"   ❌ Element not found: {selector}")
                            except Exception as click_error:
                                error_msg = str(click_error)
                                print(f"   ❌ Click failed: {selector} - {error_msg}")
                                
                                # Suggest wait_for_selector for timeout issues
                                if "timeout" in error_msg.lower():
                                    print(f"   💡 Suggestion: Use wait_for_selector action before clicking {selector}")
                                    print(f"   💡 Or increase timeout_ms parameter for this step")
                                
                                # Log the failed action
                                failure_entry = {
                                    'step': i,
                                    'selector': selector,
                                    'error': error_msg,
                                    'description': step.get('description', 'No description'),
                                    'action': 'click',
                                    'suggestion': 'Consider using wait_for_selector action or increasing timeout_ms' if 'timeout' in error_msg.lower() else None
                                }
                                failed_actions_log[path_id].append(failure_entry)
                                print(f"   📝 Logged action failure for reporting")
                                
                                # Try to list available elements for debugging
                                elements = await page.query_selector_all("[data-pendo-id]")
                                if elements:
                                    print(f"   🔍 Available data-pendo-id elements:")
                                    for elem in elements[:5]:  # Show first 5
                                        pendo_id = await elem.get_attribute("data-pendo-id")
                                        tag = await elem.evaluate("el => el.tagName")
                                        print(f"      - [{tag.lower()}][data-pendo-id='{pendo_id}']")
                                continue
                        elif step['action'] == 'type':
                            selector = step['selector']
                            value = step['value']
                            print(f"   → Typing '{value}' into: {selector}")
                            
                            # Check if previous step was navigate and this selector might need extra time
                            previous_step = steps[i-2] if i > 1 else None
                            needs_extra_wait = (previous_step and 
                                              previous_step.get('action') == 'navigate' and
                                              self._is_dynamic_selector(selector))
                            
                            try:
                                # Use step-level timeout_ms if provided, otherwise use smart defaults
                                step_timeout = step.get('timeout_ms')
                                if step_timeout:
                                    selector_timeout = step_timeout
                                elif needs_extra_wait:
                                    selector_timeout = 5000 if test_mode else 8000  # Back to original values
                                    print(f"   🎯 Using extended timeout for post-navigation dynamic element")
                                else:
                                    selector_timeout = 3000 if test_mode else 5000  # Standard timeout
                                
                                print(f"   ⏳ Waiting for selector with {selector_timeout}ms timeout...")
                                await page.wait_for_selector(selector, timeout=selector_timeout)
                                await page.fill(selector, value)
                                
                                # Skip Pendo event capture wait in test mode - we only care about selector validation
                                if not test_mode:
                                    type_wait = 200
                                    await page.wait_for_timeout(type_wait)  # Wait for type events
                                    print(f"   ⏳ Brief wait for type events")
                            except Exception as type_error:
                                error_msg = str(type_error)
                                print(f"   ❌ Type failed: {selector} - {error_msg}")
                                
                                # Suggest wait_for_selector for timeout issues
                                if "timeout" in error_msg.lower():
                                    print(f"   💡 Suggestion: Use wait_for_selector action before typing into {selector}")
                                    print(f"   💡 Or increase timeout_ms parameter for this step")
                                
                                # Log the failed action
                                failure_entry = {
                                    'step': i,
                                    'selector': selector,
                                    'error': error_msg,
                                    'description': step.get('description', 'No description'),
                                    'action': 'type',
                                    'value': value,
                                    'suggestion': 'Consider using wait_for_selector action or increasing timeout_ms' if 'timeout' in error_msg.lower() else None
                                }
                                failed_actions_log[path_id].append(failure_entry)
                                print(f"   📝 Logged action failure for reporting")
                            
                        elif step['action'] == 'wait_for_selector':
                            selector = step['selector']
                            # Use step-level timeout_ms if provided, otherwise use defaults
                            step_timeout = step.get('timeout_ms')
                            if step_timeout:
                                selector_timeout = step_timeout
                            else:
                                selector_timeout = 3000 if test_mode else 8000  # Longer timeout for explicit waits
                            
                            print(f"   → Waiting for selector to be visible: {selector} (timeout: {selector_timeout}ms)")
                            try:
                                await page.wait_for_selector(selector, state='visible', timeout=selector_timeout)
                                print(f"   ✅ Selector found and visible: {selector}")
                            except Exception as wait_error:
                                print(f"   ❌ Wait for selector failed: {selector} - {wait_error}")
                                
                                # Log the failed action
                                failure_entry = {
                                    'step': i,
                                    'selector': selector,
                                    'error': str(wait_error),
                                    'description': step.get('description', 'No description'),
                                    'action': 'wait_for_selector'
                                }
                                failed_actions_log[path_id].append(failure_entry)
                                print(f"   📝 Logged action failure for reporting")
                                
                                # Try to list available elements for debugging
                                elements = await page.query_selector_all("[data-pendo-id]")
                                if elements:
                                    print(f"   🔍 Available data-pendo-id elements:")
                                    for elem in elements[:5]:  # Show first 5
                                        pendo_id = await elem.get_attribute("data-pendo-id")
                                        tag = await elem.evaluate("el => el.tagName")
                                        print(f"      - [{tag.lower()}][data-pendo-id='{pendo_id}']")
                                continue
                        
                        elif step['action'] == 'wait':
                            # Skip wait steps in test mode - we only care about selector validation
                            if not test_mode:
                                original_delay = step.get('delay_ms', 1000)
                                recording_delay = max(200, original_delay // 10)  # Divide by 10, minimum 200ms
                                print(f"   → Waiting {recording_delay}ms (original: {original_delay}ms)")
                                await page.wait_for_timeout(recording_delay)
                        
                        # Skip step delays in test mode - we only care about selector validation
                        if not test_mode:
                            # Use original delay divided by 10 for fast recording
                            original_delay = step.get('delay_ms', 1000)
                            recording_delay = max(100, original_delay // 10)  # Minimum 100ms, divide by 10
                            await page.wait_for_timeout(recording_delay)
                        
                    except Exception as e:
                        print(f"❌ Step {i} failed for {path_id}: {e}")
                        
                        # Log the failed action for reporting
                        failed_actions_log[path_id].append({
                            'step': i,
                            'selector': step.get('selector', 'N/A'),
                            'error': str(e),
                            'description': step.get('description', 'No description'),
                            'action': step.get('action', 'unknown'),
                            'value': step.get('value', '')
                        })
                        print(f"   📝 Logged action failure for reporting")
                        continue
                
                # Final wait to capture any remaining Pendo events (AFTER all steps)
                if test_mode:
                    # In test mode, we only care about selector validation, not Pendo capture
                    print(f"   ⏳ Brief wait to ensure page is stable...")
                    await page.wait_for_timeout(500)  # Just ensure page is stable
                else:
                    # In normal mode, we need to capture all Pendo requests
                    print(f"   ⏳ Final wait for any remaining Pendo events...")
                    await page.wait_for_timeout(3000)
                    print(f"   ⏳ Ensuring all network requests are captured...")
                    
                    try:
                        await page.wait_for_load_state('networkidle', timeout=15000)
                    except Exception as e:
                        print(f"   ⚠️ Network timeout (15000ms) - continuing with captured data: {e}")
                        # Don't let network timeout kill the entire function
                
                await page.close()
                print(f"✅ Recorded {pendo_requests} Pendo requests for {path_id} (out of {total_requests} total network requests)")
            
            await browser.close()
        
        # Generate failed actions summary
        self._generate_failed_actions_report(failed_actions_log)
        
        # Handle test mode vs normal mode
        if test_mode:
            # Return test mode results with failed actions
            total_failures = sum(len(failures) for failures in failed_actions_log.values())
            validation_msg = f"✅ All paths validated successfully!" if total_failures == 0 else f"⚠️ {total_failures} failed actions found"
            
            print(f"📊 SUMMARY: Collected {total_failures} total failures across {len(failed_actions_log)} paths")
            for path_id, failures in failed_actions_log.items():
                if failures:
                    print(f"  - {path_id}: {len(failures)} failures")
            
            return {
                'templates_recorded': len(capture.captured_requests),
                'failed_actions': failed_actions_log,
                'test_mode': True
            }
        else:
            # Save all captured templates for normal recording
            capture.save_templates(workflow_name)
            return len(capture.captured_requests)
    
    def _generate_failed_actions_report(self, failed_actions_log: Dict[str, List[Dict]]):
        """Generate a summary report of all failed actions"""
        
        total_failures = sum(len(failures) for failures in failed_actions_log.values())
        
        if total_failures == 0:
            print("\n✅ SUCCESS: All selectors worked perfectly!")
            return
        
        print(f"\n⚠️  FAILED ACTIONS REPORT ({total_failures} total failures)")
        print("=" * 60)
        
        for path_id, failures in failed_actions_log.items():
            if not failures:
                print(f"✅ {path_id}: All actions successful")
                continue
                
            print(f"\n❌ {path_id}: {len(failures)} failed actions")
            for failure in failures:
                action_type = failure.get('action', 'click')
                selector = failure['selector']
                error = failure['error']
                step = failure['step']
                description = failure['description']
                
                print(f"   Step {step}: {action_type.upper()} '{selector}'")
                print(f"   Description: {description}")
                print(f"   Error: {error}")
                
                if 'value' in failure:
                    print(f"   Value: '{failure['value']}'")
                
                if 'suggestion' in failure and failure['suggestion']:
                    print(f"   💡 Suggestion: {failure['suggestion']}")
                
                print()
        
        print("💡 Failed actions are available in the API response for analysis!")
    
    async def bulk_simulate(self, workflow_name: str, user_count: int, days: int, user_journey_paths: List[Dict[str, Any]], batch_size: int = 1) -> Dict[str, Any]:
        """Execute bulk simulation using Pendo request replay"""
        
        print(f"🚀 Starting bulk simulation for {workflow_name}")
        print(f"   • Total users: {user_count}")
        print(f"   • Time range: {days} days")
        
        # Calculate distribution based on user journey percentages
        path_distributions = {}
        total_percentage = sum(path['percentage'] for path in user_journey_paths)
        
        for path in user_journey_paths:
            path_percentage = path['percentage'] / total_percentage
            path_count = int(user_count * path_percentage)
            path_distributions[path['path_id']] = path_count
        
        # Ensure we hit the exact user count
        assigned_count = sum(path_distributions.values())
        if assigned_count < user_count:
            # Add remaining users to the largest path
            largest_path = max(path_distributions.keys(), key=lambda k: path_distributions[k])
            path_distributions[largest_path] += user_count - assigned_count
        
        print(f"📊 User distribution:")
        for path_id, count in path_distributions.items():
            percentage = (count / user_count) * 100
            print(f"   • {path_id}: {count} users ({percentage:.1f}%)")
        
        # Execute Pendo replay (stateless)
        try:
            async with PendoReplay() as replay:
                await replay.bulk_replay(
                    workflow_name=workflow_name,
                    path_distributions=path_distributions,
                    days_back=days,
                    batch_size=batch_size
                )
            
            return {
                'success': True,
                'sessions_scheduled': user_count,
                'sessions_completed': user_count,
                'workflow_name': workflow_name,
                'path_distribution': path_distributions,
                'performance_note': 'High-performance stateless simulation completed!'
            }
            
        except Exception as e:
            print(f"❌ Simulation failed: {e}")
            
            return {
                'success': False,
                'error': str(e),
                'sessions_scheduled': user_count,
                'sessions_completed': 0,
                'workflow_name': workflow_name
            }

# Convenience functions for easy usage
async def record_and_replay(workflow_name: str, app_url: str, user_journey_paths: List[Dict[str, Any]], total_users: int = 1, batch_size: int = 1, test_mode: bool = False):
    """Complete workflow: record templates then replay at scale"""
    
    # Initialize (stateless)
    simulator = Simulator()
    
    # Step 1: Record templates (or test validation)
    step_text = "📋 Step 1: Testing workflow validation..." if test_mode else "📋 Step 1: Recording Pendo request templates..."
    print(step_text)
    
    recording_result = await simulator.record_workflow_templates(workflow_name, app_url, user_journey_paths, test_mode)
    
    # Handle test mode results
    if test_mode and isinstance(recording_result, dict):
        templates_count = recording_result.get('templates_recorded', 0)
        failed_actions = recording_result.get('failed_actions', {})
        
        if templates_count == 0:
            print("❌ No templates recorded - check your Pendo integration")
            return {
                'success': False,
                'error': 'No templates recorded',
                'test_mode': True,
                'failed_actions': failed_actions
            }
        
        # Return test results without doing replay
        total_failures = sum(len(failures) for failures in failed_actions.values())
        validation_msg = f"✅ All paths validated successfully!" if total_failures == 0 else f"⚠️ {total_failures} failed actions found"
        
        print(f"✅ Validated {templates_count} paths")
        print(validation_msg)
        
        # Show detailed failure info if there are any
        if total_failures > 0:
            print("\n📋 Validation Failures:")
            for path_id, failures in failed_actions.items():
                if failures:
                    print(f"  ❌ {path_id}: {len(failures)} failures")
                    for failure in failures:
                        step_num = failure.get('step', '?')
                        action = failure.get('action', 'unknown')
                        selector = failure.get('selector', 'N/A')
                        error = failure.get('error', 'Unknown error')
                        print(f"    Step {step_num} ({action}): {selector} - {error}")
        
        result_to_return = {
            'success': True,
            'templates_recorded': templates_count,
            'test_mode': True,
            'failed_actions': failed_actions,
            'validation_summary': validation_msg,
            'sessions_completed': 0  # No replay in test mode
        }
        return result_to_return
    
    # Normal mode - check template recording
    templates_recorded = recording_result if isinstance(recording_result, int) else 0
    if templates_recorded == 0:
        print("❌ No templates recorded - check your Pendo integration")
        return {'success': False, 'error': 'No templates recorded'}
    
    print(f"✅ Recorded templates for {templates_recorded} paths")
    
    # Step 2: Bulk replay at scale
    print(f"\n⚡ Step 2: Bulk replay for {total_users} users...")
    
    result = await simulator.bulk_simulate(
        workflow_name=workflow_name,
        user_count=total_users,
        days=6,
        user_journey_paths=user_journey_paths,
        batch_size=batch_size
    )
    
    if result['success']:
        print(f"🎉 Success! Generated {result['sessions_completed']} user sessions")
        print(f"   {result.get('performance_note', '')}")
    else:
        print(f"❌ Failed: {result.get('error', 'Unknown error')}")
    
    return result

# Global simulator instance
simulator = Simulator() 