"""Check publication assets against the versioned prompts and analysis outputs."""
import argparse
import subprocess
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"src"))
from or_small_models.prompts import appendix_prompt_documents

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manuscript",type=Path)
    args=parser.parse_args()
    manuscript=args.manuscript.resolve(strict=True)
    root_files={"itor-generic-template.tex","itor.cls","itor.bst","itor.bib","guide.pdf","README.md",".gitignore",".gitattributes"}
    directories={"sections","tables","figures","appendix"}
    inventory=subprocess.check_output(["git","ls-files","--cached","--others","--exclude-standard"],cwd=manuscript,text=True).splitlines()
    for name in inventory:
        path=manuscript/name
        if not path.is_file():
            continue
        parts=Path(name).parts
        if name not in root_files and (len(parts)<2 or parts[0] not in directories or path.suffix not in {".tex",".txt",".pdf",".svg",".md"}):
            raise ValueError("Non-publication file in manuscript: "+name)
    for name,expected in appendix_prompt_documents().items():
        if (manuscript/"appendix/prompts"/name).read_text(encoding="utf-8") != expected.rstrip()+"\n":
            raise ValueError("Prompt mismatch: "+name)
    for generated in (ROOT/"analysis/generated/manuscript").glob("*.tex"):
        if (manuscript/"tables"/generated.name).read_bytes()!=generated.read_bytes():
            raise ValueError("Table differs from generated rates: "+generated.name)
    for generated in (ROOT/"analysis/generated/casebook").glob("*.txt"):
        if (manuscript/"appendix/casebook"/generated.name).read_bytes()!=generated.read_bytes():
            raise ValueError("Trace differs from archived excerpt: "+generated.name)
    print("Publication inventory, runtime prompts, percentage tables and trace excerpts validated.")

if __name__=="__main__":
    main()
