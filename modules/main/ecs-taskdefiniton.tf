resource "aws_ecs_task_definition" "TD" {
  family                   = "nginx"
  requires_compatibilities = ["FARGATE"]
  execution_role_arn       = aws_iam_role.iam-role.arn
  network_mode             = "awsvpc"
  cpu                      = 256
  memory                   = 512
  container_definitions = jsonencode([
    {
      name          = "okx-container"
      image         = "${local.aws_account}.dkr.ecr.${local.aws_region}.amazonaws.com/${local.ecr_repo}:${local.image_tag}"
      cpu           = 256
      memory        = 512
      essential     = true
      portMappings = [
        {
          containerPort = 80
          hostPort      = 80
        }
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"          = "ecs-okx-logs"
          "awslogs-region"         = local.aws_region
          "awslogs-stream-prefix"  = "ecs"
        }
      }
    }
  ])
}
