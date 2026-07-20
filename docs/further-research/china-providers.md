# Chinese AI Providers — OSS/Developer Funding Programs

> **Updated**: 2026-07-13 (now with headless Brave browser verification)
> **Method**: `brave-browser --headless=new --no-sandbox --dump-dom` for JS SPA rendering

## 🇨🇳 Zhipu AI (GLM / 智谱AI)

**URL**: https://open.bigmodel.cn
**Pricing**: https://open.bigmodel.cn/pricing
**Docs**: https://docs.bigmodel.cn (on Mintlify)

### Confirmed Free Credits
- **New users**: **20 million Tokens** free on registration
- **Referral program**: Invite friends to get up to **200 million Tokens** total
- **Free models**: GLM-4.7-Flash (200K context) has free tier; GLM-4.7-FlashX also has free quota
- **OpenAI SDK compatible** — existing API code works with endpoint change

### Verified Pricing (¥ per million tokens)
| Model | Context | Input (¥/M) | Output (¥/M) | Notes |
|-------|---------|------------|-------------|-------|
| GLM-4.7-Flash | 200K | 0.5 (~$0.07) | free currently | Cheapest |
| GLM-4.7-FlashX | 200K | 0.5 (~$0.07) | free currently | Fast |
| GLM-4.5-Air | 128K | 0.8 (~$0.11) | free | |
| GLM-5.2 | 1M | 28 (~$3.86) | free currently | Flagship |
| GLM-5.1 | 128K | 24 (~$3.31) | free currently | |
| GLM-5-Turbo | 128K | 22 (~$3.04) | free | |

### Verification Status
- ✅ Accessible from Argentina (open.bigmodel.cn works)
- ✅ Can sign up with international phone/email
- ⚠️ No specific **OSS sponsorship program** found — only paid API + free tier
- ❌ No hardware/credit grants for open source projects (unlike Alibaba SMB coupon)

### Coding Plans
The docs mention "编码套餐" (Coding Plans) with integration guides for:
Cursor, Claude, Claude for IDE, Cline, CodeBuddy, Crush, Droid, Goose, Kilo, Lingma, OpenClaw, OpenCode, Qoder, Roo, Trae, ZCode — plus Cherry Studio and Zhipu's own tools.

---

## 🇨🇳 Baidu Cloud / PaddlePaddle (百度飞桨)

**URL**: https://cloud.baidu.com/campaign/opensource/index.html
**PaddlePaddle**: https://www.paddlepaddle.org.cn/

### Verification Status
- ❌ OSS campaign page: **TIMEOUT** — couldn't verify
- ❌ PaddlePaddle site: Chinese SPA, no accessible content
- ⚠️ Historically known to have hardware grants (AI accelerators) for projects using Paddle
- ⚠️ Probably requires Chinese mainland registration (身份证)

---

## 🇨🇳 BAAI FlagOpen (北京智源人工智能研究院)

**URL**: https://flagopen.baai.ac.cn/

### Verification Status
- ❌ Page loaded but **no readable content** (empty after JS render)
- ⚠️ Known to have open-source ecosystem grants
- ⚠️ Academic institution — probably China-only

---

## 🇨🇳 Volcengine / ByteDance (火山引擎)

**URL**: https://www.volcengine.com/
**Developer**: https://www.volcengine.com/docs/6257

### Verification Status
- ❌ React SPA — requires JS but headless Brave couldn't render content
- 🔍 Found nav items: "火山方舟 Agent Plan", "火山方舟 Coding Plan", "节省计划", "AgentKit"
- ❌ No way to verify from CLI — requires interactive browser session
- ⚠️ Probably China mainland only (phone number, 营业执照)

---

## 🇨🇳 Tencent Cloud (腾讯云)

**URL**: https://cloud.tencent.com/developer/support-plan

### Confirmed: Blogger Program (自媒体同步曝光计划)
- **NOT** an OSS sponsorship — it's a **blogger marketing program**
- Requires 20+ original technical articles
- **Payout**: ¥30 / ¥100 / ¥180 (~$4/$14/$25 USD) cloud server vouchers
- Plus: traffic promotion, community badges, technical event tickets
- Invite friends: both get ¥30-180 vouchers

### Verification
- ✅ Page loaded fully
- ✅ Details confirmed in Chinese
- ❌ Misleading name — this is not OSS funding, it's content marketing

---

## 🇨🇳 Huawei Cloud (华为云)

**URL**: Huawei Cloud Nurture Plan (page moved; check huaweicloud.com for current programs)

### Verification Status
- ❌ **404 page** — the "沃土计划" (Nurture Plan) URL is dead
- ❌ International page also 404
- ⚠️ Historically invested ¥1B+ in developer ecosystem but no active public program found
- ❌ Not worth pursuing

---

## 🇨🇳 OpenAtom Foundation (开放原子开源基金会)

**URL**: https://www.openatom.org/

### Verification Status
- ❌ Could not verify from CLI (no dump-dom executed this round)
- ⚠️ Government-backed OSS foundation
- ⚠️ Focuses on OpenHarmony, openEuler, infrastructure — NOT AI/NLP
- ⚠️ Requires Chinese residency

---

## Summary Table

| Provider | Free Tier | OSS Grant | Accessible from AR | Verifiable | Notes |
|----------|-----------|-----------|-------------------|------------|-------|
| **Alibaba Cloud** | 103M tokens + $5K SMB coupon | ✅ Campaign (page 404 now) | ✅ | ✅ 103M active | **Best option** |
| **Zhipu AI** | 20M tokens (200M via referrals) | ❌ None found | ✅ | ✅ | 2nd best — free API |
| **Tencent Cloud** | ¥30-180 vouchers | ❌ Blogger only | ✅ | ✅ | Not OSS funding |
| **Baidu** | Unknown | ❌ Couldn't verify | ❌ Probably not | ❌ | China mainland |
| **Volcengine** | Unknown | ❌ Couldn't verify | ❌ Probably not | ❌ | China mainland |
| **BAAI** | Unknown | Unknown | ❌ Probably not | ❌ | Academic/China |
| **Huawei** | Dead | Dead | ❌ | ✅ 404 | Not viable |
| **NGI Zero** | €5K-€50K | ✅ Yes | ✅ | ✅ | **Best OSS grant** |
| **STF (Germany)** | ~€100K | ✅ Yes | ✅ | ✅ | Sovereign tech |
| **GitHub Accelerator** | $40K + equity | ✅ Yes | ✅ | ✅ | Competitive |

### Bottom Line for reverberage

The Chinese provider landscape for OSS sponsorship is **mostly hype**:
- Only **Alibaba Cloud** has a verified, accessible, real OSS credit program (SMB coupon)
- **Zhipu AI** has the best free API tier (20M tokens) but no OSS sponsorship
- The rest are either inaccessible from Argentina, dead pages, or disguised marketing programs

The **real OSS money** for reverberage is still NGI Zero (€5K-€50K, deadline Aug 1, IIJ/NLnet).
