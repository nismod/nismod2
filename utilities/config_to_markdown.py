"""Extract model descriptions and inputs/outputs/parameters to markdown
"""
import os
from glob import glob

import pandas as pd
import yaml

models = glob(
    os.path.join(
        os.path.dirname(__file__),
        '..',
        'config/sector_models/*.yml'))

for fname in models:
    m = os.path.basename(fname)
    if m[:2] in ("co", "ap", "ag", "ex", "sa", "di", "re"):
        continue
    if "south" in m:
        continue
    print(m)
    out_fname = os.path.join('docs', os.path.basename(fname.replace(".yml", "_details.md")))
    with open(fname) as fh:
        md = yaml.safe_load(fh)

        inputs = pd.DataFrame(md['inputs'])

        params = pd.DataFrame(md['parameters'])
        if 'dims' not in params.columns:
            params['dims'] = ''
        if 'unit' not in params.columns:
            params['unit'] = ''

        outputs = pd.DataFrame(md['outputs'])

        with open(out_fname, 'w') as out:
            out.write(f"# {md['name']}\n\n")
            out.write(f"{md['description']}\n\n")
            out.write("# Inputs\n\n")
            out.write(
                inputs[['description','name','unit','dims','dtype']] \
                .to_markdown(index=False))
            out.write("\n\n")
            out.write("# Parameters\n\n")
            if len(params):
                out.write(
                    params[['description','name','unit','dims','dtype']] \
                    .to_markdown(index=False))
            else:
                out.write("No parameters.")
            out.write("\n\n")
            out.write("# Outputs\n\n")
            out.write(
                outputs[['description','name','unit','dims','dtype']] \
                .to_markdown(index=False))
            out.write("\n\n")
