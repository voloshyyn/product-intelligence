"""Structural and relational evidence validation, including local asset integrity."""
from __future__ import annotations
import argparse
import hashlib
import json
import math
import sys
from datetime import date, datetime, timezone
from pathlib import Path
from uuid import UUID
from jsonschema import Draft202012Validator, FormatChecker
from docx.image.image import Image
from docx.image.exceptions import UnrecognizedImageError, UnexpectedEndOfFileError, InvalidImageStreamError
try:
    from .model import CATEGORIES, normalize_url, product_id, safe_asset
except ImportError:
    from model import CATEGORIES, normalize_url, product_id, safe_asset


class ResearchError(ValueError):
    """Actionable invalid input; exporting must not mutate storage."""


# These critical formats cannot depend on jsonschema's optional format extras.
FORMATS=FormatChecker()
@FORMATS.checks('date-time', raises=(ValueError,TypeError))
def valid_time(value):
    if not isinstance(value,str):
        return True
    stamp=datetime.fromisoformat(value.replace('Z','+00:00'))
    return 'T' in value.upper() and stamp.tzinfo is not None

@FORMATS.checks('uuid', raises=(ValueError,TypeError,AttributeError))
def valid_uuid(value):
    if not isinstance(value,str):
        return True
    # Canonical lowercase avoids case-insensitive filesystem collisions on Windows.
    return str(UUID(value))==value

@FORMATS.checks('uri', raises=(ValueError,TypeError))
def valid_uri(value):
    if not isinstance(value,str):
        return True
    normalize_url(value)
    return True


def load(path):
    def pairs(items):
        result = {}
        for k,v in items:
            if k in result:
                raise ResearchError(f'Duplicate JSON key: {k}')
            result[k] = v
        return result
    with Path(path).open(encoding='utf-8-sig') as stream:
        return json.load(stream, object_pairs_hook=pairs,
                         parse_constant=lambda x: (_ for _ in ()).throw(ResearchError(f'Nonfinite number {x}')))


def validate(data, asset_root=None):
    schema = load(Path(__file__).resolve().parents[1] / 'references/research-schema.json')
    errors = sorted(Draft202012Validator(schema, format_checker=FORMATS).iter_errors(data), key=lambda e:str(list(e.path)))
    if errors:
        raise ResearchError('\n'.join(f'{"/".join(map(str,e.path)) or "$"}: {e.message}' for e in errors[:30]))
    def require(ok, message):
        if not ok:
            raise ResearchError(message)
    def finite_tree(value):
        if isinstance(value,float):
            require(math.isfinite(value),'Nonfinite number in research')
        elif isinstance(value,dict):
            for child in value.values(): finite_tree(child)
        elif isinstance(value,list):
            for child in value: finite_tree(child)
    finite_tree(data)
    def index(records, key):
        result = {r[key]:r for r in records}
        require(len(result)==len(records), f'Duplicate {key}')
        return result
    products = index(data['products'],'product_id')
    criteria = index(data['custom_criteria'],'criterion_id')
    sources = index(data['sources'],'source_id')
    shots = index(data['screenshots'],'screenshot_id')
    factual = index(data['claims'],'claim_id')
    hypotheses = index(data['hypotheses'],'claim_id')
    require(not factual.keys() & hypotheses.keys(), 'Claim IDs overlap factual and hypothesis collections')
    claims = {**factual, **hypotheses}
    started = datetime.fromisoformat(data['started_at'].replace('Z','+00:00'))
    completed = datetime.fromisoformat(data['completed_at'].replace('Z','+00:00'))
    require(started <= completed <= datetime.now(timezone.utc), 'Invalid run time range or future completion time')
    for p in products.values():
        require(p['product_id']==product_id(p['url'],p['market']), 'Product identity must match normalized URL and market')
        require(p['url']==normalize_url(p['url']), 'Product URL must be canonicalized by normalize_url')
    require(data['mode']!='single' or len(products)==1, 'single mode requires one product')
    require(data['mode']!='comparison' or len(products)>=2, 'comparison mode requires multiple products')
    for records, key in [(data['journeys'],'journey_id'),(data['ux_issues'],'issue_id'),(data['opportunities'],'opportunity_id'),(data['conflicts'],'conflict_id'),(data['comparisons'],'comparison_id')]:
        index(records,key)
    for records in [data['sources'],data['screenshots'],data['claims'],data['hypotheses'],data['journeys'],data['ux_issues'],data['opportunities']]:
        for r in records:
            require(r['product_id'] in products, f'Unknown product_id in {r}')
    def claim_refs(ids, pid=None, allow_hypothesis=True):
        for cid in ids:
            require(cid in claims, f'Unknown claim reference {cid}')
            require(pid is None or claims[cid]['product_id']==pid, f'Cross-product claim reference {cid}')
            require(allow_hypothesis or cid in factual, f'Hypothesis cannot populate factual field {cid}')
    for s in sources.values():
        require(started.date()<=date.fromisoformat(s['date_checked'])<=completed.date(), 'Source date outside this run; recheck stale evidence')
        normalize_url(s['url'])
        require(s['access']!='ACCESSED' or bool(s['excerpt'].strip()), f'Accessed source {s["source_id"]} needs a supporting excerpt/observation')
    require(len({s['path'].casefold() for s in shots.values()})==len(shots),'Duplicate screenshot paths')
    for s in shots.values():
        require(started<=datetime.fromisoformat(s['captured_at'].replace('Z','+00:00'))<=completed, 'Screenshot capture outside run time range')
        if asset_root is None:
            raise ResearchError('Provide --assets to verify screenshots')
        path = safe_asset(Path(asset_root),s['path'])
        require(hashlib.sha256(path.read_bytes()).hexdigest()==s['sha256'], f'Screenshot hash mismatch: {s["path"]}')
        try:
            image=Image.from_file(str(path))
            require(image.px_width>0 and image.px_height>0, 'Screenshot dimensions must be positive')
        except (UnrecognizedImageError,UnexpectedEndOfFileError,InvalidImageStreamError) as exc:
            raise ResearchError(f'Unsupported or damaged screenshot image: {s["path"]}') from exc
    for c in claims.values():
        cid = c['claim_id']
        require((cid in hypotheses)==(c['status']=='HYPOTHESIS'), f'{cid}: HYPOTHESIS must be in hypotheses only')
        require(started.date()<=date.fromisoformat(c['date_checked'])<=completed.date(), f'{cid}: evidence date outside current run')
        require(c['category']!='custom' or c.get('criterion_id') in criteria, f'{cid}: missing custom criterion')
        require(c['category']=='custom' or 'criterion_id' not in c, f'{cid}: criterion_id only belongs to custom claims')
        for sid in c['source_ids']:
            require(sid in sources and sources[sid]['product_id']==c['product_id'], f'{cid}: missing or cross-product source {sid}')
        for sid in c['screenshot_ids']:
            require(sid in shots and shots[sid]['product_id']==c['product_id'], f'{cid}: missing or cross-product screenshot {sid}')
        official = any(sources[s]['provenance']=='official' for s in c['source_ids'])
        if official or c['evidence_type']=='official_statement':
            require(c['company_statement'], f'{cid}: official evidence must be labeled company_statement')
        if c['status']=='VERIFIED':
            require(c['evidence_type'] not in ('none','inference'), f'{cid}: inappropriate VERIFIED evidence type')
            require(c['source_ids'] or c['screenshot_ids'], f'{cid}: VERIFIED needs evidence references')
            require(all(sources[s]['access']=='ACCESSED' for s in c['source_ids']), f'{cid}: inaccessible source cannot verify a claim')
            if c['evidence_type'] in ('official_statement','independent_report'):
                require(bool(c['source_ids']), f'{cid}: documentary evidence requires a source')
            if c['evidence_type']=='official_statement':
                require(official, f'{cid}: no official source')
            if c['evidence_type']=='independent_report':
                require(any(sources[s]['provenance'] in ('independent','user_report') for s in c['source_ids']), f'{cid}: no independent source')
            if c['evidence_type']=='screenshot':
                require(bool(c['screenshot_ids']), f'{cid}: screenshot evidence missing')
        if c['status']=='PARTIALLY_VERIFIED':
            require(bool(c.get('caveat','').strip()), f'{cid}: PARTIALLY_VERIFIED requires explicit caveat')
            require(c['source_ids'] or c['screenshot_ids'], f'{cid}: partial verification needs evidence')
            require(c['screenshot_ids'] or any(sources[s]['access']=='ACCESSED' for s in c['source_ids']), f'{cid}: no accessible evidence for partial verification')
        if c['status'] in ('UNVERIFIED','NOT_ACCESSIBLE','HYPOTHESIS'):
            require('value' not in c, f'{cid}: unverified/hypothesis cannot populate factual value')
        if 'value' in c:
            require('facet' in c, f'{cid}: structured value requires a facet')
        if c['evidence_type']=='browser_observation':
            require(data['tools']['browser_tested'], f'{cid}: browser observation without browser testing')
    def check_coverage(records, key, expected):
        pairs = [(r['product_id'],r[key]) for r in records]
        require(len(set(pairs))==len(pairs) and set(pairs)==expected, f'Incomplete or duplicate {key} coverage')
        for r in records:
            related = [c for c in claims.values() if c['product_id']==r['product_id'] and
                       (c['category']==r[key] if key=='category' else c.get('criterion_id')==r[key])]
            require(r['evaluation']!='EVALUATED' or bool(related), f'EVALUATED {r[key]} has no finding')
            require(r['evaluation']!='NOT_APPLICABLE' or not related, f'NOT_APPLICABLE {r[key]} has findings')
    check_coverage(data['coverage'],'category',{(p,c) for p in products for c in CATEGORIES})
    check_coverage(data['custom_results'],'criterion_id',{(p,c) for p in products for c in criteria})
    require(set(data['plan']['standard_categories'])==set(CATEGORIES) and len(data['plan']['standard_categories'])==15, 'Plan must cover all 15 categories')
    require(set(data['plan']['custom_criterion_ids'])==set(criteria), 'Plan omits custom criteria')
    require(not any('pending' in r['reason'].lower() for r in data['coverage']+data['custom_results']) or data['limitations'], 'Pending research requires limitations')
    claim_refs(data['summary_claim_ids'], allow_hypothesis=False)
    for cid in data['summary_claim_ids']:
        require(claims[cid]['status'] in ('VERIFIED','PARTIALLY_VERIFIED'), 'Executive summary must reference supported claims only')
    tools=data['tools']
    tested=[j for j in data['journeys'] if j['method']=='browser' and j['outcome']!='not_tested']
    require(not tools['browser_tested'] or (tools['browser_available'] and tools['browser_name'].strip() and tested), 'Browser testing flag needs available tool and recorded journey')
    require(tools['browser_tested'] or not tested, 'Recorded browser journey but browser_tested is false')
    for j in data['journeys']:
        require(len({s['order'] for s in j['steps']})==len(j['steps']), 'Duplicate journey step order')
        require(started<=datetime.fromisoformat(j['tested_at'].replace('Z','+00:00'))<=completed, 'Journey test outside run time range')
        for step in j['steps']:
            claim_refs(step['claim_ids'],j['product_id'],False)
            require(j['method']!='browser' or j['outcome']=='not_tested' or bool(step['claim_ids']), 'Browser steps need observation claims')
            if j['method']=='browser' and j['outcome']!='not_tested':
                require(j['tool'].strip() and all(claims[c]['evidence_type'] in ('browser_observation','screenshot') and claims[c]['status'] in ('VERIFIED','PARTIALLY_VERIFIED') for c in step['claim_ids']), 'Browser journey needs supported observation evidence')
    for issue in data['ux_issues']:
        claim_refs([issue['claim_id']],issue['product_id'])
    for o in data['opportunities']:
        require(o['hypothesis_id'] in hypotheses, 'Opportunity needs a separated hypothesis')
        claim_refs([o['hypothesis_id']],o['product_id'])
        claim_refs(o['basis_claim_ids'],o['product_id'],False)
    conflicted=set()
    for conflict in data['conflicts']:
        claim_refs(conflict['claim_ids'],allow_hypothesis=False)
        conflicted.update(conflict['claim_ids'])
    for cid in conflicted:
        require(claims[cid]['status']!='VERIFIED' and claims[cid].get('caveat'), 'Conflicting claims require non-VERIFIED status and explicit caveats')
    for comp in data['comparisons']:
        require(len({c['product_id'] for c in comp['cells']})==len(comp['cells']), 'Duplicate comparison product')
        require(comp['category']!='custom' or comp.get('criterion_id') in criteria, 'Custom comparison criterion missing')
        for cell in comp['cells']:
            claim_refs([cell['claim_id']],cell['product_id'],False)
            c=claims[cell['claim_id']]
            require(c['category']==comp['category'], 'Comparison category mismatch')
            require(comp['category']!='custom' or c.get('criterion_id')==comp['criterion_id'], 'Comparison criterion mismatch')
    return data


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('research', type=Path)
    parser.add_argument('--assets',type=Path,help='Directory containing screenshots/; defaults to JSON directory')
    args=parser.parse_args()
    try:
        data=validate(load(args.research),args.assets or args.research.parent)
        print(f'VALID {data["run_id"]}: {len(data["products"])} products')
    except (ValueError,OSError) as exc:
        print(f'Validation failed: {exc}',file=sys.stderr)
        return 2
    return 0


if __name__=='__main__':
    sys.exit(main())
