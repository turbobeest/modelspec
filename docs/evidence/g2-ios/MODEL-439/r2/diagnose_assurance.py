"""Diagnostic assurance comparison only. Does not create deploy exports."""
import argparse
from collections import Counter
from datetime import date
import json
import logging
import os
from pathlib import Path
import sys


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--code',type=Path,required=True)
    parser.add_argument('--data-dir',type=Path,required=True)
    parser.add_argument('--baseline-state',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--diagnostic-state-output',type=Path)
    args=parser.parse_args()
    args.output.mkdir(parents=True,exist_ok=True)
    sys.path.insert(0,str(args.code.resolve()))
    os.environ.pop('MODELSPEC_SOURCE_CACHE',None)
    logging.basicConfig(filename=args.output/'build.private.log',level=logging.WARNING,force=True)
    from pipeline.data_source import overlay
    from decision import registry, snapshot
    from decision.excluded import excluded_sources
    root=args.output/'private-overlay'
    if not root.exists():overlay(args.code,args.data_dir,root)
    registry.use_root(root)
    inputs=snapshot.collect_repo(root)
    premier=snapshot.load_premier(root/'premier/slice-1.yaml')
    before=json.loads(args.baseline_state.read_text())
    public={};private={}
    for period,state in before.items():
        day=date.fromisoformat(state['as_of'])
        print(f'{period}: diagnostic audit_build for {day}; no deploy export',flush=True)
        audit=snapshot.audit_build(inputs,registry=registry.default(),premier=premier,as_of=day,guard=excluded_sources())
        if args.diagnostic_state_output:
            filename='snapshot.json.gz' if period=='current' else 'snapshot-successor.json.gz'
            destination=args.diagnostic_state_output/'exports'/'decision'/filename
            audit.snapshot.write(destination,key='model439-private-proof-throwaway-key',ed25519_signer=None)
        content=audit.snapshot.content
        facts={rid for rows in content['fact_records'].values() for rid in rows.values()}
        assurance={}
        for rid in sorted(facts):
            record=snapshot._unpack_record(content['record_table'],rid)
            citation=record.get('citation') or {}
            verification=record.get('verification') or {}
            assurance[rid]=('cited' if citation.get('status')=='cited' else 'verified' if verification.get('outcome')=='verified' else 'other')
        original=state['private_fact_assurance']
        changes=[{'record_id':rid,'before':original.get(rid,'not_admitted'),'after':assurance.get(rid,'not_admitted')} for rid in sorted(original.keys()|assurance.keys()) if original.get(rid,'not_admitted')!=assurance.get(rid,'not_admitted')]
        transitions=Counter(change['before']+'_to_'+change['after'] for change in changes)
        downgraded=[change for change in changes if change['before']=='verified' and change['after']=='cited']
        public[period]={'diagnostic_only':True,'deploy_export_accepted':False,'as_of':str(day),'gap_count':len(audit.gaps),'gap_facets':dict(Counter(g.facet for g in audit.gaps)),'fact_assurance_counts':dict(Counter(assurance.values())),'fact_assurance_changes':len(changes),'verified_to_cited_changes':len(downgraded),'verified_to_cited_by_facet':dict(Counter(change['record_id'].rsplit('#',1)[-1] for change in downgraded)),'fact_assurance_transitions':dict(transitions)}
        private[period]={'assurance':assurance,'changes':changes}
        print(json.dumps(public[period],sort_keys=True),flush=True)
    (args.output/'assurance.private.json').write_text(json.dumps(private,indent=2)+'\n')
    (args.output/'assurance.public.json').write_text(json.dumps(public,indent=2)+'\n')
    return 0

if __name__=='__main__':raise SystemExit(main())
