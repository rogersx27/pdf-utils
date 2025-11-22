# API v2 - Controller-Based Architecture

## Overview

API v2 introduces a **controller-based architecture** inspired by MVC patterns, providing better separation of concerns, improved testability, and enhanced code reusability.

## Key Improvements over V1

### 1. **Controller Pattern**
- Business logic separated into dedicated controller classes
- Endpoints act as thin wrappers that delegate to controllers
- Controllers handle HTTP response formatting
- Services focus purely on business operations

### 2. **Reusable Concerns (Mixins)**
- `PasswordAwareMixin`: Shared password handling
- `BatchOperationMixin`: Batch operation utilities
- Easy to compose behaviors into controllers

### 3. **Enhanced Error Handling**
- Consistent error responses across all endpoints
- Controller-level error decorators
- Better error context and logging

### 4. **Improved Organization**
```
app/
├── api/v2/
│   ├── endpoints/        # Thin endpoint definitions
│   │   ├── pdfs.py      # PDF operations
│   │   ├── files.py     # File management
│   │   └── exports.py   # Data export
│   └── router.py        # Main v2 router
├── controllers/         # Business logic handlers
│   ├── pdf_controller.py
│   ├── file_controller.py
│   ├── export_controller.py
│   └── concerns/        # Reusable mixins
└── services/           # Core business logic
```

## Endpoints

### PDF Operations (`/api/v2/pdfs`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | List all PDFs with filters |
| GET | `/{filename}` | Get PDF information |
| GET | `/{filename}/text` | Extract text content |
| GET | `/{filename}/tables` | Extract table structures |
| GET | `/{filename}/search` | Search text in PDF |
| GET | `/{filename}/extract/savings` | Extract savings statement |
| GET | `/{filename}/extract/credit-card` | Extract credit card statement |
| GET | `/{filename}/metadata` | Get PDF metadata |

### File Management (`/api/v2/files`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/copy` | Copy a PDF file |
| POST | `/move` | Move a PDF file |
| POST | `/rename` | Rename a PDF file |
| DELETE | `/{filename}` | Delete a PDF file |
| POST | `/organize` | Organize PDFs by criteria |
| POST | `/registry/create` | Create file inventory |
| GET | `/stats` | Get file statistics |

### Data Export (`/api/v2/export`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/savings/{filename}` | Export savings account data |
| POST | `/savings/{filename}/validate` | Validate savings data |
| POST | `/credit-card/{filename}` | Export credit card data |
| POST | `/credit-card/{filename}/validate` | Validate credit card data |
| POST | `/batch/savings` | Batch export savings accounts |
| POST | `/batch/credit-cards` | Batch export credit cards |
| GET | `/formats` | Get available export formats |
| GET | `/template/{document_type}` | Download export template |

## Usage Examples

### Extract and Export Savings Account

```bash
# 1. Extract savings statement
curl -X GET "http://localhost:8000/api/v2/pdfs/Extracto_455000853_202309_CTA_AHORROS_4332.pdf/extract/savings"

# 2. Validate data
curl -X POST "http://localhost:8000/api/v2/export/savings/Extracto_455000853_202309_CTA_AHORROS_4332.pdf/validate"

# 3. Export to Excel
curl -X POST "http://localhost:8000/api/v2/export/savings/Extracto_455000853_202309_CTA_AHORROS_4332.pdf?export_format=excel"

# 4. Download file directly
curl -X POST "http://localhost:8000/api/v2/export/savings/Extracto_455000853_202309_CTA_AHORROS_4332.pdf?export_format=excel&return_file=true" -O
```

### Batch Export Multiple Files

```bash
# Export multiple savings accounts
curl -X POST "http://localhost:8000/api/v2/export/batch/savings" \
  -H "Content-Type: application/json" \
  -d '{
    "filenames": [
      "Extracto_455000853_202309_CTA_AHORROS_4332.pdf",
      "Extracto_508915065_202312_CTA_AHORROS_4332.pdf"
    ],
    "export_format": "excel"
  }'
```

### File Organization

```bash
# Preview organization (dry run)
curl -X POST "http://localhost:8000/api/v2/files/organize?by_type=true&by_year=true&dry_run=true"

# Apply organization
curl -X POST "http://localhost:8000/api/v2/files/organize?by_type=true&by_year=true"
```

### Search Across PDFs

```bash
# Search in specific PDF
curl -X GET "http://localhost:8000/api/v2/pdfs/Extracto_455000853_202309_CTA_AHORROS_4332.pdf/search?query=TRANSFERENCIA"
```

## Architecture Benefits

### **Testability**
Controllers can be tested independently of FastAPI endpoints:
```python
def test_pdf_controller():
    controller = PDFController()
    response = await controller.list_pdfs()
    assert response.status_code == 200
```

### **Reusability**
Controllers can be used outside of HTTP context:
```python
# Use in CLI, scripts, or other contexts
controller = PDFController(password="secret")
pdfs = controller.service.list_pdfs()
```

### **Maintainability**
- Clear separation of concerns
- Easy to add new features through mixins
- Consistent patterns across all endpoints

### **Extensibility**
Add new concerns easily:
```python
class AuditableMixin:
    """Track all operations for audit"""
    def _log_operation(self, operation: str, details: dict):
        # Log to audit trail
        pass

class PDFController(BaseController, PasswordAwareMixin, AuditableMixin):
    # Now has password handling AND auditing
    pass
```

## Migration from V1

Both V1 and V2 APIs are available simultaneously. V1 remains stable for backward compatibility while V2 provides the enhanced architecture.

### Key Differences

| Aspect | V1 | V2 |
|--------|----|----|
| Architecture | Direct endpoint logic | Controller pattern |
| Code organization | Endpoints contain logic | Logic in controllers/services |
| Error handling | Endpoint-level | Controller-level with decorators |
| Reusability | Limited | High (controllers + mixins) |
| Batch operations | Limited | Full support |
| Testability | Requires HTTP mocking | Can test controllers directly |

### Recommended Migration Path

1. **Start using V2 for new features**
2. **Test V2 endpoints thoroughly**
3. **Gradually migrate V1 integrations** when convenient
4. **V1 will remain available** for legacy support

## Configuration

V2 uses the same configuration as V1:
- Environment variables from `.env`
- Same data directories
- Same password handling
- Compatible with existing deployments

## Error Responses

V2 provides consistent error responses:

```json
{
  "success": false,
  "error": {
    "type": "PDFNotFoundError",
    "message": "PDF file not found: example.pdf",
    "details": {
      "filename": "example.pdf",
      "path": "/data/example.pdf"
    }
  },
  "request_id": "abc123",
  "timestamp": "2025-11-22T10:30:00Z"
}
```

## Performance

V2 includes:
- Response caching for repeated requests
- Batch operations for processing multiple files
- Optimized file operations
- Reduced overhead through controller reuse

## Future Enhancements

Planned features for V2:
- [ ] Async batch processing with progress tracking
- [ ] WebSocket support for long-running operations
- [ ] Enhanced caching strategies
- [ ] Rate limiting per operation type
- [ ] Advanced filtering and search capabilities
- [ ] GraphQL endpoint support
- [ ] Export to additional formats (Parquet, JSON, XML)

## Support

For issues or questions:
- Check the [API documentation](http://localhost:8000/docs)
- Review the [main README](../../../README.md)
- See controller implementations in `app/controllers/`
- Check service documentation in `app/services/`
