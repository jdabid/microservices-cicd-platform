# 📚 Día 2: Appointments Feature - CQRS - Aprendizajes

**Fecha:** 27 Enero 2025  
**Duración:** 4 horas  
**Estado:** ✅ Completado  
**PR:** #1

---

## 🎯 Objetivos Alcanzados

- [x] SQLAlchemy models con indexes y constraints
- [x] Pydantic schemas con validaciones custom
- [x] CQRS pattern: 3 Commands, 5 Queries
- [x] 8 RESTful endpoints
- [x] Alembic migrations configurado
- [x] 18 unit tests (100% pass rate)
- [x] Feature branch workflow aplicado

---

## 🏗️ Conceptos Clave Aprendidos

### 1. CQRS Pattern (Command Query Responsibility Segregation)

**¿Qué es CQRS?**
Separar operaciones de **escritura** (Commands) de **lectura** (Queries).

**Estructura implementada:**
```
appointments/
├── commands/              # WRITE operations
│   ├── create_appointment.py
│   ├── update_appointment.py
│   └── cancel_appointment.py
└── queries/               # READ operations
    ├── get_appointment.py
    ├── list_appointments.py
    ├── get_upcoming.py
    ├── by_patient.py
    └── by_doctor.py
```

**Diferencias clave:**

| Aspecto | Commands | Queries |
|---------|----------|---------|
| Propósito | Modificar estado | Leer datos |
| Side effects | Sí (write DB) | No (read-only) |
| Retorno | Entidad creada/actualizada | Lista/entidad |
| Transacciones | Sí (commit/rollback) | No necesarias |
| Caching | No | Sí (pueden cachear) |

**Ejemplo Command:**
```python
class CreateAppointmentCommand:
    def __init__(self, db: Session):
        self.db = db
    
    def execute(self, data: AppointmentCreate) -> Appointment:
        # Business rules validation
        if self._is_slot_taken(data.appointment_date):
            raise SlotAlreadyTakenException()
        
        # Create
        appointment = Appointment(**data.dict())
        self.db.add(appointment)
        self.db.commit()  # ← Modifica DB
        self.db.refresh(appointment)
        
        # Side effect: Send email
        send_confirmation_email.delay(appointment.id)
        
        return appointment
```

**Ejemplo Query:**
```python
class ListAppointmentsQuery:
    def __init__(self, db: Session):
        self.db = db
    
    def execute(self, skip: int, limit: int) -> List[Appointment]:
        # Solo lectura, sin side effects
        return self.db.query(Appointment)\
            .offset(skip)\
            .limit(limit)\
            .all()  # ← Solo lee
```

**Ventajas de CQRS:**
- ✅ **Separation of concerns:** Write y read son diferentes responsabilidades
- ✅ **Optimización:** Queries pueden usar read replicas, caching
- ✅ **Escalabilidad:** Escalar reads y writes independientemente
- ✅ **Testing:** Test commands vs queries separadamente
- ✅ **Business logic:** Commands contienen toda la lógica de negocio

**Cuándo usar CQRS:**
- Sistemas con reads >> writes (ej: e-commerce, blogs)
- Cuando necesitas optimizar queries complejas
- Microservicios con DBs separadas para read/write
- Event-sourced systems

**Cuándo NO usar CQRS:**
- CRUDs simples sin lógica de negocio
- Sistemas pequeños con pocas operaciones
- Cuando añade complejidad innecesaria

---

### 2. SQLAlchemy 2.0 ORM

**Model implementado:**
```python
class Appointment(Base):
    __tablename__ = "appointments"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_name = Column(String(100), nullable=False)
    patient_email = Column(String(100), nullable=False, index=True)
    doctor_name = Column(String(100), nullable=False, index=True)
    specialty = Column(String(50), nullable=False)
    appointment_date = Column(DateTime(timezone=True), nullable=False, index=True)
    status = Column(Enum(AppointmentStatus), default=AppointmentStatus.SCHEDULED, index=True)
    
    # Indexes compuestos para queries comunes
    __table_args__ = (
        Index('ix_patient_date', 'patient_email', 'appointment_date'),
        Index('ix_doctor_date', 'doctor_name', 'appointment_date'),
    )
```

**Conceptos importantes:**

**a) Indexes:**
```python
# Index simple
patient_email = Column(String, index=True)

# Index compuesto (para queries que filtran por ambos)
Index('ix_patient_date', 'patient_email', 'appointment_date')
```

**¿Por qué indexes?**
- Sin index: Full table scan (lento)
- Con index: B-tree lookup (rápido)

**Cuándo crear index:**
- ✅ Columnas en WHERE clauses
- ✅ Columnas en JOIN conditions
- ✅ Columnas en ORDER BY
- ❌ Columnas que cambian frecuentemente
- ❌ Tablas muy pequeñas

**b) Enums:**
```python
class AppointmentStatus(str, Enum):
    SCHEDULED = "SCHEDULED"
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"
    COMPLETED = "COMPLETED"
    NO_SHOW = "NO_SHOW"
```

**Ventajas:**
- Type safety en Python
- Validación automática
- Auto-completion en IDE
- DB constraint (solo valores permitidos)

**c) Relationships (futuro):**
```python
# Cuando tengamos tabla de Patients:
patient = relationship("Patient", back_populates="appointments")
```

---

### 3. Pydantic Schemas

**Schemas implementados:**
```python
# Para crear (input)
class AppointmentCreate(BaseModel):
    patient_name: str = Field(..., min_length=2, max_length=100)
    patient_email: EmailStr
    appointment_date: datetime
    duration_minutes: int = Field(30, ge=15, le=240)

# Para respuesta (output)
class AppointmentResponse(BaseModel):
    id: int
    patient_name: str
    status: AppointmentStatus
    created_at: datetime
    
    class Config:
        from_attributes = True  # Permite crear desde ORM model
```

**Validadores custom:**
```python
@field_validator('appointment_date')
def validate_future_date(cls, v):
    if v <= datetime.now(timezone.utc):
        raise ValueError('Appointment must be in the future')
    return v

@field_validator('patient_email')
def validate_email_domain(cls, v):
    if not v.endswith(('@gmail.com', '@yahoo.com')):
        raise ValueError('Only gmail/yahoo allowed')
    return v
```

**Diferencia Model vs Schema:**
- **Model (SQLAlchemy):** Representa tabla en DB
- **Schema (Pydantic):** Valida datos de API

**Flujo:**
```
Request → Pydantic Schema (validate) → Command → SQLAlchemy Model (persist) → Pydantic Schema (serialize) → Response
```

---

### 4. Alembic Migrations

**¿Qué es Alembic?**
Herramienta para versionar cambios en el schema de la DB.

**Conceptos:**

**a) Revision:**
Cada cambio en el schema es una "revision"
```python
# alembic/versions/abc123_create_appointments.py
def upgrade():
    op.create_table('appointments', ...)

def downgrade():
    op.drop_table('appointments')
```

**b) Comandos básicos:**
```bash
# Crear nueva migration
alembic revision --autogenerate -m "Add appointments table"

# Aplicar migrations
alembic upgrade head

# Rollback última migration
alembic downgrade -1

# Ver estado actual
alembic current

# Ver historial
alembic history
```

**c) Autogenerate:**
Alembic compara models con DB y genera migration automáticamente.

⚠️ **Importante:** Siempre revisar migrations autogeneradas antes de aplicar.

**Workflow típico:**
1. Cambiar SQLAlchemy model
2. `alembic revision --autogenerate -m "descripción"`
3. Revisar migration generada
4. `alembic upgrade head`
5. Commit migration al repo

---

## 🛠️ Implementación Detallada

### Arquitectura de Endpoints

**8 endpoints implementados:**

| Método | Ruta | Command/Query | Propósito |
|--------|------|---------------|-----------|
| POST | /appointments/ | CreateAppointmentCommand | Crear cita |
| GET | /appointments/ | ListAppointmentsQuery | Listar con paginación |
| GET | /appointments/{id} | GetAppointmentQuery | Obtener una cita |
| PUT | /appointments/{id} | UpdateAppointmentCommand | Actualizar cita |
| DELETE | /appointments/{id} | CancelAppointmentCommand | Cancelar (soft delete) |
| GET | /appointments/upcoming | GetUpcomingAppointmentsQuery | Próximas citas |
| GET | /appointments/patient/{email} | GetByPatientQuery | Citas de paciente |
| GET | /appointments/doctor/{name} | GetByDoctorQuery | Citas de doctor |

**Paginación:**
```python
@router.get("/", response_model=PaginatedAppointments)
def list_appointments(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    query = ListAppointmentsQuery(db)
    items = query.execute(skip, limit)
    total = query.count()
    
    return {
        "items": items,
        "total": total,
        "skip": skip,
        "limit": limit
    }
```

---

### Business Rules Implementadas

**1. No double-booking:**
```python
def _is_slot_taken(self, date: datetime, doctor: str) -> bool:
    existing = self.db.query(Appointment).filter(
        Appointment.doctor_name == doctor,
        Appointment.appointment_date == date,
        Appointment.status != AppointmentStatus.CANCELLED
    ).first()
    return existing is not None
```

**2. Only future appointments:**
```python
if appointment_date <= datetime.now(timezone.utc):
    raise ValueError("Cannot book appointments in the past")
```

**3. Valid duration:**
```python
duration_minutes: int = Field(30, ge=15, le=240, multiple_of=15)
```

**4. Cancellation rules:**
```python
def cancel(self, appointment_id: int, reason: str):
    appointment = self._get_or_404(appointment_id)
    
    if appointment.status == AppointmentStatus.COMPLETED:
        raise CannotCancelCompletedAppointment()
    
    if appointment.appointment_date < datetime.now() + timedelta(hours=24):
        raise CannotCancelLessThan24Hours()
    
    appointment.status = AppointmentStatus.CANCELLED
    appointment.cancellation_reason = reason
    self.db.commit()
```

---

## 🧪 Testing Strategy

**18 tests implementados:**

**Test structure:**
```
tests/unit/features/appointments/
├── test_commands.py      # 9 tests
└── test_queries.py       # 9 tests
```

**Fixtures importantes:**
```python
@pytest.fixture
def db_session():
    """In-memory SQLite para tests"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

@pytest.fixture
def sample_appointment(db_session):
    """Appointment de ejemplo para tests"""
    appointment = Appointment(
        patient_name="John Doe",
        patient_email="john@example.com",
        # ...
    )
    db_session.add(appointment)
    db_session.commit()
    return appointment
```

**Test examples:**
```python
def test_create_appointment_success(db_session):
    """Happy path"""
    command = CreateAppointmentCommand(db_session)
    data = AppointmentCreate(...)
    
    result = command.execute(data)
    
    assert result.id is not None
    assert result.patient_name == data.patient_name
    assert result.status == AppointmentStatus.SCHEDULED

def test_create_appointment_duplicate_slot(db_session, sample_appointment):
    """Negative case: slot already taken"""
    command = CreateAppointmentCommand(db_session)
    data = AppointmentCreate(
        appointment_date=sample_appointment.appointment_date,
        doctor_name=sample_appointment.doctor_name,
        # ...
    )
    
    with pytest.raises(SlotAlreadyTakenException):
        command.execute(data)
```

**Test categories:**
- ✅ Happy paths (todo funciona)
- ✅ Validation errors (input inválido)
- ✅ Business rule violations (double-booking)
- ✅ Not found cases (ID inexistente)
- ✅ Edge cases (límites, fechas, etc.)

---

## 🔧 Comandos Útiles
```bash
# Crear migration
alembic revision --autogenerate -m "Create appointments table"

# Aplicar migrations
alembic upgrade head

# Rollback
alembic downgrade -1

# Ver historial
alembic history

# Tests
pytest tests/unit/features/appointments/

# Con coverage
pytest --cov=app/features/appointments --cov-report=html

# Test específico
pytest tests/unit/features/appointments/test_commands.py::test_create_appointment
```

---

## 💡 Decisiones de Diseño

### 1. ¿Por qué CQRS para CRUD simple?
**Decisión:** Aplicar CQRS desde el inicio  
**Razón:**
- Preparación para escalar
- Separación clara facilita testing
- Queries optimizables independientemente
- Patrón consistente en toda la app

### 2. ¿Soft delete o hard delete?
**Decisión:** Soft delete (cambiar status a CANCELLED)  
**Razón:**
- Audit trail (histórico)
- Posibilidad de "uncancel"
- Reports incluyen canceladas
- Compliance/legal

### 3. ¿Indexes desde el inicio?
**Decisión:** Sí, en columnas que serán filtradas  
**Razón:**
- Más difícil agregar después con data
- Query performance desde día 1
- Migrations limpias

---

## 🐛 Problemas Enfrentados

### Problema 1: Timezone-aware datetime
**Síntoma:** Comparaciones de fecha fallaban

**Solución:**
```python
# Antes
appointment_date = Column(DateTime)

# Después
appointment_date = Column(DateTime(timezone=True))

# En código
datetime.now(timezone.utc)  # No datetime.now()
```

**Lección:** Siempre usar timezone-aware datetimes

---

### Problema 2: Pydantic vs SQLAlchemy naming
**Síntoma:** `from_orm` no funcionaba

**Solución:**
```python
class Config:
    from_attributes = True  # Pydantic v2
    # orm_mode = True  # Pydantic v1 (deprecated)
```

---

### Problema 3: Circular imports
**Síntoma:** ImportError entre router y commands

**Solución:** Imports locales en funciones
```python
# En router.py
def create_appointment(...):
    from .commands.create_appointment import CreateAppointmentCommand
    # ...
```

**Lección:** Organizar imports cuidadosamente en Vertical Slice

---

## 📊 Métricas del Día 2
```
Tiempo: 4 horas
Commits: 5-6 commits
PR: #1 (26 archivos, ~1,500 líneas)
Tests: 18 (100% pass)
Archivos creados: 26
Endpoints: 8
```

---

## 🎓 Para Entrevistas

**Pregunta:** ¿Explica CQRS y por qué lo usaste?

**Respuesta:**
> "CQRS separa operaciones de escritura (Commands) de lectura (Queries). Los Commands contienen toda la business logic y modifican el estado, mientras que las Queries solo leen datos sin side effects. Lo implementé porque facilita testing, permite optimizar queries independientemente, y prepara el sistema para escalar reads y writes por separado. Por ejemplo, mis Commands validan business rules como no permitir double-booking, mientras que mis Queries pueden ser cacheadas sin preocupación por side effects."

---

**Pregunta:** ¿Cómo manejas database migrations?

**Respuesta:**
> "Uso Alembic para versionar cambios en el schema. Cada vez que modifico un SQLAlchemy model, genero una migration con `alembic revision --autogenerate`, reviso el código generado, y la aplico con `alembic upgrade head`. Las migrations están en version control, lo que permite rollbacks con `alembic downgrade`. Esto da trazabilidad completa de cambios en la DB y facilita deployments coordinados entre código y schema."

---

## 🚀 Próximos Pasos

**Día 7:**
- Dockerizar backend API
- Multi-stage Dockerfile
- Optimizar imagen (<200MB)
- Health checks

---

## 📚 Recursos

- CQRS: https://martinfowler.com/bliki/CQRS.html
- SQLAlchemy: https://docs.sqlalchemy.org/
- Pydantic: https://docs.pydantic.dev/
- Alembic: https://alembic.sqlalchemy.org/

---

**Actualizado:** 28 Enero 2025