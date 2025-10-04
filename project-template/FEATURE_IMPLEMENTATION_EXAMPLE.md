# Feature Implementation Example - Following Clean Python Rules

This document demonstrates how to implement a complete feature following all the guidelines in `.cursorrules`, including comprehensive monitoring, clean Python code, and testing.

## 📋 **Feature: Business Unit Management**

We'll implement a complete business unit management feature as an example of following all our development patterns.

## 🏗️ **1. Model Implementation**

### Database Model with Monitoring
```python
# app/models/business_unit.py
"""Business Unit model with comprehensive audit trail."""

from sqlalchemy import Column, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property
import uuid
from datetime import datetime

from app.core.database import Base
from shared.monitoring.decorators import log_business_event


class BusinessUnit(Base):
    """
    Business Unit model with full audit and monitoring.
    
    Represents organizational units within a tenant for compliance management.
    """
    __tablename__ = "business_units"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Multi-tenancy (REQUIRED for all models)
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # Business fields
    name = Column(String(255), nullable=False)
    description = Column(Text)
    code = Column(String(50), nullable=False)  # Unique within tenant
    
    # Hierarchy support
    parent_id = Column(UUID(as_uuid=True), ForeignKey("business_units.id"), nullable=True)
    parent = relationship("BusinessUnit", remote_side=[id], backref="children")
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Audit fields (REQUIRED for all models)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    updated_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    deleted_at = Column(DateTime, nullable=True)  # Soft delete
    
    # Relationships
    created_by_user = relationship("User", foreign_keys=[created_by])
    updated_by_user = relationship("User", foreign_keys=[updated_by])
    
    # Constraints and indexes
    __table_args__ = (
        # Unique constraint for code within tenant
        Index('ix_business_units_tenant_code', 'tenant_id', 'code', unique=True, 
              postgresql_where=Column('deleted_at').is_(None)),
        # Performance indexes
        Index('ix_business_units_tenant_active', 'tenant_id', 'is_active'),
        Index('ix_business_units_parent', 'parent_id'),
    )
    
    @hybrid_property
    def full_path(self) -> str:
        """Get full hierarchical path of the business unit."""
        if self.parent:
            return f"{self.parent.full_path} > {self.name}"
        return self.name
    
    def to_dict(self) -> dict:
        """Convert to dictionary with monitoring."""
        log_business_event(
            "business_unit_serialized",
            business_unit_id=str(self.id),
            tenant_id=str(self.tenant_id)
        )
        
        return {
            "id": str(self.id),
            "tenant_id": str(self.tenant_id),
            "name": self.name,
            "description": self.description,
            "code": self.code,
            "parent_id": str(self.parent_id) if self.parent_id else None,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "full_path": self.full_path
        }
```

## 🔧 **2. Schema Implementation**

### Pydantic Schemas with Validation
```python
# app/schemas/business_unit.py
"""Business Unit schemas with comprehensive validation."""

from pydantic import BaseModel, Field, validator
from typing import Optional, List
from uuid import UUID
from datetime import datetime
import re


class BusinessUnitBase(BaseModel):
    """Base schema for business unit with validation rules."""
    
    name: str = Field(
        ..., 
        min_length=2, 
        max_length=255,
        description="Business unit name (2-255 characters)"
    )
    description: Optional[str] = Field(
        None, 
        max_length=1000,
        description="Optional business unit description"
    )
    code: str = Field(
        ..., 
        min_length=2, 
        max_length=50,
        description="Unique code for business unit (2-50 characters)"
    )
    parent_id: Optional[UUID] = Field(
        None,
        description="Parent business unit ID for hierarchy"
    )
    is_active: bool = Field(
        True,
        description="Whether the business unit is active"
    )
    
    @validator('name')
    def validate_name(cls, v):
        """Validate business unit name."""
        if not v or not v.strip():
            raise ValueError('Business unit name cannot be empty')
        
        # Check for special characters that might cause issues
        if re.search(r'[<>\"\'&]', v):
            raise ValueError('Business unit name contains invalid characters')
        
        return v.strip()
    
    @validator('code')
    def validate_code(cls, v):
        """Validate business unit code."""
        if not v or not v.strip():
            raise ValueError('Business unit code cannot be empty')
        
        # Code should be alphanumeric with hyphens/underscores
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('Business unit code must be alphanumeric with hyphens/underscores only')
        
        return v.upper().strip()  # Normalize to uppercase


class BusinessUnitCreate(BusinessUnitBase):
    """Schema for creating a business unit."""
    pass


class BusinessUnitUpdate(BaseModel):
    """Schema for updating a business unit."""
    
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    code: Optional[str] = Field(None, min_length=2, max_length=50)
    parent_id: Optional[UUID] = None
    is_active: Optional[bool] = None
    
    @validator('name', pre=True)
    def validate_name(cls, v):
        if v is not None:
            return BusinessUnitBase.validate_name(v)
        return v
    
    @validator('code', pre=True)
    def validate_code(cls, v):
        if v is not None:
            return BusinessUnitBase.validate_code(v)
        return v


class BusinessUnitResponse(BusinessUnitBase):
    """Schema for business unit responses."""
    
    id: UUID
    tenant_id: UUID
    full_path: str
    created_at: datetime
    updated_at: datetime
    created_by: UUID
    updated_by: UUID
    
    class Config:
        from_attributes = True


class BusinessUnitListResponse(BaseModel):
    """Schema for paginated business unit list."""
    
    items: List[BusinessUnitResponse]
    total: int
    page: int
    size: int
    pages: int
    
    class Config:
        from_attributes = True
```

## 🗃️ **3. Repository Implementation**

### Repository with Caching and Monitoring
```python
# app/repositories/business_unit_repository.py
"""Business Unit repository with comprehensive monitoring and caching."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from sqlalchemy.orm import selectinload

from app.models.business_unit import BusinessUnit
from app.schemas.business_unit import BusinessUnitCreate, BusinessUnitUpdate
from shared.monitoring.decorators import trace_method, database_operation, MetricsCollector
from app.core.cache import RedisCache
from app.core.exceptions import BusinessRuleViolation
import logging

logger = logging.getLogger(__name__)


class BusinessUnitRepository:
    """Business Unit repository with caching, monitoring, and multi-tenancy."""
    
    def __init__(self, db: AsyncSession, cache: RedisCache):
        self.db = db
        self.cache = cache
        self.metrics = MetricsCollector("business_unit_repository")
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    @trace_method("business_unit_repository.create")
    async def create(
        self, 
        business_unit_data: BusinessUnitCreate, 
        tenant_id: UUID,
        created_by: UUID
    ) -> BusinessUnit:
        """Create a new business unit with validation and monitoring."""
        
        # Check for duplicate code within tenant
        existing = await self.get_by_code(business_unit_data.code, tenant_id)
        if existing:
            raise BusinessRuleViolation(
                "business_unit_code_duplicate",
                {"code": business_unit_data.code, "tenant_id": str(tenant_id)}
            )
        
        # Validate parent exists if specified
        if business_unit_data.parent_id:
            parent = await self.get_by_id(business_unit_data.parent_id, tenant_id)
            if not parent:
                raise BusinessRuleViolation(
                    "business_unit_parent_not_found",
                    {"parent_id": str(business_unit_data.parent_id)}
                )
            
            # Prevent circular hierarchy (basic check)
            if parent.parent_id == business_unit_data.parent_id:
                raise BusinessRuleViolation(
                    "business_unit_circular_hierarchy",
                    {"parent_id": str(business_unit_data.parent_id)}
                )
        
        async with database_operation("business_units", "insert", self.metrics):
            business_unit = BusinessUnit(
                tenant_id=tenant_id,
                name=business_unit_data.name,
                description=business_unit_data.description,
                code=business_unit_data.code,
                parent_id=business_unit_data.parent_id,
                is_active=business_unit_data.is_active,
                created_by=created_by,
                updated_by=created_by
            )
            
            self.db.add(business_unit)
            await self.db.commit()
            await self.db.refresh(business_unit)
        
        # Cache the new business unit
        cache_key = f"business_unit:{business_unit.id}:{tenant_id}"
        await self.cache.set(cache_key, business_unit.to_dict(), expire=300)
        
        self.logger.info(
            "Business unit created successfully",
            extra={
                "custom_dimensions": {
                    "business_unit_id": str(business_unit.id),
                    "code": business_unit.code,
                    "tenant_id": str(tenant_id),
                    "created_by": str(created_by)
                }
            }
        )
        
        return business_unit
    
    @trace_method("business_unit_repository.get_by_id")
    async def get_by_id(self, business_unit_id: UUID, tenant_id: UUID) -> Optional[BusinessUnit]:
        """Get business unit by ID with caching."""
        cache_key = f"business_unit:{business_unit_id}:{tenant_id}"
        
        # Try cache first
        cached_data = await self.cache.get(cache_key)
        if cached_data:
            self.logger.debug(
                "Business unit retrieved from cache",
                extra={"custom_dimensions": {"business_unit_id": str(business_unit_id), "cache_hit": True}}
            )
            # Note: In real implementation, you'd reconstruct the object from cache
            # For simplicity, we'll fall through to database
        
        async with database_operation("business_units", "select", self.metrics):
            query = select(BusinessUnit).options(
                selectinload(BusinessUnit.parent),
                selectinload(BusinessUnit.children)
            ).where(
                and_(
                    BusinessUnit.id == business_unit_id,
                    BusinessUnit.tenant_id == tenant_id,
                    BusinessUnit.deleted_at.is_(None)
                )
            )
            
            result = await self.db.execute(query)
            business_unit = result.scalar_one_or_none()
        
        if business_unit:
            # Update cache
            await self.cache.set(cache_key, business_unit.to_dict(), expire=300)
            
            self.logger.debug(
                "Business unit retrieved from database",
                extra={
                    "custom_dimensions": {
                        "business_unit_id": str(business_unit_id),
                        "cache_hit": False
                    }
                }
            )
        
        return business_unit
    
    @trace_method("business_unit_repository.get_by_code")
    async def get_by_code(self, code: str, tenant_id: UUID) -> Optional[BusinessUnit]:
        """Get business unit by code within tenant."""
        async with database_operation("business_units", "select", self.metrics):
            query = select(BusinessUnit).where(
                and_(
                    BusinessUnit.code == code.upper(),
                    BusinessUnit.tenant_id == tenant_id,
                    BusinessUnit.deleted_at.is_(None)
                )
            )
            
            result = await self.db.execute(query)
            return result.scalar_one_or_none()
    
    @trace_method("business_unit_repository.list_by_tenant")
    async def list_by_tenant(
        self,
        tenant_id: UUID,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        active_only: bool = True,
        parent_id: Optional[UUID] = None
    ) -> tuple[List[BusinessUnit], int]:
        """List business units with filtering and pagination."""
        
        async with database_operation("business_units", "select", self.metrics):
            # Base query
            query = select(BusinessUnit).where(
                and_(
                    BusinessUnit.tenant_id == tenant_id,
                    BusinessUnit.deleted_at.is_(None)
                )
            ).options(
                selectinload(BusinessUnit.parent)
            )
            
            # Apply filters
            if active_only:
                query = query.where(BusinessUnit.is_active == True)
            
            if parent_id:
                query = query.where(BusinessUnit.parent_id == parent_id)
            
            if search:
                search_term = f"%{search.lower()}%"
                query = query.where(
                    or_(
                        func.lower(BusinessUnit.name).contains(search_term),
                        func.lower(BusinessUnit.code).contains(search_term),
                        func.lower(BusinessUnit.description).contains(search_term)
                    )
                )
            
            # Count total
            count_query = select(func.count()).select_from(query.subquery())
            total_result = await self.db.execute(count_query)
            total = total_result.scalar()
            
            # Apply pagination
            query = query.offset(skip).limit(limit).order_by(BusinessUnit.name)
            
            # Execute query
            result = await self.db.execute(query)
            business_units = result.scalars().all()
        
        self.logger.info(
            "Business units listed",
            extra={
                "custom_dimensions": {
                    "tenant_id": str(tenant_id),
                    "total_count": total,
                    "returned_count": len(business_units),
                    "search": search,
                    "active_only": active_only
                }
            }
        )
        
        return list(business_units), total
    
    @trace_method("business_unit_repository.update")
    async def update(
        self,
        business_unit_id: UUID,
        business_unit_data: BusinessUnitUpdate,
        tenant_id: UUID,
        updated_by: UUID
    ) -> Optional[BusinessUnit]:
        """Update business unit with validation."""
        
        # Get existing business unit
        business_unit = await self.get_by_id(business_unit_id, tenant_id)
        if not business_unit:
            return None
        
        # Validate code uniqueness if changed
        if business_unit_data.code and business_unit_data.code != business_unit.code:
            existing = await self.get_by_code(business_unit_data.code, tenant_id)
            if existing and existing.id != business_unit_id:
                raise BusinessRuleViolation(
                    "business_unit_code_duplicate",
                    {"code": business_unit_data.code}
                )
        
        async with database_operation("business_units", "update", self.metrics):
            # Update fields
            update_data = business_unit_data.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(business_unit, field, value)
            
            business_unit.updated_by = updated_by
            
            await self.db.commit()
            await self.db.refresh(business_unit)
        
        # Invalidate cache
        cache_key = f"business_unit:{business_unit_id}:{tenant_id}"
        await self.cache.delete(cache_key)
        
        self.logger.info(
            "Business unit updated successfully",
            extra={
                "custom_dimensions": {
                    "business_unit_id": str(business_unit_id),
                    "updated_by": str(updated_by),
                    "updated_fields": list(update_data.keys())
                }
            }
        )
        
        return business_unit
    
    @trace_method("business_unit_repository.soft_delete")
    async def soft_delete(
        self,
        business_unit_id: UUID,
        tenant_id: UUID,
        deleted_by: UUID
    ) -> bool:
        """Soft delete business unit with validation."""
        
        business_unit = await self.get_by_id(business_unit_id, tenant_id)
        if not business_unit:
            return False
        
        # Check if business unit has children
        async with database_operation("business_units", "select", self.metrics):
            children_query = select(func.count()).where(
                and_(
                    BusinessUnit.parent_id == business_unit_id,
                    BusinessUnit.deleted_at.is_(None)
                )
            )
            children_result = await self.db.execute(children_query)
            children_count = children_result.scalar()
        
        if children_count > 0:
            raise BusinessRuleViolation(
                "business_unit_has_children",
                {"business_unit_id": str(business_unit_id), "children_count": children_count}
            )
        
        async with database_operation("business_units", "soft_delete", self.metrics):
            business_unit.deleted_at = datetime.utcnow()
            business_unit.updated_by = deleted_by
            
            await self.db.commit()
        
        # Invalidate cache
        cache_key = f"business_unit:{business_unit_id}:{tenant_id}"
        await self.cache.delete(cache_key)
        
        self.logger.info(
            "Business unit soft deleted",
            extra={
                "custom_dimensions": {
                    "business_unit_id": str(business_unit_id),
                    "deleted_by": str(deleted_by)
                }
            }
        )
        
        return True
```

## 🎯 **4. Service Implementation**

### Service Layer with Event Publishing
```python
# app/services/business_unit_service.py
"""Business Unit service with comprehensive monitoring and event handling."""

from typing import List, Optional
from uuid import UUID

from app.repositories.business_unit_repository import BusinessUnitRepository
from app.schemas.business_unit import (
    BusinessUnitCreate, 
    BusinessUnitUpdate, 
    BusinessUnitResponse,
    BusinessUnitListResponse
)
from app.models.business_unit import BusinessUnit
from shared.monitoring.decorators import trace_method, MetricsCollector, log_business_event
from app.core.events import EventPublisher
from app.core.exceptions import BusinessRuleViolation
import logging

logger = logging.getLogger(__name__)


class BusinessUnitService:
    """Business Unit service with monitoring, caching, and event publishing."""
    
    def __init__(
        self,
        business_unit_repo: BusinessUnitRepository,
        event_publisher: EventPublisher
    ):
        self.business_unit_repo = business_unit_repo
        self.event_publisher = event_publisher
        self.metrics = MetricsCollector("business_unit_service")
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    @trace_method("business_unit_service.create_business_unit")
    async def create_business_unit(
        self,
        business_unit_data: BusinessUnitCreate,
        tenant_id: UUID,
        created_by: UUID
    ) -> BusinessUnitResponse:
        """Create a new business unit with comprehensive monitoring."""
        
        self.logger.info(
            "Creating business unit",
            extra={
                "custom_dimensions": {
                    "name": business_unit_data.name,
                    "code": business_unit_data.code,
                    "tenant_id": str(tenant_id),
                    "created_by": str(created_by)
                }
            }
        )
        
        try:
            # Create business unit
            business_unit = await self.business_unit_repo.create(
                business_unit_data, tenant_id, created_by
            )
            
            # Publish event
            await self.event_publisher.publish(
                "business_unit.business_unit.created",
                {
                    "business_unit_id": str(business_unit.id),
                    "name": business_unit.name,
                    "code": business_unit.code,
                    "tenant_id": str(tenant_id),
                    "created_by": str(created_by),
                    "timestamp": business_unit.created_at.isoformat()
                }
            )
            
            # Log business event
            log_business_event(
                "business_unit_created",
                business_unit_id=str(business_unit.id),
                name=business_unit.name,
                code=business_unit.code,
                tenant_id=str(tenant_id)
            )
            
            # Record success metrics
            self.metrics.increment_counter("business_unit_created")
            
            self.logger.info(
                "Business unit created successfully",
                extra={
                    "custom_dimensions": {
                        "business_unit_id": str(business_unit.id),
                        "name": business_unit.name,
                        "code": business_unit.code
                    }
                }
            )
            
            return BusinessUnitResponse.from_orm(business_unit)
            
        except BusinessRuleViolation as e:
            self.metrics.increment_counter("business_unit_creation_failed", {"reason": "business_rule"})
            self.logger.warning(
                "Business unit creation failed - business rule violation",
                extra={
                    "custom_dimensions": {
                        "rule": e.rule,
                        "details": e.details,
                        "tenant_id": str(tenant_id)
                    }
                }
            )
            raise
            
        except Exception as e:
            self.metrics.increment_counter("business_unit_creation_failed", {"reason": "error"})
            self.logger.error(
                "Business unit creation failed",
                extra={
                    "custom_dimensions": {
                        "error": str(e),
                        "error_type": type(e).__name__,
                        "tenant_id": str(tenant_id)
                    }
                }
            )
            raise
    
    # ... (similar implementation for other methods)
```

## 🔌 **5. API Endpoint Implementation**

### FastAPI Endpoints with Comprehensive Error Handling
```python
# app/api/routes/business_units.py
"""Business Unit API endpoints with comprehensive monitoring."""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from uuid import UUID

from app.services.business_unit_service import BusinessUnitService
from app.schemas.business_unit import (
    BusinessUnitCreate,
    BusinessUnitUpdate, 
    BusinessUnitResponse,
    BusinessUnitListResponse
)
from app.core.auth import get_current_user, require_permission
from app.core.exceptions import BusinessRuleViolation
from app.models.user import User
from shared.monitoring.decorators import trace_function
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/", response_model=BusinessUnitResponse, status_code=201)
@trace_function("business_unit_api.create_business_unit")
async def create_business_unit(
    business_unit_data: BusinessUnitCreate,
    current_user: User = Depends(get_current_user),
    business_unit_service: BusinessUnitService = Depends(),
    _: None = Depends(require_permission("business_unit:create"))
) -> BusinessUnitResponse:
    """
    Create a new business unit.
    
    Requires: business_unit:create permission
    """
    try:
        return await business_unit_service.create_business_unit(
            business_unit_data,
            current_user.tenant_id,
            current_user.id
        )
    except BusinessRuleViolation as e:
        logger.warning(
            "Business unit creation failed - business rule violation",
            extra={
                "custom_dimensions": {
                    "rule": e.rule,
                    "user_id": str(current_user.id),
                    "tenant_id": str(current_user.tenant_id)
                }
            }
        )
        raise HTTPException(
            status_code=400,
            detail={
                "error": {
                    "code": e.rule.upper(),
                    "message": str(e),
                    "details": e.details
                }
            }
        )


@router.get("/{business_unit_id}", response_model=BusinessUnitResponse)
@trace_function("business_unit_api.get_business_unit")
async def get_business_unit(
    business_unit_id: UUID,
    current_user: User = Depends(get_current_user),
    business_unit_service: BusinessUnitService = Depends(),
    _: None = Depends(require_permission("business_unit:read"))
) -> BusinessUnitResponse:
    """
    Get a business unit by ID.
    
    Requires: business_unit:read permission
    """
    business_unit = await business_unit_service.get_business_unit(
        business_unit_id,
        current_user.tenant_id
    )
    
    if not business_unit:
        raise HTTPException(
            status_code=404,
            detail={
                "error": {
                    "code": "BUSINESS_UNIT_NOT_FOUND",
                    "message": "Business unit not found"
                }
            }
        )
    
    return business_unit


@router.get("/", response_model=BusinessUnitListResponse)
@trace_function("business_unit_api.list_business_units")
async def list_business_units(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    search: Optional[str] = Query(None, description="Search term"),
    active_only: bool = Query(True, description="Show only active business units"),
    parent_id: Optional[UUID] = Query(None, description="Filter by parent business unit"),
    current_user: User = Depends(get_current_user),
    business_unit_service: BusinessUnitService = Depends(),
    _: None = Depends(require_permission("business_unit:read"))
) -> BusinessUnitListResponse:
    """
    List business units with filtering and pagination.
    
    Requires: business_unit:read permission
    """
    skip = (page - 1) * size
    
    business_units, total = await business_unit_service.list_business_units(
        tenant_id=current_user.tenant_id,
        skip=skip,
        limit=size,
        search=search,
        active_only=active_only,
        parent_id=parent_id
    )
    
    pages = (total + size - 1) // size  # Ceiling division
    
    return BusinessUnitListResponse(
        items=business_units,
        total=total,
        page=page,
        size=size,
        pages=pages
    )


# ... (similar implementation for update and delete endpoints)
```

## 🧪 **6. Comprehensive Testing**

### Unit Tests
```python
# tests/unit/test_business_unit_service.py
"""Unit tests for business unit service."""

import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import UUID, uuid4

from app.services.business_unit_service import BusinessUnitService
from app.schemas.business_unit import BusinessUnitCreate
from app.models.business_unit import BusinessUnit
from app.core.exceptions import BusinessRuleViolation


class TestBusinessUnitService:
    """Unit tests for BusinessUnitService."""
    
    @pytest.fixture
    def mock_business_unit_repo(self):
        """Mock business unit repository."""
        return AsyncMock()
    
    @pytest.fixture
    def mock_event_publisher(self):
        """Mock event publisher."""
        return AsyncMock()
    
    @pytest.fixture
    def business_unit_service(self, mock_business_unit_repo, mock_event_publisher):
        """Business unit service with mocked dependencies."""
        return BusinessUnitService(mock_business_unit_repo, mock_event_publisher)
    
    @pytest.mark.asyncio
    async def test_create_business_unit_success(
        self, 
        business_unit_service, 
        mock_business_unit_repo,
        mock_event_publisher
    ):
        """Test successful business unit creation."""
        # Arrange
        tenant_id = uuid4()
        created_by = uuid4()
        business_unit_data = BusinessUnitCreate(
            name="Test Business Unit",
            code="TEST_BU",
            description="Test description"
        )
        
        created_business_unit = BusinessUnit(
            id=uuid4(),
            tenant_id=tenant_id,
            name=business_unit_data.name,
            code=business_unit_data.code,
            description=business_unit_data.description,
            created_by=created_by
        )
        
        mock_business_unit_repo.create.return_value = created_business_unit
        
        # Act
        result = await business_unit_service.create_business_unit(
            business_unit_data, tenant_id, created_by
        )
        
        # Assert
        assert result.name == business_unit_data.name
        assert result.code == business_unit_data.code
        
        mock_business_unit_repo.create.assert_called_once_with(
            business_unit_data, tenant_id, created_by
        )
        
        mock_event_publisher.publish.assert_called_once()
        event_call = mock_event_publisher.publish.call_args
        assert event_call[0][0] == "business_unit.business_unit.created"
        assert event_call[0][1]["business_unit_id"] == str(created_business_unit.id)
    
    @pytest.mark.asyncio
    async def test_create_business_unit_duplicate_code(
        self,
        business_unit_service,
        mock_business_unit_repo
    ):
        """Test business unit creation with duplicate code."""
        # Arrange
        tenant_id = uuid4()
        created_by = uuid4()
        business_unit_data = BusinessUnitCreate(
            name="Test Business Unit",
            code="DUPLICATE_CODE"
        )
        
        mock_business_unit_repo.create.side_effect = BusinessRuleViolation(
            "business_unit_code_duplicate",
            {"code": "DUPLICATE_CODE"}
        )
        
        # Act & Assert
        with pytest.raises(BusinessRuleViolation) as exc_info:
            await business_unit_service.create_business_unit(
                business_unit_data, tenant_id, created_by
            )
        
        assert exc_info.value.rule == "business_unit_code_duplicate"
```

### Integration Tests
```python
# tests/integration/test_business_unit_api.py
"""Integration tests for business unit API."""

import pytest
from httpx import AsyncClient
from uuid import uuid4

from app.models.business_unit import BusinessUnit


class TestBusinessUnitAPI:
    """Integration tests for business unit API."""
    
    @pytest.mark.asyncio
    async def test_create_business_unit_endpoint(
        self, 
        client: AsyncClient,
        auth_headers,
        test_session
    ):
        """Test business unit creation endpoint."""
        # Arrange
        business_unit_data = {
            "name": "Test Business Unit",
            "code": "TEST_BU",
            "description": "Test description"
        }
        
        # Act
        response = await client.post(
            "/api/v1/business-units/",
            json=business_unit_data,
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == 201
        
        data = response.json()
        assert data["name"] == business_unit_data["name"]
        assert data["code"] == business_unit_data["code"]
        assert "id" in data
        assert "created_at" in data
    
    @pytest.mark.asyncio
    async def test_create_business_unit_duplicate_code(
        self,
        client: AsyncClient,
        auth_headers,
        test_session,
        test_business_unit
    ):
        """Test business unit creation with duplicate code."""
        # Arrange
        business_unit_data = {
            "name": "Another Business Unit",
            "code": test_business_unit.code  # Duplicate code
        }
        
        # Act
        response = await client.post(
            "/api/v1/business-units/",
            json=business_unit_data,
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == 400
        
        error_data = response.json()
        assert "error" in error_data
        assert error_data["error"]["code"] == "BUSINESS_UNIT_CODE_DUPLICATE"
```

## 📋 **Summary**

This example demonstrates:

1. **✅ Complete monitoring integration** - Every function, database operation, and external call is traced
2. **✅ Clean Python patterns** - Repository pattern, service layer, proper error handling
3. **✅ Comprehensive validation** - Pydantic schemas with business rule validation
4. **✅ Multi-tenancy** - Proper tenant isolation throughout
5. **✅ Event publishing** - Business events for integration
6. **✅ Caching strategy** - Redis caching with proper invalidation
7. **✅ Error handling** - Structured error responses and logging
8. **✅ Testing coverage** - Unit and integration tests
9. **✅ API documentation** - FastAPI auto-documentation
10. **✅ Security** - Permission-based access control

This pattern should be followed for **every feature** implementation to ensure consistency, monitoring, and maintainability across the platform.
