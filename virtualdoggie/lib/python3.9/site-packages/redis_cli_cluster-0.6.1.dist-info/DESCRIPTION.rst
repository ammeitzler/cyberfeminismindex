redis-cli-cluster
=================

Cluster-aware re-implementation of `redis-cli`.

Here's the problem:

.. code-block:: bash

    $ redis-cli -c -h node-0 set apple sauce
    -> Redirected to slot [7092] located at 172.255.0.3:6379
    OK
    $ ctrl-D
    $ redis-cli -c -h node-0 keys "*"
    (empty list or set)
    $ redis-cli -c -h node-1 keys "*"
    1) "apple"

Wouldn't it be great if that ``keys *`` worked the same was as in non-clustered
mode?

.. code-block:: bash

    $ redis-cli-cluster -h node-0 set apple sauce
    -> Redirected to slot [7092] located at 172.255.0.3:6379
    OK
    $ ctrl-D
    $ redis-cli-cluster -h node-0 keys "*"
    1) "apple"


