# AWS AZs

## Question

You have a service spread out over 4 ec2 instances.
The service requires a majority of instances to be available to function (so
3 instances in our case) and runs in the following aws availability zones:

• us-east-1a
• us-east-1b
• us-east-1c
• us-west-1a

What kind of possible problems do you see with that configuration?

## Answer

## Availability

The service is spread across 4 availability zones, in two regions. Loosing
us-east would result in 75% of the service being unavailable.

Latency or DNS optimisations for geographical proximity may also be a concern.
If the instance in `us-west-1a` is under significant load and having to
communicate with the other instances in `us-east-1*` to maintain quroum and data
consistency, this might cause problems.

## Recommendations

Ideally we would have an odd number of instances, a minimum of five but
preferably seven, balanced more cleanly across the regions. If the service is
stateful, it may be difficult to keep data consistent across regions.

We could consider using a load balancer with cross region support to distribute
traffic across the regions and zones more evenly.

Health checks and monitoring should be in place to detect issues quickly and
automatically failover to healthy instances; if we cannot avoid a split brain
scenario, we should at least be able to detect it and take action.
