Guillotina Nats
---------------

Guillotina AddOn to connect to Nats and Stan in order to implement PubSub and Streaming strategies

In order to configure::

    applications:
    - guillotina_nats
    load_utilities:
      nats:
        factory: guillotina_nats.utility.NatsUtility
        provides: guillotina_nats.interfaces.INatsUtility
        settings:
          hosts:
          - nats://nats.nats.svc.cluster.local:4222
          stan: stan
          timeout: 0.2
