# Running LHCR sweeps faster / off-machine

## The honest framing first

LHCR sweeps are **I/O-bound**, not compute-bound. Every cell is just HTTP calls to Bedrock /
OpenAI / Gemini, waiting on *their* inference (seconds–minutes each). The local CPU is idle the
whole time. So:

- **Bigger/cloud hardware does NOT make a single call faster**, and it does **not** raise the
  providers' rate limits — which are the real ceiling.
- The two levers that actually speed things up work **anywhere**:
  1. **Concurrency.** Set `LHCR_CONCURRENCY` (default 12). The cells are independent.
  2. **Provider parallelism.** Bedrock, OpenAI, and Gemini have **independent rate-limit pools**,
     so a mixed run (Anthropic + GPT + Gemini + the OSS-on-Bedrock set) parallelizes across all
     three. Each provider has adaptive retry/backoff, so pushing concurrency mostly trades a few
     429-retries for throughput.

So the real question isn't "faster CPU" — it's **"keep it running unattended without my laptop
killing it."** Two ways:

## Option A — zero cost: keep it alive on this machine

The runs that died were almost certainly the laptop sleeping / the session ending. Fix that for
free:

```bash
cd ~/Documents/Vaults/CodingVault/llm-bench && source .venv/bin/activate
export OPENAI_API_KEY="$(security find-generic-password -s OPENAI_API_KEY -w)"
export GEMINI_API_KEY="$(security find-generic-password -s GEMINI_API_KEY -w)"
# caffeinate -i prevents idle sleep; nohup detaches from the terminal
AWS_PROFILE=keystone LHCR_CONCURRENCY=20 caffeinate -i \
  nohup python -u -m llm_bench.familiarity.lhcr all 3 > /tmp/lhcr.log 2>&1 &
```

Resume-by-sample means if it *does* die, the same command picks up where it stopped. This is
probably all you need.

## Option B — true walk-away: a small EC2 box

Worth it if you want to close the laptop entirely, run much larger sweeps (more models, higher
k, post-fix probing), or run several back-to-back unattended.

- **Instance:** `t3.medium` (or `t3.large`) in **us-west-2** (same region as Bedrock — shaves
  round-trip latency, though inference dominates). It's I/O-bound, so a small box is plenty.
  ~$0.04–0.08/hr; stop it when idle.
- **Bedrock auth = IAM role, NOT copied keys.** Attach an instance role with an inline policy:
  ```json
  { "Version": "2012-10-17", "Statement": [{
      "Effect": "Allow",
      "Action": ["bedrock:InvokeModel", "bedrock:InvokeModelWithResponseStream", "bedrock:Converse"],
      "Resource": "*" }] }
  ```
  The account-level ZDR (`data_retention_mode: none`) carries over — it's not per-credential.
  Drop `AWS_PROFILE=keystone` on the box (the role is ambient).
- **OpenAI / Gemini keys:** put them in **SSM Parameter Store (SecureString)** or Secrets
  Manager, and load into env at run time. Do NOT bake them into the AMI or git.
- **Setup:**
  ```bash
  sudo yum install -y git python3.11
  git clone <repo> llm-bench && cd llm-bench
  python3.11 -m venv .venv && source .venv/bin/activate && pip install -e .
  export OPENAI_API_KEY="$(aws ssm get-parameter --name /llm-bench/openai --with-decryption --query Parameter.Value --output text)"
  export GEMINI_API_KEY="$(aws ssm get-parameter --name /llm-bench/gemini --with-decryption --query Parameter.Value --output text)"
  ```
- **Run detached** (tmux survives SSH drop):
  ```bash
  tmux new -s lhcr
  LHCR_CONCURRENCY=24 python -u -m llm_bench.familiarity.lhcr all 3 | tee /tmp/lhcr.log
  # Ctrl-b d to detach; `tmux attach -t lhcr` to check in
  ```
- **Get results back:** the box writes to `results/familiarity/runs/long-horizon/`. Either
  `git commit && push` from the box, or `scp` the `runs/` jsons home and run
  `python -m llm_bench.familiarity.lhcr rebuild` locally to regenerate cards/leaderboards.
- **Teardown:** `aws ec2 stop-instances` (keep the disk to resume later) or terminate.

## Don't forget

- **One sweep at a time** per results dir — concurrent sweeps race on the verdicts shard. Scale
  with `LHCR_CONCURRENCY`, not with multiple processes.
- Rotate the OpenAI + Gemini keys that were exposed earlier before putting them in SSM.
