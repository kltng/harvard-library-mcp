# Harvard Library MCP Server - Testing Guide

## 🧪 Overview

The Harvard Library MCP Server uses stdio transport for testing with the MCP Inspector. This is the standard and recommended way to test MCP servers.

---

## 🚀 Testing with stdio Transport

This is the standard way to test MCP servers.

### Command:
```bash
npx @modelcontextprotocol/inspector uv --directory . run harvard-library-mcp
```

### What Happens:
- Inspector starts and connects via stdio
- Browser opens at `http://localhost:6274` with auth token
- All 11 search tools are available
- Real-time search functionality
- Clean, focused interface

### Advantages:
- ✅ Direct MCP protocol connection
- ✅ No additional servers needed
- ✅ Full MCP feature support
- ✅ Recommended for development

---

## 🛠️ Available Search Tools

All 11 tools are available via stdio transport:

1. **search_catalog** - General search across Harvard Library catalog
2. **search_by_title** - Search by title field
3. **search_by_author** - Search by author/creator names
4. **search_by_subject** - Search by subject headings
5. **search_by_collection** - Search within specific collections
6. **search_by_date_range** - Search by publication date range
7. **search_by_geographic_origin** - Search by publication location
8. **advanced_search** - Multi-field search with filters
9. **get_record_details** - Fetch complete record by Harvard ID
10. **get_collections_list** - List available collections
11. **parse_mods_metadata** - Convert MODS XML to structured JSON

---

## 🧪 Sample Test Queries

### Basic Search Examples:
- **General**: Query "Shakespeare" → Find works by Shakespeare
- **Title**: Title "Romeo and Juliet" → Find specific play
- **Author**: Author "William Shakespeare" → Find all works by author
- **Subject**: Subject "computer science" → Find CS related materials
- **Collection**: Collection "English_Crime_and_Execution_Broadsides" → Search specific collection

### Advanced Examples:
- **Date Range**: Start "2020-01-01", End "2023-12-31" → Recent publications
- **Geographic**: Origin "United States" → US-published works
- **Multi-field**: Query "artificial intelligence", Subject "computer science" → Refined search

---

## 📊 Expected Results

### Success Indicators:
- ✅ Search returns Harvard catalog records
- ✅ Records include titles, authors, publication dates
- ✅ MODS XML metadata properly parsed
- ✅ Collections and filtering work correctly
- ✅ No connection errors or timeouts

### Sample Record Format:
```json
{
  "success": true,
  "records": [
    {
      "id": "harvard-123456",
      "title": "Complete Works of William Shakespeare",
      "authors": ["Shakespeare, William"],
      "publication_date": "2020",
      "publisher": "Harvard University Press",
      "language": "eng",
      "subjects": ["English drama", "Literature"],
      "identifiers": {"ISBN": "9780674030588"}
    }
  ],
  "total_count": 1,
  "filters": ["query: Shakespeare"]
}
```

---

## 🔧 Troubleshooting

### Connection Issues:
- **stdio**: Ensure uv is installed and in PATH

### Search Issues:
- **No results**: Try broader search terms
- **API errors**: Harvard API may be rate limiting (wait 1 second)
- **Parse errors**: MODS XML can vary; errors are handled gracefully

### Performance:
- **Rate limiting**: Built-in 10 requests/second limit
- **Large results**: Use `limit` parameter to control response size
- **Timeouts**: Default 30-second timeout for API calls

---

## 🎯 Recommended Workflow

1. **Development**: Use stdio transport for testing
2. **Testing**: Start with simple queries, then try advanced features
3. **Validation**: Verify results include expected metadata

---

## 📚 Additional Resources

- [MCP Inspector Documentation](https://modelcontextprotocol.io/docs/tools/inspector)
- [Harvard Library API](https://api.lib.harvard.edu/v2)
- [MODS XML Schema](http://www.loc.gov/standards/mods/)
- [Project README](./README.md)

---

*Happy searching! 🏛️*