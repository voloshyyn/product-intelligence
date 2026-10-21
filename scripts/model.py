"""Shared vocabulary, URL identity and run/checklist creation. No network I/O."""
from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit
from uuid import uuid4

CATEGORIES = {
    'overview': ('Product overview and geographic markets', 'Обзор продукта и географические рынки'),
    'positioning': ('Positioning and unique value proposition', 'Позиционирование и ценностное предложение'),
    'audience': ('Target audience and jobs to be done', 'Аудитория и задачи пользователей'),
    'needs': ('User problems and needs', 'Проблемы и потребности пользователей'),
    'features': ('Features and functionality', 'Возможности и функциональность'),
    'services': ('Products and services', 'Продукты и услуги'),
    'pricing': ('Pricing plans and terms', 'Цены тарифы и условия'),
    'business': ('Business model and monetization', 'Бизнес модель и монетизация'),
    'marketing': ('Marketing and customer acquisition', 'Маркетинг и привлечение клиентов'),
    'journeys': ('Core user journeys', 'Основные пользовательские сценарии'),
    'usability': ('UX heuristics and usability', 'Эвристики UX и удобство использования'),
    'design': ('UI design system and visual consistency', 'Интерфейс дизайн система и согласованность'),
    'accessibility': ('Accessibility and responsive behavior', 'Доступность и адаптивность'),
    'trust': ('Trust privacy and reputation', 'Доверие конфиденциальность и репутация'),
    'strategy': ('Strengths weaknesses and strategic opportunities', 'Сильные и слабые стороны и возможности'),
}
STATUS = ['VERIFIED', 'PARTIALLY_VERIFIED', 'HYPOTHESIS', 'UNVERIFIED', 'NOT_ACCESSIBLE']
SHEETS = ['Overview', 'Audience & JTBD', 'Features & Services', 'Pricing & Business',
          'Marketing', 'UX & UI', 'Strengths & Weaknesses', 'Opportunities',
          'Custom Research', 'Sources', 'UX Issues', 'Research History']
CATEGORY_SHEET = dict(zip(CATEGORIES, [SHEETS[i] for i in [0,0,1,1,2,2,3,3,4,5,5,5,5,0,6]]))


def normalize_url(url: str) -> str:
    """Conservative identity: preserve meaningful path/query and regional hosts.

    HTTP and HTTPS are deliberately distinct; aliasing requires an explicit choice
    of canonical URL, never an inferred merge. Tracking parameters are not identity.
    """
    parts = urlsplit(url.strip())
    if parts.scheme.lower() not in ('http', 'https') or not parts.hostname or parts.username or parts.password:
        raise ValueError('Expected an absolute HTTP(S) URL without credentials')
    host = parts.hostname.encode('idna').decode('ascii').lower()
    port = parts.port
    if ':' in host:
        host = f'[{host}]'
    if port and (parts.scheme.lower(), port) not in (('http', 80), ('https', 443)):
        host += f':{port}'
    query = [(k, v) for k, v in parse_qsl(parts.query, keep_blank_values=True)
             if not k.lower().startswith('utm_') and k.lower() not in ('gclid', 'fbclid')]
    return urlunsplit((parts.scheme.lower(), host, parts.path.rstrip('/') or '/', urlencode(sorted(query)), ''))


def product_id(url: str, market: str = 'global') -> str:
    identity = normalize_url(url) + '\n' + market.strip().casefold()
    return 'p_' + hashlib.sha256(identity.encode()).hexdigest()[:20]


def slug(value: str) -> str:
    value = unicodedata.normalize('NFKC', value).casefold()
    clean = re.sub(r'[^\w-]+', '-', value, flags=re.UNICODE).strip('-_')[:60] or 'unspecified'
    # Avoid Windows reserved basenames even when an extension is added later.
    if clean.upper() in {'CON', 'PRN', 'AUX', 'NUL', *[f'COM{i}' for i in range(1,10)], *[f'LPT{i}' for i in range(1,10)]}:
        clean = '_' + clean
    return clean


def canonical_bytes(data: dict) -> bytes:
    return json.dumps(data, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False).encode('utf-8') + b'\n'


def digest(data: dict) -> str:
    return hashlib.sha256(canonical_bytes(data)).hexdigest()


def safe_asset(base: Path, relative: str) -> Path:
    if '\\' in relative or not relative.startswith('screenshots/') or any(part in ('.','..') for part in relative.split('/')) or ':' in relative:
        raise ValueError('Screenshots must use screenshots/<filename> paths')
    path = (base / relative).resolve()
    if not path.is_relative_to(base.resolve()) or not path.is_file():
        raise ValueError(f'Missing or unsafe screenshot: {relative}')
    return path


def new_run(urls: list[str], *, industry='unspecified', market='global', depth='standard',
            language='ru', criteria=(), started_at=None) -> dict:
    now = started_at or datetime.now(timezone.utc).isoformat()
    products = [{'product_id': product_id(u, market), 'name': urlsplit(u).hostname or u,
                 'url': normalize_url(u), 'industry': industry, 'market': market} for u in urls]
    if len({p['product_id'] for p in products}) != len(products):
        raise ValueError('Duplicate product identity in request')
    custom = [{'criterion_id': f'custom_{i+1}', 'label': c, 'question': c} for i,c in enumerate(criteria)]
    checklist = [{'product_id': p['product_id'], 'category': cat,
                  'evaluation': 'NOT_EVALUATED', 'reason': 'Research pending'}
                 for p in products for cat in CATEGORIES]
    results = [{'product_id': p['product_id'], 'criterion_id': c['criterion_id'],
                'evaluation': 'NOT_EVALUATED', 'reason': 'Research pending'} for p in products for c in custom]
    return {'schema_version': '1.0', 'run_id': str(uuid4()), 'started_at': now, 'completed_at': now,
            'mode': 'single' if len(products)==1 else 'comparison', 'depth': depth,
            'language': language, 'scope': 'Public evidence research', 'products': products,
            'custom_criteria': custom, 'coverage': checklist, 'custom_results': results,
            'claims': [], 'hypotheses': [], 'sources': [], 'screenshots': [], 'journeys': [],
            'ux_issues': [], 'opportunities': [], 'conflicts': [], 'comparisons': [],
            'summary_claim_ids': [], 'limitations': ['Research has not started'],
            'tools': {'browser_available': False, 'browser_tested': False, 'browser_name': '',
                      'reason': 'Not yet checked'}, 'plan': {'standard_categories': list(CATEGORIES),
                      'custom_criterion_ids': [c['criterion_id'] for c in custom],
                      'source_strategy': 'Official pages, independent sources, available browser journeys'}}
