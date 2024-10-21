# K8s Workload Issues

## Question

You have a workload on kubernetes and notice that it looses too many
pods during kubernetes node updates.
How could you fix the problem or make it less bad?

## Answer

### PDBs

```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: my-app-pdb
spec:
  selector:
    matchLabels:
      app: my-app
  minAvailable: 80%  # You can also use an absolute number
```

### Ensure nodes are draining correctly

```bash
kubectl drain `--grace-period`
```

### Rolling Updates for Deployments

```yaml
spec:
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 1
      maxSurge: 1
```

### Change Upgrade Strategy

How this might be done depends on the environment and workloads:

* Make sure that upgrades are staggered and monitored
* Using cluster management tools which respect PDBs etc
* Timed upgrades to avoid peak times, with testing and automation
