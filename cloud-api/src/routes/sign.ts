import { Hono } from 'hono';
import type { Env } from '../index';
import { generateSignature, generateId } from '../utils/crypto';

export const signRouter = new Hono<{ Bindings: Env }>();

interface SignRequest {
    license_key: string;
    merkle_root: string;
    client_version?: string;
    timestamp_claimed?: string;
}

/**
 * POST /v1/audit/sign
 * Signs a Merkle root hash with the NIS2 Shield certificate.
 */
signRouter.post('/sign', async (c) => {
    const body = await c.req.json<SignRequest>();

    // Validate required fields
    if (!body.license_key || !body.merkle_root) {
        return c.json({
            error: 'INVALID_REQUEST',
            message: 'Missing required fields: license_key, merkle_root'
        }, 400);
    }

    // Validate merkle_root format (should be hex string)
    if (!/^[a-fA-F0-9]{64}$/.test(body.merkle_root)) {
        return c.json({
            error: 'INVALID_MERKLE_ROOT',
            message: 'Merkle root must be a 64-character hex string (SHA-256)'
        }, 400);
    }

    // Check license validity
    const license = await c.env.DB.prepare(
        'SELECT id, organization_name, status, tier, expires_at FROM licenses WHERE license_key = ?'
    ).bind(body.license_key).first<{
        id: string;
        organization_name: string;
        status: string;
        tier: string;
        expires_at: string | null;
    }>();

    if (!license) {
        return c.json({
            error: 'INVALID_LICENSE',
            message: 'License key not found'
        }, 403);
    }

    if (license.status !== 'active' && license.status !== 'trial') {
        return c.json({
            error: 'LICENSE_EXPIRED',
            message: `License status is '${license.status}'. Please renew your subscription.`
        }, 403);
    }

    // Check if expired
    if (license.expires_at && new Date(license.expires_at) < new Date()) {
        // Update status to expired
        await c.env.DB.prepare(
            "UPDATE licenses SET status = 'expired' WHERE id = ?"
        ).bind(license.id).run();

        return c.json({
            error: 'LICENSE_EXPIRED',
            message: 'License has expired. Please renew your subscription.'
        }, 403);
    }

    // Generate signature
    const signedAt = new Date().toISOString();
    const signature = await generateSignature(
        c.env.SIGNING_KEY_SECRET,
        body.merkle_root,
        signedAt
    );

    const auditId = generateId();
    const certificateId = `nis2shield-2026-ev-001`; // Placeholder for real EV cert ID

    // Store signed audit for later verification
    await c.env.DB.prepare(
        'INSERT INTO signed_audits (id, license_id, merkle_root, signature, signed_at) VALUES (?, ?, ?, ?, ?)'
    ).bind(auditId, license.id, body.merkle_root.toLowerCase(), signature, signedAt).run();

    return c.json({
        success: true,
        signature,
        timestamp: signedAt,
        certificate_id: certificateId,
        merkle_root: body.merkle_root.toLowerCase(),
        organization: license.organization_name,
        tier: license.tier
    });
});
