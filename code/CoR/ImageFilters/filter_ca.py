from pattern_ca.resolution_ca import Resolution
from pattern_ca.saturation_ca import Saturation
from pattern_ca.blur_ca import Blur
from pattern_ca.relighting_ca import Relighting
from request import Request


def configure_chain():
    res = Resolution()
    sat= Saturation()
    blur = Blur()
    rel = Relighting()

    res.set_next(sat).set_next(blur).set_next(rel)
    return res

def filter_ca(request:Request,co2_intensity:float,budgetCOR:float):
    chain = configure_chain()
    processed_immage = chain.apply_filter(request,co2_intensity,budgetCOR,0.0)
    return processed_immage