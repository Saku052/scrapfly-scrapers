from cerberus import Validator
import pytest
import yelp
import pprint

pp = pprint.PrettyPrinter(indent=4)

# enable scrapfly cache
yelp.BASE_CONFIG["cache"] = True


def validate_or_fail(item, validator):
    if not validator.validate(item):
        pp.pformat(item)
        pytest.fail(
            f"Validation failed for item: {pp.pformat(item)}\nErrors: {validator.errors}"
        )


page_schema = {
    "name": {"type": "string"},
    "website": {"type": "string"},
    "phone": {"type": "string"},
    "address": {"type": "string"},
}

review_schema = {
    "id": {"type": "string"},
    "userId": {"type": "string"},
    "business": {
        "type": "dict",
        "schema": {
            "id": {"type": "string"},
            "alias": {"type": "string"},
            "name": {"type": "string"},
            "photoSrc": {"type": "string"},
        },
    },
    "user": {
        "type": "dict",
        "schema": {
            "link": {"type": "string"},
            "src": {"type": "string"},
            "srcSet": {"type": "string", "nullable": True},
            "displayLocation": {"type": "string"},
            "altText": {"type": "string"},
            "userUrl": {"type": "string"},
        },
    },
    "comment": {
        "type": "dict",
        "schema": {
            "text": {"type": "string"},
            "language": {"type": "string"},
        },
    },
}

search_schema = {
    "bizId": {"type": "string"},
    "searchResultBusiness": {
        "type": "dict",
        "schema": {
            "name": {"type": "string"},
            "rating": {"type": "float", "nullable": True},
            "reviewCount": {"type": "integer", "nullable": True},
            "phone": {"type": "string", "nullable": True},
            "businessAttributes": {
                "type": "dict",
                "schema": {
                    "licenses": {
                        "type": "list",
                        "schema": {
                            "type": "dict",
                            "schema": {
                                "license_number": {"type": "string"},
                                "license_expiration_date": {"type": "string", "nullable": True},
                                "license_verification_url": {"type": "string"},
                                "license_verification_status": {"type": "string"},
                                "license_verification_date": {"type": "string"},
                                "license_issuing_authority": {"type": "string"},
                                "license_type": {"type": "string"},
                                "license_source": {"type": "string"},
                            },
                        },
                    }
                },
            },
            "alias": {"type": "string"},
        },
    },
}


@pytest.mark.asyncio
async def test_review_scraping():
    reviews_data = await yelp.scrape_reviews(
        url="https://www.yelp.com/biz/vons-1000-spirits-seattle-4",
        # each 10 reviews represent a review page (one request)
        max_reviews=28,
    )
    validator = Validator(review_schema, allow_unknown=True)
    for item in reviews_data:
        validate_or_fail(item, validator)
        assert len(reviews_data) >= 10


@pytest.mark.asyncio
async def test_page_scraping():
    business_data = await yelp.scrape_pages(
        urls=[
            "https://www.yelp.com/biz/vons-1000-spirits-seattle-4",
            "https://www.yelp.com/biz/ihop-seattle-4",
            "https://www.yelp.com/biz/toulouse-petit-kitchen-and-lounge-seattle",
        ]
    )
    validator = Validator(page_schema, allow_unknown=True)
    for item in business_data:
        validate_or_fail(item, validator)
        assert len(business_data) >= 1

import json
@pytest.mark.asyncio
async def test_search_scraping():
    search_data = await yelp.scrape_search(
        keyword="plumbers", location="Seattle, WA", max_pages=2
    )
    validator = Validator(search_schema, allow_unknown=True)
    for item in search_data:
        validate_or_fail(item, validator)
        assert len(search_data) >= 10
