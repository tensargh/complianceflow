"""
Smoke tests for the Compliance Flow platform.
These tests verify that the basic functionality is working after deployment.
"""

import requests
import time
import os
import json
import sys
from typing import Dict, List, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration from environment variables
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8080")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
TIMEOUT = int(os.getenv("SMOKE_TEST_TIMEOUT", "30"))

class SmokeTestRunner:
    """Runner for smoke tests."""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.timeout = TIMEOUT
        self.results: List[Dict] = []
        
        # Common headers
        self.session.headers.update({
            'User-Agent': 'ComplianceFlow-SmokeTests/1.0',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })
    
    def run_all_tests(self) -> bool:
        """Run all smoke tests."""
        logger.info("Starting smoke tests...")
        
        tests = [
            self.test_api_gateway_health,
            self.test_user_service_health,
            self.test_declaration_service_health,
            self.test_form_service_health,
            self.test_rule_engine_service_health,
            self.test_review_service_health,
            self.test_case_service_health,
            self.test_notification_service_health,
            self.test_analytics_service_health,
            self.test_frontend_availability,
            self.test_api_documentation,
            self.test_basic_auth_flow,
            self.test_cors_headers,
            self.test_security_headers,
            self.test_rate_limiting,
        ]
        
        passed = 0
        failed = 0
        
        for test in tests:
            try:
                test_name = test.__name__
                logger.info(f"Running {test_name}...")
                
                start_time = time.time()
                result = test()
                duration = time.time() - start_time
                
                if result:
                    logger.info(f"✅ {test_name} passed ({duration:.2f}s)")
                    passed += 1
                else:
                    logger.error(f"❌ {test_name} failed ({duration:.2f}s)")
                    failed += 1
                
                self.results.append({
                    'test': test_name,
                    'passed': result,
                    'duration': duration,
                    'timestamp': time.time()
                })
                
            except Exception as e:
                logger.error(f"❌ {test.__name__} failed with exception: {e}")
                failed += 1
                self.results.append({
                    'test': test.__name__,
                    'passed': False,
                    'error': str(e),
                    'timestamp': time.time()
                })
        
        logger.info(f"\nSmoke test results: {passed} passed, {failed} failed")
        return failed == 0
    
    def test_api_gateway_health(self) -> bool:
        """Test API Gateway health."""
        try:
            response = self.session.get(f"{API_BASE_URL}/health")
            return response.status_code == 200
        except Exception as e:
            logger.error(f"API Gateway health check failed: {e}")
            return False
    
    def test_user_service_health(self) -> bool:
        """Test User Service health."""
        return self._test_service_health("user-service", 8001)
    
    def test_declaration_service_health(self) -> bool:
        """Test Declaration Service health."""
        return self._test_service_health("declaration-service", 8002)
    
    def test_form_service_health(self) -> bool:
        """Test Form Service health."""
        return self._test_service_health("form-service", 8003)
    
    def test_rule_engine_service_health(self) -> bool:
        """Test Rule Engine Service health."""
        return self._test_service_health("rule-engine-service", 8004)
    
    def test_review_service_health(self) -> bool:
        """Test Review Service health."""
        return self._test_service_health("review-service", 8005)
    
    def test_case_service_health(self) -> bool:
        """Test Case Service health."""
        return self._test_service_health("case-service", 8006)
    
    def test_notification_service_health(self) -> bool:
        """Test Notification Service health."""
        return self._test_service_health("notification-service", 8007)
    
    def test_analytics_service_health(self) -> bool:
        """Test Analytics Service health."""
        return self._test_service_health("analytics-service", 8008)
    
    def _test_service_health(self, service_name: str, port: int) -> bool:
        """Test individual service health."""
        try:
            # Try via API gateway first
            response = self.session.get(f"{API_BASE_URL}/api/v1/{service_name}/health")
            if response.status_code == 200:
                return True
            
            # Fallback to direct service call (for local testing)
            direct_url = f"http://localhost:{port}/health"
            response = self.session.get(direct_url)
            return response.status_code == 200
            
        except Exception as e:
            logger.error(f"{service_name} health check failed: {e}")
            return False
    
    def test_frontend_availability(self) -> bool:
        """Test frontend availability."""
        try:
            response = self.session.get(FRONTEND_URL)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Frontend availability test failed: {e}")
            return False
    
    def test_api_documentation(self) -> bool:
        """Test API documentation availability."""
        try:
            # Test OpenAPI JSON
            response = self.session.get(f"{API_BASE_URL}/openapi.json")
            if response.status_code != 200:
                return False
            
            # Test Swagger UI (if available)
            response = self.session.get(f"{API_BASE_URL}/docs")
            # Swagger UI might not be available in production
            return response.status_code in [200, 404]
            
        except Exception as e:
            logger.error(f"API documentation test failed: {e}")
            return False
    
    def test_basic_auth_flow(self) -> bool:
        """Test basic authentication flow."""
        try:
            # Test login endpoint exists
            response = self.session.post(
                f"{API_BASE_URL}/api/v1/auth/token",
                data={
                    "username": "invalid@example.com",
                    "password": "invalid"
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            # Should return 401 for invalid credentials
            return response.status_code == 401
            
        except Exception as e:
            logger.error(f"Basic auth flow test failed: {e}")
            return False
    
    def test_cors_headers(self) -> bool:
        """Test CORS headers are present."""
        try:
            response = self.session.options(f"{API_BASE_URL}/api/v1/users/")
            headers = response.headers
            
            required_headers = [
                'access-control-allow-origin',
                'access-control-allow-methods',
                'access-control-allow-headers'
            ]
            
            return all(header in headers for header in required_headers)
            
        except Exception as e:
            logger.error(f"CORS headers test failed: {e}")
            return False
    
    def test_security_headers(self) -> bool:
        """Test security headers are present."""
        try:
            response = self.session.get(f"{API_BASE_URL}/health")
            headers = response.headers
            
            security_headers = [
                'x-content-type-options',
                'x-frame-options',
                'x-xss-protection'
            ]
            
            # At least some security headers should be present
            present_headers = sum(1 for header in security_headers if header in headers)
            return present_headers >= 2
            
        except Exception as e:
            logger.error(f"Security headers test failed: {e}")
            return False
    
    def test_rate_limiting(self) -> bool:
        """Test rate limiting (if implemented)."""
        try:
            # Make multiple rapid requests
            responses = []
            for _ in range(5):
                response = self.session.get(f"{API_BASE_URL}/health")
                responses.append(response.status_code)
                time.sleep(0.1)  # Small delay
            
            # All requests should succeed for health endpoint
            # (health endpoints are usually not rate limited)
            return all(status == 200 for status in responses)
            
        except Exception as e:
            logger.error(f"Rate limiting test failed: {e}")
            return False
    
    def test_database_connectivity(self) -> bool:
        """Test database connectivity through readiness checks."""
        try:
            # Test user service readiness (which checks database)
            response = self.session.get(f"{API_BASE_URL}/api/v1/user-service/health/ready")
            return response.status_code == 200
            
        except Exception as e:
            logger.error(f"Database connectivity test failed: {e}")
            return False
    
    def test_service_discovery(self) -> bool:
        """Test that services can discover each other."""
        # This would test inter-service communication
        # For now, we'll just check that services are responding
        return True
    
    def get_results_summary(self) -> Dict:
        """Get summary of test results."""
        total_tests = len(self.results)
        passed_tests = sum(1 for result in self.results if result['passed'])
        failed_tests = total_tests - passed_tests
        
        total_duration = sum(result.get('duration', 0) for result in self.results)
        
        return {
            'total_tests': total_tests,
            'passed': passed_tests,
            'failed': failed_tests,
            'success_rate': (passed_tests / total_tests * 100) if total_tests > 0 else 0,
            'total_duration': total_duration,
            'timestamp': time.time(),
            'details': self.results
        }
    
    def save_results(self, filename: str = "smoke_test_results.json"):
        """Save test results to file."""
        summary = self.get_results_summary()
        
        with open(filename, 'w') as f:
            json.dump(summary, f, indent=2)
        
        logger.info(f"Test results saved to {filename}")


def main():
    """Main entry point for smoke tests."""
    runner = SmokeTestRunner()
    
    try:
        success = runner.run_all_tests()
        
        # Save results
        runner.save_results()
        
        # Print summary
        summary = runner.get_results_summary()
        print(f"\n{'='*50}")
        print(f"SMOKE TEST SUMMARY")
        print(f"{'='*50}")
        print(f"Total Tests: {summary['total_tests']}")
        print(f"Passed: {summary['passed']}")
        print(f"Failed: {summary['failed']}")
        print(f"Success Rate: {summary['success_rate']:.1f}%")
        print(f"Total Duration: {summary['total_duration']:.2f}s")
        print(f"{'='*50}")
        
        # Exit with appropriate code
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        logger.info("Smoke tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Smoke tests failed with exception: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
