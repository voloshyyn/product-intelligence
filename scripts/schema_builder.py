"""Maintainable schema source; regenerate references/research-schema.json after edits."""
import json
from pathlib import Path
try:
    from .model import CATEGORIES, STATUS
except ImportError:
    from model import CATEGORIES, STATUS

TEXT = {'type': 'string', 'minLength': 1, 'maxLength': 12000}
ID = {'type': 'string', 'pattern': '^[A-Za-z0-9_-]{1,100}$'}
REFS = {'type': 'array', 'items': ID, 'uniqueItems': True}
DATE = {'type': 'string', 'format': 'date'}
TIME = {'type': 'string', 'format': 'date-time'}
URL = {'type': 'string', 'format': 'uri', 'pattern': '^https?://[^\\s]+$'}


def obj(fields, optional=()):
    return {'type':'object', 'properties':fields, 'required':[k for k in fields if k not in optional], 'additionalProperties':False}


def arr(item, minimum=0):
    return {'type':'array', 'items':item, 'minItems':minimum}


def enum(*values):
    return {'enum':list(values)}


def build_schema():
    evaluation = enum('EVALUATED','NOT_APPLICABLE','NOT_EVALUATED')
    coverage = obj({'product_id':ID, 'category':enum(*CATEGORIES), 'evaluation':evaluation, 'reason':TEXT})
    custom_result = obj({'product_id':ID,'criterion_id':ID,'evaluation':evaluation,'reason':TEXT})
    claim = obj({'claim_id':ID,'product_id':ID,'category':enum(*CATEGORIES,'custom'),
                 'criterion_id':ID, 'assertion':TEXT,'status':enum(*STATUS),
                 'evidence_type':enum('official_statement','independent_report','browser_observation','screenshot','inference','none'),
                 'source_ids':REFS,'screenshot_ids':REFS,'date_checked':DATE,
                 'confidence':{'type':'number','minimum':0,'maximum':1},'notes':{'type':'string','maxLength':12000},
                 'caveat':TEXT,'company_statement':{'type':'boolean'},
                 'facet':TEXT,'value':{'type':['string','number','boolean'],'maxLength':12000},
                 'unit':TEXT,'currency':{'type':'string','pattern':'^[A-Z]{3}$'},'billing_period':TEXT,
                 'polarity':enum('strength','weakness','neutral')},
                optional=('criterion_id','caveat','facet','value','unit','currency','billing_period','polarity'))
    source = obj({'source_id':ID,'product_id':ID,'url':URL,'title':TEXT,
                  'provenance':enum('official','independent','user_report','observation'),
                  'access':enum('ACCESSED','NOT_ACCESSIBLE'), 'date_checked':DATE,
                  'excerpt':{'type':'string','maxLength':6000},'locator':TEXT,
                  'method':TEXT,'notes':{'type':'string','maxLength':12000}})
    screenshot = obj({'screenshot_id':ID,'product_id':ID,'path':TEXT,'source_url':URL,
                      'captured_at':TIME,'caption':TEXT,'viewport':TEXT,'sha256':{'type':'string','pattern':'^[a-f0-9]{64}$'}})
    step = obj({'order':{'type':'integer','minimum':1},'action':TEXT,'expected':TEXT,
                'observed':TEXT,'claim_ids':REFS})
    journey = obj({'journey_id':ID,'product_id':ID,'goal':TEXT,'method':enum('browser','desk'),
                   'tool':TEXT,'tested_at':TIME,'outcome':enum('completed','blocked','not_tested'),
                   'steps':arr(step,1),'limitations':TEXT})
    issue = obj({'issue_id':ID,'product_id':ID,'claim_id':ID,'severity':{'type':'integer','minimum':0,'maximum':4},
                 'user_goal':TEXT,'surface':TEXT,'heuristic':TEXT,'frequency_signal':TEXT,'recommendation':TEXT})
    opportunity = obj({'opportunity_id':ID,'product_id':ID,'hypothesis_id':ID,'basis_claim_ids':REFS,
                       'priority':enum('P0','P1','P2','P3'),'impact':TEXT,'effort':TEXT,'next_test':TEXT})
    comparison = obj({'comparison_id':ID,'label':TEXT,'category':enum(*CATEGORIES,'custom'),
                      'criterion_id':ID,'cells':arr(obj({'product_id':ID,'claim_id':ID}),2),'caveats':TEXT},('criterion_id',))
    fields = {'schema_version':{'const':'1.0'},'run_id':{'type':'string','format':'uuid'},
              'started_at':TIME,'completed_at':TIME,'mode':enum('single','competitor','comparison'),
              'depth':enum('quick','standard','deep'),'language':{'type':'string','pattern':'^[a-z]{2,3}(-[A-Za-z0-9]+)*$'},
              'scope':TEXT,'products':arr(obj({'product_id':ID,'name':TEXT,'url':URL,'industry':TEXT,'market':TEXT}),1),
              'custom_criteria':arr(obj({'criterion_id':ID,'label':TEXT,'question':TEXT})),
              'coverage':arr(coverage,15),'custom_results':arr(custom_result),
              'claims':arr(claim),'hypotheses':arr(claim),'sources':arr(source),'screenshots':arr(screenshot),
              'journeys':arr(journey),'ux_issues':arr(issue),'opportunities':arr(opportunity),
              'conflicts':arr(obj({'conflict_id':ID,'claim_ids':dict(REFS,minItems=2),'explanation':TEXT})),
              'comparisons':arr(comparison),'summary_claim_ids':REFS,'limitations':arr(TEXT),
              'tools':obj({'browser_available':{'type':'boolean'},'browser_tested':{'type':'boolean'},
                           'browser_name':{'type':'string'},'reason':TEXT}),
              'plan':obj({'standard_categories':arr(enum(*CATEGORIES),15),
                          'custom_criterion_ids':REFS,'source_strategy':TEXT})}
    fields['report_labels']={'type':'object','additionalProperties':TEXT}
    return {'$schema':'https://json-schema.org/draft/2020-12/schema',
            '$id':'https://product-intelligence.local/research-schema/1.0', **obj(fields,('report_labels',))}


if __name__ == '__main__':
    target = Path(__file__).resolve().parents[1] / 'references/research-schema.json'
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(build_schema(), ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
