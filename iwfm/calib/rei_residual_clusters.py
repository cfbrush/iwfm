# rei_residual_clusters.py
# Spatial residual-cluster summary from a PEST .rei file (any PEST engine)
# Copyright (C) 2026 University of California
# -----------------------------------------------------------------------------
# This information is free; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This work is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# For a copy of the GNU General Public License, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
# -----------------------------------------------------------------------------
"""Spatial residual-cluster summary from a PEST .rei file (any engine).

Works after any PEST/BEOPEST/pestpp/pypest run that produced a .rei —
including a NOPTMAX=0 forward-run-only case:

    python -m iwfm.calib.rei_residual_clusters --rei case.rei \
        --pst case.pst --gw-dat C2VSimCG_Groundwater1974.dat \
        --streams-dat C2VSimCG_Streams.dat [--json out.json]

Method: per-site weighted sum-of-squares from the .rei (site = obs name minus
a trailing _NNN time index); head-group sites located via the groundwater
file's hydrograph print table (NAME -> X, Y); worst sites clustered by
single-linkage within a distance threshold; each cluster mapped to nearby
adjustable parametric-grid parameters. Parameter coordinates come from the
groundwater file's parametric-grid table (rows `ID PX PY <values...>`) —
the node number embedded in a parametric param name (e.g. PKH042_L1) is
that table's node id. Stream-group gages map to stream nodes via the streams
file's hydrograph table and are matched to adjustable stream-conductance
params by stream-node proximity.
"""
import argparse
import json
import math
import re

_SITE_RE = re.compile(r'^(.*)_\d+$')
_DEFAULT_PARAM_NODE_RE = re.compile(r'^(pkh|pl|pn|pv|ps)0*(\d+)_l(\d)$')
_DEFAULT_CSN_RE = re.compile(r'^c_sn_0*(\d+)$')
_DEFAULT_ELEM_PARAM_RE = re.compile(r'^(kr|kp)_0*(\d+)$')
_DEFAULT_HEAD_GROUPS = ('gwhead', 'vhead')
_DEFAULT_STREAM_GROUPS = ('swflow',)


def _parse_rei(path):
    """Per-site stats; sum_wr keeps the SIGN so mean bias = sum_wr / n."""
    sites, total = {}, 0.0
    with open(path, encoding='utf-8', errors='replace') as f:
        for line in f:
            p = line.split()
            if len(p) < 6:
                continue
            try:
                wr = float(p[4]) * float(p[5])
            except ValueError:
                continue
            total += wr * wr
            m = _SITE_RE.match(p[0])
            site = m.group(1) if m else p[0]
            rec = sites.setdefault(site, {'group': p[1], 'n': 0,
                                          'sumsq': 0.0, 'sum_wr': 0.0})
            rec['n'] += 1
            rec['sumsq'] += wr * wr
            rec['sum_wr'] += wr
    return sites, total


def _parse_hydrograph_coords(gw_dat):
    coords = {}
    pat = re.compile(r'^\s*\d+\s+\d+\s+\d+\s+([0-9.]+)\s+([0-9.]+)\s+(\S+)\s*$')
    with open(gw_dat, encoding='utf-8', errors='replace') as f:
        for line in f:
            if line.lstrip().startswith(('C', 'c', '*', '#')):
                continue
            m = pat.match(line)
            if m:
                coords[m.group(3)] = (float(m.group(1)), float(m.group(2)))
    return coords


def _parse_stream_gages(streams_dat):
    """GAGE-NAME -> (stream node id, description)."""
    gages = {}
    pat = re.compile(r'^\s*(\d+)\s+(\S+)\s*/\s*(.*?)\s*$')
    with open(streams_dat, encoding='utf-8', errors='replace') as f:
        for line in f:
            if line.lstrip().startswith(('C', 'c', '*', '#')):
                continue
            m = pat.match(line)
            if m:
                gages[m.group(2)] = (int(m.group(1)), m.group(3))
    return gages


def _parse_parametric_node_coords(gw_dat):
    """Parametric-grid node id -> (PX, PY): rows `ID PX PY <values...>` with
    UTM-magnitude coordinates."""
    coords = {}
    with open(gw_dat, encoding='utf-8', errors='replace') as f:
        for line in f:
            if line.lstrip().startswith(('C', 'c', '*', '#')):
                continue
            p = line.split()
            if len(p) >= 4:
                try:
                    nid, x, y = int(p[0]), float(p[1]), float(p[2])
                except ValueError:
                    continue
                if 1e5 < x < 1e7 and 1e6 < y < 1e7 and nid not in coords:
                    coords[nid] = (x, y)
    return coords


def _parse_node_coords(nodes_dat):
    """FE node id -> (x, y)."""
    coords = {}
    with open(nodes_dat, encoding='utf-8', errors='replace') as f:
        for line in f:
            if line.lstrip().startswith(('C', 'c', '*', '#')):
                continue
            p = line.split()
            if len(p) >= 3:
                try:
                    coords[int(p[0])] = (float(p[1]), float(p[2]))
                except ValueError:
                    continue
    return coords


def _parse_element_centroids(elements_dat, nodes_dat):
    """Element id -> centroid (x, y) from element node connectivity.
    Element-indexed params (e.g. rootzone kr_NNNN, kp_NNNN) locate here."""
    nodes = _parse_node_coords(nodes_dat)
    cents = {}
    with open(elements_dat, encoding='utf-8', errors='replace') as f:
        for line in f:
            if line.lstrip().startswith(('C', 'c', '*', '#')):
                continue
            p = line.split()
            if len(p) >= 5:
                try:
                    ids = [int(v) for v in p[:5]]
                except ValueError:
                    continue
                xy = [nodes[n] for n in ids[1:5] if n > 0 and n in nodes]
                if len(xy) >= 3 and ids[0] not in cents:
                    cents[ids[0]] = (sum(c[0] for c in xy) / len(xy),
                                     sum(c[1] for c in xy) / len(xy))
    return cents


def _parse_adjustable_params(pst):
    names, in_par = [], False
    with open(pst, encoding='utf-8', errors='replace') as f:
        for line in f:
            s = line.strip()
            if s.startswith('*'):
                in_par = s.lower().startswith('* parameter data')
                continue
            if not in_par:
                continue
            p = s.split()
            if len(p) >= 7 and p[1].lower() not in ('fixed', 'tied'):
                names.append(p[0])
    return names


def _site_coords(site, hydro):
    if site in hydro:
        return hydro[site]
    for suffix in ('_L1', '_L2', '_L3', '_L4'):
        if site + suffix in hydro:
            return hydro[site + suffix]
    return None


def _cluster_sites(located, threshold):
    clusters = []
    for site, rec, xy in located:
        merged = None
        for cl in clusters:
            if any(math.dist(xy, oxy) <= threshold for _, _, oxy in cl):
                cl.append((site, rec, xy))
                merged = cl
                break
        if merged is None:
            clusters.append([(site, rec, xy)])
    changed = True
    while changed:
        changed = False
        for i in range(len(clusters)):
            for j in range(i + 1, len(clusters)):
                if any(math.dist(a[2], b[2]) <= threshold
                       for a in clusters[i] for b in clusters[j]):
                    clusters[i] += clusters[j]
                    del clusters[j]
                    changed = True
                    break
            if changed:
                break
    return clusters


def _parse_tied_families(pst):
    """{parent: [child, ...]} from two-field lines in * parameter data."""
    fams, in_par = {}, False
    with open(pst, encoding='utf-8', errors='replace') as f:
        for line in f:
            s = line.strip()
            if s.startswith('*'):
                in_par = s.lower().startswith('* parameter data')
                continue
            if not in_par:
                continue
            p = s.split()
            if len(p) == 2:
                fams.setdefault(p[1], []).append(p[0])
    return fams


def _locate_param(name, pnodes, ecents):
    """(x, y) for any parametric or element-indexed param name, else None."""
    m = _DEFAULT_PARAM_NODE_RE.match(name.lower())
    if m and int(m.group(2)) in pnodes:
        return pnodes[int(m.group(2))]
    m = _DEFAULT_ELEM_PARAM_RE.match(name.lower())
    if m and int(m.group(2)) in ecents:
        return ecents[int(m.group(2))]
    return None


def _find_split_worthy_families(sites, hydro, families, adjustable, pnodes,
                                ecents, total, head_groups, attribute_km=25.0,
                               min_members=8, min_sites_per_side=2,
                               min_separation_km=10.0, max_report=5):
    """Families whose footprint shows OPPOSITE-SIGN head bias in two
    spatially separated sub-regions — one tied value compromising between
    a too-high and a too-low zone. Returns ranked suggestions with the
    member partition (maps onto a supervisor split_zones action)."""
    # located head sites with signed mean bias
    obs = []
    for s, r in sites.items():
        if r['group'] not in head_groups:
            continue
        xy = _site_coords(s, hydro)
        if xy:
            obs.append((s, r, xy, r['sum_wr'] / max(r['n'], 1)))
    if not obs:
        return []
    global_bias = (sum(abs(b) * r['sumsq'] for _, r, _, b in obs)
                   / max(sum(r['sumsq'] for _, r, _, _ in obs), 1e-30))

    out = []
    for parent in adjustable:
        members = [parent] + families.get(parent, [])
        mem_xy = {m: xy for m in members
                  if (xy := _locate_param(m, pnodes, ecents))}
        if len(mem_xy) < min_members:
            continue
        # attribute each obs site to its nearest member (within radius)
        mem_obs = {}
        fam_phi = 0.0
        for s, r, xy, bias in obs:
            best = min(mem_xy.items(), key=lambda kv: math.dist(xy, kv[1]))
            if math.dist(xy, best[1]) <= attribute_km * 1000.0:
                mem_obs.setdefault(best[0], []).append((r['sumsq'], bias))
                fam_phi += r['sumsq']
        # phi-weighted bias per member with observations
        mem_bias = {m: sum(w * b for w, b in v) / max(sum(w for w, _ in v), 1e-30)
                    for m, v in mem_obs.items()}
        pos = [m for m, b in mem_bias.items() if b > 0.3 * global_bias]
        neg = [m for m, b in mem_bias.items() if b < -0.3 * global_bias]
        if len(pos) < min_sites_per_side or len(neg) < min_sites_per_side:
            continue

        def centroid(ms):
            return (sum(mem_xy[m][0] for m in ms) / len(ms),
                    sum(mem_xy[m][1] for m in ms) / len(ms))

        cp, cn = centroid(pos), centroid(neg)
        sep_km = math.dist(cp, cn) / 1000.0
        if sep_km < min_separation_km:
            continue
        # partition ALL located members by nearest signed centroid
        side_a = sorted(m for m in mem_xy
                        if math.dist(mem_xy[m], cp) <= math.dist(mem_xy[m], cn))
        side_b = sorted(m for m in mem_xy if m not in set(side_a))
        wb = lambda ms: (sum(mem_bias.get(m, 0.0) *
                             sum(w for w, _ in mem_obs.get(m, [])) for m in ms)
                         / max(sum(sum(w for w, _ in mem_obs.get(m, []))
                                   for m in ms), 1e-30))
        # coherence gate: the spatial partition must actually separate the
        # sign groups — if both sides average the same sign, the family has
        # regional bias (a value/bounds problem), not split-worthy contrast.
        if wb(side_a) * wb(side_b) >= 0:
            continue
        out.append({
            'parent': parent,
            'n_members_located': len(mem_xy),
            'phi_share_pct': round(100.0 * fam_phi / total, 2),
            'bias_contrast': {
                'side_a': {'n_members': len(side_a),
                           'mean_bias': round(wb(side_a), 2),
                           'members_sample': side_a[:8]},
                'side_b': {'n_members': len(side_b),
                           'mean_bias': round(wb(side_b), 2),
                           'members_sample': side_b[:8]},
                'separation_km': round(sep_km, 1)},
            'suggestion': (f'One tied value serves zones biased '
                           f'{wb(side_a):+.1f} vs {wb(side_b):+.1f} '
                           f'{sep_km:.0f} km apart - a split_zones on '
                           f'{parent} (k=2) along this partition lets each '
                           f'side calibrate independently.'),
        })
    out.sort(key=lambda d: -d['phi_share_pct'])
    return out[:max_report]



def _find_split_worthy_stream_families(sites, gages, families, adjustable,
                                       total, stream_groups, stream_param_re,
                                       min_node_sep=2,
                                      attribute_window=10, max_report=5):
    """Stream-conductance (c_sn_*) families whose gages show OPPOSITE-SIGN
    flow bias along the reach. 1-D analog of the head-family advisor:
    members and gages live on the stream-node sequence, so 'separation' is
    counted in stream nodes (reaches are short - little km separation)."""
    gaged = []
    for s, r in sites.items():
        if r['group'] not in stream_groups or s not in gages:
            continue
        gaged.append((s, gages[s][0], r['sum_wr'] / max(r['n'], 1), r['sumsq']))
    if len(gaged) < 2:
        return []
    # robust magnitude scale: the median |bias| (a phi-weighted mean would be
    # dominated by a few giant-residual gages and mask all contrast)
    abs_biases = sorted(abs(b) for _, _, b, _ in gaged)
    scale = max(abs_biases[len(abs_biases) // 2], 0.5)

    out = []
    for parent in adjustable:
        pm = stream_param_re.match(parent.lower())
        if not pm:
            continue
        members = [(int(m.group(1)), name)
                   for name in [parent] + families.get(parent, [])
                   if (m := stream_param_re.match(name.lower()))]
        members.sort()
        if len(members) < 4:
            continue
        lo, hi = members[0][0], members[-1][0]
        fam_gages = [(s, n, b, w) for s, n, b, w in gaged
                     if lo - attribute_window <= n <= hi + attribute_window]
        pos = [g for g in fam_gages if g[2] > scale]
        neg = [g for g in fam_gages if g[2] < -scale]
        if not pos or not neg:
            continue
        # strongest opposite pair, separated along the node sequence
        gp = max(pos, key=lambda g: abs(g[2]) * g[3])
        gn = max(neg, key=lambda g: abs(g[2]) * g[3])
        node_sep = abs(gp[1] - gn[1])
        if node_sep < min_node_sep:
            continue
        mid = (gp[1] + gn[1]) / 2.0
        side_a = [name for i, name in members if i <= mid]
        side_b = [name for i, name in members if i > mid]
        fam_phi = sum(w for _, _, _, w in fam_gages)
        out.append({
            'parent': parent,
            'n_members': len(members),
            'member_node_range': [lo, hi],
            'phi_share_pct': round(100.0 * fam_phi / total, 2),
            'gage_contrast': [
                {'gage': gp[0], 'node': gp[1], 'mean_bias': round(gp[2], 2)},
                {'gage': gn[0], 'node': gn[1], 'mean_bias': round(gn[2], 2)}],
            'node_separation': node_sep,
            'suggested_partition': {
                'boundary_node': round(mid),
                'side_a_members': side_a[:8],
                'side_b_members': side_b[:8]},
            'suggestion': (f'Gages {gp[0]} (node {gp[1]}, bias {gp[2]:+.1f}) '
                           f'and {gn[0]} (node {gn[1]}, bias {gn[2]:+.1f}) '
                           f'disagree in sign along this reach family - '
                           f'split {parent} at ~node {round(mid)} so each '
                           f'sub-reach calibrates its own conductance.'),
        })
    out.sort(key=lambda d: -d['phi_share_pct'])
    return out[:max_report]



def rei_residual_clusters(rei, pst, gw_dat, streams_dat,
                          elements_dat=None, nodes_dat=None,
                          head_groups=_DEFAULT_HEAD_GROUPS,
                          stream_groups=_DEFAULT_STREAM_GROUPS,
                          param_node_re=_DEFAULT_PARAM_NODE_RE,
                          stream_param_re=_DEFAULT_CSN_RE,
                          elem_param_re=_DEFAULT_ELEM_PARAM_RE,
                          top_sites=150, cluster_km=30.0, max_clusters=6,
                          param_radius_km=60.0, stream_node_window=15):
    """Return a dict summarizing where misfit concentrates spatially and
    which adjustable parameters overlie it. See module docstring.

    elements_dat + nodes_dat (both required together, optional): also locate
    element-indexed params (rootzone kr_/kp_) at element centroids."""
    sites, total = _parse_rei(rei)
    hydro = _parse_hydrograph_coords(gw_dat)
    gages = _parse_stream_gages(streams_dat)
    pnodes = _parse_parametric_node_coords(gw_dat)
    ecents = {}
    if elements_dat and nodes_dat:
        ecents = _parse_element_centroids(elements_dat, nodes_dat)
    adjustable = _parse_adjustable_params(pst)

    param_xy, stream_ids = {}, {}
    for name in adjustable:
        m = param_node_re.match(name.lower())
        if m and int(m.group(2)) in pnodes:
            param_xy[name] = pnodes[int(m.group(2))]
            continue
        m = elem_param_re.match(name.lower())
        if m and int(m.group(2)) in ecents:
            param_xy[name] = ecents[int(m.group(2))]
            continue
        m = stream_param_re.match(name.lower())
        if m:
            stream_ids[name] = int(m.group(1))

    head_sites = sorted(
        ((s, r) for s, r in sites.items() if r['group'] in head_groups),
        key=lambda kv: -kv[1]['sumsq'])[:top_sites]
    located = []
    for s, r in head_sites:
        xy = _site_coords(s, hydro)
        if xy:
            located.append((s, r, xy))
    clusters = _cluster_sites(located, cluster_km * 1000.0)
    clusters.sort(key=lambda cl: -sum(m[1]['sumsq'] for m in cl))

    out_clusters = []
    for cl in clusters[:max_clusters]:
        sumsq = sum(m[1]['sumsq'] for m in cl)
        cx = sum(m[2][0] for m in cl) / len(cl)
        cy = sum(m[2][1] for m in cl) / len(cl)
        near = [(n, xy) for n, xy in sorted(
                    param_xy.items(),
                    key=lambda kv: math.dist((cx, cy), kv[1]))
                if math.dist((cx, cy), xy) <= param_radius_km * 1000.0][:6]
        top = sorted(cl, key=lambda m: -m[1]['sumsq'])[:5]
        out_clusters.append({
            'phi_share_pct': round(100.0 * sumsq / total, 2),
            'n_sites': len(cl),
            'groups': sorted({m[1]['group'] for m in cl}),
            'centroid_xy': [round(cx), round(cy)],
            'extent_km': round(max((math.dist(m[2], (cx, cy)) for m in cl))
                               / 1000.0, 1),
            'worst_sites': [{'site': s, 'group': r['group'],
                             'sumsq': round(r['sumsq'])} for s, r, _ in top],
            'nearest_adjustable_params': ([
                {'name': n,
                 'dist_km': round(math.dist((cx, cy), xy) / 1000.0, 1)}
                for n, xy in near] or
                f'NONE within {param_radius_km:.0f} km - no adjustable '
                'parametric param covers this cluster; consider zone splits '
                'or human review'),
        })

    stream_sites = sorted(
        ((s, r) for s, r in sites.items() if r['group'] in stream_groups),
        key=lambda kv: -kv[1]['sumsq'])[:10]
    out_streams = []
    for s, r in stream_sites:
        node, desc = gages.get(s, (None, ''))
        near_sp = []
        if node is not None:
            near_sp = [n for n, i in sorted(stream_ids.items(),
                                            key=lambda kv: abs(kv[1] - node))
                       if abs(stream_ids[n] - node) <= stream_node_window][:6]
        out_streams.append({'gage': s, 'description': desc,
                            'stream_node': node,
                            'phi_share_pct': round(100.0 * r['sumsq'] / total, 2),
                            'mean_bias': round(r['sum_wr'] / max(r['n'], 1), 2),
                            'nearby_adjustable_stream_params': near_sp})

    families = _parse_tied_families(pst)
    split_worthy = _find_split_worthy_families(
        sites, hydro, families, adjustable, pnodes, ecents, total,
        head_groups)
    split_worthy_stream = _find_split_worthy_stream_families(
        sites, gages, families, adjustable, total, stream_groups,
        stream_param_re)

    group_phi = {}
    for r in sites.values():
        group_phi[r['group']] = group_phi.get(r['group'], 0.0) + r['sumsq']

    return {
        'source_rei': rei,
        'total_phi': round(total),
        'group_phi_share_pct': {g: round(100.0 * v / total, 1)
                                for g, v in sorted(group_phi.items())},
        'note': ('Worst-fit observation sites clustered spatially from the '
                 'latest residuals. Each stream gage lists adjustable '
                 'stream-conductance params near the gage stream node; each '
                 'head cluster lists the nearest adjustable parametric '
                 'params. Use to aim bound widenings and zone splits at the '
                 'residual mass.'),
        'head_clusters': out_clusters,
        'stream_gages': out_streams,
        'split_worthy_families': split_worthy,
        'split_worthy_stream_families': split_worthy_stream,
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--rei', required=True)
    ap.add_argument('--pst', required=True)
    ap.add_argument('--gw-dat', required=True,
                    help='groundwater main file (hydrograph + parametric tables)')
    ap.add_argument('--streams-dat', required=True,
                    help='streams main file (gage hydrograph table)')
    ap.add_argument('--elements-dat', default=None,
                    help='elements file: with --nodes-dat, also locates '
                         'element-indexed params (rootzone kr_/kp_)')
    ap.add_argument('--nodes-dat', default=None,
                    help='FE node coordinates file (used with --elements-dat)')
    ap.add_argument('--json', default=None, help='also write JSON here')
    args = ap.parse_args()

    s = rei_residual_clusters(args.rei, args.pst, args.gw_dat,
                              args.streams_dat, elements_dat=args.elements_dat,
                              nodes_dat=args.nodes_dat)
    if args.json:
        with open(args.json, 'w', encoding='utf-8') as f:
            json.dump(s, f, indent=2)
    print(f"total phi {s['total_phi']:,}  groups {s['group_phi_share_pct']}")
    for i, c in enumerate(s['head_clusters']):
        print(f"\ncluster {i}: {c['phi_share_pct']}% of phi, {c['n_sites']} "
              f"sites ({'/'.join(c['groups'])}), extent {c['extent_km']} km")
        print(f"  worst: {', '.join(w['site'] for w in c['worst_sites'])}")
        pl = c['nearest_adjustable_params']
        print('  params:', ', '.join(f"{p['name']} @{p['dist_km']}km"
                                     for p in pl) if isinstance(pl, list) else pl)
    print('\nstream gages:')
    for g in s['stream_gages'][:6]:
        print(f"  {g['gage']:6s} node {g['stream_node']}  "
              f"{g['phi_share_pct']}%  "
              f"params: {', '.join(g['nearby_adjustable_stream_params']) or '(none nearby)'}")


if __name__ == '__main__':
    main()
