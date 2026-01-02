import { Hono } from 'hono';
import type { Env } from '../index';
import { generateId, generateLicenseKey } from '../utils/crypto';

export const stripeRouter = new Hono<{ Bindings: Env }>();

interface StripeEvent {
    type: string;
    data: {
        object: {
            id: string;
            customer: string;
            status?: string;
            metadata?: Record<string, string>;
        };
    };
}

/**
 * POST /webhooks/stripe
 * Handles Stripe subscription lifecycle events.
 */
stripeRouter.post('/stripe', async (c) => {
    // Note: In production, verify webhook signature using STRIPE_WEBHOOK_SECRET
    // For MVP, we'll implement basic handling

    const event = await c.req.json<StripeEvent>();

    console.log(`Stripe Webhook: ${event.type}`);

    switch (event.type) {
        case 'customer.subscription.created':
        case 'checkout.session.completed': {
            const subscription = event.data.object;
            const customerId = subscription.customer;
            const orgName = subscription.metadata?.organization_name || 'Unknown Organization';

            // Generate a new license key
            const licenseKey = generateLicenseKey();

            await c.env.DB.prepare(`
                INSERT INTO licenses (id, license_key, organization_name, stripe_customer_id, stripe_subscription_id, status, tier)
                VALUES (?, ?, ?, ?, ?, 'active', 'pro')
            `).bind(
                generateId(),
                licenseKey,
                orgName,
                customerId,
                subscription.id
            ).run();

            console.log(`Created license for ${orgName}: ${licenseKey}`);
            break;
        }

        case 'customer.subscription.updated': {
            const subscription = event.data.object;
            const status = subscription.status === 'active' ? 'active' : 'expired';

            await c.env.DB.prepare(`
                UPDATE licenses SET status = ? WHERE stripe_subscription_id = ?
            `).bind(status, subscription.id).run();

            console.log(`Updated subscription ${subscription.id} to ${status}`);
            break;
        }

        case 'customer.subscription.deleted': {
            const subscription = event.data.object;

            await c.env.DB.prepare(`
                UPDATE licenses SET status = 'cancelled' WHERE stripe_subscription_id = ?
            `).bind(subscription.id).run();

            console.log(`Cancelled subscription ${subscription.id}`);
            break;
        }

        default:
            console.log(`Unhandled event type: ${event.type}`);
    }

    return c.json({ received: true });
});
