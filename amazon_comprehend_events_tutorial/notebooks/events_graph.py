"""
Helper functions and constants for Comprehend Events semantic network graphing.
"""

from collections import Counter
from matplotlib import cm, colors
import networkx as nx
from pyvis.network import Network


ENTITY_TYPES = ['DATE', 'FACILITY', 'LOCATION', 'MONETARY_VALUE', 'ORGANIZATION',
                'PERSON', 'PERSON_TITLE', 'QUANTITY', 'STOCK_CODE']

TRIGGER_TYPES = ['BANKRUPTCY', 'EMPLOYMENT', 'CORPORATE_ACQUISITION', 
                 'INVESTMENT_GENERAL', 'CORPORATE_MERGER', 'IPO', 'RIGHTS_ISSUE', 
                 'SECONDARY_OFFERING', 'SHELF_OFFERING', 'TENDER_OFFERING', 'STOCK_SPLIT']

PROPERTY_MAP = {
    "event": {"size": 10, "shape": "box", "color": "#dbe3e5"},
    "entity_group": {"size": 6, "shape": "dot", "color": "#776d8a"},
    "entity": {"size": 4, "shape": "square", "color": "#f3e6e3"},
    "trigger": {"size": 4, "shape": "diamond", "color": "#f3e6e3"}
}

def get_color_map(tags):
    spectral = cm.get_cmap("Spectral", len(tags))
    tag_colors = [colors.rgb2hex(spectral(i)) for i in range(len(tags))]
    color_map = dict(zip(*(tags, tag_colors)))
    color_map.update({'ROLE': 'grey'})
    return color_map

COLOR_MAP = get_color_map(ENTITY_TYPES + TRIGGER_TYPES)
COLOR_MAP['ROLE'] = "grey"

IFRAME_DIMS = ("600", "800")


def get_canonical_mention(mentions, method="longest"):
    extents = enumerate([m['Text'] for m in mentions])
    if method == "longest":
        name = sorted(extents, key=lambda x: len(x[1]))
    elif method == "most_common": 
        name = [Counter(extents).most_common()[0][0]]
    else:
        name = [list(extents)[0]]
    return [mentions[name[-1][0]]]


def get_nodes_and_edges(
    result, node_types=['event', 'trigger', 'entity_group', 'entity'], thr=0.0
    ):
    """Convert results to (nodelist, edgelist) depending on specified entity types."""
    nodes = []
    edges = []
    event_nodes = []
    entity_nodes = []  
    entity_group_nodes = [] 
    trigger_nodes = []
    
    # Nodes are (id, type, tag, score, mention_type) tuples.
    if 'event' in node_types:
        event_nodes = [
            (
                "ev%d" % i,
                 t['Type'],
                 t['Type'],
                 t['Score'],
                 "event"
            )
            for i, e in enumerate(result['Events'])
            for t in e['Triggers'][:1]
            if t['GroupScore'] > thr
        ]
        nodes.extend(event_nodes)
    
    if 'trigger' in node_types:
        trigger_nodes = [
            (
                "ev%d-tr%d" % (i, j),
                t['Type'],
                t['Text'],
                t['Score'],
                "trigger"
            )
            for i, e in enumerate(result['Events'])
            for j, t in enumerate(e['Triggers'])
            if t['Score'] > thr
        ]
        trigger_nodes = list({t[1:3]: t for t in trigger_nodes}.values())
        nodes.extend(trigger_nodes)
        
    if 'entity_group' in node_types:
        entity_group_nodes = [
            (
                "gr%d" % i,
                m['Type'],
                m['Text'] if 'entity' not in node_types else m['Type'],
                m['Score'],
                "entity_group"
            )
            for i, e in enumerate(result['Entities'])
            for m in get_canonical_mention(e['Mentions'])
            if m['GroupScore'] > thr
        ]
        nodes.extend(entity_group_nodes)
        
    if 'entity' in node_types:
        entity_nodes = [
            (
                "gr%d-en%d" % (i, j),
                m['Type'],
                m['Text'],
                m['Score'],
                "entity"
            )
            for i, e in enumerate(result['Entities'])
            for j, m in enumerate(e['Mentions'])
            if m['Score'] > thr
        ]
        entity_nodes = list({t[1:3]: t for t in entity_nodes}.values())
        nodes.extend(entity_nodes)

    # Edges are (trigger_id, node_id, role, score, type) tuples.
    if event_nodes and entity_group_nodes:
        edges.extend([
            ("ev%d" % i, "gr%d" % a['EntityIndex'], a['Role'], a['Score'], "argument")
            for i, e in enumerate(result['Events'])
            for j, a in enumerate(e['Arguments'])
            #if a['Score'] > THR
        ])
    
    if entity_nodes and entity_group_nodes:
        entity_keys = set([n[0] for n in entity_nodes])
        edges.extend([
            ("gr%d" % i, "gr%d-en%d" % (i, j), "", m['GroupScore'], "coref")
            for i, e in enumerate(result['Entities'])
            for j, m in enumerate(e['Mentions'])
            if "gr%d-en%d" % (i, j) in entity_keys
            if m['GroupScore'] > thr
        ])

    if event_nodes and trigger_nodes:
        trigger_keys = set([n[0] for n in trigger_nodes])
        edges.extend([
            ("ev%d" % i, "ev%d-tr%d" % (i, j), "", a['GroupScore'], "coref")
            for i, e in enumerate(result['Events'])
            for j, a in enumerate(e['Triggers'])
            if "ev%d-tr%d" % (i, j) in trigger_keys
            if a['GroupScore'] > thr
        ])
        
    return nodes, edges


def build_network_graph(nodelist, edgelist, drop_isolates=True):
    G = nx.Graph()
    # Iterate over triggers and entity mentions.
    for mention_id, tag, extent, score, mtype in nodelist:
        G.add_node(
            mention_id,
            label=extent,
            tag=tag,
            group=mtype,
            size=PROPERTY_MAP[mtype]['size'],
            color=COLOR_MAP[tag],
            shape=PROPERTY_MAP[mtype]['shape']
            )
    # Iterate over argument role assignments
    if edgelist:
        for n1_id, n2_id, role, score, etype in edgelist:
            label = role if etype == "argument" else "coref"
            G.add_edges_from(
                [(n1_id, n2_id)],
                label=role,
                weight=score*100,
                color="grey"
            )
    # Drop mentions that don't participate in events
    if len(edgelist) > 0 and drop_isolates:
        G.remove_nodes_from(list(nx.isolates(G)))
    return G


def plot(result, node_types, filename="nx.html", thr=0.0):
    nodes, edges = get_nodes_and_edges(result, node_types, thr)
    G = build_network_graph(
        nodes, edges,
        drop_isolates=True
    )
    nt = Network(*IFRAME_DIMS, notebook=True, heading="")
    nt.from_nx(G)
    display(nt.show(filename))