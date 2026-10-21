"""Retain inspectable synthetic DOCX/XLSX artifacts inside tests/artifacts only."""
import json
from pathlib import Path
from scripts.export_research import export
from tests.fixtures import fixture


if __name__=='__main__':
    base=Path(__file__).resolve().parent/'artifacts'
    data=fixture(base/'input')
    # Fixed run identity makes repeated generation idempotent and reviewable.
    data['run_id']='00000000-0000-4000-8000-000000000001'
    result=export(data,base/'storage',base/'input')
    (base/'outputs.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,ensure_ascii=True,indent=2))
