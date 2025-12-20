#!/usr/bin/env python3
"""Test script to check Nexus server health and connectivity."""

import sys
import os

# Add src to path for local testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from nexus_client import RemoteNexusFS, RemoteConnectionError, RemoteTimeoutError
import httpx

def test_health(server_url: str, api_key: str | None = None):
    """Test Nexus server health and connectivity.
    
    Args:
        server_url: Nexus server URL (e.g., "https://nexus-server.multifi.ai")
        api_key: Optional API key for authentication
    """
    print("=" * 60)
    print("Nexus Server Health Check")
    print("=" * 60)
    print(f"Server URL: {server_url}")
    print(f"API Key: {'***' + api_key[-4:] if api_key and len(api_key) > 4 else 'Not provided'}")
    print()
    
    # Test 1: Basic HTTP connectivity
    print("Test 1: Basic HTTP connectivity...")
    try:
        # Try to connect to the server
        response = httpx.get(server_url, timeout=5.0, follow_redirects=True)
        print(f"  ✅ HTTP connection successful")
        print(f"  Status: {response.status_code}")
        print(f"  URL: {response.url}")
    except httpx.ConnectError as e:
        print(f"  ❌ Connection failed: {e}")
        return False
    except httpx.TimeoutException as e:
        print(f"  ❌ Connection timeout: {e}")
        return False
    except Exception as e:
        print(f"  ⚠️  Unexpected error: {e}")
        return False
    
    print()
    
    # Test 2: Create client and check initialization
    print("Test 2: Client initialization...")
    try:
        nx = RemoteNexusFS(server_url, api_key=api_key, timeout=10, connect_timeout=5)
        print(f"  ✅ Client created successfully")
        print(f"  Server URL: {nx.server_url}")
        print(f"  Has API Key: {nx.api_key is not None}")
    except Exception as e:
        print(f"  ❌ Client creation failed: {e}")
        return False
    
    print()
    
    # Test 3: Test RPC connectivity (list root directory)
    print("Test 3: RPC connectivity test (list root directory)...")
    try:
        result = nx.list("/", recursive=False, details=False)
        print(f"  ✅ RPC call successful")
        print(f"  Root directory items: {len(result)} files/directories")
        if result:
            print(f"  Sample items: {result[:5]}")
    except RemoteConnectionError as e:
        print(f"  ❌ Connection error: {e}")
        return False
    except RemoteTimeoutError as e:
        print(f"  ❌ Timeout error: {e}")
        return False
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "API key" in error_msg or "authentication" in error_msg.lower():
            print(f"  ⚠️  Authentication required (this is expected without API key)")
            print(f"  ✅ RPC endpoint is reachable and responding")
            print(f"  Note: Provide --api-key for full functionality")
            # This is actually a success - server is responding correctly
        else:
            print(f"  ⚠️  RPC call failed: {e}")
            print(f"  Error type: {type(e).__name__}")
            return False
    
    print()
    
    # Test 4: Check authentication info (if available)
    print("Test 4: Authentication status...")
    try:
        if nx._agent_id or nx._tenant_id:
            print(f"  ✅ Authentication successful")
            print(f"  Agent ID: {nx._agent_id}")
            print(f"  Tenant ID: {nx._tenant_id}")
        else:
            print(f"  ⚠️  No authentication info (may be anonymous access)")
    except Exception as e:
        print(f"  ⚠️  Could not check auth info: {e}")
    
    print()
    
    # Cleanup
    try:
        nx.close()
        print("Test 5: Client cleanup...")
        print("  ✅ Client closed successfully")
    except Exception as e:
        print(f"  ⚠️  Cleanup warning: {e}")
    
    print()
    print("=" * 60)
    print("✅ Health check completed!")
    print("=" * 60)
    print()
    print("Summary:")
    print("  ✅ Server is reachable")
    print("  ✅ RPC endpoint is responding")
    if not api_key:
        print("  ⚠️  API key required for authenticated operations")
        print("     Set NEXUS_API_KEY env var or use --api-key flag")
    else:
        print("  ✅ Authentication configured")
    return True


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Test Nexus server health")
    parser.add_argument(
        "--server",
        default="https://nexus-server.multifi.ai",
        help="Nexus server URL (default: https://nexus-server.multifi.ai)"
    )
    parser.add_argument(
        "--api-key",
        help="API key for authentication (or set NEXUS_API_KEY env var)"
    )
    
    args = parser.parse_args()
    
    # Get API key from args or environment
    api_key = args.api_key or os.getenv("NEXUS_API_KEY")
    
    success = test_health(args.server, api_key)
    sys.exit(0 if success else 1)

