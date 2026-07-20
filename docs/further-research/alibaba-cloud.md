# Alibaba Cloud — SMB Coupon & Free Tier

## Source
- SMB coupon campaign: ``alibabacloud.com/campaign/smb-coupon`` (HTTP 200, real content)
- Free quota help: ``alibabacloud.com/help/model-studio/new-free-quota`` (confirmed)
- AI Catalyst: ``alibabacloud.com/campaign/model-studio-ai-catalyst`` (placeholder page)

---

## Stage A — Free Tier — [OK] ACTIVE

- 103M tokens total: 81 LLM + 17 multimodal + 5 embedding models, 1M each
- 90-day validity from activation (Jul 6 -> Sep 28 2026)
- Singapore (International) region only. No credit card needed.
- "Free Quota Only" toggle in console prevents accidental charges
- Tracking: ``docs/stage-a-tracking.md`` (81 models, 10 skipped, ~71 available)
- Status: IN USE. 1 model active (qwen3-coder-plus), 80 intact

---

## Stage B — SMB Coupon — "Unlock Up to $5,000 in Credits" — [OK] ACTIVE

Previous docs said "$200 SMB coupon". **Live page shows a MUCH bigger program:**

| Tranche | Requirement | Credit |
|---------|-------------|--------|
| $200 instant | No minimum. Apply with use case (~100 words) | $200 |
| $1,000 match | Spend $1,000 within 3 months | $1,000 |
| $4,000 match | Spend $6,000 more in next 3 months ($2K x2) | $4,000 |
| **Total** | | **Up to $5,000** |

Application form: ``page-intl.aliyun.com/form/act1940285320/index.htm``

From the page: works for AI video, agents, LLM apps, text gen, image gen.
Also promises "70+ Million Tokens Free" alongside the cash credits.

---

## Stage C — AI Catalyst — [X] NOT ACTIVE

- Campaign page exists (HTTP 200) but shows: "Sorry, you've landed on an unexplored planet!"
- Was supposed to offer 2B tokens + $120K according to old plan doc
- Status: dead. Replaced by SMB coupon program.

---

## Tips

- Apply for SMB coupon with reverberage use case: alchemical NLP workshop (transcription, verification, transformation)
- Use workspace-specific endpoints for better performance
- TTS quota is separate from LLM tokens (10K chars per model)
