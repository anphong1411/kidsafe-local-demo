from datetime import datetime, timezone
from typing import Annotated, Literal
from zoneinfo import ZoneInfo
import re
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
import tldextract


class Strict(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Login(Strict):
    username: str = Field(min_length=1, max_length=100)
    password: str = Field(min_length=1, max_length=1024)


class Register(Strict):
    name: str = Field(min_length=1, max_length=80)
    username: str = Field(min_length=3, max_length=100, pattern=r"^[a-zA-Z0-9_.@-]+$")
    password: str = Field(min_length=10, max_length=1024)
    confirm_password: str = Field(min_length=10, max_length=1024)

    @field_validator('name', 'username', mode='before')
    @classmethod
    def trim_identity(cls, value):
        return value.strip() if isinstance(value, str) else value


class ChildInput(Strict):
    name: str = Field(min_length=1, max_length=80)


class ChildPasswordInput(Strict):
    password: str = Field(min_length=10, max_length=1024)


class ChildAccountInput(ChildPasswordInput):
    username: str = Field(min_length=3, max_length=100, pattern=r"^[\w.@-]+$")


class AllocationInput(Strict):
    device_id: str
    weekday_sec: int = Field(ge=0, le=86400)
    weekend_sec: int = Field(ge=0, le=86400)


class MoreTimeRequest(Strict):
    device_id: str | None = None
    minutes: Literal[5, 10, 15] = 15


class AppRule(Strict):
    name: str = Field(min_length=1, max_length=100, pattern=r"^[\w. -]+\.[eE][xX][eE]$")
    sha256: str = Field(pattern=r"^[a-fA-F0-9]{64}$")


AppGroupKey = Literal["study", "games", "video", "social", "blocked"]
GroupSeconds = dict[AppGroupKey, Annotated[int, Field(ge=0, le=86400)]]
DomainCategory = Literal["education", "entertainment", "social", "games", "age_inappropriate", "unclassified"]


class AppGroupWindow(Strict):
    days: list[Annotated[int, Field(ge=0, le=6)]] = Field(min_length=1, max_length=7)
    start_minute: int = Field(ge=0, lt=1440)
    end_minute: int = Field(gt=0, le=1440)

    @model_validator(mode="after")
    def valid_window(self):
        if self.start_minute >= self.end_minute or len(set(self.days)) != len(self.days):
            raise ValueError("Chọn ngày và khung giờ cùng ngày có giờ kết thúc sau giờ bắt đầu.")
        return self


class AppGroup(Strict):
    enabled: bool = True
    mode: Literal["daily", "entertainment", "custom"] = "daily"
    quota_sec: int | None = Field(default=None, ge=0, le=86400)
    window: AppGroupWindow | None = None
    apps: list[AppRule] = Field(default_factory=list, max_length=200)
    message: str = Field(default="", max_length=280)

    @model_validator(mode="after")
    def valid_quota(self):
        if (self.mode == "custom") != (self.quota_sec is not None):
            raise ValueError("Chỉ chế độ hạn mức riêng cần số phút của nhóm.")
        return self


def default_app_groups():
    return {
        "study": AppGroup(),
        "games": AppGroup(mode="entertainment"),
        "video": AppGroup(mode="entertainment"),
        "social": AppGroup(),
        "blocked": AppGroup(enabled=False),
    }


class PolicyInput(Strict):
    weekday_quota_sec: int = Field(default=7200, ge=0, le=86400)
    weekend_quota_sec: int = Field(default=7200, ge=0, le=86400)
    entertainment_quota_sec: int = Field(default=3600, ge=0, le=86400)
    entertainment_apps: list[str] = Field(default_factory=list, max_length=1000)
    timezone: str = "Asia/Ho_Chi_Minh"
    schedule: list[list[bool]] = Field(default_factory=lambda: [[True] * 48 for _ in range(7)])
    app_mode: Literal["blocklist", "allowlist"] = "blocklist"
    apps: list[AppRule] = Field(default_factory=list, max_length=1000)
    app_groups: dict[AppGroupKey, AppGroup] = Field(default_factory=default_app_groups)
    blocked_domains: list[str] = Field(default_factory=list, max_length=2000)
    blocked_categories: list[DomainCategory] = Field(default_factory=lambda: ["age_inappropriate"])
    safesearch: bool = True

    @model_validator(mode="after")
    def valid_entertainment_quota(self):
        daily_limit = min(self.weekday_quota_sec, self.weekend_quota_sec)
        if "entertainment_quota_sec" not in self.model_fields_set:
            self.entertainment_quota_sec = min(self.entertainment_quota_sec, daily_limit)
        elif self.entertainment_quota_sec > daily_limit:
            raise ValueError("Thời gian giải trí không được vượt quá tổng hạn mức dùng máy trong ngày")
        return self

    @field_validator("app_groups")
    @classmethod
    def valid_app_groups(cls, groups):
        if groups.keys() != default_app_groups().keys():
            raise ValueError("Cấu hình phải gồm đủ năm nhóm ứng dụng.")
        blocked = groups["blocked"]
        if blocked.enabled or blocked.mode != "daily" or blocked.window is not None:
            raise ValueError("Nhóm chặn tuyệt đối luôn khóa.")
        names, hashes = set(), set()
        for group in groups.values():
            for app in group.apps:
                name, digest = app.name.casefold(), app.sha256.lower()
                if name in names or digest in hashes:
                    raise ValueError("Tên và mã SHA-256 chỉ được đăng ký một lần trong các nhóm.")
                names.add(name)
                hashes.add(digest)
        return groups

    @field_validator("entertainment_apps")
    @classmethod
    def valid_entertainment_apps(cls, values):
        if any(not re.fullmatch(r"[\w. -]+\.exe", value, re.IGNORECASE) or len(value) > 100 for value in values):
            raise ValueError("Entertainment apps must be executable names, without paths")
        return sorted({value.casefold() for value in values})

    @field_validator("timezone")
    @classmethod
    def valid_timezone(cls, value):
        ZoneInfo(value)
        return value

    @field_validator("schedule")
    @classmethod
    def valid_schedule(cls, value):
        if len(value) != 7 or any(len(row) != 48 for row in value):
            raise ValueError("Schedule must contain 7 by 48 half-hour slots")
        return value

    @field_validator("blocked_domains")
    @classmethod
    def valid_domains(cls, values):
        return [domain(v) for v in values]


def domain(value):
    result = value.rstrip(".").lower().encode("idna").decode()
    if len(result) > 253 or "." not in result or not re.fullmatch(r"[a-z0-9](?:[a-z0-9.-]*[a-z0-9])?", result) or any(not part or len(part) > 63 or part.startswith("-") or part.endswith("-") for part in result.split(".")):
        raise ValueError("Expected a DNS domain, without scheme, URL, query or port")
    return result


_website_suffixes = tldextract.TLDExtract(suffix_list_urls=(), cache_dir=None, include_psl_private_domains=True)
DOMAIN_INPUT_ERROR = "Chỉ nhập tên miền (ví dụ: facebook.com), không nhập đường dẫn."


def website_domain(host):
    """Return a registrable domain from a hostname, using the bundled suffix list."""
    if host.removesuffix(".").endswith("."):
        raise ValueError(DOMAIN_INPUT_ERROR)
    normalized = domain(host)
    extracted = _website_suffixes(normalized)
    result = extracted.top_domain_under_public_suffix
    if extracted.is_private and not result:
        # A platform apex is also a valid rule when explicitly entered.
        result = _website_suffixes(normalized, include_psl_private_domains=False).top_domain_under_public_suffix
    if not result:
        raise ValueError(DOMAIN_INPUT_ERROR)
    return result


class WebCategoryChange(Strict):
    action: Literal["category"]
    category: DomainCategory
    enabled: bool


class WebSafeSearchChange(Strict):
    action: Literal["safesearch"]
    enabled: bool


class WebDomainChange(Strict):
    action: Literal["add_domain", "remove_domain"]
    host: str = Field(min_length=1, max_length=254)


WebRuleChange = Annotated[WebCategoryChange | WebSafeSearchChange | WebDomainChange, Field(discriminator="action")]


class Consent(Strict):
    consent: Literal[True]


class Enroll(Strict):
    code: str = Field(pattern=r"^[A-Z2-9]{8}$")
    fingerprint: str = Field(min_length=16, max_length=256)
    name: str = Field(min_length=1, max_length=80)

    @field_validator("code", mode="before")
    @classmethod
    def normalize_code(cls, value):
        if isinstance(value, str):
            value = value.strip().upper()
            if re.fullmatch(r"[A-Z2-9]{4}-[A-Z2-9]{4}", value):
                return value.replace("-", "")
        return value


class Refresh(Strict):
    device_id: str
    refresh_token: str = Field(max_length=256)


class EventInput(Strict):
    ts: datetime
    device_id: str
    child_id: str
    type: Literal["app_start", "app_stop", "domain_query", "blocked_app", "blocked_domain", "quota_warning", "locked", "unlock_request", "override_granted"]
    subject: str = Field(max_length=253)
    duration_sec: int = Field(ge=0, le=86400)
    policy_id: str = Field(min_length=1, max_length=100)

    @field_validator("ts")
    @classmethod
    def aware(cls, value):
        if value.tzinfo is None:
            raise ValueError("Timestamp must include timezone")
        return value.astimezone(timezone.utc)

    @field_validator("subject")
    @classmethod
    def minimum_subject(cls, value):
        if any(c in value for c in "/\\?#:@") or any(ord(c) < 32 for c in value):
            raise ValueError("Subject cannot contain a URL, path or control characters")
        return value


class EventBatch(Strict):
    events: list[EventInput] = Field(min_length=1, max_length=500)


class Heartbeat(Strict):
    device_id: str
    status: Literal["active", "locked", "idle", "tray_unavailable"]
    quota_used_sec: int = Field(ge=0, le=86400)
    policy_version: int = Field(ge=0)
    usage_date: str = Field(pattern=r"^\d{4}-\d{2}-\d{2}$")
    exception_used_sec: int = Field(default=0, ge=0, le=86400)
    entertainment_used_sec: int | None = Field(default=None, ge=0, le=86400)
    group_used_sec: GroupSeconds | None = None


class CommandInput(Strict):
    device_id: str
    type: Literal["lock", "unlock", "add_time"]


class TransferInput(Strict):
    donor_id: str
    recipient_id: str
    weekday_sec: int = Field(ge=0, le=86400)
    weekend_sec: int = Field(ge=0, le=86400)
