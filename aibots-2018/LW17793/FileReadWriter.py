
class FileReadWriter:

    # Write to file.
    def writeToFile(self, trainingSet, fileName):
        with open(fileName, 'a') as txtFile:
            for pArray in trainingSet:
                for pInfo in pArray:
                    s = ""
                    for i in range(len(pInfo[0])):
                        s += str(pInfo[0][i])
                        if i < len(pInfo[0]) - 1:
                            s += ","
                        else:
                            s += ";"
                    for t in pInfo[1]:
                        s += str(t) + "\n"
                    txtFile.write(s)

    # Read from file.
    def readTrainingData(self, inputCount, fileName):
        array = []
        with open(fileName) as fp:
            lines = fp.read().split("\n")
            for l in lines:
                if l == "":
                    continue
                #print(l) # For debugging.
                s = l.split(";")
                splitter = s[0].split(",")
                if len(splitter) != inputCount:
                    continue
                #print(l) # For debugging.
                row = [splitter, [s[1]]]
                for i in range(len(row)):
                    for j in range(len(row[i])):
                        row[i][j] = float(row[i][j])
                array.append(row)
        return array
