# IDS Check

A library for docker users to check the GPU and CPU utilization by simple command line commands.

## Install

Use `pip3` to install the library `idscheck`:

```
pip3 install idscheck
```

## How to Use

After install, you can just use the following easy commands to check the status of GPU and CPU.

### Most efficient way

Just use the `ids` command to check who is using the GPU and the email of them:

```
ids
```

Example Outputs are:

```
+-----------------------------------------------------------------------------+
| NVIDIA-SMI 510.73.08    Driver Version: 510.73.08    CUDA Version: 11.6     |
|-------------------------------+----------------------+----------------------+
| GPU  Name        Persistence-M| Bus-Id        Disp.A | Volatile Uncorr. ECC |
| Fan  Temp  Perf  Pwr:Usage/Cap|         Memory-Usage | GPU-Util  Compute M. |
|                               |                      |               MIG M. |
|===============================+======================+======================|
|   0  NVIDIA A100-SXM...  On   | 00000000:07:00.0 Off |                    0 |
| N/A   30C    P0    63W / 400W |   3823MiB / 40960MiB |     27%      Default |
|                               |                      |             Disabled |
+-------------------------------+----------------------+----------------------+
|   1  NVIDIA A100-SXM...  On   | 00000000:0F:00.0 Off |                    0 |
| N/A   31C    P0    86W / 400W |  13140MiB / 40960MiB |     21%      Default |
|                               |                      |             Disabled |
+-------------------------------+----------------------+----------------------+
|   2  NVIDIA A100-SXM...  On   | 00000000:47:00.0 Off |                    0 |
| N/A   27C    P0    52W / 400W |      2MiB / 40960MiB |      0%      Default |
|                               |                      |             Disabled |
+-------------------------------+----------------------+----------------------+
|   3  NVIDIA A100-SXM...  On   | 00000000:4E:00.0 Off |                    0 |
| N/A   32C    P0    84W / 400W |  26357MiB / 40960MiB |    100%      Default |
|                               |                      |             Disabled |
+-------------------------------+----------------------+----------------------+
|   4  NVIDIA A100-SXM...  On   | 00000000:87:00.0 Off |                    0 |
| N/A   34C    P0    66W / 400W |  30134MiB / 40960MiB |     25%      Default |
|                               |                      |             Disabled |
+-------------------------------+----------------------+----------------------+
|   5  NVIDIA A100-SXM...  On   | 00000000:90:00.0 Off |                    0 |
| N/A   62C    P0   296W / 400W |  38917MiB / 40960MiB |     97%      Default |
|                               |                      |             Disabled |
+-------------------------------+----------------------+----------------------+
|   6  NVIDIA A100-SXM...  On   | 00000000:B7:00.0 Off |                    0 |
| N/A   33C    P0    76W / 400W |   9309MiB / 40960MiB |      0%      Default |
|                               |                      |             Disabled |
+-------------------------------+----------------------+----------------------+
|   7  NVIDIA A100-SXM...  On   | 00000000:BD:00.0 Off |                    0 |
| N/A   63C    P0   270W / 400W |  38865MiB / 40960MiB |     93%      Default |
|                               |                      |             Disabled |
+-------------------------------+----------------------+----------------------+

+-------+---------+--------------+-----------------+-----------+---------------------------+
| GPUID |   PID   | Process Name | Used GPU Memory |    User   |      Email Address        |
+-------+---------+--------------+-----------------+-----------+---------------------------+
|     0 | 1302626 | python_naibo |         3821MiB |   naibo   | naibowang@comp.nus.edu.sg |
|     1 | 1584227 | python_naibo |         3831MiB |   naibo   | naibowang@comp.nus.edu.sg |
|     4 | 1570396 | python_naibo |         3777MiB |   naibo   | naibowang@comp.nus.edu.sg |
+-------+---------+--------------+-----------------+-----------+---------------------------+

```


### Check GPU Utilization Info

Just like `nvidia-smi`, use `idsgpu` or `ids gpu` to check GPU utilization.

```shell
idsgpu
```

or

```shell
ids gpu
```

Example output:
```
+-----------------------------------------------------------------------------+
| NVIDIA-SMI 510.73.08    Driver Version: 510.73.08    CUDA Version: 11.6     |
|-------------------------------+----------------------+----------------------+
| GPU  Name        Persistence-M| Bus-Id        Disp.A | Volatile Uncorr. ECC |
| Fan  Temp  Perf  Pwr:Usage/Cap|         Memory-Usage | GPU-Util  Compute M. |
|                               |                      |               MIG M. |
|===============================+======================+======================|
|   0  NVIDIA A100-SXM...  On   | 00000000:07:00.0 Off |                    0 |
| N/A   44C    P0   109W / 400W |   4606MiB / 40960MiB |     35%      Default |
|                               |                      |             Disabled |
+-------------------------------+----------------------+----------------------+
|   1  NVIDIA A100-SXM...  On   | 00000000:0F:00.0 Off |                    0 |
| N/A   35C    P0   126W / 400W |   3829MiB / 40960MiB |     22%      Default |
|                               |                      |             Disabled |
|   2  NVIDIA A100-SXM...  On   | 00000000:BD:00.0 Off |                    0 |
| N/A   58C    P0   263W / 400W |   3427MiB / 40960MiB |     91%      Default |
|                               |                      |             Disabled |
+-------------------------------+----------------------+----------------------+
+-----------------------------------------------------------------------------+
| Processes:                                                                  |
|  GPU   GI   CI        PID   Type   Process name                  GPU Memory |
|        ID   ID                                                   Usage      |
|=============================================================================|
|    0   N/A  N/A    423426      C   python_naibo                     3425MiB |
|    0   N/A  N/A    432801      C   python_naibo                     1391MiB |
|    1   N/A  N/A    430531      C   python_naibo                     3827MiB |
|    2   N/A  N/A    882885      C   python                          26355MiB |
+-----------------------------------------------------------------------------+

```

### Check Process

Just like the `top` commands, use `idstop` or `ids top` to check all the running processes:

```shell
idstop
```

Or you can filter some information, e.g, check who is running process with PID `423426`:

```shell
ids top | grep 423426
```

Example Output:

```
4189111 naibo     20   0   19.8g   6.0g  43720 S  2270   0.6 120124:48 python
```

### Check User Information to contact them

Use `idsquery` or `ids query` to get all the user's email addresses to contact them if you want them to leave some GPU/CPU resources for you:

```shell
idsquery
```

Example Output:
```
+--------------+---------------------------+
|  Username    |       Email Address       |
+--------------+---------------------------+
|   naibo      | naibowang@comp.nus.edu.sg |
|   xiaoming   |     xiaoming@test.com     |
+--------------+---------------------------+
```

### Check All processes' information

Use `idstopall` or `ids topall` to get all the processes' information, including the `root` user of the server.