---
name: chart-test
description: Deploy and test Helm chart in k3s environment. Use for end-to-end chart validation.
---

# Helm Chart Test

## Overview

Deploy and test the Helm chart in a local k3s Kubernetes cluster for end-to-end validation.

## Requirements

- Root/sudo access (for k3s)
- Environment variables for deployment:
  - `OPENAI_BASE_URL`
  - `OPENAI_API_KEY`
  - `OPENAI_MODEL`

## K3s Environment Management

### Start k3s

```bash
tools/k8s/k3s.sh start
```

### Check k3s Status

```bash
tools/k8s/k3s.sh status
```

### Stop k3s

```bash
tools/k8s/k3s.sh stop
```

### Delete k3s (Clean All Data)

```bash
tools/k8s/k3s.sh delete
```

## Chart Deployment

### Deploy Chart

```bash
export OPENAI_BASE_URL="your-base-url"
export OPENAI_API_KEY="your-api-key"
export OPENAI_MODEL="your-model"
tools/chart-test/run.sh deploy
```

### Check Deployment Status

```bash
tools/chart-test/run.sh status
```

### Undeploy Chart

```bash
tools/chart-test/run.sh undeploy
```

## Typical Workflow

1. **Setup Environment**
   ```bash
   tools/k8s/k3s.sh start
   ```

2. **Deploy Chart**
   ```bash
   export OPENAI_BASE_URL="..."
   export OPENAI_API_KEY="..."
   export OPENAI_MODEL="..."
   tools/chart-test/run.sh deploy
   ```

3. **Verify Deployment**
   ```bash
   tools/chart-test/run.sh status
   ```

4. **Access Frontend**
   - NodePort: 31300
   - URL: `http://<node-ip>:31300`

5. **Cleanup**
   ```bash
   tools/chart-test/run.sh undeploy
   tools/k8s/k3s.sh stop
   ```

## Configuration

- Chart values: `tools/chart-test/values.yaml`
- k3s config: Embedded in `tools/k8s/k3s.sh`
- KUBECONFIG: `/etc/rancher/k3s/k3s.yaml` (default)

## Troubleshooting

### Check k3s Logs

```bash
tail -f /var/log/k3s.log
```

### Check Pod Logs

```bash
kubectl logs -n default -l app.kubernetes.io/instance=word-voyage
```

### Check Pod Events

```bash
kubectl describe pod -n default -l app.kubernetes.io/instance=word-voyage
```

## Important

**Always ask before running tests.** This requires root access and modifies system state.
