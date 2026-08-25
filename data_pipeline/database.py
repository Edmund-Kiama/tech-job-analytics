from typing import Optional

from sqlalchemy import Boolean, Float, Integer, String, Text, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
import os
from dotenv import load_dotenv 

load_dotenv() 
DATABASE_URL = os.getenv("DATABASE_URL")  
engine = create_engine(
    DATABASE_URL,
    echo=True,
)


class Base(DeclarativeBase):
    pass


class Listing(Base):
    __tablename__ = "listings"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    redirect_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    salary_min: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    salary_max: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    salary_is_predicted: Mapped[Optional[bool]] = mapped_column(
        Boolean,
        nullable=True,
    )

    contract_time: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    contract_type: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    company_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    category_label: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    category_tag: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    location_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    latitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    longitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)