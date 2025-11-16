import osmnx as ox
import geopandas as gpd
import pandas as pd

cities = [
    "New York, USA",
    "Phoenix, USA",
    "Philadelphia, USA",
    "San Antonio, USA",
    "Chicago, USA",
    "Houston, USA",
    "Los Angeles, USA",
]

gdfs = []
for full in cities:
    try:
        g = ox.geocode_to_gdf(full)            # returns polygon for the place
        g["Store_Location"] = full.split(",")[0]
        gdfs.append(g[["Store_Location", "geometry"]])
    except Exception as e:
        print(f"Failed to fetch {full}: {e}")

if gdfs:
    out = gpd.GeoDataFrame(pd.concat(gdfs, ignore_index=True), crs=gdfs[0].crs)
    out = out.to_crs(epsg=4326)
    out.to_file("../store_regions.geojson", driver="GeoJSON")
    print("Saved store_regions.geojson")