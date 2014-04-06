import binascii
import io
import json

try:
    from urllib2 import urlopen
except ImportError:
    from urllib.request import urlopen

from ..tx import Spendable


def payments_for_address(bitcoin_address):
    "return an array of (TX ids, net_payment)"
    URL = "https://blockchain.info/address/%s?format=json" % bitcoin_address
    d = urlopen(URL).read()
    json_response = json.loads(d.decode("utf8"))
    response = []
    for tx in json_response.get("txs", []):
        total_out = 0
        for tx_out in tx.get("out", []):
            if tx_out.get("addr") == bitcoin_address:
                total_out += tx_out.get("value", 0)
        if total_out > 0:
            response.append((tx.get("hash"), total_out))
    return response


def spendables_for_address(bitcoin_address):
    """
    Return a list of Spendable objects for the
    given bitcoin address.
    """
    URL = "http://blockchain.info/unspent?active=%s" % bitcoin_address
    r = json.loads(urlopen(URL).read().decode("utf8"))
    spendables = []
    for u in r["unspent_outputs"]:
        coin_value = u["value"]
        script = binascii.unhexlify(u["script"])
        previous_hash = binascii.unhexlify(u["tx_hash"])
        previous_index = u["tx_output_n"]
        spendables.append(Spendable(coin_value, script, previous_hash, previous_index))
    return spendables


def send_tx(tx):
    s = io.BytesIO()
    tx.stream(s)
    tx_as_hex = binascii.hexlify(s.getvalue()).decode("utf8")
    data = urllib.parse.urlencode(dict(tx=tx_as_hex)).encode("utf8")
    URL = "http://blockchain.info/pushtx"
    try:
        d = urlopen(URL, data=data).read()
        return d
    except urllib.error.HTTPError as ex:
        d = ex.read()
        import pdb; pdb.set_trace()
        print(ex)
