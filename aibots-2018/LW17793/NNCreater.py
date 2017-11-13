
from NeuralNetworkMLP import NeuralNetworkMLP
from FileReadWriter import FileReadWriter
from Files import Files

# Class that initialize and trains the neural network.
class NNCreater:

    # Neural network information.
    # [Number of input neurons, number of hidden neurons, number of output neurons].
    nnInfo = [10, 10, 1]

    # Read training set and start initial training for neural network.
    def initialTraining(self):
        trainingSet = FileReadWriter().readTrainingData(self.nnInfo[0], Files.trainingSet_txt)
        # Initialize the neural network.
        neuralNet = NeuralNetworkMLP(self.nnInfo)
        newTrainVal = neuralNet.divideTrainingSet(trainingSet)
        trainingSet = newTrainVal[0]
        validationSet = newTrainVal[1]
        # Train the network.
        neuralNet.initialTraining(trainingSet, validationSet)
        return neuralNet
