# OS-health-check
Python lib that provides an easy way to check the health of an *nix OS

## How it works?
OS-health-check has been designed to provide a quick way for monitoring the health of a set of *nix based OS.

Doesn't need any agent on each node to be monitorized, just share pubkey based credentials thorugh SSH

Takes care about:
- CPU
- Mem
- Swap
- Disks (ocupation and inodes)
- Processes (creation)
- Network I/O, transfer stats
- All block dev
- Interrupts


## How to use it?

Just call it
```
$ os-health-check.py -h HOST -c CHECKSlist
```
, and reach a status line for each check
```
check1 status detail
check2 status detail
...
checkn status detail
```

, where
```
 -h define the hostname/IP address to check

 -c the set of checks to be performed comma (,) separated (without spaces!)
    OPTIONS: cpu mem disk net

 -m set the metrics pair warning,critical to analyze the status of the tests comma (,) separated (without spaces!)
    //-m 75,90 will set status = warning if range >75 and critial if >90
    
 -d define a delay for the execution of the checks
    //-d5 will wait 5sec and trigger al the checks

 -D define a delay for the execution of **each** check
    //-D5 will wait 5secs between the execution of each check

 -C get the results from cache (last execution results)
```


## Examples

```
$ os-health-check.py -h GNUites -c cpu,disk,mem,swap -m 75,90
cpu ok "la 1,0,0"
disk ok "all devices ok"
mem warning "85% used"
swap ok ""
```
