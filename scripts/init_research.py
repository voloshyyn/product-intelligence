"""Create a complete, explicitly unevaluated research plan from URLs and criteria."""
import argparse
import sys
from pathlib import Path
try:
    from .model import new_run, canonical_bytes
    from .validate_research import validate
except ImportError:
    from model import new_run, canonical_bytes
    from validate_research import validate


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--url',action='append',required=True)
    parser.add_argument('--industry',default='unspecified')
    parser.add_argument('--market',default='global')
    parser.add_argument('--depth',choices=('quick','standard','deep'),default='standard')
    parser.add_argument('--mode',choices=('single','competitor','comparison'))
    parser.add_argument('--language',default='ru')
    parser.add_argument('--criterion',action='append',default=[])
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    try:
        data=new_run(args.url,industry=args.industry,market=args.market,depth=args.depth,language=args.language,criteria=args.criterion)
        if args.mode:
            data['mode']=args.mode
        validate(data)
        args.output.parent.mkdir(parents=True,exist_ok=True)
        with args.output.open('xb') as stream:
            stream.write(canonical_bytes(data))
        print(args.output.resolve())
    except (ValueError,OSError) as exc:
        print(f'Initialization failed: {exc}',file=sys.stderr)
        return 2
    return 0


if __name__=='__main__':
    sys.exit(main())
