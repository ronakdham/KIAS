# KIAS

## Purpose 

To store KIAS info in kias.yaml file and let the script parse the yaml file, extract KIAS', match it compilation and/or simulation log files and then append the Root Cause Analysis/Solution info right below the error message. 

## Usage 

```tcsh
 ./kias_exec.py --infile kias.yaml --log debug --comp compile.log --sim sim.log 
```
 
## Yaml format 

---  <Start of Yaml Document identifier> 

KID: 001 <KIAS ID number> 

OWN: Ronak <Name of contact person who identified/worked on this issue> 

TYP: COM <Type of error, COM for compile time, SIM for simulation time> 

ERR: RO period mismatch <Err msg which script should look for in the log file, more precise, the better> 

RCA: RO period mismatches because clk period provided in testcase is not correct <Root Cause Analysis, why the error showed up, reason behind the issue> 

SOL: | <Use when need to write multi-line info> 

  Provide proper clk period in test as per RTL/Waveform. 

  Check RTL for proper clock frequency. <Multi-line/single line message of what is the possible way to resolve this kind of issue or the exact solution found in this case>
  

## Using GUI mode to update KIAS yaml 

```tcsh
./kias_exec.py --infile kias.yaml --mode=gui 
```
  
