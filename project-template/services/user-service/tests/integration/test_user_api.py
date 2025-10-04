# Integration tests for user API endpoints

import pytest
from httpx import AsyncClient
import json

class TestUserAPI:
    """Integration tests for user API endpoints."""
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_create_user_endpoint(self, client: AsyncClient, test_data_factory):
        """Test user creation endpoint."""
        # Arrange
        user_data = test_data_factory.create_user_data()
        del user_data["tenant_id"]  # Remove tenant_id as it's set by the API
        
        # Act
        response = await client.post("/api/v1/users/", json=user_data)
        
        # Assert
        assert response.status_code == 201
        created_user = response.json()
        assert created_user["email"] == user_data["email"]
        assert created_user["full_name"] == user_data["full_name"]
        assert created_user["role"] == user_data["role"]
        assert created_user["is_active"] == user_data["is_active"]
        assert "id" in created_user
        assert "created_at" in created_user
        assert "hashed_password" not in created_user  # Should not expose password

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_create_user_duplicate_email(self, client: AsyncClient, test_user, test_data_factory):
        """Test user creation with duplicate email returns error."""
        # Arrange
        user_data = test_data_factory.create_user_data(email=test_user.email)
        del user_data["tenant_id"]
        
        # Act
        response = await client.post("/api/v1/users/", json=user_data)
        
        # Assert
        assert response.status_code == 400
        error_detail = response.json()
        assert "Email already registered" in error_detail["detail"]

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_create_user_invalid_data(self, client: AsyncClient):
        """Test user creation with invalid data."""
        # Arrange
        invalid_data = {
            "email": "invalid-email",  # Invalid email format
            "full_name": "",  # Empty name
            "password": "123",  # Too short password
            "role": "invalid_role"  # Invalid role
        }
        
        # Act
        response = await client.post("/api/v1/users/", json=invalid_data)
        
        # Assert
        assert response.status_code == 422  # Validation error

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_get_user_by_id(self, client: AsyncClient, test_user, auth_headers):
        """Test get user by ID endpoint."""
        # Act
        response = await client.get(
            f"/api/v1/users/{test_user.id}",
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == 200
        user_data = response.json()
        assert user_data["id"] == str(test_user.id)
        assert user_data["email"] == test_user.email
        assert user_data["full_name"] == test_user.full_name
        assert "hashed_password" not in user_data

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_get_user_by_id_not_found(self, client: AsyncClient, auth_headers):
        """Test get user by ID with non-existent ID."""
        # Arrange
        fake_id = "00000000-0000-0000-0000-000000000000"
        
        # Act
        response = await client.get(
            f"/api/v1/users/{fake_id}",
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == 404

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_get_user_unauthorized(self, client: AsyncClient, test_user):
        """Test get user without authentication."""
        # Act
        response = await client.get(f"/api/v1/users/{test_user.id}")
        
        # Assert
        assert response.status_code == 401

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_update_user(self, client: AsyncClient, test_user, auth_headers):
        """Test user update endpoint."""
        # Arrange
        update_data = {
            "full_name": "Updated Full Name",
            "role": "admin"
        }
        
        # Act
        response = await client.put(
            f"/api/v1/users/{test_user.id}",
            json=update_data,
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == 200
        updated_user = response.json()
        assert updated_user["full_name"] == update_data["full_name"]
        assert updated_user["role"] == update_data["role"]
        assert updated_user["email"] == test_user.email  # Unchanged

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_update_user_not_found(self, client: AsyncClient, auth_headers):
        """Test user update with non-existent ID."""
        # Arrange
        fake_id = "00000000-0000-0000-0000-000000000000"
        update_data = {"full_name": "Updated Name"}
        
        # Act
        response = await client.put(
            f"/api/v1/users/{fake_id}",
            json=update_data,
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == 404

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_delete_user(self, client: AsyncClient, test_session, test_data_factory, admin_auth_headers):
        """Test user deletion endpoint."""
        # Arrange
        from app.services.user_service import UserService
        from app.schemas.user import UserCreate
        
        user_data = test_data_factory.create_user_data(email="delete-test@example.com")
        user_create = UserCreate(**user_data)
        user_service = UserService(test_session)
        user_to_delete = await user_service.create_user(user_create)
        
        # Act
        response = await client.delete(
            f"/api/v1/users/{user_to_delete.id}",
            headers=admin_auth_headers
        )
        
        # Assert
        assert response.status_code == 204
        
        # Verify user is deleted
        get_response = await client.get(
            f"/api/v1/users/{user_to_delete.id}",
            headers=admin_auth_headers
        )
        assert get_response.status_code == 404

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_delete_user_permission_denied(self, client: AsyncClient, test_user, auth_headers):
        """Test user deletion without admin permissions."""
        # Act
        response = await client.delete(
            f"/api/v1/users/{test_user.id}",
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == 403  # Forbidden

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_list_users(self, client: AsyncClient, test_user, test_admin_user, admin_auth_headers):
        """Test list users endpoint."""
        # Act
        response = await client.get(
            "/api/v1/users/",
            headers=admin_auth_headers
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "size" in data
        assert len(data["items"]) >= 2  # At least test_user and test_admin_user
        
        user_emails = [user["email"] for user in data["items"]]
        assert test_user.email in user_emails
        assert test_admin_user.email in user_emails

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_list_users_with_pagination(self, client: AsyncClient, admin_auth_headers):
        """Test list users with pagination parameters."""
        # Act
        response = await client.get(
            "/api/v1/users/?page=1&size=1",
            headers=admin_auth_headers
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1
        assert data["page"] == 1
        assert data["size"] == 1

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_list_users_filter_by_role(self, client: AsyncClient, admin_auth_headers):
        """Test list users filtered by role."""
        # Act
        response = await client.get(
            "/api/v1/users/?role=admin",
            headers=admin_auth_headers
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        for user in data["items"]:
            assert user["role"] == "admin"

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_authenticate_user(self, client: AsyncClient, test_user):
        """Test user authentication endpoint."""
        # Arrange
        login_data = {
            "username": test_user.email,  # OAuth2 standard uses 'username'
            "password": "testpassword123"
        }
        
        # Act
        response = await client.post(
            "/api/v1/auth/token",
            data=login_data,  # Form data for OAuth2
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        # Assert
        assert response.status_code == 200
        token_data = response.json()
        assert "access_token" in token_data
        assert "token_type" in token_data
        assert token_data["token_type"] == "bearer"

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_authenticate_user_invalid_credentials(self, client: AsyncClient, test_user):
        """Test authentication with invalid credentials."""
        # Arrange
        login_data = {
            "username": test_user.email,
            "password": "wrongpassword"
        }
        
        # Act
        response = await client.post(
            "/api/v1/auth/token",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        # Assert
        assert response.status_code == 401

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_get_current_user(self, client: AsyncClient, test_user, auth_headers):
        """Test get current user endpoint."""
        # Act
        response = await client.get(
            "/api/v1/auth/me",
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == 200
        user_data = response.json()
        assert user_data["id"] == str(test_user.id)
        assert user_data["email"] == test_user.email

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_change_password(self, client: AsyncClient, test_user, auth_headers):
        """Test change password endpoint."""
        # Arrange
        password_data = {
            "old_password": "testpassword123",
            "new_password": "newpassword456"
        }
        
        # Act
        response = await client.post(
            f"/api/v1/users/{test_user.id}/change-password",
            json=password_data,
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == 200
        
        # Test login with new password
        login_data = {
            "username": test_user.email,
            "password": "newpassword456"
        }
        
        login_response = await client.post(
            "/api/v1/auth/token",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        assert login_response.status_code == 200

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_change_password_wrong_old_password(self, client: AsyncClient, test_user, auth_headers):
        """Test change password with wrong old password."""
        # Arrange
        password_data = {
            "old_password": "wrongpassword",
            "new_password": "newpassword456"
        }
        
        # Act
        response = await client.post(
            f"/api/v1/users/{test_user.id}/change-password",
            json=password_data,
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == 400

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_health_check(self, client: AsyncClient):
        """Test health check endpoint."""
        # Act
        response = await client.get("/health")
        
        # Assert
        assert response.status_code == 200
        health_data = response.json()
        assert health_data["status"] == "healthy"
        assert "service" in health_data
        assert "timestamp" in health_data

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_api_documentation(self, client: AsyncClient):
        """Test API documentation endpoints."""
        # Test OpenAPI JSON
        response = await client.get("/openapi.json")
        assert response.status_code == 200
        
        # Test Swagger UI
        response = await client.get("/docs")
        assert response.status_code == 200
        
        # Test ReDoc
        response = await client.get("/redoc")
        assert response.status_code == 200

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_cors_headers(self, client: AsyncClient):
        """Test CORS headers are properly set."""
        # Act
        response = await client.options("/api/v1/users/")
        
        # Assert
        assert response.status_code == 200
        assert "access-control-allow-origin" in response.headers
        assert "access-control-allow-methods" in response.headers
        assert "access-control-allow-headers" in response.headers

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_request_id_header(self, client: AsyncClient, auth_headers):
        """Test that request ID is included in response headers."""
        # Act
        response = await client.get("/api/v1/users/", headers=auth_headers)
        
        # Assert
        assert response.status_code == 200
        assert "x-request-id" in response.headers

    @pytest.mark.integration
    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_api_rate_limiting(self, client: AsyncClient):
        """Test API rate limiting (if implemented)."""
        # This test would check rate limiting behavior
        # Implementation depends on your rate limiting strategy
        responses = []
        
        # Make multiple requests rapidly
        for _ in range(10):
            response = await client.get("/health")
            responses.append(response)
        
        # All health checks should succeed (health endpoint usually not rate limited)
        for response in responses:
            assert response.status_code == 200

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_tenant_isolation(self, client: AsyncClient, test_session, test_data_factory):
        """Test that tenant isolation is properly enforced."""
        # Arrange - Create users in different tenants
        from app.services.user_service import UserService
        from app.schemas.user import UserCreate
        
        user_service = UserService(test_session)
        
        # Create user in tenant A
        user_a_data = test_data_factory.create_user_data(
            email="user-a@example.com",
            tenant_id="tenant-a"
        )
        user_create_a = UserCreate(**user_a_data)
        user_a = await user_service.create_user(user_create_a)
        
        # Create user in tenant B
        user_b_data = test_data_factory.create_user_data(
            email="user-b@example.com",
            tenant_id="tenant-b"
        )
        user_create_b = UserCreate(**user_b_data)
        user_b = await user_service.create_user(user_create_b)
        
        # Create tokens for each user
        from app.core.security import create_access_token
        
        token_a = create_access_token(data={
            "sub": user_a.email,
            "user_id": str(user_a.id),
            "tenant_id": user_a.tenant_id,
            "role": user_a.role
        })
        
        headers_a = {"Authorization": f"Bearer {token_a}"}
        
        # Act - User A tries to access User B's data
        response = await client.get(
            f"/api/v1/users/{user_b.id}",
            headers=headers_a
        )
        
        # Assert - Should not be able to access user from different tenant
        assert response.status_code == 404  # Not found (due to tenant filtering)
