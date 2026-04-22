# NPO CLI Pipeline

`npo-cli-pipeline` is a stripped-down project that keeps the existing engine execution flow, but removes the web frontend and API server.

The flow is:

1. A user submits a command from the CLI.
2. The command is stored in a Redis-backed Celery queue.
3. One or more workers automatically pick up queued jobs.
4. Results and logs are written to the folders chosen by the user.

This project is designed to work in a distributed setup:

1. One machine runs Redis.
2. Many worker machines connect to that Redis instance.
3. Users can submit jobs from any machine that can reach Redis.
4. All machines share the same NAS mount for input, output, and job state.

## What is reused

- `npo-engine-lib`: Docker-based engine execution helpers
- Celery + Redis: queue and worker distribution

## What is removed

- frontend
- apiserver
- database dependency for job tracking

Job status is stored as JSON files and job logs are stored as text files.

In a single-machine setup, the default location is `state/`.

In a distributed setup, `NPO_CLI_STATE_DIR` should point to a shared NAS folder so that:

- the submit machine can create job metadata
- worker machines can update job status
- users can inspect logs and results from any machine

## Distributed architecture

Recommended layout:

- `1 x Redis host`: only runs Redis
- `N x worker hosts`: each host runs `uv run npo-cli worker`
- `submit hosts`: run CLI submissions directly or through a submit container
- `1 x shared NAS`: mounted on every submit host and worker host

Typical data flow:

1. A submit host sends a job to Redis.
2. Redis keeps the job in the Celery queue.
3. One idle worker pulls the next job.
4. That worker launches the engine container on its own machine.
5. The engine reads input from the NAS mount and writes output back to the NAS mount.
6. The worker writes job status and logs to the shared state directory on the NAS.

Important requirement:

- every worker must be able to access the same dataset and output paths
- the NAS should be mounted at the same absolute path on every worker machine

For example, if a submitted job uses `/mnt/npo-nas/datasets/job-001`, then every worker host should see that exact same path.

This matters because the worker launches Docker containers locally, and those containers mount host folders by path.

## Quick start

1. On the Redis host, start Redis.

```bash
docker compose -f npo-redis/docker-compose.yml up -d
```

2. On every submit host and worker host, install dependencies.

```bash
uv sync
```

3. On every submit host and worker host, set `.env`.

Example:

```bash
CELERY_BROKER=redis://10.0.0.10:30108/0
CELERY_BACKEND=redis://10.0.0.10:30108/1
ENGINE_IMAGE=devboxhq/npo:etri_scapi-0.1.4
NPO_CLI_STATE_DIR=/mnt/npo-nas/npo-cli-state
```

4. On each worker host, start a worker.

```bash
uv run npo-cli worker
```

5. From any submit host, submit a job.

```bash
uv run npo-cli submit preprocess-video \
  --source-folder /home/sjpark/Documents/Webapp/npo-cli-pipeline/Server/DockerTest1/temp/Test \
  --target-folder /home/sjpark/Documents/Webapp/npo-cli-pipeline/Server/DockerTest1/temp/output1 \
  --factor 4
```

6. Inspect progress from any machine that shares the same `NPO_CLI_STATE_DIR`.

```bash
uv run npo-cli status <job-id>
uv run npo-cli logs <job-id>
uv run npo-cli wait <job-id>
```

## Docker deployment

For deployment, the recommended split is:

- `worker`: run as a long-lived Docker container
- `submit`: use either a host CLI or a short-lived Docker CLI container

### Worker container

Build and start:

```bash
# edit npo-worker/.env
./scripts/run-worker.sh
```

This starts a persistent worker container using [docker-compose.yml](/home/sjpark/Documents/Webapp/npo-cli-pipeline/npo-worker/docker-compose.yml:1).

Important worker requirements:

- mount the Docker socket: `/var/run/docker.sock:/var/run/docker.sock`
- mount the shared NAS at the same absolute path on the host and in the container
- use the same Redis and NAS settings as every other worker
- pass `HOST_CWD` only if container paths need to be translated back to host paths

### Submit container

There are two good ways to use submit in production.

Option 1: run submit directly on the host

```bash
uv run npo-cli submit ...
```

Option 2: run submit through a Docker CLI container

```bash
# edit npo-submit/.env
./scripts/submit.sh submit preprocess-video \
  --source-folder /home/sjpark/Documents/Webapp/npo-cli-pipeline/Server/DockerTest1/temp/Test \
  --target-folder /home/sjpark/Documents/Webapp/npo-cli-pipeline/Server/DockerTest1/temp/output1 \
  --factor 4
```

This is useful when you want a clean deployment artifact and do not want to install Python or `uv` on the submit PC.

### Interactive submit shell

If you want a dedicated command window, use the submit container in shell mode:

```bash
./scripts/submit-shell.sh
```

Then inside that shell you can type:

```text
submit preprocess-video --source-folder /home/sjpark/Documents/Webapp/npo-cli-pipeline/Server/DockerTest1/temp/Test --target-folder /home/sjpark/Documents/Webapp/npo-cli-pipeline/Server/DockerTest1/temp/output1 --factor 4 --param-frame 1 --start-frame 1 --finish-frame 1
status <job-id>
logs <job-id>
list
quit
```

This uses the new `npo-cli shell` command and gives you the "just type submit ..." workflow.

## Commands

### `submit preprocess-image`

Copies the source dataset to the target folder if needed, then runs:

- `build_param`
- `build_layer`

Example:

```bash
uv run npo-cli submit preprocess-image \
  --source-folder /mnt/npo-nas/data/image-input \
  --target-folder /mnt/npo-nas/data/image-work \
  --factor 4
```

### `submit preprocess-video`

Extracts frames into the target folder, then preprocesses the extracted frames there.

Example:

```bash
uv run npo-cli submit preprocess-video \
  --source-folder /home/sjpark/Documents/Webapp/npo-cli-pipeline/Server/DockerTest1/temp/Test \
  --target-folder /home/sjpark/Documents/Webapp/npo-cli-pipeline/Server/DockerTest1/temp/output1 \
  --factor 4 \
  --param-frame 1 \
  --start-frame 1 \
  --finish-frame 5
```

Current local test setup:

- `source-folder` should point to a folder under `Server/DockerTest1/temp`
- `target-folder` should also point to a folder under `Server/DockerTest1/temp`
- `preprocess-video` now creates `target-folder/Video` and copies the input video files there before running the engine

Example commands:

```bash
./scripts/submit.sh submit preprocess-video \
  --source-folder /home/sjpark/Documents/Webapp/npo-cli-pipeline/Server/DockerTest1/temp/Test \
  --target-folder /home/sjpark/Documents/Webapp/npo-cli-pipeline/Server/DockerTest1/temp/output1 \
  --factor 4 \
  --param-frame 1 \
  --start-frame 1 \
  --finish-frame 1
```

```bash
./scripts/submit.sh list --limit 5
./scripts/submit.sh status <job-id>
./scripts/submit.sh logs <job-id> --tail 100
```

### `submit render`

Renders a frame range from a preprocessed dataset into the chosen output folder.

```bash
uv run npo-cli submit render \
  --data-folder /mnt/npo-nas/data/image-work \
  --output-folder /mnt/npo-nas/data/render-output \
  --view-range 1.0 \
  --focal 50 \
  --num-views 49 \
  --start-frame 1 \
  --finish-frame 5
```

### `submit render-quilt-image`

Renders a quilt image for one frame into the chosen output folder.

```bash
uv run npo-cli submit render-quilt-image \
  --data-folder /mnt/npo-nas/data/image-work \
  --output-folder /mnt/npo-nas/data/quilt-output \
  --view-range 1.0 \
  --focal 50 \
  --rows 7 \
  --cols 7 \
  --frame-number 1
```

## Environment

Update `npo-worker/.env` and `npo-submit/.env` for your deployment.

- `CELERY_BROKER`
- `CELERY_BACKEND`
- `ENGINE_IMAGE`
- `HOST_CWD`
- `NPO_CLI_STATE_DIR`

Recommended distributed values:

- `CELERY_BROKER=redis://<redis-host>:30108/0`
- `CELERY_BACKEND=redis://<redis-host>:30108/1`
- `NPO_CLI_STATE_DIR=/mnt/npo-nas/npo-cli-state`
 
`NPO_CLI_STATE_DIR` is still required in Docker mode. Compose does not use it directly, but the application uses it at runtime to decide where job metadata and log files are written. In a multi-PC deployment, this should be a NAS path shared by submit and worker machines.

`HOST_CWD` is a worker-side compatibility setting from `npo-engine-lib`. It is used when a worker container receives a path like `/mnt/npo-nas/job-001`, but the engine container that is launched through the host Docker socket must actually mount a different host-side root.

Use `HOST_CWD` like this:

- leave it empty when the host and the worker container see the NAS at the same absolute path
- set it only in `.env.worker` when the worker container path and host path differ
- do not set it in `.env.submit`, because submit does not launch engine containers

Example:

- host path: `/data/nas`
- worker container path: `/mnt/npo-nas`
- submitted job path: `/mnt/npo-nas/work/job-001`
- then `HOST_CWD=/data/nas`

In that case, `npo-engine-lib` converts the container-visible path into a host path before asking Docker to mount it.

If the worker runs directly on the host OS, `HOST_CWD` can usually stay empty.

## Deployment notes

- Redis does not execute jobs itself. It acts as the shared broker and result backend.
- Celery workers pull jobs from Redis when they are idle, so work is naturally distributed across all running workers.
- If 10 worker PCs are running and jobs keep being submitted, Celery will spread the queue across those workers based on availability.
- Output folders must be on the shared NAS, otherwise results will be written only to the local disk of the worker that processed the job.
- `NPO_CLI_STATE_DIR` should also be on the NAS in multi-PC deployments, otherwise `status`, `logs`, and `wait` will not show a unified view.
- The worker container must have access to the host Docker daemon because it launches engine containers locally.
- The submit container does not need Docker socket access because it only pushes jobs into Redis and reads shared state from the NAS.
