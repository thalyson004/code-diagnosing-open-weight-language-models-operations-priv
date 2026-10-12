"""Generate six-model tables with uniform derived failure labels."""
import argparse
import json
import sys
from pathlib import Path
import table_core as base

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT / "analysis"))
from normalize_outcomes import MODELS, normalize

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--journal",type=Path,default=ROOT/"artifacts/journal")
    parser.add_argument("--output-dir",type=Path,default=ROOT/"analysis/generated/manuscript")
    args=parser.parse_args()
    base.MODELS=MODELS
    records,digest=base.load_records(args.journal)
    base.validate(records)
    normalized=[normalize(r) for r in records]
    report={"selected_records_sha256":digest,"selected_models":list(MODELS),"selected_observations":len(records),
        "classification_version":"uniform-failure-labels-v1","objective_scores_changed":0,
        "reclassified":sum(a["terminal_outcome"]!=b["terminal_outcome"] for a,b in zip(records,normalized)),
        "cells":base.summarize(normalized),"observable_mechanisms":base.observable_mechanisms(normalized),
        "shot_pairs":base.paired(normalized,"shot_condition","zero_shot","few_shot"),
        "pipeline_pairs":base.paired(normalized,"pipeline","direct","code")+base.paired(normalized,"pipeline","code","formulation_code")}
    args.output_dir.mkdir(parents=True,exist_ok=True)
    (args.output_dir/"six_model_audit.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    base.write_latex_tables(report,args.output_dir)
    base.write_paired_contrasts(report,args.output_dir)
    print(json.dumps({"observations":len(records),"reclassified":report["reclassified"],"objective_scores_changed":0}))

if __name__=="__main__":
    main()
