Requirements
------------

* Python (2 or 3)
* virtualenv
* pip

Setup
-----

1. Create a virtualenv (first `virtualenv .env`, then `source .env/bin/activate` on *nix or `.env\Scripts\activate` on Windows)
1. Install requirements (`pip install -r requirements.txt`)
1. `python www.py`


API
====

`/api/schedule`
---------------

Fetch the schedule. Defaults to ICS, use `?format=json` or `Accept: application/json` for a JSON return.

To filter the schedule, pass arguments like

    /api/schedule?faculty=eng-software,eng-computer&level=senior&status=co-op

For a full list of available filter keys and values, see `/api/filters`.

`/api/filters`
--------------

Returns a dict of available filter keys and values for `/api/schedule`. Filters are always specified by their `slug`, the other values returned are for display purposes only and may be unstable.
