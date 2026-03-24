from enum import Enum


class SourceType(str, Enum):
    GOVERNMENT = "government"
    PRIVATE = "private"
    API = "api"
    SCRAPED = "scraped"
    PARTNER = "partner"
    OTHER = "other"


class MetricValueType(str, Enum):
    NUMERIC = "numeric"
    TEXT = "text"
    BOOLEAN = "boolean"
    JSON = "json"


class MetricFrequency(str, Enum):
    REAL_TIME = "real_time"
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"
    AD_HOC = "ad_hoc"


class LocationLevel(str, Enum):
    COUNTRY = "country"
    REGION = "region"
    CITY = "city"
    DISTRICT = "district"
    WARD = "ward"
    OTHER = "other"


class ScraperRunStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    PARTIAL = "partial"
    CANCELLED = "cancelled"
