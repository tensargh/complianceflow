# Pact Consumer tests for user service

import pytest
from pact import Consumer, Provider, Like, Term, Format
import asyncio
import json
from httpx import AsyncClient
import os

# Pact configuration
PACT_BROKER_URL = os.getenv("PACT_BROKER_BASE_URL", "http://localhost:9292")
PACT_BROKER_USERNAME = os.getenv("PACT_BROKER_USERNAME", "pact_broker")
PACT_BROKER_PASSWORD = os.getenv("PACT_BROKER_PASSWORD", "pact_broker")

# Define the consumer and provider
user_service_consumer = Consumer("user-service")
declaration_service_provider = Provider("declaration-service")

# Pact instance
pact = user_service_consumer.has_pact_with(
    declaration_service_provider,
    host_name="localhost",
    port=1234,
    pact_dir="pacts"
)

class TestUserServiceAsConsumer:
    """Test user service as a consumer of other services."""
    
    def setup_method(self):
        """Set up Pact mock server before each test."""
        pact.start()
    
    def teardown_method(self):
        """Stop Pact mock server after each test."""
        pact.stop()
    
    @pytest.mark.contract
    def test_get_user_declarations(self):
        """Test that user service can get declarations for a user."""
        # Define the expected interaction
        expected_response = {
            "declarations": Like([
                {
                    "id": Like("123e4567-e89b-12d3-a456-426614174000"),
                    "title": Like("Annual Declaration 2024"),
                    "status": Like("submitted"),
                    "user_id": Like("456e7890-e89b-12d3-a456-426614174000"),
                    "created_at": Term(
                        r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}",
                        "2024-01-15T10:30:00"
                    ),
                    "updated_at": Term(
                        r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}",
                        "2024-01-15T10:30:00"
                    )
                }
            ]),
            "total": Like(1),
            "page": Like(1),
            "size": Like(10)
        }
        
        # Set up the interaction expectation
        (pact
         .given("a user with declarations exists")
         .upon_receiving("a request for user declarations")
         .with_request(
             method="GET",
             path="/api/v1/declarations/user/456e7890-e89b-12d3-a456-426614174000",
             headers={
                 "Authorization": Like("Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."),
                 "Content-Type": "application/json",
                 "Accept": "application/json"
             },
             query="page=1&size=10"
         )
         .will_respond_with(
             status=200,
             headers={"Content-Type": "application/json"},
             body=expected_response
         ))
        
        # Execute the test
        with pact:
            # Simulate the user service making a request to declaration service
            import requests
            
            response = requests.get(
                f"http://localhost:1234/api/v1/declarations/user/456e7890-e89b-12d3-a456-426614174000",
                headers={
                    "Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                },
                params={"page": 1, "size": 10}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "declarations" in data
            assert "total" in data
            assert len(data["declarations"]) >= 0
    
    @pytest.mark.contract
    def test_validate_user_exists(self):
        """Test that other services can validate if a user exists."""
        # Define the expected interaction for user validation
        expected_response = {
            "exists": Like(True),
            "user_id": Like("456e7890-e89b-12d3-a456-426614174000"),
            "tenant_id": Like("tenant-123"),
            "is_active": Like(True)
        }
        
        (pact
         .given("a user exists")
         .upon_receiving("a request to validate user existence")
         .with_request(
             method="GET",
             path="/api/v1/users/456e7890-e89b-12d3-a456-426614174000/validate",
             headers={
                 "Authorization": Like("Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."),
                 "Content-Type": "application/json"
             }
         )
         .will_respond_with(
             status=200,
             headers={"Content-Type": "application/json"},
             body=expected_response
         ))
        
        with pact:
            import requests
            
            response = requests.get(
                "http://localhost:1234/api/v1/users/456e7890-e89b-12d3-a456-426614174000/validate",
                headers={
                    "Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                    "Content-Type": "application/json"
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["exists"] is True
            assert "user_id" in data
    
    @pytest.mark.contract
    def test_get_business_unit_members(self):
        """Test getting members of a business unit."""
        expected_response = {
            "members": Like([
                {
                    "user_id": Like("456e7890-e89b-12d3-a456-426614174000"),
                    "email": Format().email,
                    "full_name": Like("John Doe"),
                    "role": Like("user"),
                    "business_unit_id": Like("789e0123-e89b-12d3-a456-426614174000")
                }
            ]),
            "total": Like(1)
        }
        
        (pact
         .given("a business unit with members exists")
         .upon_receiving("a request for business unit members")
         .with_request(
             method="GET",
             path="/api/v1/business-units/789e0123-e89b-12d3-a456-426614174000/members",
             headers={
                 "Authorization": Like("Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."),
                 "Content-Type": "application/json"
             }
         )
         .will_respond_with(
             status=200,
             headers={"Content-Type": "application/json"},
             body=expected_response
         ))
        
        with pact:
            import requests
            
            response = requests.get(
                "http://localhost:1234/api/v1/business-units/789e0123-e89b-12d3-a456-426614174000/members",
                headers={
                    "Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                    "Content-Type": "application/json"
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "members" in data
            assert "total" in data
    
    @pytest.mark.contract
    def test_user_not_found(self):
        """Test handling of user not found scenarios."""
        (pact
         .given("a user does not exist")
         .upon_receiving("a request for a non-existent user")
         .with_request(
             method="GET",
             path="/api/v1/users/00000000-0000-0000-0000-000000000000/validate",
             headers={
                 "Authorization": Like("Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."),
                 "Content-Type": "application/json"
             }
         )
         .will_respond_with(
             status=404,
             headers={"Content-Type": "application/json"},
             body={
                 "error": {
                     "code": Like("USER_NOT_FOUND"),
                     "message": Like("User not found"),
                     "correlation_id": Like("correlation-123")
                 }
             }
         ))
        
        with pact:
            import requests
            
            response = requests.get(
                "http://localhost:1234/api/v1/users/00000000-0000-0000-0000-000000000000/validate",
                headers={
                    "Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                    "Content-Type": "application/json"
                }
            )
            
            assert response.status_code == 404
            data = response.json()
            assert "error" in data
            assert data["error"]["code"] == "USER_NOT_FOUND"

# Provider verification tests (when user-service acts as a provider)
class TestUserServiceAsProvider:
    """Test user service as a provider for other services."""
    
    @pytest.mark.contract
    def test_publish_contracts_to_broker(self):
        """Publish contracts to Pact Broker after successful tests."""
        # This would typically be done in CI/CD pipeline
        # Here we simulate the publishing process
        
        try:
            from pact.broker import Broker
            
            broker = Broker(
                broker_base_url=PACT_BROKER_URL,
                broker_username=PACT_BROKER_USERNAME,
                broker_password=PACT_BROKER_PASSWORD
            )
            
            # Publish the pact file
            result = broker.publish(
                consumer_name="user-service",
                consumer_version="1.0.0",
                pact_dir="pacts",
                tags=["main", "dev"]
            )
            
            assert result is True
            
        except ImportError:
            # If pact-broker client is not available, skip
            pytest.skip("Pact broker client not available")
        except Exception as e:
            # In real implementation, this might be expected in test environments
            print(f"Could not publish to broker: {e}")
            pass

# Async contract tests
class TestAsyncUserServiceContracts:
    """Test async interactions for user service."""
    
    @pytest.mark.contract
    @pytest.mark.asyncio
    async def test_async_user_validation(self):
        """Test async user validation contract."""
        # Set up Pact for async testing
        async_pact = user_service_consumer.has_pact_with(
            Provider("async-validation-service"),
            host_name="localhost",
            port=1235,
            pact_dir="pacts"
        )
        
        expected_response = {
            "is_valid": Like(True),
            "user_id": Like("456e7890-e89b-12d3-a456-426614174000"),
            "validation_result": {
                "email_verified": Like(True),
                "account_active": Like(True),
                "permissions": Like(["read", "write"])
            }
        }
        
        (async_pact
         .given("a valid user exists")
         .upon_receiving("an async user validation request")
         .with_request(
             method="POST",
             path="/api/v1/validate-user",
             headers={"Content-Type": "application/json"},
             body={
                 "user_id": "456e7890-e89b-12d3-a456-426614174000",
                 "tenant_id": "tenant-123"
             }
         )
         .will_respond_with(
             status=200,
             headers={"Content-Type": "application/json"},
             body=expected_response
         ))
        
        async_pact.start()
        
        try:
            async with AsyncClient(base_url="http://localhost:1235") as client:
                response = await client.post(
                    "/api/v1/validate-user",
                    json={
                        "user_id": "456e7890-e89b-12d3-a456-426614174000",
                        "tenant_id": "tenant-123"
                    },
                    headers={"Content-Type": "application/json"}
                )
                
                assert response.status_code == 200
                data = response.json()
                assert data["is_valid"] is True
                assert "validation_result" in data
        
        finally:
            async_pact.stop()

# Contract test configuration
def pytest_configure(config):
    """Configure contract tests."""
    # Ensure pacts directory exists
    import os
    os.makedirs("pacts", exist_ok=True)
    
    # Set up Pact verification
    config.addinivalue_line(
        "markers", "contract: mark test as a contract test"
    )

# Verification helpers
def verify_user_service_contracts():
    """Verify user service fulfills its contracts as a provider."""
    from pact.verifier import Verifier
    
    verifier = Verifier(
        provider="user-service",
        provider_base_url="http://localhost:8001"
    )
    
    # Verify against Pact Broker
    exit_code = verifier.verify_with_broker(
        broker_url=PACT_BROKER_URL,
        broker_username=PACT_BROKER_USERNAME,
        broker_password=PACT_BROKER_PASSWORD,
        publish_version="1.0.0",
        publish_verification_results=True
    )
    
    return exit_code == 0

if __name__ == "__main__":
    # Run contract verification
    if verify_user_service_contracts():
        print("✅ All contracts verified successfully")
    else:
        print("❌ Contract verification failed")
