# AWS ECR & IAM

## Question

You have one aws account with an ECR repository and another one with
an iam user.

The IAM user should be able to assume a role in the ecr aws account and
push docker images to the ecr repository.

Briefly outline the missing parts.

## Answer

### Repository Policy

Assuming the IAM User already exists in Account A, we can add a repository policy
for the ECR in account B:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "AllowPull",
            "Effect": "Allow",
            "Principal": {
                "AWS": [
                    "arn:aws:iam::accountb-id:user/pull-user-1",
                    "arn:aws:iam::accountb-id:user/pull-user-2"
                ]
            },
            "Action": [
                "ecr:BatchGetImage",
                "ecr:GetDownloadUrlForLayer"
            ]
        },
        {
            "Sid": "AllowAll",
            "Effect": "Allow",
            "Principal": {
                "AWS": "arn:aws:iam::accountb-id:user/push-user"
            },
            "Action": [
                "ecr:GetAuthorizationToken",
                "ecr:BatchCheckLayerAvailability",
                "ecr:CompleteLayerUpload",
                "ecr:UploadLayerPart",
                "ecr:InitiateLayerUpload",
                "ecr:PutImage"
            ]
        }
    ]
}
```

An IAM role in account B that allows the IAM user in Account A to assume it via
a trust policy:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::AccountA-ID:user/Username"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
```

That same role would also require a permissions policy for ECR access:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ecr:GetAuthorizationToken",
        "ecr:BatchCheckLayerAvailability",
        "ecr:CompleteLayerUpload",
        "ecr:UploadLayerPart",
        "ecr:InitiateLayerUpload",
        "ecr:PutImage"
      ],
      "Resource": "*" # or the specific ARN of the ECR repository
    }
  ]
}
```

Lastly, the IAM user in Account A would need to be able assume the role in
Account B:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "sts:AssumeRole",
      "Resource": "arn:aws:iam::AccountB-ID:role/RoleName"
    }
  ]
}
```
