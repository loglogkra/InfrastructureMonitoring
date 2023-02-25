# VMware Checks
Connections can be made to exposed api from host machine or vSphere
Host machine:
>    10.136.250.72     - https://10.136.250.72/ui/#/host - e.g. $python check_health.py -s 10.136.250.72 -u root -S  
>    10.136.250.73     - https://10.136.250.73/ui/#/host - e.g. $python check_health.py -s 10.136.250.73 -u root -S  
>    10.135.250.52     - https://10.136.250.52/ui/#/host - e.g. $python check_health.py -s 10.136.250.52 -u root -S  
>    10.135.250.176    - https://10.136.250.176/ui/#/host - e.g. $python check_health.py -s 10.136.250.176 -u root -S  
>    10.136.250.70     - ???  
>    10.136.250.74     - ???    

vSphere:
>    10.136.250.72     - https://devat-vc01.tgwdev.internal - e.g. $python check_health.py -s 10.14.12.36 -u tgw\baford -S  
>    10.136.250.73     - https://devat-vc01.tgwdev.internal - e.g. $python check_health.py -s 10.14.12.36 -u tgw\baford -S  
>    10.135.250.52     - https://devat-vc01.tgwdev.internal - e.g. $python check_health.py -s 10.14.12.36 -u tgw\baford -S  
>    10.135.250.176    - https://devat-vc01.tgwdev.internal - e.g. $python check_health.py -s 10.14.12.36 -u tgw\baford -S  
>    10.136.250.70     - ???  
>    10.136.250.74     - ???  
    
# Host Managed Object 
Two ways of getting a host managed object is by matching the UUID or DNS value of the target host. 
However, the matching values will be different depending on your method of entry (vsphere or host api).

## UUID values (vSphere)
Note: Untested, but should work!
>    10.136.250.72     - ???    
>    10.136.250.73     - 5c59eeaf-dafa-2f0e-0f26-20677cf08004    
>    10.135.250.52     - ???    
>    10.135.250.176    - 529f32c0-a9b5-bc64-a28b-c81f66cf3ac9    
>    10.136.250.70     - ???    
>    10.136.250.74     - ???    

## UUID values (Host)
>    10.136.250.72     - ???  
>    10.136.250.73     - ???  
>    10.135.250.52     - ???  
>    10.135.250.176    - ???  
>    10.136.250.70     - ???  
>    10.136.250.74     - ???  

## DNS values (vSphere)
Note: Yes, the "DNS Name" is the same as the target machine's IP address.
>    10.136.250.72     - 10.136.250.72  
>    10.136.250.73     - 10.136.250.73  
>    10.135.250.52     - 10.136.250.52  
>    10.135.250.176    - 10.136.250.176  
>    10.136.250.70     - ???  
>    10.136.250.74     - ???  

        
## DNS values (vSphere)
>    10.136.250.72     - US-MI-SL1300-DC-VMH-DEV.tgw.local  
>    10.136.250.73     - US-MI-SL1300-DC-VMH-DEV2.tgw.local  
>    10.135.250.52     - USGRESX52.tgw.local  
>    10.135.250.176    - ???  
>    10.136.250.70     - ???  
>    10.136.250.74     - ???  