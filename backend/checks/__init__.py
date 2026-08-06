"""
GEO Check modules.
"""
from .base import CheckBase, CheckResult
from .robots_txt import RobotsTxtCheck
from .llms_txt import LLMsTxtCheck
from .sitemap import SitemapCheck
from .title import TitleCheck
from .meta_description import MetaDescriptionCheck
from .organization_schema import OrganizationSchemaCheck
from .faq_schema import FAQSchemaCheck
from .article_schema import ArticleSchemaCheck
from .breadcrumb_schema import BreadcrumbSchemaCheck
from .headings import HeadingsCheck
from .nap_consistency import NAPConsistencyCheck
from .freshness import FreshnessCheck

ALL_CHECKS = [
    RobotsTxtCheck(),
    LLMsTxtCheck(),
    SitemapCheck(),
    TitleCheck(),
    MetaDescriptionCheck(),
    OrganizationSchemaCheck(),
    FAQSchemaCheck(),
    ArticleSchemaCheck(),
    BreadcrumbSchemaCheck(),
    HeadingsCheck(),
    NAPConsistencyCheck(),
    FreshnessCheck(),
]
