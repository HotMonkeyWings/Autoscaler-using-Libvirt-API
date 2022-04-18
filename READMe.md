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
git clone 
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

