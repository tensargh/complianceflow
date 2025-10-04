# Unit tests for user service business logic

import pytest
from unittest.mock import AsyncMock, patch
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from app.services.user_service import UserService
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import verify_password, get_password_hash


class TestUserService:
    """Test cases for UserService."""
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_create_user_success(self, test_session, test_data_factory):
        """Test successful user creation."""
        # Arrange
        user_data = test_data_factory.create_user_data()
        user_create = UserCreate(**user_data)
        user_service = UserService(test_session)
        
        # Act
        created_user = await user_service.create_user(user_create)
        
        # Assert
        assert created_user.email == user_data["email"]
        assert created_user.full_name == user_data["full_name"]
        assert created_user.role == user_data["role"]
        assert created_user.is_active == user_data["is_active"]
        assert created_user.tenant_id == user_data["tenant_id"]
        assert verify_password(user_data["password"], created_user.hashed_password)
        assert created_user.id is not None
        assert created_user.created_at is not None

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_create_user_duplicate_email(self, test_session, test_user, test_data_factory):
        """Test user creation with duplicate email fails."""
        # Arrange
        user_data = test_data_factory.create_user_data(email=test_user.email)
        user_create = UserCreate(**user_data)
        user_service = UserService(test_session)
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await user_service.create_user(user_create)
        
        assert exc_info.value.status_code == 400
        assert "Email already registered" in str(exc_info.value.detail)

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_user_by_id_success(self, test_session, test_user):
        """Test successful user retrieval by ID."""
        # Arrange
        user_service = UserService(test_session)
        
        # Act
        retrieved_user = await user_service.get_user_by_id(
            test_user.id, test_user.tenant_id
        )
        
        # Assert
        assert retrieved_user is not None
        assert retrieved_user.id == test_user.id
        assert retrieved_user.email == test_user.email
        assert retrieved_user.tenant_id == test_user.tenant_id

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_user_by_id_not_found(self, test_session):
        """Test user retrieval with non-existent ID."""
        # Arrange
        user_service = UserService(test_session)
        fake_id = "00000000-0000-0000-0000-000000000000"
        tenant_id = "test-tenant-123"
        
        # Act
        result = await user_service.get_user_by_id(fake_id, tenant_id)
        
        # Assert
        assert result is None

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_user_by_id_wrong_tenant(self, test_session, test_user):
        """Test user retrieval with wrong tenant ID."""
        # Arrange
        user_service = UserService(test_session)
        wrong_tenant_id = "wrong-tenant-456"
        
        # Act
        result = await user_service.get_user_by_id(
            test_user.id, wrong_tenant_id
        )
        
        # Assert
        assert result is None

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_user_by_email_success(self, test_session, test_user):
        """Test successful user retrieval by email."""
        # Arrange
        user_service = UserService(test_session)
        
        # Act
        retrieved_user = await user_service.get_user_by_email(
            test_user.email, test_user.tenant_id
        )
        
        # Assert
        assert retrieved_user is not None
        assert retrieved_user.email == test_user.email
        assert retrieved_user.tenant_id == test_user.tenant_id

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_update_user_success(self, test_session, test_user):
        """Test successful user update."""
        # Arrange
        user_service = UserService(test_session)
        update_data = UserUpdate(
            full_name="Updated Name",
            role="admin"
        )
        
        # Act
        updated_user = await user_service.update_user(
            test_user.id, update_data, test_user.tenant_id
        )
        
        # Assert
        assert updated_user is not None
        assert updated_user.full_name == "Updated Name"
        assert updated_user.role == "admin"
        assert updated_user.email == test_user.email  # Unchanged
        assert updated_user.updated_at > test_user.created_at

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_update_user_not_found(self, test_session):
        """Test user update with non-existent ID."""
        # Arrange
        user_service = UserService(test_session)
        fake_id = "00000000-0000-0000-0000-000000000000"
        tenant_id = "test-tenant-123"
        update_data = UserUpdate(full_name="Updated Name")
        
        # Act
        result = await user_service.update_user(fake_id, update_data, tenant_id)
        
        # Assert
        assert result is None

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_delete_user_success(self, test_session, test_user):
        """Test successful user deletion (soft delete)."""
        # Arrange
        user_service = UserService(test_session)
        
        # Act
        result = await user_service.delete_user(
            test_user.id, test_user.tenant_id
        )
        
        # Assert
        assert result is True
        
        # Verify user is soft deleted
        deleted_user = await user_service.get_user_by_id(
            test_user.id, test_user.tenant_id
        )
        assert deleted_user is None

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_delete_user_not_found(self, test_session):
        """Test user deletion with non-existent ID."""
        # Arrange
        user_service = UserService(test_session)
        fake_id = "00000000-0000-0000-0000-000000000000"
        tenant_id = "test-tenant-123"
        
        # Act
        result = await user_service.delete_user(fake_id, tenant_id)
        
        # Assert
        assert result is False

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_authenticate_user_success(self, test_session, test_user):
        """Test successful user authentication."""
        # Arrange
        user_service = UserService(test_session)
        password = "testpassword123"
        
        # Act
        authenticated_user = await user_service.authenticate_user(
            test_user.email, password, test_user.tenant_id
        )
        
        # Assert
        assert authenticated_user is not None
        assert authenticated_user.email == test_user.email
        assert authenticated_user.id == test_user.id

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_authenticate_user_wrong_password(self, test_session, test_user):
        """Test user authentication with wrong password."""
        # Arrange
        user_service = UserService(test_session)
        wrong_password = "wrongpassword"
        
        # Act
        result = await user_service.authenticate_user(
            test_user.email, wrong_password, test_user.tenant_id
        )
        
        # Assert
        assert result is None

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_authenticate_user_not_found(self, test_session):
        """Test user authentication with non-existent email."""
        # Arrange
        user_service = UserService(test_session)
        email = "nonexistent@example.com"
        password = "password123"
        tenant_id = "test-tenant-123"
        
        # Act
        result = await user_service.authenticate_user(email, password, tenant_id)
        
        # Assert
        assert result is None

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_authenticate_inactive_user(self, test_session, test_data_factory):
        """Test authentication of inactive user fails."""
        # Arrange
        user_data = test_data_factory.create_user_data(is_active=False)
        user_create = UserCreate(**user_data)
        user_service = UserService(test_session)
        
        # Create inactive user
        inactive_user = await user_service.create_user(user_create)
        
        # Act
        result = await user_service.authenticate_user(
            inactive_user.email, user_data["password"], user_data["tenant_id"]
        )
        
        # Assert
        assert result is None

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_list_users_success(self, test_session, test_user, test_admin_user):
        """Test successful user listing."""
        # Arrange
        user_service = UserService(test_session)
        
        # Act
        users, total = await user_service.list_users(
            tenant_id=test_user.tenant_id,
            skip=0,
            limit=10
        )
        
        # Assert
        assert len(users) == 2  # test_user and test_admin_user
        assert total == 2
        user_emails = [user.email for user in users]
        assert test_user.email in user_emails
        assert test_admin_user.email in user_emails

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_list_users_with_pagination(self, test_session, test_user, test_admin_user):
        """Test user listing with pagination."""
        # Arrange
        user_service = UserService(test_session)
        
        # Act
        users, total = await user_service.list_users(
            tenant_id=test_user.tenant_id,
            skip=1,
            limit=1
        )
        
        # Assert
        assert len(users) == 1
        assert total == 2

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_list_users_filter_by_role(self, test_session, test_user, test_admin_user):
        """Test user listing filtered by role."""
        # Arrange
        user_service = UserService(test_session)
        
        # Act
        users, total = await user_service.list_users(
            tenant_id=test_user.tenant_id,
            role="admin",
            skip=0,
            limit=10
        )
        
        # Assert
        assert len(users) == 1
        assert total == 1
        assert users[0].role == "admin"
        assert users[0].email == test_admin_user.email

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_change_password_success(self, test_session, test_user):
        """Test successful password change."""
        # Arrange
        user_service = UserService(test_session)
        old_password = "testpassword123"
        new_password = "newpassword456"
        
        # Act
        result = await user_service.change_password(
            test_user.id,
            old_password,
            new_password,
            test_user.tenant_id
        )
        
        # Assert
        assert result is True
        
        # Verify new password works
        authenticated_user = await user_service.authenticate_user(
            test_user.email, new_password, test_user.tenant_id
        )
        assert authenticated_user is not None

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_change_password_wrong_old_password(self, test_session, test_user):
        """Test password change with wrong old password."""
        # Arrange
        user_service = UserService(test_session)
        wrong_old_password = "wrongpassword"
        new_password = "newpassword456"
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await user_service.change_password(
                test_user.id,
                wrong_old_password,
                new_password,
                test_user.tenant_id
            )
        
        assert exc_info.value.status_code == 400
        assert "Incorrect password" in str(exc_info.value.detail)

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_user_service_with_kafka_event(self, test_session, test_data_factory, mock_kafka_producer):
        """Test that user creation publishes Kafka event."""
        # Arrange
        user_data = test_data_factory.create_user_data()
        user_create = UserCreate(**user_data)
        
        with patch('app.services.user_service.publish_user_event') as mock_publish:
            user_service = UserService(test_session)
            
            # Act
            created_user = await user_service.create_user(user_create)
            
            # Assert
            assert created_user is not None
            mock_publish.assert_called_once()
            call_args = mock_publish.call_args[0]
            assert call_args[0] == "user.user.created"
            assert call_args[1]["user_id"] == str(created_user.id)

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_user_service_with_cache(self, test_session, test_user, mock_redis):
        """Test that user service uses Redis cache."""
        # Arrange
        user_service = UserService(test_session)
        cache_key = f"user:{test_user.id}:{test_user.tenant_id}"
        
        with patch('app.services.user_service.cache_get') as mock_cache_get, \
             patch('app.services.user_service.cache_set') as mock_cache_set:
            
            # Configure mocks
            mock_cache_get.return_value = None  # Cache miss
            
            # Act
            retrieved_user = await user_service.get_user_by_id(
                test_user.id, test_user.tenant_id
            )
            
            # Assert
            assert retrieved_user is not None
            mock_cache_get.assert_called_once_with(cache_key)
            mock_cache_set.assert_called_once()
