/**
 * Cryptographic utilities for the Cloud Signing API.
 */

/**
 * Generates a cryptographic signature for a Merkle root.
 * Uses HMAC-SHA256 with the signing key secret.
 */
export async function generateSignature(
    signingKey: string,
    merkleRoot: string,
    timestamp: string
): Promise<string> {
    const encoder = new TextEncoder();
    const data = encoder.encode(`${merkleRoot}:${timestamp}`);
    const keyData = encoder.encode(signingKey);

    const cryptoKey = await crypto.subtle.importKey(
        'raw',
        keyData,
        { name: 'HMAC', hash: 'SHA-256' },
        false,
        ['sign']
    );

    const signature = await crypto.subtle.sign('HMAC', cryptoKey, data);

    // Convert to base64
    return btoa(String.fromCharCode(...new Uint8Array(signature)));
}

/**
 * Generates a random UUID v4.
 */
export function generateId(): string {
    return crypto.randomUUID();
}

/**
 * Generates a new license key in the format: nis2_live_XXXXXXXXXXXX
 */
export function generateLicenseKey(): string {
    const bytes = new Uint8Array(16);
    crypto.getRandomValues(bytes);
    const hex = Array.from(bytes).map(b => b.toString(16).padStart(2, '0')).join('');
    return `nis2_live_${hex}`;
}

/**
 * Verifies an HMAC signature.
 */
export async function verifySignature(
    signingKey: string,
    merkleRoot: string,
    timestamp: string,
    signature: string
): Promise<boolean> {
    const expected = await generateSignature(signingKey, merkleRoot, timestamp);
    return expected === signature;
}
