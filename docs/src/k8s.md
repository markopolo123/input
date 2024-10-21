# K8S Load Skew

## Question

You have a kubernetes deployment for a backend. That backend is accessed
by clients through a kubernetes service:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: my-service
spec:
  selector:
  app: my-service
  ports:
  - protocol: TCP
      port: 443
      targetPort: 9376
```

Over time, you notice that load on the backend pods skews. Some pods have high
load, others barely any at all.

What might be possible problems?

## Answer

* kube-proxy; Iptables & DNAT
* Session Affinity - Client IP
* Persistent Connections (gRPC, Websockets)
* Issues with networkpolicy, (anti)affinity and resource requests/limits
* Issues or long running requests within the application
