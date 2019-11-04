#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd


# In[2]:


import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestClassifier


# In[3]:


from sklearn.svm import SVC
from sklearn import svm
from sklearn.neural_network import MLPClassifier


# In[4]:


from sklearn.metrics import confusion_matrix, classification_report
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split


# In[5]:


resistance = pd.read_csv('resistance.csv',sep=',')


# In[6]:


resistance.head()


# In[7]:


resistance.isnull().sum()


# In[8]:


resistance['isSpy'].value_counts()


# In[9]:


sns.countplot(resistance['isSpy'])


# In[10]:


X = resistance.drop('isSpy', axis=1)
y = resistance['isSpy']


# In[11]:


X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.2, random_state = 93)


# In[12]:


sc = StandardScaler()
X_train = sc.fit_transform(X_train)
X_test = sc.transform(X_test)


# In[13]:


X_train[:10]


# # Random Forest Classifier

# In[14]:


rfc = RandomForestClassifier(n_estimators=600)
rfc.fit(X_train, y_train)
pred_rfc = rfc.predict(X_test)


# In[15]:


X_test[:20]


# In[16]:


print(classification_report(y_test, pred_rfc))


# In[17]:


print(confusion_matrix(y_test, pred_rfc))


# # SVM Classifier

# In[18]:


clf = svm.SVC()
clf.fit(X_train, y_train)
pred_clf = clf.predict(X_test)


# In[19]:


print(classification_report(y_test, pred_clf))
print(confusion_matrix(y_test, pred_clf))


# # Neural Network

# In[20]:


mlpc = MLPClassifier(hidden_layer_sizes=(5,5,5),max_iter=200)
mlpc.fit(X_train, y_train)
pred_mlpc = mlpc.predict(X_test)


# In[21]:


print(classification_report(y_test, pred_mlpc))
print(confusion_matrix(y_test, pred_mlpc))


# In[22]:


from sklearn.metrics import accuracy_score
cm = accuracy_score(y_test, pred_rfc)
cm


# In[23]:


resistance.head(10)


# In[24]:


Xnew = [[5,0.75,0.5,0.33,0,1]]
Xnew = sc.transform(Xnew)


# In[25]:


ynew = rfc.predict(Xnew)
ynew


# In[26]:


import pickle
pickle_path = 'rfc_pickle.pkl'
rfc_pickle = open(pickle_path, 'wb')
pickle.dump(rfc, rfc_pickle)
rfc_pickle.close()


# In[27]:


sc_pickle = open('sc_pickle.pkl', 'wb')
pickle.dump(sc, sc_pickle)
sc_pickle.close()


# In[ ]:




