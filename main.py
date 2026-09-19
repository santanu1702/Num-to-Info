from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from time import perf_counter
import phonenumbers
from phonenumbers import (
    geocoder,
    carrier,
    timezone,
    PhoneNumberFormat,
    NumberParseException,
)

app = FastAPI(
    title="Number Info API",
    description="Phone-number metadata API",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=["*"],
)

OWNER = "@TheRealSanatani"


def lookup_number(number: str, region: str | None = None):
    try:
        parsed = phonenumbers.parse(number, region)
    except NumberParseException:
        raise HTTPException(
            status_code=400,
            detail="Invalid phone number format"
        )

    possible = phonenumbers.is_possible_number(parsed)

    if not possible:
        raise HTTPException(
            status_code=400,
            detail="Impossible phone number"
        )

    valid = phonenumbers.is_valid_number(parsed)

    country_code = parsed.country_code
    national_number = str(parsed.national_number)

    region_code = (
        phonenumbers.region_code_for_number(parsed)
        or ""
    )

    country_name = (
        geocoder.country_name_for_number(parsed, "en")
        or ""
    )

    location = (
        geocoder.description_for_number(parsed, "en")
        or ""
    )

    carrier_name = (
        carrier.name_for_number(parsed, "en")
        or ""
    )

    zones = list(
        timezone.time_zones_for_number(parsed)
    )

    international = phonenumbers.format_number(
        parsed,
        PhoneNumberFormat.INTERNATIONAL
    )

    e164 = phonenumbers.format_number(
        parsed,
        PhoneNumberFormat.E164
    )

    return {
        "mobile": national_number,

        "name": "",
        "fname": "",
        "id": "",

        "circle": country_name,
        "address": location,

        "email": "",
        "alt": "",

        "country_code": f"+{country_code}",
        "country_iso": region_code,
        "carrier": carrier_name,
        "timezone": zones,

        "international": international,
        "e164": e164,

        "valid": valid,
        "possible": possible,
    }


@app.get("/")
async def root():
    return {
        "status": "success",
        "message": "Number Info API",
        "version": "2.0.0",
        "endpoint": "/api/number",
        "docs": "/docs",
        "owner": OWNER,
    }


@app.get("/health")
async def health():
    return {
        "status": "success",
        "message": "API is running",
    }


@app.get("/api/number")
async def number_info(
    number: str = Query(
        ...,
        description="Phone number"
    ),
    region: str | None = Query(
        None,
        description="ISO-2 region, e.g. IN"
    ),
):
    started = perf_counter()

    number = number.strip()

    if not number:
        raise HTTPException(
            status_code=400,
            detail="Number is required"
        )

    if len(number) > 40:
        raise HTTPException(
            status_code=400,
            detail="Number is too long"
        )

    result = lookup_number(
        number,
        region
    )

    elapsed = (
        perf_counter() - started
    ) * 1000

    return {
        "status": "success",
        "count": 1,
        "search_time": f"{elapsed:.2f}ms",
        "results": [
            result
        ],
        "owner": OWNER,
    }
    