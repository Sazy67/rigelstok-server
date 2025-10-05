import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '.'))

# Set up Flask application context
from app import create_app
app = create_app()

with app.app_context():
    from routes.reservation import api_rezervasyon_notu_kaydet
    from utils.database import save_urun_rezervasyon_notu
    from flask import Request
    from werkzeug.datastructures import ImmutableMultiDict
    import json

    def test_reservation_api_endpoint():
        """Test the reservation API endpoint function directly"""
        print("Testing reservation API endpoint function directly...")
        
        # Create a mock request
        class MockRequest:
            def __init__(self, json_data):
                self._json = json_data
            
            def get_json(self):
                return self._json
        
        # Test data
        test_data = {
            "urun_kodu": "TRACE-TEST-001",
            "renk": "Mavi",
            "note": "Trace test notu"
        }
        
        # Mock the request
        original_request = app.view_functions['reservation.api_rezervasyon_notu_kaydet'].__globals__.get('request')
        
        try:
            # Create a mock request object
            mock_request = MockRequest(test_data)
            
            # Temporarily replace the request in the function's globals
            app.view_functions['reservation.api_rezervasyon_notu_kaydet'].__globals__['request'] = mock_request
            
            # Call the API endpoint function directly
            print(f"Calling API endpoint function directly with data: {test_data}")
            result = api_rezervasyon_notu_kaydet()
            
            print(f"API endpoint result: {result}")
            print(f"Result type: {type(result)}")
            
            if hasattr(result, 'json'):
                print(f"Result JSON: {result.json}")
            
            if hasattr(result, 'data'):
                print(f"Result data: {result.data}")
                
            if hasattr(result, 'status_code'):
                print(f"Result status code: {result.status_code}")
            
            return True
            
        except Exception as e:
            print(f"Error calling API endpoint function directly: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            # Restore the original request if it existed
            if original_request:
                app.view_functions['reservation.api_rezervasyon_notu_kaydet'].__globals__['request'] = original_request

    if __name__ == "__main__":
        try:
            success = test_reservation_api_endpoint()
            if success:
                print("\n✅ API endpoint test completed!")
                sys.exit(0)
            else:
                print("\n❌ API endpoint test failed!")
                sys.exit(1)
        except Exception as e:
            print(f"\n❌ API endpoint test failed with exception: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)