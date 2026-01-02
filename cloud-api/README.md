# NIS2 Shield Cloud Signing API

**Production API for cryptographically signing NIS2 compliance audit reports.**

## Quick Start

```bash
# Install dependencies
npm install

# Create D1 database (first time only)
wrangler d1 create nis2-licenses

# Apply schema
wrangler d1 execute nis2-licenses --file=./db-schema.sql.template

# Set the signing secret
wrangler secret put SIGNING_KEY_SECRET

# Run locally
npm run dev

# Deploy to production
npm run deploy
```

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/v1/audit/sign` | Sign a Merkle root with license validation |
| `GET` | `/v1/audit/verify/:merkle_root` | Verify a signature publicly |
| `POST` | `/webhooks/stripe` | Handle Stripe subscription events |

## Environment Setup

1. **Cloudflare Account**: Create a Cloudflare Workers account
2. **D1 Database**: Create a D1 database and update `wrangler.toml` with the ID
3. **Secrets**:
   - `SIGNING_KEY_SECRET`: Your HMAC signing key (generate a strong random string)
   - `STRIPE_WEBHOOK_SECRET`: Your Stripe webhook signing secret

## Architecture

```
cloud-api/
├── src/
│   ├── index.ts          # Main Hono app
│   ├── routes/
│   │   ├── sign.ts       # POST /v1/audit/sign
│   │   ├── verify.ts     # GET /v1/audit/verify/:hash
│   │   └── stripe.ts     # Stripe webhooks
│   └── utils/
│       └── crypto.ts     # HMAC signing utilities
├── wrangler.toml         # Cloudflare Workers config
├── db-schema.sql.template # D1 database schema
└── package.json
```

## License

MIT - Part of the [NIS2 Shield](https://nis2shield.com) ecosystem.
