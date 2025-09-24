# Phase 1 Technical Specifications: Core Infrastructure Foundation

**Document Version**: 1.0
**Date**: 2025-09-23
**Project**: Trading Bot - Phase 1 Development
**Compliance Framework**: PCI DSS, SOX, GDPR, MiFID II

---

## Executive Summary

This document provides comprehensive technical specifications for Phase 1 of the trading bot development: Core Infrastructure Foundation. The specifications address four critical components that form the secure, auditable foundation for all trading operations.

**Phase 1 Components:**
1. Secure Configuration Management System
2. Comprehensive Logging & Audit Framework
3. Core Data Models & Database Setup
4. Essential Utilities & Services

All specifications are designed to meet financial industry compliance requirements including data encryption (AES-256), audit trails for regulatory compliance, and fail-safe error handling patterns.

---

## 1. Secure Configuration Management System

### 1.1 Functional Requirements

**FR-CONFIG-001**: System shall encrypt all sensitive configuration data using Fernet symmetric encryption (AES-256)
**FR-CONFIG-002**: System shall support environment-based configuration loading with validation
**FR-CONFIG-003**: System shall implement key rotation mechanisms for encryption keys
**FR-CONFIG-004**: System shall validate configuration schema before application startup
**FR-CONFIG-005**: System shall support hierarchical configuration inheritance (default → environment → local)

### 1.2 Technical Implementation Specifications

#### 1.2.1 Core Classes and Interfaces

```python
# File: trading_bot/config/encryption.py
from cryptography.fernet import Fernet
from typing import Optional, Dict, Any
import os
from datetime import datetime, timedelta

class ConfigEncryption:
    """Handles encryption/decryption of sensitive configuration data."""

    def __init__(self, key_file: str = "config/encryption.key"):
        self.key_file = key_file
        self._fernet: Optional[Fernet] = None
        self._key_rotation_interval = timedelta(days=90)

    def generate_key(self) -> bytes:
        """Generate new encryption key for configuration data."""

    def load_key(self) -> bytes:
        """Load encryption key from secure storage."""

    def encrypt_value(self, value: str) -> str:
        """Encrypt configuration value."""

    def decrypt_value(self, encrypted_value: str) -> str:
        """Decrypt configuration value."""

    def rotate_key(self) -> bool:
        """Rotate encryption key and re-encrypt all values."""

# File: trading_bot/config/manager.py
from pydantic import BaseModel, Field, validator
from typing import Dict, Any, Optional, Union
import os
from pathlib import Path

class DatabaseConfig(BaseModel):
    """Database connection configuration."""
    host: str = Field(..., description="Database host")
    port: int = Field(5432, ge=1, le=65535)
    username: str = Field(..., min_length=1)
    password: str = Field(..., min_length=8)
    database: str = Field(..., min_length=1)
    pool_size: int = Field(10, ge=1, le=100)
    max_overflow: int = Field(20, ge=0, le=100)

    @validator('password')
    def validate_password_strength(cls, v):
        # Implement password strength validation
        return v

class APIConfig(BaseModel):
    """API configuration for external services."""
    alpha_vantage_key: str = Field(..., min_length=16)
    polygon_key: Optional[str] = None
    rate_limit_per_minute: int = Field(5, ge=1, le=1000)
    timeout_seconds: int = Field(30, ge=5, le=300)

class TradingConfig(BaseModel):
    """Trading-specific configuration."""
    default_position_size: float = Field(0.02, ge=0.001, le=0.1)
    max_portfolio_risk: float = Field(0.05, ge=0.001, le=0.2)
    base_currency: str = Field("USD", regex=r"^[A-Z]{3}$")
    trading_hours_start: str = Field("09:30", regex=r"^\d{2}:\d{2}$")
    trading_hours_end: str = Field("16:00", regex=r"^\d{2}:\d{2}$")

class ConfigManager:
    """Centralized configuration management with encryption and validation."""

    def __init__(self, env_file: str = ".env"):
        self.env_file = env_file
        self.encryption = ConfigEncryption()
        self._config_cache: Dict[str, Any] = {}

    def load_config(self) -> Dict[str, Any]:
        """Load and validate configuration from all sources."""

    def get_database_config(self) -> DatabaseConfig:
        """Get validated database configuration."""

    def get_api_config(self) -> APIConfig:
        """Get validated API configuration."""

    def get_trading_config(self) -> TradingConfig:
        """Get validated trading configuration."""

    def validate_configuration(self) -> bool:
        """Validate entire configuration schema."""

    def update_encrypted_value(self, key: str, value: str) -> bool:
        """Update encrypted configuration value."""
```

#### 1.2.2 File Structure

```
config/
├── __init__.py
├── manager.py          # Main configuration management
├── encryption.py       # Encryption utilities
├── schemas.py         # Pydantic configuration schemas
├── validators.py      # Custom validation functions
└── templates/
    ├── .env.example   # Environment template
    └── config.yaml.example  # Configuration template
```

### 1.3 Security Requirements

**SEC-CONFIG-001**: All API keys and passwords must be encrypted using AES-256 encryption
**SEC-CONFIG-002**: Encryption keys must be stored separately from encrypted data
**SEC-CONFIG-003**: Key rotation must occur every 90 days maximum
**SEC-CONFIG-004**: Configuration files must have restricted file permissions (600)
**SEC-CONFIG-005**: No sensitive data shall be logged in plain text

### 1.4 Input/Output Specifications

#### 1.4.1 Environment Variables
```bash
# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_USER=trading_bot
DB_PASSWORD=encrypted:gAAAAABh...  # Fernet encrypted
DB_NAME=trading_bot_dev

# API Keys (encrypted)
ALPHA_VANTAGE_KEY=encrypted:gAAAAABh...
POLYGON_API_KEY=encrypted:gAAAAABh...

# Trading Configuration
TRADING_ENVIRONMENT=development  # development|staging|production
DEFAULT_POSITION_SIZE=0.02
MAX_PORTFOLIO_RISK=0.05
```

#### 1.4.2 Configuration Schema Validation
```python
# Example configuration validation
config_manager = ConfigManager()
try:
    config = config_manager.load_config()
    db_config = config_manager.get_database_config()
    api_config = config_manager.get_api_config()
except ValidationError as e:
    logger.error(f"Configuration validation failed: {e}")
    raise ConfigurationError("Invalid configuration")
```

### 1.5 Error Handling Requirements

**ERR-CONFIG-001**: Invalid configuration must prevent application startup
**ERR-CONFIG-002**: Decryption failures must be logged and raise ConfigurationError
**ERR-CONFIG-003**: Missing required configuration must provide clear error messages
**ERR-CONFIG-004**: Configuration validation errors must specify field and constraint

### 1.6 Performance Criteria

- Configuration loading: < 100ms
- Encryption/decryption: < 10ms per operation
- Memory usage: < 50MB for configuration data
- Key rotation: < 5 seconds for all values

### 1.7 Testing Requirements

```python
# Test cases required
class TestConfigManager:
    def test_encrypt_decrypt_api_key(self):
        """Test API key encryption/decryption."""

    def test_configuration_validation(self):
        """Test configuration schema validation."""

    def test_key_rotation(self):
        """Test encryption key rotation process."""

    def test_invalid_configuration_handling(self):
        """Test handling of invalid configuration."""

    def test_environment_variable_loading(self):
        """Test loading from environment variables."""
```

---

## 2. Comprehensive Logging & Audit Framework

### 2.1 Functional Requirements

**FR-LOG-001**: System shall implement structured logging in JSON format
**FR-LOG-002**: System shall maintain complete audit trail for regulatory compliance
**FR-LOG-003**: System shall provide performance monitoring hooks
**FR-LOG-004**: System shall implement log rotation and retention policies
**FR-LOG-005**: System shall log all security events and access attempts

### 2.2 Technical Implementation Specifications

#### 2.2.1 Core Classes and Interfaces

```python
# File: trading_bot/logging/audit.py
from typing import Dict, Any, Optional, Union
from datetime import datetime
from enum import Enum
import json
import logging
from dataclasses import dataclass, asdict

class AuditEventType(Enum):
    """Audit event types for regulatory compliance."""
    TRADE_EXECUTED = "trade_executed"
    STRATEGY_STARTED = "strategy_started"
    STRATEGY_STOPPED = "strategy_stopped"
    RISK_LIMIT_BREACH = "risk_limit_breach"
    CONFIGURATION_CHANGED = "configuration_changed"
    USER_LOGIN = "user_login"
    DATA_ACCESS = "data_access"
    SYSTEM_ERROR = "system_error"

@dataclass
class AuditEvent:
    """Structured audit event for compliance tracking."""
    event_id: str
    event_type: AuditEventType
    timestamp: datetime
    user_id: Optional[str]
    session_id: Optional[str]
    component: str
    action: str
    details: Dict[str, Any]
    risk_level: str  # LOW, MEDIUM, HIGH, CRITICAL
    compliance_tags: list[str]

    def to_json(self) -> str:
        """Convert audit event to JSON string."""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        data['event_type'] = self.event_type.value
        return json.dumps(data)

class AuditLogger:
    """Centralized audit logging for regulatory compliance."""

    def __init__(self, audit_file: str = "logs/audit.log"):
        self.audit_file = audit_file
        self.logger = self._setup_audit_logger()

    def log_trade_execution(
        self,
        symbol: str,
        quantity: float,
        price: float,
        strategy: str,
        user_id: str = None
    ) -> None:
        """Log trade execution for audit trail."""

    def log_risk_event(
        self,
        event_type: str,
        details: Dict[str, Any],
        risk_level: str = "HIGH"
    ) -> None:
        """Log risk management events."""

    def log_configuration_change(
        self,
        component: str,
        old_value: Any,
        new_value: Any,
        user_id: str
    ) -> None:
        """Log configuration changes for audit."""

    def log_data_access(
        self,
        data_source: str,
        query_params: Dict[str, Any],
        user_id: str = None
    ) -> None:
        """Log data access for compliance."""

# File: trading_bot/logging/performance.py
from contextlib import contextmanager
from time import perf_counter
from typing import Dict, Any, Optional
import logging

class PerformanceMonitor:
    """Performance monitoring and profiling utilities."""

    def __init__(self):
        self.metrics: Dict[str, Any] = {}
        self.logger = logging.getLogger("trading_bot.performance")

    @contextmanager
    def measure_time(self, operation: str, metadata: Optional[Dict] = None):
        """Context manager for timing operations."""
        start_time = perf_counter()
        try:
            yield
        finally:
            duration = perf_counter() - start_time
            self._record_timing(operation, duration, metadata)

    def _record_timing(
        self,
        operation: str,
        duration: float,
        metadata: Optional[Dict] = None
    ) -> None:
        """Record timing metrics."""

    def log_memory_usage(self, component: str) -> None:
        """Log current memory usage."""

    def log_database_query_performance(
        self,
        query: str,
        duration: float,
        rows_affected: int = 0
    ) -> None:
        """Log database query performance."""

# File: trading_bot/logging/structured.py
import logging
import json
from pythonjsonlogger import jsonlogger
from typing import Dict, Any, Optional

class TradingBotFormatter(jsonlogger.JsonFormatter):
    """Custom JSON formatter for trading bot logs."""

    def add_fields(self, log_record, record, message_dict):
        super().add_fields(log_record, record, message_dict)
        log_record['timestamp'] = record.created
        log_record['level'] = record.levelname
        log_record['logger'] = record.name
        log_record['component'] = getattr(record, 'component', 'unknown')
        log_record['trace_id'] = getattr(record, 'trace_id', None)

class StructuredLogger:
    """Structured logging implementation for trading bot."""

    def __init__(self, name: str, component: str):
        self.component = component
        self.logger = logging.getLogger(name)
        self._setup_logger()

    def _setup_logger(self) -> None:
        """Setup structured JSON logging."""

    def info(self, message: str, **kwargs) -> None:
        """Log info message with structured data."""

    def warning(self, message: str, **kwargs) -> None:
        """Log warning message with structured data."""

    def error(self, message: str, error: Exception = None, **kwargs) -> None:
        """Log error message with structured data."""

    def trade_event(
        self,
        action: str,
        symbol: str,
        quantity: float = None,
        price: float = None,
        **kwargs
    ) -> None:
        """Log trading-specific events."""
```

#### 2.2.2 File Structure

```
logging/
├── __init__.py
├── audit.py           # Audit trail implementation
├── structured.py      # Structured JSON logging
├── performance.py     # Performance monitoring
├── formatters.py      # Custom log formatters
├── handlers.py        # Custom log handlers
└── config.py         # Logging configuration
```

### 2.3 Security Requirements

**SEC-LOG-001**: All logs must be tamper-evident with checksums
**SEC-LOG-002**: Sensitive data must be masked or encrypted in logs
**SEC-LOG-003**: Log files must have restricted access permissions
**SEC-LOG-004**: Audit logs must be backed up to secure storage
**SEC-LOG-005**: Log integrity must be verified on startup

### 2.4 Input/Output Specifications

#### 2.4.1 Log Format Examples

```json
{
  "timestamp": "2024-01-15T14:30:45.123Z",
  "level": "INFO",
  "logger": "trading_bot.strategy",
  "component": "momentum_strategy",
  "trace_id": "abc123def456",
  "message": "Strategy executed successfully",
  "symbol": "AAPL",
  "action": "buy_signal_generated",
  "quantity": 100,
  "price": 150.25,
  "metadata": {
    "rsi": 65.2,
    "sma_20": 148.75,
    "signal_strength": 0.85
  }
}
```

#### 2.4.2 Audit Trail Format

```json
{
  "event_id": "evt_20240115_143045_abc123",
  "event_type": "trade_executed",
  "timestamp": "2024-01-15T14:30:45.123Z",
  "user_id": "system",
  "session_id": "sess_abc123",
  "component": "execution_engine",
  "action": "execute_market_order",
  "details": {
    "order_id": "ord_123456",
    "symbol": "AAPL",
    "side": "buy",
    "quantity": 100,
    "price": 150.25,
    "commission": 1.50,
    "strategy": "momentum_v1"
  },
  "risk_level": "MEDIUM",
  "compliance_tags": ["sox", "mifid2", "trade_reporting"]
}
```

### 2.5 Performance Criteria

- Log writing: < 5ms per log entry
- Log rotation: < 1 second
- Audit query response: < 100ms for last 24 hours
- Log compression ratio: > 70%
- Storage efficiency: < 100MB per trading day

### 2.6 Testing Requirements

```python
class TestAuditFramework:
    def test_audit_event_creation(self):
        """Test audit event structure and validation."""

    def test_log_rotation_functionality(self):
        """Test log rotation and retention policies."""

    def test_performance_monitoring(self):
        """Test performance measurement accuracy."""

    def test_structured_logging_format(self):
        """Test JSON log format compliance."""

    def test_audit_trail_integrity(self):
        """Test audit trail completeness and integrity."""
```

---

## 3. Core Data Models & Database Setup

### 3.1 Functional Requirements

**FR-DB-001**: System shall implement SQLAlchemy ORM models for all trading entities
**FR-DB-002**: System shall support database connection pooling with configurable limits
**FR-DB-003**: System shall implement database migration management
**FR-DB-004**: System shall enforce data validation and constraints
**FR-DB-005**: System shall include audit columns for all mutable entities

### 3.2 Technical Implementation Specifications

#### 3.2.1 Core Models and Database Schema

```python
# File: trading_bot/models/base.py
from sqlalchemy import Column, Integer, DateTime, String, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime
from typing import Any, Dict

Base = declarative_base()

class AuditMixin:
    """Mixin class for audit fields required for compliance."""

    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())
    created_by = Column(String(100), nullable=True)
    updated_by = Column(String(100), nullable=True)
    version = Column(Integer, nullable=False, default=1)
    is_deleted = Column(Boolean, nullable=False, default=False)
    deleted_at = Column(DateTime, nullable=True)
    deleted_by = Column(String(100), nullable=True)

class TimestampMixin:
    """Mixin for timestamp tracking."""

    timestamp = Column(DateTime, nullable=False, index=True)

# File: trading_bot/models/market_data.py
from sqlalchemy import Column, Integer, String, Numeric, DateTime, Index, UniqueConstraint
from decimal import Decimal
from .base import Base, TimestampMixin, AuditMixin

class Symbol(Base, AuditMixin):
    """Master symbol reference table."""

    __tablename__ = 'symbols'

    id = Column(Integer, primary_key=True)
    symbol = Column(String(20), nullable=False, unique=True, index=True)
    name = Column(String(200), nullable=False)
    sector = Column(String(100), nullable=True)
    industry = Column(String(100), nullable=True)
    exchange = Column(String(20), nullable=False)
    currency = Column(String(3), nullable=False, default='USD')
    is_active = Column(Boolean, nullable=False, default=True)

    __table_args__ = (
        Index('idx_symbol_exchange', 'symbol', 'exchange'),
    )

class PriceData(Base, TimestampMixin):
    """Historical and real-time price data."""

    __tablename__ = 'price_data'

    id = Column(Integer, primary_key=True)
    symbol_id = Column(Integer, ForeignKey('symbols.id'), nullable=False)
    timestamp = Column(DateTime, nullable=False, index=True)
    open_price = Column(Numeric(18, 8), nullable=False)
    high_price = Column(Numeric(18, 8), nullable=False)
    low_price = Column(Numeric(18, 8), nullable=False)
    close_price = Column(Numeric(18, 8), nullable=False)
    volume = Column(Integer, nullable=False)
    adjusted_close = Column(Numeric(18, 8), nullable=True)
    timeframe = Column(String(10), nullable=False)  # 1m, 5m, 1h, 1d
    data_source = Column(String(50), nullable=False)

    __table_args__ = (
        UniqueConstraint('symbol_id', 'timestamp', 'timeframe', name='uq_price_data'),
        Index('idx_price_data_symbol_time', 'symbol_id', 'timestamp'),
        Index('idx_price_data_timeframe', 'timeframe'),
    )

# File: trading_bot/models/trading.py
from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum
from .base import Base, AuditMixin

class OrderStatus(PyEnum):
    PENDING = "pending"
    FILLED = "filled"
    PARTIALLY_FILLED = "partially_filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"

class OrderType(PyEnum):
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"

class OrderSide(PyEnum):
    BUY = "buy"
    SELL = "sell"

class Strategy(Base, AuditMixin):
    """Trading strategy metadata."""

    __tablename__ = 'strategies'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    version = Column(String(20), nullable=False)
    parameters = Column(Text, nullable=True)  # JSON string
    risk_parameters = Column(Text, nullable=True)  # JSON string
    is_active = Column(Boolean, nullable=False, default=True)

class Order(Base, AuditMixin):
    """Order management and tracking."""

    __tablename__ = 'orders'

    id = Column(Integer, primary_key=True)
    external_order_id = Column(String(100), nullable=True, index=True)
    strategy_id = Column(Integer, ForeignKey('strategies.id'), nullable=False)
    symbol_id = Column(Integer, ForeignKey('symbols.id'), nullable=False)
    order_type = Column(Enum(OrderType), nullable=False)
    side = Column(Enum(OrderSide), nullable=False)
    quantity = Column(Numeric(18, 8), nullable=False)
    price = Column(Numeric(18, 8), nullable=True)
    stop_price = Column(Numeric(18, 8), nullable=True)
    status = Column(Enum(OrderStatus), nullable=False, default=OrderStatus.PENDING)
    filled_quantity = Column(Numeric(18, 8), nullable=False, default=0)
    average_price = Column(Numeric(18, 8), nullable=True)
    commission = Column(Numeric(18, 8), nullable=True)
    submitted_at = Column(DateTime, nullable=False)
    filled_at = Column(DateTime, nullable=True)

    # Relationships
    strategy = relationship("Strategy", backref="orders")
    symbol = relationship("Symbol", backref="orders")

    __table_args__ = (
        Index('idx_orders_strategy_status', 'strategy_id', 'status'),
        Index('idx_orders_symbol_time', 'symbol_id', 'submitted_at'),
    )

class Position(Base, AuditMixin):
    """Position tracking and management."""

    __tablename__ = 'positions'

    id = Column(Integer, primary_key=True)
    strategy_id = Column(Integer, ForeignKey('strategies.id'), nullable=False)
    symbol_id = Column(Integer, ForeignKey('symbols.id'), nullable=False)
    quantity = Column(Numeric(18, 8), nullable=False)
    average_price = Column(Numeric(18, 8), nullable=False)
    market_value = Column(Numeric(18, 2), nullable=False)
    unrealized_pnl = Column(Numeric(18, 2), nullable=False, default=0)
    realized_pnl = Column(Numeric(18, 2), nullable=False, default=0)
    opened_at = Column(DateTime, nullable=False)
    closed_at = Column(DateTime, nullable=True)

    # Relationships
    strategy = relationship("Strategy", backref="positions")
    symbol = relationship("Symbol", backref="positions")

    __table_args__ = (
        UniqueConstraint('strategy_id', 'symbol_id', name='uq_position_strategy_symbol'),
        Index('idx_positions_strategy', 'strategy_id'),
    )
```

#### 3.2.2 Database Connection and Session Management

```python
# File: trading_bot/database/connection.py
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from contextlib import contextmanager
from typing import Generator, Optional
import logging

class DatabaseManager:
    """Database connection and session management."""

    def __init__(self, connection_string: str, **kwargs):
        self.connection_string = connection_string
        self.engine = self._create_engine(**kwargs)
        self.SessionLocal = sessionmaker(bind=self.engine)
        self.logger = logging.getLogger(__name__)

    def _create_engine(self, **kwargs):
        """Create SQLAlchemy engine with connection pooling."""
        engine_kwargs = {
            'poolclass': QueuePool,
            'pool_size': kwargs.get('pool_size', 10),
            'max_overflow': kwargs.get('max_overflow', 20),
            'pool_pre_ping': True,
            'pool_recycle': 3600,
            'echo': kwargs.get('debug', False)
        }

        engine = create_engine(self.connection_string, **engine_kwargs)

        # Add connection event listeners
        @event.listens_for(engine, 'connect')
        def receive_connect(dbapi_connection, connection_record):
            self.logger.debug("Database connection established")

        @event.listens_for(engine, 'checkout')
        def receive_checkout(dbapi_connection, connection_record, connection_proxy):
            self.logger.debug("Database connection checked out from pool")

        return engine

    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """Get database session with automatic cleanup."""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            self.logger.error(f"Database session error: {e}")
            raise
        finally:
            session.close()

    def health_check(self) -> bool:
        """Check database connectivity and health."""
        try:
            with self.get_session() as session:
                session.execute("SELECT 1")
                return True
        except Exception as e:
            self.logger.error(f"Database health check failed: {e}")
            return False

# File: trading_bot/database/migrations.py
from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory
from alembic.environment import EnvironmentContext
import logging

class MigrationManager:
    """Database migration management."""

    def __init__(self, alembic_cfg_path: str):
        self.alembic_cfg = Config(alembic_cfg_path)
        self.logger = logging.getLogger(__name__)

    def run_migrations(self) -> bool:
        """Run all pending migrations."""
        try:
            command.upgrade(self.alembic_cfg, "head")
            self.logger.info("Database migrations completed successfully")
            return True
        except Exception as e:
            self.logger.error(f"Migration failed: {e}")
            return False

    def create_migration(self, message: str) -> bool:
        """Create new migration script."""
        try:
            command.revision(self.alembic_cfg, message=message, autogenerate=True)
            return True
        except Exception as e:
            self.logger.error(f"Failed to create migration: {e}")
            return False

    def get_current_revision(self) -> Optional[str]:
        """Get current database revision."""
        try:
            script = ScriptDirectory.from_config(self.alembic_cfg)
            with EnvironmentContext(self.alembic_cfg, script) as env_context:
                return env_context.get_current_revision()
        except Exception as e:
            self.logger.error(f"Failed to get current revision: {e}")
            return None
```

### 3.3 Security Requirements

**SEC-DB-001**: All database connections must use SSL/TLS encryption
**SEC-DB-002**: Database credentials must be encrypted in configuration
**SEC-DB-003**: All sensitive data must be encrypted at column level
**SEC-DB-004**: Database access must be logged for audit trail
**SEC-DB-005**: Connection pooling must implement timeout controls

### 3.4 Performance Criteria

- Connection pool initialization: < 2 seconds
- Query response time: < 100ms for standard operations
- Concurrent connections: Support 50+ simultaneous connections
- Migration execution: < 30 seconds for schema changes
- Bulk data insertion: > 10,000 records per second

### 3.5 Testing Requirements

```python
class TestDatabaseModels:
    def test_model_creation_and_validation(self):
        """Test model creation with valid data."""

    def test_audit_columns_population(self):
        """Test audit column automatic population."""

    def test_database_constraints(self):
        """Test database constraint enforcement."""

    def test_connection_pooling(self):
        """Test connection pool behavior."""

    def test_migration_execution(self):
        """Test database migration process."""
```

---

## 4. Essential Utilities & Services

### 4.1 Functional Requirements

**FR-UTIL-001**: System shall implement trading-specific exception hierarchy
**FR-UTIL-002**: System shall provide financial data validation utilities
**FR-UTIL-003**: System shall handle market-aware date/time operations
**FR-UTIL-004**: System shall ensure decimal precision for financial calculations
**FR-UTIL-005**: System shall validate all configuration and input data

### 4.2 Technical Implementation Specifications

#### 4.2.1 Exception Framework

```python
# File: trading_bot/utils/exceptions.py
from typing import Optional, Dict, Any

class TradingBotException(Exception):
    """Base exception for all trading bot errors."""

    def __init__(
        self,
        message: str,
        error_code: str = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.details = details or {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for logging."""
        return {
            'error_type': self.__class__.__name__,
            'error_code': self.error_code,
            'message': self.message,
            'details': self.details
        }

class ConfigurationError(TradingBotException):
    """Configuration-related errors."""
    pass

class DataValidationError(TradingBotException):
    """Data validation errors."""

    def __init__(self, field: str, value: Any, constraint: str, **kwargs):
        message = f"Validation failed for field '{field}': {constraint}"
        details = {'field': field, 'value': str(value), 'constraint': constraint}
        super().__init__(message, details=details, **kwargs)

class TradingError(TradingBotException):
    """Trading operation errors."""
    pass

class StrategyError(TradingBotException):
    """Strategy execution errors."""
    pass

class RiskManagementError(TradingBotException):
    """Risk management violations."""

    def __init__(self, risk_type: str, current_value: float, limit: float, **kwargs):
        message = f"Risk limit exceeded: {risk_type} = {current_value}, limit = {limit}"
        details = {'risk_type': risk_type, 'current_value': current_value, 'limit': limit}
        super().__init__(message, details=details, **kwargs)

class MarketDataError(TradingBotException):
    """Market data related errors."""
    pass

class DatabaseError(TradingBotException):
    """Database operation errors."""
    pass
```

#### 4.2.2 Financial Data Validation

```python
# File: trading_bot/utils/validators.py
from decimal import Decimal, ROUND_HALF_UP
from typing import Union, Optional, List
import re
from datetime import datetime, time

class FinancialValidator:
    """Validation utilities for financial data."""

    # Price precision constants
    PRICE_PRECISION = Decimal('0.00000001')  # 8 decimal places
    QUANTITY_PRECISION = Decimal('0.00000001')  # 8 decimal places
    CURRENCY_PRECISION = Decimal('0.01')  # 2 decimal places

    @staticmethod
    def validate_price(price: Union[float, Decimal, str]) -> Decimal:
        """Validate and normalize price data."""
        if price is None:
            raise DataValidationError('price', price, 'cannot be None')

        try:
            decimal_price = Decimal(str(price))
        except (ValueError, TypeError):
            raise DataValidationError('price', price, 'must be a valid number')

        if decimal_price < 0:
            raise DataValidationError('price', price, 'cannot be negative')

        if decimal_price == 0:
            raise DataValidationError('price', price, 'cannot be zero')

        # Round to appropriate precision
        return decimal_price.quantize(FinancialValidator.PRICE_PRECISION, rounding=ROUND_HALF_UP)

    @staticmethod
    def validate_quantity(quantity: Union[float, Decimal, str]) -> Decimal:
        """Validate and normalize quantity data."""
        if quantity is None:
            raise DataValidationError('quantity', quantity, 'cannot be None')

        try:
            decimal_quantity = Decimal(str(quantity))
        except (ValueError, TypeError):
            raise DataValidationError('quantity', quantity, 'must be a valid number')

        if decimal_quantity < 0:
            raise DataValidationError('quantity', quantity, 'cannot be negative')

        return decimal_quantity.quantize(FinancialValidator.QUANTITY_PRECISION, rounding=ROUND_HALF_UP)

    @staticmethod
    def validate_symbol(symbol: str) -> str:
        """Validate trading symbol format."""
        if not symbol:
            raise DataValidationError('symbol', symbol, 'cannot be empty')

        # Basic symbol validation (alphanumeric, dots, hyphens)
        if not re.match(r'^[A-Z0-9.-]+$', symbol.upper()):
            raise DataValidationError('symbol', symbol, 'invalid format')

        if len(symbol) > 20:
            raise DataValidationError('symbol', symbol, 'too long (max 20 characters)')

        return symbol.upper()

    @staticmethod
    def validate_currency(currency: str) -> str:
        """Validate currency code (ISO 4217)."""
        if not currency:
            raise DataValidationError('currency', currency, 'cannot be empty')

        currency = currency.upper()
        if not re.match(r'^[A-Z]{3}$', currency):
            raise DataValidationError('currency', currency, 'must be 3-letter code')

        # List of common currency codes
        valid_currencies = {
            'USD', 'EUR', 'GBP', 'JPY', 'CAD', 'AUD', 'CHF', 'CNY', 'SEK', 'NZD'
        }

        if currency not in valid_currencies:
            raise DataValidationError('currency', currency, f'unsupported currency')

        return currency

# File: trading_bot/utils/market_time.py
from datetime import datetime, time, timezone, timedelta
from typing import Optional, Union
import pytz

class MarketTimeHandler:
    """Market-aware date/time handling utilities."""

    def __init__(self, market_timezone: str = 'America/New_York'):
        self.market_tz = pytz.timezone(market_timezone)
        self.utc_tz = pytz.UTC

        # Standard US market hours
        self.market_open = time(9, 30)  # 9:30 AM
        self.market_close = time(16, 0)  # 4:00 PM

        # Pre-market and after-hours
        self.premarket_start = time(4, 0)   # 4:00 AM
        self.afterhours_end = time(20, 0)   # 8:00 PM

    def is_market_open(self, dt: Optional[datetime] = None) -> bool:
        """Check if market is currently open."""
        if dt is None:
            dt = datetime.now(self.utc_tz)

        market_time = dt.astimezone(self.market_tz)

        # Check if it's a weekday
        if market_time.weekday() >= 5:  # Saturday = 5, Sunday = 6
            return False

        # Check market hours
        current_time = market_time.time()
        return self.market_open <= current_time <= self.market_close

    def next_market_open(self, dt: Optional[datetime] = None) -> datetime:
        """Get next market open time."""
        if dt is None:
            dt = datetime.now(self.utc_tz)

        market_time = dt.astimezone(self.market_tz)

        # If currently market hours on weekday, next open is tomorrow
        if self.is_market_open(dt):
            next_day = market_time + timedelta(days=1)
        else:
            next_day = market_time

        # Find next weekday
        while next_day.weekday() >= 5:
            next_day += timedelta(days=1)

        next_open = market_time.replace(
            year=next_day.year,
            month=next_day.month,
            day=next_day.day,
            hour=self.market_open.hour,
            minute=self.market_open.minute,
            second=0,
            microsecond=0
        )

        return next_open.astimezone(self.utc_tz)

    def market_time_to_utc(self, market_dt: datetime) -> datetime:
        """Convert market time to UTC."""
        if market_dt.tzinfo is None:
            market_dt = self.market_tz.localize(market_dt)
        return market_dt.astimezone(self.utc_tz)

    def utc_to_market_time(self, utc_dt: datetime) -> datetime:
        """Convert UTC time to market time."""
        if utc_dt.tzinfo is None:
            utc_dt = self.utc_tz.localize(utc_dt)
        return utc_dt.astimezone(self.market_tz)

# File: trading_bot/utils/calculations.py
from decimal import Decimal, ROUND_HALF_UP
from typing import List, Union, Tuple

class FinancialCalculations:
    """Financial calculation utilities with proper precision."""

    @staticmethod
    def calculate_position_value(quantity: Decimal, price: Decimal) -> Decimal:
        """Calculate position market value."""
        return (quantity * price).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    @staticmethod
    def calculate_pnl(
        quantity: Decimal,
        entry_price: Decimal,
        current_price: Decimal
    ) -> Decimal:
        """Calculate profit/loss for a position."""
        return ((current_price - entry_price) * quantity).quantize(
            Decimal('0.01'), rounding=ROUND_HALF_UP
        )

    @staticmethod
    def calculate_percentage_change(old_value: Decimal, new_value: Decimal) -> Decimal:
        """Calculate percentage change between two values."""
        if old_value == 0:
            return Decimal('0')
        return ((new_value - old_value) / old_value * 100).quantize(
            Decimal('0.0001'), rounding=ROUND_HALF_UP
        )

    @staticmethod
    def calculate_position_size(
        account_value: Decimal,
        risk_percentage: Decimal,
        entry_price: Decimal,
        stop_price: Decimal
    ) -> Decimal:
        """Calculate position size based on risk management."""
        risk_amount = account_value * (risk_percentage / 100)
        risk_per_share = abs(entry_price - stop_price)

        if risk_per_share == 0:
            return Decimal('0')

        position_size = risk_amount / risk_per_share
        return position_size.quantize(Decimal('0.00000001'), rounding=ROUND_HALF_UP)
```

### 4.3 Security Requirements

**SEC-UTIL-001**: All financial calculations must use Decimal precision
**SEC-UTIL-002**: Input validation must prevent injection attacks
**SEC-UTIL-003**: Error messages must not expose sensitive information
**SEC-UTIL-004**: All utilities must log security-relevant operations

### 4.4 Performance Criteria

- Validation operations: < 1ms per field
- Financial calculations: < 0.1ms per operation
- Market time calculations: < 5ms per operation
- Exception handling: < 0.5ms overhead

### 4.5 Testing Requirements

```python
class TestUtilities:
    def test_price_validation_precision(self):
        """Test price validation with various precision scenarios."""

    def test_market_time_calculations(self):
        """Test market time aware operations."""

    def test_financial_calculation_precision(self):
        """Test decimal precision in financial calculations."""

    def test_exception_hierarchy(self):
        """Test exception creation and inheritance."""

    def test_symbol_validation(self):
        """Test trading symbol validation rules."""
```

---

## 5. Implementation Roadmap

### 5.1 Development Timeline

**Week 1 (Days 1-7):**
- Day 1-2: Secure Configuration Management System
- Day 3-4: Core Database Models and Migrations
- Day 5-7: Essential Utilities Framework

**Week 2 (Days 8-14):**
- Day 8-10: Comprehensive Logging & Audit Framework
- Day 11-12: Database Connection Management
- Day 13-14: Integration Testing and Documentation

### 5.2 Implementation Priority

1. **Critical Path (Must Complete First):**
   - Configuration encryption and loading
   - Database connection and basic models
   - Exception framework

2. **High Priority (Core Functionality):**
   - Audit logging framework
   - Financial data validation
   - Market time handling

3. **Medium Priority (Enhancement):**
   - Performance monitoring
   - Advanced validation rules
   - Migration management

### 5.3 Quality Gates

Each component must pass the following quality gates:

- **Code Coverage**: Minimum 90% test coverage
- **Security Review**: All security requirements validated
- **Performance Testing**: All performance criteria met
- **Compliance Check**: Regulatory requirements satisfied
- **Documentation**: Complete API and usage documentation

---

## 6. Compliance and Risk Considerations

### 6.1 Regulatory Compliance

**SOX Compliance:**
- Complete audit trail for all financial data modifications
- Segregation of duties in configuration management
- Regular access review and certification

**GDPR Compliance:**
- Data encryption for all personally identifiable information
- Data retention policies with automatic purging
- Audit logging of all data access operations

**MiFID II Compliance:**
- Complete transaction reporting capabilities
- Clock synchronization for timestamp accuracy
- Best execution monitoring and reporting

### 6.2 Risk Mitigation

**Operational Risk:**
- Automated failover for database connections
- Circuit breaker patterns for external dependencies
- Comprehensive error handling and recovery

**Security Risk:**
- End-to-end encryption for sensitive data
- Input validation to prevent injection attacks
- Regular security audits and penetration testing

**Compliance Risk:**
- Built-in audit trails for all operations
- Automated compliance reporting
- Regular compliance validation and testing

---

## 7. Acceptance Criteria

### 7.1 Functional Acceptance Criteria

- [ ] **CONFIG-AC-001**: All sensitive configuration data encrypted with AES-256
- [ ] **CONFIG-AC-002**: Configuration validation prevents startup with invalid data
- [ ] **CONFIG-AC-003**: Key rotation completes within 5 seconds
- [ ] **LOG-AC-001**: All operations create structured audit logs
- [ ] **LOG-AC-002**: Log rotation maintains 90-day retention policy
- [ ] **LOG-AC-003**: Performance monitoring captures all critical metrics
- [ ] **DB-AC-001**: Database supports 50+ concurrent connections
- [ ] **DB-AC-002**: All migrations execute without data loss
- [ ] **DB-AC-003**: Audit columns populated automatically
- [ ] **UTIL-AC-001**: Financial calculations maintain 8-decimal precision
- [ ] **UTIL-AC-002**: Market time calculations accurate across time zones
- [ ] **UTIL-AC-003**: Exception hierarchy provides clear error classification

### 7.2 Non-Functional Acceptance Criteria

- [ ] **PERF-AC-001**: Configuration loading completes within 100ms
- [ ] **PERF-AC-002**: Database queries respond within 100ms (95th percentile)
- [ ] **PERF-AC-003**: Logging overhead less than 5ms per operation
- [ ] **SEC-AC-001**: All security requirements implemented and tested
- [ ] **SEC-AC-002**: Penetration testing identifies no critical vulnerabilities
- [ ] **COMP-AC-001**: Audit trail meets regulatory requirements
- [ ] **COMP-AC-002**: Data retention policies implemented correctly

### 7.3 Quality Acceptance Criteria

- [ ] **QUAL-AC-001**: Code coverage exceeds 90% for all components
- [ ] **QUAL-AC-002**: All code passes static analysis with no critical issues
- [ ] **QUAL-AC-003**: Performance testing validates all criteria
- [ ] **QUAL-AC-004**: Documentation complete for all public APIs
- [ ] **QUAL-AC-005**: Integration tests cover all component interactions

---

This technical specification provides a comprehensive foundation for implementing Phase 1 of the trading bot development. All components are designed with financial industry best practices, regulatory compliance requirements, and production-grade security measures.

The specifications are implementation-ready and include detailed class structures, security requirements, performance criteria, and acceptance criteria that enable systematic development and validation of the core infrastructure foundation.