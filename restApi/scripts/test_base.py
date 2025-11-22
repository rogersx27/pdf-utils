"""
Quick test script to verify the API base setup

Run this script to check if all components are working correctly.
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_imports():
    """Test that all core components can be imported"""
    print("Testing imports...")
    
    try:
        # Core imports
        from app.core import (
            settings,
            PDFAnalyzerException,
            BadRequestError,
            NotFoundError,
            PDFNotFoundError,
            APIResponse,
            success_response,
            error_response,
            paginated_response,
            ErrorHandlerMiddleware,
            RequestLoggingMiddleware,
            log_endpoint,
            require_password,
            validate_filename_format,
            cache_response,
            get_pdf_password,
            PaginationDep,
            OptionalPasswordDep,
        )
        print("✅ Core imports successful")
        
        # Schema imports
        from app.schemas import (
            BaseSchema,
            SuccessResponse,
            ErrorResponse,
            PaginatedResponse,
            HealthResponse,
            PaginationParams,
        )
        print("✅ Schema imports successful")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False


def test_exceptions():
    """Test exception creation"""
    print("\nTesting exceptions...")
    
    try:
        from app.core import PDFNotFoundError, InvalidFilenameError
        
        # Test creating exceptions
        exc1 = PDFNotFoundError("test.pdf")
        assert exc1.status_code == 404
        assert "test.pdf" in exc1.detail
        
        exc2 = InvalidFilenameError("bad_name.pdf")
        assert exc2.status_code == 400
        
        print("✅ Exceptions work correctly")
        return True
        
    except Exception as e:
        print(f"❌ Exception test failed: {e}")
        return False


def test_responses():
    """Test response creation"""
    print("\nTesting responses...")
    
    try:
        from app.core import success_response, paginated_response, APIResponse
        
        # Test success response
        resp1 = success_response(
            data={"test": "value"},
            message="Test message"
        )
        assert resp1.status_code == 200
        
        # Test paginated response
        resp2 = paginated_response(
            data=[1, 2, 3],
            page=1,
            page_size=10,
            total=3
        )
        assert resp2.status_code == 200
        
        # Test created response
        resp3 = APIResponse.created(
            data={"id": 123},
            message="Created"
        )
        assert resp3.status_code == 201
        
        print("✅ Responses work correctly")
        return True
        
    except Exception as e:
        print(f"❌ Response test failed: {e}")
        return False


def test_schemas():
    """Test schema validation"""
    print("\nTesting schemas...")
    
    try:
        from app.schemas import PaginationParams, BaseSchema
        from pydantic import Field
        
        # Test pagination params
        params = PaginationParams(page=2, page_size=20)
        assert params.offset == 20
        
        # Test custom schema
        class TestSchema(BaseSchema):
            name: str = Field(min_length=1)
            value: int = Field(ge=0)
        
        schema = TestSchema(name="test", value=42)
        assert schema.name == "test"
        assert schema.value == 42
        
        print("✅ Schemas work correctly")
        return True
        
    except Exception as e:
        print(f"❌ Schema test failed: {e}")
        return False


def test_config():
    """Test configuration"""
    print("\nTesting configuration...")
    
    try:
        from app.core import settings
        
        assert settings.api_title
        assert settings.api_version
        assert settings.host
        assert settings.port
        assert settings.data_dir.exists()
        
        print(f"✅ Configuration loaded correctly")
        print(f"   - API Title: {settings.api_title}")
        print(f"   - Version: {settings.api_version}")
        print(f"   - Data Dir: {settings.data_dir}")
        
        return True
        
    except Exception as e:
        print(f"❌ Config test failed: {e}")
        return False


def main():
    """Run all tests"""
    print("=" * 60)
    print("API Base Setup - Quick Test")
    print("=" * 60)
    
    tests = [
        test_imports,
        test_exceptions,
        test_responses,
        test_schemas,
        test_config,
    ]
    
    results = [test() for test in tests]
    
    print("\n" + "=" * 60)
    print(f"Results: {sum(results)}/{len(results)} tests passed")
    print("=" * 60)
    
    if all(results):
        print("\n🎉 All tests passed! Your API base is ready to use.")
        print("\nNext steps:")
        print("1. Run the server: python restApi/main.py")
        print("2. Visit http://localhost:8000/docs")
        print("3. Try the example endpoints at /api/v1/examples")
        return 0
    else:
        print("\n❌ Some tests failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
