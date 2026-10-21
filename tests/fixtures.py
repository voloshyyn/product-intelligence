"""Synthetic research with reserved .example domains and local generated images."""
from copy import deepcopy
import hashlib
from pathlib import Path
import struct
import zlib
from scripts.model import new_run

START='2026-01-15T09:00:00+00:00'
END='2026-01-15T10:00:00+00:00'


def fixture(assets: Path, multiple=True, language='ru'):
    data=new_run(['https://alpha.example/']+(['https://beta.example/'] if multiple else []),
                 industry='Retail',market='UA',language=language,
                 criteria=['Data portability','Support response evidence'],started_at=START)
    data['completed_at']=END
    data['scope']='SYNTHETIC TEST ONLY — export contract demonstration'
    data['limitations']=['SYNTHETIC TEST ONLY. No real product or browser was researched.']
    data['tools']={'browser_available':True,'browser_tested':True,'browser_name':'synthetic-browser-fixture',
                   'reason':'Synthetic browser records exercise validation; no actual browser session occurred.'}
    p=data['products'][0]['product_id']
    data['products'][0]['name']='Synthetic Alpha'
    if multiple:
        data['products'][1]['industry']='Education'
        data['products'][1]['name']='Synthetic Beta'
    source={'source_id':'src_a','product_id':p,'url':'https://alpha.example/plans','title':'Synthetic plan statement',
            'provenance':'official','access':'ACCESSED','date_checked':'2026-01-15','excerpt':'Synthetic plan costs 12 test currency units.',
            'locator':'Synthetic fixture section','method':'synthetic test fixture','notes':'Not real research'}
    data['sources']=[source]
    def claim(cid,cat,assertion,status='VERIFIED',**extra):
        return {'claim_id':cid,'product_id':p,'category':cat,'assertion':assertion,'status':status,
                'evidence_type':'official_statement','source_ids':['src_a'],'screenshot_ids':[],
                'date_checked':'2026-01-15','confidence':.8,'notes':'Synthetic fixture only','company_statement':True,**extra}
    data['claims']=[claim('price_a','pricing','Компания сообщает тестовую цену 12 единиц.',facet='plan_price',value=12,currency='USD',unit='seat',billing_period='month'),
                    claim('custom_a','custom','Тестовый источник сообщает о функции экспорта.',criterion_id='custom_1'),
                    claim('unknown_a','custom','Скорость ответа поддержки не установлена.',status='UNVERIFIED',criterion_id='custom_2',evidence_type='none',source_ids=[],company_statement=False)]
    # Generated PNG is deliberately synthetic, never a purported screenshot of a real site.
    path=assets/'screenshots/fixture.png'
    path.parent.mkdir(parents=True,exist_ok=True)
    def chunk(kind,content):
        return struct.pack('!I',len(content))+kind+content+struct.pack('!I',zlib.crc32(kind+content)&0xffffffff)
    width,height=640,160
    pixels=b''.join(b'\x00'+bytes((24,53,74))*width for _ in range(height))
    path.write_bytes(b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('!2I5B',width,height,8,2,0,0,0))+chunk(b'IDAT',zlib.compress(pixels))+chunk(b'IEND',b''))
    data['screenshots']=[{'screenshot_id':'shot_a','product_id':p,'path':'screenshots/fixture.png',
                        'source_url':'https://alpha.example/','captured_at':'2026-01-15T09:30:00+00:00',
                        'caption':'SYNTHETIC IMAGE — no real browser capture','viewport':'640 x 160 desktop test',
                        'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}]
    data['claims'].append(claim('ux_a','usability','Синтетическое наблюдение о недоступной метке поля.',
        evidence_type='browser_observation',source_ids=[],screenshot_ids=['shot_a'],company_statement=False))
    data['claims'].append(claim('feature_a','features','Synthetic optional feature',status='PARTIALLY_VERIFIED',caveat='Only vendor documentation was available.'))
    data['hypotheses']=[claim('hyp_a','strategy','Тестирование явной метки может уменьшить число ошибок.',status='HYPOTHESIS',evidence_type='inference',source_ids=[],company_statement=False)]
    evaluated={c['category'] for c in data['claims']+data['hypotheses'] if c['category']!='custom'}
    for c in data['coverage']:
        c.update(evaluation='EVALUATED' if c['product_id']==p and c['category'] in evaluated else 'NOT_EVALUATED',
                 reason='Synthetic fixture coverage; no real product evaluated')
    for c in data['custom_results']:
        c.update(evaluation='EVALUATED' if c['product_id']==p else 'NOT_EVALUATED',reason='Synthetic criterion coverage')
    data['journeys']=[{'journey_id':'journey_a','product_id':p,'goal':'Synthetic form journey','method':'browser',
        'tool':'synthetic-browser-fixture','tested_at':'2026-01-15T09:30:00+00:00','outcome':'blocked',
        'steps':[{'order':1,'action':'Synthetic inspect','expected':'Visible field label','observed':'Synthetic missing label','claim_ids':['ux_a']}],
        'limitations':'Synthetic only; no real testing'}]
    data['ux_issues']=[{'issue_id':'issue_a','product_id':p,'claim_id':'ux_a','severity':2,'user_goal':'Complete a form',
        'surface':'Synthetic form','heuristic':'Recognition rather than recall','frequency_signal':'One synthetic scenario; prevalence unknown',
        'recommendation':'Test an explicit label'}]
    data['opportunities']=[{'opportunity_id':'opp_a','product_id':p,'hypothesis_id':'hyp_a','basis_claim_ids':['ux_a'],
        'priority':'P1','impact':'Unknown; test required','effort':'Small assumed effort','next_test':'Task-based usability test'}]
    data['summary_claim_ids']=['price_a','ux_a']
    if multiple:
        q=data['products'][1]['product_id']
        b=deepcopy(source); b.update(source_id='src_b',product_id=q,url='https://beta.example/plans',excerpt='Synthetic plan costs 24 test currency units.')
        data['sources'].append(b)
        c=claim('price_b','pricing','Synthetic Beta company reports 24 units.',product_id=q,source_ids=['src_b'],facet='plan_price',value=24,currency='USD',unit='seat',billing_period='month')
        data['claims'].append(c)
        for cov in data['coverage']:
            if cov['product_id']==q and cov['category']=='pricing': cov['evaluation']='EVALUATED'
        data['comparisons']=[{'comparison_id':'compare_price','label':'Synthetic monthly seat price','category':'pricing',
            'cells':[{'product_id':p,'claim_id':'price_a'},{'product_id':q,'claim_id':'price_b'}],
            'caveats':'Synthetic amounts only. Packaging and taxes are not comparable without more evidence.'}]
    return data
