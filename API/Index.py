from flask import Flask, request, jsonify
import requests
import json
from datetime import datetime
import os

app = Flask(__name__)

# Cache dictionary (in-memory cache)
cache = {}

class AadharFamilyAPI:
    def __init__(self):
        self.base_url = "https://aadharfamily.razaisback509.workers.dev"
        
    def get_family_details(self, aadhaar_number):
        """
        Fetch family details using Aadhaar number
        """
        try:
            # Check cache first
            if aadhaar_number in cache:
                cached_data = cache[aadhaar_number]
                # Check if cache is still valid (1 hour cache)
                if (datetime.now() - cached_data['timestamp']).seconds < 3600:
                    return {
                        'success': True,
                        'data': cached_data['data'],
                        'from_cache': True
                    }
            
            # Make API request
            response = requests.get(
                f"{self.base_url}?number={aadhaar_number}",
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Store in cache
                cache[aadhaar_number] = {
                    'data': data,
                    'timestamp': datetime.now()
                }
                
                return {
                    'success': True,
                    'data': data,
                    'from_cache': False
                }
            else:
                return {
                    'success': False,
                    'error': f"API returned status code: {response.status_code}"
                }
                
        except requests.exceptions.Timeout:
            return {
                'success': False,
                'error': "Request timeout. Please try again."
            }
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': f"Network error: {str(e)}"
            }
        except Exception as e:
            return {
                'success': False,
                'error': f"Unexpected error: {str(e)}"
            }

# Initialize API handler
api_handler = AadharFamilyAPI()

@app.route('/', methods=['GET', 'POST'])
def home():
    """Home endpoint with API information"""
    return jsonify({
        'developer': '@Ros3_x',
        'name': 'Aadhar Family Details API',
        'version': '1.0.0',
        'endpoints': {
            '/family': {
                'method': 'GET',
                'params': {
                    'aadhaar': 'Aadhaar number (12 digits)'
                },
                'example': '/family?aadhaar=691871998983'
            },
            '/clear-cache': {
                'method': 'POST',
                'description': 'Clear cache'
            },
            '/health': {
                'method': 'GET',
                'description': 'Check API health'
            }
        }
    })

@app.route('/family', methods=['GET'])
def get_family():
    """
    Get family details by Aadhaar number
    Query params: aadhaar=691871998983
    """
    # Get Aadhaar number from query string
    aadhaar_number = request.args.get('aadhaar')
    
    # Validate Aadhaar number
    if not aadhaar_number:
        return jsonify({
            'success': False,
            'error': 'Aadhaar number is required',
            'usage': '?aadhaar=691871998983'
        }), 400
    
    # Remove spaces and dashes
    aadhaar_number = aadhaar_number.replace(' ', '').replace('-', '')
    
    # Check if it's a valid 12-digit number
    if not aadhaar_number.isdigit() or len(aadhaar_number) != 12:
        return jsonify({
            'success': False,
            'error': 'Invalid Aadhaar number. Must be 12 digits'
        }), 400
    
    # Fetch family details
    result = api_handler.get_family_details(aadhaar_number)
    
    if result['success']:
        response_data = result['data']
        # Add metadata
        response_data['from_cache'] = result.get('from_cache', False)
        response_data['timestamp'] = datetime.now().isoformat()
        return jsonify(response_data)
    else:
        return jsonify({
            'success': False,
            'error': result.get('error', 'Unknown error occurred')
        }), 500

@app.route('/clear-cache', methods=['POST'])
def clear_cache():
    """Clear the cache"""
    cache.clear()
    return jsonify({
        'success': True,
        'message': 'Cache cleared successfully'
    })

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'cache_size': len(cache),
        'timestamp': datetime.now().isoformat()
    })

# For local development
if __name__ == '__main__':
    app.run(debug=True, port=5000)
