# 
<h1>
    <center>CS4037D Cloud Computing</center>
    <center>Programming Assignment 1: Build your own cloud management system using the libvirt API</center>
</h1>
<p><center>Dev Sony, B180297CS</center></p>
<p><center>Anish Sharma, B181065CS</center></p>
<p><center>Arjun Syam, B180031CS</center></p>
<p><center>Adil Chery, B180372CS</center></p>
<p><center>Indrajith T S, B180486CS</center></p>

[Github Repo](https://github.com/HotMonkeyWings/Autoscaler-using-Libvirt-API.git)

## To setup

Clone the repo 

```
git clone https://github.com/HotMonkeyWings/Autoscaler-using-Libvirt-API.git
```

Start the first VM and then launch the programs:
```
python src/client.py
python src/client_communicator.py
python src/autoscaler.py
```

The VMs are to have auto-login, with the server script starting up on boot. To do so, you may add the following line to `.bashrc`:
```
python3 server.py
```

*P.S. The examples folder was used to just experiment from the libvirt API.*

## The Autoscaling Algorithm

We use a modified **Dual-Threshold Horizontal Scaling Algorithm** in order to autoscale the VMs. [Reference](https://www.hindawi.com/journals/sp/2021/6397786/)

The alpha(α) and beta(β) values for the first and second thresholds are taken as 50% and 75%. What this implies is that, every cycle around the array,
<mark>[1, 1, 1, 1, 1]</mark>, the algorithm will proceed to update the array element up or down, depending on the element values and the threshold crossed by the CPU. The cycle moves on to the next element when any of the rules are satisfied. 

The rules are as follows:

1. If the value of the array element is 1, and the `CPU USAGE` has crossed `α`, the array element is updated to 2.

2. If the value of the array element is 2, and the `CPU USAGE` has crossed `β`, the array element is updated to 3.

3. If the value of the array element is 3, and the `CPU USAGE` is below `β`, the array element is updated to 2.

4. If the value of the array element is 2, and the `CPU USAGE` is below `α`, the array element is updated to 1.

5. If all the elements in the array are 3, the array is reset and a new VM is attempted to be spawned. 

