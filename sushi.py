#!/usr/bin/python
import Queue
import threading
import sys
from time import sleep
#
####################################################################################
# Initialize Section
####################################################################################
consCount = Queue.Queue(maxsize=0)
dropCount = Queue.Queue(maxsize=0)
counter = Queue.Queue(maxsize=100)
itemEaten = False
numberOfFish = 0
numberofVegi = 0
custFish = 0
custVegi = 0
custEgal = 0
custCat = 0
# Beware of the limitations (if we have more than 10, we append an integer for uniqueness)
catNames = ['Schroedinger', 'Spot', 'Garfield' , 'Einstein', 'Hawking', 'Socrates', 'Heisenberg', 'Archimedes', 'Newton', 'Leibnitz']
humanNames = ['Kirk', 'Picard', 'Riker', 'Janeway', 'Scotty', 'Seven of Nine', 'Data', 'Sulu', 'Chekov', 'McCoy']
#
####################################################################################
# Display Message
####################################################################################
def writeMsg(logMsg):
  print >>sys.stderr, logMsg, # Tailing "," to indicate no implicit EOL
#
####################################################################################
# Command line arguments
####################################################################################
numberOfArguments = len(sys.argv)
arrayofArguments = str(sys.argv)
for argIndex in range(1,numberOfArguments):
  inputString = str(sys.argv[argIndex])
  if inputString[0] == "-" and inputString[2] == "=":
    # Production limits
    if inputString[1] == "a":
      try:
        numberOfFish = int(inputString[3:len(inputString)])
      except ValueError:
        numberOfFish = 0
    if inputString[1] == "b":
      try:
        numberofVegi = int(inputString[3:len(inputString)])
      except ValueError:
        numberofVegi = 0
    # Consumers
    if inputString[1] == "f":
      try:
        custFish = int(inputString[3:len(inputString)])
      except ValueError:
        custFish = 0
    if inputString[1] == "v":
      try:
        custVegi = int(inputString[3:len(inputString)])
      except ValueError:
        custVegi = 0
    if inputString[1] == "e":
      try:
        custEgal = int(inputString[3:len(inputString)])
      except ValueError:
        custEgal = 0
    if inputString[1] == "c":
      try:
        custCat = int(inputString[3:len(inputString)])
      except ValueError:
        custCat = 0
#
####################################################################################
# User Input during run-time
####################################################################################
if numberOfArguments == 1: # Only ask user if we have no command line parameters
  # Production limits
  x = raw_input('How many fish Sushi will be produced?       ')
  if x > 0:
    try:
      numberOfFish = int(x)
    except ValueError:
      numberOfFish = 0
  x = raw_input('How many vegetarian Sushi will be produced? ')
  if x > 0:
    try:
      numberofVegi = int(x)
    except ValueError:
      numberofVegi = 0
  # Consumers
  x = raw_input('How many customers perfer fish?       ')
  if x > 0:
    try:
      custFish = int(x)
    except ValueError:
      custFish = 0
  x = raw_input('How many customers perfer vegetarian? ')
  if x > 0:
    try:
      custVegi = int(x)
    except ValueError:
      custVegi = 0
  x = raw_input('How many customers how no preference? ')
  if x > 0:
    try:
      custEgal = int(x)
    except ValueError:
      custEgal = 0
  x = raw_input('How many cats are in the restaurant?  ')
  if x > 0:
    try:
      custCat = int(x)
    except ValueError:
      custCat = 0
#
####################################################################################
# Producer
####################################################################################
def producer(producerID):
  logMsg = ""
  produceSushi = True
  produceMaximum = 0
  produceCount = 0
  while produceSushi:
    logMsg = ""
    try:
      if producerID == 0:
        counter.put("A",True)
        logMsg = 'Alice created a masterpiece of fish sushi and placed it on the counter.\n' 
        produceMaximum = numberOfFish
      if producerID == 1:
        counter.put("B",True)
        counter.task_done()
        logMsg = 'Bob crafted one piece of vegetarian sushi and placed it on the counter.\n' 
        produceMaximum = numberofVegi
      produceCount += 1
      sleep(1) # After production we need 1 time unit rest before we can start over again
      if produceCount == produceMaximum:
        produceSushi = False
    except Queue.Full:
      sleep(0.01*producerID)
    writeMsg(logMsg)
#
####################################################################################
# Human Customer
####################################################################################
def humanCustomer(customerID):
  sleep(1.5) # Give Alice and Bob a chance to produce sushi first
  humanID = customerID%10 # Pick an index which is valid using mod
  iteration = customerID//10 + 1 # Use floor devision to get the iteration of name
  if iteration > 1:
    humanName = humanNames[humanID]+" "+str(iteration) # concatenate the iteration integer
  else:
    humanName = humanNames[humanID]
  eatSushi = True
  sleepCounter = 0
  sushiCounter = 0
  counterItem = ""
  while eatSushi:
    logMsg = ""
    try:
      counterItem = counter.get(False) # Use False to avoid blocking while getting the item
      if counterItem == "A":
        sushiType = "fish"
        sleepCounter = 0
      if counterItem == "B":
        sushiType = "vegetarian"
        sleepCounter = 0
      if customerID < custFish:  
        custType = "F"
      elif customerID < custFish+custVegi:  
        custType = "V"
      elif customerID < humanCustomers:  
        custType = "E"
      # Check type vs. taken product
      itemEaten = False
      if custType == "F" and counterItem == "A":
        itemEaten = True
      if custType == "V" and counterItem == "B":
        itemEaten = True
      if custType == "E":
        itemEaten = True
      # Consumption leads to a wait time for the next product
      if itemEaten == True and counterItem != "":
        consCount.put(counterItem,True) # Keep record of sushi (use True to force append)
        logMsg = '%s took one piece of %s sushi and consumed it.\n' % (humanName,sushiType)
        sushiCounter += 1
        sleep(3) # We need 3 seconds to consume the sushi as humans
      if itemEaten == False and counterItem != "":
        logMsg = '%s took one piece of %s sushi and dropped it.\n' % (humanName,sushiType)
        dropCount.put(counterItem,True) # Keep record of sushi (use True to force append)
    except Queue.Empty:
      sleep(0.1) # Try to get an item 0.1 seconds later
      sleepCounter += 1
      #print "wait for food"
      if sleepCounter > 100:
        eatSushi = False  
        break 
    if logMsg != "":  
      writeMsg(logMsg)
#
####################################################################################
# Cat Customer
####################################################################################
def catCustomer(catID):
  sleep(1.5) # Give Alice and Bob a chance to produce sushi first
  logMsg = ""
  iteration = catID//10 + 1 # Use floor devision to get the iteration of name
  catIDmod = catID%10 # Pick an index which is valid using mod
  if iteration > 1:
    catName = catNames[catIDmod]+" "+str(iteration) # concatenate the iteration integer
  else:
    catName = catNames[catIDmod]  
  getItem = True
  sleepCounter = 0
  sushiCounter = 0
  counterItem = ""
  while sushiCounter < 2:
    logMsg = ""
    try:
      counterItem = counter.get(False) # Use False to avoid blocking while getting the item
      if counterItem == "A":
        sushiType = "fish"
      if counterItem == "B":
        sushiType = "vegetarian"
      if counterItem == "A": # Cats only eat fish
        sleepCounter = 0
        sushiCounter += 1
        if sushiCounter == 1:
          logMsg = '%s picked out the %s of the %s sushi and enjoyed the first piece.\n' % (catName,sushiType,sushiType)
        else:
          logMsg = '%s picked out the %s of the %s sushi, enjoyed it, and is full.\n' % (catName,sushiType,sushiType)
        consCount.put(counterItem,True) # Keep record of sushi (use True to force append)
        sleep(2) # We need 2 seconds to consume the sushi as cats
      if counterItem == "B":
        sleepCounter = 0
        logMsg = '%s leaves the %s sushi on the floor.\n' % (catName,sushiType)
        dropCount.put(counterItem,True) # Keep record of sushi (use True to force append)
    except Queue.Empty:
      sleep(0.1) # Try to get an item 0.1 seconds later
      sleepCounter = sleepCounter + 1
      if sleepCounter > 100:
        sushiCounter = 2   
        break
    if logMsg != "":  
      writeMsg(logMsg)
  #counter.task_done() # There seems to be a limit for this call!
#
####################################################################################
# Main section:
####################################################################################
humanCustomers = custFish + custVegi + custEgal
#
# Check if we have human customers (requirements to operate restaurant)
if humanCustomers == 0:
  logMsg = "At least one human has to be in the restaurant to keep it running.\n"
  writeMsg(logMsg)
  sys.exit(0) # Exit program
#
# Check if we have production (requirements to operate restaurant)
if numberOfFish == 0 and numberofVegi == 0:
  logMsg = "At least one type of sushi has to be produced to operate this restaurant.\n"
  writeMsg(logMsg)
  sys.exit(0) # Exit program
#
# Check for negative values
if numberOfFish < 0 or numberofVegi < 0 or custFish < 0 or custVegi < 0 or custEgal < 0 or custCat < 0:
  logMsg = "Negative values are not allowed!\n"
  writeMsg(logMsg)
  sys.exit(0) # Exit program
#
# Create Producer Threads (We know it is going to be 2)
for producerID in range(2):
  individualThread = threading.Thread(target=producer, args=(producerID,))
  threadName = "Producer",producerID
  individualThread.setName(threadName)
  individualThread.start()
#
# Create Human Consumer Threads 
for customerID in range(humanCustomers):
  individualThread = threading.Thread(target=humanCustomer, args=(customerID,))
  threadName = "Customer",customerID
  individualThread.setName(threadName)
  individualThread.start()
#
# Create Cat Consumer Threads
for catID in range(custCat):
  individualThread = threading.Thread(target=catCustomer, args=(catID,))
  threadName = "Cat",catID
  individualThread.setName(threadName)
  individualThread.start()
#
# Wait until all threads are done
individualThread.join()
#
####################################################################################
# Processing results of simulation
####################################################################################
#
# Q.join()/Q.task_done() have a thread limit causing exceptions displayed
# Use activeCount as a replacement
while threading.activeCount() > 1: # First thread is the main program
  sleep(0.1)
#
# Dropped Sushi processing
dropFishCount = 0
dropVegiCount = 0
#
for queueIndex in range(dropCount.qsize()):
  dropItem = dropCount.get()
  if dropItem == "A":
    dropFishCount += 1
  else:
    dropVegiCount += 1
#
if dropFishCount == 1:
  logMsg = "%d piece of fish sushi was dropped on the floor.\n" % (dropFishCount)
else:
  logMsg = "%d pieces of fish sushi were dropped on the floor.\n" % (dropFishCount)
writeMsg(logMsg)
if dropVegiCount == 1:
  logMsg = "%d piece of vegetarian sushi was dropped on the floor.\n" % (dropVegiCount)
else:
  logMsg = "%d pieces of vegetarian sushi were dropped on the floor.\n" % (dropVegiCount)
writeMsg(logMsg)
#
# Consumed Sushi processing
consFishCount = 0
consVegiCount = 0
#
for queueIndex in range(consCount.qsize()):
  consItem = consCount.get()
  if consItem == "A":
    consFishCount += 1
  else:
    consVegiCount += 1
#
if consFishCount == 1:
  logMsg = "%d piece of fish sushi was consumed.\n" % (consFishCount)
else:
  logMsg = "%d pieces of fish sushi were consumed.\n" % (consFishCount)
writeMsg(logMsg)
if consVegiCount == 1:
  logMsg = "%d piece of vegetarian sushi was consumed.\n" % (consVegiCount)
else:
  logMsg = "%d pieces of vegetarian sushi were consumed.\n" % (consVegiCount)
writeMsg(logMsg)
#
# End of Program
