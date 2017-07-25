import keras
from keras.models import Sequential
from keras.layers import Dense, Activation

def main():
    model = ann()
    #import axelrod players
    #annotate with correct hypothetical outcome
    #try with one objective pair (selfish) at first
    #compile the model and crap
    print "Success"

def ann(weights=None):
    model = Sequential()
    #check to see if I want dense layer of 32
    model.add(Dense(32, input_shape=(6,)))
    model.add(Activation('relu'))
    model.add(Dense(16))
    model.add(Activation('relu'))
    model.add(Dense(8))
    model.add(Activation('relu'))
    model.add(Dense(2))
    model.add(Activation('softmax'))
    print model.summary()
    return model

if __name__ == "__main__":
    main();