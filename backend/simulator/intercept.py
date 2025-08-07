import json
import re
from typing import List, Dict, Any, Callable, Optional
from datetime import datetime
from playwright.async_api import Page, Route, Request
import asyncio

# Database imports removed - now stateless
from ..models.schemas import PendoEvent

class PendoEventInterceptor:
    def __init__(self):
        pass  # Now stateless
        self.captured_events: List[Dict[str, Any]] = []
        self.session_id: Optional[int] = None
        
        # Pendo URL patterns to intercept
        self.pendo_patterns = [
            r'.*\.pendo\.io.*',
            r'.*pendo.*analytics.*',
            r'.*pendo.*events.*',
            r'.*pendo.*track.*'
        ]
    
    def set_session_id(self, session_id: int):
        """Set the session ID for event tracking"""
        self.session_id = session_id
        self.captured_events = []
    
    async def setup_interception(self, page: Page):
        """Set up network interception for Pendo events"""
        await page.route("**/*", self._handle_request)
    
    async def _handle_request(self, route: Route):
        """Handle intercepted network requests"""
        request = route.request
        
        # Check if this is a Pendo request
        if self._is_pendo_request(request.url):
            # Capture the request data
            await self._capture_pendo_event(request)
        
        # Always continue the request to maintain normal app behavior
        await route.continue_()
    
    def _is_pendo_request(self, url: str) -> bool:
        """Check if URL matches Pendo patterns"""
        for pattern in self.pendo_patterns:
            if re.match(pattern, url, re.IGNORECASE):
                return True
        return False
    
    async def _capture_pendo_event(self, request: Request):
        """Capture and store a Pendo event"""
        try:
            # Extract event data
            url = request.url
            method = request.method
            headers = dict(request.headers)
            
            # Get POST data if available
            post_data = None
            if method == "POST":
                try:
                    post_data = request.post_data
                    if post_data:
                        # Try to parse as JSON
                        try:
                            post_data = json.loads(post_data)
                        except json.JSONDecodeError:
                            # Keep as string if not valid JSON
                            pass
                except Exception:
                    post_data = None
            
            # Determine event type from URL and data
            event_type = self._determine_event_type(url, post_data)
            
            # Create event payload
            event_payload = {
                'method': method,
                'url': url,
                'headers': headers,
                'post_data': post_data,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            # Store in memory for immediate access (stateless)
            self.captured_events.append({
                'event_type': event_type,
                'url': url,
                'payload': event_payload,
                'timestamp': datetime.utcnow()
            })
            
            # Database storage removed - now stateless
                
        except Exception as e:
            print(f"Error capturing Pendo event: {str(e)}")
    
    def _determine_event_type(self, url: str, post_data: Any) -> str:
        """Determine the type of Pendo event based on URL and data"""
        url_lower = url.lower()
        
        # Common Pendo event types
        if 'track' in url_lower or 'event' in url_lower:
            return 'track'
        elif 'identify' in url_lower:
            return 'identify'
        elif 'page' in url_lower or 'pageview' in url_lower:
            return 'page'
        elif 'guide' in url_lower:
            return 'guide'
        elif 'poll' in url_lower:
            return 'poll'
        elif 'feedback' in url_lower:
            return 'feedback'
        
        # Try to determine from POST data
        if isinstance(post_data, dict):
            if 'type' in post_data:
                return post_data['type']
            elif 'event' in post_data:
                return 'custom_event'
            elif 'action' in post_data:
                return 'action'
        
        return 'unknown'
    
    def get_captured_events(self) -> List[Dict[str, Any]]:
        """Get all events captured in the current session"""
        return self.captured_events.copy()
    
    def get_event_count(self) -> int:
        """Get the number of events captured"""
        return len(self.captured_events)
    
    def clear_events(self):
        """Clear captured events"""
        self.captured_events = []
    
    async def wait_for_events(self, expected_count: int, timeout_seconds: int = 10) -> bool:
        """Wait for a specific number of events to be captured"""
        start_time = datetime.utcnow()
        
        while len(self.captured_events) < expected_count:
            if (datetime.utcnow() - start_time).total_seconds() > timeout_seconds:
                return False
            await asyncio.sleep(0.1)
        
        return True
    
    def filter_events_by_type(self, event_type: str) -> List[Dict[str, Any]]:
        """Filter captured events by type"""
        return [event for event in self.captured_events if event['event_type'] == event_type]

# Global interceptor instance
pendo_interceptor = PendoEventInterceptor() 