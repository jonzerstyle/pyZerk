import copy

class Class_Container():
  def __init__(self):
    self.text = []
    self.data = []
  def addItem(self, text, inData):
    itemFound = False
    #replace item if it already exists
    for i in (range(len(self.text))):
      if self.text[i] == text:
        self.data[i] = copy.deepcopy(inData)
        itemFound = True
        break
    #item not found append it
    if itemFound == False:
      self.data.append(copy.deepcopy(inData))
      self.text.append(copy.deepcopy(text))
  def getItem(self, text):
    for i in (range(len(self.text))):
      if self.text[i] == text:
        return self.data[i]
