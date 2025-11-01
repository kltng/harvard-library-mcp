#!/usr/bin/env python3
"""
Test script specifically for MCP Inspector validation.
Tests all tools that will be exposed through MCP.
"""

import asyncio
import json
import sys
sys.path.insert(0, 'src')

from harvard_library_mcp.tools.search_tools import (
    search_catalog,
    search_by_title,
    search_by_author,
    search_by_subject,
    search_by_collection,
    search_by_date_range,
    search_by_geographic_origin,
    advanced_search,
    get_collections_list,
    parse_mods_metadata,
)


async def test_mcp_functionality():
    """Test all MCP functionality for Inspector validation."""
    print("=" * 80)
    print("🏛️  HARVARD LIBRARY MCP SERVER - MCP INSPECTOR VALIDATION")
    print("=" * 80)

    tests = [
        ("search_catalog", "Basic catalog search", {"query": "Shakespeare", "limit": 5}),
        ("search_by_title", "Title search", {"title": "Romeo and Juliet", "limit": 5}),
        ("search_by_author", "Author search", {"author": "Shakespeare", "limit": 5}),
        ("search_by_subject", "Subject search", {"subject": "computer science", "limit": 5}),
        ("search_by_collection", "Collection search", {"collection": "English_Crime_and_Execution_Broadsides", "limit": 5}),
        ("search_by_date_range", "Date range search", {"start_date": "2020-01-01", "end_date": "2023-12-31", "query": "artificial intelligence", "limit": 5}),
        ("search_by_geographic_origin", "Geographic search", {"origin_place": "United States", "limit": 5}),
        ("advanced_search", "Advanced search", {"query": "machine learning", "subject": "computer science", "limit": 5}),
        ("get_collections_list", "Collections list", {}),
        ("parse_mods_metadata", "MODS parsing", {"mods_xml": """<?xml version="1.0" encoding="UTF-8"?>
<mods xmlns="http://www.loc.gov/mods/v3">
    <titleInfo>
        <title>Test Book Title</title>
    </titleInfo>
    <name type="personal">
        <namePart>Test Author</namePart>
        <role>
            <roleTerm type="text">author</roleTerm>
        </role>
    </name>
    <originInfo>
        <dateIssued>2023</dateIssued>
        <publisher>Test Publisher</publisher>
    </originInfo>
    <language>
        <languageTerm type="code" authority="iso639-2b">eng</languageTerm>
    </language>
</mods>"""})
    ]

    passed = 0
    failed = 0

    for i, (func_name, description, params) in enumerate(tests, 1):
        print(f"\n🔍 Test {i}/{len(tests)}: {func_name}")
        print(f"   Description: {description}")
        print(f"   Parameters: {json.dumps(params, indent=6)}")

        try:
            # Get the function
            func = globals()[func_name]

            # Call the function
            result = await func(**params)

            # Check result
            if isinstance(result, dict) and result.get("success", False):
                passed += 1
                print(f"   ✅ PASSED")

                # Show summary of results
                if "records" in result:
                    record_count = len(result.get("records", []))
                    print(f"   📊 Found {record_count} records")
                    if record_count > 0 and result["records"]:
                        sample = result["records"][0]
                        if "title" in sample:
                            print(f"   📚 Sample title: {sample['title'][:80]}...")
                elif "collections" in result:
                    collection_count = len(result.get("collections", []))
                    print(f"   📚 Found {collection_count} collections")
                elif "parsed_metadata" in result:
                    print(f"   📄 MODS metadata parsed successfully")

            else:
                failed += 1
                print(f"   ❌ FAILED")
                print(f"   Error: {result.get('error', 'Unknown error')}")

        except Exception as e:
            failed += 1
            print(f"   ❌ FAILED")
            print(f"   Exception: {e}")

    # Summary
    print("\n" + "=" * 80)
    print("📊 MCP VALIDATION SUMMARY")
    print("=" * 80)
    print(f"Total Tests: {len(tests)}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"Success Rate: {(passed/len(tests))*100:.1f}%")

    if failed == 0:
        print("\n🎉 ALL TESTS PASSED! Your Harvard Library MCP server is ready for use!")
        print("\n🚀 You can now run the MCP Inspector:")
        print("   npx @modelcontextprotocol/inspector uv --directory . run harvard-library-mcp")
    else:
        print(f"\n⚠️  {failed} test(s) failed. Check the errors above.")

    return failed == 0


if __name__ == "__main__":
    asyncio.run(test_mcp_functionality())