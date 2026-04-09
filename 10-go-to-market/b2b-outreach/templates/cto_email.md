# Cold Outreach Email — CTO / VP Engineering

**Subject line options** (pick one):
- "Does your security team block GitHub Insights?"
- "Git analytics for companies that can't use SaaS tools"
- "2-second git history analysis, completely offline"

---

Hi [First Name],

I'll keep this short.

I built a tool for engineering orgs at companies like yours — where InfoSec blocks SaaS analytics tools. [Company Name]'s size suggests you might care about this.

**The problem**: Your team probably has questions like "which files cause the most bugs?" or "what's our bus factor risk?" But GitHub Insights requires OAuth. CodeClimate sends your code off-machine. That's often blocked in [finance / healthcare / defense].

**What Stageira does**: Analyzes your entire git history in < 2 seconds, completely locally. No API tokens. No data ever leaves your machine. Works air-gapped.

```bash
stageira analyze /path/to/repo
# → code churn, bus factor, contributor risk in 2 seconds
```

Single Rust binary. Works on GitHub, GitLab, Bitbucket, or any git repo.

Would a 15-minute call make sense? I'd love to learn if this matches a problem you're dealing with.

[Your name]

P.S. Open source core: [GitHub link]. Compliance checker script included.

---

**Follow-up if no reply after 1 week:**

Hi [First Name], just bumping this. I know you're busy. Short version: offline git analytics for teams where GitHub Insights is blocked. Takes 30 seconds to try: `cargo install stageira`. No commitment.

[Your name]
