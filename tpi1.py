from tree_search import *
from cidades import *

class MyNode(SearchNode):
    def __init__(self,state,parent,arg3=None,arg4=None,arg5=None):
        super().__init__(state,parent)

class MyTree(SearchTree):

    def __init__(self,problem, strategy='breadth',seed=0): 
        super().__init__(problem,strategy,seed)

    def astar_add_to_open(self,lnewnodes):
        #IMPLEMENT HERE
        pass

    def propagate_eval_upwards(self,node):
        #IMPLEMENT HERE
        pass

    def search2(self,atmostonce=False):
        #IMPLEMENT HERE
        pass

    def repeated_random_depth(self,numattempts=3,atmostonce=False):
        #IMPLEMENT HERE
        pass

    def make_shortcuts(self):
        #IMPLEMENT HERE
        pass



class MyCities(Cidades):

    def maximum_tree_size(self,depth):   # assuming there is no loop prevention
        #IMPLEMENT HERE
        pass


