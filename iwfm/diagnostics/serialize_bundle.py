# serialize_bundle.py
# Serialize DiagnosticBundle to compact JSON
# Copyright (C) 2020-2026 University of California
# License: GNU GPL v2.0+

'''Serialize DiagnosticBundle to compact JSON.'''

import json
import math


def serialize_bundle(bundle, output_path=None, indent=2, max_list_items=15,
                     float_precision=3):
    """Convert DiagnosticBundle to compact JSON string.

    Parameters
    ----------
    bundle : DiagnosticBundle
        Assembled diagnostic bundle.
    output_path : str, optional
        If provided, write JSON to this file.
    indent : int
        JSON indentation.
    max_list_items : int
        Truncate lists longer than this.
    float_precision : int
        Round floats to this many decimal places.

    Returns
    -------
    str
        JSON string.
    """
    d = bundle.to_dict()
    d = _truncate_lists(d, max_list_items)
    d = _round_floats(d, float_precision)

    json_str = json.dumps(d, indent=indent, default=_json_default)

    if output_path:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(json_str)

    return json_str


def _truncate_lists(obj, max_items):
    """Recursively truncate lists to max_items."""
    if isinstance(obj, dict):
        return {k: _truncate_lists(v, max_items) for k, v in obj.items()}
    if isinstance(obj, list):
        truncated = [_truncate_lists(item, max_items) for item in obj[:max_items]]
        if len(obj) > max_items:
            truncated.append({'_truncated': len(obj) - max_items})
        return truncated
    return obj


def _round_floats(obj, precision):
    """Recursively round floats."""
    if isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return None
        return round(obj, precision)
    if isinstance(obj, dict):
        return {k: _round_floats(v, precision) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_round_floats(item, precision) for item in obj]
    return obj


def _json_default(obj):
    """Handle numpy types that leak through dataclasses.asdict()."""
    try:
        import numpy as np
        if isinstance(obj, (np.integer,)):
            return int(obj)
        if isinstance(obj, (np.floating,)):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
    except ImportError:
        pass
    raise TypeError(f'Object of type {type(obj)} is not JSON serializable')
