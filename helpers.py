from typing import Union, List, Dict, Optional

from settings import TOKEN


def build_body(method: str, param: Optional[Union[List, Dict]] = None, locale: Optional[str] = None) -> Dict:
    res = {
        "method": method,
        "token": TOKEN
    }
    if param:
        res.update({'param': param})
    if locale:
        res.update({'locale': locale})
    return res
