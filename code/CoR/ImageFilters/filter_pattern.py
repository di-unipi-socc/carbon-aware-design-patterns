from pattern.resolution import Resolution
from pattern.saturation import Saturation
from pattern.blur import Blur
from pattern.relighting import Relighting
from request import Request


def configure_chain():
    res = Resolution()
    sat= Saturation()
    blur = Blur()
    rel = Relighting()

    res.set_next(sat).set_next(blur).set_next(rel)
    return res

def filter(request:Request):
    chain = configure_chain()
    processed_immage = chain.apply_filter(request)
    return processed_immage