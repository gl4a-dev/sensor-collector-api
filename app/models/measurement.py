import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Float, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base


class Measurement(Base):
    __tablename__ = "measurements"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)

    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    accuracy: Mapped[float | None] = mapped_column(Float, nullable=True)
    altitude: Mapped[float | None] = mapped_column(Float, nullable=True)

    connection_type: Mapped[str] = mapped_column(String(20), nullable=False)  # 'wifi', 'mobile', 'none'
    has_internet: Mapped[bool] = mapped_column(Boolean, default=False)

    ping: Mapped[float | None] = mapped_column(Float, nullable=True)
    jitter: Mapped[float | None] = mapped_column(Float, nullable=True)
    ping_success_rate: Mapped[float | None] = mapped_column(Float, nullable=True)
    download_mbps: Mapped[float | None] = mapped_column(Float, nullable=True)
    upload_mbps: Mapped[float | None] = mapped_column(Float, nullable=True)
    test_success: Mapped[bool | None] = mapped_column(Boolean, nullable=True)

    noise_db: Mapped[float | None] = mapped_column(Float, nullable=True)
    noise_rms: Mapped[float | None] = mapped_column(Float, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    wifi_connection: Mapped["WifiConnection | None"] = relationship(
        "WifiConnection", back_populates="measurement", uselist=False, cascade="all, delete-orphan"
    )
    mobile_connection: Mapped["MobileConnection | None"] = relationship(
        "MobileConnection", back_populates="measurement", uselist=False, cascade="all, delete-orphan"
    )
    wifi_scans: Mapped[list["WifiScan"]] = relationship(
        "WifiScan", back_populates="measurement", cascade="all, delete-orphan"
    )


class WifiConnection(Base):
    __tablename__ = "wifi_connections"

    measurement_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("measurements.id", ondelete="CASCADE"),
        primary_key=True,
    )
    connected_ssid: Mapped[str | None] = mapped_column(String(64), nullable=True)
    connected_bssid: Mapped[str | None] = mapped_column(String(18), nullable=True, index=True)

    measurement: Mapped["Measurement"] = relationship("Measurement", back_populates="wifi_connection")


class MobileConnection(Base):
    __tablename__ = "mobile_connections"

    measurement_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("measurements.id", ondelete="CASCADE"),
        primary_key=True,
    )
    mobile_operator: Mapped[str | None] = mapped_column(String(50), nullable=True)
    mobile_country_code: Mapped[str | None] = mapped_column(String(10), nullable=True)
    mobile_network_code: Mapped[str | None] = mapped_column(String(10), nullable=True)

    measurement: Mapped["Measurement"] = relationship("Measurement", back_populates="mobile_connection")


class WifiScan(Base):
    __tablename__ = "wifi_scans"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    measurement_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("measurements.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    bssid: Mapped[str] = mapped_column(String(18), nullable=False, index=True)
    rssi: Mapped[int] = mapped_column(Integer, nullable=False)

    measurement: Mapped["Measurement"] = relationship("Measurement", back_populates="wifi_scans")