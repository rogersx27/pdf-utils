# Migration Guide: V1 to V2

## Overview

This guide helps you migrate from API v1 to v2. Both versions remain available, so you can migrate gradually.

## Architecture Comparison

### V1 Architecture (Direct Approach)
```
Request → Endpoint → Service → Response
```

### V2 Architecture (Controller Pattern)
```
Request → Endpoint → Controller → Service → Controller → Response
```

## Key Changes

### 1. URL Structure

Both versions use the same endpoint paths, just with different prefixes:

| Operation | V1 | V2 |
|-----------|----|----|
| List PDFs | `GET /api/v1/pdfs` | `GET /api/v2/pdfs` |
| Get PDF | `GET /api/v1/pdfs/{filename}` | `GET /api/v2/pdfs/{filename}` |
| Export | `POST /api/v1/export/savings/{filename}` | `POST /api/v2/export/savings/{filename}` |

**Migration**: Simply replace `/api/v1/` with `/api/v2/` in your URLs.

### 2. Response Format

Both versions return the same response structure:

```json
{
  "success": true,
  "data": { ... },
  "message": "Operation successful",
  "meta": { ... },
  "request_id": "...",
  "timestamp": "..."
}
```

**Migration**: No changes needed to response handling.

### 3. Query Parameters

V2 maintains backward compatibility with V1 parameters:

```bash
# V1
GET /api/v1/pdfs?tipo=CTA_AHORROS&fecha=202309

# V2 (same parameters)
GET /api/v2/pdfs?tipo=CTA_AHORROS&fecha=202309
```

**Migration**: No changes needed to query parameters.

### 4. Error Handling

V2 provides more detailed error responses:

**V1 Error:**
```json
{
  "success": false,
  "error": {
    "type": "PDFNotFoundError",
    "message": "PDF not found"
  }
}
```

**V2 Error (enhanced):**
```json
{
  "success": false,
  "error": {
    "type": "PDFNotFoundError",
    "message": "PDF file not found: example.pdf",
    "details": {
      "filename": "example.pdf",
      "path": "/data/example.pdf",
      "suggestion": "Check if file exists in data directory"
    }
  },
  "request_id": "abc123"
}
```

**Migration**: Update error handlers to use enhanced error details if desired.

## Feature Comparison

### New in V2

#### 1. Batch Operations

**V2 Only:**
```bash
# Batch export multiple files
POST /api/v2/export/batch/savings
POST /api/v2/export/batch/credit-cards
```

#### 2. File Statistics

**V2 Only:**
```bash
GET /api/v2/files/stats
```

#### 3. Export Templates

**V2 Only:**
```bash
GET /api/v2/export/template/{document_type}
```

#### 4. Data Validation

**V2 Only:**
```bash
POST /api/v2/export/savings/{filename}/validate
POST /api/v2/export/credit-card/{filename}/validate
```

### Maintained Features

All V1 features are available in V2:
- ✅ PDF listing and filtering
- ✅ Text/table extraction
- ✅ Statement extraction
- ✅ File operations (copy/move/rename)
- ✅ Data export (CSV/Excel)
- ✅ Search functionality

## Step-by-Step Migration

### Phase 1: Testing (No Changes)

1. **Verify V2 availability:**
   ```bash
   curl http://localhost:8000/
   ```
   Should show both v1 and v2 in the versions section.

2. **Test V2 endpoints:**
   ```bash
   # Same as V1, just change prefix
   curl http://localhost:8000/api/v2/pdfs
   ```

### Phase 2: Parallel Running

Run both APIs simultaneously:

```python
# Old code (V1) - keep running
v1_client = APIV1Client("http://localhost:8000/api/v1")

# New code (V2) - test in parallel
v2_client = APIV2Client("http://localhost:8000/api/v2")

# Compare results
v1_result = v1_client.list_pdfs()
v2_result = v2_client.list_pdfs()
assert v1_result == v2_result
```

### Phase 3: Gradual Migration

Migrate endpoints one by one:

```python
class PDFClient:
    def __init__(self, base_url: str, use_v2: bool = False):
        version = "v2" if use_v2 else "v1"
        self.base_url = f"{base_url}/api/{version}"
    
    def list_pdfs(self, **filters):
        # Same implementation for both versions
        response = requests.get(f"{self.base_url}/pdfs", params=filters)
        return response.json()

# Enable V2 with a flag
client = PDFClient("http://localhost:8000", use_v2=True)
```

### Phase 4: Feature Adoption

Start using V2-exclusive features:

```python
# Use batch export (V2 only)
client = APIV2Client("http://localhost:8000/api/v2")

result = client.batch_export_savings(
    filenames=["file1.pdf", "file2.pdf"],
    export_format="excel"
)

print(f"Exported {result['meta']['success_count']} files")
```

### Phase 5: Complete Migration

Once confident, switch default to V2:

```python
# Update configuration
API_VERSION = "v2"  # Changed from "v1"
API_BASE_URL = f"http://localhost:8000/api/{API_VERSION}"
```

## Code Examples

### Example 1: Simple Endpoint Migration

**Before (V1):**
```python
import requests

def get_pdfs():
    response = requests.get("http://localhost:8000/api/v1/pdfs")
    return response.json()
```

**After (V2):**
```python
import requests

def get_pdfs():
    response = requests.get("http://localhost:8000/api/v2/pdfs")
    return response.json()
```

**Change:** Only the URL changed.

### Example 2: Using New Batch Features

**Before (V1) - Manual Loop:**
```python
def export_multiple_savings(filenames):
    results = []
    for filename in filenames:
        response = requests.post(
            f"http://localhost:8000/api/v1/export/savings/{filename}",
            params={"export_format": "excel"}
        )
        results.append(response.json())
    return results
```

**After (V2) - Batch Operation:**
```python
def export_multiple_savings(filenames):
    response = requests.post(
        "http://localhost:8000/api/v2/export/batch/savings",
        params={
            "filenames": filenames,
            "export_format": "excel"
        }
    )
    return response.json()
```

**Benefits:**
- Single request instead of multiple
- Better performance
- Transaction-like behavior
- Detailed error reporting per file

### Example 3: Enhanced Error Handling

**Before (V1):**
```python
try:
    response = requests.get(f"http://localhost:8000/api/v1/pdfs/{filename}")
    data = response.json()
    if not data["success"]:
        print(f"Error: {data['error']['message']}")
except Exception as e:
    print(f"Request failed: {e}")
```

**After (V2) - Using Enhanced Details:**
```python
try:
    response = requests.get(f"http://localhost:8000/api/v2/pdfs/{filename}")
    data = response.json()
    if not data["success"]:
        error = data["error"]
        print(f"Error: {error['message']}")
        if "details" in error:
            print(f"Details: {error['details']}")
            if "suggestion" in error["details"]:
                print(f"Suggestion: {error['details']['suggestion']}")
except Exception as e:
    print(f"Request failed: {e}")
```

## Client Library Updates

### Python Client Example

```python
from typing import Optional, List, Literal
from dataclasses import dataclass
import requests

@dataclass
class APIConfig:
    base_url: str = "http://localhost:8000"
    version: Literal["v1", "v2"] = "v2"
    timeout: int = 30
    
    @property
    def api_url(self) -> str:
        return f"{self.base_url}/api/{self.version}"


class PDFAnalyzerClient:
    def __init__(self, config: Optional[APIConfig] = None):
        self.config = config or APIConfig()
    
    def list_pdfs(self, tipo: Optional[str] = None, fecha: Optional[str] = None):
        """List PDFs with optional filters"""
        params = {}
        if tipo:
            params["tipo"] = tipo
        if fecha:
            params["fecha"] = fecha
        
        response = requests.get(
            f"{self.config.api_url}/pdfs",
            params=params,
            timeout=self.config.timeout
        )
        return response.json()
    
    def export_savings(
        self,
        filename: str,
        export_format: Literal["csv", "excel"] = "excel",
        return_file: bool = False
    ):
        """Export savings account statement"""
        response = requests.post(
            f"{self.config.api_url}/export/savings/{filename}",
            params={
                "export_format": export_format,
                "return_file": return_file
            },
            timeout=self.config.timeout
        )
        
        if return_file:
            return response.content  # Binary file data
        return response.json()
    
    def batch_export_savings(
        self,
        filenames: List[str],
        export_format: Literal["csv", "excel"] = "excel"
    ):
        """Batch export multiple savings statements (V2 only)"""
        if self.config.version == "v1":
            raise ValueError("Batch export requires V2 API")
        
        response = requests.post(
            f"{self.config.api_url}/export/batch/savings",
            params={
                "filenames": filenames,
                "export_format": export_format
            },
            timeout=self.config.timeout * 2  # Longer timeout for batch
        )
        return response.json()


# Usage
client = PDFAnalyzerClient(APIConfig(version="v2"))
pdfs = client.list_pdfs(tipo="CTA_AHORROS")
```

## Rollback Plan

If you need to rollback to V1:

### 1. Configuration Rollback
```python
# Change version in config
API_VERSION = "v1"  # Back to v1
```

### 2. Feature Compatibility Check
```python
def is_v2_only_feature(feature: str) -> bool:
    v2_only = [
        "batch_export",
        "validate_data",
        "get_export_template",
        "get_file_stats"
    ]
    return feature in v2_only

def safe_call(feature: str, version: str):
    if is_v2_only_feature(feature) and version == "v1":
        raise ValueError(f"{feature} requires V2 API")
    # Proceed with call
```

## Testing Migration

### Unit Tests
```python
import pytest

@pytest.mark.parametrize("version", ["v1", "v2"])
def test_list_pdfs(version):
    client = PDFAnalyzerClient(APIConfig(version=version))
    result = client.list_pdfs()
    assert result["success"] is True
    assert "data" in result

def test_batch_export_v2_only():
    # Should work with V2
    client_v2 = PDFAnalyzerClient(APIConfig(version="v2"))
    result = client_v2.batch_export_savings(["file1.pdf"])
    assert result["success"] is True
    
    # Should fail with V1
    client_v1 = PDFAnalyzerClient(APIConfig(version="v1"))
    with pytest.raises(ValueError):
        client_v1.batch_export_savings(["file1.pdf"])
```

## Timeline Recommendation

| Week | Action |
|------|--------|
| 1 | Test V2 endpoints in development |
| 2 | Run parallel testing (V1 vs V2) |
| 3 | Migrate read-only operations to V2 |
| 4 | Migrate write operations to V2 |
| 5 | Adopt V2-exclusive features |
| 6+ | Full V2 deployment, monitor V1 usage |

## Support

V1 will remain supported indefinitely for backward compatibility. However, new features will only be added to V2.

### When to Migrate
- ✅ You need batch operations
- ✅ You want enhanced error details
- ✅ You need data validation before export
- ✅ You want better testability
- ⚠️ You can test thoroughly
- ⚠️ You can update client code

### When to Stay on V1
- 🔄 Legacy systems that can't be updated easily
- 🔄 Production systems requiring zero changes
- 🔄 Third-party integrations you don't control

## Questions & Issues

If you encounter migration issues:
1. Check this guide
2. Review the [V2 README](README.md)
3. Compare endpoint documentation in `/docs`
4. Test with both versions in parallel
5. Open an issue with details
