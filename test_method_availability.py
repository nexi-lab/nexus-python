#!/usr/bin/env python3
"""Test which RPC methods are available on the Nexus server."""

import sys
import os

# Add src to path for local testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from nexus_client import RemoteNexusFS

def test_method_availability(server_url: str, api_key: str):
    """Test which RPC methods are available on the server."""
    print("=" * 70)
    print("Nexus Server RPC Method Availability Test")
    print("=" * 70)
    print(f"Server: {server_url}")
    print()
    
    nx = RemoteNexusFS(server_url, api_key=api_key, timeout=10)
    
    # Test file path
    test_file = "/workspace/nexus-client-test/test_read_write.txt"
    
    # Methods to test
    methods_to_test = [
        # File metadata methods
        ("stat", lambda: nx.stat(test_file), "Get file metadata (size, etag, etc.)"),
        ("get_metadata", lambda: nx.get_metadata(test_file), "Get file metadata (permissions, ownership)"),
        ("get_etag", lambda: nx.get_etag(test_file), "Get file ETag (content hash)"),
        
        # Memory methods
        ("memory.list", lambda: nx.memory.list(limit=1), "List memories"),
        ("memory.query", lambda: nx.memory.query(limit=1), "Query memories"),
        ("memory.search", lambda: nx.memory.search("test", limit=1), "Search memories"),
        
        # Direct RPC calls to check method names
        ("list_memories (direct)", lambda: nx._call_rpc("list_memories", {"limit": 1}), "Direct list_memories RPC"),
        ("query_memories (direct)", lambda: nx._call_rpc("query_memories", {"limit": 1}), "Direct query_memories RPC"),
    ]
    
    results = []
    
    for method_name, test_func, description in methods_to_test:
        print(f"Testing: {method_name}")
        print(f"  Description: {description}")
        try:
            result = test_func()
            print(f"  ✅ Available")
            if isinstance(result, dict):
                print(f"     Result keys: {list(result.keys())[:5]}")
            elif isinstance(result, list):
                print(f"     Result type: list with {len(result)} items")
            else:
                print(f"     Result type: {type(result).__name__}")
            results.append((method_name, True, None))
        except Exception as e:
            error_msg = str(e)
            if "Unknown method" in error_msg:
                print(f"  ❌ Not available: Method not found on server")
                results.append((method_name, False, "Method not found"))
            elif "401" in error_msg or "authentication" in error_msg.lower():
                print(f"  ⚠️  Authentication error (may need different permissions)")
                results.append((method_name, False, "Auth error"))
            else:
                print(f"  ⚠️  Error: {error_msg[:100]}")
                results.append((method_name, False, error_msg[:100]))
        print()
    
    # Summary
    print("=" * 70)
    print("Summary")
    print("=" * 70)
    available = [r for r in results if r[1]]
    unavailable = [r for r in results if not r[1]]
    
    print(f"\n✅ Available methods ({len(available)}):")
    for name, _, _ in available:
        print(f"   - {name}")
    
    print(f"\n❌ Unavailable methods ({len(unavailable)}):")
    for name, _, reason in unavailable:
        print(f"   - {name}: {reason}")
    
    print()
    
    # Recommendations
    print("=" * 70)
    print("Recommendations")
    print("=" * 70)
    
    if any("stat" in r[0] and not r[1] for r in results):
        print("\n📝 stat() method not available:")
        print("   Alternative: Use get_metadata() or get_etag() if available")
        print("   Workaround: Read file and check size, or use list() with details=True")
    
    if any("query_memories" in r[0] and not r[1] for r in results):
        print("\n📝 query_memories() method not available:")
        print("   Alternative: Try memory.list() or list_memories() if available")
        print("   Note: Different server versions may use different method names")
    
    nx.close()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Test Nexus server RPC method availability")
    parser.add_argument(
        "--server",
        default="https://nexus-server.multifi.ai",
        help="Nexus server URL"
    )
    parser.add_argument(
        "--api-key",
        help="API key for authentication (or set NEXUS_API_KEY env var)"
    )
    
    args = parser.parse_args()
    
    api_key = args.api_key or os.getenv("NEXUS_API_KEY")
    if not api_key:
        print("Error: API key required")
        sys.exit(1)
    
    test_method_availability(args.server, api_key)

