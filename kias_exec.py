#!/tools/gvt/common/anaconda_3.7/bin/python

# Copyright 2021 Xilinx Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import sys
import re
import subprocess
import argparse
import yaml
import logging
import os.path
from pathlib import Path
import tkinter
from tkinter import *
import tkinter.font as tkFont
from tkinter.scrolledtext import ScrolledText
import getpass
from pymongo import MongoClient

#----------------------------------------------------------------------------
# Parse all arguments
#----------------------------------------------------------------------------

parser = argparse.ArgumentParser(description='KIAS Executable')

parser.add_argument('--infile', help='Path to KIAS input file with all KIAS mentioned in YAML format', required=True)
parser.add_argument('--compile', '--comp', help='Path to compile log file')
parser.add_argument('--simulation', '--sim', help='Path to simulation run log file')
parser.add_argument('--log', help='Logging verbosity options : info, debug, warning, error, critical', choices = ["debug","info","warning","error","critical","DEBUG","INFO","WARNING","ERROR","CRITICAL"], required=False)
parser.add_argument('--mode', '--mod', help='select run mode either batch (default execution), gui (yaml writing) or interactive (yaml writing) mode', choices = ["batch","interactive","gui"])

args = parser.parse_args()

yml_log_path = args.infile
com_log_path = args.compile
sim_log_path = args.simulation

username = getpass.getuser()
logging.debug("Username: %r",username)

#----------------------------------------------------------------------------
# Basic logger to create log file
# Assuming loglevel is bound to the string value obtained from the
# command line argument. Convert to upper case to allow the user to
# specify --log=DEBUG or --log=debug
#----------------------------------------------------------------------------

if (args.log == None):
 loglevel = "INFO"
else:
 loglevel = args.log
getattr(logging, loglevel.upper())

numeric_level = getattr(logging, loglevel.upper(), None)
if not isinstance(numeric_level, int):
    raise ValueError('Invalid log level: %s' % loglevel)

logging.basicConfig(filename='kias_exec.log', filemode='w', level=numeric_level)

#----------------------------------------------------------------------------
# Connect to database
#----------------------------------------------------------------------------
client = MongoClient("mongodb://xsjvcpgmongodb:27017")
db=client.kias
collection = db['everest']

#----------------------------------------------------------------------------
# Function to write KIAS to YAML using interactive or gui mode
#----------------------------------------------------------------------------

def write_yaml(log,own,typ,err,rca,sol):
    stream = open(log, 'r+')  #Extracting previous yaml KID
    for yaml_line in stream:
      kid = re.search("KID: ([\d]+)",yaml_line)
      if(kid != None):
        KID = int(kid.group(1))
     
    #print("KID: {:03d}".format(KID+1))
    
    # Create a dictonary to add to monogoDB.
    my_dict={"KID":KID+1,"OWN":own,"TYP":typ,"ERR":err,"RCA":rca,"SOL":sol}
    print (my_dict)
    x = collection.insert_one(my_dict)
   
    # If using YAML file instead of mongoDB, write to it
    stream.writelines("---")
    stream.writelines("\nKID: {:03d}".format(KID+1))
    stream.writelines("\nOWN: "+own)
    stream.writelines("\nTYP: "+typ)
    stream.writelines("\nERR: "+err)

    stream.writelines("\nRCA: |")
    stream.writelines("\n "+rca)
    stream.writelines("\nSOL: |")
    stream.writelines("\n "+sol)
    stream.close()
    
#----------------------------------------------------------------------------
# Interactive mode
#----------------------------------------------------------------------------

if(args.mode == "interactive"):
  yml_log_path = args.infile
   
  own = input("OWN: ")
  typ = input("TYP: ")
  err = input("ERR: ")
 #Logic for recieving multi-line RCA.  
  rca = ""
  print("RCA: ")
  while 1:
    y = input()
    if(y == "exit"):
      break
    rca += "\n " + y
 
 #Logic for recieving multi-line Sol. 
  sol = ""
  print("SOL: ")
  while 1:
    x = input()
    if(x == "exit"):
      break
    sol += "\n " + x

  write_yaml(yml_log_path,own,typ,err,rca,sol)

#----------------------------------------------------------------------------
# GUI interface
#----------------------------------------------------------------------------

elif(args.mode == "gui"):

  ymlip = Tk()
  ymlip.title("KIAS Entry Form")
  ymlip['bg'] = '#22436b'
  

  own=""
  err=""
  rca=""
  sol=""
  typ=""

  def acquireinfo():
      own=username
      err=e1.get()
      rca=e2.get("1.0", tkinter.END) #Get all of the text in widget
      sol=e3.get("1.0", tkinter.END)
      typ=e4.get()
      write_yaml(yml_log_path,own,typ,err,rca,sol)
   
  fontStyle = tkFont.Font(family="Arial", size=12, weight="bold")
  fontStyle1 = tkFont.Font(family="Helvetica", size=12, weight="bold")

  Label(ymlip, text='Error String',font=fontStyle,bg='#22436b',fg='#ff4500').grid(row=3) 
  Label(ymlip, text='Root Cause Analysis',font=fontStyle,bg='#22436b',fg='#00ffff').grid(row=4) 
  Label(ymlip, text='Solution',font=fontStyle,bg='#22436b',fg='#7cfc00').grid(row=5)
  Label(ymlip, text='',font=fontStyle,bg='#22436b',fg='#7cfc00').grid(row=7)
  e1 = Entry(ymlip) 
  e2 = ScrolledText(ymlip, height=5)
  e3 = ScrolledText(ymlip, height=5)
  e1.grid(row=3, column=1,ipadx=216,ipady=25) 
  e2.grid(row=4, column=1) 
  e3.grid(row=5, column=1)
  
  e4 = StringVar() 
  rb1=Radiobutton(ymlip, text='COMPILATION', font=fontStyle,variable=e4, value="COM",bg='#22436b',fg='#ff00ff') 
  rb1.grid(row=0, column=0)
  rb2=Radiobutton(ymlip, text='SIMULATION', font=fontStyle,variable=e4, value="SIM",bg='#22436b',fg='#daa520')  
  rb2.grid(row=1, column=0)
  
  button1=Button(ymlip, text="Submit", command=acquireinfo)
  button1.grid(row=6, column=0,sticky="EW")
  
  Button(ymlip, text="Exit", command=sys.exit).grid(row=8, column=0, sticky="EW")
  

  help_msg = """  HELP GUIDE TO KIAS

  Type:  Choose appropriate button to select type of error, COMPILATION for compile time, SIMULATION for simulation time error
  
  Error String: This is a single line string which the script should look for in the log file, more precise, the better. Can also use regular expressions as demonstrated at the end
  
  Root Cause Analysis: Why the error showed up, reason and causality behind the issue. Can use multi-line comments.  
  
  Solution: Multi-line/single line message of what is the possible way to resolve this kind of issue or the exact solution found in the given case.


  REGULAR EXPRESSIONS HELP - BASIC 
  
  \    Used to drop the special meaning of character following it (discussed below)
  [ ]  Represent a character class
  ^    Matches the beginning
  $    Matches the end
  .     Matches any character except newline
  ?    Matches zero or one occurrence
  |     Means OR (Matches with any of the characters separated by it
  *    Any number of occurrences (including 0 occurrences)
  +    One or more occurrences
  { }  Indicate number of occurrences of a preceding RE to match.
  ( )  Enclose a group of REs

  \d   Matches any decimal digit, this is equivalent to the set class [0-9]
  \D  Matches any non-digit character
  \s   Matches any whitespace character
  \S   Matches any non-whitespace character
  \w   Matches any alphanumeric character, this is equivalent to the class [a-zA-Z0-9_]
  \W  Matches any non-alphanumeric character


  REGULAR EXPRESSIONS HELP - DETAILED

  SPECIAL CHARACTERS
  ^ | Matches the expression to its right at the start of a string. It matches every such instance before each \\n in the string.
  
  $ | Matches the expression to its left at the end of a string. It matches every such instance before each \\n in the string.
  
  . | Matches any character except line terminators like \\n.
  
  \ | Escapes special characters or denotes character classes.
  
  A|B | Matches expression A or B. If A is matched first, B is left untried.
  
  + | Greedily matches the expression to its left 1 or more times.
  
  * | Greedily matches the expression to its left 0 or more times.
  
  ? | Greedily matches the expression to its left 0 or 1 times. But if ? is added to qualifiers (+, *, and ? itself) it will perform matches in a non-greedy manner.
  
  {m} | Matches the expression to its left m times, and not less.
  
  {m,n} | Matches the expression to its left m to n times, and not less.
  
  {m,n}? | Matches the expression to its left m times, and ignores n. See ? above.
  
  
  CHARACTER CLASSES (a.k.a. Special Sequences)
  \w | Matches alphanumeric characters, which means a-z, A-Z, and 0-9. It also matches the underscore, _.
  
  \d | Matches digits, which means 0-9.
  
  \D | Matches any non-digits.
  
  \s | Matches whitespace characters, which include the \\t, \\n, \\r, and space characters.
  
  \S | Matches non-whitespace characters.
  
  \b | Matches the boundary (or empty string) at the start and end of a word, that is, between \w and \W.
  
  \B | Matches where \b does not, that is, the boundary of \w characters.
  
  \A | Matches the expression to its right at the absolute start of a string whether in single or multi-line mode.
  
  \Z | Matches the expression to its left at the absolute end of a string whether in single or multi-line mode.
  
  
  SETS
  [ ] | Contains a set of characters to match.
  
  [amk] | Matches either a, m, or k. It does not match amk.
  
  [a-z] | Matches any alphabet from a to z.
  
  [a\-z] | Matches a, -, or z. It matches - because \ escapes it.
  
  [a-] | Matches a or -, because - is not being used to indicate a series of characters.
  
  [-a] | As above, matches a or -.
  
  [a-z0-9] | Matches characters from a to z and also from 0 to 9.
  
  [(+*)] | Special characters become literal inside a set, so this matches (, +, *, and ).
  
  [^ab5] | Adding ^ excludes any character in the set. Here, it matches characters that are not a, b, or 5.
  
  
  GROUPS
  ( ) | Matches the expression inside the parentheses and groups it.
  
  (? ) | Inside parentheses like this, ? acts as an extension notation. Its meaning depends on the character immediately to its right.
  
  (?PAB) | Matches the expression AB, and it can be accessed with the group name.
  
  (?aiLmsux) | Here, a, i, L, m, s, u, and x are flags:
  
  a — Matches ASCII only
  i — Ignore case
  L — Locale dependent
  m — Multi-line
  s — Matches all
  u — Matches unicode
  x — Verbose
  (?:A) | Matches the expression as represented by A, but unlike (?PAB), it cannot be retrieved afterwards.
  
  (?#...) | A comment. Contents are for us to read, not for matching.
  
  A(?=B) | Lookahead assertion. This matches the expression A only if it is followed by B.
  
  A(?!B) | Negative lookahead assertion. This matches the expression A only if it is not followed by B.
  
  (?<=B)A | Positive lookbehind assertion. This matches the expression A only if B is immediately to its left. This can only matched fixed length expressions.
  
  (?<!B)A | Negative lookbehind assertion. This matches the expression A only if B is not immediately to its left. This can only matched fixed length expressions.
  
  (?P=name) | Matches the expression matched by an earlier group named “name”.
  
  (...)\1 | The number 1 corresponds to the first group to be matched. If we want to match more instances of the same expresion, simply use its number instead of writing out the whole expression again. We can use from 1 up to 99 such groups and their corresponding numbers. """
  
  e7 = ScrolledText(ymlip, font=fontStyle1,bg='#fffacd',fg='#696969',height=25,width=150)  # Grey on Yellow bg
  e7.grid(row=12, column=1)
  e7.insert(tkinter.INSERT,help_msg)

  ymlip.mainloop()
 
#----------------------------------------------------------------------------
# Execution code for batch mode
#----------------------------------------------------------------------------

else:

#----------------------------------------------------------------------------
# Load the YAML file and extract contents in dict
#----------------------------------------------------------------------------
  comp_arr = [] 
  sim_arr = [] 
  
  stream = open(yml_log_path, 'r')
  kdict_list = yaml.load_all(stream, Loader=yaml.FullLoader)
  
  for doc in kdict_list:
       logging.debug("New KIAS document:")
       dlist = doc.items()
       logging.debug("Dictionary List %r",dlist)
       if ("TYP","COM") in dlist:
           logging.debug("Compilation Dict found")
           comp_arr.append(doc)
           logging.debug("Printing Dictionary %r",doc)
       elif ("TYP","SIM") in dlist:
           logging.debug("Simulation Dict found")
           sim_arr.append(doc)
           logging.debug("Printing Dictionary %r",doc)
       for key, value in doc.items():
           logging.debug("%r",(key + " : " + str(value)))
           if type(value) is list:
               logging.debug("%r",(str(len(value))))
  
  logging.debug("%r",comp_arr)
  logging.debug("%r",sim_arr)

#----------------------------------------------------------------------------
# Function to search/process the log files for err message and 
# append kias info extracted from YAML
#----------------------------------------------------------------------------

  def process_kias(log,arr_list):
      # Open log file in rw mode and start processing line by line
      lines = []
      text = open(log,'r')
      # For each dictionary, search for message string in each line, if error found then append KIAS message in the log
      # Read operation
      for line in text.readlines():
          lines.append(line)
          for d in arr_list: # Foreach dictionary in this list
              val = d.get("ERR") #Get value of ERR key
              match = re.search(val,line)  # Search for err pattern, if found, append KIAS info based on the key-value pairs
              if match:
                  logging.debug("Error Matched for err_msg: %r! Appending KIAS Info", val)
                  lines.append("---------------------------------------------KIAS BEGIN--------------------------------------------------\n")
                  lines.append("KIAS ID:                  " + str(d.get("KID")) + "\n")
                  lines.append("KIAS OWNER:               " + d.get("OWN") + "\n")
                  lines.append("KIAS ROOT CAUSE ANALYSIS: " + d.get("RCA") + "\n")
                  lines.append("KIAS SOLUTION:            " + d.get("SOL"))
                  lines.append("---------------------------------------------KIAS END----------------------------------------------------\n")
      text.close()
      
      # Write operation
      text = open(log, 'w+')
      text.writelines(lines)
      text.close()


#----------------------------------------------------------------------------
# Validate COMPILE/SIM FAIL and then process KIAS
#----------------------------------------------------------------------------

  def validate(log,failname,arr_list):
  
       logging.debug("CWD %r",Path.cwd())
       for path in Path.cwd().rglob(failname):
           p = str(path)
           p = p.replace(failname,log)
           if os.path.isfile(p) :
               logging.debug("Log file found %r",p)
               process_kias(p,arr_list) #Process log for KIAS
               #continue #Only match first time
           else:
               logging.debug("Log not found: %r",p)
               return False

#----------------------------------------------------------------------------
# Run compile/sim log KIAS based on arguments
#----------------------------------------------------------------------------

  if (args.compile == None):
   logging.debug("compile log for KIAS not provided, going for search in CWD")
   validate("compile.log","COMPILE_FAIL",comp_arr)
  else:
   process_kias(com_log_path,comp_arr) #Process compile log for KIAS
  
  
  if (args.simulation == None):
   logging.debug("sim log for KIAS not provided, going for search in CWD")
   validate("run.log","SIM_FAIL",sim_arr)
  else:
   process_kias(sim_log_path,sim_arr) #Process sim log for KIAS


#----------------------------------------------------------------------------
# Finishing line banner
#----------------------------------------------------------------------------

  logging.debug("******** KIAS Execution Done **********")


