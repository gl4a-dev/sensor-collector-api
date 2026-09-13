import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base


class Measurement(Base):
    __tablename__ = "measurements"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)

    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    accuracy: Mapped[float | None] = mapped_column(Float, nullable=True)
    altitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    provider: Mapped[str | None] = mapped_column(String(50), nullable=True)

    ping: Mapped[float | None] = mapped_column(Float, nullable=True)
    jitter: Mapped[float | None] = mapped_column(Float, nullable=True)
    download_mbps: Mapped[float | None] = mapped_column(Float, nullable=True)
    upload_mbps: Mapped[float | None] = mapped_column(Float, nullable=True)
    connection_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    connected_ssid: Mapped[str | None] = mapped_column(String(64), nullable=True)
    connected_bssid: Mapped[str | None] = mapped_column(String(18), nullable=True)

    noise_db: Mapped[float | None] = mapped_column(Float, nullable=True)
    noise_rms: Mapped[float | None] = mapped_column(Float, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    wifi_networks: Mapped[list["WifiNetwork"]] = relationship(
        "WifiNetwork",
        back_populates="measurement",
        cascade="all, delete-orphan",
    )


class WifiNetwork(Base):
    __tablename__ = "wifi_networks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    measurement_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("measurements.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    ssid: Mapped[str] = mapped_column(String(64), nullable=False)
    bssid: Mapped[str] = mapped_column(String(18), nullable=False, index=True)
    rssi: Mapped[int] = mapped_column(Integer, nullable=False)

    measurement: Mapped["Measurement"] = relationship(
        "Measurement", back_populates="wifi_networks"
    )