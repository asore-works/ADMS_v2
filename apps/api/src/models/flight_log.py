"""Flight Log model"""

from __future__ import annotations

import enum
from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base, TimestampMixin, uuid_pk

if TYPE_CHECKING:
    from src.models.equipment import Equipment
    from src.models.project import Project
    from src.models.staff import Staff


class FlightPurpose(enum.Enum):
    """Flight purpose types"""

    SURVEY = "survey"  # Aerial survey/mapping
    INSPECTION = "inspection"  # Infrastructure inspection
    PHOTOGRAPHY = "photography"  # Photography/videography
    AGRICULTURE = "agriculture"  # Agricultural operations
    DELIVERY = "delivery"  # Delivery operations
    TRAINING = "training"  # Training flights
    MAINTENANCE = "maintenance"  # Test flights after maintenance
    OTHER = "other"  # Other purposes


class WeatherCondition(enum.Enum):
    """Weather condition categories"""

    CLEAR = "clear"  # Clear sky
    CLOUDY = "cloudy"  # Cloudy
    PARTLY_CLOUDY = "partly_cloudy"  # Partly cloudy
    RAINY = "rainy"  # Rainy
    WINDY = "windy"  # Strong winds
    FOG = "fog"  # Foggy


class FlightLog(Base, TimestampMixin):
    """Flight Log model

    Records details of each drone flight operation.
    """

    __tablename__ = "flight_logs"

    id: Mapped[uuid_pk]
    flight_number: Mapped[str | None] = mapped_column(String(50))  # Internal flight number
    purpose: Mapped[FlightPurpose] = mapped_column(
        Enum(FlightPurpose, native_enum=False, length=20),
        nullable=False,
        index=True,
    )

    # Time information
    takeoff_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    landing_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    flight_duration_minutes: Mapped[int] = mapped_column(Integer, nullable=False)

    # Location information
    takeoff_location: Mapped[str | None] = mapped_column(Text)
    landing_location: Mapped[str | None] = mapped_column(Text)
    takeoff_latitude: Mapped[float | None] = mapped_column(Numeric(10, 7))
    takeoff_longitude: Mapped[float | None] = mapped_column(Numeric(10, 7))
    landing_latitude: Mapped[float | None] = mapped_column(Numeric(10, 7))
    landing_longitude: Mapped[float | None] = mapped_column(Numeric(10, 7))
    max_altitude_meters: Mapped[int | None] = mapped_column(Integer)
    max_distance_meters: Mapped[int | None] = mapped_column(Integer)
    flight_path_geojson: Mapped[str | None] = mapped_column(Text)  # GeoJSON for flight path

    # Weather conditions
    weather_condition: Mapped[WeatherCondition | None] = mapped_column(
        Enum(WeatherCondition, native_enum=False, length=20),
    )
    temperature_celsius: Mapped[float | None] = mapped_column(Numeric(5, 2))
    wind_speed_mps: Mapped[float | None] = mapped_column(Numeric(5, 2))  # meters per second
    humidity_percent: Mapped[int | None] = mapped_column(Integer)

    # Battery information
    battery_start_percent: Mapped[int | None] = mapped_column(Integer)
    battery_end_percent: Mapped[int | None] = mapped_column(Integer)

    # Notes and observations
    notes: Mapped[str | None] = mapped_column(Text)
    incidents: Mapped[str | None] = mapped_column(Text)  # Any incidents or issues

    # Foreign keys
    equipment_id: Mapped[UUID] = mapped_column(
        ForeignKey("equipments.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    pilot_id: Mapped[UUID] = mapped_column(
        ForeignKey("staff.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    project_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("projects.id", ondelete="SET NULL"),
        index=True,
    )

    # Relationships
    equipment: Mapped[Equipment] = relationship(back_populates="flight_logs")
    pilot: Mapped[Staff] = relationship(back_populates="flight_logs")
    project: Mapped[Project | None] = relationship(back_populates="flight_logs")

    def __repr__(self) -> str:
        return f"FlightLog(id={self.id!r}, flight_number={self.flight_number!r})"
