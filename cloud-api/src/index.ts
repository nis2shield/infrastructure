import { Hono } from 'hono';
import { cors } from 'hono/cors';
import { signRouter } from './routes/sign';
import { verifyRouter } from './routes/verify';
import { stripeRouter } from './routes/stripe';

// Type definitions for Cloudflare Workers environment
export interface Env {
    DB: D1Database;
    ENVIRONMENT: string;
    SIGNING_KEY_SECRET: string; // Set via wrangler secret put
    STRIPE_WEBHOOK_SECRET?: string;
}

const app = new Hono<{ Bindings: Env }>();

// CORS for all origins (API is public)
app.use('*', cors({
    origin: '*',
    allowMethods: ['GET', 'POST', 'OPTIONS'],
    allowHeaders: ['Content-Type', 'Authorization'],
}));

// Health check
app.get('/', (c) => {
    return c.json({
        service: 'NIS2 Shield Cloud Signing API',
        version: '0.1.0',
        status: 'operational',
        environment: c.env.ENVIRONMENT
    });
});

// Mount routers
app.route('/v1/audit', signRouter);
app.route('/v1/audit', verifyRouter);
app.route('/webhooks', stripeRouter);

// 404 handler
app.notFound((c) => {
    return c.json({ error: 'NOT_FOUND', message: 'Endpoint not found' }, 404);
});

// Error handler
app.onError((err, c) => {
    console.error('API Error:', err);
    return c.json({
        error: 'INTERNAL_ERROR',
        message: c.env.ENVIRONMENT === 'staging' ? err.message : 'Internal server error'
    }, 500);
});

export default app;
