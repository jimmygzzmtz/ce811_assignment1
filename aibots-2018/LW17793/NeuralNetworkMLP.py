# Made by 'Lars Christian Wiik'
import math
import random
import copy
import time

import numpy as np


class NeuralNetworkMLP:
    # Weights
    # each row = all weights going out from that Neuron
    # - Weights from input layer to hidden layer
    hiddenWeights = None
    # - Weights from hidden layer to output layer
    outputWeights = None
    # Training and Validation sets
    trainingSet = None
    # Bias.
    biasValue = -1
    # Learning rate.
    n = 0.1
    k = 1

    stopMultiplier = 1.03
    iterationsPerValidation = 1000
    maxValidationSize = 300
    minimumTrainingIteration = 5

# ---------- INIT ----------

    def __init__(self, neuralNetInfo):
        # ----- Initilize Weights -----
        def computeWVal(n):
            return [(-1 / math.sqrt(n)), (1 / math.sqrt(n))]

        def makeRandomArray(rndFromTo, rowCount, columnCount):
            row = []
            for r in range(rowCount):
                column = []
                for c in range(columnCount):
                    column.append(random.uniform(rndFromTo[0], rndFromTo[1]))
                row.append(column)
            return np.array(row)

        # Initilize input-hidden weights
        wValRange = computeWVal(neuralNetInfo[0])
        # +1 because of bias in input and hidden layer
        self.hiddenWeights = makeRandomArray(wValRange, neuralNetInfo[1], neuralNetInfo[0] + 1)

        # Initilize hidden-output weights
        wValRange = computeWVal(neuralNetInfo[1])
        # +1 because of bias in input and hidden layer
        self.outputWeights = makeRandomArray(wValRange, neuralNetInfo[2], neuralNetInfo[1] + 1)

# ---------- Code ----------

    # Calculate activation function.
    def activationFunction(self, fromSet, weights):
        # Activation function.
        def sigmoidFunction(sumMatrix):
            return 1/(1 + math.e**(-self.k*sumMatrix))

        sumMatrix = np.dot(np.transpose(fromSet), np.transpose(weights))
        return sigmoidFunction(sumMatrix)

    # Forward.
    def forward(self, inSet):
        inputSet = np.array(inSet)
        inputSet = np.append(inputSet, self.biasValue)
        # calculate activation function in hidden
        hiddenSet = self.activationFunction(inputSet, self.hiddenWeights)
        hiddenSet = np.append(hiddenSet, self.biasValue)  # bias
        # calculate activation function in output nodes
        outputSet = self.activationFunction(hiddenSet, self.outputWeights)
        return [inputSet, hiddenSet, outputSet]

    # Calculate error.
    def errorFunction(self, outputs, target):
        errorSum = 0
        for k in range(0, len(outputs)):
            errorSum += ((target[k] - outputs[k]) ** 2)
        errorSum *= 0.5
        return errorSum

    def backwards(self, inputs, hiddens, outputs, targets):
        # y = output, t = target
        def calculateDeltaO(y, t):
            return (y - t) * y* (1 - y)

        # a = activationFunction from hidden
        def calculateDeltaH(deltaO, a, outputW):
            return a * (1 - a) * (np.dot(deltaO, outputW))

        def calculateNewWeights(pastLayer, weights, delta):
            dotting = np.dot(np.transpose([pastLayer]), [delta])
            weights = weights - self.n * np.transpose(dotting)
            return weights

        # Calulate deltas.
        deltaO = calculateDeltaO(outputs, targets)
        deltaH = calculateDeltaH(deltaO, hiddens, self.outputWeights)
        # Remove the bias deltaH.
        deltaH = deltaH[:len(deltaH)-1]

        # Update weights.
        self.outputWeights = calculateNewWeights(hiddens, self.outputWeights, deltaO)
        self.hiddenWeights = calculateNewWeights(inputs, self.hiddenWeights, deltaH)

    # Train.
    def initialTraining(self, tSet, vSet):
        trainingSet = copy.copy(tSet)
        validationSet = copy.copy(vSet)

        counter = 0
        while True:
            '''
            print("Lars Neural Net Training Validation Test: "
                + str(counter) + ".    "
                + str(errorFuncSum - errorFuncSumValidation))
            '''
            errorFuncSum = 0
            errorFuncSumValidation = 0

            # Train
            for _ in range(self.iterationsPerValidation):
                # pick random training set
                rnd = random.randrange(len(trainingSet))
                rndSet = copy.copy(trainingSet[rnd])
                inputNeurons = np.array(copy.copy(rndSet[0]))
                targets = np.array(copy.copy(rndSet[1]))

                # Forward.
                forwardResult = self.forward(inputNeurons)
                inputNeurons = forwardResult[0]
                hiddenNeurons = forwardResult[1]
                outputNeurons = forwardResult[2]

                # Error function.
                errorFunc = self.errorFunction(outputNeurons, targets)
                errorFuncSum += errorFunc

                # Backward.
                self.backwards(inputNeurons, hiddenNeurons, outputNeurons, targets)

            # Validate
            for _ in range(self.iterationsPerValidation):
                # pick random training set
                rnd = random.randrange(len(validationSet))
                rndSet = copy.copy(validationSet[rnd])
                inputNeurons = np.array(copy.copy(rndSet[0]))
                targets = np.array(copy.copy(rndSet[1]))

                # Forward.
                forwardResult = self.forward(inputNeurons)
                inputNeurons = forwardResult[0]
                hiddenNeurons = forwardResult[1]
                outputNeurons = forwardResult[2]

                # Error function.
                errorFunc = self.errorFunction(outputNeurons, targets)
                errorFuncSumValidation += errorFunc

            if ((errorFuncSumValidation > errorFuncSum * self.stopMultiplier and
                counter >= self.minimumTrainingIteration) or
                counter > 15):
                #print("errorFuncSum = " + str(errorFuncSum))
                #print("errorFuncSumValidation = " + str(errorFuncSumValidation))
                break

            counter += 1

    # Train neural netowork with no validation set.
    def train(self, inputTargets, n):
        self.n = n

        for data in inputTargets:
            inputNeurons = data[0]
            targets = data[1]

            # Forward.
            forwardResult = self.forward(inputNeurons)
            inputNeurons = forwardResult[0]
            hiddenNeurons = forwardResult[1]
            outputNeurons = forwardResult[2]

            # Backward.
            self.backwards(inputNeurons, hiddenNeurons, outputNeurons, targets)

    # Divides training set into training and validation set.
    def divideTrainingSet(self, trainSet):
        trainingSet = copy.copy(trainSet)
        validationSet = []
        for row in trainingSet:
            rnd = random.randrange(len(trainingSet))
            rndSet = copy.copy(trainingSet[rnd])
            validationSet.append(rndSet)
            trainingSet = [r for r in trainingSet if r != rndSet]
            if len(validationSet) >= len(trainingSet) * 0.1 or len(validationSet) > self.maxValidationSize:
                break

        return [trainingSet, validationSet]

    # Make a prediction.
    def predict(self, inSet):
        forwardResult = self.forward(inSet)
        outputNeurons = forwardResult[2]
        output = outputNeurons[len(outputNeurons)-1]
        return output
