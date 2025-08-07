"""
Pendo Event Capture & Replay System
===================================

Captures real Pendo jzb requests during browser simulation,
then replays them at scale with realistic variations.
"""

import base64
import json
import gzip
import urllib.parse
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import random
import string
import asyncio
import aiohttp
import ssl
from dataclasses import dataclass, asdict

@dataclass
class PendoEventTemplate:
    """Template for a Pendo event with variable placeholders"""
    path_id: str
    sequence_order: int
    base_url: str
    query_params: Dict[str, str]
    decoded_events: List[Dict[str, Any]]
    timing_delay_ms: int  # Delay from previous event

class PendoCapture:
    """Captures Pendo requests during browser simulation"""
    
    def __init__(self):
        self.captured_requests: Dict[str, List[PendoEventTemplate]] = {}
    
    async def intercept_pendo_request(self, route, path_id: str, sequence_order: int, original_delay_ms: int = 1000) -> bool:
        """Intercept and capture Pendo requests during browser simulation"""
        request = route.request
        
        # Check for any Pendo-related requests (broader filter)
        is_pendo_request = (
            'pendo.io' in request.url or 
            'pendo' in request.url.lower()
        )
        
        if is_pendo_request:
            import datetime
            current_time = datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]
            print(f"📡 [{current_time}] Intercepting Pendo GET request: {request.url[:100]}...")
            
            # Parse the request
            parsed_url = urllib.parse.urlparse(request.url)
            query_params = urllib.parse.parse_qs(parsed_url.query)
            
            print(f"   → Method: {request.method}")
            print(f"   → Base URL: {parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}")
            
            # Decode the jzb parameter
            if 'jzb' in query_params:
                jzb_encoded = query_params['jzb'][0]
                decoded_events = self.decode_jzb(jzb_encoded)
                if decoded_events:
                    pass  # Events decoded successfully
                
                # Create template
                template = PendoEventTemplate(
                    path_id=path_id,
                    sequence_order=sequence_order,
                    base_url=f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}",
                    query_params={k: v[0] for k, v in query_params.items()},
                    decoded_events=decoded_events,
                    timing_delay_ms=original_delay_ms  # Use original workflow delay
                )
                
                # Store the template
                if path_id not in self.captured_requests:
                    self.captured_requests[path_id] = []
                self.captured_requests[path_id].append(template)
                
                print(f"✅ Captured Pendo GET request for {path_id} (sequence {sequence_order})")
                
                # Continue the request
                await route.continue_()
                return True  # Successfully captured a Pendo request
            else:
                print(f"   ⚠️ No jzb parameter found in query params: {list(query_params.keys())}")
                await route.continue_()
                return True  # Still a Pendo request, just no jzb
        
        # Not a Pendo request - continue without capturing
        await route.continue_()
        return False  # Did not capture
    
    def decode_jzb(self, jzb_encoded: str) -> List[Dict[str, Any]]:
        """Decode Pendo's jzb parameter"""
        try:
            # URL decode first
            url_decoded = urllib.parse.unquote(jzb_encoded)
            
            # Base64 decode with URL-safe base64 support
            try:
                # Pendo uses URL-safe base64 encoding
                # Convert URL-safe base64 to standard base64
                url_safe_decoded = url_decoded.replace('-', '+').replace('_', '/')
                
                # Calculate proper padding
                missing_padding = len(url_safe_decoded) % 4
                if missing_padding:
                    url_safe_decoded += '=' * (4 - missing_padding)
                
                base64_decoded = base64.b64decode(url_safe_decoded)
            except Exception as b64_error:
                # Fallback to regular base64
                try:
                    missing_padding = len(url_decoded) % 4
                    if missing_padding:
                        url_decoded += '=' * (4 - missing_padding)
                    
                    base64_decoded = base64.b64decode(url_decoded)
                except Exception as std_b64_error:
                    return []
            
            # Try decompression with multiple approaches
            json_string = None
            
            # Method 1: Try zlib with different wbits values
            import zlib
            for wbits in [-15, 15, -13, 13]:  # Different deflate/zlib formats
                try:
                    zlib_decoded = zlib.decompress(base64_decoded, wbits)
                    json_string = zlib_decoded.decode('utf-8')
                    break
                except Exception as e:
                    continue
            
            # Method 2: Try raw deflate if zlib failed
            if not json_string:
                try:
                    # Skip zlib header and try raw deflate 
                    raw_data = base64_decoded[2:]  # Skip 0x78, 0x9c header
                    deflate_decoded = zlib.decompress(raw_data, -15)  # Raw deflate
                    json_string = deflate_decoded.decode('utf-8')
                except Exception as deflate_error:
                    pass
            
            # Method 3: Try gzip as fallback
            if not json_string:
                try:
                    gzip_decoded = gzip.decompress(base64_decoded)
                    json_string = gzip_decoded.decode('utf-8')
                except Exception as gzip_error:
                    pass
            
            # Method 4: Try as uncompressed data
            if not json_string:
                try:
                    json_string = base64_decoded.decode('utf-8')
                except Exception as utf8_error:
                    return []
            
            # Final check if we got valid JSON string
            if not json_string:
                return []
            
            # Parse JSON
            events = json.loads(json_string)
            parsed_events = events if isinstance(events, list) else [events]
            
            return parsed_events
            
        except Exception as e:
            return []
    
    def save_templates(self, workflow_name: str):
        """Save captured templates to database or file"""
        # For now, save to JSON file
        templates_data = {}
        total_requests = 0
        
        for path_id, templates in self.captured_requests.items():
            templates_data[path_id] = [asdict(t) for t in templates]
            total_requests += len(templates)
            
            print(f"📋 Path '{path_id}': captured {len(templates)} GET requests")
            for i, template in enumerate(templates[:2]):  # Show first 2
                events_count = len(template.decoded_events)
                base_url = template.base_url
                print(f"   Request {i+1}: {base_url} ({events_count} events)")
        
        filename = f"pendo_templates_{workflow_name}.json"
        with open(filename, 'w') as f:
            json.dump(templates_data, f, indent=2)
        
        print(f"💾 Saved {len(self.captured_requests)} paths ({total_requests} total GET requests) to {filename}")
        
        if total_requests == 0:
            print("⚠️ No Pendo GET requests were captured!")
            print("   Make sure:")
            print("   - Your app has Pendo script loaded")
            print("   - Elements have data-pendo-id attributes")
            print("   - Pendo is firing events to data.pendo.io")

class PendoReplay:
    """Replays captured Pendo requests at scale with variations"""
    
    def __init__(self):
        self.session = None
    
    async def __aenter__(self):
        # Create session with SSL verification disabled for demo purposes
        try:
            # First try with SSL disabled
            connector = aiohttp.TCPConnector(ssl=False)
            self.session = aiohttp.ClientSession(connector=connector)
            print("🔒 Created HTTP session with SSL verification disabled (demo mode)")
        except Exception as e:
            print(f"⚠️ SSL config failed, using default: {e}")
            self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def load_templates(self, workflow_name: str) -> Dict[str, List[PendoEventTemplate]]:
        """Load captured templates from file"""
        filename = f"pendo_templates_{workflow_name}.json"
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
            
            templates = {}
            total_events = 0
            
            for path_id, template_list in data.items():
                templates[path_id] = []
                for template_data in template_list:
                    template = PendoEventTemplate(**template_data)
                    templates[path_id].append(template)
                    event_count = len(template.decoded_events)
                    total_events += event_count
                    print(f"📋 Loaded template {path_id} seq {template.sequence_order}: {event_count} events")
            
            print(f"✅ Loaded {len(templates)} paths with {total_events} total events")
            return templates
        except FileNotFoundError:
            print(f"❌ Template file {filename} not found")
            return {}
        except Exception as e:
            print(f"❌ Failed to load templates: {e}")
            import traceback
            traceback.print_exc()
            return {}
    
    def generate_user_session_ids(self) -> Dict[str, str]:
        """Generate realistic session identifiers for one user"""
        return {
            'visitor_id': f"_PENDO_T_{self.random_string(11)}",
            'session_id': self.random_string(16),
            'tab_id': self.random_string(15),
            'frame_id': self.random_string(16),
            'account_id': "demo_account"  # Keep consistent for demo
        }
    
    def random_string(self, length: int) -> str:
        """Generate random string for IDs"""
        chars = string.ascii_letters + string.digits
        return ''.join(random.choice(chars) for _ in range(length))
    
    async def replay_user_journey(
        self, 
        templates: List[PendoEventTemplate], 
        user_base_timestamp: datetime,
        session_ids: Dict[str, str]
    ):
        """Replay a complete user journey with realistic timing"""
        
        current_timestamp = user_base_timestamp
        
        for template in sorted(templates, key=lambda t: t.sequence_order):
            # Add realistic delay from previous event
            current_timestamp += timedelta(milliseconds=template.timing_delay_ms or random.randint(1000, 4000))
            
            # Generate the request
            await self.send_pendo_request(template, current_timestamp, session_ids)
            
            # Small delay to avoid overwhelming the server
            await asyncio.sleep(0.01)  # 10ms between requests
    
    async def send_pendo_request(
        self, 
        template: PendoEventTemplate, 
        timestamp: datetime,
        session_ids: Dict[str, str]
    ):
        """Send a single Pendo request with variations"""
        
        # Create modified events
        modified_events = []
        browser_time = int(timestamp.timestamp() * 1000)
        
        for event in template.decoded_events:
            modified_event = event.copy()
            
            # Update with new session data
            modified_event.update({
                'browser_time': browser_time,
                'visitor_id': session_ids['visitor_id'],
                'session_id': session_ids['session_id'],
                'tab_id': session_ids['tab_id'],
                'frame_id': session_ids['frame_id'],
                'account_id': session_ids['account_id']
            })
            
            modified_events.append(modified_event)
        
        # Encode back to jzb format
        jzb_encoded = self.encode_to_jzb(modified_events)
        
        # Build request URL - preserve original GET format
        query_params = template.query_params.copy()
        query_params['jzb'] = jzb_encoded
        query_params['ct'] = str(browser_time)  # Update client timestamp
        
        url = f"{template.base_url}?{urllib.parse.urlencode(query_params)}"
        
        print(f"🚀 Replaying Pendo GET request:")
        print(f"   → URL: {url[:100]}...")
        print(f"   → Events in payload: {len(modified_events)}")
        print(f"   → User: {session_ids['visitor_id'][:20]}...")
        
        # Send the GET request (matching original Pendo format)
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    print(f"✅ Pendo GET request successful: {template.path_id} at {timestamp.strftime('%H:%M:%S')}")
                else:
                    print(f"⚠️ Pendo GET request failed: HTTP {response.status}")
                    response_text = await response.text()
                    print(f"   Response: {response_text[:200]}")
        except Exception as e:
            print(f"❌ Failed to send Pendo GET request: {e}")
            print(f"   URL was: {url[:150]}...")
    
    def encode_to_jzb(self, events: List[Dict[str, Any]]) -> str:
        """Encode events back to Pendo's jzb format"""
        # Convert to JSON
        json_string = json.dumps(events, separators=(',', ':'))
        
        # Zlib compress (to match Pendo's compression format)
        import zlib
        compressed = zlib.compress(json_string.encode('utf-8'))
        
        # URL-safe Base64 encode (to match Pendo's format)
        base64_encoded = base64.urlsafe_b64encode(compressed).decode('utf-8')
        
        # Remove padding (Pendo doesn't use padding)
        base64_encoded = base64_encoded.rstrip('=')
        
        # URL encode (though it should be URL-safe already)
        return urllib.parse.quote(base64_encoded, safe='')
    
    async def bulk_replay(
        self, 
        workflow_name: str, 
        path_distributions: Dict[str, int],  # {path_id: user_count}
        days_back: int = 6,
        batch_size: int = 50
    ):
        """Generate thousands of realistic user sessions"""
        
        templates = self.load_templates(workflow_name)
        if not templates:
            print(f"❌ No templates found for {workflow_name}")
            return
        
        print(f"🚀 Starting bulk replay for {workflow_name}")
        print(f"   • Total users: {sum(path_distributions.values())}")
        print(f"   • Time range: {days_back} days back from now")
        
        # Generate all user sessions
        all_sessions = []
        now = datetime.now()
        
        for path_id, user_count in path_distributions.items():
            if path_id not in templates:
                print(f"⚠️ No templates for path {path_id}")
                continue
            
            path_templates = templates[path_id]
            total_events_in_path = sum(len(t.decoded_events) for t in path_templates)
            print(f"📋 Path {path_id}: {len(path_templates)} templates, {total_events_in_path} total events")
            
            if total_events_in_path == 0:
                print(f"⚠️ Path {path_id} has no events - skipping {user_count} users")
                continue
            
            for i in range(user_count):
                # Random timestamp within the past N days
                random_seconds_back = random.randint(0, days_back * 24 * 60 * 60)
                user_timestamp = now - timedelta(seconds=random_seconds_back)
                
                session_ids = self.generate_user_session_ids()
                
                all_sessions.append((path_templates, user_timestamp, session_ids, path_id))
        
        # Shuffle sessions for realistic distribution
        random.shuffle(all_sessions)
        
        # Execute sessions in batches to avoid overwhelming
        for i in range(0, len(all_sessions), batch_size):
            batch = all_sessions[i:i + batch_size]
            
            tasks = [
                self.replay_user_journey(templates, timestamp, session_ids)
                for templates, timestamp, session_ids, path_id in batch
            ]
            
            await asyncio.gather(*tasks, return_exceptions=True)
            
            print(f"📊 Completed batch {i//batch_size + 1}/{(len(all_sessions)-1)//batch_size + 1}")
            
            # Brief pause between batches
            await asyncio.sleep(0.5)
        
        print(f"🎉 Bulk replay complete: {len(all_sessions)} user sessions generated!")

# Example usage functions
async def record_workflow_templates(workflow_name: str, app_url: str):
    """Record Pendo request templates for a workflow"""
    from playwright.async_api import async_playwright
    
    capture = PendoCapture()
    
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        
        # Set up request interception
        sequence = 0
        
        async def intercept_with_sequence(route):
            nonlocal sequence
            await capture.intercept_pendo_request(route, "integration_first_path", sequence)
            sequence += 1
        
        await page.route("**/data.pendo.io/**", intercept_with_sequence)
        
        # Execute the workflow steps (you'd replace this with your actual steps)
        await page.goto(app_url)
        await page.click("data-pendo-id='main-tab-integration'")
        await page.click("data-pendo-id='copy-snippet-btn'")
        await page.wait_for_timeout(3000)
        
        await browser.close()
    
    # Save the captured templates
    capture.save_templates(workflow_name)

async def replay_at_scale(workflow_name: str, total_users: int = 3000):
    """Replay captured templates at scale"""
    
    # Define distribution based on your workflow percentages
    path_distributions = {
        "integration_first_path": int(total_users * 0.50),    # 50%
        "dashboard_explorer_path": int(total_users * 0.35),   # 35%
        "drop_off_path": int(total_users * 0.15)              # 15%
    }
    
    async with PendoReplay() as replay:
        await replay.bulk_replay(workflow_name, path_distributions, days_back=6) 