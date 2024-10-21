# Terraform State Backends

## Question

Describe what a remote state backend does in terraform.

## Answer

The hashicorp documentation actually refers to the HCP Terraform Cloud state
storage as `remote state storage` . This has been replaced in newer versions
of Terraform with `terraform cloud` commands.

I am assuming the question refers to using backends like `s3` , `consul` or
`http` to store state.

> Mostly this exists because **Terraform** is a CLI tool with no good story
> around an API for shared use environments. The industry bolts on all kind of
> stuff to try and mitigate this.

When we run `terraform`  `plan` or `apply` commands **Terraform** checks three
things:

* The configuration files where you *declare what you want*
* The *actual state* of the infrastructure via API calls
* The state file; where Terraform stores the *last known state* of the infrastructure

The state file is `JSON` and also used to store *metadata* around the Terraform
run. This includes the *provider* and *module* configurations, terraform
versions, State ID, etc.

### Collaboration

When working in a team, the state file is a shared resource.

* Any action which may write to the state file will lock it first
* If an action can't get the lock it will fail.
* Typically the state file will be versioned

### Locking

Helps prevent race conditions when groups of people are working on shared infra.
Not all state backends support `locking` .
If working with **AWS** then the **S3** state backend with locking provided by
**DynamoDB** is the way to go.

### Security

* The state file may contain secrets so controls are needed to protect it.
* Access controls (IAM in AWS) should be used to restrict access to the state file.
* Encryption at rest should be enabled.

### Disaster Recovery

Versioning the state file is a good idea.
Do not commit the state file to source control.
