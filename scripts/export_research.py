"""Validate and publish Word/Excel snapshots with locking and rollback.

The snapshot registry is the recovery authority. Filesystem replacement is atomic
per file, not across an entire multi-file transaction; --rebuild repairs Excel
after interruption between the snapshot and workbook commit.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
try:
    from .model import canonical_bytes, digest, safe_asset
    from .validate_research import load, validate, ResearchError
    from .database import storage_lock, read_snapshots, run_path, write_workbook, assert_managed_workbook, assert_projection_current
    from .report import write_report
except ImportError:
    from model import canonical_bytes, digest, safe_asset
    from validate_research import load, validate, ResearchError
    from database import storage_lock, read_snapshots, run_path, write_workbook, assert_managed_workbook, assert_projection_current
    from report import write_report


def replace(source,target):
    """Isolated for failure-injection tests; os.replace is atomic on one volume."""
    os.replace(source,target)


def manifest_for(folder):
    return {p.relative_to(folder).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(folder.rglob('*')) if p.is_file() and p.name!='manifest.json'}


def verify_bundle(folder):
    manifest=load(folder/'manifest.json')
    if manifest_for(folder)!=manifest:
        raise ResearchError(f'Run bundle changed or incomplete: {folder}')


def verify_registry(runs,root):
    seen=set()
    for data in runs:
        if data['run_id'] in seen:
            raise ResearchError('Duplicate run ID in snapshot registry')
        seen.add(data['run_id'])
        # Every bundle carries the full multi-product JSON and screenshot registry.
        for p in data['products']:
            folder=run_path(root,data,p)
            verify_bundle(folder)
            if digest(load(folder/'research.json'))!=digest(data):
                raise ResearchError('Snapshot differs from archived research.json')
        validate(data,run_path(root,data,data['products'][0]))


def export(data,root=None,asset_root=None):
    root=Path(root or Path.home()/'product-research').expanduser().resolve()
    assets=Path(asset_root or '.').resolve()
    validate(data,assets)  # No storage write before validation.
    with storage_lock(root):
        workbook=root/'competitors.xlsx'
        assert_managed_workbook(workbook)
        runs=read_snapshots(root)
        verify_registry(runs,root)
        previous=next((r for r in runs if r['run_id']==data['run_id']),None)
        paths=[run_path(root,data,p) for p in data['products']]
        if previous:
            if digest(previous)!=digest(data):
                raise ResearchError('Run ID already exists with different content; create a new run ID')
            if not workbook.is_file():
                raise ResearchError('Workbook missing; run --rebuild before re-export')
            assert_projection_current(workbook,runs)
            return {'run_id':data['run_id'],'idempotent':True,'workbook':str(workbook),
                    'reports':[str(p/'report.docx') for p in paths],
                    'research':[str(p/'research.json') for p in paths]}
        if any(p.exists() for p in paths):
            raise ResearchError('Uncommitted run directory exists; inspect interruption and recover before retrying')
        snapshots=root/'.snapshots'
        snapshots.mkdir(exist_ok=True)
        snapshot=snapshots/f'{data["run_id"]}.json'
        published=[]
        committed_snapshot=False
        with tempfile.TemporaryDirectory(prefix='.staging-',dir=root) as temporary:
            stage=Path(temporary)
            report=stage/'report.docx'
            write_report(data,report,assets)
            staged_workbook=stage/'competitors.xlsx'
            write_workbook(runs+[data],staged_workbook,root)
            staged_snapshot=stage/'snapshot.json'
            staged_snapshot.write_bytes(canonical_bytes(data))
            for i,path in enumerate(paths):
                bundle=stage/f'bundle-{i}'
                bundle.mkdir()
                shutil.copy2(report,bundle/'report.docx')
                (bundle/'research.json').write_bytes(canonical_bytes(data))
                for shot in data['screenshots']:
                    target=bundle/shot['path']
                    target.parent.mkdir(parents=True,exist_ok=True)
                    shutil.copy2(safe_asset(assets,shot['path']),target)
                (bundle/'manifest.json').write_bytes(canonical_bytes(manifest_for(bundle)))
                verify_bundle(bundle)
            try:
                for i,path in enumerate(paths):
                    path.parent.mkdir(parents=True,exist_ok=True)
                    replace(stage/f'bundle-{i}',path)
                    published.append(path)
                replace(staged_snapshot,snapshot)
                committed_snapshot=True
                # Last failure-prone mutation: previous workbook survives failures here.
                replace(staged_workbook,workbook)
            except BaseException:
                if committed_snapshot:
                    snapshot.unlink(missing_ok=True)
                for path in published:
                    shutil.rmtree(path)
                raise
        return {'run_id':data['run_id'],'idempotent':False,'workbook':str(workbook),
                'reports':[str(p/'report.docx') for p in paths],
                'research':[str(p/'research.json') for p in paths]}


def rebuild(root):
    root=Path(root).expanduser().resolve()
    with storage_lock(root):
        assert_managed_workbook(root/'competitors.xlsx')
        runs=read_snapshots(root)
        if not runs:
            raise ResearchError('No snapshots to rebuild')
        verify_registry(runs,root)
        with tempfile.TemporaryDirectory(prefix='.rebuild-',dir=root) as temporary:
            target=Path(temporary)/'competitors.xlsx'
            write_workbook(runs,target,root)
            replace(target,root/'competitors.xlsx')
    return {'workbook':str(root/'competitors.xlsx'),'runs':len(runs)}


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('research',type=Path,nargs='?')
    parser.add_argument('--root',type=Path,default=Path.home()/'product-research')
    parser.add_argument('--assets',type=Path)
    parser.add_argument('--rebuild',action='store_true')
    args=parser.parse_args()
    if (args.research is None)==(not args.rebuild):
        parser.error('Provide research.json OR --rebuild')
    try:
        result=rebuild(args.root) if args.rebuild else export(load(args.research),args.root,args.assets or args.research.parent)
        print(json.dumps(result,ensure_ascii=False,indent=2))
    except (ValueError,OSError) as exc:
        print(f'Export failed: {exc}',file=sys.stderr)
        return 2
    return 0


if __name__=='__main__':
    sys.exit(main())
