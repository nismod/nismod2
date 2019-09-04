"""GB Postcode Sectors

ref: https://datashare.is.ed.ac.uk/handle/10283/2597
"""
import os
import zipfile

import geopandas as gpd
import requests


def download(url, filename, dirname=".", force=False):
    if force or not os.path.exists(filename):
        r = requests.get(url, stream=True)
        with open(filename, 'wb') as fd:
            for chunk in r.iter_content(chunk_size=128):
                fd.write(chunk)
    if filename.endswith(".zip"):
        with zipfile.ZipFile(filename,"r") as zf:
            zf.extractall(dirname)


def main():
    tmpdir = os.path.join(os.path.dirname(__file__), "..", "tmp")
    dimdir = os.path.join(os.path.dirname(__file__), "..", "data", "dimensions")
    url = "https://datashare.is.ed.ac.uk/bitstream/handle/10283/2597/GB_Postcodes.zip?sequence=1&isAllowed=y"
    download(url, os.path.join(tmpdir, "gb_postcodes.zip"), tmpdir)

    ps = gpd.read_file(os.path.join(tmpdir, "GB_Postcodes", "PostalSector.shp")) \
        .rename(columns={'StrSect': 'name'}) \
        [['name', 'geometry']]

    lads = gpd.read_file(os.path.join(dimdir, 'lad_uk_2016-12', 'lad_uk_2016-12.shp'))

    # Overlay to find intersecting areas
    overlay = gpd.overlay(ps, lads, how="intersection")
    overlay['area'] = overlay.geometry.area

    # Filter to create lookup based on max overlapping area
    link = overlay[['name_1', 'name_2', 'desc', 'area']] \
        .rename(columns={'name_1': 'name', 'name_2': 'lad'}) \
        .sort_values(by='area', ascending=False) \
        .drop_duplicates(subset='name', keep='first')

    # Merge lookup
    ps = ps.merge(link, on='name', how='left')

    # Check validity
    validity = ps.geometry.apply(lambda geom: geom.is_valid)
    print(~validity.any())

    ps.to_file(os.path.join(dimdir, "postcode_sector.shp"))


if __name__ == '__main__':
    main()
