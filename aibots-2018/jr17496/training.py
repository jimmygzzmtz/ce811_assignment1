from sklearn import tree
import numpy as np
import pickle

#preparation_list_x will contain the inputs for the decision tree
preparation_list_x = []
#preparation_list_y will contain the outputs for the decision tree
preparation_list_y = []

#Opening the file created by the bot to train the decision tree on it
with open('data_bots_ai.txt') as training_set:
    for line in training_set:
        training_set_line = line
        training_set_line_final = [x.strip() for x in training_set_line.split(',')]
        #formating the values from the txt file
        if (len(training_set_line_final) == 4):
            training_set_line_final[0] = int(training_set_line_final[0])
            training_set_line_final[1] = int(training_set_line_final[1])
            training_set_line_final[2] = float(training_set_line_final[2])
            training_set_line_final[3] = int(training_set_line_final[3])
            preparation_list_x.append([training_set_line_final[0],training_set_line_final[1],training_set_line_final[2]])
            preparation_list_y.append([training_set_line_final[3]])

X =preparation_list_x
Y = preparation_list_y
#chosing the method for learning the data set
clf = tree.DecisionTreeClassifier()
#passing the values to the Decision tree classifier
clf = clf.fit(X, Y)
pickle.dump(clf,open( "training_tree.p", "wb" ))