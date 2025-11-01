#!/usr/bin/env python3
"""
Comprehensive test suite for Harvard Library MCP Server.
Tests all tools, resources, and edge cases.
"""

import asyncio
import json
import sys
import traceback
from datetime import datetime, timedelta
from typing import Any, Dict, List

sys.path.insert(0, 'src')

from harvard_library_mcp.api.client import HarvardLibraryClient
from harvard_library_mcp.tools.search_tools import (
    search_catalog,
    search_by_title,
    search_by_author,
    search_by_subject,
    search_by_collection,
    search_by_date_range,
    search_by_geographic_origin,
    advanced_search,
    get_record_details,
    get_collections_list,
    parse_mods_metadata,
)


class TestResult:
    """Test result container."""
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.success = False
        self.error = None
        self.result = None
        self.execution_time = 0.0


class HarvardLibraryTester:
    """Comprehensive tester for Harvard Library MCP Server."""

    def __init__(self):
        self.client = None
        self.test_results: List[TestResult] = []
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0

    async def setup(self):
        """Set up test environment."""
        try:
            self.client = HarvardLibraryClient()
            print("✓ Client initialized successfully")
        except Exception as e:
            print(f"✗ Client initialization failed: {e}")
            raise

    async def teardown(self):
        """Clean up test environment."""
        if self.client:
            await self.client.close()

    async def run_test(self, test_name: str, description: str, test_func) -> TestResult:
        """Run a single test and capture results."""
        self.total_tests += 1
        result = TestResult(test_name, description)

        print(f"\n🧪 Testing: {test_name}")
        print(f"   {description}")

        start_time = datetime.now()

        try:
            test_result = await test_func()
            result.result = test_result
            result.success = True
            self.passed_tests += 1
            print(f"✅ PASSED ({(datetime.now() - start_time).total_seconds():.2f}s)")

        except Exception as e:
            result.error = str(e)
            result.success = False
            self.failed_tests += 1
            print(f"❌ FAILED ({(datetime.now() - start_time).total_seconds():.2f}s)")
            print(f"   Error: {e}")

        result.execution_time = (datetime.now() - start_time).total_seconds()
        self.test_results.append(result)
        return result

    # API Client Tests
    async def test_client_initialization(self):
        """Test HarvardLibraryClient initialization."""
        client = HarvardLibraryClient()
        assert client.base_url == "https://api.lib.harvard.edu/v2"
        assert client.timeout == 30
        await client.close()

    async def test_api_connectivity(self):
        """Test basic API connectivity."""
        async with HarvardLibraryClient() as client:
            response = await client._make_request("GET", "items.json", {"q": "test", "limit": 1})
            assert response.status_code == 200
            data = response.json()
            assert "pagination" in data
            assert "items" in data

    # Search Tool Tests
    async def test_search_catalog_basic(self):
        """Test basic catalog search."""
        result = await search_catalog(query="Shakespeare", limit=5)
        assert result["success"] == True
        assert "records" in result
        assert "total_count" in result
        assert result["total_count"] > 0
        if result["records"]:
            record = result["records"][0]
            assert "title" in record or "raw_data" in record

    async def test_search_catalog_empty_query(self):
        """Test catalog search with empty query."""
        result = await search_catalog(query="", limit=5)
        # This might succeed or fail depending on API behavior
        return result

    async def test_search_by_title(self):
        """Test title-specific search."""
        result = await search_by_title(title="Romeo and Juliet", limit=5)
        assert result["success"] == True
        assert "records" in result
        if result["records"]:
            print(f"   Found {len(result['records'])} records with 'Romeo and Juliet' in title")

    async def test_search_by_author(self):
        """Test author-specific search."""
        result = await search_by_author(author="Shakespeare", limit=5)
        assert result["success"] == True
        assert "records" in result
        if result["records"]:
            print(f"   Found {len(result['records'])} records by 'Shakespeare'")

    async def test_search_by_subject(self):
        """Test subject-specific search."""
        result = await search_by_subject(subject="computer science", limit=5)
        assert result["success"] == True
        assert "records" in result
        if result["records"]:
            print(f"   Found {len(result['records'])} records about 'computer science'")

    async def test_search_by_collection(self):
        """Test collection-specific search."""
        result = await search_by_collection(collection="English_Crime_and_Execution_Broadsides", limit=5)
        assert result["success"] == True
        assert "records" in result
        if result["records"]:
            print(f"   Found {len(result['records'])} records in collection")

    async def test_search_by_date_range(self):
        """Test date range search."""
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=365*5)).strftime("%Y-%m-%d")

        result = await search_by_date_range(
            start_date=start_date,
            end_date=end_date,
            query="digital",
            limit=5
        )
        assert result["success"] == True
        assert "records" in result
        print(f"   Found {len(result['records'])} records from {start_date} to {end_date}")

    async def test_search_by_geographic_origin(self):
        """Test geographic origin search."""
        result = await search_by_geographic_origin(origin_place="United States", limit=5)
        assert result["success"] == True
        assert "records" in result
        if result["records"]:
            print(f"   Found {len(result['records'])} records from 'United States'")

    async def test_advanced_search(self):
        """Test advanced multi-field search."""
        result = await advanced_search(
            query="artificial intelligence",
            subject="computer science",
            limit=5,
            start_date="2020-01-01",
            end_date="2023-12-31"
        )
        assert result["success"] == True
        assert "records" in result
        assert "filters" in result
        if result["records"]:
            print(f"   Found {len(result['records'])} records with advanced search")
            print(f"   Filters applied: {result.get('filters', [])}")

    # Record Details Tests
    async def test_get_record_details_valid(self):
        """Test getting record details with valid ID."""
        # First, search for a record to get a valid ID
        search_result = await search_catalog(query="Shakespeare", limit=1)
        if search_result["success"] and search_result["records"]:
            # Try to extract record ID from the first record
            record = search_result["records"][0]
            record_id = record.get("id") or record.get("recordId")

            if record_id:
                details_result = await get_record_details(record_id)
                assert details_result["success"] == True
                assert "record" in details_result
                print(f"   Retrieved details for record ID: {record_id}")
            else:
                print("   ⚠️  No record ID found in search result")
        else:
            print("   ⚠️  Could not find any records to test with")

    async def test_get_record_details_invalid(self):
        """Test getting record details with invalid ID."""
        result = await get_record_details("invalid_id_12345")
        # This should fail gracefully
        assert result["success"] == False
        assert "error" in result
        print(f"   Correctly handled invalid ID: {result['error']}")

    # Collections Tests
    async def test_get_collections_list(self):
        """Test getting collections list."""
        result = await get_collections_list()
        assert result["success"] == True
        assert "collections" in result
        assert isinstance(result["collections"], list)
        print(f"   Found {len(result['collections'])} collections")

    # MODS Parsing Tests
    async def test_parse_mods_metadata(self):
        """Test MODS XML parsing."""
        sample_mods_xml = """<?xml version="1.0" encoding="UTF-8"?>
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
        </mods>"""

        result = await parse_mods_metadata(sample_mods_xml)
        assert result["success"] == True
        assert "parsed_metadata" in result
        assert result["parsed_metadata"]["title"] == "Test Book Title"
        print("   ✓ MODS XML parsing successful")

    async def test_parse_mods_metadata_invalid(self):
        """Test MODS XML parsing with invalid XML."""
        invalid_xml = "<invalid>not <proper> xml</invalid>"
        result = await parse_mods_metadata(invalid_xml)
        # Should handle gracefully
        print(f"   Handled invalid XML: {result.get('success', False)}")

    # Edge Case Tests
    async def test_search_with_special_characters(self):
        """Test search with special characters."""
        special_queries = ["test&query", "test+query", "test%20query", "café", "naïve"]
        for query in special_queries:
            result = await search_catalog(query=query, limit=3)
            assert result["success"] == True
            print(f"   ✓ Special characters handled: '{query}'")

    async def test_search_pagination(self):
        """Test search pagination."""
        # First page
        result1 = await search_catalog(query="science", limit=5, offset=0)
        assert result1["success"] == True

        # Second page
        result2 = await search_catalog(query="science", limit=5, offset=5)
        assert result2["success"] == True

        if result1["records"] and result2["records"]:
            # Ensure we get different records
            assert result1["records"][0]["id"] != result2["records"][0]["id"]
            print("   ✓ Pagination working correctly")

    async def test_search_response_formats(self):
        """Test different response formats."""
        for format_type in ["json", "xml"]:
            result = await search_catalog(query="test", limit=3, response_format=format_type)
            assert result["success"] == True
            print(f"   ✓ {format_type.upper()} format working")

    async def test_search_limits(self):
        """Test search result limits."""
        for limit in [1, 10, 50, 100]:
            result = await search_catalog(query="test", limit=limit)
            assert result["success"] == True
            assert len(result["records"]) <= limit
            print(f"   ✓ Limit {limit} working")

    async def test_search_large_query(self):
        """Test search with large query."""
        large_query = "a" * 1000  # 1000 character query
        result = await search_catalog(query=large_query, limit=3)
        # Should handle gracefully
        print(f"   Large query handled: {result['success']}")

    async def test_rate_limiting(self):
        """Test rate limiting behavior."""
        # Make multiple quick requests
        results = []
        for i in range(5):
            result = await search_catalog(query=f"test{i}", limit=2)
            results.append(result)
            await asyncio.sleep(0.1)  # Small delay

        success_count = sum(1 for r in results if r["success"])
        print(f"   ✓ Rate limiting: {success_count}/5 requests successful")

    # Resource Tests
    async def test_api_info_resource(self):
        """Test API info resource."""
        # This would be tested through MCP server resources
        # For now, just test the underlying functionality
        client = HarvardLibraryClient()
        assert client.base_url == "https://api.lib.harvard.edu/v2"
        assert client.timeout == 30
        await client.close()

    async def run_all_tests(self):
        """Run all tests."""
        print("=" * 80)
        print("🏛️  HARVARD LIBRARY MCP SERVER - COMPREHENSIVE TEST SUITE")
        print("=" * 80)

        await self.setup()

        tests = [
            # API Client Tests
            ("Client Initialization", "Test HarvardLibraryClient setup", self.test_client_initialization),
            ("API Connectivity", "Test basic API connectivity", self.test_api_connectivity),

            # Search Tool Tests
            ("Catalog Search Basic", "Test basic catalog search", self.test_search_catalog_basic),
            ("Catalog Search Empty", "Test catalog search with empty query", self.test_search_catalog_empty_query),
            ("Search by Title", "Test title-specific search", self.test_search_by_title),
            ("Search by Author", "Test author-specific search", self.test_search_by_author),
            ("Search by Subject", "Test subject-specific search", self.test_search_by_subject),
            ("Search by Collection", "Test collection-specific search", self.test_search_by_collection),
            ("Search by Date Range", "Test date range search", self.test_search_by_date_range),
            ("Search by Geographic Origin", "Test geographic origin search", self.test_search_by_geographic_origin),
            ("Advanced Search", "Test advanced multi-field search", self.test_advanced_search),

            # Record Details Tests
            ("Record Details Valid", "Test getting record details with valid ID", self.test_get_record_details_valid),
            ("Record Details Invalid", "Test getting record details with invalid ID", self.test_get_record_details_invalid),

            # Collections Tests
            ("Collections List", "Test getting collections list", self.test_get_collections_list),

            # MODS Parsing Tests
            ("MODS Parsing", "Test MODS XML parsing", self.test_parse_mods_metadata),
            ("MODS Parsing Invalid", "Test MODS XML parsing with invalid XML", self.test_parse_mods_metadata_invalid),

            # Edge Case Tests
            ("Special Characters", "Test search with special characters", self.test_search_with_special_characters),
            ("Pagination", "Test search pagination", self.test_search_pagination),
            ("Response Formats", "Test different response formats", self.test_search_response_formats),
            ("Search Limits", "Test search result limits", self.test_search_limits),
            ("Large Query", "Test search with large query", self.test_search_large_query),
            ("Rate Limiting", "Test rate limiting behavior", self.test_rate_limiting),

            # Resource Tests
            ("API Info Resource", "Test API info resource", self.test_api_info_resource),
        ]

        for test_name, description, test_func in tests:
            await self.run_test(test_name, description, test_func)

        await self.teardown()
        self.print_summary()

    def print_summary(self):
        """Print test summary."""
        print("\n" + "=" * 80)
        print("📊 TEST SUMMARY")
        print("=" * 80)
        print(f"Total Tests: {self.total_tests}")
        print(f"✅ Passed: {self.passed_tests}")
        print(f"❌ Failed: {self.failed_tests}")
        print(f"Success Rate: {(self.passed_tests/self.total_tests)*100:.1f}%")

        if self.failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result.success:
                    print(f"   - {result.name}: {result.error}")

        # Performance summary
        if self.test_results:
            avg_time = sum(r.execution_time for r in self.test_results) / len(self.test_results)
            print(f"\n⏱️  Average execution time: {avg_time:.2f}s")

            slowest = max(self.test_results, key=lambda r: r.execution_time)
            print(f"    Slowest test: {slowest.name} ({slowest.execution_time:.2f}s)")

        print("\n" + "=" * 80)


async def main():
    """Main test runner."""
    tester = HarvardLibraryTester()

    try:
        await tester.run_all_tests()
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
    except Exception as e:
        print(f"\n\n💥 Test suite crashed: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())