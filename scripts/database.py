"""Immutable snapshot registry and deterministic normalized Excel projections.

JSON snapshots are authoritative. Excel is a managed projection: manual edits
are not imported. Every fact remains a row; historical rows have is_current=False.
"""
from __future__ import annotations
from contextlib import contextmanager
from datetime import datetime
import hashlib
import os
from pathlib import Path
from zipfile import BadZipFile
from openpyxl import Workbook, load_workbook
from openpyxl.utils.exceptions import InvalidFileException
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.worksheet.table import Table, TableStyleInfo
from openpyxl.utils import get_column_letter
try:
    from .model import SHEETS, CATEGORY_SHEET, slug, canonical_bytes, digest
    from .validate_research import ResearchError, load
except ImportError:
    from model import SHEETS, CATEGORY_SHEET, slug, canonical_bytes, digest
    from validate_research import ResearchError, load

MARKER='product-intelligence/schema-1.0'
EXTRA_SHEETS=['Evidence Links','Coverage','Journeys','Comparisons','Conflicts']
COMMON=['run_id','product_id','product','industry','market','completed_at','is_current']
CLAIM_COLUMNS=COMMON+['claim_id','record_type','category','criterion_id','criterion','assertion','status',
    'evidence_type','company_statement','confidence','date_checked','facet','verified_value',
    'company_reported_value','partial_value','unit','currency','billing_period','polarity','caveat','notes']
HEADERS={s:CLAIM_COLUMNS[:] for s in SHEETS[:7]}
HEADERS['Overview']+=['url','mode','depth','evaluated_categories','total_categories']
HEADERS.update({
    'Custom Research':CLAIM_COLUMNS+['research_question','evaluation','reason'],
    'Opportunities':COMMON+['opportunity_id','hypothesis_id','recommendation','priority','impact','effort','next_test'],
    'Sources':COMMON+['source_id','kind','url','title','provenance','access','date_checked','excerpt','locator','method','notes','screenshot_path','sha256','viewport'],
    'UX Issues':COMMON+['issue_id','claim_id','assertion','status','severity','user_goal','surface','heuristic','frequency_signal','recommendation'],
    'Research History':COMMON+['mode','depth','scope','language','browser_tested','limitations','report_path','research_path','content_sha256'],
    'Evidence Links':COMMON+['claim_id','reference_type','reference_id'],
    'Coverage':COMMON+['category','criterion_id','criterion','evaluation','reason'],
    'Journeys':COMMON+['journey_id','goal','method','tool','tested_at','outcome','step_order','action','expected','observed','claim_id','limitations'],
    'Comparisons':COMMON+['comparison_id','label','category','criterion_id','claim_id','caveats'],
    'Conflicts':COMMON+['conflict_id','claim_id','explanation']})


@contextmanager
def storage_lock(root: Path):
    """Fail fast; do not guess whether an existing lock belongs to a live process."""
    root.mkdir(parents=True, exist_ok=True)
    path=root/'.export.lock'
    try:
        fd=os.open(path,os.O_CREAT|os.O_EXCL|os.O_WRONLY)
    except FileExistsError as exc:
        raise ResearchError(f'Storage is locked: {path}. Check the exporting process before removing a stale lock.') from exc
    try:
        with os.fdopen(fd,'w',encoding='utf-8') as stream:
            stream.write(str(os.getpid()))
        yield
    finally:
        path.unlink(missing_ok=True)


def run_path(root, data, product):
    # Identity-derived path cannot move when display name or industry label changes.
    industry=slug(product['industry'])
    industry+='_'+hashlib.sha256(product['industry'].casefold().encode()).hexdigest()[:8]
    return Path(root)/industry/product['product_id']/f'{data["completed_at"][:10]}_{data["run_id"]}'


def read_snapshots(root):
    return [load(p) for p in sorted((Path(root)/'.snapshots').glob('*.json'))]


def assert_managed_workbook(path):
    if not Path(path).exists():
        return
    try:
        wb=load_workbook(path,read_only=True)
    except (BadZipFile,InvalidFileException,KeyError) as exc:
        raise ResearchError(f'Existing workbook is corrupt or unsupported; preserve it and restore/rebuild: {path}') from exc
    try:
        if wb.properties.identifier!=MARKER:
            raise ResearchError(f'Refusing to replace an unrelated workbook: {path}')
    finally:
        wb.close()


def registry_fingerprint(runs):
    return hashlib.sha256(canonical_bytes({d['run_id']:digest(d) for d in runs})).hexdigest()


def assert_projection_current(path,runs):
    wb=load_workbook(path,read_only=True)
    try:
        if wb.properties.keywords!='snapshots_sha256:'+registry_fingerprint(runs):
            raise ResearchError('Workbook snapshot revision is stale; run --rebuild')
    finally:
        wb.close()


def rows_for(runs, root):
    latest={}
    for d in runs:
        for p in d['products']:
            key=p['product_id']
            stamp=(datetime.fromisoformat(d['completed_at'].replace('Z','+00:00')),d['run_id'])
            if key not in latest or stamp>latest[key]:
                latest[key]=stamp
    rows={s:[] for s in HEADERS}
    for d in sorted(runs,key=lambda r:(r['completed_at'],r['run_id'])):
        products={p['product_id']:p for p in d['products']}
        criteria={c['criterion_id']:c['label'] for c in d['custom_criteria']}
        questions={c['criterion_id']:c['question'] for c in d['custom_criteria']}
        claims={c['claim_id']:c for c in d['claims']+d['hypotheses']}
        def base(pid):
            p=products[pid]
            return dict(zip(COMMON,[d['run_id'],pid,p['name'],p['industry'],p['market'],
                d['completed_at'],latest[pid]==(datetime.fromisoformat(d['completed_at'].replace('Z','+00:00')),d['run_id'])]))
        for c in claims.values():
            r={**base(c['product_id']),**{k:v for k,v in c.items() if k not in ('value','source_ids','screenshot_ids')}}
            r['record_type']='hypothesis' if c['status']=='HYPOTHESIS' else 'claim'
            r['criterion']=criteria.get(c.get('criterion_id'),'')
            r['research_question']=questions.get(c.get('criterion_id'),'')
            if 'value' in c:
                field='partial_value' if c['status']=='PARTIALLY_VERIFIED' else 'company_reported_value' if c['company_statement'] else 'verified_value'
                r[field]=c['value']
            sheet='Custom Research' if c['category']=='custom' else CATEGORY_SHEET[c['category']]
            rows[sheet].append(r)
            for kind,ids in [('source',c['source_ids']),('screenshot',c['screenshot_ids'])]:
                for ref in ids:
                    rows['Evidence Links'].append({**base(c['product_id']),'claim_id':c['claim_id'],'reference_type':kind,'reference_id':ref})
        for r in d['coverage']+d['custom_results']:
            row={**base(r['product_id']),**r,'criterion':criteria.get(r.get('criterion_id'),'')}
            rows['Coverage'].append(row)
            if 'criterion_id' in r:
                # One criterion coverage row remains present even with no accessible evidence.
                rows['Custom Research'].append({**row,'record_type':'coverage','research_question':questions[r['criterion_id']]})
        for s in d['sources']:
            rows['Sources'].append({**base(s['product_id']),**s,'kind':'source'})
        for s in d['screenshots']:
            path=run_path(root,d,products[s['product_id']])/s['path']
            rows['Sources'].append({**base(s['product_id']),'source_id':s['screenshot_id'],'kind':'screenshot',
                'url':s['source_url'],'title':s['caption'],'provenance':'observation','access':'ACCESSED',
                'date_checked':s['captured_at'][:10],'screenshot_path':str(path.resolve()),'sha256':s['sha256'],'viewport':s['viewport']})
        for issue in d['ux_issues']:
            c=claims[issue['claim_id']]
            rows['UX Issues'].append({**base(issue['product_id']),**issue,'assertion':c['assertion'],'status':c['status']})
        for o in d['opportunities']:
            rows['Opportunities'].append({**base(o['product_id']),**o,'recommendation':claims[o['hypothesis_id']]['assertion']})
            for cid in o['basis_claim_ids']:
                rows['Evidence Links'].append({**base(o['product_id']),'claim_id':o['hypothesis_id'],'reference_type':'basis_claim','reference_id':cid})
        for j in d['journeys']:
            for step in j['steps']:
                for cid in step['claim_ids'] or ['']:
                    rows['Journeys'].append({**base(j['product_id']),**j,**step,'step_order':step['order'],'claim_id':cid})
        for c in d['comparisons']:
            for cell in c['cells']:
                rows['Comparisons'].append({**base(cell['product_id']),**c,**cell})
        for c in d['conflicts']:
            for cid in c['claim_ids']:
                rows['Conflicts'].append({**base(claims[cid]['product_id']),**c,'claim_id':cid})
        for p in products.values():
            path=run_path(root,d,p)
            rows['Overview'].append({**base(p['product_id']),'record_type':'product','url':p['url'],
                'mode':d['mode'],'depth':d['depth'],'total_categories':15,
                'evaluated_categories':sum(r['product_id']==p['product_id'] and r['evaluation']=='EVALUATED' for r in d['coverage'])})
            # Limitation records are normalized: one row per limitation, one empty row if none.
            for limitation in d['limitations'] or ['']:
                rows['Research History'].append({**base(p['product_id']),'mode':d['mode'],'depth':d['depth'],
                    'scope':d['scope'],'language':d['language'],'browser_tested':d['tools']['browser_tested'],
                    'limitations':limitation,'report_path':str((path/'report.docx').resolve()),
                    'research_path':str((path/'research.json').resolve()),'content_sha256':digest(d)})
    return rows


def write_workbook(runs, target, root):
    """Write a NEW file only. Caller owns atomic publication and locking."""
    rows=rows_for(runs,root)
    wb=Workbook()
    wb.remove(wb.active)
    wb.properties.identifier=MARKER
    wb.properties.title='Product intelligence research snapshots'
    wb.properties.keywords='snapshots_sha256:'+registry_fingerprint(runs)
    for number,name in enumerate(SHEETS+EXTRA_SHEETS,1):
        ws=wb.create_sheet(name)
        headers=HEADERS[name]
        ws.append(headers)
        for record in rows[name]:
            ws.append([record.get(h) for h in headers])
        if ws.max_row>1_048_576:
            raise ResearchError(f'Excel row limit exceeded in {name}; split the research library')
        for row in ws:
            for cell in row:
                # All user/source strings are literal text, including formula-like assertions.
                if isinstance(cell.value,str):
                    cell.data_type='s'
                cell.alignment=Alignment(vertical='top',wrap_text=True)
                cell.font=Font(name='Calibri',size=11)
                if cell.row>1 and cell.value is not None:
                    header=headers[cell.column-1]
                    if header in ('date_checked',):
                        cell.value=datetime.fromisoformat(str(cell.value))
                        cell.number_format='yyyy-mm-dd'
                    if header=='confidence':
                        cell.number_format='0%'
                    if header in ('url','report_path','research_path','screenshot_path'):
                        cell.hyperlink=str(cell.value) if header=='url' else Path(str(cell.value)).as_uri()
                        cell.font=Font(name='Calibri',size=11,color='0563C1',underline='single')
        for cell in ws[1]:
            cell.fill=PatternFill('solid',fgColor='18354A')
            cell.font=Font(name='Calibri',size=11,bold=True,color='FFFFFF')
            cell.alignment=Alignment(horizontal='center',vertical='center',wrap_text=True)
        ws.freeze_panes='C2'
        ws.sheet_view.showGridLines=False
        ws.row_dimensions[1].height=44
        for i,h in enumerate(headers,1):
            ws.column_dimensions[get_column_letter(i)].width=60 if h in ('assertion','excerpt','recommendation','reason','notes','limitations') else 30 if h.endswith('_id') or h.endswith('_path') or h=='url' else 22
        # Excel does not automatically fit wrapped rows until an interactive edit.
        # Estimate line height without truncating long cells; the full value remains stored.
        import textwrap
        for row in ws.iter_rows(min_row=2):
            lines=max((sum(max(1,len(textwrap.wrap(line,width=max(8,int(ws.column_dimensions[get_column_letter(c.column)].width)-3))))
                           for line in str(c.value or '').split('\n')) for c in row),default=1)
            ws.row_dimensions[row[0].row].height=min(409,max(30,15*lines+8))
        ws.auto_filter.ref=ws.dimensions
        if ws.max_row>1:
            table=Table(displayName=f'Research{number}',ref=ws.dimensions)
            table.tableStyleInfo=TableStyleInfo(name='TableStyleMedium2',showRowStripes=True)
            ws.add_table(table)
        ws.print_title_rows='1:1'
        ws.sheet_properties.pageSetUpPr.fitToPage=True
        ws.page_setup.orientation='landscape'
        ws.page_setup.paperSize=ws.PAPERSIZE_A3
        ws.page_setup.fitToWidth=1
        ws.page_setup.fitToHeight=0
    wb.save(target)
    wb.close()
    check=load_workbook(target,read_only=True)
    try:
        if check.sheetnames!=SHEETS+EXTRA_SHEETS:
            raise ResearchError('Workbook verification failed')
    finally:
        check.close()
