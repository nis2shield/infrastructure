import { Hono } from 'hono';
import type { Env } from '../index';

export const verifyRouter = new Hono<{ Bindings: Env }>();

/**
 * GET /v1/audit/verify/:merkle_root
 * Verifies if a Merkle root has been signed and returns signature details.
 */
verifyRouter.get('/verify/:merkle_root', async (c) => {
    const merkleRoot = c.req.param('merkle_root').toLowerCase();

    // Validate format
    if (!/^[a-fA-F0-9]{64}$/.test(merkleRoot)) {
        return c.json({
            error: 'INVALID_MERKLE_ROOT',
            message: 'Merkle root must be a 64-character hex string (SHA-256)'
        }, 400);
    }

    // Look up signed audit
    const result = await c.env.DB.prepare(`
        SELECT 
            sa.signature,
            sa.signed_at,
            l.organization_name,
            l.tier
        FROM signed_audits sa
        JOIN licenses l ON sa.license_id = l.id
        WHERE sa.merkle_root = ?
    `).bind(merkleRoot).first<{
        signature: string;
        signed_at: string;
        organization_name: string;
        tier: string;
    }>();

    if (!result) {
        return c.json({
            valid: false,
            message: 'No signature found for this Merkle root'
        });
    }

    return c.json({
        valid: true,
        signed_at: result.signed_at,
        organization: result.organization_name,
        tier: result.tier,
        certificate_id: 'nis2shield-2026-ev-001'
    });
});
