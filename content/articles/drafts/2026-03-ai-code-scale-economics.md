---
title: The Math on Running AI Code at Scale
status: draft
platform: x-article
thumbnail: pending
perspective: "Every team running AI agent code hits a predictable cost inflection with managed sandbox platforms, and the break-even math is simpler than most engineering leaders think."
sources:
  - research/reports/20260219-code-execution-sandboxes.md
content-id: 20260308-AD-008
---

# The Math on Running AI Code at Scale

A single AI code execution session costs about half a cent. At 1 million sessions per day, that's $135,000 per month. These numbers are not hypothetical. They come directly from the published pricing of E2B, Daytona, and Modal, the three platforms that dominate the managed sandbox market right now.

Most teams discover this math too late. They build on a managed platform when volume is low and the per-session cost is invisible. Then usage grows, and the bill grows linearly with it. By the time someone runs the numbers on alternatives, the switching cost feels enormous.

But the inflection point is predictable. The break-even between managed and self-hosted sits around 200,000 to 500,000 sessions per day. Below that, managed platforms are the obvious choice. Above it, you're lighting money on fire.

## What a Session Actually Costs

Take E2B as the reference case. Their published rate is $0.000014 per vCPU per second, plus $0.0000045 per GiB per second for memory. For a typical session (1 vCPU, 512 MiB RAM, running for 5 minutes):

```
vCPU:  1 vCPU  x 300s x $0.000014/vCPU/s  = $0.0042
RAM:   0.5 GiB x 300s x $0.0000045/GiB/s  = $0.000675
Total per session:                          ~$0.005
```

Daytona and Blaxel land at roughly the same number. Modal is slightly higher at about $0.006 per session. Cloudflare comes in around the same.

The per-session price feels trivial. Half a cent. But volume changes everything.

| Sessions/Day | Monthly Cost (Managed) | Monthly Cost (DIY Firecracker) |
|---|---|---|
| 10,000 | ~$1,350 | Not worth it |
| 100,000 | ~$13,500 | Still not worth it |
| 500,000 | ~$67,500 | $24K-$90K |
| 1,000,000 | ~$135,000 | $24K-$90K |

DIY means running Firecracker microVMs on bare-metal EC2 instances. The infrastructure cost flattens because you're paying for hosts, not per session. An i3.metal instance runs about $3,593/month on-demand and can handle 200+ concurrent microVMs. The cost scales with concurrency, not total volume.

## The Costs Nobody Warns You About

The per-session rate is just the headline number. Three hidden costs routinely add 20-40% on top.

### Warm Pools

If your product needs fast response times, you keep pre-booted VMs idling in a warm pool. On a managed platform, idle VMs cost the same as active ones. You're paying per-second for compute that sits there doing nothing.

The math gets painful fast. Say you maintain 1,000 idle VMs to handle burst traffic (1 vCPU, 512 MiB each):

```
On E2B:   1,000 VMs x $0.000014/s x 86,400s = $1,210/day = ~$36K/month
On EC2:   ~12 m5.xlarge instances            = ~$1,659/month
```

That's roughly 20x more expensive on a managed platform. For idle compute. The managed platform charges per-second whether the VM is doing work or waiting for work. EC2 charges a flat rate for the metal.

### Data Egress

Every session produces output. If each one generates about 1 MB (logs, artifacts, results), that's 1 TB per day at a million sessions. 30 TB per month.

```
AWS egress:        30 TB x $0.09  = $2,700/month
GCP egress:        30 TB x $0.11  = $3,300/month
Cloudflare egress: 30 TB x $0.025 = $750/month
```

Not catastrophic, but not negligible either. And these charges show up on the cloud provider bill, not the sandbox bill, which makes them easy to miss.

### Snapshot Storage

Platforms that support snapshot-based fast restore (and you want this, because it's the difference between 15ms and 150ms cold starts) need to store those snapshots somewhere. A memory snapshot runs 128 MB to 2 GB compressed. At 100,000 snapshots, that's about 50 TB of S3 storage at $1,150/month.

## Billing Granularity: The Quiet Killer

This is the cost factor that surprises people the most. If your workloads are short-lived, the billing increment matters more than the per-unit rate.

Consider a 30-second task on a 1 vCPU instance:

```
Per-second billing:  30s x $0.000014 = $0.00042
Per-minute billing:  1m  x $0.00084  = $0.00084   (2x overpay)
Per-hour billing:    1hr x $0.05     = $0.05       (120x overpay)
```

At a million sessions per day, per-second billing costs $420/day. Per-hour billing costs $50,000/day. Same workload, same infrastructure, 120x price difference.

E2B, Daytona, and Modal all bill per-second. AWS Fargate has a one-minute minimum. Traditional VM providers often bill hourly. If you're evaluating options and your sessions are short, check the billing increment before anything else.

## The Break-Even Calculation

The DIY path means running Firecracker on bare-metal instances (you need KVM access, so you need metal). Here's what the comparison looks like:

```
                    DIY (Firecracker on EC2)     Managed (E2B/Daytona/Modal)
                    ========================     ===========================
Infra cost/month    $24K-$90K (hosts)            Linear with usage
Engineering cost    6-12 months to build          Near zero
Cold start          You control it                150ms-3s
Security patches    Your responsibility           Provider handles it
Scaling             Manual or custom              Automatic
```

The 6-12 months of engineering time is the real cost. Firecracker itself is well-documented and straightforward. What takes months is everything around it: networking (TAP devices, iptables per VM), storage (overlay filesystems), an API layer (create/destroy/manage), scheduling (bin-packing VMs across hosts), monitoring, snapshotting, and security hardening.

The break-even:

```
< 100K sessions/day:    Managed. Not close.
100K - 500K/day:        Evaluate. Depends on team and timeline.
> 500K sessions/day:    DIY saves real money. $45K-$110K/month in savings.
> 1M sessions/day:      DIY is the only sane option.
```

## What Teams Get Wrong

The most common mistake is treating this as a binary decision: use a managed platform or build from scratch. The real answer is sequential.

Start managed. Every time. The engineering cost of building sandbox infrastructure before you've validated that your product needs a million sessions per day is pure waste. E2B or Daytona will get you to market faster than any DIY approach, and at low volume the cost difference is irrelevant.

But plan the migration. The break-even point is knowable in advance. If your growth trajectory points toward 200K+ sessions per day within 18 months, start scoping the DIY infrastructure now. The 6-12 month build time means you need to begin before the economics force your hand.

The second mistake is ignoring warm pool costs during planning. I've seen teams budget for session compute and then get blindsided by the cost of keeping VMs warm for acceptable latency. At scale, warm pool overhead can exceed active compute costs. If your product requires sub-100ms response times, model the warm pool cost separately. It changes the break-even math significantly.

The third mistake is assuming managed platforms will offer volume discounts that change the equation. They might. But the fundamental economics of per-second billing versus owning your hosts don't change with a discount code. Even at 50% off, a million sessions per day on E2B is $67,500/month. DIY on Firecracker is still $24K-$90K with no discount needed.

## The Bottom Line

The economics of AI code execution at scale are not complicated. They're arithmetic. Half a cent per session, linear scaling on managed platforms, fixed costs on self-hosted infrastructure. The inflection point sits between 200K and 500K sessions per day.

If you're below that, use a managed platform and focus your engineering effort on your actual product. If you're above it, every month you delay the migration is money you're choosing to spend on someone else's margin instead of your own infrastructure.

The math is simple. The only question is whether you run the numbers before or after you get the bill.
