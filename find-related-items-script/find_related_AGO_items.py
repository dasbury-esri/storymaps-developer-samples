"""
ArcGIS Item Relationship Analysis Graphing Tool

This script connects to an ArcGIS portal to analyze, classify, and map relationships
between various ArcGIS items within an organization. It retrieves, processes, and saves
information about related items to CSV files, and can also generate an HTML file for
visualizing item relationships using a network graph.

Dependencies:
***REMOVED******REMOVED***- arcgis: ArcGIS API for Python
***REMOVED******REMOVED***- pandas: Data manipulation and storage
***REMOVED******REMOVED***- re: Regular expressions for item ID extraction
***REMOVED******REMOVED***- warnings: To suppress irrelevant warnings
***REMOVED******REMOVED***- uuid: To generate unique identifiers for rows
***REMOVED******REMOVED***- networkx, pyvis: For graph construction and visualization
***REMOVED******REMOVED***- matplotlib: For graphing (if HTML graph is enabled)

Configuration Parameters:
***REMOVED******REMOVED***- PORTAL (str): The ArcGIS portal URL.
***REMOVED******REMOVED***- USERNAME, PASSWORD (str): Credentials for portal login.
***REMOVED******REMOVED***- OUTPUT_FILE (str): File path to save results on related items.
***REMOVED******REMOVED***- OUTPUT_MISS_FILE (str): File path to save items that could not be processed.
***REMOVED******REMOVED***- GRAPH_FILE (str): File path to save the graph as an HTML file.
***REMOVED******REMOVED***- CREATE_GRAPH_HTML (bool): Option to generate an HTML graph.
***REMOVED******REMOVED***- QUERY_START_DATE (int): Timestamp in milliseconds to set a starting date for queries.
***REMOVED******REMOVED***- ACCOUNT (str): Account to analyze (defaults to logged-in user if empty).
***REMOVED******REMOVED***- TEST_MAX_PROCESSED_ITEMS, TEST_MAX_FOUND_ITEMS (int): Limits for testing; set to None for production.

Main Functions:
***REMOVED******REMOVED***- classify_by_type_typekeywords: Classifies an ArcGIS item based on type and type keywords.
***REMOVED******REMOVED***- get_all_content_items_in_org: Retrieves all items within an organization.
***REMOVED******REMOVED***- get_related_items_for_id: Recursively finds related items for a given item ID.
***REMOVED******REMOVED***- process_paused_related_items: Manages items marked as "paused" to avoid cyclic dependencies.
***REMOVED******REMOVED***- insert_slice_below: Helper function to insert DataFrame slices.
***REMOVED******REMOVED***- replace_path: Modifies paths for tracking item relationships.
***REMOVED******REMOVED***- find_all_possible_ids: Extracts potential ArcGIS item IDs from JSON strings.

Usage:
***REMOVED******REMOVED***- Ensure the ArcGIS API for Python is installed and valid credentials are available.
***REMOVED******REMOVED***- Set configuration parameters at the top of the script as needed.
***REMOVED******REMOVED***- Run the script to produce CSV files of related items and (optionally) an HTML graph.
***REMOVED******REMOVED***- Review the output CSVs to examine processed and missed items.

Example:
***REMOVED******REMOVED***$ python arcgis_item_analysis.py
"""


import re
import time
import uuid
import warnings
from typing import List, Set, Union

import pandas as pd
from arcgis.gis import GIS, Item

warnings.filterwarnings("ignore")

# Portal to investigate
PORTAL = "https://www.arcgis.com"
# Username to log in to the portal
USERNAME = ""
# Password associated with the portal
PASSWORD = ""
# Output CSV file location
OUTPUT_FILE = "related_items.csv"
# Location for CSV where missed items and error messages will be added
OUTPUT_MISS_FILE = "missed_items.csv"
# Location of graphing html file. Will only output when CREATE_GRAPH_HTML is True
GRAPH_FILE = "graph.html"
# Should data be graphed at the end of the process
CREATE_GRAPH_HTML = True
# Unix timestamp (in milliseconds) marking the starting point for the search algorithm. Default is 00:00:00, January 1st, 2016
QUERY_START_DATE = 1451624400000
# The name of the account to be analyzed. If left blank the script will use the logged in user.
ACCOUNT = None
# Max number of items to analyze. FOR dev/testing purposes. Modify this value to an integer if you want to test this script with a shortened run
TEST_MAX_PROCESSED_ITEMS = None
# Max number of items to find.. FOR dev/testing purposes.***REMOVED***Modify this value to an integer if you want to test this script with a shortened run
TEST_MAX_FOUND_ITEMS = None

COLOR_MAP = {
***REMOVED******REMOVED***# Maps - Blue
***REMOVED******REMOVED***"360 VR Experience": "#00BFFF",***REMOVED***# DeepSkyBlue
***REMOVED******REMOVED***"CityEngine Web Scene": "#00BFFF",***REMOVED***# DeepSkyBlue
***REMOVED******REMOVED***"Map Area": "#00BFFF",***REMOVED***# DeepSkyBlue
***REMOVED******REMOVED***"Pro Map": "#00BFFF",***REMOVED***# DeepSkyBlue
***REMOVED******REMOVED***"Web Map": "#00BFFF",***REMOVED***# DeepSkyBlue
***REMOVED******REMOVED***"Web Scene": "#00BFFF",***REMOVED***# DeepSkyBlue
***REMOVED******REMOVED***# Layers - Yellow
***REMOVED******REMOVED***"Feature Collection": "#FFD700",***REMOVED***# Gold
***REMOVED******REMOVED***"Feature Collection Template": "#FFD700",***REMOVED***# Gold
***REMOVED******REMOVED***"Feature Service": "#FFD700",***REMOVED***# Gold
***REMOVED******REMOVED***"Geodata Service": "#FFD700",***REMOVED***# Gold
***REMOVED******REMOVED***"Group Layer": "#FFD700",***REMOVED***# Gold
***REMOVED******REMOVED***"Media Layer": "#FFD700",***REMOVED***# Gold
***REMOVED******REMOVED***"Image Service": "#FFD700",***REMOVED***# Gold
***REMOVED******REMOVED***"KML": "#FFD700",***REMOVED***# Gold
***REMOVED******REMOVED***"KML Collection": "#FFD700",***REMOVED***# Gold
***REMOVED******REMOVED***"Map Service": "#FFD700",***REMOVED***# Gold
***REMOVED******REMOVED***"OGCFeatureServer": "#FFD700",***REMOVED***# Gold
***REMOVED******REMOVED***"Oriented Imagery Catalog": "#FFD700",***REMOVED***# Gold
***REMOVED******REMOVED***"Relational Database Connection": "#FFD700",***REMOVED***# Gold
***REMOVED******REMOVED***"3DTilesService": "#FFD700",***REMOVED***# Gold
***REMOVED******REMOVED***"Scene Service": "#FFD700",***REMOVED***# Gold
***REMOVED******REMOVED***"Vector Tile Service": "#FFD700",***REMOVED***# Gold
***REMOVED******REMOVED***"WFS": "#FFD700",***REMOVED***# Gold
***REMOVED******REMOVED***"WMS": "#FFD700",***REMOVED***# Gold
***REMOVED******REMOVED***"WMTS": "#FFD700",***REMOVED***# Gold
***REMOVED******REMOVED***# Service Palette
***REMOVED******REMOVED***"Geometry Service": "#778899",***REMOVED***# LightSlateGray
***REMOVED******REMOVED***"Geocoding Service": "#778899",***REMOVED***# LightSlateGray
***REMOVED******REMOVED***"Geoprocessing Service": "#778899",***REMOVED***# LightSlateGray
***REMOVED******REMOVED***"Network Analysis Service": "#778899",***REMOVED***# LightSlateGray
***REMOVED******REMOVED***"Workflow Manager Service": "#778899",***REMOVED***# LightSlateGray
***REMOVED******REMOVED***# StoryMaps
***REMOVED******REMOVED***"Collection": "#008080",***REMOVED***# Teal
***REMOVED******REMOVED***"Briefing": "#008B8B",***REMOVED***# DarkCyan
***REMOVED******REMOVED***"StoryMap": "#008B8B",***REMOVED***# DarkCyan
***REMOVED******REMOVED***"Frame": "#20B2AA",***REMOVED***# LightSeaGreen
***REMOVED******REMOVED***"Theme": "#20B2AA",***REMOVED***# LightSeaGreen
***REMOVED******REMOVED***"StoryMap Template": "#20B2AA",***REMOVED***# LightSeaGreen
***REMOVED******REMOVED***"StoryMap Theme": "#20B2AA",***REMOVED***# LightSeaGreen
***REMOVED******REMOVED***# Dashboard - Orange
***REMOVED******REMOVED***"Dashboard": "#FFA500",***REMOVED***# Orange
***REMOVED******REMOVED***# Experience Builder
***REMOVED******REMOVED***"Experience Builder Widget": "#66CDAA",***REMOVED***# Aquamarine
***REMOVED******REMOVED***"Experience Builder Widget Package": "#66CDAA",***REMOVED***# Aquamarine
***REMOVED******REMOVED***# Web Experience
***REMOVED******REMOVED***"Web Experience": "#AFEEEE",***REMOVED***# PaleTurquoise
***REMOVED******REMOVED***"Web Experience Template": "#AFEEEE",***REMOVED***# PaleTurquoise
***REMOVED******REMOVED***# Web Map Apps
***REMOVED******REMOVED***"Web Mapping Application": "#008000",***REMOVED***# DarkGreen
***REMOVED******REMOVED***# Hub - DarkOrchid
***REMOVED******REMOVED***"Hub Event": "#9932CC",***REMOVED***# DarkOrchid
***REMOVED******REMOVED***"Hub Initiative": "#9932CC",***REMOVED***# DarkOrchid
***REMOVED******REMOVED***"Hub Initiative Template": "#9932CC",***REMOVED***# DarkOrchid
***REMOVED******REMOVED***"Hub Page": "#9932CC",***REMOVED***# DarkOrchid
***REMOVED******REMOVED***"Hub Project": "#9932CC",***REMOVED***# DarkOrchid
***REMOVED******REMOVED***"Hub Site Application": "#9932CC",***REMOVED***# DarkOrchid
***REMOVED******REMOVED***# Survey123
***REMOVED******REMOVED***"Form": "#9ACD32",***REMOVED***# YellowGreen
***REMOVED******REMOVED***# Insights - OrangeRed
***REMOVED******REMOVED***"Insights Workbook": "#FF4500",***REMOVED***# OrangeRed
***REMOVED******REMOVED***"Insights Workbook Package": "#FF4500",***REMOVED***# OrangeRed
***REMOVED******REMOVED***"Insights Model": "#FF4500",***REMOVED***# OrangeRed
***REMOVED******REMOVED***"Insights Page": "#FF4500",***REMOVED***# OrangeRed
***REMOVED******REMOVED***"Insights Theme": "#FF4500",***REMOVED***# OrangeRed
***REMOVED******REMOVED***"Insights Data Engineering Workbook": "#FF4500",***REMOVED***# OrangeRed
***REMOVED******REMOVED***"Insights Data Engineering Model": "#FF4500",***REMOVED***# OrangeRed
***REMOVED******REMOVED***## NO PREFERENCE for these...
***REMOVED******REMOVED***"GeoBIM Application": "#90EE90",***REMOVED***# CornflowerBlue
***REMOVED******REMOVED***"GeoBIM Project": "#8FBC8F",***REMOVED***# CornflowerBlue
***REMOVED******REMOVED***"Data Pipeline": "#32CD32",***REMOVED***# Lime Green
***REMOVED******REMOVED***"Deep Learning Studio Project": "#00FF7F",***REMOVED***# Spring Green
***REMOVED******REMOVED***"Esri Classification Schema": "#00FA9A",***REMOVED***# Medium Spring Green
***REMOVED******REMOVED***"Excalibur Imagery Project": "#8FBC8F",***REMOVED***# Dark Sea Green
***REMOVED******REMOVED***"AppBuilder Extension": "#006400",***REMOVED***# Dark Green
***REMOVED******REMOVED***"AppBuilder Widget Package": "#228B22",***REMOVED***# Forest Green
***REMOVED******REMOVED***"Code Attachment": "#2E8B57",***REMOVED***# Sea Green
***REMOVED******REMOVED***"Investigation": "#7FFF00",***REMOVED***# Chartreuse
***REMOVED******REMOVED***"Knowledge Studio Project": "#90EE90",***REMOVED***# Light Green
***REMOVED******REMOVED***"Mission": "#98FB98",***REMOVED***# Pale Green
***REMOVED******REMOVED***"Mobile Application": "#ADFF2F",***REMOVED***# Green Yellow
***REMOVED******REMOVED***"Notebook": "#00FF00",***REMOVED***# Pure Green
***REMOVED******REMOVED***"Notebook Code Snippet Library": "#7CFC00",***REMOVED***# Lawn Green
***REMOVED******REMOVED***"Native Application": "#9ACD32",***REMOVED***# Yellow Green
***REMOVED******REMOVED***"Native Application Installer": "#32CD32",***REMOVED***# Lime Green
***REMOVED******REMOVED***"Ortho Mapping Project": "#20B2AA",***REMOVED***# Light Sea Green
***REMOVED******REMOVED***"Ortho Mapping Template": "#66CDAA",***REMOVED***# Aquamarine
***REMOVED******REMOVED***"Solution": "#3CB371",***REMOVED***# Medium Sea Green
***REMOVED******REMOVED***"Web AppBuilder Widget": "#7FFF00",***REMOVED***# Chartreuse
***REMOVED******REMOVED***"Workforce Project": "#90EE90",***REMOVED***# Light Green
***REMOVED******REMOVED***# Data Palette
***REMOVED******REMOVED***"Administrative Report": "#FFE4B5",***REMOVED***# Moccasin
***REMOVED******REMOVED***"Apache Parquet": "#FFE4B5",***REMOVED***# Moccasin
***REMOVED******REMOVED***"CAD Drawing": "#FFE4B5",***REMOVED***# Moccasin
***REMOVED******REMOVED***"Color Set": "#FFE4B5",***REMOVED***# Moccasin
***REMOVED******REMOVED***"Content Category Set": "#FFE4B5",***REMOVED***# Moccasin
***REMOVED******REMOVED***"CSV": "#FFE4B5",***REMOVED***# Moccasin
***REMOVED******REMOVED***"CSV Collection": "#FFE4B5",***REMOVED***# Moccasin
***REMOVED******REMOVED***"Document Link": "#FFE4B5",***REMOVED***# Moccasin
***REMOVED******REMOVED***"Earth configuration": "#FFE4B5",***REMOVED***# Moccasin
***REMOVED******REMOVED***"Esri Classifier Definition": "#FFE4B5",***REMOVED***# Moccasin
***REMOVED******REMOVED***"Export Package": "#FFE4B5",***REMOVED***# Moccasin
***REMOVED******REMOVED***"File Geodatabase": "#CFFE4B5",***REMOVED***# Moccasin
***REMOVED******REMOVED***"GeoJson": "#FFE4B5",***REMOVED***# Moccasin
***REMOVED******REMOVED***"GeoPackage": "#FFE4B5",***REMOVED***# Moccasin
***REMOVED******REMOVED***"GML": "#FFE4B5",***REMOVED***# Moccasin
***REMOVED******REMOVED***"Image": "#FFE4B5",***REMOVED***# Moccasin
***REMOVED******REMOVED***"iWork Keynote": "#FFE4B5",***REMOVED***# Moccasin
***REMOVED******REMOVED***"iWork Numbers": "#FFE4B5",***REMOVED***# Moccasin
***REMOVED******REMOVED***"iWork Pages": "#FFE4B5",***REMOVED***# Moccasin
***REMOVED******REMOVED***"Microsoft Excel": "#4FFE4B5",***REMOVED***# Moccasin
***REMOVED******REMOVED***"Microsoft Powerpoint": "#FFE4B5",***REMOVED***# Moccasin
***REMOVED******REMOVED***"Microsoft Word": "#FFE4B5",***REMOVED***# Moccasin
***REMOVED******REMOVED***"PDF": "#FFE4B5",***REMOVED***# Moccasin
***REMOVED******REMOVED***"Report Template": "#FFE4B5",***REMOVED***# Moccasin
***REMOVED******REMOVED***"Service Definition": "#FFE4B5",***REMOVED***# Moccasin
***REMOVED******REMOVED***"Shapefile": "#FFE4B5",***REMOVED***# Moccasin
***REMOVED******REMOVED***"SQLite Geodatabase": "#FFE4B5",***REMOVED***# Moccasin
***REMOVED******REMOVED***"Statistical Data Collection": "#FFE4B5",***REMOVED***# Moccasin
***REMOVED******REMOVED***"Style": "#FFE4B5",***REMOVED***# Moccasin
***REMOVED******REMOVED***"Symbol Set": "#FFE4B5",***REMOVED***# Moccasin
***REMOVED******REMOVED***"Visio Document": "#FFE4B5",***REMOVED***# Moccasin
***REMOVED******REMOVED***# Other Palette
***REMOVED******REMOVED***"other": "#C0C0C0",***REMOVED***# Silver
}


def classify_by_type_typekeywords(item: Item) -> str:
***REMOVED******REMOVED***"""
***REMOVED******REMOVED***Classifies an ArcGIS item based on its type keywords.

***REMOVED******REMOVED***Args:
***REMOVED******REMOVED******REMOVED******REMOVED***item (Item): The ArcGIS item to classify.

***REMOVED******REMOVED***Returns:
***REMOVED******REMOVED******REMOVED******REMOVED***str: The classification of the item.
***REMOVED******REMOVED***"""
***REMOVED******REMOVED***typekeywords = item.typeKeywords
***REMOVED******REMOVED***isTemplate = "storymaptemplate" in typekeywords
***REMOVED******REMOVED***if "storymapbriefing" in typekeywords and "StoryMap" in typekeywords:
***REMOVED******REMOVED******REMOVED******REMOVED***return "Briefing"
***REMOVED******REMOVED***if "storymapcollection" in typekeywords and "StoryMap" in typekeywords:
***REMOVED******REMOVED******REMOVED******REMOVED***return "Collection"
***REMOVED******REMOVED***if "storymapframe" in typekeywords and "StoryMap" in typekeywords:
***REMOVED******REMOVED******REMOVED******REMOVED***return "Frame"
***REMOVED******REMOVED***if "StoryMap Theme" in typekeywords:
***REMOVED******REMOVED******REMOVED******REMOVED***return "Theme"
***REMOVED******REMOVED***if "StoryMap" in typekeywords:
***REMOVED******REMOVED******REMOVED******REMOVED***return "StoryMap Template" if isTemplate else "StoryMap"
***REMOVED******REMOVED***# Not a storymap return the type if it is in color map else return other
***REMOVED******REMOVED***if item.type in COLOR_MAP:
***REMOVED******REMOVED******REMOVED******REMOVED***return item.type
***REMOVED******REMOVED***else:
***REMOVED******REMOVED******REMOVED******REMOVED***return "other"


def get_all_content_items_in_org(gis_con: GIS, owner: str = None) -> Set[str]:
***REMOVED******REMOVED***"""
***REMOVED******REMOVED***Retrieves all StoryMap items within the organization.

***REMOVED******REMOVED***Args:
***REMOVED******REMOVED******REMOVED******REMOVED***gis_con (GIS): The GIS connection object.
***REMOVED******REMOVED******REMOVED******REMOVED***owner (str, optional): The owner to filter items, if not passed will default to logged in user.

***REMOVED******REMOVED***Returns:
***REMOVED******REMOVED******REMOVED******REMOVED***Set[str]: A set of item IDs found.
***REMOVED******REMOVED***"""
***REMOVED******REMOVED***org_users = gis_con.users.search(query=f"username:{owner}")
***REMOVED******REMOVED***run_date = int(time.time() * 1000)
***REMOVED******REMOVED***if owner is None:
***REMOVED******REMOVED******REMOVED******REMOVED***owner = gis_con.users.me.username
***REMOVED******REMOVED***found_ids = set()
***REMOVED******REMOVED***total_items_found = 0
***REMOVED******REMOVED***for index_user, user in enumerate(org_users):
***REMOVED******REMOVED******REMOVED******REMOVED***# TODO Owner should never be none at this point, can rework this section
***REMOVED******REMOVED******REMOVED******REMOVED***if owner is not None and len(owner) > 0 and user.username != owner:
***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED***continue
***REMOVED******REMOVED******REMOVED******REMOVED***loop_counter = 0
***REMOVED******REMOVED******REMOVED******REMOVED***current_results = []
***REMOVED******REMOVED******REMOVED******REMOVED***modified_date_modifier = None
***REMOVED******REMOVED******REMOVED******REMOVED***len_result = 1000
***REMOVED******REMOVED******REMOVED******REMOVED***start = 0
***REMOVED******REMOVED******REMOVED******REMOVED***while len_result == 1000:
***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED***if (
***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED***TEST_MAX_FOUND_ITEMS is not None
***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED***and total_items_found > TEST_MAX_FOUND_ITEMS
***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED***):
***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED***break
***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED***loop_counter += 1
***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED***if start >= 10000:
***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED***# add a 1ms reduction to the last modified date of the current results
***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED***last_created = current_results[-1].created
***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED***modified_date_modifier = (
***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED***last_created + 1
***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED***)***REMOVED***# Adjust the modified date range
***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED***start = 0
***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED***query = f"owner: {user.username}"
***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED***if modified_date_modifier:
***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED***query += f" AND created:[{modified_date_modifier} TO {run_date}]"
***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED***else:
***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED***query += f" AND created:[{QUERY_START_DATE} TO {run_date}]"
***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED***print(f"Query: {query}")
***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED***result = gis_con.content.advanced_search(
***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED***query=query,
***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED***max_items=1000,
***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED***start=start,
***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED***sort_field="created",
***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED***sort_order="asc",
***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED***)
***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED***len_result = len(result["results"])
***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED***start += len_result
***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED***total_items_found += len_result
***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED***current_results = result["results"]
***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED***for item in result["results"]:
***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED***found_ids.add(item.id)
***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED***if len_result < 1000:
***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED***break
***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED***# print progress
***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED***print(f"Total items found: {len(found_ids)} in {loop_counter} loops")
***REMOVED******REMOVED******REMOVED******REMOVED***# if index_user <= 1:
***REMOVED******REMOVED******REMOVED******REMOVED***#***REMOVED******REMOVED*** return found_ids
***REMOVED******REMOVED***return found_ids


def get_item_data(item: Item):
***REMOVED******REMOVED***"""
***REMOVED******REMOVED***Fetches data for a given ArcGIS item, handling different resource types.

***REMOVED******REMOVED***Args:
***REMOVED******REMOVED******REMOVED******REMOVED***item (Item): The ArcGIS item to fetch data for.

***REMOVED******REMOVED***Returns:
***REMOVED******REMOVED******REMOVED******REMOVED***tuple: A tuple containing the item data and any related data.
***REMOVED******REMOVED***"""
***REMOVED******REMOVED***item_data = item.get_data(try_json=True)
***REMOVED******REMOVED***if item.type in ["StoryMap", "StoryMap Theme"]:
***REMOVED******REMOVED******REMOVED******REMOVED***# Should only be relevant to StoryMaps
***REMOVED******REMOVED******REMOVED******REMOVED***try:
***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED***resources = [resource["resource"] for resource in item.resources.list()]
***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED***has_published_data = "published_data.json" in resources
***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED***draft_id = None
***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED***for keyword in item.typeKeywords:
***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED***if keyword.startswith("smdraftresourceid"):
***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED***draft_id = keyword.split(":")[1]
***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED***if has_published_data and not draft_id:
***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED***return (item.resources.get("published_data.json", try_json=True), None)
***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED***elif draft_id and not has_published_data:
***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED***return (item.resources.get(f"{draft_id}", try_json=True), None)
***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED***elif draft_id and has_published_data:
***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED***return (
***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED***item.resources.get(f"{draft_id}", try_json=True),
***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED***item.resources.get("published_data.json", try_json=True),
***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED***)
***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED***else:
***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED***return (item.resources.get("draft.json", try_json=True), None)
***REMOVED******REMOVED******REMOVED******REMOVED***except Exception as e:
***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED***return (None, None)
***REMOVED******REMOVED***return (item_data, None)


def find_all_possible_ids(json_string: str):
***REMOVED******REMOVED***"""
***REMOVED******REMOVED***Extracts all possible item IDs from a JSON string using regex.

***REMOVED******REMOVED***Args:
***REMOVED******REMOVED******REMOVED******REMOVED***json_string (str): The JSON string to search for IDs.

***REMOVED******REMOVED***Returns:
***REMOVED******REMOVED******REMOVED******REMOVED***list: A list of found item IDs.
***REMOVED******REMOVED***"""
***REMOVED******REMOVED***return re.findall(r"[\"\'\/]([a-zA-Z0-9]{32})[\"\'\/]", json_string)


def get_related_items_for_id(
***REMOVED******REMOVED***gis_con: GIS,
***REMOVED******REMOVED***item_id: str,
***REMOVED******REMOVED***related_items_df: pd.DataFrame,
***REMOVED******REMOVED***missed_items_df: pd.DataFrame,
***REMOVED******REMOVED***main_ancestors: Set[str],
***REMOVED******REMOVED***base_ancestor: Union[Item | None] = None,
***REMOVED******REMOVED***relation_path: List[str] = [],
***REMOVED******REMOVED***relations_in_process: List[str] = [],
):
***REMOVED******REMOVED***"""
***REMOVED******REMOVED***Fetches related items for a given item ID and updates the related items DataFrame.
***REMOVED******REMOVED***This function attempts to fetch an item by its ID up to three times. If successful, it processes the item to find its related items and updates the provided DataFrames accordingly. It also handles cyclic dependencies and ensures that items are not processed multiple times.
***REMOVED******REMOVED***Args:
***REMOVED******REMOVED******REMOVED******REMOVED***gis_con (GIS): The GIS connection object.
***REMOVED******REMOVED******REMOVED******REMOVED***item_id (str): The ID of the item to fetch and process.
***REMOVED******REMOVED******REMOVED******REMOVED***related_items_df (pd.DataFrame): DataFrame to store information about related items.
***REMOVED******REMOVED******REMOVED******REMOVED***missed_items_df (pd.DataFrame): DataFrame to store information about items that could not be fetched.
***REMOVED******REMOVED******REMOVED******REMOVED***main_ancestors (Set[str]): Set to store the IDs of main ancestor items.
***REMOVED******REMOVED******REMOVED******REMOVED***base_ancestor (Union[Item, None], optional): The base ancestor item. Defaults to None.
***REMOVED******REMOVED******REMOVED******REMOVED***relation_path (List[str], optional): List to track the relation path of items. Defaults to an empty list.
***REMOVED******REMOVED******REMOVED******REMOVED***relations_in_process (List[str], optional): List to track items that are currently being processed. Defaults to an empty list.
***REMOVED******REMOVED***Returns:
***REMOVED******REMOVED******REMOVED******REMOVED***None
***REMOVED******REMOVED***"""

***REMOVED******REMOVED***valid_item = None
***REMOVED******REMOVED***# Attempt to fetch the item up to 3 times
***REMOVED******REMOVED***for tries in range(3):
***REMOVED******REMOVED******REMOVED******REMOVED***try:
***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED***valid_item = Item(gis_con, item_id)
***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED***break***REMOVED***# Exit loop on successful fetch
***REMOVED******REMOVED******REMOVED******REMOVED***except Exception as e:
***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED***# print(f"Error fetching item {item_id}: {e}. Retrying ({tries+1}/3)...")
***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED***time.sleep(1)***REMOVED***# Adding delay before retry
***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED***if tries == 2:
***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED***missed_items_df.loc[uuid.uuid4()] = [item_id, None, None, str(e)]
***REMOVED******REMOVED***# Copy the current relation path for further processing
***REMOVED******REMOVED***new_relation_path = relation_path.copy()
***REMOVED******REMOVED***# Check if currently handling the main ancestor
***REMOVED******REMOVED***currently_handling_main_ancestor = base_ancestor is None
***REMOVED******REMOVED***# Detect cyclic dependency: if the item is already in the relation path
***REMOVED******REMOVED***if not currently_handling_main_ancestor and valid_item.itemid in relation_path:
***REMOVED******REMOVED******REMOVED******REMOVED***print(
***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED***f"Detected a cyclic dependency! {valid_item.itemid} appears in the relation path {relation_path}."
***REMOVED******REMOVED******REMOVED******REMOVED***)
***REMOVED******REMOVED******REMOVED******REMOVED***return
***REMOVED******REMOVED***# If currently handling the main ancestor and valid_item is found, set it as the base ancestor
***REMOVED******REMOVED***if currently_handling_main_ancestor and valid_item:
***REMOVED******REMOVED******REMOVED******REMOVED***base_ancestor = valid_item
***REMOVED******REMOVED******REMOVED******REMOVED***main_ancestors.add(valid_item.itemid)
***REMOVED******REMOVED***# Only add the valid item's ID to the relation path if not handling the main ancestor
***REMOVED******REMOVED***if valid_item:
***REMOVED******REMOVED******REMOVED******REMOVED***new_relation_path.append(valid_item.itemid)
***REMOVED******REMOVED***# If not handling the main ancestor, proceed to process the valid item and add it to the related items DataFrame
***REMOVED******REMOVED***if not currently_handling_main_ancestor:
***REMOVED******REMOVED******REMOVED******REMOVED***# print("processing related item", valid_item.itemid)
***REMOVED******REMOVED******REMOVED******REMOVED***new_row = [
***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED***base_ancestor.itemid,
***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED***classify_by_type_typekeywords(base_ancestor),
***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED***base_ancestor.title,
***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED***base_ancestor.access,
***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED***base_ancestor.owner,
***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED***valid_item.itemid,
***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED***classify_by_type_typekeywords(valid_item),
***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED***valid_item.title,
***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED***valid_item.access,
***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED***valid_item.owner,
***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED***valid_item.get("orgId", None),
***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED***new_relation_path,
***REMOVED******REMOVED******REMOVED******REMOVED***]
***REMOVED******REMOVED******REMOVED******REMOVED***# if exact row already exists, skip
***REMOVED******REMOVED******REMOVED******REMOVED***if related_items_df.apply(lambda row: row.tolist() == new_row, axis=1).any():
***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED***# print("oops!")
***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED***return
***REMOVED******REMOVED******REMOVED******REMOVED***## Check if the related item is already being processed:
***REMOVED******REMOVED******REMOVED******REMOVED***if valid_item.itemid in relations_in_process:
***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED***new_row.append("Yes")
***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED***related_items_df.loc[uuid.uuid4()] = new_row
***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED***print(f"Item {valid_item.itemid} is already in process")
***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED***return
***REMOVED******REMOVED******REMOVED******REMOVED***new_row.append("No")
***REMOVED******REMOVED******REMOVED******REMOVED***## Add valid item to the ancestors
***REMOVED******REMOVED******REMOVED******REMOVED***related_items_df.loc[uuid.uuid4()] = new_row
***REMOVED******REMOVED***# If valid_item was successfully fetched, and all previous conditions are met, proceed to fetch related items for this item
***REMOVED******REMOVED***if valid_item:
***REMOVED******REMOVED******REMOVED******REMOVED***items_related_to_valid_item = set()
***REMOVED******REMOVED******REMOVED******REMOVED***relations_in_process.append(valid_item.itemid)
***REMOVED******REMOVED******REMOVED******REMOVED***valid_item_data = get_item_data(valid_item)
***REMOVED******REMOVED******REMOVED******REMOVED***# If the first part of the fetched data is not empty
***REMOVED******REMOVED******REMOVED******REMOVED***if valid_item_data[0] is not None or valid_item_data[0] != {}:
***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED***related_json_string = str(valid_item_data[0])
***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED***related_ids = find_all_possible_ids(related_json_string)
***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED***[items_related_to_valid_item.add(related_id) for related_id in related_ids]
***REMOVED******REMOVED******REMOVED******REMOVED***# If the second part of the fetched data is not empty (only relevant to StoryMaps), and considers draft related items
***REMOVED******REMOVED******REMOVED******REMOVED***if valid_item_data[1] is not None or valid_item_data[1] != {}:
***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED***related_json_string = str(valid_item_data[1])
***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED***related_ids = find_all_possible_ids(related_json_string)
***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED***[items_related_to_valid_item.add(related_id) for related_id in related_ids]
***REMOVED******REMOVED******REMOVED******REMOVED***# Iterate over each related ID found
***REMOVED******REMOVED******REMOVED******REMOVED***for related_id in items_related_to_valid_item:
***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED***# Recursively call the function to find related items for each related ID
***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED***get_related_items_for_id(
***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED***gis_con,
***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED***related_id,
***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED***related_items_df,
***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED***missed_items_df,
***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED***main_ancestors,
***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED***base_ancestor,
***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED***new_relation_path,
***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED***)


def insert_slice_below(df, index, new_slice: pd.DataFrame):
***REMOVED******REMOVED***"""
***REMOVED******REMOVED***Inserts a slice of a DataFrame below a specified index.

***REMOVED******REMOVED***Args:
***REMOVED******REMOVED******REMOVED******REMOVED***df (pd.DataFrame): The DataFrame to insert the slice into.
***REMOVED******REMOVED******REMOVED******REMOVED***index (int): The index to insert the slice below.
***REMOVED******REMOVED******REMOVED******REMOVED***new_slice (pd.DataFrame): The slice to insert.
***REMOVED******REMOVED***"""
***REMOVED******REMOVED***# split original dataframe into two parts
***REMOVED******REMOVED***top = df.iloc[: index + 1]
***REMOVED******REMOVED***## only slice bottom if index is not the last row
***REMOVED******REMOVED***if index == len(df) - 1:
***REMOVED******REMOVED******REMOVED******REMOVED***print("index is last row")
***REMOVED******REMOVED******REMOVED******REMOVED***bottom = df.iloc[index + 1 :]
***REMOVED******REMOVED******REMOVED******REMOVED***return pd.concat([top, new_slice])
***REMOVED******REMOVED***bottom = df.iloc[index + 1 :]
***REMOVED******REMOVED***# concatenate the two parts with the new slice in between
***REMOVED******REMOVED***return pd.concat([top, new_slice, bottom])


def replace_path(processed_path: list, original_path: list, paused_item_id: str):
***REMOVED******REMOVED***"""
***REMOVED******REMOVED***Takes the original path and appends the processed path from the paused item.

***REMOVED******REMOVED***Args:
***REMOVED******REMOVED******REMOVED******REMOVED***processed_path (list): The processed path from the paused item.
***REMOVED******REMOVED******REMOVED******REMOVED***original_path (list): The original path.
***REMOVED******REMOVED******REMOVED******REMOVED***paused_item_id (str): The ID of the paused item.
***REMOVED******REMOVED***"""
***REMOVED******REMOVED***# takes the origianl path and appends the processed path from the paused item
***REMOVED******REMOVED***# find the index of the paused item in the original path
***REMOVED******REMOVED***paused_item_index = processed_path.index(paused_item_id)
***REMOVED******REMOVED***# append the processed path from the paused item
***REMOVED******REMOVED***if paused_item_index == len(processed_path) - 1:
***REMOVED******REMOVED******REMOVED******REMOVED***return original_path
***REMOVED******REMOVED***return original_path + processed_path[paused_item_index + 1 :]


def process_paused_related_items(related_df: pd.DataFrame):
***REMOVED******REMOVED***"""
***REMOVED******REMOVED***Processes paused related items in the given DataFrame.
***REMOVED******REMOVED***This function identifies rows in the DataFrame where the 'Awaiting Processing' column is marked as "Yes".
***REMOVED******REMOVED***For each paused item, it finds the corresponding processed item where the 'Related Item Id' matches and
***REMOVED******REMOVED***'Awaiting Processing' is marked as "No". It then counts the number of related rows following the processed item
***REMOVED******REMOVED***that include the paused item's ID in their 'Relationship Path'. An empty DataFrame of the same size is created and
***REMOVED******REMOVED***inserted below the paused item. A slice of the DataFrame from the processed item index to the related row count is
***REMOVED******REMOVED***created, modified, and inserted below the paused item. Finally, duplicates are removed from the DataFrame.
***REMOVED******REMOVED***Args:
***REMOVED******REMOVED******REMOVED******REMOVED***related_df (pd.DataFrame): The DataFrame containing related items with columns including 'Awaiting Processing',
***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED***'Relationship Path', 'Related Item Id', 'Organization Item', 'Org item type',
***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED***'Org item Title', 'Org Item Sharing', and 'Org item owner'.
***REMOVED******REMOVED***Returns:
***REMOVED******REMOVED******REMOVED******REMOVED***None: The DataFrame is modified in place.
***REMOVED******REMOVED***"""
***REMOVED******REMOVED***paused_items = related_df[related_df["Awaiting Processing"] == "Yes"]
***REMOVED******REMOVED***paused_items_indexes = paused_items.index.tolist()
***REMOVED******REMOVED***for index in paused_items_indexes:
***REMOVED******REMOVED******REMOVED******REMOVED***# get the paused item
***REMOVED******REMOVED******REMOVED******REMOVED***paused_item = related_df.loc[index]
***REMOVED******REMOVED******REMOVED******REMOVED***# get integer index of the paused item
***REMOVED******REMOVED******REMOVED******REMOVED***paused_item_index = related_df.index.get_loc(index)
***REMOVED******REMOVED******REMOVED******REMOVED***# get the path of the paused item
***REMOVED******REMOVED******REMOVED******REMOVED***paused_item_path = paused_item["Relationship Path"]
***REMOVED******REMOVED******REMOVED******REMOVED***# get the paused item id
***REMOVED******REMOVED******REMOVED******REMOVED***paused_item_id = paused_item["Related Item Id"]
***REMOVED******REMOVED******REMOVED******REMOVED***# get processed item where related item id is the paused item id and Await Processing is No
***REMOVED******REMOVED******REMOVED******REMOVED***processed_item = related_df[
***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED***(related_df["Related Item Id"] == paused_item_id)
***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED***& (related_df["Awaiting Processing"] == "No")
***REMOVED******REMOVED******REMOVED******REMOVED***]
***REMOVED******REMOVED******REMOVED******REMOVED***if processed_item.empty:
***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED***print("No processed item found")
***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED***continue
***REMOVED******REMOVED******REMOVED******REMOVED***# get the index of the processed item
***REMOVED******REMOVED******REMOVED******REMOVED***print("processed item:", processed_item)
***REMOVED******REMOVED******REMOVED******REMOVED***processed_item_index = processed_item.index[0]
***REMOVED******REMOVED******REMOVED******REMOVED***print("processed item index:", processed_item_index)
***REMOVED******REMOVED******REMOVED******REMOVED***processed_item_int_index = related_df.index.get_loc(processed_item_index)
***REMOVED******REMOVED******REMOVED******REMOVED***print("processed item int index:", processed_item_int_index)
***REMOVED******REMOVED******REMOVED******REMOVED***related_row_count = 0
***REMOVED******REMOVED******REMOVED******REMOVED***counting_related_rows = True
***REMOVED******REMOVED******REMOVED******REMOVED***# count number of items following the processed item that include the paused item id
***REMOVED******REMOVED******REMOVED******REMOVED***while counting_related_rows:
***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED***if (
***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED***paused_item_id
***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED***in related_df.iloc[processed_item_int_index + related_row_count + 1][
***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED***"Relationship Path"
***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED***]
***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED***):
***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED***related_row_count += 1
***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED***else:
***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED***counting_related_rows = False
***REMOVED******REMOVED******REMOVED******REMOVED***# If Related row count is 0 that means the investigated item has no dependencies, and we can move on to the next item
***REMOVED******REMOVED******REMOVED******REMOVED***if related_row_count < 1:
***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED***continue
***REMOVED******REMOVED******REMOVED******REMOVED***# Add empty dataframe of size related_row_count to the related items dataframe at the location of the paused item
***REMOVED******REMOVED******REMOVED******REMOVED***empty_df = pd.DataFrame(columns=related_df.columns)
***REMOVED******REMOVED******REMOVED******REMOVED***for i in range(related_row_count):
***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED***empty_df.loc[uuid.uuid4()] = [None for i in range(len(related_df.columns))]
***REMOVED******REMOVED******REMOVED******REMOVED***# Create slice df of the related items dataframe from the processed item index + 1 to related_row_count
***REMOVED******REMOVED******REMOVED******REMOVED***slice_df = related_df.iloc[
***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED***processed_item_int_index
***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED***+ 1 : processed_item_int_index
***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED***+ related_row_count
***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED***+ 1
***REMOVED******REMOVED******REMOVED******REMOVED***]
***REMOVED******REMOVED******REMOVED******REMOVED***slice_df.index = [uuid.uuid4() for i in range(len(slice_df))]
***REMOVED******REMOVED******REMOVED******REMOVED***slice_df["Awaiting Processing"] = slice_df["Awaiting Processing"].apply(
***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED***lambda x: "NA"
***REMOVED******REMOVED******REMOVED******REMOVED***)
***REMOVED******REMOVED******REMOVED******REMOVED***slice_df["Organization Item"] = slice_df["Organization Item"].apply(
***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED***lambda x: paused_item["Organization Item"]
***REMOVED******REMOVED******REMOVED******REMOVED***)
***REMOVED******REMOVED******REMOVED******REMOVED***slice_df["Org item type"] = slice_df["Org item type"].apply(
***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED***lambda x: paused_item["Org item type"]
***REMOVED******REMOVED******REMOVED******REMOVED***)
***REMOVED******REMOVED******REMOVED******REMOVED***slice_df["Org item Title"] = slice_df["Org item Title"].apply(
***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED***lambda x: paused_item["Org item Title"]
***REMOVED******REMOVED******REMOVED******REMOVED***)
***REMOVED******REMOVED******REMOVED******REMOVED***slice_df["Org Item Sharing"] = slice_df["Org Item Sharing"].apply(
***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED***lambda x: paused_item["Org Item Sharing"]
***REMOVED******REMOVED******REMOVED******REMOVED***)
***REMOVED******REMOVED******REMOVED******REMOVED***slice_df["Org item owner"] = slice_df["Org item owner"].apply(
***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED***lambda x: paused_item["Org item owner"]
***REMOVED******REMOVED******REMOVED******REMOVED***)
***REMOVED******REMOVED******REMOVED******REMOVED***# replace the path in the slice using the processed item path
***REMOVED******REMOVED******REMOVED******REMOVED***slice_df["Relationship Path"] = slice_df["Relationship Path"].apply(
***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED***lambda x: replace_path(x, paused_item_path, paused_item_id)
***REMOVED******REMOVED******REMOVED******REMOVED***)
***REMOVED******REMOVED******REMOVED******REMOVED***related_df = insert_slice_below(related_df, paused_item_index, slice_df)
***REMOVED******REMOVED******REMOVED******REMOVED***# drop duplicates from the related items dataframe, do not include index
***REMOVED******REMOVED******REMOVED******REMOVED***related_df = related_df.loc[related_df.astype(str).drop_duplicates().index]


if __name__ == "__main__":
***REMOVED******REMOVED***gis_con = GIS(PORTAL, USERNAME, PASSWORD)
***REMOVED******REMOVED***all_storymap_items = get_all_content_items_in_org(gis_con, ACCOUNT)
***REMOVED******REMOVED***print(len(all_storymap_items))
***REMOVED******REMOVED***missed_items = pd.DataFrame(
***REMOVED******REMOVED******REMOVED******REMOVED***columns=["itemId", "item_title", "item_owner", "error_message"]
***REMOVED******REMOVED***)
***REMOVED******REMOVED***related_items = pd.DataFrame(
***REMOVED******REMOVED******REMOVED******REMOVED***columns=[
***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED***"Organization Item",
***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED***"Org item type",
***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED***"Org item Title",
***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED***"Org Item Sharing",
***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED***"Org item owner",
***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED***"Related Item Id",
***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED***"Related Item Type",
***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED***"Related Item Title",
***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED***"Related Item Sharing",
***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED***"Related Item Owner",
***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED***"Related Item Org",
***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED***"Relationship Path",
***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED***"Awaiting Processing",
***REMOVED******REMOVED******REMOVED******REMOVED***]
***REMOVED******REMOVED***)
***REMOVED******REMOVED***for index, item_id in enumerate(all_storymap_items):
***REMOVED******REMOVED******REMOVED******REMOVED***print(f"Processing item {index} with id {item_id}")
***REMOVED******REMOVED******REMOVED******REMOVED***try:
***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED***get_related_items_for_id(
***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED***gis_con, item_id, related_items, missed_items, all_storymap_items
***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED***)
***REMOVED******REMOVED******REMOVED******REMOVED***except Exception as e:
***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED***missed_items.loc[uuid.uuid4()] = [item_id, None, None, str(e)]
***REMOVED******REMOVED******REMOVED******REMOVED***if TEST_MAX_PROCESSED_ITEMS is not None and index > TEST_MAX_PROCESSED_ITEMS:
***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED***break
***REMOVED******REMOVED***print(len(related_items))
***REMOVED******REMOVED***related_items.to_csv(OUTPUT_FILE)
***REMOVED******REMOVED***# only have unique rows in the missed items
***REMOVED******REMOVED***missed_items = missed_items.drop_duplicates()
***REMOVED******REMOVED***missed_items.to_csv(OUTPUT_MISS_FILE)

***REMOVED******REMOVED***# find paused related items and their indexes
***REMOVED******REMOVED***process_paused_related_items(related_items)
***REMOVED******REMOVED***related_items.to_csv(OUTPUT_FILE)

***REMOVED******REMOVED***# Optional graphing
***REMOVED******REMOVED***if CREATE_GRAPH_HTML and GRAPH_FILE is not None:
***REMOVED******REMOVED******REMOVED******REMOVED***import networkx as nx
***REMOVED******REMOVED******REMOVED******REMOVED***from pyvis.network import Network

***REMOVED******REMOVED******REMOVED******REMOVED***data_for_graph = related_items["Relationship Path"].tolist()
***REMOVED******REMOVED******REMOVED******REMOVED***list_of_unique_items_and_types = (
***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED***related_items["Related Item Type"].tolist()
***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED***+ related_items["Org item type"].tolist()
***REMOVED******REMOVED******REMOVED******REMOVED***)
***REMOVED******REMOVED******REMOVED******REMOVED***number_of_unique_item_types = len(set(list_of_unique_items_and_types))
***REMOVED******REMOVED******REMOVED******REMOVED***sorted_unique_item_types = sorted(set(list_of_unique_items_and_types))
***REMOVED******REMOVED******REMOVED******REMOVED***G = nx.Graph()
***REMOVED******REMOVED******REMOVED******REMOVED***for path in data_for_graph:
***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED***for index, item in enumerate(path):
***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED***item_ago = Item(gis_con, item)
***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED***item_type = classify_by_type_typekeywords(item_ago)
***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED***G.add_node(
***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED***item,
***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED***title=f"<p>Open <a href='{PORTAL}/home/item.html?id={item}'>{item_type}</a></p>",
***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED***label=f"{item_type}: {item_ago.title}",
***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED***color=COLOR_MAP[item_type],
***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED***)
***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED***nx.add_path(G, path)
***REMOVED******REMOVED******REMOVED******REMOVED***# if not running this script in a Notebook, make `notebook=False`
***REMOVED******REMOVED******REMOVED******REMOVED***net = Network(notebook=True, select_menu=True, filter_menu=True)
***REMOVED******REMOVED******REMOVED******REMOVED***net.from_nx(G)
***REMOVED******REMOVED******REMOVED******REMOVED***for node in net.nodes:
***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED***node["color"] = COLOR_MAP[
***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED***classify_by_type_typekeywords(Item(gis_con, node["id"]))
***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED***]
***REMOVED******REMOVED******REMOVED******REMOVED***for edge in net.edges:
***REMOVED******REMOVED******REMOVED******REMOVED******REMOVED******REMOVED***edge["color"] = "#0A0A0A"
***REMOVED******REMOVED******REMOVED******REMOVED***net.show(GRAPH_FILE)
