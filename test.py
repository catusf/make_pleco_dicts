import hanzipy

from hanzipy.decomposer import HanziDecomposer

decomposer = HanziDecomposer()


import chin_dict.chindict

decomposition = decomposer.tree("桂")
print(decomposition)
print(decomposition["tree"])
pass
