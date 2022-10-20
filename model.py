import pickle

class Model:
    def __init__(self):
        pass

    def get_comport(self):
        try:
            with open('data/comport.pkl', 'rb') as file:
                myvar = pickle.load(file)
                return myvar
        except:
            return""

    def put_comport(self,comport):
        myvar=comport
        with open('data/comport.pkl', 'wb') as file:
            pickle.dump(myvar, file)














