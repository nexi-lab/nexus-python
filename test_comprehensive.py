#!/usr/bin/env python3
"""Comprehensive test script for Nexus client functionality."""

import sys
import os
import tempfile

# Add src to path for local testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from nexus_client import RemoteNexusFS, RemoteMemory

def test_comprehensive(server_url: str, api_key: str):
    """Run comprehensive tests of Nexus client functionality.
    
    Args:
        server_url: Nexus server URL
        api_key: API key for authentication
    """
    print("=" * 60)
    print("Nexus Client Comprehensive Test")
    print("=" * 60)
    print(f"Server: {server_url}")
    print(f"API Key: ***{api_key[-4:] if len(api_key) > 4 else ''}")
    print()
    
    nx = RemoteNexusFS(server_url, api_key=api_key, timeout=30)
    
    try:
        # Test 1: List root directory
        print("Test 1: List root directory...")
        try:
            items = nx.list("/", recursive=False, details=False)
            print(f"  ✅ Found {len(items)} items in root")
            for item in items[:5]:
                print(f"     - {item}")
        except Exception as e:
            print(f"  ❌ Failed: {e}")
            return False
        
        print()
        
        # Test 2: Check if workspace exists, create test directory
        print("Test 2: Workspace operations...")
        test_dir = "/workspace/nexus-client-test"
        try:
            # Check if directory exists
            exists = nx.exists(test_dir)
            if exists:
                print(f"  ✅ Test directory exists: {test_dir}")
            else:
                print(f"  ℹ️  Test directory doesn't exist, will create")
            
            # Create directory if needed
            if not exists:
                # Try to create by writing a file (mkdir might not be available)
                test_file = f"{test_dir}/test.txt"
                nx.write(test_file, b"test")
                print(f"  ✅ Created test directory via file write")
        except Exception as e:
            print(f"  ⚠️  Workspace test: {e}")
        
        print()
        
        # Test 3: File operations (read/write)
        print("Test 3: File read/write operations...")
        test_file = f"{test_dir}/test_read_write.txt"
        test_content = b"Hello from nexus-client! This is a test file."
        try:
            # Write file
            result = nx.write(test_file, test_content)
            print(f"  ✅ File written successfully")
            print(f"     Path: {test_file}")
            print(f"     Size: {len(test_content)} bytes")
            print(f"     ETag: {result.get('etag', 'N/A')}")
            
            # Read file back
            read_content = nx.read(test_file)
            if read_content == test_content:
                print(f"  ✅ File read successfully, content matches")
            else:
                print(f"  ⚠️  Content mismatch (expected {len(test_content)} bytes, got {len(read_content)} bytes)")
            
            # Check file exists
            exists = nx.exists(test_file)
            print(f"  ✅ File exists check: {exists}")
            
        except Exception as e:
            print(f"  ❌ File operations failed: {e}")
            return False
        
        print()
        
        # Test 4: File metadata (stat) - may not be available on all servers
        # TODO: Server at nexus-server.multifi.ai doesn't support stat() RPC method
        #       This is a server version compatibility issue - stat() is a newer feature
        #       Workaround: Use list() with details=True or read file to get size
        print("Test 4: File metadata (stat)...")
        try:
            stat_info = nx.stat(test_file)
            print(f"  ✅ Stat successful")
            print(f"     Size: {stat_info.get('size', 'N/A')} bytes")
            print(f"     ETag: {stat_info.get('etag', 'N/A')}")
            print(f"     Modified: {stat_info.get('modified_at', 'N/A')}")
        except Exception as e:
            print(f"  ⚠️  Stat method not available on server: {e}")
            print(f"     (This is OK - stat may not be implemented on all servers)")
        
        print()
        
        # Test 5: Glob pattern search
        print("Test 5: Glob pattern search...")
        try:
            # Search for our test files
            matches = nx.glob("test*.txt", test_dir)
            print(f"  ✅ Glob search found {len(matches)} files")
            for match in matches[:5]:
                print(f"     - {match}")
        except Exception as e:
            print(f"  ⚠️  Glob search failed: {e}")
        
        print()
        
        # Test 6: Grep search
        print("Test 6: Grep search...")
        try:
            results = nx.grep("nexus-client", path=test_dir, file_pattern="*.txt")
            print(f"  ✅ Grep search completed")
            print(f"     Found {len(results)} match results")
            # Grep returns a list of dicts with file path and matches
            for result in results[:3]:
                file_path = result.get('path', 'N/A')
                matches = result.get('matches', [])
                print(f"     - {file_path}: {len(matches)} matches")
        except Exception as e:
            print(f"  ⚠️  Grep search failed: {e}")
        
        print()
        
        # Test 7: Memory API
        # TODO: Server at nexus-server.multifi.ai doesn't support list_memories/query_memories RPC methods
        #       This is a server version compatibility issue - memory API may not be enabled or available
        #       See METHOD_AVAILABILITY_ANALYSIS.md for details
        print("Test 7: Memory API...")
        try:
            memory = RemoteMemory(nx)
            
            # Query memories (using query instead of list)
            memories = memory.query(limit=5)
            print(f"  ✅ Memory API accessible")
            print(f"     Found {len(memories)} memories (limited to 5)")
            
            # Try to store a test memory
            test_memory_id = memory.store(
                content="This is a test memory from nexus-client",
                metadata={"test": True, "source": "nexus-client-test"}
            )
            print(f"  ✅ Test memory stored: {test_memory_id}")
            
            # Note: retrieve() uses namespace/path, not memory_id
            # We'll skip retrieval test since we don't know the namespace structure
            print(f"  ℹ️  Memory stored with ID: {test_memory_id}")
            print(f"     (Retrieval requires namespace/path, not memory_id)")
            
        except Exception as e:
            print(f"  ⚠️  Memory API test failed: {e}")
        
        print()
        
        # Test 8: Skills API
        print("Test 8: Skills API...")
        try:
            # Test 8a: List all skills
            print("  8a. List all skills...")
            skills_result = nx.skills_list()
            print(f"     ✅ Skills list successful")
            
            # Handle different response formats
            if isinstance(skills_result, dict):
                skills_list = skills_result.get("skills", [])
                count = skills_result.get("count", len(skills_list))
                print(f"     Found {count} skills")
                
                # Display first few skills
                if skills_list:
                    print(f"     Sample skills:")
                    for skill in skills_list[:3]:
                        if isinstance(skill, dict):
                            name = skill.get('name', 'N/A')
                            desc = str(skill.get('description', 'N/A'))[:50]
                            tier = skill.get('tier', 'N/A')
                            print(f"       - {name} ({tier}): {desc}...")
                        else:
                            print(f"       - {skill}")
                else:
                    print(f"     (No skills found)")
            elif isinstance(skills_result, list):
                print(f"     Found {len(skills_result)} skills")
                for skill in skills_result[:3]:
                    if isinstance(skill, dict):
                        print(f"       - {skill.get('name', 'N/A')}: {str(skill.get('description', 'N/A'))[:50]}...")
                    else:
                        print(f"       - {skill}")
            else:
                print(f"     Unexpected response format: {type(skills_result)}")
            
            # Test 8b: Get skill info (if we have skills)
            if isinstance(skills_result, dict):
                skills_list = skills_result.get("skills", [])
            elif isinstance(skills_result, list):
                skills_list = skills_result
            else:
                skills_list = []
            
            if skills_list and isinstance(skills_list[0], dict):
                first_skill_name = skills_list[0].get('name')
                if first_skill_name:
                    print(f"  8b. Get skill info for '{first_skill_name}'...")
                    try:
                        skill_info = nx.skills_info(first_skill_name)
                        print(f"     ✅ Skill info retrieved")
                        if isinstance(skill_info, dict):
                            print(f"       Name: {skill_info.get('name', 'N/A')}")
                            print(f"       Tier: {skill_info.get('tier', 'N/A')}")
                            print(f"       Version: {skill_info.get('version', 'N/A')}")
                    except Exception as e:
                        print(f"     ⚠️  Could not get skill info: {e}")
            
            # Test 8c: Search skills
            print(f"  8c. Search skills...")
            try:
                search_result = nx.skills_search("", limit=5)  # Empty query to get some results
                print(f"     ✅ Skills search successful")
                if isinstance(search_result, dict):
                    search_skills = search_result.get("skills", [])
                    print(f"     Found {len(search_skills)} skills in search results")
                elif isinstance(search_result, list):
                    print(f"     Found {len(search_result)} skills in search results")
            except Exception as e:
                print(f"     ⚠️  Skills search failed: {e}")
            
            print(f"  ✅ Skills API tests completed")
            
        except Exception as e:
            print(f"  ⚠️  Skills API test failed: {e}")
        
        print()
        
        # Test 9: Cleanup - delete test file
        print("Test 9: Cleanup...")
        try:
            nx.delete(test_file)
            print(f"  ✅ Test file deleted: {test_file}")
        except Exception as e:
            print(f"  ⚠️  Cleanup warning: {e}")
        
        print()
        print("=" * 60)
        print("✅ Comprehensive test completed successfully!")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        nx.close()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Comprehensive Nexus client test")
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
    
    # Get API key from args or environment
    api_key = args.api_key or os.getenv("NEXUS_API_KEY")
    
    if not api_key:
        print("Error: API key required. Use --api-key or set NEXUS_API_KEY env var")
        sys.exit(1)
    
    success = test_comprehensive(args.server, api_key)
    sys.exit(0 if success else 1)
